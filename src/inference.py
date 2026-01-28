# ============================================================
# RUNPOD ASGI ENTRYPOINT - HARD LOCKED
# ============================================================

import os
import sys
import time
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
    Purpose: prove routing + surface first real runtime error.
    """

    print(">>> /infer endpoint hit", flush=True)

    print(">>> Instantiating TryonPipeline", flush=True)
    pipe = TryonPipeline()

    return {
        "status": "entered_infer",
        "pipeline_type": str(type(pipe)),
    }
