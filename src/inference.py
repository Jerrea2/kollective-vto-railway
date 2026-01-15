# =========================================================
# RUNPOD ASGI ENTRYPOINT — HARD LOCKED
# =========================================================

import os
import sys
import time
from fastapi import FastAPI

# -------- IDENTITY GATE (MUST PRINT) --------
print("???? IDENTITY GATE HIT — src.inference IMPORTED ????", flush=True)
print(f"FILE={__file__}", flush=True)
print(f"CWD={os.getcwd()}", flush=True)
print(f"SYS_PATH_HEAD={sys.path[:5]}", flush=True)

# -------- CRITICAL RELATIVE IMPORT (THIS IS THE FIX) --------
from .tryon_pipeline import StableDiffusionXLInpaintPipeline as TryonPipeline

# -------- APP --------
app = FastAPI()

@app.get("/health")
def health():
    return {
        "status": "ok",
        "stamp": time.time(),
        "file": __file__,
        "cwd": os.getcwd(),
        "sys_path_head": sys.path[:5],
    }
