import os, sys, json
from pathlib import Path

SDXL_DIR = Path(os.environ.get("SDXL_DIR", "/models/sdxl"))

def fail(msg):
    print(f"FAIL: {msg}", flush=True)
    sys.exit(1)

def pass_(msg):
    print(f"PASS: {msg}", flush=True)

print("=== SDXL BAKE VERIFICATION ===", flush=True)
print(f"Checking path: {SDXL_DIR}", flush=True)

if not SDXL_DIR.exists():
    fail("SDXL directory does not exist")

model_index = SDXL_DIR / "model_index.json"

if not model_index.exists():
    fail("model_index.json missing")

try:
    data = json.loads(model_index.read_text())
except Exception as e:
    fail(f"Invalid model_index.json: {e}")

if "_class_name" not in data:
    fail("model_index.json missing _class_name")

safetensors = list(SDXL_DIR.rglob("*.safetensors"))

if len(safetensors) == 0:
    fail("No .safetensors files found")

pass_("model_index.json valid")
pass_(f"Found {len(safetensors)} safetensors files")

print("=== RESULT: SDXL STRUCTURALLY BAKED ===", flush=True)
sys.exit(0)
