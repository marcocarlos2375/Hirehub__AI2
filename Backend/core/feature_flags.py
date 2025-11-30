"""
Feature Flags System (Phase 3.5).
Enable A/B testing and gradual rollout of optimizations.
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


# ========================================
# Feature Flag Models
# ========================================

class FlagStatus(str, Enum):
    """Feature flag status."""
    ENABLED = "enabled"
    DISABLED = "disabled"
    PERCENTAGE = "percentage"  # Percentage-based rollout


@dataclass
class FeatureFlag:
    """Single feature flag configuration."""
    name: str
    status: FlagStatus
    description: str
    rollout_percentage: int = 0  # 0-100 for percentage rollout
    enabled_for_users: list = None  # Specific user IDs
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.enabled_for_users is None:
            self.enabled_for_users = []
        if self.metadata is None:
            self.metadata = {}


# ========================================
# Feature Flags Manager
# ========================================

class FeatureFlagsManager:
    """
    Feature flags manager (Phase 3.5).

    Features:
    - On/off toggles
    - Percentage-based rollout
    - User-based targeting
    - Persistent storage (file/Redis)
    - A/B testing support
    """

    def __init__(self, storage_path: str = "data/feature_flags.json"):
        """
        Initialize feature flags manager.

        Args:
            storage_path: Path to JSON file for flag persistence
        """
        self.storage_path = storage_path
        self.flags: Dict[str, FeatureFlag] = {}

        # Load flags from storage
        self._load_flags()

        # Initialize default flags if none exist
        if not self.flags:
            self._initialize_default_flags()

    def _load_flags(self):
        """Load flags from storage."""
        if not os.path.exists(self.storage_path):
            return

        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)

            for name, flag_data in data.items():
                self.flags[name] = FeatureFlag(
                    name=name,
                    status=FlagStatus(flag_data['status']),
                    description=flag_data['description'],
                    rollout_percentage=flag_data.get('rollout_percentage', 0),
                    enabled_for_users=flag_data.get('enabled_for_users', []),
                    metadata=flag_data.get('metadata', {})
                )
        except Exception as e:
            print(f"Warning: Could not load feature flags: {e}")

    def _save_flags(self):
        """Save flags to storage."""
        os.makedirs(os.path.dirname(self.storage_path) or '.', exist_ok=True)

        data = {}
        for name, flag in self.flags.items():
            data[name] = {
                'status': flag.status.value,
                'description': flag.description,
                'rollout_percentage': flag.rollout_percentage,
                'enabled_for_users': flag.enabled_for_users,
                'metadata': flag.metadata
            }

        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _initialize_default_flags(self):
        """Initialize default feature flags."""
        default_flags = [
            FeatureFlag(
                name="use_prompt_cache_optimizer",
                status=FlagStatus.ENABLED,
                description="Use optimized prompt structure for caching (Phase 2.4)"
            ),
            FeatureFlag(
                name="use_batch_generation",
                status=FlagStatus.ENABLED,
                description="Use batch question generation API (Phase 2.3)"
            ),
            FeatureFlag(
                name="dynamic_quality_thresholds",
                status=FlagStatus.ENABLED,
                description="Use dynamic quality thresholds by priority (Phase 1 Quick Win #1)"
            ),
            FeatureFlag(
                name="parallel_rag_searches",
                status=FlagStatus.ENABLED,
                description="Use parallel RAG searches (Phase 1 Quick Win #3)"
            ),
            FeatureFlag(
                name="experimental_llm_model",
                status=FlagStatus.DISABLED,
                description="Use experimental Gemini model (gemini-2.0-flash-exp vs flash-lite)"
            ),
            FeatureFlag(
                name="experimental_embedding_model",
                status=FlagStatus.DISABLED,
                description="Use experimental embedding model (text-embedding-005 vs 004)"
            ),
            FeatureFlag(
                name="advanced_quality_evaluation",
                status=FlagStatus.PERCENTAGE,
                rollout_percentage=50,
                description="Use advanced quality evaluation with more criteria"
            ),
        ]

        for flag in default_flags:
            self.flags[flag.name] = flag

        self._save_flags()

    # ========================================
    # Flag Operations
    # ========================================

    def is_enabled(
        self,
        flag_name: str,
        user_id: Optional[str] = None,
        default: bool = False
    ) -> bool:
        """
        Check if feature flag is enabled.

        Args:
            flag_name: Name of the flag
            user_id: Optional user ID for user-based targeting
            default: Default value if flag doesn't exist

        Returns:
            True if flag is enabled, False otherwise
        """
        if flag_name not in self.flags:
            return default

        flag = self.flags[flag_name]

        # Check status
        if flag.status == FlagStatus.ENABLED:
            return True

        if flag.status == FlagStatus.DISABLED:
            return False

        # Percentage-based rollout
        if flag.status == FlagStatus.PERCENTAGE:
            # Check if user explicitly enabled
            if user_id and user_id in flag.enabled_for_users:
                return True

            # Use user_id hash for consistent assignment
            if user_id:
                user_hash = hash(user_id) % 100
                return user_hash < flag.rollout_percentage

            # No user_id: random assignment based on percentage
            import random
            return random.randint(0, 99) < flag.rollout_percentage

        return default

    def enable(self, flag_name: str):
        """Enable a feature flag."""
        if flag_name not in self.flags:
            raise ValueError(f"Flag {flag_name} does not exist")

        self.flags[flag_name].status = FlagStatus.ENABLED
        self._save_flags()

    def disable(self, flag_name: str):
        """Disable a feature flag."""
        if flag_name not in self.flags:
            raise ValueError(f"Flag {flag_name} does not exist")

        self.flags[flag_name].status = FlagStatus.DISABLED
        self._save_flags()

    def set_rollout_percentage(self, flag_name: str, percentage: int):
        """
        Set rollout percentage for gradual rollout.

        Args:
            flag_name: Name of the flag
            percentage: Rollout percentage (0-100)
        """
        if flag_name not in self.flags:
            raise ValueError(f"Flag {flag_name} does not exist")

        if not 0 <= percentage <= 100:
            raise ValueError("Percentage must be between 0 and 100")

        self.flags[flag_name].status = FlagStatus.PERCENTAGE
        self.flags[flag_name].rollout_percentage = percentage
        self._save_flags()

    def enable_for_user(self, flag_name: str, user_id: str):
        """Enable flag for specific user."""
        if flag_name not in self.flags:
            raise ValueError(f"Flag {flag_name} does not exist")

        if user_id not in self.flags[flag_name].enabled_for_users:
            self.flags[flag_name].enabled_for_users.append(user_id)
            self._save_flags()

    def disable_for_user(self, flag_name: str, user_id: str):
        """Disable flag for specific user."""
        if flag_name not in self.flags:
            raise ValueError(f"Flag {flag_name} does not exist")

        if user_id in self.flags[flag_name].enabled_for_users:
            self.flags[flag_name].enabled_for_users.remove(user_id)
            self._save_flags()

    # ========================================
    # Flag Management
    # ========================================

    def list_flags(self) -> Dict[str, Dict[str, Any]]:
        """List all feature flags."""
        return {
            name: {
                'status': flag.status.value,
                'description': flag.description,
                'rollout_percentage': flag.rollout_percentage,
                'enabled_for_users_count': len(flag.enabled_for_users),
                'metadata': flag.metadata
            }
            for name, flag in self.flags.items()
        }

    def get_flag(self, flag_name: str) -> Optional[FeatureFlag]:
        """Get feature flag by name."""
        return self.flags.get(flag_name)

    def create_flag(
        self,
        name: str,
        description: str,
        status: FlagStatus = FlagStatus.DISABLED
    ):
        """Create a new feature flag."""
        if name in self.flags:
            raise ValueError(f"Flag {name} already exists")

        self.flags[name] = FeatureFlag(
            name=name,
            status=status,
            description=description
        )
        self._save_flags()

    def delete_flag(self, flag_name: str):
        """Delete a feature flag."""
        if flag_name not in self.flags:
            raise ValueError(f"Flag {flag_name} does not exist")

        del self.flags[flag_name]
        self._save_flags()


# ========================================
# Singleton Instance
# ========================================

_feature_flags = None


def get_feature_flags() -> FeatureFlagsManager:
    """Get singleton feature flags manager."""
    global _feature_flags
    if _feature_flags is None:
        _feature_flags = FeatureFlagsManager()
    return _feature_flags


# ========================================
# Example Usage
# ========================================

if __name__ == "__main__":
    """Test feature flags."""
    print("=" * 80)
    print("Feature Flags System (Phase 3.5)")
    print("=" * 80)

    flags = get_feature_flags()

    print(f"\n📊 All Feature Flags:")
    for name, flag_info in flags.list_flags().items():
        print(f"\n   {name}:")
        print(f"      Status: {flag_info['status']}")
        print(f"      Description: {flag_info['description']}")
        if flag_info['rollout_percentage'] > 0:
            print(f"      Rollout: {flag_info['rollout_percentage']}%")

    print(f"\n🧪 Testing Flag Evaluation:")

    test_flags = [
        "use_prompt_cache_optimizer",
        "use_batch_generation",
        "experimental_llm_model",
        "advanced_quality_evaluation"
    ]

    for flag_name in test_flags:
        is_enabled = flags.is_enabled(flag_name, user_id="test_user_123")
        status = "✅ Enabled" if is_enabled else "❌ Disabled"
        print(f"   {flag_name}: {status}")

    print(f"\n🎲 Testing Percentage Rollout:")
    percentage_flag = "advanced_quality_evaluation"

    enabled_count = 0
    test_users = [f"user_{i}" for i in range(100)]

    for user_id in test_users:
        if flags.is_enabled(percentage_flag, user_id=user_id):
            enabled_count += 1

    print(f"   Flag: {percentage_flag}")
    print(f"   Target: 50% rollout")
    print(f"   Actual: {enabled_count}/100 users ({enabled_count}%)")
    print(f"   ✅ Rollout working correctly" if 45 <= enabled_count <= 55 else "⚠️  Rollout variance")

    print("\n" + "=" * 80)
