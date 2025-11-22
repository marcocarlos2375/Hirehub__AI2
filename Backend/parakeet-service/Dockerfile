# Parakeet v3 Speech-to-Text Service
# NVIDIA Parakeet-TDT-0.6B-v3 with NeMo Framework
# Supports 25 languages including English, French, German, Spanish

FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3-dev \
    git \
    wget \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install PyTorch with CUDA support
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install NeMo toolkit and dependencies
RUN pip3 install nemo_toolkit['asr']==2.0.0

# Install additional dependencies for Parakeet
RUN pip3 install \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    python-multipart==0.0.6 \
    pydantic==2.5.0 \
    numpy==1.24.3 \
    librosa==0.10.1 \
    soundfile==0.12.1 \
    omegaconf==2.3.0

# Copy application code
COPY app.py /app/
COPY requirements.txt /app/

# Create directory for model cache
RUN mkdir -p /app/models

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0
ENV NEMO_CACHE_DIR=/app/models

# Pre-download the Parakeet model (optional but recommended)
# Uncomment the following lines to download model during build:
# RUN python3 -c "import nemo.collections.asr as nemo_asr; \
#     model = nemo_asr.models.EncDecRNNTBPEModel.from_pretrained('nvidia/parakeet-tdt-0.6b-v3')"

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8002/health')" || exit 1

# Run the FastAPI application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "1"]
