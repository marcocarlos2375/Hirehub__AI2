"""
Create a fully working Grafana dashboard with properly configured Infinity queries.
This dashboard uses JSONata expressions to extract values from nested JSON.
"""

import requests
import json

GRAFANA_URL = "http://localhost:3001"
USERNAME = "admin"
PASSWORD = "r28RMXy@k5kSRR"

# Working dashboard with proper Infinity JSONata configuration
dashboard = {
    "dashboard": {
        "id": None,
        "uid": "hirehub-final",
        "title": "HireHub Metrics Dashboard",
        "tags": ["hirehub", "metrics", "production"],
        "timezone": "browser",
        "schemaVersion": 39,
        "refresh": "10s",
        "time": {
            "from": "now-1h",
            "to": "now"
        },
        "panels": [
            # Row 1: Main Performance Metrics
            {
                "id": 1,
                "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
                "type": "stat",
                "title": "P95 Latency",
                "description": "95th percentile response time for all operations",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/performance?time_window_minutes=60",
                        "root_selector": "all_operations",
                        "columns": [
                            {
                                "selector": "p95_ms",
                                "text": "P95 Latency",
                                "type": "number"
                            }
                        ]
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "ms",
                        "decimals": 0,
                        "color": {"mode": "thresholds"},
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"value": 0, "color": "green"},
                                {"value": 1500, "color": "yellow"},
                                {"value": 2500, "color": "red"}
                            ]
                        }
                    }
                }
            },
            {
                "id": 2,
                "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0},
                "type": "stat",
                "title": "Average Latency",
                "description": "Average response time for all operations",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/performance?time_window_minutes=60",
                        "root_selector": "all_operations",
                        "columns": [
                            {
                                "selector": "avg_ms",
                                "text": "Avg Latency",
                                "type": "number"
                            }
                        ]
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "ms",
                        "decimals": 0,
                        "color": {"mode": "thresholds"},
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"value": 0, "color": "green"},
                                {"value": 1000, "color": "yellow"},
                                {"value": 2000, "color": "red"}
                            ]
                        }
                    }
                }
            },
            {
                "id": 3,
                "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0},
                "type": "stat",
                "title": "Total Operations",
                "description": "Number of operations in the last hour",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/performance?time_window_minutes=60",
                        "root_selector": "all_operations",
                        "columns": [
                            {
                                "selector": "count",
                                "text": "Operations",
                                "type": "number"
                            }
                        ]
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "short",
                        "decimals": 0,
                        "color": {"mode": "palette-classic"}
                    }
                }
            },
            {
                "id": 4,
                "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0},
                "type": "stat",
                "title": "Max Latency",
                "description": "Maximum response time observed",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/performance?time_window_minutes=60",
                        "root_selector": "all_operations",
                        "columns": [
                            {
                                "selector": "max_ms",
                                "text": "Max Latency",
                                "type": "number"
                            }
                        ]
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "ms",
                        "decimals": 0,
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

            # Row 2: Cost Metrics
            {
                "id": 5,
                "gridPos": {"h": 6, "w": 6, "x": 0, "y": 8},
                "type": "stat",
                "title": "Hourly Cost",
                "description": "Total cost in the last hour",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/costs?time_window_minutes=60",
                        "root_selector": "costs",
                        "columns": [
                            {
                                "selector": "total_cost_usd",
                                "text": "Total Cost",
                                "type": "number"
                            }
                        ]
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "currencyUSD",
                        "decimals": 4,
                        "color": {"mode": "palette-classic"}
                    }
                }
            },
            {
                "id": 6,
                "gridPos": {"h": 6, "w": 6, "x": 6, "y": 8},
                "type": "stat",
                "title": "Monthly Projection",
                "description": "Projected monthly cost",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/costs?time_window_minutes=60",
                        "root_selector": "costs",
                        "columns": [
                            {
                                "selector": "projected_monthly_cost_usd",
                                "text": "Monthly Cost",
                                "type": "number"
                            }
                        ]
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "currencyUSD",
                        "decimals": 2,
                        "color": {"mode": "thresholds"},
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"value": 0, "color": "green"},
                                {"value": 100, "color": "yellow"},
                                {"value": 500, "color": "red"}
                            ]
                        }
                    }
                }
            },
            {
                "id": 7,
                "gridPos": {"h": 6, "w": 6, "x": 12, "y": 8},
                "type": "gauge",
                "title": "Cache Hit Rate",
                "description": "Percentage of cache hits",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/costs?time_window_minutes=60",
                        "root_selector": "costs",
                        "columns": [
                            {
                                "selector": "cache_hit_rate_percent",
                                "text": "Cache Hit Rate",
                                "type": "number"
                            }
                        ]
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "percent",
                        "min": 0,
                        "max": 100,
                        "decimals": 1,
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"value": 0, "color": "red"},
                                {"value": 40, "color": "yellow"},
                                {"value": 70, "color": "green"}
                            ]
                        }
                    }
                }
            },
            {
                "id": 8,
                "gridPos": {"h": 6, "w": 6, "x": 18, "y": 8},
                "type": "stat",
                "title": "Total Tokens",
                "description": "Total tokens processed",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/costs?time_window_minutes=60",
                        "root_selector": "costs",
                        "columns": [
                            {
                                "selector": "total_tokens",
                                "text": "Total Tokens",
                                "type": "number"
                            }
                        ]
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "short",
                        "decimals": 0,
                        "color": {"mode": "palette-classic"}
                    }
                }
            },

            # Row 3: Quality Metrics
            {
                "id": 9,
                "gridPos": {"h": 6, "w": 8, "x": 0, "y": 14},
                "type": "stat",
                "title": "Average Quality Score",
                "description": "Average quality evaluation score",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/quality?time_window_minutes=60",
                        "root_selector": "all_questions",
                        "columns": [
                            {
                                "selector": "avg_quality_score",
                                "text": "Avg Score",
                                "type": "number"
                            }
                        ]
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "none",
                        "min": 0,
                        "max": 10,
                        "decimals": 1,
                        "color": {"mode": "thresholds"},
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"value": 0, "color": "red"},
                                {"value": 5, "color": "yellow"},
                                {"value": 7, "color": "green"}
                            ]
                        }
                    }
                }
            },
            {
                "id": 10,
                "gridPos": {"h": 6, "w": 8, "x": 8, "y": 14},
                "type": "stat",
                "title": "Refinement Rate",
                "description": "Percentage of answers refined",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/quality?time_window_minutes=60",
                        "root_selector": "all_questions",
                        "columns": [
                            {
                                "selector": "refinement_rate_percent",
                                "text": "Refinement Rate",
                                "type": "number"
                            }
                        ]
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "percent",
                        "min": 0,
                        "max": 100,
                        "decimals": 1,
                        "color": {"mode": "thresholds"},
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"value": 0, "color": "green"},
                                {"value": 30, "color": "yellow"},
                                {"value": 60, "color": "red"}
                            ]
                        }
                    }
                }
            },
            {
                "id": 11,
                "gridPos": {"h": 6, "w": 8, "x": 16, "y": 14},
                "type": "stat",
                "title": "Total Questions",
                "description": "Total questions evaluated",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": "P51F3915E1E6FA47F"},
                        "type": "json",
                        "source": "url",
                        "format": "table",
                        "url": "/api/metrics/quality?time_window_minutes=60",
                        "root_selector": "all_questions",
                        "columns": [
                            {
                                "selector": "count",
                                "text": "Questions",
                                "type": "number"
                            }
                        ]
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "short",
                        "decimals": 0,
                        "color": {"mode": "palette-classic"}
                    }
                }
            }
        ]
    },
    "overwrite": True,
    "message": "Working dashboard with proper Infinity query configuration"
}

print("📊 Creating Working Grafana Dashboard...")
print(f"   URL: {GRAFANA_URL}")
print(f"   Dashboard UID: hirehub-final")

try:
    response = requests.post(
        f"{GRAFANA_URL}/api/dashboards/db",
        auth=(USERNAME, PASSWORD),
        headers={"Content-Type": "application/json"},
        json=dashboard
    )

    if response.status_code == 200:
        result = response.json()
        dashboard_url = f"{GRAFANA_URL}{result.get('url')}"
        print(f"\n✅ Dashboard created successfully!")
        print(f"\n🎯 Open this URL in your browser:")
        print(f"   {dashboard_url}")
        print(f"\n💡 The dashboard will auto-refresh every 10 seconds")
        print(f"\n📊 Expected metrics (from current test data):")
        print(f"   • P95 Latency: ~2437ms")
        print(f"   • Avg Latency: ~1609ms")
        print(f"   • Total Operations: 20")
        print(f"   • Hourly Cost: ~$0.07")
        print(f"   • Monthly Projection: ~$52")
        print(f"   • Cache Hit Rate: ~50%")
        print(f"   • Quality Score: 6-8/10")
        print(f"\n🔄 If panels show 'No data', generate fresh metrics:")
        print(f"   curl -X POST http://localhost:8001/api/test-metrics")
    else:
        print(f"\n❌ Failed to create dashboard")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"\n❌ Error: {e}")
