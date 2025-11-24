"""
SearXNG search client for learning resource discovery.
Provides interface to self-hosted SearXNG meta-search engine.
"""
import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime


class SearXNGClient:
    """Client for interacting with self-hosted SearXNG instance."""

    def __init__(self, base_url: str = None):
        """
        Initialize SearXNG client.

        Args:
            base_url: SearXNG instance URL (defaults to env var or Docker service name)
        """
        if base_url is None:
            base_url = os.getenv("SEARXNG_URL", "http://searxng:8080")

        self.base_url = base_url.rstrip('/')
        self.search_endpoint = f"{self.base_url}/search"
        self.health_endpoint = f"{self.base_url}/healthz"

    def search(
        self,
        query: str,
        num_results: int = 10,
        categories: str = "general",
        engines: Optional[List[str]] = None,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Search using SearXNG.

        Args:
            query: Search query string
            num_results: Number of results to return
            categories: Search categories (general, images, videos, etc.)
            engines: Specific engines to use (e.g., ["google", "duckduckgo"])
            language: Search language code (default: "en")

        Returns:
            List of search results with title, url, content, engine
        """
        params = {
            "q": query,
            "format": "json",
            "categories": categories,
            "language": language,
            "pageno": 1
        }

        if engines:
            params["engines"] = ",".join(engines)

        try:
            response = requests.get(
                self.search_endpoint,
                params=params,
                timeout=15
            )
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            # Parse and structure results
            parsed_results = []
            for result in results[:num_results]:
                parsed_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("content", ""),
                    "engine": result.get("engine", "unknown"),
                    "score": result.get("score", 0),
                    "category": result.get("category", "general"),
                    "publishedDate": result.get("publishedDate"),
                    "img_src": result.get("img_src")
                })

            return parsed_results

        except requests.exceptions.RequestException as e:
            print(f"SearXNG search error: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected error in SearXNG search: {str(e)}")
            return []

    def search_learning_resources(
        self,
        skill: str,
        user_level: str = "beginner",
        num_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Specialized search for learning resources.

        Args:
            skill: Skill/technology to search for
            user_level: User's skill level (beginner/intermediate/advanced)
            num_results: Number of results to return

        Returns:
            List of learning resources filtered for trusted platforms
        """
        # Craft optimized query
        query = self._build_learning_query(skill, user_level)

        # Search using relevant engines
        results = self.search(
            query=query,
            num_results=num_results * 3,  # Get extra for filtering
            engines=["google", "duckduckgo", "bing"]
        )

        # Filter for learning platforms
        learning_platforms = [
            "udemy.com", "coursera.org", "freecodecamp.org",
            "youtube.com", "github.com", "medium.com",
            "dev.to", "pluralsight.com", "udacity.com",
            "codecademy.com", "linkedin.com/learning",
            "edx.org", "skillshare.com", "egghead.io",
            "frontendmasters.com", "laracasts.com",
            "realpython.com", "css-tricks.com",
            "smashingmagazine.com", "scotch.io"
        ]

        filtered = []
        for result in results:
            url = result.get("url", "")
            if any(platform in url.lower() for platform in learning_platforms):
                filtered.append(result)

            if len(filtered) >= num_results:
                break

        return filtered

    def _build_learning_query(self, skill: str, user_level: str) -> str:
        """
        Build an optimized search query for learning resources.

        Args:
            skill: Technology/skill name
            user_level: User's experience level

        Returns:
            Optimized search query string
        """
        # Add year for freshness
        current_year = datetime.now().year

        # Build query with platform hints
        query = f"{skill} {user_level} course tutorial {current_year}"

        # Add platform hints for better results
        query += " (site:udemy.com OR site:coursera.org OR site:freecodecamp.org OR site:youtube.com OR site:github.com)"

        return query

    def health_check(self) -> bool:
        """
        Check if SearXNG instance is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = requests.get(
                self.health_endpoint,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    def get_engines_status(self) -> Dict[str, Any]:
        """
        Get status of available search engines.

        Returns:
            Dictionary of engine statuses
        """
        try:
            response = requests.get(
                f"{self.base_url}/stats",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return {}
        except:
            return {}


# Singleton instance
_searxng_client = None

def get_searxng_client() -> SearXNGClient:
    """
    Get or create SearXNG client singleton.

    Returns:
        SearXNGClient instance
    """
    global _searxng_client
    if _searxng_client is None:
        _searxng_client = SearXNGClient()
    return _searxng_client
