"""
Simple script to populate metrics with test data.
Uses the MetricsCollector directly to generate realistic metrics.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.metrics_collector import get_metrics_collector
import time
import random

def populate_performance_metrics():
    """Generate performance metrics."""
    collector = get_metrics_collector()

    print("\n📊 Generating Performance Metrics...")

    operations = [
        ("generate_deep_dive_prompts", "CRITICAL"),
        ("evaluate_quality", "IMPORTANT"),
        ("refine_answer", "MEDIUM"),
        ("search_resources", "HIGH"),
        ("generate_learning_plan", "LOW"),
    ]

    for i in range(30):
        operation, priority = random.choice(operations)

        # Simulate operation with random latency
        latency_ms = random.uniform(200, 2000)

        collector.record_performance(
            operation=operation,
            duration_ms=latency_ms,
            metadata={
                "gap_priority": priority,
                "test_run": i + 1
            }
        )

    print(f"   ✅ Generated {i+1} performance metrics")


def populate_cost_metrics():
    """Generate cost metrics."""
    collector = get_metrics_collector()

    print("\n💰 Generating Cost Metrics...")

    operations = [
        "generate_deep_dive_prompts",
        "evaluate_quality",
        "refine_answer",
        "search_resources",
    ]

    for i in range(25):
        operation = random.choice(operations)

        # Simulate LLM call costs
        input_tokens = random.randint(500, 3000)
        output_tokens = random.randint(200, 1500)
        cache_hit = random.random() > 0.3  # 70% cache hit rate

        collector.record_llm_cost(
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_hit=cache_hit,
            metadata={
                "test_run": i + 1
            }
        )

    print(f"   ✅ Generated {i+1} cost metrics")


def populate_quality_metrics():
    """Generate quality metrics."""
    collector = get_metrics_collector()

    print("\n⭐ Generating Quality Metrics...")

    priorities = ["CRITICAL", "IMPORTANT", "MEDIUM", "LOW"]

    for i in range(20):
        priority = random.choice(priorities)

        # Simulate quality scores (0-10)
        quality_score = int(random.uniform(5.0, 9.5))
        refinement_count = 1 if quality_score < 7 else 0

        collector.record_quality(
            question_id=f"test-q-{i}",
            gap_priority=priority,
            quality_score=quality_score,
            refinement_count=refinement_count,
            metadata={
                "test_run": i + 1
            }
        )

    print(f"   ✅ Generated {i+1} quality metrics")


def show_metrics_summary():
    """Display metrics summary."""
    collector = get_metrics_collector()

    print("\n" + "=" * 80)
    print("  METRICS SUMMARY")
    print("=" * 80)

    # Get dashboard summary
    summary = collector.get_dashboard_summary(time_window_minutes=60)

    # Performance
    perf = summary["performance"]["all_operations"]
    print(f"\n📊 Performance:")
    print(f"   Total Operations: {perf.get('total_operations', 0)}")
    print(f"   Avg Latency: {perf.get('avg_latency_ms', 0):.2f}ms")
    print(f"   P95 Latency: {perf.get('p95_ms', 0):.2f}ms")
    print(f"   Error Rate: {perf.get('error_rate', 0):.2%}")

    # Costs
    costs = summary.get("costs", {})
    print(f"\n💰 Costs:")
    print(f"   Total Cost: ${costs.get('total_cost_usd', 0):.4f}")
    print(f"   Avg Cost/Call: ${costs.get('avg_cost_per_call', 0):.6f}")
    print(f"   Cache Hit Rate: {costs.get('cache_hit_rate_percent', 0):.1f}%")
    print(f"   Monthly Projection: ${costs.get('projected_monthly_cost_usd', 0):.2f}")

    # Quality
    quality = summary.get("quality", {})
    print(f"\n⭐ Quality:")
    print(f"   Avg Quality Score: {quality.get('avg_quality_score', 0):.2f}/10")
    print(f"   Refinement Rate: {quality.get('refinement_rate_percent', 0):.1f}%")
    print(f"   First-Pass Acceptance: {quality.get('first_pass_acceptance_percent', 0):.1f}%")

    # Cache
    cache_data = summary.get("cache", {}).get("prompt_cache", {})
    print(f"\n🗄️  Cache:")
    print(f"   Hit Rate: {cache_data.get('hit_rate_percent', 0):.1f}%")
    print(f"   Total Requests: {cache_data.get('total_requests', 0)}")

    # Health
    health = summary.get("health", {})
    print(f"\n❤️  Health:")
    print(f"   Status: {health.get('overall_status', 'unknown')}")

    print("\n" + "=" * 80)


def main():
    """Main function."""
    print("=" * 80)
    print("  POPULATING METRICS FOR GRAFANA")
    print("=" * 80)

    # Generate test data
    populate_performance_metrics()
    populate_cost_metrics()
    populate_quality_metrics()

    # Show summary
    show_metrics_summary()

    print("\n✅ Metrics populated successfully!")
    print("\n📊 You can now view the data in:")
    print("   • Grafana: http://localhost:3001")
    print("   • API Dashboard: http://localhost:8001/api/metrics/dashboard")
    print("\n💡 Refresh the Grafana dashboard to see the new data!")


if __name__ == "__main__":
    main()
