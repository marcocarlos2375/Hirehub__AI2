"""
LLM Fallback Module with Retry Logic.
Provides Gemini → GPT-4o-mini fallback for all text generation operations.
Uses tenacity for exponential backoff retry on transient failures.
"""

from typing import Optional, Dict, Any, Tuple
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryError
)
import httpx

from core.config.logging_config import logger
from core.config.settings import settings
from core.config.clients import get_gemini_client, get_openai_client


# Define transient exceptions that should trigger retry
TRANSIENT_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    httpx.TimeoutException,
    httpx.ConnectError,
    httpx.ReadTimeout,
)


def _call_gemini(
    prompt: str,
    model: str,
    temperature: float,
    **kwargs
) -> str:
    """
    Call Gemini API with retry logic for transient failures.

    Args:
        prompt: The prompt text
        model: Gemini model name
        temperature: Generation temperature
        **kwargs: Additional config options

    Returns:
        Generated text response

    Raises:
        Exception: If all retries fail
    """
    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(
            multiplier=1,
            min=settings.retry_min_wait,
            max=settings.retry_max_wait
        ),
        retry=retry_if_exception_type(TRANSIENT_EXCEPTIONS),
        before_sleep=before_sleep_log(logger, "WARNING"),
        reraise=True
    )
    def _call_with_retry():
        client = get_gemini_client()
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={"temperature": temperature, **kwargs}
        )
        return response.text

    return _call_with_retry()


def _call_openai(
    prompt: str,
    model: str,
    temperature: float
) -> str:
    """
    Call OpenAI API with retry logic for transient failures.

    Args:
        prompt: The prompt text
        model: OpenAI model name
        temperature: Generation temperature

    Returns:
        Generated text response

    Raises:
        Exception: If all retries fail
    """
    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(
            multiplier=1,
            min=settings.retry_min_wait,
            max=settings.retry_max_wait
        ),
        retry=retry_if_exception_type(TRANSIENT_EXCEPTIONS),
        before_sleep=before_sleep_log(logger, "WARNING"),
        reraise=True
    )
    def _call_with_retry():
        client = get_openai_client()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content

    return _call_with_retry()


def generate_with_fallback(
    prompt: str,
    model_gemini: str = None,
    model_openai: str = None,
    temperature: float = None,
    **kwargs
) -> Tuple[str, str]:
    """
    Generate text with Gemini, fall back to OpenAI GPT-4o-mini on any error.
    Includes retry logic with exponential backoff for transient failures.

    Args:
        prompt: The prompt text to send
        model_gemini: Gemini model name (default from settings)
        model_openai: OpenAI model name (default from settings)
        temperature: Generation temperature (default from settings)
        **kwargs: Additional config options for Gemini

    Returns:
        tuple: (response_text, provider_used)
            - response_text: Generated text
            - provider_used: "gemini" or "openai"

    Raises:
        Exception: If both providers fail after all retries
    """
    # Use settings defaults if not specified
    model_gemini = model_gemini or settings.parsing_model
    model_openai = model_openai or settings.fallback_model
    temperature = temperature if temperature is not None else settings.parsing_temperature

    # Try Gemini first (with retry)
    gemini_error = None
    try:
        response = _call_gemini(prompt, model_gemini, temperature, **kwargs)
        logger.debug(f"Gemini generation successful using {model_gemini}")
        return response, "gemini"

    except RetryError as e:
        # All retries exhausted
        gemini_error = e.last_attempt.exception()
        logger.warning(
            f"Gemini API failed after {settings.max_retries} retries: {gemini_error}. "
            f"Falling back to OpenAI {model_openai}..."
        )

    except Exception as e:
        # Non-retryable error
        gemini_error = e
        logger.warning(
            f"Gemini API failed (non-retryable): {e}. "
            f"Falling back to OpenAI {model_openai}..."
        )

    # Fall back to OpenAI (with retry)
    try:
        response = _call_openai(prompt, model_openai, temperature)
        logger.info(f"OpenAI fallback successful using {model_openai}")
        return response, "openai"

    except RetryError as e:
        openai_error = e.last_attempt.exception()
        logger.error(
            f"Both Gemini and OpenAI failed after retries. "
            f"Gemini: {gemini_error}. OpenAI: {openai_error}"
        )
        raise Exception(
            f"Both Gemini and OpenAI failed after retries. "
            f"Gemini: {gemini_error}. OpenAI: {openai_error}"
        )

    except Exception as openai_error:
        logger.error(
            f"Both Gemini and OpenAI failed. "
            f"Gemini: {gemini_error}. OpenAI: {openai_error}"
        )
        raise Exception(
            f"Both Gemini and OpenAI failed. "
            f"Gemini: {gemini_error}. OpenAI: {openai_error}"
        )


# Async version for future use
async def generate_with_fallback_async(
    prompt: str,
    model_gemini: str = None,
    model_openai: str = None,
    temperature: float = None,
    **kwargs
) -> Tuple[str, str]:
    """
    Async version of generate_with_fallback.
    Currently wraps sync version, can be optimized later with native async clients.
    """
    import asyncio
    return await asyncio.to_thread(
        generate_with_fallback,
        prompt,
        model_gemini,
        model_openai,
        temperature,
        **kwargs
    )


# Export clients for compatibility with existing code
gemini_client = get_gemini_client
openai_client = get_openai_client

__all__ = [
    'generate_with_fallback',
    'generate_with_fallback_async',
    'gemini_client',
    'openai_client'
]
