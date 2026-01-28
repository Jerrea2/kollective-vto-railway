# ============================================================
# RUNPOD ASGI ENTRYPOINT - HARD LOCKED
# ============================================================

import os
import sys
import time

import torch
from fastapi import FastAPI
from pydantic import BaseModel

# ------------------------------------------------------------
# Identity Gate (DO NOT MOVE / DO NOT MODIFY)
# ------------------------------------------------------------
STAMP = os.environ.get("BUILD_ID", "NO_BUILD_ID")

print(
    f"???? IDENTITY GATE HIT - src.inference IMPORTED - STAMP={STAMP} - T={time.time()} ????",
    flush=True,
)
print(f"FILE={__file__}", flush=True)
print(f"CWD={os.getcwd()}", flush=True)
print(f"SYS_PATH_HEAD={sys.path[:8]}", flush=True)

# ------------------------------------------------------------
# Pipeline Import (package-relative)
# ------------------------------------------------------------
from .tryon_pipeline import StableDiffusionXLInpaintPipeline as TryonPipeline

# ------------------------------------------------------------
# FastAPI App
# ------------------------------------------------------------
app = FastAPI()

# ------------------------------------------------------------
# Health Check (local-only, dev verification)
# ------------------------------------------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "stamp": STAMP,
        "file": __file__,
        "cwd": os.getcwd(),
        "sys_path_head": sys.path[:8],
    }

# ------------------------------------------------------------
# Minimal Inference Route (INTENTIONALLY NAIVE)
# ------------------------------------------------------------
class InferRequest(BaseModel):
    debug: bool = True


@app.post("/infer")
def infer(req: InferRequest):
    """
    Minimal inference entrypoint.
    Purpose: prove routing + surface next real runtime error.
    """

    print(">>> /infer endpoint hit", flush=True)

    # We intentionally require an explicit model path/id to avoid guessing.
    # This forces a clean, deterministic next error if not configured.
    model_ref = (
        os.environ.get("PRETRAINED_MODEL_PATH")
        or os.environ.get("MODEL_PATH")
        or os.environ.get("MODEL_ID")
    )

    print(f">>> MODEL_REF={model_ref}", flush=True)

    if not model_ref:
        raise RuntimeError(
            "MODEL PATH NOT SET. Set PRETRAINED_MODEL_PATH (preferred) "
            "or MODEL_PATH or MODEL_ID to a local directory or HF model id."
        )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f">>> torch.cuda.is_available()={torch.cuda.is_available()} device={device}", flush=True)

    print(">>> Constructing TryonPipeline via from_pretrained()", flush=True)
    pipe = TryonPipeline.from_pretrained(
        model_ref,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    )

    print(f">>> Moving pipeline to device: {device}", flush=True)
    pipe = pipe.to(device)

    # Not running inference yet — just proving construction is possible.
    return {
        "status": "pipeline_loaded",
        "model_ref": model_ref,
        "device": device,
        "pipeline_type": str(type(pipe)),
    }
