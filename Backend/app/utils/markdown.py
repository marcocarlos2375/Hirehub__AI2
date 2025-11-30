"""
Markdown processing utilities.
Single source of truth for markdown cleanup functions.
"""


def strip_markdown_code_blocks(text: str) -> str:
    """
    Remove markdown code blocks from text.
    This is commonly needed when parsing LLM responses that may be wrapped in markdown.

    Args:
        text: Text that may contain markdown code blocks

    Returns:
        Cleaned text with markdown code blocks removed

    Examples:
        >>> strip_markdown_code_blocks("```json\\n{\"key\": \"value\"}\\n```")
        '{"key": "value"}'
        >>> strip_markdown_code_blocks("```\\nsome text\\n```")
        'some text'
    """
    if not text:
        return ""

    cleaned = text.strip()

    # Check if the text starts with a code block
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")

        # Remove the opening ``` (and optional language specifier like ```json)
        if len(lines) > 1:
            lines = lines[1:]

        # Handle closing ```
        if lines and lines[-1].strip() == "```":
            # Remove standalone closing ```
            lines = lines[:-1]
        elif lines and lines[-1].strip().endswith("```"):
            # Remove trailing ``` from last line
            lines[-1] = lines[-1].replace("```", "").strip()

        cleaned = "\n".join(lines).strip()

    return cleaned


def extract_json_from_text(text: str) -> str:
    """
    Extract JSON content from text that may contain additional content.
    Looks for the first '{' and last '}' to extract JSON object,
    or first '[' and last ']' for JSON array.

    Args:
        text: Text that may contain JSON embedded in other content

    Returns:
        Extracted JSON string or original text if no JSON found
    """
    if not text:
        return ""

    cleaned = strip_markdown_code_blocks(text)

    # Try to find JSON object
    first_brace = cleaned.find('{')
    last_brace = cleaned.rfind('}')

    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return cleaned[first_brace:last_brace + 1]

    # Try to find JSON array
    first_bracket = cleaned.find('[')
    last_bracket = cleaned.rfind(']')

    if first_bracket != -1 and last_bracket != -1 and last_bracket > first_bracket:
        return cleaned[first_bracket:last_bracket + 1]

    return cleaned


def truncate_text(text: str, max_length: int = 6200) -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum allowed length

    Returns:
        Truncated text
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length]
