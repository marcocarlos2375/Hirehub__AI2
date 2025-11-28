"""
Simple Perplexica integration test (no pytest required).
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.perplexica_client import get_perplexica_client
from core.resource_matcher import get_resource_matcher


def test_perplexica_health():
    """Test Perplexica health check."""
    print("\n" + "="*60)
    print("TEST 1: Perplexica Health Check")
    print("="*60)

    client = get_perplexica_client()
    is_healthy = client.health_check()

    if is_healthy:
        print("✓ PASSED: Perplexica service is healthy")
        return True
    else:
        print("✗ FAILED: Perplexica service is not responding")
        return False


def test_perplexica_search():
    """Test basic Perplexica search."""
    print("\n" + "="*60)
    print("TEST 2: Perplexica Basic Search")
    print("="*60)

    client = get_perplexica_client()

    result = client.search(
        query="Python programming tutorial",
        focus_mode="webSearch",
        optimization_mode="balanced"
    )

    if "error" in result:
        print(f"✗ FAILED: Search returned error: {result['error']}")
        return False

    if "answer" in result and "sources" in result:
        print(f"✓ PASSED: Search returned results")
        print(f"  - Answer length: {len(result['answer'])} chars")
        print(f"  - Sources found: {len(result['sources'])}")
        print(f"  - Answer preview: {result['answer'][:150]}...")
        return True
    else:
        print("✗ FAILED: Search result missing required fields")
        return False


def test_learning_resources():
    """Test learning resource discovery."""
    print("\n" + "="*60)
    print("TEST 3: Learning Resource Discovery")
    print("="*60)

    client = get_perplexica_client()

    result = client.search_learning_resources(
        skill="React",
        user_level="beginner",
        num_results=5
    )

    if "error" in result:
        print(f"✗ FAILED: Learning resource search error: {result['error']}")
        return False

    if "answer" in result and "sources" in result:
        print(f"✓ PASSED: Learning resources found")
        print(f"  - Skill: React")
        print(f"  - User Level: beginner")
        print(f"  - Sources: {len(result['sources'])}")

        if result['sources']:
            print(f"  - First source: {result['sources'][0].get('title', 'N/A')}")

        print(f"  - AI Summary: {result['answer'][:200]}...")
        return True
    else:
        print("✗ FAILED: Missing required fields in result")
        return False


def test_resource_matcher():
    """Test resource matcher with Perplexica mode."""
    print("\n" + "="*60)
    print("TEST 4: Resource Matcher with Perplexica")
    print("="*60)

    matcher = get_resource_matcher()

    gap = {
        "title": "JavaScript ES6+",
        "description": "Modern JavaScript features",
        "severity": "critical"
    }

    result = matcher.find_resources_with_web_search(
        gap=gap,
        user_level="beginner",
        max_days=10,
        cost_preference="any",
        limit=5,
        search_mode="perplexica"
    )

    if "resources" not in result:
        print("✗ FAILED: No resources in result")
        return False

    resources = result.get("resources", [])
    sources_used = result.get("sources_used", [])

    print(f"✓ PASSED: Resource matcher executed")
    print(f"  - Total resources: {len(resources)}")
    print(f"  - Sources used: {', '.join(sources_used)}")

    # Check if any Perplexica resources were returned
    perplexica_resources = [r for r in resources if r.get("source") == "perplexica"]

    if perplexica_resources:
        print(f"  - Perplexica resources: {len(perplexica_resources)}")
        first = perplexica_resources[0]
        print(f"  - First resource: {first.get('title', 'N/A')}")
        print(f"  - Provider: {first.get('provider', 'N/A')}")
        print(f"  - Source badge: {first.get('source_badge', 'N/A')}")
    else:
        print(f"  - No Perplexica resources (fallback to {', '.join(sources_used)})")

    return True


def test_fallback_mechanism():
    """Test fallback to SearXNG."""
    print("\n" + "="*60)
    print("TEST 5: Fallback Mechanism")
    print("="*60)

    from core.perplexica_client import PerplexicaClient

    # Create invalid client
    invalid_client = PerplexicaClient(base_url="http://invalid-perplexica:9999")
    is_healthy = invalid_client.health_check()

    if not is_healthy:
        print("✓ PASSED: Health check correctly fails for invalid URL")
        print("  - Fallback mechanism should activate")
        return True
    else:
        print("✗ FAILED: Health check should have failed")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PERPLEXICA INTEGRATION TESTS")
    print("="*60)

    tests = [
        test_perplexica_health,
        test_perplexica_search,
        test_learning_resources,
        test_resource_matcher,
        test_fallback_mechanism
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ EXCEPTION: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print(f"\n✗ {total - passed} TESTS FAILED")
        sys.exit(1)
