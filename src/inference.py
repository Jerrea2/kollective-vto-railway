import sys
import os
import logging

logging.basicConfig(level=logging.WARNING, force=True)

logging.warning("?????? IDENTITY GATE HIT ??????")
logging.warning(f"inference.py path: {__file__}")
logging.warning(f"cwd: {os.getcwd()}")
logging.warning(f"sys.path: {sys.path}")

from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}


