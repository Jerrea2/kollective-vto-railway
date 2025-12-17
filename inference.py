import os
import torch
from fastapi import FastAPI, UploadFile, File
from diffusers import UNet2DConditionModel
from huggingface_hub import hf_hub_download
from PIL import Image
import io

app = FastAPI()

PRETRAINED_MODEL_NAME = "yisol/IDM-VTON"
DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

_pipeline = None


def _load_unet_with_sanitized_config():
    """
    CRITICAL FIX:
    Diffusers validates encoder_hid_dim_type DURING construction.
    We must remove it from the config BEFORE creating the UNet.
    """

    from diffusers.configuration_utils import FrozenDict

    config_path = hf_hub_download(
        repo_id=PRETRAINED_MODEL_NAME,
        filename="unet/config.json"
    )

    import json
    with open(config_path, "r") as f:
        config = json.load(f)

    if "encoder_hid_dim_type" in config:
        print("[VTO] Removing encoder_hid_dim_type from UNet config BEFORE load")
        config["encoder_hid_dim_type"] = None

    config = FrozenDict(config)

    unet = UNet2DConditionModel.from_config(config)
    weights_path = hf_hub_download(
        repo_id=PRETRAINED_MODEL_NAME,
        filename="unet/diffusion_pytorch_model.safetensors"
    )

    state_dict = torch.load(weights_path, map_location="cpu")
    unet.load_state_dict(state_dict)
    unet.to(device=DEVICE, dtype=DTYPE)

    return unet


def _lazy_load_pipeline():
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    print("[VTO] Lazy-loading IDM-VTON with sanitized UNet config")
    unet = _load_unet_with_sanitized_config()

    _pipeline = {
        "unet": unet
    }

    return _pipeline


@app.get("/")
def health():
    return {"status": "IDM-VTON FastAPI backend is running."}


@app.post("/tryon")
async def tryon(
    person_image: UploadFile = File(...),
    clothing_image: UploadFile = File(...)
):
    _lazy_load_pipeline()

    person_bytes = await person_image.read()
    cloth_bytes = await clothing_image.read()

    person = Image.open(io.BytesIO(person_bytes)).convert("RGB")
    cloth = Image.open(io.BytesIO(cloth_bytes)).convert("RGB")

    # TEMP OUTPUT to confirm pipeline execution
    output = person
    buf = io.BytesIO()
    output.save(buf, format="PNG")
    buf.seek(0)

    return buf.read()
