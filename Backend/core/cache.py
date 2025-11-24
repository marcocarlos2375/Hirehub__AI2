"""
Caching utilities for embedding optimization.
Provides both in-memory LRU cache and optional Redis cache for persistence.
"""

import hashlib
import json
from functools import lru_cache
from typing import Optional, Tuple

# Try to import Redis, fall back gracefully if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: redis not installed. Using in-memory cache only.")


class EmbeddingCache:
    """
    Two-tier caching system for embeddings:
    1. L1: In-memory LRU cache (fast, 1000 entries)
    2. L2: Redis cache (persistent, unlimited with TTL)
    """

    def __init__(self, redis_url: Optional[str] = None, ttl: int = 86400):
        """
        Initialize cache system.

        Args:
            redis_url: Redis connection URL (e.g., "redis://localhost:6379/0")
            ttl: Time-to-live for Redis entries in seconds (default: 24 hours)
        """
        self.ttl = ttl
        self.redis_client = None
        self.stats = {
            "l1_hits": 0,
            "l2_hits": 0,
            "misses": 0,
            "total_requests": 0
        }

        # Try to connect to Redis if URL provided
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=False)
                self.redis_client.ping()
                print(f"✅ Redis cache connected: {redis_url}")
            except Exception as e:
                print(f"⚠️  Redis connection failed: {e}")
                print("    Falling back to in-memory cache only")
                self.redis_client = None

    @staticmethod
    def _hash_text(text: str) -> str:
        """Generate MD5 hash of text for cache key."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    @lru_cache(maxsize=1000)
    def _get_from_l1(self, text_hash: str) -> Optional[Tuple]:
        """
        L1 cache (in-memory LRU).
        Returns None to indicate miss (actual data stored in L2 or needs generation).
        """
        return None  # Placeholder, actual caching happens via @lru_cache

    def get(self, text: str) -> Optional[list]:
        """
        Get embedding from cache (L1 → L2 → miss).

        Args:
            text: Text to get embedding for (or direct cache key like "ind:...", "role:...", "score:...")

        Returns:
            Cached embedding/data or None if not found
        """
        self.stats["total_requests"] += 1

        # Support both hashed and direct keys
        if text.startswith(('ind:', 'role:', 'score:')):
            # Direct cache key, no hashing
            cache_key = text
        else:
            # Standard embedding key with hash
            text_hash = self._hash_text(text)
            cache_key = text_hash

        # Try L1 (in-memory)
        # Note: We use a separate dict because @lru_cache doesn't support dynamic values
        if not hasattr(self, '_l1_cache'):
            self._l1_cache = {}

        if cache_key in self._l1_cache:
            self.stats["l1_hits"] += 1
            return self._l1_cache[cache_key]

        # Try L2 (Redis)
        if self.redis_client:
            try:
                # Use direct key for custom prefixes, add "emb:" for standard embeddings
                redis_key = cache_key if text.startswith(('ind:', 'role:', 'score:')) else f"emb:{cache_key}"
                cached_data = self.redis_client.get(redis_key)
                if cached_data:
                    self.stats["l2_hits"] += 1
                    embedding = json.loads(cached_data)
                    # Promote to L1
                    self._l1_cache[cache_key] = embedding
                    return embedding
            except Exception as e:
                print(f"Redis get error: {e}")

        # Cache miss
        self.stats["misses"] += 1
        return None

    def set(self, text: str, embedding: list, ttl: Optional[int] = None):
        """
        Store embedding in cache (both L1 and L2).

        Args:
            text: Text key (or cache key if using custom prefix)
            embedding: Embedding vector to cache (or any JSON-serializable data)
            ttl: Optional custom TTL in seconds (uses default if not specified)
        """
        # Support both hashed and direct keys (for custom cache keys like "ind:..." or "role:...")
        if text.startswith(('ind:', 'role:', 'score:')):
            # Direct cache key, no hashing
            cache_key = text
        else:
            # Standard embedding key with hash
            text_hash = self._hash_text(text)
            cache_key = f"emb:{text_hash}"

        # Store in L1
        if not hasattr(self, '_l1_cache'):
            self._l1_cache = {}

        # Keep L1 size under control (LRU eviction)
        if len(self._l1_cache) >= 1000:
            # Remove oldest entry (simple FIFO, could be improved)
            first_key = next(iter(self._l1_cache))
            del self._l1_cache[first_key]

        self._l1_cache[cache_key] = embedding

        # Store in L2 (Redis)
        if self.redis_client:
            try:
                actual_ttl = ttl if ttl is not None else self.ttl
                self.redis_client.setex(
                    cache_key,
                    actual_ttl,
                    json.dumps(embedding)
                )
            except Exception as e:
                print(f"Redis set error: {e}")

    def get_stats(self) -> dict:
        """
        Get cache performance statistics.

        Returns:
            Dictionary with hit rates and counts
        """
        total = self.stats["total_requests"]
        if total == 0:
            return {**self.stats, "hit_rate": 0.0}

        total_hits = self.stats["l1_hits"] + self.stats["l2_hits"]
        hit_rate = (total_hits / total) * 100

        return {
            **self.stats,
            "hit_rate": round(hit_rate, 2),
            "l1_hit_rate": round((self.stats["l1_hits"] / total) * 100, 2),
            "l2_hit_rate": round((self.stats["l2_hits"] / total) * 100, 2)
        }

    def clear(self):
        """Clear all caches (embeddings, domains, parsing, scoring, etc.)."""
        if hasattr(self, '_l1_cache'):
            self._l1_cache.clear()

        if self.redis_client:
            try:
                # Clear all cache key patterns
                patterns = ["emb:*", "domains:*", "parse:*", "score:*", "ind:*", "role:*"]
                for pattern in patterns:
                    for key in self.redis_client.scan_iter(pattern):
                        self.redis_client.delete(key)
            except Exception as e:
                print(f"Redis clear error: {e}")

        # Reset stats
        self.stats = {
            "l1_hits": 0,
            "l2_hits": 0,
            "misses": 0,
            "total_requests": 0
        }


# Global cache instance
_cache_instance = None


def get_cache(redis_url: Optional[str] = None) -> EmbeddingCache:
    """
    Get or create global cache instance (singleton pattern).

    Args:
        redis_url: Redis connection URL (only used on first call)

    Returns:
        EmbeddingCache instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = EmbeddingCache(redis_url=redis_url)
    return _cache_instance
