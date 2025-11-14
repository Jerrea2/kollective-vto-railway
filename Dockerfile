FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/models \
    HUGGINGFACE_HUB_CACHE=/models \
    UVICORN_HOST=0.0.0.0 \
    UVICORN_PORT=80 \
    ENABLE_ML=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 ca-certificates git curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Reuse pip layer cache by installing from your requirements file only
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# App code
COPY . /app

# Clone ONLY code for IDM-VTON (no LFS weights)
RUN git clone --depth 1 https://github.com/yisol/IDM-VTON /app/vendor/IDM-VTON && \
    rm -rf /app/vendor/IDM-VTON/.git
EXPOSE 8000
# Healthcheck hits your existing /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://127.0.0.1:8000/health || exit 1

# Download/verify weights at first run, then start API with your exact flags on port 80
CMD ["/bin/bash","-lc","python /app/startup.py && uvicorn inference:app --host 0.0.0.0 --port 80 --log-level debug --proxy-headers --forwarded-allow-ips=\"*\" --workers 1"]
