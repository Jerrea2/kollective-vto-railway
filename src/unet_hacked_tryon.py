# Minimal shim: reuse Diffusers UNet2DConditionModel so imports succeed.
try:
    from diffusers.models.unet_2d_condition import UNet2DConditionModel as _BaseUNet
except Exception:
    from diffusers import UNet2DConditionModel as _BaseUNet  # older diffusers fallback

class UNet2DConditionModel(_BaseUNet):
    pass

__all__ = ["UNet2DConditionModel"]
