import io, os
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
    CLIPTextModel
)

# ✅ local import stays the same for your repo layout
from tryon_pipeline import StableDiffusionXLInpaintPipeline as TryonPipeline
from src.unet_hacked_tryon import UNet2DConditionModel
from src.unet_hacked_garmnet import UNet2DConditionModel as UNet2DConditionModel_ref

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======== MODEL LOADING ========
# If PRETRAINED_MODEL_NAME is set to a path (e.g., "/models/IDM-VTON"), the pipeline will load from disk.
# Otherwise it falls back to the hub id "yisol/IDM-VTON".
PRETRAINED_MODEL_NAME = os.getenv("PRETRAINED_MODEL_NAME", "yisol/IDM-VTON")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# (Your existing pipeline construction code remains unchanged below)
# ... load schedulers/tokenizers/encoders/unets/vae using PRETRAINED_MODEL_NAME ...
# ... build TryonPipeline and move to DEVICE ...

@app.get("/health")
def health():
    try:
        gpu = torch.cuda.is_available()
        return {"ready": True, "gpu": gpu, "model": PRETRAINED_MODEL_NAME}
    except Exception as e:
        return JSONResponse({"ready": False, "error": str(e)})

@app.post("/tryon")
async def tryon_endpoint(
    person_image: UploadFile = File(...),
    clothing_image: UploadFile = File(...)
):
    try:
        person = Image.open(io.BytesIO(await person_image.read())).convert("RGB")
        cloth  = Image.open(io.BytesIO(await clothing_image.read())).convert("RGBA")
        # ... your existing inference steps ...
        out_img = person  # placeholder; your real composite goes here
        buf = io.BytesIO()
        out_img.save(buf, format="PNG")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
