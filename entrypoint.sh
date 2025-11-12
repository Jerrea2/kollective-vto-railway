#!/usr/bin/env bash
set -euo pipefail

pip_retry() {
  local max=5 n=1
  until python -m pip install --no-cache-dir "$@"; do
    if (( n == max )); then
      echo "pip install failed after $max attempts: $*" >&2
      exit 1
    fi
    echo "pip failed (attempt $n) – retrying in $((10*n))s..."
    sleep $((10*n))
    n=$((n+1))
  done
}

if [[ "${RUNTIME_GPU:-0}" == "1" ]]; then
  echo "[startup] Installing CUDA wheels (torch/torchvision/torchaudio)..."
  pip_retry --extra-index-url https://download.pytorch.org/whl/cu121 \
    torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1
else
  echo "[startup] RUNTIME_GPU != 1 - skipping CUDA wheels."
fi

echo "[startup] Launching inference.py ..."
exec python /app/inference.py
