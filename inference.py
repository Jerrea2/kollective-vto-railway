import os
import torch
from diffusers import StableDiffusionInpaintPipeline
from PIL import Image

MODEL_DIR = os.environ.get("IDM_VTON_MODEL_DIR", "/models/vendor-IDM-VTON")

print(f"[inference] Loading IDM-VTON model from: {MODEL_DIR}")

pipe = StableDiffusionInpaintPipeline.from_pretrained(
    MODEL_DIR,
    torch_dtype=torch.float16,
    safety_checker=None
).to("cuda")

pipe.enable_xformers_memory_efficient_attention()

def run_inference(person_img_path: str, cloth_img_path: str, output_path: str):
    print("[inference] Loading input images...")
    person = Image.open(person_img_path).convert("RGB")
    cloth = Image.open(cloth_img_path).convert("RGBA")

    print("[inference] Running diffusion...")
    result = pipe(
        prompt="a person wearing the given clothing item, photorealistic",
        image=person,
        mask_image=cloth,
        guidance_scale=7.5,
        num_inference_steps=30,
    ).images[0]

    print("[inference] Saving result...")
    result.save(output_path)
    return output_path
