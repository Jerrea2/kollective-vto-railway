import os, time
from pathlib import Path
from huggingface_hub import snapshot_download

# use HF_HOME if set, fallback to /app/hf-cache
MODELS_DIR = Path(os.environ.get("HF_HOME", "/app/hf-cache"))
IDM_DIR = MODELS_DIR / "yisol__IDM-VTON"
READY_FLAG = IDM_DIR / ".READY"

def ensure_models():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id="yisol/IDM-VTON",
        local_dir=str(IDM_DIR),
        local_dir_use_symlinks=False,
        resume_download=True,
        max_workers=4,
    )
    READY_FLAG.write_text(str(time.time()))

def quick_warmup():
    import torch
    print("[startup] torch", torch.__version__, "cuda:", torch.cuda.is_available(), flush=True)

if __name__ == "__main__":
    print("[startup] Ensuring IDM-VTON weights in", IDM_DIR, flush=True)
    ensure_models()
    quick_warmup()
    print("[startup] Models ready.", flush=True)
