"""
Parakeet v3 Speech-to-Text API Service

NVIDIA Parakeet-TDT-0.6B-v3 ASR model with FastAPI
Supports 25 languages including English, French, German, Spanish

Performance: 10x faster than Whisper, 2.1 GB VRAM
Cost Savings: 95% cheaper than OpenAI Whisper API
"""

import os
import time
import tempfile
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import torch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Parakeet v3 Speech-to-Text API",
    description="Self-hosted ASR service using NVIDIA Parakeet-TDT-0.6B-v3",
    version="1.0.0"
)

# Global model variable (loaded on startup)
asr_model = None
MODEL_NAME = "nvidia/parakeet-tdt-0.6b-v3"

# Supported languages (ISO 639-1 codes)
SUPPORTED_LANGUAGES = [
    "en", "fr", "de", "es", "it", "pt", "nl", "pl", "ru", "uk",
    "bg", "hr", "cs", "da", "et", "fi", "el", "hu", "lv", "lt",
    "mt", "ro", "sk", "sl", "sv"
]

# Response models
class TranscriptionResponse(BaseModel):
    text: str
    language: Optional[str] = None
    duration: float
    model: str = "parakeet-v3"
    success: bool = True

class HealthResponse(BaseModel):
    status: str
    model: str
    gpu_available: bool
    cuda_version: Optional[str] = None
    supported_languages: int

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    success: bool = False


@app.on_event("startup")
async def load_model():
    """Load Parakeet model on startup"""
    global asr_model

    try:
        logger.info(f"Loading Parakeet model: {MODEL_NAME}")
        logger.info(f"CUDA available: {torch.cuda.is_available()}")

        if torch.cuda.is_available():
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA version: {torch.version.cuda}")

        # Import NeMo ASR
        import nemo.collections.asr as nemo_asr

        # Load pre-trained model
        asr_model = nemo_asr.models.EncDecRNNTBPEModel.from_pretrained(
            model_name=MODEL_NAME
        )

        # Move to GPU if available
        if torch.cuda.is_available():
            asr_model = asr_model.cuda()
            logger.info("Model loaded on GPU")
        else:
            logger.warning("GPU not available, using CPU (will be slower)")

        # Set to evaluation mode
        asr_model.eval()

        logger.info(f"✅ Parakeet model loaded successfully")
        logger.info(f"Supported languages: {len(SUPPORTED_LANGUAGES)}")

    except Exception as e:
        logger.error(f"❌ Failed to load model: {str(e)}")
        raise


@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "service": "Parakeet v3 Speech-to-Text API",
        "version": "1.0.0",
        "model": MODEL_NAME,
        "status": "operational" if asr_model else "model not loaded"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if asr_model else "model not loaded",
        model=MODEL_NAME,
        gpu_available=torch.cuda.is_available(),
        cuda_version=torch.version.cuda if torch.cuda.is_available() else None,
        supported_languages=len(SUPPORTED_LANGUAGES)
    )


@app.get("/languages", response_model=dict)
async def list_languages():
    """List supported languages"""
    return {
        "supported_languages": SUPPORTED_LANGUAGES,
        "total": len(SUPPORTED_LANGUAGES),
        "note": "Language detection is automatic if not specified"
    }


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None)
):
    """
    Transcribe audio file to text

    Args:
        file: Audio file (wav, mp3, flac, ogg)
        language: Optional language code (en, fr, de, es, etc.)
                 If not provided, language is auto-detected

    Returns:
        TranscriptionResponse with text and metadata
    """

    if not asr_model:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please wait for startup to complete."
        )

    # Validate language if provided
    if language and language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Language '{language}' not supported. Supported: {SUPPORTED_LANGUAGES}"
        )

    temp_file = None

    try:
        start_time = time.time()

        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        logger.info(f"Transcribing file: {file.filename} ({len(content)} bytes)")
        if language:
            logger.info(f"Target language: {language}")

        # Transcribe using Parakeet
        # Note: Parakeet does automatic language detection
        # The model handles multilingual input natively
        transcription = asr_model.transcribe([temp_file_path])[0]

        # Calculate duration
        duration = time.time() - start_time

        logger.info(f"✅ Transcription complete in {duration:.2f}s")
        logger.info(f"Text length: {len(transcription)} characters")

        # Clean up temp file
        os.unlink(temp_file_path)

        return TranscriptionResponse(
            text=transcription,
            language=language if language else "auto-detected",
            duration=duration,
            model=MODEL_NAME
        )

    except Exception as e:
        logger.error(f"❌ Transcription failed: {str(e)}")

        # Clean up temp file if it exists
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@app.post("/transcribe-batch", response_model=dict)
async def transcribe_batch(
    files: list[UploadFile] = File(...),
    language: Optional[str] = Form(None)
):
    """
    Transcribe multiple audio files in batch

    Args:
        files: List of audio files
        language: Optional language code

    Returns:
        Dict with results for each file
    """

    if not asr_model:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )

    if len(files) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 files per batch request"
        )

    results = []
    temp_files = []

    try:
        start_time = time.time()

        # Save all files
        file_paths = []
        for uploaded_file in files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.filename).suffix) as temp_file:
                content = await uploaded_file.read()
                temp_file.write(content)
                file_paths.append(temp_file.name)
                temp_files.append(temp_file.name)

        # Batch transcribe
        logger.info(f"Batch transcribing {len(file_paths)} files")
        transcriptions = asr_model.transcribe(file_paths)

        duration = time.time() - start_time

        # Build results
        for idx, (uploaded_file, transcription) in enumerate(zip(files, transcriptions)):
            results.append({
                "filename": uploaded_file.filename,
                "text": transcription,
                "index": idx
            })

        # Clean up
        for temp_path in temp_files:
            os.unlink(temp_path)

        logger.info(f"✅ Batch transcription complete: {len(files)} files in {duration:.2f}s")

        return {
            "success": True,
            "count": len(results),
            "duration": duration,
            "results": results
        }

    except Exception as e:
        logger.error(f"❌ Batch transcription failed: {str(e)}")

        # Clean up temp files
        for temp_path in temp_files:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

        raise HTTPException(
            status_code=500,
            detail=f"Batch transcription failed: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "success": False
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8002,
        reload=False,
        workers=1
    )
