# syntax=docker/dockerfile:1.6

############################
# STAGE 1 — Bake SDXL
############################
FROM python:3.10-slim AS sdxl_bake

ARG SDXL_REPO=stabilityai/stable-diffusion-xl-base-1.0
ARG SDXL_REVISION=main
ARG SDXL_DIR=/models/sdxl

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir huggingface_hub==0.25.2

RUN --mount=type=secret,id=HF_TOKEN \
    export HF_TOKEN=$(cat /run/secrets/HF_TOKEN) && \
    python - << 'PY'
import os
from huggingface_hub import snapshot_download

repo_id = os.environ["SDXL_REPO"]
revision = os.environ["SDXL_REVISION"]
local_dir = os.environ["SDXL_DIR"]
token = os.environ["HF_TOKEN"]

snapshot_download(
    repo_id=repo_id,
    revision=revision,
    local_dir=local_dir,
    local_dir_use_symlinks=False,
    token=token
)

print("SDXL baked into:", local_dir)
PY

RUN test -f ${SDXL_DIR}/model_index.json

############################
# STAGE 2 — Runtime (Offline)
############################
FROM python:3.10-slim AS runtime

ARG SDXL_DIR=/models/sdxl
ENV SDXL_DIR=${SDXL_DIR}

ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1
ENV HF_DATASETS_OFFLINE=1
ENV HF_HUB_DISABLE_TELEMETRY=1

RUN pip install --no-cache-dir \
    torch==2.2.2 \
    diffusers==0.30.3 \
    transformers==4.44.2 \
    safetensors==0.4.5 \
    accelerate==0.33.0

COPY --from=sdxl_bake /models/sdxl /models/sdxl
COPY verify_sdxl_baked.py /opt/verify_sdxl_baked.py

CMD ["python", "/opt/verify_sdxl_baked.py"]
