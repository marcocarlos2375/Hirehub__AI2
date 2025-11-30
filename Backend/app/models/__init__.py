"""
Pydantic models for the HireHubAI Backend API.
"""

from app.models.base import BaseResponse, ErrorResponse
from app.models.parsing import (
    ParseRequest,
    ParseResponse,
    CVParseRequest,
    CVParseResponse,
)

__all__ = [
    'BaseResponse',
    'ErrorResponse',
    'ParseRequest',
    'ParseResponse',
    'CVParseRequest',
    'CVParseResponse',
]
