"""
LangChain Configuration Module.
Initializes LangChain components for adaptive question workflows including:
- Google Gemini LLM
- Qdrant Vector Store
- Embeddings
- Optional LangSmith tracing
"""

import os
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_openai import ChatOpenAI
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LangChainConfig:
    """
    Centralized configuration for Lang Chain components.
    Provides singleton access to LLMs, vector stores, and embeddings.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LangChainConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize LangChain components if not already initialized."""
        if not self._initialized:
            self._setup()
            LangChainConfig._initialized = True

    def _setup(self):
        """Setup all LangChain components."""
        # API Keys
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")  # Optional

        # Qdrant configuration
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")  # Optional for local

        # Initialize components
        self._init_llms()
        self._init_embeddings()
        self._init_vector_stores()
        self._init_langsmith()

    def _init_llms(self):
        """Initialize Language Models."""
        # Primary LLM: Google Gemini (for most operations)
        self.llm_fast = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0.1,
            google_api_key=self.gemini_api_key,
            convert_system_message_to_human=True,  # Gemini compatibility
        )

        # Quality LLM: Gemini 2.0 Flash Exp (for critical operations like gap analysis)
        self.llm_quality = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            google_api_key=self.gemini_api_key,
            convert_system_message_to_human=True,
        )

        # Creative LLM: For resume rewriting (slightly higher temperature)
        self.llm_creative = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0.3,
            google_api_key=self.gemini_api_key,
            convert_system_message_to_human=True,
        )

        # Fallback LLM: OpenAI GPT-4 (optional, for comparison or fallback)
        if self.openai_api_key:
            self.llm_openai = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                openai_api_key=self.openai_api_key,
            )
        else:
            self.llm_openai = None

    def _init_embeddings(self):
        """Initialize embedding models."""
        # Google Embeddings (matches existing system)
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=self.gemini_api_key,
        )

        # Dimension: 768 (same as current system)
        self.embedding_dimension = 768

    def _init_vector_stores(self):
        """Initialize Qdrant vector stores."""
        # Qdrant client
        self.qdrant_client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key,
        )

        # Vector store for user experiences (RAG for questions)
        # This is the existing collection from core/vector_store.py
        self.user_experiences_store = None  # Lazy initialization

        # Vector store for learning resources (semantic search)
        self.learning_resources_store = None  # Lazy initialization

    def _init_langsmith(self):
        """Initialize LangSmith tracing (optional)."""
        if self.langsmith_api_key:
            os.environ["LANGSMITH_API_KEY"] = self.langsmith_api_key
            os.environ["LANGSMITH_TRACING"] = "true"
            os.environ["LANGSMITH_PROJECT"] = "HireHub-AI"
            print("✅ LangSmith tracing enabled for project: HireHub-AI")
        else:
            print("ℹ️  LangSmith tracing disabled (no API key)")

    def get_user_experiences_vectorstore(self) -> QdrantVectorStore:
        """
        Get or create vector store for user experiences (RAG).
        Uses existing 'user_experiences' collection from core/vector_store.py
        """
        if self.user_experiences_store is None:
            self.user_experiences_store = QdrantVectorStore(
                client=self.qdrant_client,
                collection_name="user_experiences",
                embedding=self.embeddings,
            )
        return self.user_experiences_store

    def get_learning_resources_vectorstore(self) -> QdrantVectorStore:
        """
        Get or create vector store for learning resources.
        Enables semantic search for courses/projects based on skill gaps.
        """
        if self.learning_resources_store is None:
            # Check if collection exists, create if not
            try:
                self.qdrant_client.get_collection("learning_resources")
            except Exception:
                # Collection doesn't exist, create it
                from qdrant_client.models import Distance, VectorParams

                self.qdrant_client.create_collection(
                    collection_name="learning_resources",
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                print("✅ Created 'learning_resources' Qdrant collection")

            self.learning_resources_store = QdrantVectorStore(
                client=self.qdrant_client,
                collection_name="learning_resources",
                embedding=self.embeddings,
            )
        return self.learning_resources_store

    def get_llm(self, mode: str = "fast") -> ChatGoogleGenerativeAI:
        """
        Get appropriate LLM based on use case.

        Args:
            mode: 'fast' (default), 'quality', 'creative', or 'openai'

        Returns:
            Configured LLM instance
        """
        if mode == "fast":
            return self.llm_fast
        elif mode == "quality":
            return self.llm_quality
        elif mode == "creative":
            return self.llm_creative
        elif mode == "openai":
            if self.llm_openai:
                return self.llm_openai
            else:
                print("⚠️  OpenAI LLM not configured, falling back to Gemini fast")
                return self.llm_fast
        else:
            return self.llm_fast


# Singleton instance
_config = None


def get_langchain_config() -> LangChainConfig:
    """
    Get singleton LangChain configuration instance.

    Usage:
        from core.langchain_config import get_langchain_config

        config = get_langchain_config()
        llm = config.get_llm("fast")
        vectorstore = config.get_user_experiences_vectorstore()
    """
    global _config
    if _config is None:
        _config = LangChainConfig()
    return _config


# Convenience functions
def get_llm(mode: str = "fast"):
    """Get LLM with specified mode."""
    return get_langchain_config().get_llm(mode)


def get_embeddings():
    """Get embedding model."""
    return get_langchain_config().embeddings


def get_user_experiences_vectorstore():
    """Get user experiences vector store (for RAG)."""
    return get_langchain_config().get_user_experiences_vectorstore()


def get_learning_resources_vectorstore():
    """Get learning resources vector store (for semantic search)."""
    return get_langchain_config().get_learning_resources_vectorstore()


# Example usage
if __name__ == "__main__":
    # Test configuration
    config = get_langchain_config()

    print("\n🔧 LangChain Configuration Test")
    print("=" * 50)
    print(f"✅ Gemini Fast LLM: {config.llm_fast.model}")
    print(f"✅ Gemini Quality LLM: {config.llm_quality.model}")
    print(f"✅ Gemini Creative LLM: {config.llm_creative.model}")
    print(f"✅ Embeddings Model: text-embedding-004")
    print(f"✅ Embedding Dimension: {config.embedding_dimension}")
    print(f"✅ Qdrant URL: {config.qdrant_url}")

    if config.llm_openai:
        print(f"✅ OpenAI LLM: {config.llm_openai.model}")
    else:
        print("⚠️  OpenAI LLM: Not configured")

    print("\n🎯 Vector Stores:")
    try:
        user_exp_store = config.get_user_experiences_vectorstore()
        print(f"✅ User Experiences Store: Connected to '{user_exp_store.collection_name}'")
    except Exception as e:
        print(f"⚠️  User Experiences Store: {str(e)}")

    try:
        resources_store = config.get_learning_resources_vectorstore()
        print(f"✅ Learning Resources Store: Connected to '{resources_store.collection_name}'")
    except Exception as e:
        print(f"⚠️  Learning Resources Store: {str(e)}")

    print("=" * 50)
    print("✅ Configuration test complete!\n")
