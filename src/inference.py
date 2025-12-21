import os, sys

print("=================================================")
print("[VTO] 🚨 IDENTITY GATE PASSED 🚨")
print("[VTO] FILE       :", __file__)
print("[VTO] REALPATH   :", os.path.realpath(__file__))
print("[VTO] CWD        :", os.getcwd())
print("[VTO] PYTHONPATH :")
for p in sys.path:
    print("   ", p)
print("=================================================")

from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "identity-ok", "file": os.path.realpath(__file__)}

@app.post("/tryon")
def tryon():
    raise RuntimeError("STOP — identity gate only")
