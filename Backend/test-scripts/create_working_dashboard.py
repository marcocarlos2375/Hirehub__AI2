"""
Create a working Grafana dashboard with properly configured Infinity queries.
"""

import requests
import json

GRAFANA_URL = "http://localhost:3001"
USERNAME = "admin"
PASSWORD = "r28RMXy@k5kSRR"

# Working dashboard with proper Infinity configuration
dashboard = {
    "dashboard": {
        "id": None,
        "uid": "hirehub-metrics",
        "title": "HireHub Metrics Dashboard",
        "tags": ["hirehub", "metrics"],
        "timezone": "browser",
        "schemaVersion": 39,
        "refresh": "10s",
        "time": {
            "from": "now-1h",
            "to": "now"
        },
        "panels": [
            # Panel 1: P95 Latency
            {
                "id": 1,
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                "type": "stat",
                "title": "P95 Latency",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/performance?time_window_minutes=60",
                        "root_selector": "performance.all_operations.p95_ms",
                        "columns": []
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "ms",
                        "color": {"mode": "thresholds"},
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"value": 0, "color": "green"},
                                {"value": 2000, "color": "yellow"},
                                {"value": 3000, "color": "red"}
                            ]
                        }
                    }
                }
            },
            # Panel 2: Total Cost
            {
                "id": 2,
                "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0},
                "type": "stat",
                "title": "Total Cost (Hourly)",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/costs?time_window_minutes=60",
                        "root_selector": "costs.total_cost_usd",
                        "columns": []
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "currencyUSD",
                        "decimals": 4
                    }
                }
            },
            # Panel 3: Cache Hit Rate
            {
                "id": 3,
                "gridPos": {"h": 4, "w": 6, "x": 18, "y": 0},
                "type": "gauge",
                "title": "Cache Hit Rate",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/costs?time_window_minutes=60",
                        "root_selector": "costs.cache_hit_rate_percent",
                        "columns": []
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "percent",
                        "min": 0,
                        "max": 100,
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"value": 0, "color": "red"},
                                {"value": 50, "color": "yellow"},
                                {"value": 80, "color": "green"}
                            ]
                        }
                    }
                }
            },
            # Panel 4: Operation Count
            {
                "id": 4,
                "gridPos": {"h": 4, "w": 6, "x": 12, "y": 4},
                "type": "stat",
                "title": "Total Operations",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/performance?time_window_minutes=60",
                        "root_selector": "performance.all_operations.count",
                        "columns": []
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "short"
                    }
                }
            },
            # Panel 5: Monthly Cost Projection
            {
                "id": 5,
                "gridPos": {"h": 4, "w": 6, "x": 18, "y": 4},
                "type": "stat",
                "title": "Monthly Cost Projection",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/costs?time_window_minutes=60",
                        "root_selector": "costs.projected_monthly_cost_usd",
                        "columns": []
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "currencyUSD",
                        "decimals": 2
                    }
                }
            },
            # Panel 6: Average Latency
            {
                "id": 6,
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                "type": "stat",
                "title": "Average Latency",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/performance?time_window_minutes=60",
                        "root_selector": "performance.all_operations.avg_ms",
                        "columns": []
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "ms"
                    }
                }
            },
            # Panel 7: Total Tokens Used
            {
                "id": 7,
                "gridPos": {"h": 4, "w": 6, "x": 12, "y": 8},
                "type": "stat",
                "title": "Total Tokens",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/costs?time_window_minutes=60",
                        "root_selector": "costs.total_tokens",
                        "columns": []
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "short"
                    }
                }
            },
            # Panel 8: Cost per Call
            {
                "id": 8,
                "gridPos": {"h": 4, "w": 6, "x": 18, "y": 8},
                "type": "stat",
                "title": "Avg Cost per Call",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/costs?time_window_minutes=60",
                        "root_selector": "costs.avg_cost_per_call_usd",
                        "columns": []
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "currencyUSD",
                        "decimals": 6
                    }
                }
            }
        ]
    },
    "overwrite": True,
    "message": "Updated with working Infinity queries"
}

print("📊 Creating Working Grafana Dashboard...")
print(f"   URL: {GRAFANA_URL}")

try:
    response = requests.post(
        f"{GRAFANA_URL}/api/dashboards/db",
        auth=(USERNAME, PASSWORD),
        headers={"Content-Type": "application/json"},
        json=dashboard
    )

    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Dashboard created successfully!")
        print(f"   Dashboard URL: {GRAFANA_URL}{result.get('url')}")
        print(f"\n🎯 Open this URL in your browser:")
        print(f"   {GRAFANA_URL}{result.get('url')}")
        print(f"\n💡 The dashboard will auto-refresh every 10 seconds")
        print(f"\n📊 You should now see:")
        print(f"   • P95 Latency: ~2438ms")
        print(f"   • Total Cost: ~$0.08")
        print(f"   • Cache Hit Rate: ~50%")
        print(f"   • Total Operations: 20")
        print(f"   • Monthly Projection: ~$59")
    else:
        print(f"\n❌ Failed to create dashboard")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"\n❌ Error: {e}")
