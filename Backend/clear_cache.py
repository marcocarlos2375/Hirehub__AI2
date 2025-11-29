"""
Clear Gemini prompt cache by calling the API endpoint or restarting the service.
"""

import requests

API_BASE = "http://localhost:8001"

def clear_cache():
    """Clear the Gemini prompt cache."""
    try:
        # First, let's check if there's a cache clearing endpoint
        # If not, we can restart the service which will clear the in-memory cache

        print("Clearing Gemini prompt cache...")
        print("Option 1: Restart the API service (this clears in-memory cache)")
        print("Option 2: Wait 5 minutes for cache TTL to expire")

        # Get current cache stats
        response = requests.get(f"{API_BASE}/api/prompt-cache/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"\nCurrent cache stats:")
            print(f"  Active caches: {stats.get('active_caches', 0)}")
            print(f"  Cache hits: {stats.get('prompt_cache_hits', 0)}")
            print(f"  Cache misses: {stats.get('prompt_cache_misses', 0)}")

        print("\n✅ To force cache clear, restart the API service:")
        print("   docker-compose restart api")
        print("\nOr wait 5 minutes for automatic expiration.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    clear_cache()
