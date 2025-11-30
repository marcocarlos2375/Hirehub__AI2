"""
Create a super simple dashboard using JSON query mode with explicit paths.
"""

import requests

GRAFANA_URL = "http://localhost:3001"
USERNAME = "admin"
PASSWORD = "r28RMXy@k5kSRR"

# Ultra-simple dashboard with backend parser
dashboard = {
    "dashboard": {
        "id": None,
        "uid": "hirehub-simple",
        "title": "HireHub Metrics (Simple)",
        "tags": ["hirehub"],
        "timezone": "browser",
        "schemaVersion": 39,
        "refresh": "10s",
        "panels": [
            {
                "id": 1,
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                "type": "stat",
                "title": "P95 Latency (ms)",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "url": "/api/metrics/performance?time_window_minutes=60",
                        "format": "backend",
                        "parser": "backend",
                        "root_selector": "$",
                        "jsonata": "all_operations.p95_ms"
                    }
                ]
            },
            {
                "id": 2,
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                "type": "stat",
                "title": "Total Cost (USD)",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "url": "/api/metrics/costs?time_window_minutes=60",
                        "format": "backend",
                        "parser": "backend",
                        "root_selector": "$",
                        "jsonata": "costs.total_cost_usd"
                    }
                ]
            }
        ]
    },
    "overwrite": True
}

print("Creating simple test dashboard...")
response = requests.post(
    f"{GRAFANA_URL}/api/dashboards/db",
    auth=(USERNAME, PASSWORD),
    headers={"Content-Type": "application/json"},
    json=dashboard
)

if response.status_code == 200:
    result = response.json()
    url = f"{GRAFANA_URL}{result['url']}"
    print(f"✅ Dashboard created: {url}")
else:
    print(f"❌ Failed: {response.status_code}")
    print(response.text)
