"""
Test script to generate metrics for Grafana dashboard.
This will populate all metrics endpoints with realistic data.
"""

import asyncio
import time
import requests
from typing import Dict, Any
import json

# API base URL
API_BASE_URL = "http://localhost:8001"

# Test data
SAMPLE_GAP = {
    "gap_info": {
        "title": "Docker",
        "description": "Container platform for building and deploying applications",
        "priority": "CRITICAL"
    },
    "question_id": "test-docker-1",
    "session_id": "test-session-grafana"
}

SAMPLE_INPUTS = {
    "question_id": "test-docker-1",
    "session_id": "test-session-grafana",
    "deep_dive_inputs": {
        "experience_level": "intermediate",
        "specific_tools": "Docker Compose, Kubernetes",
        "duration": "2 years"
    }
}

SAMPLE_EVALUATION = {
    "question_id": "test-docker-1",
    "session_id": "test-session-grafana",
    "quality_score": 7.5,
    "needs_refinement": False
}


def print_section(title: str):
    """Print section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_endpoint(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Test an API endpoint."""
    url = f"{API_BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "data": response.json() if response.content else {}
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def generate_test_traffic():
    """Generate test traffic to populate metrics."""
    print_section("Generating Test Traffic")

    print("\n📊 Running 20 test requests to generate metrics...\n")

    for i in range(20):
        # Test 1: Start adaptive questions
        gap_data = SAMPLE_GAP.copy()
        gap_data["question_id"] = f"test-question-{i}"
        gap_data["session_id"] = f"test-session-{i}"
        gap_data["gap_info"]["title"] = f"Test Skill {i}"

        result = test_endpoint("/api/adaptive-questions/start", "POST", gap_data)

        if result["success"]:
            print(f"✅ Request {i+1}/20: Started adaptive question")
        else:
            print(f"❌ Request {i+1}/20: Failed - {result.get('error')}")

        # Small delay between requests
        await asyncio.sleep(0.5)

    print("\n✅ Test traffic generation complete!")


def check_metrics_endpoints():
    """Check all metrics endpoints."""
    print_section("Checking Metrics Endpoints")

    endpoints = [
        ("/api/metrics/dashboard", "Dashboard Metrics"),
        ("/api/metrics/performance?time_window_minutes=60", "Performance Metrics"),
        ("/api/metrics/costs?time_window_minutes=60", "Cost Metrics"),
        ("/api/metrics/quality?time_window_minutes=60", "Quality Metrics"),
        ("/api/metrics/cache", "Cache Metrics"),
        ("/api/metrics/health", "Health Metrics"),
    ]

    results = []

    for endpoint, name in endpoints:
        print(f"\n📡 Testing: {name}")
        print(f"   Endpoint: {endpoint}")

        result = test_endpoint(endpoint, "GET")

        if result["success"]:
            data = result["data"]
            print(f"   ✅ Status: {result['status_code']}")

            # Show sample data
            if isinstance(data, dict):
                # Show top-level keys
                keys = list(data.keys())
                print(f"   📦 Response keys: {', '.join(keys)}")

                # Show some metrics if available
                if "performance" in data:
                    perf = data["performance"]
                    if "all_operations" in perf:
                        ops = perf["all_operations"]
                        print(f"   📊 P95 Latency: {ops.get('p95_ms', 'N/A')}ms")
                        print(f"   📊 Error Rate: {ops.get('error_rate', 'N/A')}")

                if "costs" in data:
                    costs = data["costs"]
                    print(f"   💰 Total Cost: ${costs.get('total_cost_usd', 'N/A')}")

                if "quality" in data:
                    quality = data["quality"]
                    print(f"   ⭐ Avg Quality: {quality.get('avg_quality_score', 'N/A')}")

                if "cache" in data:
                    cache = data["cache"]
                    if "prompt_cache" in cache:
                        pc = cache["prompt_cache"]
                        print(f"   🗄️  Cache Hit Rate: {pc.get('hit_rate_percent', 'N/A')}%")

                if "health" in data:
                    health = data["health"]
                    print(f"   ❤️  Status: {health.get('status', 'N/A')}")

            results.append({
                "endpoint": endpoint,
                "name": name,
                "success": True,
                "data": data
            })
        else:
            print(f"   ❌ Error: {result.get('error')}")
            results.append({
                "endpoint": endpoint,
                "name": name,
                "success": False,
                "error": result.get("error")
            })

    return results


def check_grafana_connection():
    """Check if Grafana is accessible."""
    print_section("Checking Grafana Connection")

    grafana_url = "http://localhost:3001"

    try:
        print(f"\n🔍 Checking Grafana at: {grafana_url}")
        response = requests.get(f"{grafana_url}/api/health", timeout=5)

        if response.status_code == 200:
            health = response.json()
            print(f"✅ Grafana is running")
            print(f"   Version: {health.get('version', 'unknown')}")
            print(f"   Database: {health.get('database', 'unknown')}")
            return True
        else:
            print(f"⚠️  Grafana responded with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Grafana: {e}")
        print(f"\n💡 Make sure Grafana is running:")
        print(f"   docker-compose up -d grafana")
        return False


def verify_grafana_datasource():
    """Verify Grafana datasource configuration."""
    print_section("Verifying Grafana Datasource")

    # Note: This requires Grafana API access
    # Using basic auth with default admin/admin credentials

    grafana_url = "http://localhost:3001"

    try:
        print(f"\n🔍 Checking Grafana datasources...")

        # Try to access datasources (requires authentication)
        response = requests.get(
            f"{grafana_url}/api/datasources",
            auth=("admin", "admin"),
            timeout=5
        )

        if response.status_code == 200:
            datasources = response.json()
            print(f"✅ Found {len(datasources)} datasource(s)")

            for ds in datasources:
                print(f"\n   📊 Datasource: {ds.get('name')}")
                print(f"      Type: {ds.get('type')}")
                print(f"      URL: {ds.get('url')}")
                print(f"      Default: {ds.get('isDefault')}")

            return True
        else:
            print(f"⚠️  Cannot access datasources (status {response.status_code})")
            print(f"   This is normal if you changed the admin password")
            return False
    except Exception as e:
        print(f"⚠️  Cannot verify datasources: {e}")
        print(f"   This is normal if you changed the admin password")
        return False


def print_summary(metrics_results):
    """Print summary and next steps."""
    print_section("Summary")

    successful = sum(1 for r in metrics_results if r["success"])
    total = len(metrics_results)

    print(f"\n📊 Metrics Endpoints: {successful}/{total} working")

    print("\n✅ What to do next:")
    print("\n1. Open Grafana in your browser:")
    print("   👉 http://localhost:3001")

    print("\n2. Login with default credentials:")
    print("   Username: admin")
    print("   Password: admin")
    print("   (Change password when prompted)")

    print("\n3. View the dashboard:")
    print("   • Click 'Dashboards' (☰ menu)")
    print("   • Click 'Browse'")
    print("   • Click 'HireHub Metrics Dashboard'")

    print("\n4. Verify panels are showing data:")
    print("   • P95 Latency - should show line chart")
    print("   • Hourly Cost - should show dollar amount")
    print("   • Cache Hit Rate - should show percentage gauge")
    print("   • System Health - should show table with components")

    print("\n5. If panels show 'No data':")
    print("   • Wait 10 seconds (auto-refresh)")
    print("   • Change time range to 'Last 15 minutes'")
    print("   • Refresh the dashboard manually")

    print("\n💡 Troubleshooting:")
    print("   • If datasource shows error: Check API is running (docker-compose ps api)")
    print("   • If dashboard is blank: Wait for provisioning (10 second interval)")
    print("   • If panels don't update: Check auto-refresh is enabled (top-right)")


async def main():
    """Main test function."""
    print("\n" + "=" * 80)
    print("  GRAFANA METRICS TEST")
    print("  Testing all metrics endpoints and Grafana connectivity")
    print("=" * 80)

    # Step 1: Check Grafana is running
    grafana_ok = check_grafana_connection()

    # Step 2: Generate test traffic
    await generate_test_traffic()

    # Step 3: Check metrics endpoints
    metrics_results = check_metrics_endpoints()

    # Step 4: Verify Grafana datasource (optional)
    if grafana_ok:
        verify_grafana_datasource()

    # Step 5: Print summary
    print_summary(metrics_results)

    print("\n" + "=" * 80)
    print("  TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
