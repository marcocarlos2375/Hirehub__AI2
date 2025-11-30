"""
Import dashboard directly via Grafana API.
This bypasses provisioning issues.
"""

import requests
import json

GRAFANA_URL = "http://localhost:3001"
USERNAME = "admin"
PASSWORD = "r28RMXy@k5kSRR"

# Dashboard configuration
dashboard = {
    "dashboard": {
        "id": None,
        "uid": None,
        "title": "HireHub Metrics Dashboard",
        "tags": ["hirehub", "metrics", "performance"],
        "timezone": "browser",
        "schemaVersion": 16,
        "version": 0,
        "refresh": "10s",
        "panels": [
            {
                "id": 1,
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                "type": "timeseries",
                "title": "P95 Latency (Last Hour)",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/performance?time_window_minutes=60",
                        "parser": "backend",
                        "root_selector": "performance.all_operations"
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "ms",
                        "custom": {"drawStyle": "line", "showPoints": "auto"}
                    }
                }
            },
            {
                "id": 2,
                "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0},
                "type": "stat",
                "title": "Hourly Cost",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/costs?time_window_minutes=60",
                        "parser": "backend",
                        "root_selector": "costs"
                    }
                ],
                "fieldConfig": {"defaults": {"unit": "currencyUSD"}}
            },
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
                        "url": "/api/metrics/cache",
                        "parser": "backend",
                        "root_selector": "cache.prompt_cache"
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "percent",
                        "min": 0,
                        "max": 100
                    }
                }
            },
            {
                "id": 4,
                "gridPos": {"h": 4, "w": 6, "x": 12, "y": 4},
                "type": "stat",
                "title": "Average Quality Score",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/quality?time_window_minutes=60",
                        "parser": "backend",
                        "root_selector": "quality"
                    }
                ],
                "fieldConfig": {"defaults": {"unit": "short", "min": 0, "max": 10}}
            },
            {
                "id": 5,
                "gridPos": {"h": 4, "w": 6, "x": 18, "y": 4},
                "type": "table",
                "title": "System Health",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/health",
                        "parser": "backend",
                        "root_selector": "health"
                    }
                ]
            },
            {
                "id": 6,
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                "type": "timeseries",
                "title": "Monthly Cost Projection",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/costs?time_window_minutes=1440",
                        "parser": "backend",
                        "root_selector": "costs"
                    }
                ],
                "fieldConfig": {"defaults": {"unit": "currencyUSD"}}
            }
        ]
    },
    "overwrite": True,
    "message": "Imported via API"
}

print("📊 Importing HireHub Metrics Dashboard to Grafana...")
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
        print(f"\n✅ Dashboard imported successfully!")
        print(f"   Dashboard ID: {result.get('id')}")
        print(f"   Dashboard UID: {result.get('uid')}")
        print(f"   Dashboard URL: {result.get('url')}")
        print(f"\n🎯 Access your dashboard at:")
        print(f"   {GRAFANA_URL}{result.get('url')}")
    else:
        print(f"\n❌ Failed to import dashboard")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"\n❌ Error: {e}")
