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

# ===== MODEL LOCATION =====
HF_HOME = os.environ.get("HF_HOME", "/app/hf-cache")
default_path = os.path.join(HF_HOME, "yisol__IDM-VTON")
PRETRAINED_MODEL_NAME = default_path if os.path.exists(default_path) else "yisol/IDM-VTON"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

@app.get("/health")
def health():
    try:
        return {"ready": True, "gpu": torch.cuda.is_available(), "model": PRETRAINED_MODEL_NAME}
    except Exception as e:
        return JSONResponse({"ready": False, "error": str(e)})

@app.post("/tryon")
async def tryon_endpoint(person_image: UploadFile = File(...), clothing_image: UploadFile = File(...)):
    try:
        person = Image.open(io.BytesIO(await person_image.read())).convert("RGB")
        cloth  = Image.open(io.BytesIO(await clothing_image.read())).convert("RGBA")
        # TODO: insert real VTON inference here
        out_img = person
        buf = io.BytesIO()
        out_img.save(buf, format="PNG")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
