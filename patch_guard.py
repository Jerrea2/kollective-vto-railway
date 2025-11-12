from pathlib import Path

p = Path("tryon_pipeline.py")
s = p.read_text(encoding="utf-8")

# Ensure imports
if "from fastapi import Request" not in s:
    s = s.replace("from fastapi import", "from fastapi import Request,")
if "from fastapi.responses import JSONResponse" not in s:
    s = "from fastapi.responses import JSONResponse\n" + s

block = """
# --- CPU guard for /tryon (auto-injected by Andy) ---
import torch
from fastapi import Request
from fastapi.responses import JSONResponse

@app.middleware("http")
async def _gpu_required_guard(request: Request, call_next):
    # Intercept any route containing "tryon" before body parsing/validation.
    if ("tryon" in request.url.path.lower()) and (not torch.cuda.is_available()):
        return JSONResponse(status_code=503, content={"detail": "GPU required"})
    return await call_next(request)
# --- end guard ---
"""

if "_gpu_required_guard" not in s:
    s = s.rstrip() + "\n" + block + "\n"

p.write_text(s, encoding="utf-8")
print("OK: guard present")
