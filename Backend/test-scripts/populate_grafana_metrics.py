"""
Generate comprehensive test metrics for Grafana dashboard.
This script calls the /api/test-metrics endpoint multiple times to create
a realistic dataset with varied performance, cost, and quality metrics.
"""

import requests
import time
import json

API_URL = "http://localhost:8001"
GRAFANA_URL = "http://localhost:3001"

def generate_metrics_batch():
    """Generate a batch of test metrics."""
    try:
        response = requests.post(f"{API_URL}/api/test-metrics")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def check_metrics_api():
    """Check if metrics are available via API."""
    try:
        # Check performance metrics
        perf_response = requests.get(f"{API_URL}/api/metrics/performance?time_window_minutes=60")
        perf_data = perf_response.json()

        # Check cost metrics
        cost_response = requests.get(f"{API_URL}/api/metrics/costs?time_window_minutes=60")
        cost_data = cost_response.json()

        # Check quality metrics
        quality_response = requests.get(f"{API_URL}/api/metrics/quality?time_window_minutes=60")
        quality_data = quality_response.json()

        return {
            "performance": perf_data.get("all_operations", {}),
            "costs": cost_data.get("costs", {}),
            "quality": quality_data.get("all_questions", {})
        }
    except Exception as e:
        print(f"   ❌ Error checking metrics: {e}")
        return None

print("=" * 70)
print("🚀 GRAFANA METRICS GENERATOR")
print("=" * 70)

print("\n📊 Step 1: Generating test metrics...")
print("   This will create realistic data for your Grafana dashboard\n")

# Generate 5 batches of metrics to create more realistic data
total_batches = 5
for i in range(1, total_batches + 1):
    print(f"   Batch {i}/{total_batches}...", end=" ")
    result = generate_metrics_batch()
    if result:
        print("✅")
    else:
        print("❌")

    # Small delay between batches
    if i < total_batches:
        time.sleep(0.5)

print("\n📈 Step 2: Verifying metrics data...")
metrics = check_metrics_api()

if metrics:
    perf = metrics.get("performance", {})
    costs = metrics.get("costs", {})
    quality = metrics.get("quality", {})

    print("\n" + "=" * 70)
    print("✅ METRICS SUCCESSFULLY GENERATED!")
    print("=" * 70)

    print("\n📊 PERFORMANCE METRICS:")
    print(f"   • Total Operations: {perf.get('count', 0)}")
    print(f"   • Average Latency: {perf.get('avg_ms', 0):.0f}ms")
    print(f"   • P95 Latency: {perf.get('p95_ms', 0):.0f}ms")
    print(f"   • P99 Latency: {perf.get('p99_ms', 0):.0f}ms")
    print(f"   • Min Latency: {perf.get('min_ms', 0):.0f}ms")
    print(f"   • Max Latency: {perf.get('max_ms', 0):.0f}ms")

    print("\n💰 COST METRICS:")
    print(f"   • Total Cost (Hourly): ${costs.get('total_cost_usd', 0):.4f}")
    print(f"   • Avg Cost per Call: ${costs.get('avg_cost_per_call_usd', 0):.6f}")
    print(f"   • Total Tokens: {costs.get('total_tokens', 0):,}")
    print(f"   • Input Tokens: {costs.get('total_input_tokens', 0):,}")
    print(f"   • Output Tokens: {costs.get('total_output_tokens', 0):,}")
    print(f"   • Cache Hit Rate: {costs.get('cache_hit_rate_percent', 0):.1f}%")
    print(f"   • Daily Projection: ${costs.get('projected_daily_cost_usd', 0):.2f}")
    print(f"   • Monthly Projection: ${costs.get('projected_monthly_cost_usd', 0):.2f}")

    print("\n⭐ QUALITY METRICS:")
    print(f"   • Total Questions: {quality.get('count', 0)}")
    print(f"   • Average Quality Score: {quality.get('avg_quality_score', 0):.1f}/10")
    print(f"   • Refinement Rate: {quality.get('refinement_rate_percent', 0):.1f}%")
    print(f"   • Avg Refinements: {quality.get('avg_refinement_count', 0):.2f}")

    print("\n" + "=" * 70)
    print("🎯 GRAFANA DASHBOARD")
    print("=" * 70)
    print(f"\n   Dashboard URL:")
    print(f"   {GRAFANA_URL}/d/hirehub-final/hirehub-metrics-dashboard")

    print("\n📝 WHAT TO DO NEXT:")
    print("   1. Open the dashboard URL above in your browser")
    print("   2. All panels should now display data")
    print("   3. Dashboard auto-refreshes every 10 seconds")
    print("   4. To generate more test data, run this script again")

    print("\n💡 TIPS:")
    print("   • Each run adds 100 operations (20 per batch × 5 batches)")
    print("   • Metrics are stored in-memory (cleared on API restart)")
    print("   • Use time_window_minutes parameter to adjust time range")

    print("\n" + "=" * 70)

else:
    print("\n❌ Failed to verify metrics. Check if API is running:")
    print(f"   curl {API_URL}/api/metrics/dashboard")

print()
