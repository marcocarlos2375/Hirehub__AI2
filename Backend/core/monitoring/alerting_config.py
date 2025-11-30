"""
Alert Configuration and Thresholds (Phase 3.3).
Defines alert rules and notification settings.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


# ========================================
# Alert Severity Levels
# ========================================

class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"           # Informational, no action needed
    WARNING = "warning"     # Attention needed, not urgent
    CRITICAL = "critical"   # Immediate action required


# ========================================
# Alert Thresholds
# ========================================

@dataclass
class AlertThreshold:
    """Single alert threshold configuration."""
    name: str
    severity: AlertSeverity
    threshold_value: float
    comparison: str  # "gt", "lt", "gte", "lte", "eq"
    message_template: str
    recommended_actions: List[str]
    cooldown_minutes: int = 15  # Prevent spam


# Performance Alert Thresholds
PERFORMANCE_THRESHOLDS = [
    AlertThreshold(
        name="high_p95_latency",
        severity=AlertSeverity.WARNING,
        threshold_value=3000,  # 3 seconds
        comparison="gt",
        message_template="P95 latency is {value}ms (threshold: {threshold}ms)",
        recommended_actions=[
            "Check LLM API status",
            "Review recent code changes",
            "Verify cache hit rates",
            "Check database query performance"
        ],
        cooldown_minutes=15
    ),
    AlertThreshold(
        name="critical_p95_latency",
        severity=AlertSeverity.CRITICAL,
        threshold_value=5000,  # 5 seconds
        comparison="gt",
        message_template="CRITICAL: P95 latency is {value}ms (threshold: {threshold}ms)",
        recommended_actions=[
            "IMMEDIATE: Check system resources",
            "IMMEDIATE: Verify LLM API availability",
            "Scale horizontally if needed",
            "Enable emergency caching"
        ],
        cooldown_minutes=5  # More frequent for critical
    ),
    AlertThreshold(
        name="high_error_rate",
        severity=AlertSeverity.WARNING,
        threshold_value=5.0,  # 5%
        comparison="gt",
        message_template="Error rate is {value}% (threshold: {threshold}%)",
        recommended_actions=[
            "Check error logs",
            "Verify external service availability",
            "Review recent deployments"
        ],
        cooldown_minutes=10
    ),
    AlertThreshold(
        name="critical_error_rate",
        severity=AlertSeverity.CRITICAL,
        threshold_value=10.0,  # 10%
        comparison="gt",
        message_template="CRITICAL: Error rate is {value}% (threshold: {threshold}%)",
        recommended_actions=[
            "IMMEDIATE: Check system health",
            "Roll back recent changes if applicable",
            "Enable fallback mechanisms"
        ],
        cooldown_minutes=5
    ),
]


# Cost Alert Thresholds
COST_THRESHOLDS = [
    AlertThreshold(
        name="high_hourly_cost",
        severity=AlertSeverity.WARNING,
        threshold_value=0.50,  # $0.50/hour
        comparison="gt",
        message_template="Hourly cost is ${value:.2f} (threshold: ${threshold:.2f})",
        recommended_actions=[
            "Review cache hit rates",
            "Check for inefficient queries",
            "Verify prompt caching is enabled",
            "Look for excessive retries"
        ],
        cooldown_minutes=60
    ),
    AlertThreshold(
        name="critical_hourly_cost",
        severity=AlertSeverity.CRITICAL,
        threshold_value=1.00,  # $1.00/hour = $720/month
        comparison="gt",
        message_template="CRITICAL: Hourly cost is ${value:.2f} (threshold: ${threshold:.2f})",
        recommended_actions=[
            "IMMEDIATE: Review unusual activity",
            "Check for runaway processes",
            "Implement rate limiting if needed",
            "Contact LLM provider support"
        ],
        cooldown_minutes=30
    ),
    AlertThreshold(
        name="low_cache_hit_rate",
        severity=AlertSeverity.WARNING,
        threshold_value=60.0,  # 60%
        comparison="lt",
        message_template="Cache hit rate is {value}% (threshold: {threshold}%)",
        recommended_actions=[
            "Review prompt structure",
            "Check cache TTL settings",
            "Verify cache warming is working",
            "Increase cache size if needed"
        ],
        cooldown_minutes=30
    ),
    AlertThreshold(
        name="high_daily_cost_projection",
        severity=AlertSeverity.WARNING,
        threshold_value=20.00,  # $20/day = $600/month
        comparison="gt",
        message_template="Daily cost projected at ${value:.2f} (threshold: ${threshold:.2f})",
        recommended_actions=[
            "Review cost trends",
            "Optimize prompt sizes",
            "Enable additional caching",
            "Consider model alternatives"
        ],
        cooldown_minutes=120  # Check less frequently
    ),
]


# Quality Alert Thresholds
QUALITY_THRESHOLDS = [
    AlertThreshold(
        name="low_avg_quality",
        severity=AlertSeverity.WARNING,
        threshold_value=6.0,  # Below 6/10
        comparison="lt",
        message_template="Average quality score is {value}/10 (threshold: {threshold}/10)",
        recommended_actions=[
            "Review prompt templates",
            "Check for prompt degradation",
            "Verify example quality",
            "Consider model fine-tuning"
        ],
        cooldown_minutes=60
    ),
    AlertThreshold(
        name="critical_avg_quality",
        severity=AlertSeverity.CRITICAL,
        threshold_value=5.0,  # Below 5/10
        comparison="lt",
        message_template="CRITICAL: Average quality score is {value}/10 (threshold: {threshold}/10)",
        recommended_actions=[
            "IMMEDIATE: Review prompt changes",
            "Roll back if quality degraded recently",
            "Check LLM model version",
            "Escalate to team lead"
        ],
        cooldown_minutes=30
    ),
    AlertThreshold(
        name="high_refinement_rate",
        severity=AlertSeverity.WARNING,
        threshold_value=50.0,  # 50%
        comparison="gt",
        message_template="Refinement rate is {value}% (threshold: {threshold}%)",
        recommended_actions=[
            "Review quality thresholds",
            "Check if prompts are too strict",
            "Analyze common refinement reasons",
            "Adjust acceptance criteria"
        ],
        cooldown_minutes=60
    ),
    AlertThreshold(
        name="low_first_pass_acceptance",
        severity=AlertSeverity.WARNING,
        threshold_value=60.0,  # Below 60%
        comparison="lt",
        message_template="First-pass acceptance is {value}% (threshold: {threshold}%)",
        recommended_actions=[
            "Improve prompt clarity",
            "Provide better examples",
            "Adjust quality thresholds",
            "Review evaluation criteria"
        ],
        cooldown_minutes=60
    ),
]


# System Health Thresholds
HEALTH_THRESHOLDS = [
    AlertThreshold(
        name="redis_down",
        severity=AlertSeverity.CRITICAL,
        threshold_value=0,  # Not used for health checks
        comparison="eq",
        message_template="Redis is down",
        recommended_actions=[
            "IMMEDIATE: Check Redis service",
            "Restart Redis if needed",
            "System will fall back to file-based state",
            "Monitor for data loss"
        ],
        cooldown_minutes=5
    ),
    AlertThreshold(
        name="qdrant_down",
        severity=AlertSeverity.CRITICAL,
        threshold_value=0,
        comparison="eq",
        message_template="Qdrant vector DB is down",
        recommended_actions=[
            "IMMEDIATE: Check Qdrant service",
            "RAG features will be degraded",
            "Restart Qdrant if needed"
        ],
        cooldown_minutes=5
    ),
    AlertThreshold(
        name="llm_high_errors",
        severity=AlertSeverity.CRITICAL,
        threshold_value=10.0,  # 10% LLM errors
        comparison="gt",
        message_template="LLM error rate is {value}% (threshold: {threshold}%)",
        recommended_actions=[
            "IMMEDIATE: Check Gemini API status",
            "Verify API key validity",
            "Check rate limits",
            "Enable fallback LLM if available"
        ],
        cooldown_minutes=5
    ),
]


# ========================================
# Notification Configuration
# ========================================

@dataclass
class NotificationChannel:
    """Configuration for a notification channel."""
    name: str
    enabled: bool
    min_severity: AlertSeverity  # Only send alerts at or above this level


# Default notification channels
NOTIFICATION_CHANNELS = {
    "console": NotificationChannel(
        name="console",
        enabled=True,
        min_severity=AlertSeverity.INFO
    ),
    "email": NotificationChannel(
        name="email",
        enabled=False,  # Requires SMTP configuration
        min_severity=AlertSeverity.WARNING
    ),
    "slack": NotificationChannel(
        name="slack",
        enabled=False,  # Requires webhook URL
        min_severity=AlertSeverity.WARNING
    ),
}


# ========================================
# Alert Configuration
# ========================================

class AlertConfig:
    """Central alert configuration."""

    def __init__(self):
        self.performance_thresholds = PERFORMANCE_THRESHOLDS
        self.cost_thresholds = COST_THRESHOLDS
        self.quality_thresholds = QUALITY_THRESHOLDS
        self.health_thresholds = HEALTH_THRESHOLDS
        self.notification_channels = NOTIFICATION_CHANNELS

    def get_all_thresholds(self) -> List[AlertThreshold]:
        """Get all configured thresholds."""
        return (
            self.performance_thresholds +
            self.cost_thresholds +
            self.quality_thresholds +
            self.health_thresholds
        )

    def get_thresholds_by_severity(
        self,
        severity: AlertSeverity
    ) -> List[AlertThreshold]:
        """Get thresholds filtered by severity."""
        return [
            t for t in self.get_all_thresholds()
            if t.severity == severity
        ]

    def get_enabled_channels(self) -> Dict[str, NotificationChannel]:
        """Get enabled notification channels."""
        return {
            name: channel
            for name, channel in self.notification_channels.items()
            if channel.enabled
        }


# ========================================
# Singleton Instance
# ========================================

_alert_config = None


def get_alert_config() -> AlertConfig:
    """Get singleton alert configuration."""
    global _alert_config
    if _alert_config is None:
        _alert_config = AlertConfig()
    return _alert_config


# ========================================
# Example Usage
# ========================================

if __name__ == "__main__":
    """Test alert configuration."""
    print("=" * 80)
    print("Alert Configuration (Phase 3.3)")
    print("=" * 80)

    config = get_alert_config()

    print(f"\n📊 Threshold Summary:")
    print(f"   Performance: {len(config.performance_thresholds)} thresholds")
    print(f"   Cost: {len(config.cost_thresholds)} thresholds")
    print(f"   Quality: {len(config.quality_thresholds)} thresholds")
    print(f"   Health: {len(config.health_thresholds)} thresholds")
    print(f"   Total: {len(config.get_all_thresholds())} thresholds")

    print(f"\n🚨 Critical Alerts:")
    for threshold in config.get_thresholds_by_severity(AlertSeverity.CRITICAL):
        print(f"   • {threshold.name}: {threshold.message_template.split(':')[-1].strip()}")

    print(f"\n⚠️  Warning Alerts:")
    for threshold in config.get_thresholds_by_severity(AlertSeverity.WARNING):
        print(f"   • {threshold.name}")

    print(f"\n📢 Notification Channels:")
    for name, channel in config.notification_channels.items():
        status = "✅ Enabled" if channel.enabled else "❌ Disabled"
        print(f"   • {name}: {status} (min severity: {channel.min_severity.value})")

    print("\n" + "=" * 80)
