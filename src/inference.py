import os
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from diffusers import StableDiffusionXLPipeline

print("???? IDENTITY GATE HIT - src.inference IMPORTED ????", flush=True)
print("FILE=/app/src/inference.py", flush=True)
print("CWD=", os.getcwd(), flush=True)
print("SYS_PATH_HEAD=", __import__("sys").path[:6], flush=True)

app = FastAPI()

print("Loading SDXL from Hugging Face (NOT /app/model)", flush=True)

pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16
).to("cuda")

class InferRequest(BaseModel):
    prompt: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/infer")
def infer(req: InferRequest):
    image = pipe(
        prompt=req.prompt,
        num_inference_steps=25,
        guidance_scale=7.5,
    ).images[0]

    out_path = "/app/output.png"
    image.save(out_path)
    return FileResponse(out_path, media_type="image/png")
