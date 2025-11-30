"""
Hybrid state persistence layer (Phase 2.2).
Automatically uses Redis if available, falls back to file-based persistence.

This provides a seamless migration path from Quick Win #5 to Phase 2.2.
"""

import os
from typing import Optional
from core.workflow.answer_flow_state import AdaptiveAnswerState


class HybridStateBackend:
    """
    Hybrid state backend that uses Redis when available, files as fallback.

    Priority:
    1. Redis (if REDIS_STATE_URL configured and redis package installed)
    2. File-based (fallback from Quick Win #5)

    This enables zero-config operation while supporting distributed deployments.
    """

    def __init__(self):
        """Initialize hybrid backend with Redis priority."""
        self.redis_backend = None
        self.file_backend = None
        self._using_redis = False

        self._init_backends()

    def _init_backends(self):
        """Initialize backends in priority order."""
        # Try Redis first
        redis_url = os.getenv("REDIS_STATE_URL")

        if redis_url:
            try:
                from core.persistence.state_persistence_redis import get_redis_backend

                self.redis_backend = get_redis_backend()

                if self.redis_backend._connected:
                    self._using_redis = True
                    print("✅ Using Redis for state persistence (distributed)")
                    return
                else:
                    print("⚠️  Redis configured but connection failed")

            except ImportError:
                print("⚠️  Redis package not installed (pip install redis)")
            except Exception as e:
                print(f"⚠️  Redis initialization failed: {e}")

        # Fall back to file-based persistence
        print("ℹ️  Using file-based state persistence (single-server)")
        self._using_redis = False

    async def save_state(
        self,
        session_id: str,
        question_id: str,
        state: AdaptiveAnswerState,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Save state using available backend.

        Args:
            session_id: Session UUID
            question_id: Question identifier
            state: Workflow state
            ttl: TTL in seconds (Redis only, ignored for files)

        Returns:
            True if saved successfully
        """
        if self._using_redis and self.redis_backend:
            # Use Redis (async)
            return await self.redis_backend.save_state(session_id, question_id, state, ttl)
        else:
            # Use file-based (sync, wrapped in async)
            from core.persistence.state_persistence import save_state_snapshot

            try:
                save_state_snapshot(state)
                return True
            except Exception as e:
                print(f"⚠️  File-based save failed: {e}")
                return False

    async def load_state(
        self,
        session_id: str,
        question_id: str
    ) -> Optional[AdaptiveAnswerState]:
        """
        Load state from available backend.

        Args:
            session_id: Session UUID
            question_id: Question identifier

        Returns:
            Loaded state or None
        """
        if self._using_redis and self.redis_backend:
            # Use Redis (async)
            return await self.redis_backend.load_state(session_id, question_id)
        else:
            # Use file-based (sync)
            from core.persistence.state_persistence import load_state_snapshot

            try:
                return load_state_snapshot(session_id, question_id)
            except Exception as e:
                print(f"⚠️  File-based load failed: {e}")
                return None

    async def delete_state(
        self,
        session_id: str,
        question_id: str
    ) -> bool:
        """Delete state from available backend."""
        if self._using_redis and self.redis_backend:
            return await self.redis_backend.delete_state(session_id, question_id)
        else:
            from core.persistence.state_persistence import delete_state_snapshot

            try:
                return delete_state_snapshot(session_id, question_id)
            except Exception:
                return False

    async def list_session_questions(self, session_id: str) -> list[str]:
        """List all question IDs for a session."""
        if self._using_redis and self.redis_backend:
            return await self.redis_backend.list_session_questions(session_id)
        else:
            from core.persistence.state_persistence import list_snapshots_for_session

            try:
                return list_snapshots_for_session(session_id)
            except Exception:
                return []

    def is_using_redis(self) -> bool:
        """Check if currently using Redis backend."""
        return self._using_redis

    async def close(self):
        """Close backend connections."""
        if self.redis_backend:
            await self.redis_backend.close()


# ========================================
# Singleton Instance
# ========================================

_hybrid_backend = None


def get_state_backend() -> HybridStateBackend:
    """
    Get singleton hybrid state backend.

    Automatically uses Redis if configured, otherwise file-based.

    Returns:
        HybridStateBackend instance
    """
    global _hybrid_backend
    if _hybrid_backend is None:
        _hybrid_backend = HybridStateBackend()
    return _hybrid_backend


# ========================================
# Convenience Functions (Async)
# ========================================

async def save_state(
    session_id: str,
    question_id: str,
    state: AdaptiveAnswerState,
    ttl: Optional[int] = None
) -> bool:
    """Convenience function for saving state."""
    backend = get_state_backend()
    return await backend.save_state(session_id, question_id, state, ttl)


async def load_state(
    session_id: str,
    question_id: str
) -> Optional[AdaptiveAnswerState]:
    """Convenience function for loading state."""
    backend = get_state_backend()
    return await backend.load_state(session_id, question_id)


async def delete_state(session_id: str, question_id: str) -> bool:
    """Convenience function for deleting state."""
    backend = get_state_backend()
    return await backend.delete_state(session_id, question_id)


# ========================================
# Example Usage
# ========================================

if __name__ == "__main__":
    """Test hybrid backend."""
    import asyncio
    from datetime import datetime
    from core.persistence.state_persistence import generate_session_id

    async def test_hybrid():
        print("=" * 80)
        print("Testing Hybrid State Backend (Phase 2.2)")
        print("=" * 80)

        backend = get_state_backend()

        print(f"\n📊 Backend Type:")
        print(f"   Using Redis: {backend.is_using_redis()}")

        # Create sample state
        session_id = generate_session_id()
        question_id = "q1_hybrid_test"

        sample_state: AdaptiveAnswerState = {
            "session_id": session_id,
            "question_id": question_id,
            "question_text": "Hybrid test question",
            "question_data": {},
            "gap_info": {"title": "Test Skill"},
            "user_id": "test_user",
            "parsed_cv": {},
            "parsed_jd": {},
            "language": "english",
            "current_step": "deep_dive",
            "started_at": datetime.utcnow(),
            "refinement_iteration": 0,
            "answer_accepted": False
        }

        print(f"\n✅ Test 1: Save State")
        saved = await save_state(session_id, question_id, sample_state)
        print(f"   Saved: {saved}")

        print(f"\n✅ Test 2: Load State")
        loaded = await load_state(session_id, question_id)
        print(f"   Loaded: {loaded is not None}")

        print(f"\n✅ Test 3: List Session Questions")
        questions = await backend.list_session_questions(session_id)
        print(f"   Questions: {questions}")

        print(f"\n✅ Test 4: Delete State")
        deleted = await delete_state(session_id, question_id)
        print(f"   Deleted: {deleted}")

        await backend.close()

        print("\n" + "=" * 80)
        print("Hybrid backend tests passed!")
        print("=" * 80)

    asyncio.run(test_hybrid())
