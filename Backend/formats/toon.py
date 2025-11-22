"""
TOON format utilities for LLM token optimization
"""

try:
    from toon_format import encode, decode, estimate_savings, compare_formats
    TOON_AVAILABLE = True
except ImportError:
    TOON_AVAILABLE = False
    print("Warning: toon-format not installed. Install with: pip install git+https://github.com/toon-format/toon-python.git")

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    print("Warning: tiktoken not installed. Install with: pip install tiktoken")


def to_toon(data: dict | list | str) -> str:
    """
    Convert Python data structure to TOON format.

    Args:
        data: Python dict, list, or string to convert

    Returns:
        TOON-formatted string
    """
    if not TOON_AVAILABLE:
        raise ImportError("toon-format not installed")

    if isinstance(data, str):
        # If already a string, return as-is
        return data

    return encode(data)


def from_toon(toon_str: str) -> dict | list:
    """
    Parse TOON format string to Python data structure.

    Args:
        toon_str: TOON-formatted string

    Returns:
        Python dict or list
    """
    if not TOON_AVAILABLE:
        raise ImportError("toon-format not installed")

    return decode(toon_str)


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count tokens in text using tiktoken.

    Args:
        text: Text to count tokens for
        model: Model name for tokenizer (default: gpt-4)

    Returns:
        Token count
    """
    if not TIKTOKEN_AVAILABLE:
        # Rough estimate: ~4 characters per token
        return len(text) // 4

    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        # Fallback to cl100k_base (GPT-4/ChatGPT)
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))


def compare_json_vs_toon(data: dict | list) -> dict:
    """
    Compare JSON vs TOON format for token efficiency.

    Args:
        data: Python data structure to compare

    Returns:
        Dict with comparison metrics
    """
    import json

    if not TOON_AVAILABLE:
        raise ImportError("toon-format not installed")

    # Convert to both formats
    json_str = json.dumps(data)
    toon_str = encode(data)

    # Count tokens
    json_tokens = count_tokens(json_str)
    toon_tokens = count_tokens(toon_str)

    # Calculate savings
    token_reduction = json_tokens - toon_tokens
    percent_reduction = (token_reduction / json_tokens * 100) if json_tokens > 0 else 0

    return {
        "json_size": len(json_str),
        "toon_size": len(toon_str),
        "json_tokens": json_tokens,
        "toon_tokens": toon_tokens,
        "size_reduction_bytes": len(json_str) - len(toon_str),
        "size_reduction_percent": ((len(json_str) - len(toon_str)) / len(json_str) * 100) if len(json_str) > 0 else 0,
        "token_reduction": token_reduction,
        "token_reduction_percent": percent_reduction,
        "json_sample": json_str[:200] + "..." if len(json_str) > 200 else json_str,
        "toon_sample": toon_str[:200] + "..." if len(toon_str) > 200 else toon_str
    }


def format_comparison_table(comparison: dict) -> str:
    """
    Format comparison results as a readable table.

    Args:
        comparison: Output from compare_json_vs_toon()

    Returns:
        Formatted table string
    """
    return f"""
╔══════════════════════════════════════════════════════════════╗
║                  JSON vs TOON COMPARISON                      ║
╚══════════════════════════════════════════════════════════════╝

📏 SIZE:
   JSON:  {comparison['json_size']:>6} bytes
   TOON:  {comparison['toon_size']:>6} bytes
   Saved: {comparison['size_reduction_bytes']:>6} bytes ({comparison['size_reduction_percent']:.1f}% smaller)

🎯 TOKENS:
   JSON:  {comparison['json_tokens']:>6} tokens
   TOON:  {comparison['toon_tokens']:>6} tokens
   Saved: {comparison['token_reduction']:>6} tokens ({comparison['token_reduction_percent']:.1f}% reduction)

📄 SAMPLES:
   JSON: {comparison['json_sample']}
   TOON: {comparison['toon_sample']}
"""
