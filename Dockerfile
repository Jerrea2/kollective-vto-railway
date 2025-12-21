FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime

# -----------------------------
# System deps
# -----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends `
    libgl1 `
    libglib2.0-0 `
    ca-certificates `
    git `
    curl `
 && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Workdir
# -----------------------------
WORKDIR /app

# -----------------------------
# Python deps
# -----------------------------
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && `
    pip install --no-cache-dir -r /app/requirements.txt

# -----------------------------
# 🚨 CACHE BUST (NON-NEGOTIABLE)
# Change this value ANY time code must update
# -----------------------------
ARG CACHEBUST=2025-12-21T-ID-GATE

# -----------------------------
# App code (FORCES COPY)
# -----------------------------
COPY . /app

# -----------------------------
# Vendor model repo
# -----------------------------
RUN git clone --depth 1 https://github.com/yisol/IDM-VTON /app/vendor/IDM-VTON && `
    rm -rf /app/vendor/IDM-VTON/.git

# -----------------------------
# Server
# -----------------------------
EXPOSE 8000
CMD ["uvicorn", "src.inference:app", "--host", "0.0.0.0", "--port", "8000"]
