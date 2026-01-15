# =========================================================
# RUNPOD ASGI ENTRYPOINT - HARD LOCKED
# =========================================================
import os, sys, time
from fastapi import FastAPI

STAMP = os.environ.get("BUILD_ID", "NO_BUILD_ID")

print(f"???? IDENTITY GATE HIT - src.inference IMPORTED - STAMP={STAMP} - T={time.time()} ????", flush=True)
print(f"FILE={__file__}", flush=True)
print(f"CWD={os.getcwd()}", flush=True)
print(f"SYS_PATH_HEAD={sys.path[:8]}", flush=True)

# CRITICAL: package-relative import (requires src/ to be a package)
from .tryon_pipeline import StableDiffusionXLInpaintPipeline as TryonPipeline

app = FastAPI()

@app.get("/health")
def health():
    return {
        "status": "ok",
        "stamp": STAMP,
        "file": __file__,
        "cwd": os.getcwd(),
        "sys_path_head": sys.path[:8],
    }
