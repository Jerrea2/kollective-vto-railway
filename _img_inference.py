import io
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import torch
from diffusers import DDPMScheduler, AutoencoderKL
from transformers import (
    AutoTokenizer,
    CLIPImageProcessor,
    CLIPVisionModelWithProjection,
    CLIPTextModelWithProjection,
    CLIPTextModel,
)
from src.unet_hacked_tryon import UNet2DConditionModel
from src.unet_hacked_garmnet import UNet2DConditionModel as UNet2DConditionModel_ref
from src.tryon_pipeline import StableDiffusionXLInpaintPipeline as TryonPipeline

app = FastAPI()

# CORS (open for demo; restrict in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======== MODEL LOADING (runs at container start) ========
PRETRAINED_MODEL_NAME = "yisol/IDM-VTON"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32

print("Loading IDM-VTON models... (first cold start can take a minute)")
noise_scheduler = DDPMScheduler.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="scheduler")
vae = AutoencoderKL.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="vae", torch_dtype=DTYPE)
unet = UNet2DConditionModel.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="unet", torch_dtype=DTYPE)
image_encoder = CLIPVisionModelWithProjection.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="image_encoder", torch_dtype=DTYPE)
unet_encoder = UNet2DConditionModel_ref.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="unet_encoder", torch_dtype=DTYPE)
text_encoder_one = CLIPTextModel.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="text_encoder", torch_dtype=DTYPE)
text_encoder_two = CLIPTextModelWithProjection.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="text_encoder_2", torch_dtype=DTYPE)
tokenizer_one = AutoTokenizer.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="tokenizer", revision=None, use_fast=False)
tokenizer_two = AutoTokenizer.from_pretrained(PRETRAINED_MODEL_NAME, subfolder="tokenizer_2", revision=None, use_fast=False)

pipe = TryonPipeline.from_pretrained(
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
    torch_dtype=DTYPE,
).to(DEVICE)

# ======== /tryon API endpoint ========
@app.post("/tryon")
async def tryon(
    person_image: UploadFile = File(...),
    clothing_image: UploadFile = File(...),
):
    try:
        # Read uploaded images
        person_bytes = await person_image.read()
        clothing_bytes = await clothing_image.read()
        person_img = Image.open(io.BytesIO(person_bytes)).convert("RGB")
        clothing_img = Image.open(io.BytesIO(clothing_bytes)).convert("RGBA")
    except Exception as e:
        return JSONResponse({"error": f"Invalid input images: {str(e)}"}, status_code=400)

    try:
        # Keep memory low for serverless
        max_size = 512
        person_img.thumbnail((max_size, max_size), Image.LANCZOS)
        clothing_img.thumbnail((max_size, max_size), Image.LANCZOS)

        width, height = person_img.size
        pose_img = person_img.copy().resize((width, height))
        inpaint_mask = Image.new("L", (width, height), 128)  # simple neutral mask

        with torch.no_grad():
            output = pipe(
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
        import traceback
        traceback_str = traceback.format_exc()
        print("==== FULL TRACEBACK START ====")
        print(traceback_str)
        print("==== FULL TRACEBACK END ====")
        return JSONResponse({"error": f"Inference failed: {str(e)}", "traceback": traceback_str}, status_code=500)

    buf = io.BytesIO()
    output.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

# ======== Health check endpoints (required by RunPod) ========
@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"status": "IDM-VTON FastAPI backend is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("inference:app", host="0.0.0.0", port=7860)
