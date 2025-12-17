# --- snip imports above ---

from diffusers import UNet2DConditionModel
import torch

# ... existing code ...

def _lazy_load_pipeline():
    global pipe

    if pipe is not None:
        return pipe

    print("[VTO] Lazy-loading IDM-VTON pipeline")

    unet = UNet2DConditionModel.from_pretrained(
        PRETRAINED_MODEL_NAME,
        subfolder="unet",
        torch_dtype=_DTYPE,
        ignore_mismatched_sizes=True
    )

    # 🔧 HARD FIX FOR IDM-VTON / DIFFUSERS COMPATIBILITY
    if hasattr(unet.config, "encoder_hid_dim_type"):
        print("[VTO] Forcing encoder_hid_dim_type=None for IDM-VTON compatibility")
        unet.config.encoder_hid_dim_type = None

    pipe = StableDiffusionInpaintPipeline.from_pretrained(
        PRETRAINED_MODEL_NAME,
        unet=unet,
        torch_dtype=_DTYPE
    ).to("cuda")

    return pipe

# --- rest of file unchanged ---
