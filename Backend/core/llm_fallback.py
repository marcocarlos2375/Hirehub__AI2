"""
LLM Fallback Module
Provides Gemini → GPT-3.5 Turbo fallback for all text generation operations.
"""

import os
from typing import Optional, Dict, Any
from google import genai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize clients
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_with_fallback(
    prompt: str,
    model_gemini: str = "gemini-2.5-flash-lite",
    model_openai: str = "gpt-3.5-turbo",
    temperature: float = 0.2,
    **kwargs
) -> tuple[str, str]:
    """
    Generate text with Gemini, fall back to OpenAI GPT-3.5 on any error.

    Returns:
        tuple: (response_text, provider_used)
        - response_text: Generated text
        - provider_used: "gemini" or "openai"
    """
    # Try Gemini first
    try:
        response = gemini_client.models.generate_content(
            model=model_gemini,
            contents=prompt,
            config={"temperature": temperature, **kwargs}
        )
        return response.text, "gemini"

    except Exception as gemini_error:
        # Log Gemini failure
        print(f"⚠️  Gemini API failed: {gemini_error}. Falling back to OpenAI GPT-3.5...")

        # Fall back to OpenAI GPT-3.5
        try:
            response = openai_client.chat.completions.create(
                model=model_openai,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            return response.choices[0].message.content, "openai"

        except Exception as openai_error:
            # Both failed - raise critical error
            raise Exception(
                f"Both Gemini and OpenAI failed. "
                f"Gemini: {gemini_error}. OpenAI: {openai_error}"
            )

# Export gemini_client for compatibility
__all__ = ['generate_with_fallback', 'gemini_client', 'openai_client']
