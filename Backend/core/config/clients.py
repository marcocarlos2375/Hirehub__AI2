"""
Centralized API client factory with singleton pattern.
Provides thread-safe, connection-pooled clients for all external services.
"""

import threading
from typing import Optional
import httpx
from google import genai
from openai import OpenAI

from core.config.logging_config import logger
from core.config.settings import settings

# Try to import Redis, fall back gracefully if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis package not installed, Redis caching unavailable")


class ClientFactory:
    """
    Thread-safe factory for API clients using singleton pattern.
    All clients use connection pooling for optimal performance.
    """

    _gemini_client: Optional[genai.Client] = None
    _openai_client: Optional[OpenAI] = None
    _redis_client: Optional["redis.Redis"] = None
    _http_client: Optional[httpx.Client] = None
    _async_http_client: Optional[httpx.AsyncClient] = None

    _lock = threading.RLock()
    _initialized = {
        "gemini": False,
        "openai": False,
        "redis": False,
        "http": False,
        "async_http": False
    }

    @classmethod
    def get_gemini(cls) -> genai.Client:
        """
        Get Gemini API client (thread-safe singleton).

        Returns:
            Configured Gemini client instance
        """
        if not cls._initialized["gemini"]:
            with cls._lock:
                if not cls._initialized["gemini"]:
                    cls._gemini_client = genai.Client(api_key=settings.gemini_api_key)
                    cls._initialized["gemini"] = True
                    logger.info("Gemini client initialized")
        return cls._gemini_client

    @classmethod
    def get_openai(cls) -> OpenAI:
        """
        Get OpenAI API client with HTTP/2 connection pooling (thread-safe singleton).

        Returns:
            Configured OpenAI client instance
        """
        if not cls._initialized["openai"]:
            with cls._lock:
                if not cls._initialized["openai"]:
                    # Create HTTP/2 client with connection pooling
                    http_client = httpx.Client(
                        http2=True,
                        timeout=settings.llm_timeout,
                        limits=httpx.Limits(
                            max_keepalive_connections=10,
                            keepalive_expiry=30.0
                        )
                    )
                    cls._openai_client = OpenAI(
                        api_key=settings.openai_api_key,
                        http_client=http_client
                    )
                    cls._initialized["openai"] = True
                    logger.info("OpenAI client initialized with HTTP/2 pooling")
        return cls._openai_client

    @classmethod
    def get_redis(cls) -> Optional["redis.Redis"]:
        """
        Get Redis client (thread-safe singleton).

        Returns:
            Redis client instance or None if not configured/available
        """
        if not REDIS_AVAILABLE:
            return None

        if not cls._initialized["redis"]:
            with cls._lock:
                if not cls._initialized["redis"]:
                    if settings.redis_url:
                        try:
                            cls._redis_client = redis.from_url(
                                settings.redis_url,
                                decode_responses=False
                            )
                            cls._redis_client.ping()
                            cls._initialized["redis"] = True
                            logger.info(f"Redis client connected: {settings.redis_url}")
                        except Exception as e:
                            logger.warning(f"Redis connection failed: {e}")
                            cls._redis_client = None
                    else:
                        logger.debug("No Redis URL configured, skipping Redis client")
        return cls._redis_client

    @classmethod
    def get_http_client(cls) -> httpx.Client:
        """
        Get synchronous HTTP client with connection pooling (thread-safe singleton).

        Returns:
            Configured httpx.Client instance
        """
        if not cls._initialized["http"]:
            with cls._lock:
                if not cls._initialized["http"]:
                    cls._http_client = httpx.Client(
                        http2=True,
                        timeout=settings.http_timeout,
                        limits=httpx.Limits(
                            max_keepalive_connections=20,
                            keepalive_expiry=30.0
                        )
                    )
                    cls._initialized["http"] = True
                    logger.debug("HTTP client initialized with connection pooling")
        return cls._http_client

    @classmethod
    def get_async_http_client(cls) -> httpx.AsyncClient:
        """
        Get asynchronous HTTP client with connection pooling (thread-safe singleton).

        Returns:
            Configured httpx.AsyncClient instance
        """
        if not cls._initialized["async_http"]:
            with cls._lock:
                if not cls._initialized["async_http"]:
                    cls._async_http_client = httpx.AsyncClient(
                        http2=True,
                        timeout=settings.http_timeout,
                        limits=httpx.Limits(
                            max_keepalive_connections=20,
                            keepalive_expiry=30.0
                        )
                    )
                    cls._initialized["async_http"] = True
                    logger.debug("Async HTTP client initialized with connection pooling")
        return cls._async_http_client

    @classmethod
    def health_check(cls) -> dict:
        """
        Check health of all configured services.

        Returns:
            Dictionary with service health status
        """
        health = {
            "gemini": False,
            "openai": False,
            "redis": False
        }

        # Check Gemini
        try:
            client = cls.get_gemini()
            if client:
                health["gemini"] = True
        except Exception as e:
            logger.warning(f"Gemini health check failed: {e}")

        # Check OpenAI
        try:
            client = cls.get_openai()
            if client:
                health["openai"] = True
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")

        # Check Redis
        try:
            client = cls.get_redis()
            if client:
                client.ping()
                health["redis"] = True
        except Exception as e:
            logger.debug(f"Redis health check failed: {e}")

        return health

    @classmethod
    def close_all(cls):
        """Close all client connections gracefully."""
        with cls._lock:
            if cls._http_client:
                cls._http_client.close()
                cls._http_client = None
                cls._initialized["http"] = False

            if cls._async_http_client:
                # Note: async client should be closed with await, but we handle sync here
                cls._async_http_client = None
                cls._initialized["async_http"] = False

            if cls._redis_client:
                cls._redis_client.close()
                cls._redis_client = None
                cls._initialized["redis"] = False

            logger.info("All clients closed")


# Convenience functions for quick access
def get_gemini_client() -> genai.Client:
    """Get Gemini client instance."""
    return ClientFactory.get_gemini()


def get_openai_client() -> OpenAI:
    """Get OpenAI client instance."""
    return ClientFactory.get_openai()


def get_redis_client() -> Optional["redis.Redis"]:
    """Get Redis client instance."""
    return ClientFactory.get_redis()


__all__ = [
    'ClientFactory',
    'get_gemini_client',
    'get_openai_client',
    'get_redis_client'
]
