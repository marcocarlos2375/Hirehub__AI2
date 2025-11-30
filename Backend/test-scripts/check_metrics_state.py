"""Check the current state of metrics collector."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.metrics_collector import get_metrics_collector

collector = get_metrics_collector()

print("=" * 80)
print("  METRICS COLLECTOR STATE")
print("=" * 80)

# Check performance metrics
print(f"\n📊 Performance Metrics:")
print(f"   Total entries: {len(collector._performance_metrics)}")
if collector._performance_metrics:
    print(f"   Sample entries (last 3):")
    for entry in collector._performance_metrics[-3:]:
        print(f"      {entry}")

# Check cost metrics
print(f"\n💰 Cost Metrics:")
print(f"   Total entries: {len(collector._cost_metrics)}")
if collector._cost_metrics:
    print(f"   Sample entries (last 3):")
    for entry in collector._cost_metrics[-3:]:
        print(f"      {entry}")

# Check quality metrics
print(f"\n⭐ Quality Metrics:")
print(f"   Total entries: {len(collector._quality_metrics)}")
if collector._quality_metrics:
    print(f"   Sample entries (last 3):")
    for entry in collector._quality_metrics[-3:]:
        print(f"      {entry}")

# Check cache metrics
print(f"\n🗄️  Cache Metrics:")
print(f"   Prompt cache hits: {collector._cache_metrics.get('prompt_cache_hits', 0)}")
print(f"   Prompt cache misses: {collector._cache_metrics.get('prompt_cache_misses', 0)}")

print("\n" + "=" * 80)
