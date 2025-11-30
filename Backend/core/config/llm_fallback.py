"""
LLM Fallback Module with Retry Logic, Backpressure, and Circuit Breaker.
Provides Gemini → GPT-4o-mini fallback for all text generation operations.
Uses tenacity for exponential backoff retry on transient failures.
Includes both sync and true async implementations for scalability.
Implements semaphore-based backpressure to prevent overwhelming LLM APIs.
Circuit breaker pattern for resilience against external service failures.
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
import asyncio
import threading

from core.config.logging_config import logger
from core.config.settings import settings
from core.config.clients import get_gemini_client, get_openai_client, get_async_openai_client
from core.config.circuit_breaker import get_circuit_breaker, CircuitBreakerOpenError


# Define transient exceptions that should trigger retry
TRANSIENT_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    httpx.TimeoutException,
    httpx.ConnectError,
    httpx.ReadTimeout,
)


# =============================================================================
# BACKPRESSURE: Semaphore-based concurrency control for LLM API calls
# Prevents overwhelming external APIs under high load (5,000+ concurrent users)
# =============================================================================

# Global semaphore for async LLM calls (created lazily per event loop)
_llm_semaphore: Optional[asyncio.Semaphore] = None
_semaphore_lock = threading.Lock()


def _get_llm_semaphore() -> asyncio.Semaphore:
    """
    Get or create the LLM semaphore for the current event loop.
    Thread-safe lazy initialization.

    Returns:
        asyncio.Semaphore with max_concurrent_llm_calls permits
    """
    global _llm_semaphore

    # Check if semaphore exists and is for current event loop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop, create a new semaphore when needed
        return asyncio.Semaphore(settings.max_concurrent_llm_calls)

    with _semaphore_lock:
        if _llm_semaphore is None:
            _llm_semaphore = asyncio.Semaphore(settings.max_concurrent_llm_calls)
            logger.info(f"LLM backpressure semaphore initialized with {settings.max_concurrent_llm_calls} permits")

    return _llm_semaphore


class LLMBackpressureError(Exception):
    """Raised when LLM queue is full and request cannot be processed in time."""
    pass


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


async def _call_gemini_async(
    prompt: str,
    model: str,
    temperature: float,
    **kwargs
) -> str:
    """
    Call Gemini API asynchronously using google-genai's async support.
    Uses asyncio.to_thread for Gemini (native async support limited).
    Protected by circuit breaker for resilience.

    Args:
        prompt: The prompt text
        model: Gemini model name
        temperature: Generation temperature
        **kwargs: Additional config options

    Returns:
        Generated text response
    """
    max_retries = settings.max_retries
    last_error = None

    # Get circuit breaker for Gemini
    circuit_breaker = await get_circuit_breaker("gemini")

    async def _make_request():
        client = get_gemini_client()
        # google-genai's sync client - run in thread pool to not block
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model,
            contents=prompt,
            config={"temperature": temperature, **kwargs}
        )
        return response.text

    for attempt in range(max_retries):
        try:
            # Use circuit breaker for the actual API call
            return await circuit_breaker.call(_make_request)
        except CircuitBreakerOpenError:
            # Don't retry if circuit is open, fail immediately to fallback
            raise
        except TRANSIENT_EXCEPTIONS as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = min(settings.retry_max_wait, settings.retry_min_wait * (2 ** attempt))
                logger.warning(f"Gemini async retry {attempt + 1}/{max_retries} after {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
            else:
                raise

    raise last_error


async def _call_openai_async(
    prompt: str,
    model: str,
    temperature: float
) -> str:
    """
    Call OpenAI API asynchronously using AsyncOpenAI client.
    True async - does not block the event loop.
    Protected by circuit breaker for resilience.

    Args:
        prompt: The prompt text
        model: OpenAI model name
        temperature: Generation temperature

    Returns:
        Generated text response
    """
    max_retries = settings.max_retries
    last_error = None

    # Get circuit breaker for OpenAI
    circuit_breaker = await get_circuit_breaker("openai")

    async def _make_request():
        client = get_async_openai_client()
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content

    for attempt in range(max_retries):
        try:
            # Use circuit breaker for the actual API call
            return await circuit_breaker.call(_make_request)
        except CircuitBreakerOpenError:
            # Don't retry if circuit is open, fail immediately
            raise
        except TRANSIENT_EXCEPTIONS as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = min(settings.retry_max_wait, settings.retry_min_wait * (2 ** attempt))
                logger.warning(f"OpenAI async retry {attempt + 1}/{max_retries} after {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
            else:
                raise

    raise last_error


async def generate_with_fallback_async(
    prompt: str,
    model_gemini: str = None,
    model_openai: str = None,
    temperature: float = None,
    **kwargs
) -> Tuple[str, str]:
    """
    Generate text asynchronously with Gemini, fall back to OpenAI GPT-4o-mini on any error.
    True async implementation - does not block the event loop (critical for scalability).
    Implements backpressure via semaphore to limit concurrent LLM API calls.

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
        LLMBackpressureError: If semaphore acquisition times out (system overloaded)
        Exception: If both providers fail after all retries
    """
    # Use settings defaults if not specified
    model_gemini = model_gemini or settings.parsing_model
    model_openai = model_openai or settings.fallback_model
    temperature = temperature if temperature is not None else settings.parsing_temperature

    # BACKPRESSURE: Acquire semaphore with timeout
    semaphore = _get_llm_semaphore()
    try:
        # Try to acquire semaphore with timeout
        acquired = await asyncio.wait_for(
            semaphore.acquire(),
            timeout=settings.llm_queue_timeout
        )
    except asyncio.TimeoutError:
        logger.error(
            f"LLM backpressure timeout: queue full for {settings.llm_queue_timeout}s "
            f"(max concurrent: {settings.max_concurrent_llm_calls})"
        )
        raise LLMBackpressureError(
            f"LLM API queue is full. Please try again later. "
            f"(timeout: {settings.llm_queue_timeout}s)"
        )

    try:
        # Try Gemini first (with retry)
        gemini_error = None
        try:
            response = await _call_gemini_async(prompt, model_gemini, temperature, **kwargs)
            logger.debug(f"Gemini async generation successful using {model_gemini}")
            return response, "gemini"

        except Exception as e:
            gemini_error = e
            logger.warning(
                f"Gemini async API failed: {e}. "
                f"Falling back to OpenAI {model_openai}..."
            )

        # Fall back to OpenAI (with retry)
        try:
            response = await _call_openai_async(prompt, model_openai, temperature)
            logger.info(f"OpenAI async fallback successful using {model_openai}")
            return response, "openai"

        except Exception as openai_error:
            logger.error(
                f"Both Gemini and OpenAI async failed. "
                f"Gemini: {gemini_error}. OpenAI: {openai_error}"
            )
            raise Exception(
                f"Both Gemini and OpenAI failed. "
                f"Gemini: {gemini_error}. OpenAI: {openai_error}"
            )
    finally:
        # ALWAYS release semaphore
        semaphore.release()


# Export clients for compatibility with existing code
gemini_client = get_gemini_client
openai_client = get_openai_client

__all__ = [
    'generate_with_fallback',
    'generate_with_fallback_async',
    'gemini_client',
    'openai_client',
    'LLMBackpressureError',
    'CircuitBreakerOpenError',
]
