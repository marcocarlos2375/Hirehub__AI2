"""
Base response models for standardized API responses.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Base response model with common fields."""
    success: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """Standardized error response model."""
    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorCodes:
    """Standard error codes for the API."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    LLM_FAILURE = "LLM_FAILURE"
    PARSING_ERROR = "PARSING_ERROR"
    CACHE_ERROR = "CACHE_ERROR"
    NOT_FOUND = "NOT_FOUND"
    TIMEOUT = "TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
