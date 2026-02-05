import os
import torch
from fastapi import FastAPI
from diffusers import StableDiffusionXLPipeline

# ============================
# IDENTITY GATE (MUST PRINT ONCE)
# ============================
print("🚨🚨 IDENTITY GATE HIT — src.inference IMPORTED 🚨🚨", flush=True)
print(f"FILE={__file__}", flush=True)
print(f"CWD={os.getcwd()}", flush=True)
print(f"SYS_PATH_HEAD={os.sys.path[:3]}", flush=True)

# ============================
# APP INIT
# ============================
app = FastAPI()

# ============================
# SDXL LOCALITY (DETERMINISTIC)
# ============================
SDXL_PATH = "/workspace/models/sdxl"

print(f"Loading SDXL from local path: {SDXL_PATH}", flush=True)

pipe = StableDiffusionXLPipeline.from_pretrained(
    SDXL_PATH,
    torch_dtype=torch.float16,
    local_files_only=True,
).to("cuda")

print("SDXL loaded successfully on CUDA", flush=True)

# ============================
# HEALTH CHECK
# ============================
@app.get("/health")
def health():
    return {
        "status": "ok",
        "sdxl_path": SDXL_PATH,
        "cuda_available": torch.cuda.is_available(),
        "device_count": torch.cuda.device_count(),
    }

# ============================
# PLACEHOLDER INFERENCE ROUTE
# (DO NOT CALL UNTIL STEP 2 PASS)
# ============================
@app.post("/infer")
def infer():
    return {"error": "Inference disabled until SDXL locality gate passes"}
