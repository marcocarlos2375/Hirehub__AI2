"""
Input validation utilities.
"""

from typing import Optional, Tuple
from fastapi import HTTPException

from core.logging_config import logger


SUPPORTED_LANGUAGES = ["english", "french", "german", "spanish"]
MIN_TEXT_LENGTH = 50
MAX_TEXT_LENGTH = 6200


def validate_language(language: str) -> str:
    """
    Validate and normalize language parameter.

    Args:
        language: Language string to validate

    Returns:
        Normalized language string (lowercase, defaults to english if invalid)
    """
    if not language:
        return "english"

    normalized = language.lower().strip()

    if normalized not in SUPPORTED_LANGUAGES:
        logger.debug(f"Unsupported language '{language}', defaulting to english")
        return "english"

    return normalized


def validate_min_length(
    text: str,
    field_name: str = "text",
    min_length: int = MIN_TEXT_LENGTH
) -> None:
    """
    Validate that text meets minimum length requirement.

    Args:
        text: Text to validate
        field_name: Name of the field for error message
        min_length: Minimum required length

    Raises:
        HTTPException: If text is too short
    """
    if not text or len(text.strip()) < min_length:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must be at least {min_length} characters"
        )


def validate_text_input(
    text: str,
    field_name: str = "text",
    min_length: int = MIN_TEXT_LENGTH,
    max_length: int = MAX_TEXT_LENGTH
) -> str:
    """
    Validate and process text input.

    Args:
        text: Text to validate
        field_name: Name of the field for error message
        min_length: Minimum required length
        max_length: Maximum allowed length (text will be truncated)

    Returns:
        Validated and potentially truncated text

    Raises:
        HTTPException: If text is too short
    """
    validate_min_length(text, field_name, min_length)

    # Truncate if too long
    if len(text) > max_length:
        logger.info(f"{field_name} truncated from {len(text)} to {max_length} characters")
        return text[:max_length]

    return text


def detect_prompt_injection(text: str) -> Tuple[bool, Optional[str]]:
    """
    Basic detection of potential prompt injection patterns.
    This is a simple heuristic check, not a comprehensive security measure.

    Args:
        text: Text to check for injection patterns

    Returns:
        Tuple of (is_suspicious, reason)
    """
    import re

    suspicious_patterns = [
        (r'ignore\s+(the\s+)?(above|previous|all)', "Instruction override attempt"),
        (r'system\s+prompt', "System prompt reference"),
        (r'forget\s+(all|everything|previous)', "Memory reset attempt"),
        (r'new\s+instructions?:', "New instruction injection"),
        (r'you\s+are\s+now\s+a', "Role override attempt"),
    ]

    text_lower = text.lower()

    for pattern, reason in suspicious_patterns:
        if re.search(pattern, text_lower):
            logger.warning(f"Potential prompt injection detected: {reason}")
            return True, reason

    return False, None
