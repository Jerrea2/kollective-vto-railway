# inference.py
# -----------------------------------------------------
# FastAPI backend for IDM-VTON (local-only, lazy load)
# Registers: GET /, GET /health, GET /__whoami, POST /tryon
# Prints exact file + all routes at startup.
# -----------------------------------------------------

import io
import os
import sys
from functools import lru_cache

# Force offline (no HF network calls)
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import torch

# Pillow ≥10 compatibility for LANCZOS
Resample = getattr(Image, "Resampling", Image)

# Ensure local import of pipeline next to this file
HERE = os.path.abspath(os.path.dirname(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# Your custom pipeline (this file must be next to inference.py)
from tryon_pipeline import StableDiffusionXLInpaintPipeline as TryonPipeline

# Diffusers / Transformers components
from diffusers import DDPMScheduler, AutoencoderKL
from transformers import (
    AutoTokenizer, CLIPImageProcessor,
    CLIPVisionModelWithProjection,
    CLIPTextModelWithProjection, CLIPTextModel
)
from diffusers.models import UNet2DConditionModel  # trust_remote_code=True

# ---------------- FastAPI ----------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # open for demo; tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print(f"[BOOT] Running file: {__file__}")

@app.on_event("startup")
async def _print_routes():
    # Helps verify exactly which routes are live
    print("[BOOT] Registered routes:")
    for r in app.router.routes:
        methods = sorted(list(getattr(r, "methods", []))) if hasattr(r, "methods") else []
        print("   ", methods, r.path)

# --------------- Model config ---------------
# EDIT THIS if your snapshot path changes:
LOCAL_SNAPSHOT = r"C:\Users\Owner\.cache\huggingface\hub\models--yisol--IDM-VTON\snapshots\585a32e74aee241cbc0d0cc3ab21392ca58c916a"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32

# Keep CPU from pegging all cores on Windows
if os.name == "nt" and DEVICE == "cpu":
    try:
        torch.set_num_threads(max(1, (os.cpu_count() or 2)//2))
    except Exception:
        pass

# --------------- Lazy singleton loader ---------------
@lru_cache(maxsize=1)
def get_pipe() -> TryonPipeline:
    """
    Lazily initialize the pipeline using ONLY local files.
    This keeps / and /health instant and prevents re-downloads.
    """
    if not os.path.isdir(LOCAL_SNAPSHOT):
        raise RuntimeError(
            f"Local snapshot not found: {LOCAL_SNAPSHOT}\n"
            "Set LOCAL_SNAPSHOT to your verified IDM-VTON snapshot directory."
        )

    print(f"[BOOT] Initializing IDM-VTON from local snapshot on {DEVICE} ({DTYPE})")
    lf = dict(local_files_only=True)

    # Core components
    noise_scheduler = DDPMScheduler.from_pretrained(LOCAL_SNAPSHOT, subfolder="scheduler", **lf)
    vae = AutoencoderKL.from_pretrained(LOCAL_SNAPSHOT, subfolder="vae", torch_dtype=DTYPE, **lf)

    # Both UNets use trust_remote_code=True so IDM-VTON custom code is honored
    unet = UNet2DConditionModel.from_pretrained(
        LOCAL_SNAPSHOT, subfolder="unet", torch_dtype=DTYPE, trust_remote_code=True, local_files_only=True
    )
    unet_encoder = UNet2DConditionModel.from_pretrained(
        LOCAL_SNAPSHOT, subfolder="unet_encoder", torch_dtype=DTYPE, trust_remote_code=True, local_files_only=True
    )

    # Encoders / Tokenizers
    image_encoder = CLIPVisionModelWithProjection.from_pretrained(
        LOCAL_SNAPSHOT, subfolder="image_encoder", torch_dtype=DTYPE, **lf
    )
    text_encoder_one = CLIPTextModel.from_pretrained(
        LOCAL_SNAPSHOT, subfolder="text_encoder", torch_dtype=DTYPE, **lf
    )
    text_encoder_two = CLIPTextModelWithProjection.from_pretrained(
        LOCAL_SNAPSHOT, subfolder="text_encoder_2", torch_dtype=DTYPE, **lf
    )
    tokenizer_one = AutoTokenizer.from_pretrained(
        LOCAL_SNAPSHOT, subfolder="tokenizer", use_fast=False, **lf
    )
    tokenizer_two = AutoTokenizer.from_pretrained(
        LOCAL_SNAPSHOT, subfolder="tokenizer_2", use_fast=False, **lf
    )

    # Build pipeline purely from local parts
    pipe = TryonPipeline.from_pretrained(
        LOCAL_SNAPSHOT,
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
        torch_dtype=DTYPE,
        local_files_only=True,
    ).to(DEVICE)

    if DEVICE == "cuda":
        torch.cuda.empty_cache()

    print("[BOOT] Pipeline ready.")
    return pipe

# ---------------- Routes ----------------
@app.get("/")
def root():
    return {"status": "IDM-VTON FastAPI backend is running."}

@app.get("/health")
def health():
    """Fast health check (does NOT force model load)."""
    loaded = get_pipe.cache_info().currsize > 0
    return {"status": "ok", "device": DEVICE, "dtype": str(DTYPE), "loaded": loaded}

# Debug route to prove which file & routes are live
@app.get("/__whoami")
def __whoami():
    routes = []
    for r in app.router.routes:
        methods = sorted(list(getattr(r, "methods", []))) if hasattr(r, "methods") else []
        routes.append({"methods": methods, "path": r.path})
    return {"file": __file__, "routes": routes}

@app.post("/tryon")
async def tryon(
    person_image: UploadFile = File(...),
    clothing_image: UploadFile = File(...),
):
    # 1) Read & validate inputs
    try:
        person_bytes = await person_image.read()
        clothing_bytes = await clothing_image.read()
        person_img = Image.open(io.BytesIO(person_bytes)).convert("RGB")
        clothing_img = Image.open(io.BytesIO(clothing_bytes)).convert("RGBA")
    except Exception as e:
        return JSONResponse({"error": f"Invalid input images: {e}"}, status_code=400)

    # 2) Normalize sizes (CPU-friendly defaults)
    max_size = 384 if DEVICE == "cpu" else 512
    person_img.thumbnail((max_size, max_size), Resample.LANCZOS)
    clothing_img.thumbnail((max_size, max_size), Resample.LANCZOS)
    width, height = person_img.size

    # Dummy pose + neutral mask required by IDM-VTON
    pose_img = person_img.copy().resize((width, height), Resample.LANCZOS)
    mask = Image.new("L", (width, height), 128)

    # 3) Inference
    try:
        pipe = get_pipe()  # lazy init on first request
        with torch.no_grad():
            out_img = pipe(
                prompt="photo of a person wearing clothing",
                image=person_img,
                cloth=clothing_img,
                mask_image=mask,
                pose_img=pose_img,
                height=height,
                width=width,
                guidance_scale=2.0,
                num_inference_steps=5 if DEVICE == "cpu" else 10,
            )[0]
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print("==== INFERENCE FAILED ====\n", tb)
        return JSONResponse({"error": str(e), "traceback": tb}, status_code=500)

    # 4) Stream PNG
    buf = io.BytesIO()
    out_img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


if __name__ == "__main__":
    # Running the file directly avoids any module import confusion
    import uvicorn
    uvicorn.run("inference:app", host="0.0.0.0", port=7860, reload=False)
