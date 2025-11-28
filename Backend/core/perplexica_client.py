"""
Perplexica AI search client for learning resource discovery.
Provides AI-synthesized answers with citations using Perplexica's API.
"""
import os
import requests
from typing import List, Dict, Any, Optional, Literal


class PerplexicaClient:
    """Client for interacting with self-hosted Perplexica instance."""

    def __init__(self, base_url: str = None):
        """
        Initialize Perplexica client.

        Args:
            base_url: Perplexica URL (defaults to env var or Docker service name)
        """
        if base_url is None:
            base_url = os.getenv("PERPLEXICA_URL", "http://perplexica:3000")

        self.base_url = base_url.rstrip('/')
        self.search_endpoint = f"{self.base_url}/api/search"
        self.health_endpoint = self.base_url
        self._gemini_chat_provider_id = None
        self._gemini_embedding_provider_id = None

    def search(
        self,
        query: str,
        focus_mode: str = "webSearch",
        optimization_mode: Literal["speed", "balanced"] = "balanced",
        chat_model_provider: str = None,
        chat_model_key: str = None,
        embedding_model_provider: str = None,
        embedding_model_key: str = None
    ) -> Dict[str, Any]:
        """
        Search using Perplexica AI synthesis.

        Args:
            query: Search query string
            focus_mode: Type of search (webSearch, academicSearch, youtubeSearch, etc.)
            optimization_mode: Speed vs quality trade-off
            chat_model_provider: LLM provider UUID (defaults to Gemini)
            chat_model_key: Model key/name (defaults to gemini-2.0-flash-exp)
            embedding_model_provider: Embedding provider UUID (defaults to Gemini)
            embedding_model_key: Embedding model key/name (defaults to text-embedding-004)

        Returns:
            Dictionary with:
            - message: AI-synthesized summary
            - sources: List of citations with metadata
        """
        # Use Gemini defaults if not specified
        if chat_model_provider is None or embedding_model_provider is None:
            chat_provider_id, embedding_provider_id = self._get_gemini_provider_ids()
            if chat_model_provider is None:
                chat_model_provider = chat_provider_id
            if embedding_model_provider is None:
                embedding_model_provider = embedding_provider_id

        if chat_model_key is None:
            chat_model_key = "models/gemini-2.0-flash-exp"
        if embedding_model_key is None:
            embedding_model_key = "models/text-embedding-004"

        payload = {
            "query": query,
            "focusMode": focus_mode,
            "optimizationMode": optimization_mode,
            "chatModel": {
                "providerId": chat_model_provider,
                "key": chat_model_key
            },
            "embeddingModel": {
                "providerId": embedding_model_provider,
                "key": embedding_model_key
            },
            "history": [],
            "stream": False
        }

        try:
            response = requests.post(
                self.search_endpoint,
                json=payload,
                timeout=30  # AI synthesis takes longer than raw search
            )
            response.raise_for_status()

            data = response.json()

            return {
                "answer": data.get("message", ""),
                "sources": data.get("sources", []),
                "query": query,
                "focus_mode": focus_mode
            }

        except requests.exceptions.RequestException as e:
            print(f"Perplexica search error: {str(e)}")
            return {"answer": "", "sources": [], "error": str(e)}
        except Exception as e:
            print(f"Unexpected error in Perplexica search: {str(e)}")
            return {"answer": "", "sources": [], "error": str(e)}

    def _get_gemini_provider_ids(self) -> tuple:
        """
        Fetch Gemini provider UUIDs from Perplexica configuration.

        Returns:
            Tuple of (chat_provider_id, embedding_provider_id)

        Raises:
            ValueError: If Gemini provider is not configured
        """
        # Return cached IDs if available
        if self._gemini_chat_provider_id and self._gemini_embedding_provider_id:
            return self._gemini_chat_provider_id, self._gemini_embedding_provider_id

        try:
            # Perplexica stores config in a file accessible via the container
            # We'll read it directly using a simple HTTP request to the config endpoint
            # or by reading the mounted volume if available

            # For now, use the known UUID from config.json
            # In production, this could be fetched dynamically via API
            self._gemini_chat_provider_id = "0b892904-e752-4e89-ab60-484ef8989843"
            self._gemini_embedding_provider_id = "0b892904-e752-4e89-ab60-484ef8989843"

            return self._gemini_chat_provider_id, self._gemini_embedding_provider_id

        except Exception as e:
            print(f"Failed to get Gemini provider IDs: {e}")
            raise ValueError("Gemini provider not configured in Perplexica")

    def search_learning_resources(
        self,
        skill: str,
        user_level: str = "beginner",
        num_results: int = 10
    ) -> Dict[str, Any]:
        """
        Specialized search for learning resources with AI synthesis.

        Args:
            skill: Skill/technology to search for
            user_level: User's skill level (beginner/intermediate/advanced)
            num_results: Number of results to return (not directly used, but for context)

        Returns:
            Dictionary with AI answer and cited sources
        """
        # Craft optimized query
        query = self._build_learning_query(skill, user_level)

        # Get Gemini provider UUIDs
        chat_provider_id, embedding_provider_id = self._get_gemini_provider_ids()

        # Use Gemini models via proper provider UUIDs
        # Note: Model names should match Google's API format
        return self.search(
            query=query,
            focus_mode="webSearch",  # Good balance for courses/tutorials
            optimization_mode="balanced",
            chat_model_provider=chat_provider_id,  # Gemini UUID
            chat_model_key="models/gemini-2.0-flash-exp",  # Full Google API format
            embedding_model_provider=embedding_provider_id,  # Gemini UUID
            embedding_model_key="models/text-embedding-004"  # Full Google API format
        )

    def _build_learning_query(self, skill: str, user_level: str) -> str:
        """
        Build an optimized search query for learning resources.

        Args:
            skill: Technology/skill name
            user_level: User's experience level

        Returns:
            Optimized search query string
        """
        from datetime import datetime
        current_year = datetime.now().year

        # Build query with specific learning intent and platform prioritization
        # Explicitly mention learning platforms to guide Perplexica's search
        query = f"Find the best {user_level} {skill} courses, tutorials, and projects to learn in {current_year}. Priority: Udemy, Coursera, LinkedIn Learning, Pluralsight, freeCodeCamp, YouTube tutorials, edX, Udacity, Khan Academy, and official documentation. Exclude Reddit, forums, and discussion posts."

        return query

    def health_check(self) -> bool:
        """
        Check if Perplexica instance is healthy.

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


# Singleton instance
_perplexica_client = None

def get_perplexica_client() -> PerplexicaClient:
    """
    Get or create Perplexica client singleton.

    Returns:
        PerplexicaClient instance
    """
    global _perplexica_client
    if _perplexica_client is None:
        _perplexica_client = PerplexicaClient()
    return _perplexica_client
