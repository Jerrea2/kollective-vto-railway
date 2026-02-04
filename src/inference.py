# ============================================================
# RUNPOD ASGI ENTRYPOINT — HARD LOCKED
# SDXL BASE PIPELINE (NO INPAINT)
# ============================================================

import os
import sys
import time

import torch
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from diffusers import StableDiffusionXLPipeline

# -------------------------
# Identity Gate (DO NOT MOVE)
# -------------------------
STAMP = os.environ.get("BUILD_ID", "NO_BUILD_ID")

print(
    f"???? IDENTITY GATE HIT - src.inference IMPORTED - STAMP={STAMP} - T={time.time()} ????",
    flush=True,
)
print(f"FILE={__file__}", flush=True)
print(f"CWD={os.getcwd()}", flush=True)
print(f"SYS_PATH_HEAD={sys.path[:8]}", flush=True)

# -------------------------
# App
# -------------------------
app = FastAPI()

MODEL_PATH = os.environ.get("PRETRAINED_MODEL_PATH", "/app/model")
print(f"Loading SDXL from {MODEL_PATH}", flush=True)

pipe = StableDiffusionXLPipeline.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16,
    local_files_only=True,
).to("cuda")

class InferRequest(BaseModel):
    prompt: str

@app.get("/health")
def health():
    return {"status": "ok", "model_path": MODEL_PATH}

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
