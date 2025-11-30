"""
Alert Manager (Phase 3.3).
Monitors metrics and triggers alerts when thresholds are exceeded.
"""

import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass

from core.monitoring.alerting_config import get_alert_config, AlertSeverity, AlertThreshold
from core.monitoring.metrics_collector import get_metrics_collector


# ========================================
# Alert Models
# ========================================

@dataclass
class Alert:
    """Single alert instance."""
    threshold_name: str
    severity: AlertSeverity
    message: str
    current_value: float
    threshold_value: float
    recommended_actions: List[str]
    triggered_at: datetime
    metadata: Dict[str, Any]


# ========================================
# Alert Manager
# ========================================

class AlertManager:
    """
    Monitors metrics and triggers alerts (Phase 3.3).

    Features:
    - Threshold-based alerting
    - Cooldown to prevent spam
    - Multiple notification channels
    - Alert history tracking
    """

    def __init__(self):
        """Initialize alert manager."""
        self.config = get_alert_config()
        self.collector = get_metrics_collector()

        # Track last alert time for cooldown
        self._last_alert_time: Dict[str, datetime] = {}

        # Alert history (keep last 100)
        self._alert_history: List[Alert] = []
        self._max_history = 100

    def check_all_alerts(self, time_window_minutes: int = 15) -> List[Alert]:
        """
        Check all configured alert thresholds.

        Args:
            time_window_minutes: Time window for metrics (default: 15 min)

        Returns:
            List of triggered alerts
        """
        triggered_alerts = []

        # Check performance alerts
        triggered_alerts.extend(
            self._check_performance_alerts(time_window_minutes)
        )

        # Check cost alerts
        triggered_alerts.extend(
            self._check_cost_alerts(time_window_minutes)
        )

        # Check quality alerts
        triggered_alerts.extend(
            self._check_quality_alerts(time_window_minutes)
        )

        # Check health alerts
        triggered_alerts.extend(
            self._check_health_alerts()
        )

        return triggered_alerts

    # ========================================
    # Performance Alerts
    # ========================================

    def _check_performance_alerts(
        self,
        time_window_minutes: int
    ) -> List[Alert]:
        """Check performance-related alerts."""
        alerts = []

        # Get performance stats
        perf_stats = self.collector.get_performance_stats(
            time_window_minutes=time_window_minutes
        )

        if perf_stats['count'] == 0:
            return alerts  # No data to check

        # Check P95 latency thresholds
        p95_ms = perf_stats.get('p95_ms', 0)

        for threshold in self.config.performance_thresholds:
            if 'p95_latency' in threshold.name:
                alert = self._check_threshold(
                    threshold=threshold,
                    current_value=p95_ms,
                    metadata={
                        "metric": "p95_latency_ms",
                        "time_window_minutes": time_window_minutes,
                        "operation_count": perf_stats['count']
                    }
                )
                if alert:
                    alerts.append(alert)

        # Calculate error rate (if error tracking is implemented)
        total_ops = self.collector._operation_counts.get('all', 1)
        total_errors = sum(self.collector._error_counts.values())
        error_rate = (total_errors / total_ops * 100) if total_ops > 0 else 0

        for threshold in self.config.performance_thresholds:
            if 'error_rate' in threshold.name:
                alert = self._check_threshold(
                    threshold=threshold,
                    current_value=error_rate,
                    metadata={
                        "metric": "error_rate_percent",
                        "total_operations": total_ops,
                        "total_errors": total_errors
                    }
                )
                if alert:
                    alerts.append(alert)

        return alerts

    # ========================================
    # Cost Alerts
    # ========================================

    def _check_cost_alerts(self, time_window_minutes: int) -> List[Alert]:
        """Check cost-related alerts."""
        alerts = []

        # Get cost stats
        cost_stats = self.collector.get_cost_stats(
            time_window_minutes=time_window_minutes
        )

        if cost_stats['count'] == 0:
            return alerts

        # Check hourly cost
        # Convert time window to hourly rate
        hourly_cost = cost_stats['total_cost_usd'] * (60 / time_window_minutes)

        for threshold in self.config.cost_thresholds:
            if 'hourly_cost' in threshold.name:
                alert = self._check_threshold(
                    threshold=threshold,
                    current_value=hourly_cost,
                    metadata={
                        "metric": "hourly_cost_usd",
                        "time_window_cost": cost_stats['total_cost_usd'],
                        "time_window_minutes": time_window_minutes
                    }
                )
                if alert:
                    alerts.append(alert)

        # Check cache hit rate
        cache_hit_rate = cost_stats.get('cache_hit_rate_percent', 100)

        for threshold in self.config.cost_thresholds:
            if 'cache_hit_rate' in threshold.name:
                alert = self._check_threshold(
                    threshold=threshold,
                    current_value=cache_hit_rate,
                    metadata={
                        "metric": "cache_hit_rate_percent",
                        "total_calls": cost_stats['count']
                    }
                )
                if alert:
                    alerts.append(alert)

        # Check daily cost projection
        daily_cost = cost_stats.get('projected_daily_cost_usd', 0)

        for threshold in self.config.cost_thresholds:
            if 'daily_cost_projection' in threshold.name:
                alert = self._check_threshold(
                    threshold=threshold,
                    current_value=daily_cost,
                    metadata={
                        "metric": "projected_daily_cost_usd",
                        "projected_monthly_cost_usd": cost_stats.get('projected_monthly_cost_usd', 0)
                    }
                )
                if alert:
                    alerts.append(alert)

        return alerts

    # ========================================
    # Quality Alerts
    # ========================================

    def _check_quality_alerts(self, time_window_minutes: int) -> List[Alert]:
        """Check quality-related alerts."""
        alerts = []

        # Get quality stats
        quality_stats = self.collector.get_quality_stats(
            time_window_minutes=time_window_minutes
        )

        if quality_stats['count'] == 0:
            return alerts

        # Check average quality score
        avg_quality = quality_stats.get('avg_quality_score', 10)

        for threshold in self.config.quality_thresholds:
            if 'avg_quality' in threshold.name:
                alert = self._check_threshold(
                    threshold=threshold,
                    current_value=avg_quality,
                    metadata={
                        "metric": "avg_quality_score",
                        "evaluations_count": quality_stats['count'],
                        "median_score": quality_stats.get('median_quality_score', 0)
                    }
                )
                if alert:
                    alerts.append(alert)

        # Check refinement rate
        refinement_rate = quality_stats.get('refinement_rate_percent', 0)

        for threshold in self.config.quality_thresholds:
            if 'refinement_rate' in threshold.name:
                alert = self._check_threshold(
                    threshold=threshold,
                    current_value=refinement_rate,
                    metadata={
                        "metric": "refinement_rate_percent",
                        "evaluations_count": quality_stats['count']
                    }
                )
                if alert:
                    alerts.append(alert)

        # Check first-pass acceptance
        first_pass = quality_stats.get('first_pass_acceptance_rate_percent', 100)

        for threshold in self.config.quality_thresholds:
            if 'first_pass_acceptance' in threshold.name:
                alert = self._check_threshold(
                    threshold=threshold,
                    current_value=first_pass,
                    metadata={
                        "metric": "first_pass_acceptance_percent"
                    }
                )
                if alert:
                    alerts.append(alert)

        return alerts

    # ========================================
    # Health Alerts
    # ========================================

    def _check_health_alerts(self) -> List[Alert]:
        """Check system health alerts."""
        alerts = []

        # Get health status
        health = self.collector.get_system_health()

        # Check each component
        for component, info in health['components'].items():
            status = info['status']

            # Check if component is down
            if status == "down":
                threshold_name = f"{component}_down"

                # Find matching threshold
                for threshold in self.config.health_thresholds:
                    if threshold.name == threshold_name:
                        alert = self._check_threshold(
                            threshold=threshold,
                            current_value=0,  # Down = 0
                            metadata={
                                "component": component,
                                "status": status,
                                "last_check": info.get('last_check')
                            }
                        )
                        if alert:
                            alerts.append(alert)

        return alerts

    # ========================================
    # Core Alert Logic
    # ========================================

    def _check_threshold(
        self,
        threshold: AlertThreshold,
        current_value: float,
        metadata: Dict[str, Any]
    ) -> Optional[Alert]:
        """
        Check if a single threshold is exceeded.

        Returns:
            Alert if threshold exceeded and not in cooldown, None otherwise
        """
        # Check if threshold exceeded
        is_exceeded = False

        if threshold.comparison == "gt":
            is_exceeded = current_value > threshold.threshold_value
        elif threshold.comparison == "lt":
            is_exceeded = current_value < threshold.threshold_value
        elif threshold.comparison == "gte":
            is_exceeded = current_value >= threshold.threshold_value
        elif threshold.comparison == "lte":
            is_exceeded = current_value <= threshold.threshold_value
        elif threshold.comparison == "eq":
            is_exceeded = current_value == threshold.threshold_value

        if not is_exceeded:
            return None

        # Check cooldown
        if not self._is_cooldown_expired(threshold.name, threshold.cooldown_minutes):
            return None

        # Create alert
        message = threshold.message_template.format(
            value=current_value,
            threshold=threshold.threshold_value
        )

        alert = Alert(
            threshold_name=threshold.name,
            severity=threshold.severity,
            message=message,
            current_value=current_value,
            threshold_value=threshold.threshold_value,
            recommended_actions=threshold.recommended_actions,
            triggered_at=datetime.utcnow(),
            metadata=metadata
        )

        # Update last alert time
        self._last_alert_time[threshold.name] = datetime.utcnow()

        # Add to history
        self._add_to_history(alert)

        return alert

    def _is_cooldown_expired(
        self,
        threshold_name: str,
        cooldown_minutes: int
    ) -> bool:
        """Check if cooldown period has expired."""
        if threshold_name not in self._last_alert_time:
            return True

        last_alert = self._last_alert_time[threshold_name]
        cooldown_expires = last_alert + timedelta(minutes=cooldown_minutes)

        return datetime.utcnow() >= cooldown_expires

    def _add_to_history(self, alert: Alert):
        """Add alert to history."""
        self._alert_history.append(alert)

        # Keep only last N alerts
        if len(self._alert_history) > self._max_history:
            self._alert_history = self._alert_history[-self._max_history:]

    # ========================================
    # Alert Notification
    # ========================================

    def send_alert(self, alert: Alert):
        """
        Send alert to configured notification channels.

        Args:
            alert: Alert to send
        """
        enabled_channels = self.config.get_enabled_channels()

        for channel_name, channel in enabled_channels.items():
            # Check if alert severity meets channel minimum
            if not self._should_send_to_channel(alert.severity, channel.min_severity):
                continue

            # Send to channel
            if channel_name == "console":
                self._send_console_alert(alert)
            elif channel_name == "email":
                self._send_email_alert(alert)
            elif channel_name == "slack":
                self._send_slack_alert(alert)

    def _should_send_to_channel(
        self,
        alert_severity: AlertSeverity,
        channel_min_severity: AlertSeverity
    ) -> bool:
        """Check if alert should be sent to channel based on severity."""
        severity_order = {
            AlertSeverity.INFO: 0,
            AlertSeverity.WARNING: 1,
            AlertSeverity.CRITICAL: 2
        }

        return severity_order[alert_severity] >= severity_order[channel_min_severity]

    def _send_console_alert(self, alert: Alert):
        """Send alert to console."""
        severity_icon = {
            AlertSeverity.INFO: "ℹ️",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.CRITICAL: "🚨"
        }

        print("\n" + "=" * 80)
        print(f"{severity_icon[alert.severity]} ALERT: {alert.severity.value.upper()}")
        print("=" * 80)
        print(f"Threshold: {alert.threshold_name}")
        print(f"Message: {alert.message}")
        print(f"Time: {alert.triggered_at.isoformat()}")

        if alert.metadata:
            print(f"\nDetails:")
            for key, value in alert.metadata.items():
                print(f"  • {key}: {value}")

        print(f"\nRecommended Actions:")
        for i, action in enumerate(alert.recommended_actions, 1):
            print(f"  {i}. {action}")

        print("=" * 80)

    def _send_email_alert(self, alert: Alert):
        """Send alert via email (placeholder)."""
        # TODO: Implement SMTP email sending
        print(f"📧 [Email] {alert.message}")

    def _send_slack_alert(self, alert: Alert):
        """Send alert to Slack (placeholder)."""
        # TODO: Implement Slack webhook
        print(f"💬 [Slack] {alert.message}")

    # ========================================
    # Alert History
    # ========================================

    def get_alert_history(
        self,
        limit: int = 10,
        severity: Optional[AlertSeverity] = None
    ) -> List[Alert]:
        """Get recent alerts."""
        filtered = self._alert_history

        if severity:
            filtered = [a for a in filtered if a.severity == severity]

        return filtered[-limit:]

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary statistics."""
        total = len(self._alert_history)
        by_severity = {
            "info": 0,
            "warning": 0,
            "critical": 0
        }

        for alert in self._alert_history:
            by_severity[alert.severity.value] += 1

        return {
            "total_alerts": total,
            "by_severity": by_severity,
            "last_24_hours": len([
                a for a in self._alert_history
                if a.triggered_at >= datetime.utcnow() - timedelta(hours=24)
            ])
        }


# ========================================
# Singleton Instance
# ========================================

_alert_manager = None


def get_alert_manager() -> AlertManager:
    """Get singleton alert manager."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager


# ========================================
# Example Usage
# ========================================

if __name__ == "__main__":
    """Test alert manager."""
    print("=" * 80)
    print("Testing Alert Manager (Phase 3.3)")
    print("=" * 80)

    manager = get_alert_manager()

    print(f"\n📊 Checking Alerts...")

    alerts = manager.check_all_alerts(time_window_minutes=15)

    if alerts:
        print(f"\n🚨 {len(alerts)} alert(s) triggered:")
        for alert in alerts:
            manager.send_alert(alert)
    else:
        print(f"\n✅ No alerts triggered - all systems normal")

    # Show alert summary
    summary = manager.get_alert_summary()
    print(f"\n📊 Alert Summary:")
    print(f"   Total alerts (history): {summary['total_alerts']}")
    print(f"   Last 24 hours: {summary['last_24_hours']}")
    print(f"   By severity: {summary['by_severity']}")

    print("\n" + "=" * 80)
