"""
Qdrant Vector Database utilities for RAG-based question generation.
Stores and retrieves similar past experiences to help generate personalized questions.
"""

import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini client for embeddings
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", ":memory:")  # Use in-memory if not configured
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "past_experiences"
VECTOR_SIZE = 768  # text-embedding-004 dimension


class QdrantManager:
    """Manager for Qdrant vector database operations"""

    def __init__(self):
        """Initialize Qdrant client and ensure collection exists"""
        if QDRANT_URL == ":memory:":
            # Use in-memory mode for development/testing
            self.client = QdrantClient(":memory:")
            print("⚠️  Using in-memory Qdrant (data will not persist)")
        else:
            # Use cloud or local Qdrant instance
            self.client = QdrantClient(
                url=QDRANT_URL,
                api_key=QDRANT_API_KEY
            )
            print(f"✅ Connected to Qdrant at {QDRANT_URL}")

        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if COLLECTION_NAME not in collection_names:
                self.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=VECTOR_SIZE,
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ Created collection: {COLLECTION_NAME}")

                # Seed with initial data
                self.seed_initial_experiences()
            else:
                print(f"✅ Collection '{COLLECTION_NAME}' already exists")
        except Exception as e:
            print(f"❌ Error ensuring collection exists: {e}")
            raise

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text using Gemini text-embedding-004"""
        try:
            response = gemini_client.models.embed_content(
                model="text-embedding-004",
                contents=[text]
            )
            return response.embeddings[0].values
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            raise

    def store_experience(
        self,
        experience_text: str,
        metadata: Dict[str, Any],
        point_id: int | None = None
    ) -> bool:
        """
        Store an experience in Qdrant with its embedding and metadata.

        Args:
            experience_text: The text describing the experience
            metadata: Additional metadata (e.g., gap_type, skill, impact)
            point_id: Optional ID for the point (auto-generated if None)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate embedding
            embedding = self.generate_embedding(experience_text)

            # Create point
            point = PointStruct(
                id=point_id or self.client.count(COLLECTION_NAME).count + 1,
                vector=embedding,
                payload={
                    "text": experience_text,
                    **metadata
                }
            )

            # Upload to Qdrant
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=[point]
            )

            return True
        except Exception as e:
            print(f"❌ Error storing experience: {e}")
            return False

    def search_similar_experiences(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar past experiences using semantic search.

        Args:
            query: The search query (e.g., gap description)
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of similar experiences with scores
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)

            # Search Qdrant using query_points (newer API)
            results = self.client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            ).points

            # Format results
            experiences = []
            for result in results:
                experiences.append({
                    "text": result.payload.get("text", ""),
                    "score": result.score,
                    "metadata": {k: v for k, v in result.payload.items() if k != "text"}
                })

            return experiences
        except Exception as e:
            print(f"❌ Error searching experiences: {e}")
            return []

    def seed_initial_experiences(self):
        """
        Seed the database with initial experiences for early users.
        This provides RAG context even when there are no user submissions yet.
        """
        print("🌱 Seeding initial experiences...")

        initial_experiences = [
            # Next.js advanced features
            {
                "text": "Candidate had basic Next.js experience but discovered they had used SSR and API routes in a side project. Impact: +15% on frontend skills.",
                "metadata": {"gap_type": "Next.js", "skill": "Next.js Advanced Features", "impact": "+15%", "priority": "CRITICAL"}
            },
            {
                "text": "Candidate claimed no Next.js experience, but upon questioning revealed they built a blog with SSG and ISR. Impact: +12%.",
                "metadata": {"gap_type": "Next.js", "skill": "Static Generation", "impact": "+12%", "priority": "CRITICAL"}
            },

            # AI/ML experience
            {
                "text": "Candidate didn't list AI experience but had experimented with OpenAI API for a hackathon project. Won 2nd place. Impact: +12% on domain expertise.",
                "metadata": {"gap_type": "AI/ML", "skill": "GenAI", "impact": "+12%", "priority": "CRITICAL"}
            },
            {
                "text": "Candidate built a chatbot using LangChain during online course but didn't include it on CV. Impact: +10% on AI exposure.",
                "metadata": {"gap_type": "AI/ML", "skill": "LLMs", "impact": "+10%", "priority": "CRITICAL"}
            },

            # Startup experience
            {
                "text": "Candidate worked at mid-size company but led a 3-person team with full autonomy and ownership. Startup-like environment. Impact: +10% on culture fit.",
                "metadata": {"gap_type": "Startup", "skill": "Ownership", "impact": "+10%", "priority": "CRITICAL"}
            },
            {
                "text": "Candidate freelanced for 6 months helping an early-stage startup. Fast-paced, wore multiple hats. Impact: +8%.",
                "metadata": {"gap_type": "Startup", "skill": "Agility", "impact": "+8%", "priority": "HIGH"}
            },

            # State management
            {
                "text": "Candidate listed Redux but also used Zustand and React Context in production. Impact: +8% on frontend architecture.",
                "metadata": {"gap_type": "State Management", "skill": "Modern State", "impact": "+8%", "priority": "HIGH"}
            },

            # Database & API design
            {
                "text": "Candidate designed a microservices architecture with REST + GraphQL endpoints. Not on CV. Impact: +7%.",
                "metadata": {"gap_type": "Database/API", "skill": "API Design", "impact": "+7%", "priority": "HIGH"}
            },

            # Security & best practices
            {
                "text": "Candidate implemented OAuth2, JWT, and rate limiting but didn't highlight it. Impact: +5%.",
                "metadata": {"gap_type": "Security", "skill": "Auth & Security", "impact": "+5%", "priority": "MEDIUM"}
            },

            # Experience level justification
            {
                "text": "Candidate had 3 years experience but in 2 of those years worked on projects equivalent to 5+ years due to complexity and scope. Impact: Overcame 5-year requirement.",
                "metadata": {"gap_type": "Experience", "skill": "Level", "impact": "+25%", "priority": "CRITICAL"}
            },

            # Relocation willingness
            {
                "text": "Candidate was remote but enthusiastically willing to relocate for the right opportunity. Addressed logistics gap. Impact: +35% on logistics.",
                "metadata": {"gap_type": "Logistics", "skill": "Relocation", "impact": "+35%", "priority": "HIGH"}
            },

            # Portfolio quality
            {
                "text": "Candidate had GitHub repos with 500+ stars and contributions to popular open-source projects. Forgot to mention. Impact: +5%.",
                "metadata": {"gap_type": "Portfolio", "skill": "Open Source", "impact": "+5%", "priority": "MEDIUM"}
            }
        ]

        for i, exp in enumerate(initial_experiences, 1):
            success = self.store_experience(
                experience_text=exp["text"],
                metadata=exp["metadata"],
                point_id=i
            )
            if success:
                print(f"  ✅ Seeded experience {i}/{len(initial_experiences)}")

        print(f"✅ Seeded {len(initial_experiences)} initial experiences")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.client.count(COLLECTION_NAME).count
            return {
                "collection_name": COLLECTION_NAME,
                "total_experiences": count,
                "vector_size": VECTOR_SIZE
            }
        except Exception as e:
            print(f"❌ Error getting collection stats: {e}")
            return {}


# Global instance
qdrant_manager = None


def get_qdrant_manager() -> QdrantManager:
    """Get or create global Qdrant manager instance"""
    global qdrant_manager
    if qdrant_manager is None:
        qdrant_manager = QdrantManager()
    return qdrant_manager
