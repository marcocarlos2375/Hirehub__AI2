import re


def normalize_text(text: str) -> str:
    """
    Remove unnecessary whitespace to reduce token count and improve API performance.

    This function:
    - Replaces multiple consecutive spaces with a single space
    - Replaces all newlines and tabs with single spaces
    - Strips leading and trailing whitespace
    - Preserves sentence structure and readability

    Args:
        text: The input text to normalize

    Returns:
        Normalized text with minimal whitespace
    """
    # Replace all types of whitespace (spaces, tabs, newlines) with single space
    text = re.sub(r'\s+', ' ', text)

    # Strip leading and trailing whitespace
    text = text.strip()

    return text


def estimate_token_count(text: str) -> int:
    """
    Rough estimate of token count (actual tokenization varies by model).
    Generally: ~4 characters per token for English text.

    Args:
        text: The input text

    Returns:
        Estimated token count
    """
    return len(text) // 4
