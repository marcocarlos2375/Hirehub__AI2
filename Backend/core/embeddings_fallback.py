"""
Embeddings Fallback Module
Provides Gemini text-embedding-004 → OpenAI text-embedding-3-small fallback.
"""

import os
from typing import List
from google import genai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize clients
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding_with_fallback(text: str) -> tuple[List[float], str]:
    """
    Generate embedding with Gemini, fall back to OpenAI on any error.

    Returns:
        tuple: (embedding_vector, provider_used)
        - embedding_vector: 768-dim vector (Gemini) or 1536-dim (OpenAI)
        - provider_used: "gemini" or "openai"
    """
    # Try Gemini first (768 dimensions)
    try:
        response = gemini_client.models.embed_content(
            model="text-embedding-004",
            contents=[text]
        )
        return response.embeddings[0].values, "gemini"

    except Exception as gemini_error:
        print(f"⚠️  Gemini embeddings failed: {gemini_error}. Falling back to OpenAI...")

        # Fall back to OpenAI (1536 dimensions)
        try:
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                dimensions=768  # Match Gemini's dimension for compatibility
            )
            return response.data[0].embedding, "openai"

        except Exception as openai_error:
            # Both failed - return zero vector as ultimate fallback
            print(f"⚠️  Both embedding providers failed. Returning zero vector.")
            return [0.0] * 768, "zero_fallback"

__all__ = ['get_embedding_with_fallback']
