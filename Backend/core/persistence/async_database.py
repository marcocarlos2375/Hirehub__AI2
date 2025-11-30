"""
Async Database Session Factory for PostgreSQL.
Provides high-performance async database operations for 10,000+ concurrent users.

Features:
- Async SQLAlchemy with asyncpg driver (fastest Python PostgreSQL driver)
- Connection pooling optimized for high concurrency
- Context manager for automatic session cleanup
- Health check and graceful shutdown support
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.pool import AsyncAdaptedQueuePool

from core.config.logging_config import logger
from core.config.settings import settings


class AsyncDatabaseManager:
    """
    Manages async database connections with connection pooling.
    Thread-safe singleton pattern for sharing across the application.
    """

    _instance: Optional["AsyncDatabaseManager"] = None
    _lock = asyncio.Lock()

    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self._initialized = False

    @classmethod
    async def get_instance(cls) -> "AsyncDatabaseManager":
        """Get or create singleton instance (async-safe)."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    async def initialize(self, database_url: Optional[str] = None) -> bool:
        """
        Initialize the async database engine and session factory.

        Args:
            database_url: PostgreSQL connection URL (default from settings)

        Returns:
            True if initialization successful, False otherwise
        """
        if self._initialized:
            return True

        db_url = database_url or settings.database_url
        if not db_url:
            logger.warning("No database URL configured, async database disabled")
            return False

        try:
            # Convert sync URL to async URL format
            # postgresql://... -> postgresql+asyncpg://...
            if db_url.startswith("postgresql://"):
                async_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif db_url.startswith("postgres://"):
                async_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
            else:
                async_url = db_url

            # Create async engine with optimized pool settings for high concurrency
            self._engine = create_async_engine(
                async_url,
                echo=False,  # Set True for SQL debugging
                pool_size=settings.db_pool_size,  # Default: 20
                max_overflow=settings.db_max_overflow,  # Default: 40
                pool_timeout=30,  # Wait up to 30s for connection
                pool_recycle=1800,  # Recycle connections after 30 minutes
                pool_pre_ping=True,  # Verify connections before use
                poolclass=AsyncAdaptedQueuePool,
            )

            # Create async session factory
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,  # Don't expire objects after commit
                autoflush=False,  # Manual flush for better control
            )

            # Test connection
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))

            self._initialized = True
            logger.info(
                f"Async database initialized with pool_size={settings.db_pool_size}, "
                f"max_overflow={settings.db_max_overflow}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize async database: {e}")
            self._engine = None
            self._session_factory = None
            return False

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Context manager for database sessions.
        Automatically handles commit/rollback and cleanup.

        Usage:
            async with db_manager.session() as session:
                result = await session.execute(query)
        """
        if not self._initialized or self._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

    @asynccontextmanager
    async def read_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Context manager for read-only database sessions.
        No commit, optimized for queries.

        Usage:
            async with db_manager.read_session() as session:
                result = await session.execute(select_query)
        """
        if not self._initialized or self._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        session = self._session_factory()
        try:
            yield session
        finally:
            await session.close()

    async def health_check(self) -> dict:
        """
        Check database connection health.

        Returns:
            Dictionary with health status and pool statistics
        """
        if not self._initialized or self._engine is None:
            return {
                "status": "not_initialized",
                "connected": False
            }

        try:
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))

            pool = self._engine.pool
            return {
                "status": "healthy",
                "connected": True,
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalidatedcount() if hasattr(pool, 'invalidatedcount') else 0
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }

    async def close(self) -> None:
        """Gracefully close all database connections."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            self._initialized = False
            logger.info("Async database connections closed")

    @property
    def is_initialized(self) -> bool:
        """Check if database is initialized."""
        return self._initialized


# Global instance accessor
_db_manager: Optional[AsyncDatabaseManager] = None


async def get_db_manager() -> AsyncDatabaseManager:
    """
    Get the global async database manager instance.
    Initializes on first call if database URL is configured.
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = await AsyncDatabaseManager.get_instance()
        if settings.database_url:
            await _db_manager.initialize()
    return _db_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    Usage in endpoints:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_db_session)):
            ...
    """
    manager = await get_db_manager()
    if not manager.is_initialized:
        raise RuntimeError("Database not available")

    async with manager.session() as session:
        yield session


__all__ = [
    'AsyncDatabaseManager',
    'get_db_manager',
    'get_db_session',
]
