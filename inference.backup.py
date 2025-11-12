import io
import traceback
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

# ---------------- App + CORS ----------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Global state (no heavy imports here) ----------------
_STATE = {"ready": True, "loaded": False, "last_error": None}
_PIPE = None
_DTYPE = None
_DEVICE = None

def _log(msg: str):
    print(f"[VTO] {msg}", flush=True)

def _lazy_load_pipeline():
    """Load the heavy model ONLY once (on first /tryon), keep server alive if it fails."""
    global _PIPE, _STATE, _DTYPE, _DEVICE
    if _STATE["loaded"]:
        return _PIPE

    try:
        import os
        import torch
        from diffusers import DDPMScheduler, AutoencoderKL
        from transformers import (
            AutoTokenizer,
            CLIPImageProcessor,
            CLIPVisionModelWithProjection,
            CLIPTextModelWithProjection,
            CLIPTextModel,
        )

        # Try both layouts: with src/ or at repo root
        try:
            from src.unet_hacked_tryon import UNet2DConditionModel  # type: ignore
            from src.unet_hacked_garmnet import UNet2DConditionModel as UNet2DConditionModel_ref  # type: ignore
            from src.tryon_pipeline import StableDiffusionXLInpaintPipeline as TryonPipeline  # type: ignore
            _log("Using imports from src/*")
        except Exception:
            from unet_hacked_tryon import UNet2DConditionModel  # type: ignore
            from unet_hacked_garmnet import UNet2DConditionModel as UNet2DConditionModel_ref  # type: ignore
            from tryon_pipeline import StableDiffusionXLInpaintPipeline as TryonPipeline  # type: ignore
            _log("Using imports from project root")

        PRETRAINED_MODEL_NAME = os.environ.get("IDM_VTON_MODEL", "yisol/IDM-VTON")
        _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        _DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32

        _log(f"Lazy-loading IDM-VTON from {PRETRAINED_MODEL_NAME} on {_DEVICE} ({_DTYPE})")

        noise_scheduler = DDPMScheduler.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="scheduler")
        vae = AutoencoderKL.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="vae", torch_dtype=_DTYPE)
        unet = UNet2DConditionModel.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="unet", torch_dtype=_DTYPE)
        image_encoder = CLIPVisionModelWithProjection.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="image_encoder", torch_dtype=_DTYPE)
        unet_encoder = UNet2DConditionModel_ref.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="unet_encoder", torch_dtype=_DTYPE)
        text_encoder_one = CLIPTextModel.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="text_encoder", torch_dtype=_DTYPE)
        text_encoder_two = CLIPTextModelWithProjection.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="text_encoder_2", torch_dtype=_DTYPE)
        tokenizer_one = AutoTokenizer.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="tokenizer", revision=None, use_fast=False)
        tokenizer_two = AutoTokenizer.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="tokenizer_2", revision=None, use_fast=False)

        _PIPE = TryonPipeline.from_pretrained(
            PRETRAINED_MODEL_NAME,
            unet=unet,
            vae=vae,
            feature_extractor=CLIPImageProcessor(),
            text_encoder=text_encoder_one,
            text_encoder_2=text_encoder_two,
            tokenizer=tokenizer_one,
            tokenizer_2=tokenizer_two,
            scheduler=noise_scheduler,
            image_encoder=image_encoder,
            unet_encoder=unet_encoder,
            torch_dtype=_DTYPE,
        ).to(_DEVICE)

        _STATE.update({"loaded": True, "ready": True, "last_error": None})
        _log("Pipeline loaded. Ready.")
        return _PIPE

    except Exception as e:
        tb = traceback.format_exc()
        _STATE.update({"loaded": False, "ready": False, "last_error": f"{e}\n{tb}"})
        _log(f"Pipeline load FAILED: {e}\n{tb}")
        # keep the server alive; do not raise
        return None

# ---------- Health routes that never trigger heavy load ----------
@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"ready": _STATE["ready"], "loaded": _STATE["loaded"], "error": _STATE["last_error"]}

@app.get("/")
def root():
    return {"status": "IDM-VTON FastAPI backend is running."}

# ---------- Try-on endpoint (triggers first lazy load) ----------
@app.post("/tryon")
async def tryon(person_image: UploadFile = File(...), clothing_image: UploadFile = File(...)):
    if not _STATE["loaded"]:
        _lazy_load_pipeline()
        if not _STATE["loaded"]:
            return JSONResponse({"error": "model not loaded", "detail": _STATE["last_error"]}, status_code=500)

    import torch  # safe now
    try:
        person_bytes = await person_image.read()
        clothing_bytes = await clothing_image.read()
        person_img = Image.open(io.BytesIO(person_bytes)).convert("RGB")
        clothing_img = Image.open(io.BytesIO(clothing_bytes)).convert("RGBA")
    except Exception as e:
        return JSONResponse({"error": f"Invalid input images: {str(e)}"}, status_code=400)

    try:
        # Speed guard
        max_side = 640
        person_img.thumbnail((max_side, max_side), Image.LANCZOS)
        clothing_img.thumbnail((max_side, max_side), Image.LANCZOS)

        width, height = person_img.size
        pose_img = person_img.copy().resize((width, height))
        inpaint_mask = Image.new("L", (width, height), 128)  # neutral mask

        with torch.no_grad():
            result = _PIPE(
                prompt="photo of a person wearing clothing",
                image=person_img,
                cloth=clothing_img,
                mask_image=inpaint_mask,
                pose_img=pose_img,
                height=height,
                width=width,
                guidance_scale=2.0,
                num_inference_steps=10,
            )[0]
    except Exception as e:
        tb = traceback.format_exc()
        _log(f"Inference FAILED: {e}\n{tb}")
        return JSONResponse({"error": f"Inference failed: {str(e)}", "traceback": tb}, status_code=500)

    buf = io.BytesIO()
    result.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("inference:app", host="0.0.0.0", port=7860, log_level="info")
