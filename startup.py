# startup.py — authoritative PID-1 entrypoint

import os
import sys

# ---- IDENTITY GATE (MUST PRINT) ----
print("???? IDENTITY GATE HIT — startup.py LOADED ????", flush=True)
print(f"PID: {os.getpid()}", flush=True)
print(f"Python: {sys.executable}", flush=True)
print(f"CWD: {os.getcwd()}", flush=True)

# ---- IMPORT APP (MUST EXECUTE) ----
print("Importing inference module...", flush=True)
import inference  # identity gate inside inference MUST print

# ---- START SERVER (PID-1) ----
print("Starting uvicorn via startup.py (PID-1)...", flush=True)

import uvicorn

HOST = os.environ.get("UVICORN_HOST", "0.0.0.0")
PORT = int(os.environ.get("UVICORN_PORT", "7860"))

uvicorn.run(
    "inference:app",
    host=HOST,
    port=PORT,
    log_level="info",
)
