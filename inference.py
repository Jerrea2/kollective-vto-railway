from diffusers import UNet2DConditionModel, AutoencoderKL
from transformers import CLIPTextModel, CLIPTokenizer
from huggingface_hub import hf_hub_download
import torch
import os

DTYPE = torch.float16
PRETRAINED_MODEL_NAME = "yisol/IDM-VTON"

def load_unet():
    print("[VTO] Loading UNet config manually")

    config = UNet2DConditionModel.load_config(
        PRETRAINED_MODEL_NAME,
        subfolder="unet"
    )

    # FORCE compatibility
    if "encoder_hid_dim_type" in config:
        print("[VTO] Removing encoder_hid_dim_type from config")
        config["encoder_hid_dim_type"] = None

    unet = UNet2DConditionModel.from_config(config)
    unet.load_state_dict(
        UNet2DConditionModel.from_pretrained(
            PRETRAINED_MODEL_NAME,
            subfolder="unet",
            torch_dtype=DTYPE
        ).state_dict()
    )

    return unet.to("cuda")

# rest of your inference code continues unchanged
