# ============================================
# RUNPOD PODS ENTRY SEAM (ASGI IMPORT)
# If you don't see the print below in logs,
# then this module is NOT the one being imported.
# ============================================
import os, sys, time

STAMP = os.environ.get("BUILD_ID", "NO_BUILD_ID")
print(f"???? IDENTITY GATE HIT — src/inference.py IMPORTED — STAMP={STAMP} — {time.time()} ????", flush=True)
print(f"DEBUG: INFERENCE_PATH={__file__}", flush=True)
print(f"DEBUG: CWD={os.getcwd()}", flush=True)
print(f"DEBUG: SYS_PATH_HEAD={sys.path[:5]}", flush=True)

from fastapi import FastAPI

# IMPORTANT: RunPod/uvicorn expects a module-level `app` object.
app = FastAPI()

@app.get("/health")
def health():
    return {
        "status": "ok",
        "stamp": STAMP,
        "inference_path": __file__,
        "cwd": os.getcwd(),
        "sys_path_head": sys.path[:5],
    }
