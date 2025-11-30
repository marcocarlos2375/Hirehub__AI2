"""
Redis-based state persistence for adaptive question workflow (Phase 2.2).
Enables distributed state management for multi-server deployments.

Replaces file-based snapshots (Quick Win #5) with Redis for:
- Session sharing across API instances
- Automatic TTL-based cleanup
- Better performance and scalability
"""

import json
import os
from typing import Optional, Dict, Any
from datetime import datetime

# Try to import Redis, fall back gracefully
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    try:
        import redis
        REDIS_AVAILABLE = True
    except ImportError:
        REDIS_AVAILABLE = False
        print("⚠️  redis not installed. Install with: pip install redis")

from core.answer_flow_state import AdaptiveAnswerState


class RedisStateBackend:
    """
    Redis backend for distributed state management (Phase 2.2).

    Features:
    - Async operations for better performance
    - Automatic TTL-based expiration
    - Session sharing across servers
    - Fallback to file-based persistence if Redis unavailable
    """

    def __init__(self, redis_url: Optional[str] = None, default_ttl: int = 3600):
        """
        Initialize Redis state backend.

        Args:
            redis_url: Redis connection URL (e.g., "redis://localhost:6379/1")
                      Falls back to REDIS_STATE_URL env var
            default_ttl: Default TTL in seconds (default: 1 hour)
        """
        self.redis_url = redis_url or os.getenv("REDIS_STATE_URL", "redis://localhost:6379/1")
        self.default_ttl = default_ttl
        self.redis_client = None
        self._connected = False

        if not REDIS_AVAILABLE:
            print("⚠️  Redis not available - will fall back to file-based persistence")
        else:
            self._connect()

    def _connect(self):
        """Establish Redis connection."""
        try:
            # Use async Redis client for better performance
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,  # Auto-decode strings
                encoding="utf-8"
            )
            self._connected = True
            print(f"✅ Redis state backend connected: {self.redis_url}")
        except Exception as e:
            print(f"⚠️  Redis connection failed: {e}")
            print(f"   Falling back to file-based state persistence")
            self._connected = False

    @staticmethod
    def _serialize_state(state: AdaptiveAnswerState) -> str:
        """
        Serialize state to JSON string.
        Handles datetime objects and other non-serializable types.

        Args:
            state: Workflow state

        Returns:
            JSON string
        """
        serialized = {}

        for key, value in state.items():
            # Convert datetime to ISO format string
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            else:
                serialized[key] = value

        return json.dumps(serialized)

    @staticmethod
    def _deserialize_state(data: str) -> AdaptiveAnswerState:
        """
        Deserialize state from JSON string.
        Converts ISO datetime strings back to datetime objects.

        Args:
            data: JSON string

        Returns:
            Workflow state
        """
        parsed = json.loads(data)
        state: AdaptiveAnswerState = {}

        for key, value in parsed.items():
            # Convert ISO strings back to datetime for known fields
            if key in ["started_at", "completed_at"] and isinstance(value, str):
                try:
                    state[key] = datetime.fromisoformat(value)
                except (ValueError, TypeError):
                    state[key] = value
            else:
                state[key] = value

        return state

    @staticmethod
    def _get_state_key(session_id: str, question_id: str) -> str:
        """Generate Redis key for state."""
        return f"session:{session_id}:question:{question_id}"

    async def save_state(
        self,
        session_id: str,
        question_id: str,
        state: AdaptiveAnswerState,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Save state to Redis with TTL (ASYNC - Phase 2.2).

        Args:
            session_id: Session UUID
            question_id: Question identifier
            state: Workflow state to save
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            True if saved successfully, False otherwise
        """
        if not self._connected or not self.redis_client:
            return False

        try:
            key = self._get_state_key(session_id, question_id)
            serialized = self._serialize_state(state)
            actual_ttl = ttl if ttl is not None else self.default_ttl

            # Set with TTL (async operation)
            await self.redis_client.setex(key, actual_ttl, serialized)

            return True

        except Exception as e:
            print(f"⚠️  Redis save_state failed: {e}")
            return False

    async def load_state(
        self,
        session_id: str,
        question_id: str
    ) -> Optional[AdaptiveAnswerState]:
        """
        Load state from Redis (ASYNC - Phase 2.2).

        Args:
            session_id: Session UUID
            question_id: Question identifier

        Returns:
            Loaded state or None if not found
        """
        if not self._connected or not self.redis_client:
            return None

        try:
            key = self._get_state_key(session_id, question_id)

            # Get from Redis (async operation)
            data = await self.redis_client.get(key)

            if data:
                return self._deserialize_state(data)

            return None

        except Exception as e:
            print(f"⚠️  Redis load_state failed: {e}")
            return None

    async def delete_state(
        self,
        session_id: str,
        question_id: str
    ) -> bool:
        """
        Delete state from Redis (ASYNC - Phase 2.2).

        Args:
            session_id: Session UUID
            question_id: Question identifier

        Returns:
            True if deleted, False otherwise
        """
        if not self._connected or not self.redis_client:
            return False

        try:
            key = self._get_state_key(session_id, question_id)
            deleted = await self.redis_client.delete(key)

            return deleted > 0

        except Exception as e:
            print(f"⚠️  Redis delete_state failed: {e}")
            return False

    async def list_session_questions(self, session_id: str) -> list[str]:
        """
        List all question IDs for a given session (ASYNC - Phase 2.2).

        Args:
            session_id: Session UUID

        Returns:
            List of question IDs with saved state
        """
        if not self._connected or not self.redis_client:
            return []

        try:
            pattern = f"session:{session_id}:question:*"

            # Scan for matching keys (async operation)
            question_ids = []
            async for key in self.redis_client.scan_iter(match=pattern):
                # Extract question_id from key
                parts = key.split(":")
                if len(parts) == 4:  # session:{id}:question:{qid}
                    question_ids.append(parts[3])

            return question_ids

        except Exception as e:
            print(f"⚠️  Redis list_session_questions failed: {e}")
            return []

    async def get_ttl(self, session_id: str, question_id: str) -> int:
        """
        Get remaining TTL for a state (ASYNC - Phase 2.2).

        Args:
            session_id: Session UUID
            question_id: Question identifier

        Returns:
            Remaining TTL in seconds, -1 if no TTL, -2 if key doesn't exist
        """
        if not self._connected or not self.redis_client:
            return -2

        try:
            key = self._get_state_key(session_id, question_id)
            return await self.redis_client.ttl(key)

        except Exception as e:
            print(f"⚠️  Redis get_ttl failed: {e}")
            return -2

    async def extend_ttl(
        self,
        session_id: str,
        question_id: str,
        additional_seconds: int
    ) -> bool:
        """
        Extend TTL for an existing state (ASYNC - Phase 2.2).

        Args:
            session_id: Session UUID
            question_id: Question identifier
            additional_seconds: Seconds to add to current TTL

        Returns:
            True if extended, False otherwise
        """
        if not self._connected or not self.redis_client:
            return False

        try:
            key = self._get_state_key(session_id, question_id)
            current_ttl = await self.redis_client.ttl(key)

            if current_ttl > 0:
                new_ttl = current_ttl + additional_seconds
                await self.redis_client.expire(key, new_ttl)
                return True

            return False

        except Exception as e:
            print(f"⚠️  Redis extend_ttl failed: {e}")
            return False

    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self._connected = False


# ========================================
# Singleton Instance
# ========================================

_redis_backend = None


def get_redis_backend() -> RedisStateBackend:
    """
    Get singleton Redis state backend instance.

    Returns:
        RedisStateBackend instance
    """
    global _redis_backend
    if _redis_backend is None:
        _redis_backend = RedisStateBackend()
    return _redis_backend


# ========================================
# Example Usage
# ========================================

if __name__ == "__main__":
    """Test Redis state backend."""
    import asyncio
    from core.state_persistence import generate_session_id

    async def test_redis_backend():
        print("=" * 80)
        print("Testing Redis State Backend (Phase 2.2)")
        print("=" * 80)

        backend = get_redis_backend()

        if not backend._connected:
            print("\n⚠️  Redis not connected - cannot run test")
            print("   Start Redis: docker-compose up -d redis")
            return

        # Create sample state
        session_id = generate_session_id()
        question_id = "q1_test"

        sample_state: AdaptiveAnswerState = {
            "session_id": session_id,
            "question_id": question_id,
            "question_text": "Test question",
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
        saved = await backend.save_state(session_id, question_id, sample_state, ttl=300)
        print(f"   Saved: {saved}")

        print(f"\n✅ Test 2: Load State")
        loaded = await backend.load_state(session_id, question_id)
        print(f"   Loaded: {loaded is not None}")
        print(f"   Session ID: {loaded['session_id'] if loaded else 'N/A'}")

        print(f"\n✅ Test 3: Get TTL")
        ttl = await backend.get_ttl(session_id, question_id)
        print(f"   TTL: {ttl}s")

        print(f"\n✅ Test 4: Extend TTL")
        extended = await backend.extend_ttl(session_id, question_id, 60)
        print(f"   Extended: {extended}")

        print(f"\n✅ Test 5: List Session Questions")
        questions = await backend.list_session_questions(session_id)
        print(f"   Questions: {questions}")

        print(f"\n✅ Test 6: Delete State")
        deleted = await backend.delete_state(session_id, question_id)
        print(f"   Deleted: {deleted}")

        await backend.close()

        print("\n" + "=" * 80)
        print("All Redis backend tests passed!")
        print("=" * 80)

    asyncio.run(test_redis_backend())
