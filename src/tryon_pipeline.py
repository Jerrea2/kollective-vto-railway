# --- FastAPI middleware shim for import-time safety (added by Andy) ---
try:
    app
except NameError:
    class _NoApp:
        def middleware(self, *args, **kwargs):
            def deco(fn): 
                return fn  # no-op decorator
            return deco
    app = _NoApp()
# --- end shim ---
from fastapi.responses import JSONResponse
# tryon_pipeline.py
import inspect
from typing import Optional, List, Union
import numpy as np
import PIL.Image
import torch
from transformers import (
    CLIPTokenizer,
    CLIPTextModel,
    CLIPTextModelWithProjection,
    CLIPImageProcessor,
    CLIPVisionModelWithProjection,
)
from diffusers import DiffusionPipeline, AutoencoderKL, UNet2DConditionModel, DDPMScheduler
from diffusers.image_processor import VaeImageProcessor
from diffusers.utils import logging

logger = logging.get_logger(__name__)

def retrieve_latents(encoder_output, generator=None, sample_mode="sample"):
    if hasattr(encoder_output, "latent_dist") and sample_mode == "sample":
        return encoder_output.latent_dist.sample(generator)
    elif hasattr(encoder_output, "latent_dist") and sample_mode == "argmax":
        return encoder_output.latent_dist.mode()
    elif hasattr(encoder_output, "latents"):
        return encoder_output.latents
    else:
        raise AttributeError("No latents found in encoder_output")

class StableDiffusionXLInpaintPipeline(DiffusionPipeline):
    def __init__(
        self,
        vae: AutoencoderKL,
        text_encoder: CLIPTextModel,
        text_encoder_2: CLIPTextModelWithProjection,
        tokenizer: CLIPTokenizer,
        tokenizer_2: CLIPTokenizer,
        unet: UNet2DConditionModel,
        unet_encoder: UNet2DConditionModel,
        scheduler: DDPMScheduler,
        image_encoder: CLIPVisionModelWithProjection = None,
        feature_extractor: CLIPImageProcessor = None,
    ):
        super().__init__()
        self.register_modules(
            vae=vae,
            text_encoder=text_encoder,
            text_encoder_2=text_encoder_2,
            tokenizer=tokenizer,
            tokenizer_2=tokenizer_2,
            unet=unet,
            unet_encoder=unet_encoder,
            scheduler=scheduler,
            image_encoder=image_encoder,
            feature_extractor=feature_extractor,
        )
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor)

    def _encode_vae_image(self, image: torch.Tensor, generator=None):
        dtype = image.dtype
        if self.vae.config.force_upcast:
            image = image.float()
            self.vae.to(dtype=torch.float32)
        if isinstance(generator, list):
            latents = [retrieve_latents(self.vae.encode(image[i:i+1]), generator[i]) for i in range(image.shape[0])]
            latents = torch.cat(latents, dim=0)
        else:
            latents = retrieve_latents(self.vae.encode(image), generator=generator)
        if self.vae.config.force_upcast:
            self.vae.to(dtype)
        return latents.to(dtype)

    @torch.no_grad()
    def __call__(
        self,
        prompt: str,
        image: PIL.Image.Image,
        cloth: PIL.Image.Image,
        mask_image: PIL.Image.Image,
        pose_img: Optional[PIL.Image.Image] = None,
        height: int = 512,
        width: int = 512,
        num_inference_steps: int = 20,
        guidance_scale: float = 5.0,
    ):
        device = self._execution_device

        # === Encode text prompt ===
        text_inputs = self.tokenizer(prompt, return_tensors="pt", padding="max_length", truncation=True)
        prompt_embeds = self.text_encoder(text_inputs.input_ids.to(device), output_hidden_states=True).hidden_states[-2]

        text_inputs_2 = self.tokenizer_2(prompt, return_tensors="pt", padding="max_length", truncation=True)
        prompt_embeds_2 = self.text_encoder_2(text_inputs_2.input_ids.to(device), output_hidden_states=True).hidden_states[-2]

        prompt_embeds = torch.cat([prompt_embeds, prompt_embeds_2], dim=-1).to(device)

        # === Encode person image ===
        image = self.image_processor.preprocess(image, height=height, width=width).to(device)
        latents = self._encode_vae_image(image, generator=None)

        # === Encode garment image ===
        cloth = self.image_processor.preprocess(cloth, height=height, width=width).to(device)
        cloth_latents = self._encode_vae_image(cloth, generator=None)

        garment_feat = None if getattr(self, "unet_encoder", None) is None else self.unet_encoder(cloth_latents).sample

        # === Encode pose image (optional) ===
        pose_latents = None
        if pose_img is not None:
            pose_img = self.image_processor.preprocess(pose_img, height=height, width=width).to(device)
            pose_latents = self._encode_vae_image(pose_img, generator=None)

        # === Prepare noise schedule ===
        self.scheduler.set_timesteps(num_inference_steps)
        noise = torch.randn_like(latents).to(device)
        latents = noise * self.scheduler.init_noise_sigma

        # === Diffusion loop ===
        for t in self.progress_bar(self.scheduler.timesteps):
            latent_model_input = latents

            if pose_latents is not None and latent_model_input.shape[1] == 13:
                latent_model_input = torch.cat([latent_model_input, pose_latents], dim=1)

            noise_pred = self.unet(
                latent_model_input, t, encoder_hidden_states=prompt_embeds, added_cond_kwargs=({"garment": garment_feat} if garment_feat is not None else None)
            ).sample

            latents = self.scheduler.step(noise_pred, t, latents).prev_sample

        # === Decode image ===
        image = self.vae.decode(latents / self.vae.config.scaling_factor).sample
        image = (image / 2 + 0.5).clamp(0, 1)
        image = self.image_processor.postprocess(image, output_type="pil")
        return image

# --- CPU guard for /tryon (auto-injected by Andy) ---
import torch
from fastapi import Request
from fastapi.responses import JSONResponse

@app.middleware("http")
async def _gpu_required_guard(request: Request, call_next):
    # Intercept any route containing "tryon" before body parsing/validation.
    if ("tryon" in request.url.path.lower()) and (not torch.cuda.is_available()):
        return JSONResponse(status_code=503, content={"detail": "GPU required"})
    return await call_next(request)
# --- end guard ---


