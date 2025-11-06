import os
from fastapi import FastAPI, Header, Response
import uvicorn

app = FastAPI()

# ---- Health/Ping: NO AUTH (for RunPod probe) ----
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ping")
def ping():
    return {"ok": True}

# ---- Example protected route (kept secured) ----
EXPECTED_KEY = os.environ.get("ENDPOINT_KEY", "").strip()

def check_key(header_val: str | None) -> bool:
    return (not EXPECTED_KEY) or (header_val and header_val.strip() == EXPECTED_KEY)

@app.get("/secure-check")
def secure_check(endpointkey: str | None = Header(default=None)):
    if not check_key(endpointkey):
        return Response(status_code=401)
    return {"secure": "ok"}

if __name__ == "__main__":
    uvicorn.run("inference:app", host="0.0.0.0", port=int(os.environ.get("PORT", "80")), workers=1)
