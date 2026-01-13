# --- IDENTITY GATE ---
print("\n" + "!"*60)
print("?? IDENTITY GATE: 2026-01-05T00:00:00Z ??")
print("?? STATUS: BOOTSTRAPPING PACKAGE MODEL ??")
print("!"*60 + "\n")

import sys
import os

print(f"DEBUG: INFERENCE_PATH={__file__}")
print(f"DEBUG: CWD={os.getcwd()}")
print(f"DEBUG: SYS_PATH={sys.path}")

if "/app" not in sys.path:
    raise RuntimeError("IDENTITY_VIOLATION: /app not in sys.path")

try:
    import src.tryon_pipeline as tp
    print("?? ENGINE MODULE FOUND: src.tryon_pipeline")
except Exception as e:
    print(f"?? ENGINE MODULE FAILURE: {e}")
    raise

from fastapi import FastAPI

def create_app():
    app = FastAPI()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
