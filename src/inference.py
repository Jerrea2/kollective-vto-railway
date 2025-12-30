import sys
print("🚨🚨🚨 IDENTITY GATE HIT — src/inference.py IMPORTED 🚨🚨🚨")
sys.stdout.flush()

from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
