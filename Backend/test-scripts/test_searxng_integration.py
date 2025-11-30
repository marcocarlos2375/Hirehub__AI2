"""
Test SearXNG integration with hybrid search.
Tests local_only, web_only, and hybrid search modes.
"""
import requests
import json
import time

API_BASE = "http://localhost:8001"


def test_search_mode(search_mode: str, gap_title: str):
    """Test a specific search mode."""
    print(f"\n{'='*60}")
    print(f"Testing: {search_mode.upper()} mode for '{gap_title}'")
    print('='*60)

    data = {
        "gap": {
            "title": gap_title,
            "description": f"Learning {gap_title} for web development"
        },
        "user_level": "beginner",
        "max_days": 10,
        "cost_preference": "any",
        "limit": 3,
        "search_mode": search_mode
    }

    start = time.time()
    try:
        response = requests.post(
            f"{API_BASE}/api/adaptive-questions/get-learning-resources",
            json=data,
            timeout=60
        )
        duration = time.time() - start

        if response.status_code == 200:
            result = response.json()
            resources = result.get("resources", [])
            sources = result.get("sources_used", [])

            print(f"✅ Success ({duration:.2f}s)")
            print(f"   Found: {len(resources)} resources")
            print(f"   Sources: {', '.join(sources) if sources else 'N/A'}")

            if resources:
                print(f"\n   Top 3 Resources:")
                for i, r in enumerate(resources[:3], 1):
                    source_badge = r.get("source_badge", "Unknown")
                    print(f"   {i}. [{source_badge}] {r['title']}")
                    print(f"      {r.get('provider', 'Unknown')} | {r.get('type', 'N/A')} | "
                          f"{r.get('duration_days', 0)} days | {r.get('cost', 'N/A')}")
                    print(f"      URL: {r.get('url', 'N/A')[:60]}...")
            else:
                print("   ⚠️  No resources found")

            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_searxng_health():
    """Test SearXNG health check."""
    print(f"\n{'='*60}")
    print("SearXNG Health Check")
    print('='*60)

    try:
        response = requests.get("http://localhost:8888/healthz", timeout=5)
        if response.status_code == 200:
            print("✅ SearXNG is healthy")
            return True
        else:
            print(f"⚠️  SearXNG returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ SearXNG not accessible: {str(e)}")
        return False


def test_searxng_direct_search():
    """Test direct SearXNG search."""
    print(f"\n{'='*60}")
    print("Direct SearXNG Search Test")
    print('='*60)

    try:
        response = requests.get(
            "http://localhost:8888/search",
            params={"q": "Python tutorial", "format": "json"},
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            print(f"✅ Direct search works: {len(results)} results")
            if results:
                print(f"   First result: {results[0].get('title', 'N/A')}")
            return True
        else:
            print(f"❌ Search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Direct search error: {str(e)}")
        return False


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "="*60)
    print("SEARXNG INTEGRATION TEST SUITE")
    print("="*60)

    results = []

    # Test 1: SearXNG Health
    results.append(("SearXNG Health", test_searxng_health()))
    time.sleep(1)

    # Test 2: Direct SearXNG Search
    results.append(("Direct SearXNG Search", test_searxng_direct_search()))
    time.sleep(2)

    # Test 3: Local Only Mode
    results.append(("Local Only Mode", test_search_mode("local_only", "React")))
    time.sleep(2)

    # Test 4: Web Only Mode
    results.append(("Web Only Mode", test_search_mode("web_only", "Vue.js")))
    time.sleep(2)

    # Test 5: Hybrid Mode (most important)
    results.append(("Hybrid Mode", test_search_mode("hybrid", "Svelte")))

    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")

    print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 All tests passed! SearXNG integration is working perfectly!")
    elif passed >= 3:
        print("\n⚠️  Most tests passed. Some features may need debugging.")
    else:
        print("\n❌ Multiple failures. Check SearXNG and API configuration.")

    print("="*60)


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
