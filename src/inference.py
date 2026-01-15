# ============================================
# RUNPOD ASGI ENTRYPOINT
# ============================================
import os, sys, time
from fastapi import FastAPI

print("?? IDENTITY GATE HIT — src.inference IMPORTED", flush=True)
print(f"FILE={__file__}", flush=True)
print(f"CWD={os.getcwd()}", flush=True)
print(f"SYS_PATH={sys.path[:5]}", flush=True)

# ? THIS IS THE FIX
from .tryon_pipeline import StableDiffusionXLInpaintPipeline as TryonPipeline

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
