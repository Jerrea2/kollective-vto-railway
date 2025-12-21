FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime

# -----------------------------
# System deps
# -----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    ca-certificates \
    git \
    curl \
 && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Workdir
# -----------------------------
WORKDIR /app

# -----------------------------
# Python deps
# -----------------------------
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# -----------------------------
# 🔥 HARD CACHE BREAK (REAL ONE)
# This file NEVER exists before build
# -----------------------------
RUN date > /app/__cache_bust__

# -----------------------------
# App code (FORCED COPY)
# -----------------------------
COPY . /app

# -----------------------------
# Vendor repo
# -----------------------------
RUN git clone --depth 1 https://github.com/yisol/IDM-VTON /app/vendor/IDM-VTON && \
    rm -rf /app/vendor/IDM-VTON/.git

# -----------------------------
# Server (EXPLICIT)
# -----------------------------
EXPOSE 8000
CMD ["uvicorn", "src.inference:app", "--host", "0.0.0.0", "--port", "8000"]
