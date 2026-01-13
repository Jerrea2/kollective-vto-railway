print("???? IDENTITY GATE HIT — startup.py LOADED ????", flush=True)

import sys
import os

print(f"DEBUG: CWD={os.getcwd()}", flush=True)
print(f"DEBUG: sys.path={sys.path}", flush=True)

from src.inference import create_app
import uvicorn

app = create_app()

uvicorn.run(
    app,
    host="0.0.0.0",
    port=int(os.environ.get("UVICORN_PORT", "7860")),
)
