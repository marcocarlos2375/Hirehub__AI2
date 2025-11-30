"""
Comprehensive Metrics Collection (Phase 2.5).
Tracks performance, costs, and system health across all workflow components.

Metrics Categories:
1. Performance: Latency, throughput, cache hit rates
2. Costs: LLM token usage, API call costs
3. Quality: Question quality scores, refinement rates
4. System Health: Error rates, resource usage
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


# ========================================
# Metric Data Models
# ========================================

@dataclass
class PerformanceMetric:
    """Single performance measurement."""
    operation: str
    duration_ms: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CostMetric:
    """Single cost measurement."""
    operation: str
    input_tokens: int
    output_tokens: int
    cache_hit: bool
    cost_usd: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityMetric:
    """Single quality measurement."""
    question_id: str
    gap_priority: str
    quality_score: int
    refinement_count: int
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


# ========================================
# Metrics Collector
# ========================================

class MetricsCollector:
    """
    Collects and aggregates metrics across workflow (Phase 2.5).

    Features:
    - Real-time metric collection
    - Aggregation by time window (1min, 5min, 1hour, 1day)
    - Percentile calculations (p50, p95, p99)
    - Cost tracking with cache-aware pricing
    - Quality trends over time
    """

    def __init__(self, retention_hours: int = 24):
        """
        Initialize metrics collector.

        Args:
            retention_hours: How long to keep raw metrics (default 24h)
        """
        self.retention_hours = retention_hours

        # Raw metrics storage (with automatic cleanup)
        self._performance_metrics: List[PerformanceMetric] = []
        self._cost_metrics: List[CostMetric] = []
        self._quality_metrics: List[QualityMetric] = []

        # Real-time counters
        self._operation_counts = defaultdict(int)
        self._error_counts = defaultdict(int)
        self._cache_stats = {
            "l1_hits": 0,
            "l1_misses": 0,
            "l2_hits": 0,
            "l2_misses": 0,
            "prompt_cache_hits": 0,
            "prompt_cache_misses": 0
        }

        # System health
        self._health_checks = defaultdict(lambda: {"status": "unknown", "last_check": None})

    # ========================================
    # Performance Tracking
    # ========================================

    def record_performance(
        self,
        operation: str,
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record a performance metric.

        Args:
            operation: Operation name (e.g., "question_generation", "quality_evaluation")
            duration_ms: Duration in milliseconds
            metadata: Optional metadata (e.g., {"gap_priority": "CRITICAL"})
        """
        metric = PerformanceMetric(
            operation=operation,
            duration_ms=duration_ms,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )

        self._performance_metrics.append(metric)
        self._operation_counts[operation] += 1
        self._cleanup_old_metrics()

    def get_performance_stats(
        self,
        operation: Optional[str] = None,
        time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Get performance statistics.

        Args:
            operation: Filter by operation name (None = all operations)
            time_window_minutes: Time window for stats (default 60min)

        Returns:
            Dict with p50, p95, p99, avg, min, max latencies
        """
        cutoff = datetime.utcnow() - timedelta(minutes=time_window_minutes)

        # Filter metrics
        metrics = [
            m for m in self._performance_metrics
            if m.timestamp >= cutoff and (operation is None or m.operation == operation)
        ]

        if not metrics:
            return {
                "operation": operation or "all",
                "count": 0,
                "time_window_minutes": time_window_minutes
            }

        durations = [m.duration_ms for m in metrics]

        return {
            "operation": operation or "all",
            "count": len(metrics),
            "time_window_minutes": time_window_minutes,
            "avg_ms": round(statistics.mean(durations), 2),
            "median_ms": round(statistics.median(durations), 2),
            "p95_ms": round(self._percentile(durations, 0.95), 2),
            "p99_ms": round(self._percentile(durations, 0.99), 2),
            "min_ms": round(min(durations), 2),
            "max_ms": round(max(durations), 2),
            "total_time_seconds": round(sum(durations) / 1000, 2)
        }

    # ========================================
    # Cost Tracking
    # ========================================

    def record_llm_cost(
        self,
        operation: str,
        input_tokens: int,
        output_tokens: int,
        cache_hit: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record LLM API cost.

        Args:
            operation: Operation name
            input_tokens: Input token count
            output_tokens: Output token count
            cache_hit: Whether prompt cache was used
            metadata: Optional metadata
        """
        # Gemini pricing (as of 2025)
        INPUT_COST_PER_1K = 0.001  # $0.001 per 1K input tokens
        OUTPUT_COST_PER_1K = 0.002  # $0.002 per 1K output tokens
        CACHE_DISCOUNT = 0.5  # 50% discount on cached input tokens

        # Calculate cost
        input_cost = (input_tokens / 1000) * INPUT_COST_PER_1K
        if cache_hit:
            input_cost *= CACHE_DISCOUNT

        output_cost = (output_tokens / 1000) * OUTPUT_COST_PER_1K
        total_cost = input_cost + output_cost

        metric = CostMetric(
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_hit=cache_hit,
            cost_usd=total_cost,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )

        self._cost_metrics.append(metric)
        self._cleanup_old_metrics()

    def get_cost_stats(
        self,
        operation: Optional[str] = None,
        time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Get cost statistics.

        Args:
            operation: Filter by operation name (None = all)
            time_window_minutes: Time window (default 60min)

        Returns:
            Dict with total cost, token usage, cache hit rate
        """
        cutoff = datetime.utcnow() - timedelta(minutes=time_window_minutes)

        # Filter metrics
        metrics = [
            m for m in self._cost_metrics
            if m.timestamp >= cutoff and (operation is None or m.operation == operation)
        ]

        if not metrics:
            return {
                "operation": operation or "all",
                "count": 0,
                "time_window_minutes": time_window_minutes
            }

        total_cost = sum(m.cost_usd for m in metrics)
        total_input_tokens = sum(m.input_tokens for m in metrics)
        total_output_tokens = sum(m.output_tokens for m in metrics)
        cache_hits = sum(1 for m in metrics if m.cache_hit)
        cache_hit_rate = (cache_hits / len(metrics)) * 100 if metrics else 0

        return {
            "operation": operation or "all",
            "count": len(metrics),
            "time_window_minutes": time_window_minutes,
            "total_cost_usd": round(total_cost, 4),
            "avg_cost_per_call_usd": round(total_cost / len(metrics), 6),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "projected_daily_cost_usd": round(total_cost * (1440 / time_window_minutes), 2),
            "projected_monthly_cost_usd": round(total_cost * (1440 / time_window_minutes) * 30, 2)
        }

    # ========================================
    # Quality Tracking
    # ========================================

    def record_quality(
        self,
        question_id: str,
        gap_priority: str,
        quality_score: int,
        refinement_count: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record answer quality metric.

        Args:
            question_id: Question identifier
            gap_priority: Gap priority level
            quality_score: Quality score (0-10)
            refinement_count: Number of refinement iterations
            metadata: Optional metadata
        """
        metric = QualityMetric(
            question_id=question_id,
            gap_priority=gap_priority,
            quality_score=quality_score,
            refinement_count=refinement_count,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )

        self._quality_metrics.append(metric)
        self._cleanup_old_metrics()

    def get_quality_stats(
        self,
        gap_priority: Optional[str] = None,
        time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Get quality statistics.

        Args:
            gap_priority: Filter by gap priority (None = all)
            time_window_minutes: Time window (default 60min)

        Returns:
            Dict with avg quality, refinement rate, acceptance rate
        """
        cutoff = datetime.utcnow() - timedelta(minutes=time_window_minutes)

        # Filter metrics
        metrics = [
            m for m in self._quality_metrics
            if m.timestamp >= cutoff and (gap_priority is None or m.gap_priority == gap_priority)
        ]

        if not metrics:
            return {
                "gap_priority": gap_priority or "all",
                "count": 0,
                "time_window_minutes": time_window_minutes
            }

        quality_scores = [m.quality_score for m in metrics]
        refinement_counts = [m.refinement_count for m in metrics]
        needed_refinement = sum(1 for m in metrics if m.refinement_count > 0)

        return {
            "gap_priority": gap_priority or "all",
            "count": len(metrics),
            "time_window_minutes": time_window_minutes,
            "avg_quality_score": round(statistics.mean(quality_scores), 2),
            "median_quality_score": round(statistics.median(quality_scores), 2),
            "min_quality_score": min(quality_scores),
            "max_quality_score": max(quality_scores),
            "avg_refinement_count": round(statistics.mean(refinement_counts), 2),
            "refinement_rate_percent": round((needed_refinement / len(metrics)) * 100, 2),
            "first_pass_acceptance_rate_percent": round(((len(metrics) - needed_refinement) / len(metrics)) * 100, 2)
        }

    # ========================================
    # Cache Tracking
    # ========================================

    def record_cache_hit(self, cache_type: str):
        """Record cache hit (l1, l2, prompt)."""
        key = f"{cache_type}_hits"
        if key in self._cache_stats:
            self._cache_stats[key] += 1

    def record_cache_miss(self, cache_type: str):
        """Record cache miss (l1, l2, prompt)."""
        key = f"{cache_type}_misses"
        if key in self._cache_stats:
            self._cache_stats[key] += 1

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {}

        for cache_type in ["l1", "l2", "prompt_cache"]:
            hits = self._cache_stats[f"{cache_type}_hits"]
            misses = self._cache_stats[f"{cache_type}_misses"]
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0

            stats[cache_type] = {
                "hits": hits,
                "misses": misses,
                "total": total,
                "hit_rate_percent": round(hit_rate, 2)
            }

        return stats

    # ========================================
    # Error Tracking
    # ========================================

    def record_error(self, operation: str, error_type: str):
        """Record an error occurrence."""
        key = f"{operation}:{error_type}"
        self._error_counts[key] += 1

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        total_errors = sum(self._error_counts.values())

        return {
            "total_errors": total_errors,
            "errors_by_type": dict(self._error_counts),
            "top_errors": sorted(
                self._error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }

    # ========================================
    # System Health
    # ========================================

    def record_health_check(self, component: str, status: str, details: Optional[Dict] = None):
        """
        Record component health check.

        Args:
            component: Component name (e.g., "redis", "qdrant", "llm")
            status: "healthy", "degraded", "down"
            details: Optional details dict
        """
        self._health_checks[component] = {
            "status": status,
            "last_check": datetime.utcnow(),
            "details": details or {}
        }

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        components = {}

        for component, info in self._health_checks.items():
            components[component] = {
                "status": info["status"],
                "last_check": info["last_check"].isoformat() if info["last_check"] else None,
                "details": info["details"]
            }

        # Overall status
        statuses = [info["status"] for info in self._health_checks.values()]
        if any(s == "down" for s in statuses):
            overall = "degraded"
        elif any(s == "degraded" for s in statuses):
            overall = "degraded"
        elif statuses:
            overall = "healthy"
        else:
            overall = "unknown"

        return {
            "overall_status": overall,
            "components": components,
            "last_update": datetime.utcnow().isoformat()
        }

    # ========================================
    # Dashboard Summary
    # ========================================

    def get_dashboard_summary(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """
        Get comprehensive dashboard summary.

        Args:
            time_window_minutes: Time window for stats (default 60min)

        Returns:
            Dict with performance, cost, quality, cache, and health stats
        """
        return {
            "time_window_minutes": time_window_minutes,
            "timestamp": datetime.utcnow().isoformat(),
            "performance": {
                "all_operations": self.get_performance_stats(time_window_minutes=time_window_minutes),
                "top_operations": self._get_top_operations(limit=5)
            },
            "costs": self.get_cost_stats(time_window_minutes=time_window_minutes),
            "quality": self.get_quality_stats(time_window_minutes=time_window_minutes),
            "cache": self.get_cache_stats(),
            "errors": self.get_error_stats(),
            "health": self.get_system_health()
        }

    # ========================================
    # Utilities
    # ========================================

    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile from data."""
        if not data:
            return 0.0

        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]

    def _get_top_operations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top N operations by call count."""
        sorted_ops = sorted(
            self._operation_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        return [
            {
                "operation": op,
                "count": count,
                "stats": self.get_performance_stats(operation=op, time_window_minutes=60)
            }
            for op, count in sorted_ops
        ]

    def _cleanup_old_metrics(self):
        """Remove metrics older than retention period."""
        cutoff = datetime.utcnow() - timedelta(hours=self.retention_hours)

        self._performance_metrics = [
            m for m in self._performance_metrics if m.timestamp >= cutoff
        ]
        self._cost_metrics = [
            m for m in self._cost_metrics if m.timestamp >= cutoff
        ]
        self._quality_metrics = [
            m for m in self._quality_metrics if m.timestamp >= cutoff
        ]

    def reset_stats(self):
        """Reset all statistics (useful for testing)."""
        self._performance_metrics.clear()
        self._cost_metrics.clear()
        self._quality_metrics.clear()
        self._operation_counts.clear()
        self._error_counts.clear()
        self._cache_stats = {
            "l1_hits": 0,
            "l1_misses": 0,
            "l2_hits": 0,
            "l2_misses": 0,
            "prompt_cache_hits": 0,
            "prompt_cache_misses": 0
        }


# ========================================
# Singleton Instance
# ========================================

_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """Get singleton metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


# ========================================
# Context Manager for Performance Tracking
# ========================================

class track_performance:
    """
    Context manager for automatic performance tracking.

    Usage:
        with track_performance("question_generation", metadata={"gap_priority": "CRITICAL"}):
            result = generate_question(gap)
    """

    def __init__(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        self.operation = operation
        self.metadata = metadata or {}
        self.start_time = None
        self.collector = get_metrics_collector()

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000

        # Record error if exception occurred
        if exc_type is not None:
            self.collector.record_error(self.operation, exc_type.__name__)

        # Always record performance
        self.collector.record_performance(
            operation=self.operation,
            duration_ms=duration_ms,
            metadata=self.metadata
        )

        return False  # Don't suppress exceptions


# ========================================
# Example Usage
# ========================================

if __name__ == "__main__":
    """Test metrics collector."""
    print("=" * 80)
    print("Testing Metrics Collector (Phase 2.5)")
    print("=" * 80)

    collector = get_metrics_collector()

    # Simulate some operations
    print("\n✅ Simulating operations...")

    # Record performance
    collector.record_performance("question_generation", 1200, {"gap_priority": "CRITICAL"})
    collector.record_performance("question_generation", 950, {"gap_priority": "IMPORTANT"})
    collector.record_performance("question_generation", 800, {"gap_priority": "MEDIUM"})
    collector.record_performance("quality_evaluation", 600)
    collector.record_performance("answer_refinement", 1500)

    # Record costs
    collector.record_llm_cost("question_generation", 500, 150, cache_hit=False)
    collector.record_llm_cost("question_generation", 500, 150, cache_hit=True)
    collector.record_llm_cost("quality_evaluation", 300, 100, cache_hit=True)

    # Record quality
    collector.record_quality("q1", "CRITICAL", 9, 0)
    collector.record_quality("q2", "IMPORTANT", 5, 2)
    collector.record_quality("q3", "MEDIUM", 7, 1)

    # Record cache events
    collector.record_cache_hit("l1")
    collector.record_cache_hit("l1")
    collector.record_cache_miss("l1")
    collector.record_cache_hit("prompt_cache")

    # Get dashboard
    print("\n📊 Dashboard Summary:")
    print("=" * 80)

    summary = collector.get_dashboard_summary()

    print(f"\n⏱️  Performance (last 60min):")
    print(f"   Operations: {summary['performance']['all_operations']['count']}")
    print(f"   Avg latency: {summary['performance']['all_operations'].get('avg_ms', 0)}ms")
    print(f"   P95 latency: {summary['performance']['all_operations'].get('p95_ms', 0)}ms")

    print(f"\n💰 Costs (last 60min):")
    print(f"   Total cost: ${summary['costs'].get('total_cost_usd', 0):.4f}")
    print(f"   Cache hit rate: {summary['costs'].get('cache_hit_rate_percent', 0)}%")
    print(f"   Projected monthly: ${summary['costs'].get('projected_monthly_cost_usd', 0):.2f}")

    print(f"\n✨ Quality (last 60min):")
    print(f"   Avg score: {summary['quality'].get('avg_quality_score', 0)}/10")
    print(f"   Refinement rate: {summary['quality'].get('refinement_rate_percent', 0)}%")

    print(f"\n🗄️  Cache Stats:")
    for cache_type, stats in summary['cache'].items():
        print(f"   {cache_type}: {stats['hit_rate_percent']}% hit rate ({stats['hits']}/{stats['total']})")

    print("\n" + "=" * 80)
    print("Metrics collector test complete!")
    print("=" * 80)
