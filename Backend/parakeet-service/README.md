# Parakeet v3 Speech-to-Text Service

Self-hosted speech recognition service using NVIDIA Parakeet-TDT-0.6B-v3 model.

## Overview

This service provides a REST API for audio transcription using the open-source Parakeet v3 model from NVIDIA. It offers significant cost savings compared to cloud APIs while maintaining high accuracy.

### Key Features

- **25 Language Support**: English, French, German, Spanish, and 21 other European languages
- **High Performance**: 10x faster than OpenAI Whisper
- **Low Resource Usage**: Only 2.1 GB VRAM required
- **Automatic Language Detection**: No need to specify language
- **Cost Savings**: 95% cheaper than OpenAI Whisper API
- **GPU Accelerated**: Optimized for NVIDIA GPUs

### Supported Languages

`en` (English), `fr` (French), `de` (German), `es` (Spanish), `it` (Italian), `pt` (Portuguese), `nl` (Dutch), `pl` (Polish), `ru` (Russian), `uk` (Ukrainian), `bg` (Bulgarian), `hr` (Croatian), `cs` (Czech), `da` (Danish), `et` (Estonian), `fi` (Finnish), `el` (Greek), `hu` (Hungarian), `lv` (Latvian), `lt` (Lithuanian), `mt` (Maltese), `ro` (Romanian), `sk` (Slovak), `sl` (Slovenian), `sv` (Swedish)

## Requirements

### Hardware

**Minimum**:
- NVIDIA GPU with 3+ GB VRAM
- CUDA Compute Capability 7.0+
- 8 GB system RAM
- 10 GB disk space

**Recommended**:
- NVIDIA T4 or better
- 16 GB system RAM
- SSD storage

### Software

- Docker with NVIDIA Container Runtime
- Docker Compose
- NVIDIA drivers (525.x or newer)
- CUDA 12.1+

## Installation

### 1. Install NVIDIA Container Runtime

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### 2. Verify GPU Access

```bash
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

You should see your GPU listed.

### 3. Build and Run

The Parakeet service is already configured in `docker-compose.yml`. Simply run:

```bash
cd Backend
docker-compose up -d parakeet
```

**Note**: First startup will download the Parakeet model (~2.3 GB) which may take 5-10 minutes depending on your internet connection.

## Usage

### API Endpoints

#### POST /transcribe

Transcribe an audio file to text.

**Request**:
```bash
curl -X POST http://localhost:8002/transcribe \
  -F "file=@audio.mp3" \
  -F "language=en"
```

**Response**:
```json
{
  "text": "This is the transcribed text",
  "language": "en",
  "duration": 0.15,
  "model": "parakeet-v3",
  "success": true
}
```

**Parameters**:
- `file` (required): Audio file (wav, mp3, flac, ogg, webm)
- `language` (optional): Target language code (e.g., "en", "fr", "de", "es")

#### GET /health

Check service health and GPU status.

**Request**:
```bash
curl http://localhost:8002/health
```

**Response**:
```json
{
  "status": "healthy",
  "model": "nvidia/parakeet-tdt-0.6b-v3",
  "gpu_available": true,
  "cuda_version": "12.1",
  "supported_languages": 25
}
```

#### GET /languages

List all supported languages.

**Request**:
```bash
curl http://localhost:8002/languages
```

**Response**:
```json
{
  "supported_languages": ["en", "fr", "de", "es", ...],
  "total": 25,
  "note": "Language detection is automatic if not specified"
}
```

## Integration with Main API

The main HireHub API automatically uses Parakeet when `USE_PARAKEET=true` is set in `.env`.

### Environment Variables

Add to `Backend/.env`:

```env
# Enable Parakeet
USE_PARAKEET=true

# Parakeet service URL
PARAKEET_URL=http://parakeet:8002
```

### Fallback Behavior

If Parakeet fails, the system automatically falls back to OpenAI Whisper API. This ensures reliability while you're testing or if the GPU service is temporarily unavailable.

## Performance

### Speed Comparison

| Model | Time for 2-min audio | Real-Time Factor |
|-------|---------------------|------------------|
| **Parakeet v3 (GPU)** | 0.12s | 1000x |
| OpenAI Whisper API | 2-4s | 30-60x |
| Whisper Large (local) | 12s | 10x |

### Accuracy

- **Word Error Rate**: 6-8% for clean audio
- **Noisy environments**: 21% WER (vs Whisper's 30%)
- **Best for**: English, Spanish, Italian (5-6% WER)
- **Good for**: French, German (7-8% WER)

## Monitoring

### Check Logs

```bash
docker-compose logs -f parakeet
```

### View Resource Usage

```bash
docker stats parakeet-service-parakeet-1
```

### GPU Monitoring

```bash
watch -n 1 nvidia-smi
```

## Troubleshooting

### Service Won't Start

**Problem**: `docker-compose up parakeet` fails

**Solutions**:
1. Check GPU access: `docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi`
2. Verify NVIDIA Container Runtime is installed
3. Check CUDA version compatibility (need 12.1+)
4. Ensure sufficient disk space for model download (3 GB)

### Out of Memory

**Problem**: CUDA out of memory error

**Solutions**:
1. Check GPU VRAM: `nvidia-smi` (need 3+ GB free)
2. Close other GPU applications
3. Restart Docker: `sudo systemctl restart docker`
4. Use smaller batch sizes if processing multiple files

### Slow Transcription

**Problem**: Taking longer than expected

**Possible causes**:
1. Running on CPU instead of GPU (check logs for "using CPU")
2. GPU is busy with other processes
3. Large audio files (>10 minutes)

**Solutions**:
1. Verify GPU is detected: `curl http://localhost:8002/health`
2. Check `nvidia-smi` for GPU utilization
3. Split large files into smaller chunks

### Model Download Fails

**Problem**: Error downloading Parakeet model

**Solutions**:
1. Check internet connection
2. Retry: `docker-compose restart parakeet`
3. Manually download and cache:
   ```python
   import nemo.collections.asr as nemo_asr
   model = nemo_asr.models.EncDecRNNTBPEModel.from_pretrained('nvidia/parakeet-tdt-0.6b-v3')
   ```

## Cost Analysis

### Monthly Cost Comparison (100,000 requests, 2 min each)

| Solution | Monthly Cost | Savings |
|----------|--------------|---------|
| OpenAI Whisper API | $1,200 | - |
| Parakeet (Cloud Run GCP) | $77 | **$1,123** (94%) |
| Parakeet (T4 VM GCP) | $239 | **$961** (80%) |
| Parakeet (self-hosted) | $0* | **$1,200** (100%) |

*Electricity costs for GPU usage not included

### Resource Requirements

**For 100,000 requests/month (200,000 minutes of audio)**:
- Processing time: ~20 hours GPU time
- VRAM: 2.1 GB constant
- Storage: 3 GB (model) + temporary audio files

## Development

### Local Testing

```bash
cd Backend/parakeet-service
python3 app.py
```

### Run Without Docker

```bash
# Install dependencies
pip install -r requirements.txt
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Run service
python3 app.py
```

Access at `http://localhost:8002`

## Model Information

- **Model**: nvidia/parakeet-tdt-0.6b-v3
- **Architecture**: FastConformer-TDT (Token-and-Duration Transducer)
- **Parameters**: 600 million
- **Training Data**: 1.7M hours multilingual audio
- **License**: CC-BY-4.0 (commercial use allowed)
- **Framework**: NVIDIA NeMo

## Support

For issues specific to:
- **Parakeet model**: https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3
- **NeMo framework**: https://github.com/NVIDIA/NeMo
- **This service**: Create an issue in your repository

## License

This service wrapper is part of the HireHub project. The Parakeet model is licensed under CC-BY-4.0 by NVIDIA.
