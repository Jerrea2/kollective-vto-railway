FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Python deps (cacheable)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# CRITICAL: copy src exactly as it exists locally
COPY src /app/src

# HARD FAIL if inference.py is missing
RUN test -f /app/src/inference.py && ls -la /app/src

EXPOSE 8000

# ?? HARD PIN — PLATFORM CANNOT OVERRIDE THIS
ENTRYPOINT ["python3","-u","/app/src/inference.py"]
