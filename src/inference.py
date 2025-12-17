import os
import sys
import torch
from diffusers import UNet2DConditionModel
from transformers import AutoConfig

print("======================================")
print("[VTO] RUNNING INFERENCE FILE:", __file__)
print("======================================")

DTYPE = torch.float16
PRETRAINED_MODEL_NAME = "yisol/IDM-VTON"

def _load_unet():
    print("[VTO] Loading UNet config ONLY (NO from_pretrained allowed)")

    config = AutoConfig.from_pretrained(
        PRETRAINED_MODEL_NAME,
        subfolder="unet"
    ).to_dict()

    if "encoder_hid_dim_type" in config:
        print("[VTO] Removing encoder_hid_dim_type BEFORE UNet construction")
        config["encoder_hid_dim_type"] = None

    # 🚨 HARD FAIL IF THIS EVER CHANGES
    if "from_pretrained" in str(UNet2DConditionModel):
        raise RuntimeError("from_pretrained is FORBIDDEN in this project")

    unet = UNet2DConditionModel.from_config(config)
    unet = unet.to(dtype=DTYPE)

    return unet

def lazy_load_pipeline():
    print("[VTO] Lazy-loading pipeline")
    unet = _load_unet()
    return unet
