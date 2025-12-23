import os
import sys
print("======================================")
print("[IDENTITY] inference.py LOADED")
print("[IDENTITY] __file__ =", __file__)
print("[IDENTITY] cwd =", os.getcwd())
print("[IDENTITY] sys.path =", sys.path)
print("======================================")

from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
