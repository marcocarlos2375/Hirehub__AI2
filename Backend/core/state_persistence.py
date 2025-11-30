"""
State persistence utilities for adaptive question workflow (Quick Win #5).
Enables session resumption and prevents redundant processing on user drop-off.
"""

import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from core.answer_flow_state import AdaptiveAnswerState


# State snapshot storage directory
SNAPSHOT_DIR = Path("data/state_snapshots")
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)


def generate_session_id() -> str:
    """
    Generate a unique session ID for tracking.

    Returns:
        UUID string (e.g., "f47ac10b-58cc-4372-a567-0e02b2c3d479")
    """
    return str(uuid.uuid4())


def serialize_state(state: AdaptiveAnswerState) -> Dict[str, Any]:
    """
    Serialize state to JSON-compatible format.

    Handles datetime objects and other non-serializable types.

    Args:
        state: Workflow state to serialize

    Returns:
        JSON-compatible dictionary
    """
    serialized = {}

    for key, value in state.items():
        # Convert datetime to ISO format string
        if isinstance(value, datetime):
            serialized[key] = value.isoformat()
        # Keep other types as-is (dicts, lists, strings, numbers, etc.)
        else:
            serialized[key] = value

    return serialized


def deserialize_state(data: Dict[str, Any]) -> AdaptiveAnswerState:
    """
    Deserialize state from JSON format.

    Converts ISO datetime strings back to datetime objects.

    Args:
        data: JSON-compatible dictionary

    Returns:
        Workflow state
    """
    state: AdaptiveAnswerState = {}

    for key, value in data.items():
        # Convert ISO strings back to datetime for known datetime fields
        if key in ["started_at", "completed_at"] and isinstance(value, str):
            try:
                state[key] = datetime.fromisoformat(value)
            except (ValueError, TypeError):
                state[key] = value
        else:
            state[key] = value

    return state


def save_state_snapshot(state: AdaptiveAnswerState) -> str:
    """
    Save state snapshot to disk for resumption.

    Args:
        state: Current workflow state

    Returns:
        Path to saved snapshot file
    """
    # Ensure session_id exists
    if "session_id" not in state or not state["session_id"]:
        state["session_id"] = generate_session_id()

    session_id = state["session_id"]
    question_id = state.get("question_id", "unknown")

    # Create filename: {session_id}_{question_id}.json
    filename = f"{session_id}_{question_id}.json"
    filepath = SNAPSHOT_DIR / filename

    # Serialize and save
    serialized = serialize_state(state)
    serialized["snapshot_created_at"] = datetime.utcnow().isoformat()

    with open(filepath, "w") as f:
        json.dump(serialized, f, indent=2)

    return str(filepath)


def load_state_snapshot(session_id: str, question_id: str) -> Optional[AdaptiveAnswerState]:
    """
    Load state snapshot from disk.

    Args:
        session_id: Session UUID
        question_id: Question identifier

    Returns:
        Restored state or None if not found
    """
    filename = f"{session_id}_{question_id}.json"
    filepath = SNAPSHOT_DIR / filename

    if not filepath.exists():
        return None

    try:
        with open(filepath, "r") as f:
            data = json.load(f)

        return deserialize_state(data)

    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️  Failed to load state snapshot: {e}")
        return None


def delete_state_snapshot(session_id: str, question_id: str) -> bool:
    """
    Delete state snapshot after successful completion.

    Args:
        session_id: Session UUID
        question_id: Question identifier

    Returns:
        True if deleted, False if not found
    """
    filename = f"{session_id}_{question_id}.json"
    filepath = SNAPSHOT_DIR / filename

    if filepath.exists():
        filepath.unlink()
        return True

    return False


def list_snapshots_for_session(session_id: str) -> list[str]:
    """
    List all snapshots for a given session.

    Useful for resuming an entire question flow session.

    Args:
        session_id: Session UUID

    Returns:
        List of question IDs with saved snapshots
    """
    pattern = f"{session_id}_*.json"
    snapshots = SNAPSHOT_DIR.glob(pattern)

    question_ids = []
    for snapshot_path in snapshots:
        # Extract question_id from filename
        filename = snapshot_path.stem  # Remove .json
        parts = filename.split("_", 1)  # Split on first underscore
        if len(parts) == 2:
            question_ids.append(parts[1])

    return question_ids


def cleanup_old_snapshots(max_age_hours: int = 24) -> int:
    """
    Clean up old snapshots to prevent disk bloat.

    Args:
        max_age_hours: Delete snapshots older than this (default: 24 hours)

    Returns:
        Number of snapshots deleted
    """
    from datetime import timedelta

    cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
    deleted_count = 0

    for snapshot_path in SNAPSHOT_DIR.glob("*.json"):
        try:
            # Read snapshot to check creation time
            with open(snapshot_path, "r") as f:
                data = json.load(f)

            created_at_str = data.get("snapshot_created_at")
            if created_at_str:
                created_at = datetime.fromisoformat(created_at_str)

                # Delete if older than cutoff
                if created_at < cutoff_time:
                    snapshot_path.unlink()
                    deleted_count += 1

        except (json.JSONDecodeError, IOError, ValueError, KeyError):
            # If we can't read the snapshot, skip it
            continue

    return deleted_count


def get_state_summary(state: AdaptiveAnswerState) -> Dict[str, Any]:
    """
    Get a lightweight summary of state for debugging/monitoring.

    Args:
        state: Workflow state

    Returns:
        Summary dictionary with key metrics
    """
    return {
        "session_id": state.get("session_id"),
        "question_id": state.get("question_id"),
        "user_id": state.get("user_id"),
        "current_step": state.get("current_step"),
        "has_experience": state.get("has_experience"),
        "quality_score": state.get("quality_score"),
        "refinement_iteration": state.get("refinement_iteration"),
        "answer_accepted": state.get("answer_accepted"),
        "started_at": state.get("started_at").isoformat() if state.get("started_at") else None,
        "total_time_seconds": state.get("total_time_seconds"),
        "error": state.get("error")
    }


# ========================================
# Example Usage
# ========================================

if __name__ == "__main__":
    """Test state persistence functionality."""

    print("=" * 80)
    print("Testing State Persistence (Quick Win #5)")
    print("=" * 80)

    # Create sample state
    sample_state: AdaptiveAnswerState = {
        "session_id": generate_session_id(),
        "question_id": "q1",
        "question_text": "Do you have AWS Lambda experience?",
        "question_data": {"priority": "CRITICAL"},
        "gap_info": {"title": "AWS Lambda", "description": "Serverless functions"},
        "user_id": "user123",
        "parsed_cv": {"skills": ["Python"]},
        "parsed_jd": {"required_skills": ["AWS Lambda"]},
        "language": "english",
        "current_step": "deep_dive",
        "has_experience": True,
        "chosen_path": "deep_dive",
        "experience_check_response": "yes",
        "started_at": datetime.utcnow(),
        "refinement_iteration": 0,
        "answer_accepted": False
    }

    print("\n✅ Test 1: Save State Snapshot")
    snapshot_path = save_state_snapshot(sample_state)
    print(f"   Saved to: {snapshot_path}")

    print("\n✅ Test 2: Load State Snapshot")
    loaded_state = load_state_snapshot(
        sample_state["session_id"],
        sample_state["question_id"]
    )
    assert loaded_state is not None, "Failed to load snapshot"
    print(f"   Loaded session: {loaded_state['session_id']}")
    print(f"   Current step: {loaded_state['current_step']}")

    print("\n✅ Test 3: Get State Summary")
    summary = get_state_summary(sample_state)
    print(f"   Summary: {json.dumps(summary, indent=2)}")

    print("\n✅ Test 4: List Session Snapshots")
    snapshots = list_snapshots_for_session(sample_state["session_id"])
    print(f"   Found {len(snapshots)} snapshot(s): {snapshots}")

    print("\n✅ Test 5: Delete Snapshot")
    deleted = delete_state_snapshot(
        sample_state["session_id"],
        sample_state["question_id"]
    )
    assert deleted, "Failed to delete snapshot"
    print(f"   Deleted successfully")

    print("\n" + "=" * 80)
    print("All state persistence tests passed!")
    print("=" * 80)
