"""
Caching utilities for embedding optimization.
Provides both in-memory LRU cache and optional Redis cache for persistence.
Thread-safe implementation using RLock for concurrent access.
"""

import hashlib
import json
import time
import threading
from functools import lru_cache
from typing import Optional, Tuple, Any

from core.config.logging_config import logger
from core.config.settings import settings

# Try to import Redis, fall back gracefully if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis package not installed, using in-memory cache only")


class EmbeddingCache:
    """
    Thread-safe two-tier caching system for embeddings:
    1. L1: In-memory LRU cache (fast, configurable size)
    2. L2: Redis cache (persistent, unlimited with TTL)

    All operations are protected by RLock for thread safety.
    """

    def __init__(self, redis_url: Optional[str] = None, ttl: int = None, max_l1_size: int = None):
        """
        Initialize cache system.

        Args:
            redis_url: Redis connection URL (e.g., "redis://localhost:6379/0")
            ttl: Time-to-live for Redis entries in seconds (default from settings)
            max_l1_size: Maximum L1 cache entries (default from settings)
        """
        self.ttl = ttl or settings.embedding_cache_ttl
        self.max_l1_size = max_l1_size or settings.l1_cache_size
        self.redis_client = None

        # Thread lock for cache operations
        self._lock = threading.RLock()

        # Statistics tracking
        self.stats = {
            "l1_hits": 0,
            "l2_hits": 0,
            "misses": 0,
            "total_requests": 0,
            "zero_vector_fallbacks": 0
        }

        # L1 cache storage
        self._l1_cache = {}
        self._l1_cache_access_time = {}

        # Try to connect to Redis if URL provided
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=False)
                self.redis_client.ping()
                logger.info(f"Redis cache connected: {redis_url}")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, falling back to in-memory cache only")
                self.redis_client = None

    @staticmethod
    def _hash_text(text: str) -> str:
        """Generate MD5 hash of text for cache key."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def get(self, text: str) -> Optional[Any]:
        """
        Get embedding from cache (L1 → L2 → miss).
        Thread-safe operation.

        Args:
            text: Text to get embedding for (or direct cache key like "ind:...", "role:...", "score:...")

        Returns:
            Cached embedding/data or None if not found
        """
        with self._lock:
            self.stats["total_requests"] += 1

            # Support both hashed and direct keys
            if text.startswith(('ind:', 'role:', 'score:')):
                cache_key = text
            else:
                text_hash = self._hash_text(text)
                cache_key = text_hash

            # Try L1 (in-memory)
            if cache_key in self._l1_cache:
                self.stats["l1_hits"] += 1
                self._l1_cache_access_time[cache_key] = time.time()
                return self._l1_cache[cache_key]

        # Try L2 (Redis) - release lock during I/O
        if self.redis_client:
            try:
                redis_key = cache_key if text.startswith(('ind:', 'role:', 'score:')) else f"emb:{cache_key}"
                cached_data = self.redis_client.get(redis_key)
                if cached_data:
                    embedding = json.loads(cached_data)
                    # Promote to L1 (re-acquire lock)
                    with self._lock:
                        self.stats["l2_hits"] += 1
                        self._l1_cache[cache_key] = embedding
                        self._l1_cache_access_time[cache_key] = time.time()
                    return embedding
            except Exception as e:
                logger.debug(f"Redis get error: {e}")

        # Cache miss
        with self._lock:
            self.stats["misses"] += 1
        return None

    def set(self, text: str, embedding: Any, ttl: Optional[int] = None) -> None:
        """
        Store embedding in cache (both L1 and L2).
        Thread-safe operation with LRU eviction.

        Args:
            text: Text key (or cache key if using custom prefix)
            embedding: Embedding vector to cache (or any JSON-serializable data)
            ttl: Optional custom TTL in seconds (uses default if not specified)
        """
        # Support both hashed and direct keys
        if text.startswith(('ind:', 'role:', 'score:')):
            cache_key = text
        else:
            text_hash = self._hash_text(text)
            cache_key = text_hash

        # Store in L1 with LRU eviction (thread-safe)
        with self._lock:
            if len(self._l1_cache) >= self.max_l1_size:
                # Remove least recently used entry (LRU eviction)
                if self._l1_cache_access_time:
                    lru_key = min(self._l1_cache_access_time, key=self._l1_cache_access_time.get)
                    del self._l1_cache[lru_key]
                    del self._l1_cache_access_time[lru_key]
                    logger.debug(f"L1 cache evicted key: {lru_key[:8]}...")

            self._l1_cache[cache_key] = embedding
            self._l1_cache_access_time[cache_key] = time.time()

        # Store in L2 (Redis) - outside lock for I/O
        if self.redis_client:
            try:
                actual_ttl = ttl if ttl is not None else self.ttl
                redis_key = cache_key if text.startswith(('ind:', 'role:', 'score:')) else f"emb:{cache_key}"
                self.redis_client.setex(
                    redis_key,
                    actual_ttl,
                    json.dumps(embedding)
                )
            except Exception as e:
                logger.debug(f"Redis set error: {e}")

    def get_stats(self) -> dict:
        """
        Get cache performance statistics.
        Thread-safe operation.

        Returns:
            Dictionary with hit rates and counts
        """
        with self._lock:
            total = self.stats["total_requests"]
            if total == 0:
                return {**self.stats, "hit_rate": 0.0, "l1_hit_rate": 0.0, "l2_hit_rate": 0.0}

            total_hits = self.stats["l1_hits"] + self.stats["l2_hits"]
            hit_rate = (total_hits / total) * 100

            return {
                **self.stats,
                "hit_rate": round(hit_rate, 2),
                "l1_hit_rate": round((self.stats["l1_hits"] / total) * 100, 2),
                "l2_hit_rate": round((self.stats["l2_hits"] / total) * 100, 2),
                "l1_size": len(self._l1_cache),
                "l1_max_size": self.max_l1_size
            }

    def record_zero_vector_fallback(self) -> None:
        """Record when a zero vector fallback is used (for monitoring)."""
        with self._lock:
            self.stats["zero_vector_fallbacks"] += 1

    def clear(self) -> None:
        """Clear all caches (embeddings, domains, parsing, scoring, etc.)."""
        with self._lock:
            self._l1_cache.clear()
            self._l1_cache_access_time.clear()

        if self.redis_client:
            try:
                patterns = ["emb:*", "domains:*", "parse:*", "score:*", "ind:*", "role:*"]
                for pattern in patterns:
                    for key in self.redis_client.scan_iter(pattern):
                        self.redis_client.delete(key)
                logger.info("Redis cache cleared")
            except Exception as e:
                logger.warning(f"Redis clear error: {e}")

        # Reset stats
        with self._lock:
            self.stats = {
                "l1_hits": 0,
                "l2_hits": 0,
                "misses": 0,
                "total_requests": 0,
                "zero_vector_fallbacks": 0
            }
        logger.info("Cache cleared")


# Global cache instance with thread-safe initialization
_cache_instance = None
_cache_lock = threading.Lock()


def get_cache(redis_url: Optional[str] = None) -> EmbeddingCache:
    """
    Get or create global cache instance (thread-safe singleton pattern).

    Args:
        redis_url: Redis connection URL (only used on first call)

    Returns:
        EmbeddingCache instance
    """
    global _cache_instance
    if _cache_instance is None:
        with _cache_lock:
            if _cache_instance is None:
                _cache_instance = EmbeddingCache(redis_url=redis_url or settings.redis_url)
    return _cache_instance


__all__ = ['EmbeddingCache', 'get_cache']
