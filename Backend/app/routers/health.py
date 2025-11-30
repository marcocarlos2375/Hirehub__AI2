"""
Health and monitoring endpoints.
"""

from fastapi import APIRouter

from core.logging_config import logger
from core.cache import get_cache
from core.gemini_cache import get_prompt_cache_stats
from core.clients import ClientFactory

router = APIRouter(tags=["Health"])

cache = get_cache()


@router.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "HireHubAI API",
        "version": "2.1.0"
    }


@router.get("/health")
async def health_check():
    """Detailed health check with service status."""
    health_status = ClientFactory.health_check()

    return {
        "status": "healthy" if health_status.get("gemini") else "degraded",
        "services": health_status,
        "version": "2.1.0"
    }


@router.get("/cache/stats")
async def get_cache_stats():
    """Get embedding cache statistics."""
    stats = cache.get_stats()
    return {
        "embedding_cache": stats,
        "message": "Cache statistics"
    }


@router.get("/api/cache/stats")
async def get_api_cache_stats():
    """Get embedding cache statistics (API prefix version)."""
    stats = cache.get_stats()
    return {
        "embedding_cache": stats,
        "message": "Cache statistics"
    }


@router.get("/api/prompt-cache/stats")
async def get_api_prompt_cache_stats():
    """Get Gemini prompt cache statistics."""
    stats = get_prompt_cache_stats()
    return {
        "prompt_cache": stats,
        "message": "Prompt cache statistics"
    }


@router.post("/api/cache/clear")
async def clear_cache():
    """Clear all caches."""
    try:
        cache.clear()
        logger.info("All caches cleared by API request")
        return {"success": True, "message": "All caches cleared"}
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/api/cache/clear-domains")
async def clear_domain_cache():
    """Clear domain/industry cache only."""
    try:
        # Clear domain-specific cache entries
        if cache.redis_client:
            patterns = ["ind:*", "role:*"]
            count = 0
            for pattern in patterns:
                for key in cache.redis_client.scan_iter(pattern):
                    cache.redis_client.delete(key)
                    count += 1
            logger.info(f"Cleared {count} domain cache entries")
            return {"success": True, "message": f"Cleared {count} domain cache entries"}

        return {"success": True, "message": "In-memory cache cleared (no Redis)"}

    except Exception as e:
        logger.error(f"Domain cache clear failed: {e}")
        return {"success": False, "error": str(e)}
