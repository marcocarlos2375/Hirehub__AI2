"""
Centralized application settings using pydantic-settings.
All configuration is loaded from environment variables with sensible defaults.
"""

from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys (required)
    gemini_api_key: str = Field(..., description="Google Gemini API key")
    openai_api_key: str = Field(..., description="OpenAI API key")

    # Optional Services
    redis_url: Optional[str] = Field(None, description="Redis connection URL for caching")
    database_url: Optional[str] = Field(None, description="PostgreSQL connection URL")
    parakeet_url: str = Field("http://parakeet:8002", description="Parakeet STT service URL")
    use_parakeet: bool = Field(False, description="Enable Parakeet speech-to-text")

    # CORS Configuration
    cors_origins: str = Field(
        "http://localhost:3000,http://127.0.0.1:3000",
        description="Comma-separated list of allowed CORS origins"
    )

    # Model Configuration
    parsing_model: str = Field("gemini-2.5-flash-lite", description="Model for parsing operations")
    analysis_model: str = Field("gemini-2.0-flash-exp", description="Model for analysis operations")
    fallback_model: str = Field("gpt-4o-mini", description="OpenAI fallback model")
    embedding_model: str = Field("text-embedding-004", description="Embedding model")

    # Temperature Settings
    parsing_temperature: float = Field(0.2, description="Temperature for parsing")
    analysis_temperature: float = Field(0.3, description="Temperature for analysis")
    generation_temperature: float = Field(0.5, description="Temperature for text generation")

    # Cache Configuration
    embedding_cache_ttl: int = Field(86400, description="Embedding cache TTL in seconds (24h)")
    result_cache_ttl: int = Field(2592000, description="Result cache TTL in seconds (30d)")
    l1_cache_size: int = Field(1000, description="L1 in-memory cache max entries")

    # Redis Connection Pool Configuration (for 10,000+ concurrent users)
    # Formula: max_connections = (concurrent_users / workers) * 2 = (10000 / 8) * 2 ≈ 200
    redis_max_connections: int = Field(200, description="Redis connection pool max connections")
    redis_pool_timeout: float = Field(5.0, description="Redis connection pool timeout (seconds)")

    # Database Connection Pool Configuration (for 10,000+ concurrent users)
    # Formula: pool_size = workers * 3 = 8 * 3 = 24, overflow = pool_size * 2
    db_pool_size: int = Field(25, description="DB connection pool size")
    db_max_overflow: int = Field(50, description="DB max overflow connections")
    db_pool_recycle: int = Field(1800, description="Recycle DB connections after N seconds")

    # Retry Configuration
    max_retries: int = Field(3, description="Maximum retry attempts for API calls")
    retry_min_wait: float = Field(2.0, description="Minimum wait between retries (seconds)")
    retry_max_wait: float = Field(10.0, description="Maximum wait between retries (seconds)")

    # Timeout Configuration
    llm_timeout: float = Field(30.0, description="Timeout for LLM operations (seconds)")
    embedding_timeout: float = Field(10.0, description="Timeout for embedding operations (seconds)")
    http_timeout: float = Field(15.0, description="Default HTTP request timeout (seconds)")

    # Concurrency Control (Backpressure)
    max_concurrent_llm_calls: int = Field(50, description="Maximum concurrent LLM API calls (backpressure)")
    llm_queue_timeout: float = Field(60.0, description="Timeout waiting for LLM semaphore (seconds)")

    # Thread Pool Configuration
    max_workers: int = Field(8, description="Maximum ThreadPoolExecutor workers")

    # Logging Configuration
    log_level: str = Field("INFO", description="Logging level")
    log_serialize: bool = Field(False, description="Serialize logs as JSON")

    # Circuit Breaker Configuration (for resilience)
    circuit_breaker_failure_threshold: int = Field(5, description="Failures before opening circuit")
    circuit_breaker_recovery_timeout: float = Field(30.0, description="Seconds before half-open state")
    circuit_breaker_half_open_requests: int = Field(3, description="Test requests in half-open state")

    # Feature Flags
    enable_metrics: bool = Field(True, description="Enable metrics collection")
    enable_prompt_cache: bool = Field(True, description="Enable Gemini prompt caching")
    enable_circuit_breaker: bool = Field(True, description="Enable circuit breaker for external services")

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance (singleton pattern).

    Returns:
        Settings instance with all configuration loaded
    """
    return Settings()


# Export settings instance for convenience
settings = get_settings()

__all__ = ['Settings', 'get_settings', 'settings']
