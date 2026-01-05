# --- LINE 1: NO IMPORTS ABOVE THIS ---
print("\n" + "!"*60)
print("?? IDENTITY GATE: 2026-01-05T00:00:00Z ??")
print("?? STATUS: BOOTSTRAPPING PACKAGE MODEL ??")
print("!"*60 + "\n")

import sys
import os

# Mandatory Path Audit
print(f"DEBUG: INFERENCE_PATH={__file__}")
print(f"DEBUG: CWD={os.getcwd()}")
print(f"DEBUG: SYS_PATH={sys.path}")

# HARD INVARIANT
if "/app" not in sys.path:
    raise RuntimeError("IDENTITY_VIOLATION: /app not in sys.path")

# Explicit Package Import (module first, then symbol)
try:
    import src.tryon_pipeline as tp
    print("? ENGINE MODULE FOUND: src.tryon_pipeline")
except Exception as e:
    print(f"? ENGINE MODULE FAILURE: {e}")
    raise

from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
