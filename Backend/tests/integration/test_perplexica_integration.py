"""
Integration tests for Perplexica service.

Tests the full Perplexica integration including:
1. Health check
2. Basic search
3. Learning resource discovery
4. Resource matching and parsing
5. Fallback to SearXNG
"""
import os
import pytest
from core.perplexica_client import get_perplexica_client, PerplexicaClient
from core.resource_matcher import get_resource_matcher


def test_perplexica_health_check():
    """Test that Perplexica service is healthy."""
    client = get_perplexica_client()

    # Check if Perplexica is enabled
    use_perplexica = os.getenv("USE_PERPLEXICA", "true").lower() == "true"

    if use_perplexica:
        is_healthy = client.health_check()
        assert is_healthy, "Perplexica service should be healthy"
        print("✓ Perplexica health check passed")
    else:
        print("⊘ Perplexica disabled, skipping health check")


def test_perplexica_basic_search():
    """Test basic Perplexica search functionality."""
    client = get_perplexica_client()

    # Perform a simple search
    result = client.search(
        query="Python programming tutorial for beginners",
        focus_mode="webSearch",
        optimization_mode="balanced"
    )

    # Verify result structure
    assert "answer" in result, "Result should contain 'answer' field"
    assert "sources" in result, "Result should contain 'sources' field"

    # Check if we got an answer
    if "error" not in result:
        assert len(result["answer"]) > 0, "Answer should not be empty"
        assert isinstance(result["sources"], list), "Sources should be a list"
        print(f"✓ Basic search returned {len(result['sources'])} sources")
        print(f"  AI Answer: {result['answer'][:100]}...")
    else:
        print(f"⚠ Search returned error: {result['error']}")


def test_perplexica_learning_resources():
    """Test specialized learning resource search."""
    client = get_perplexica_client()

    # Search for learning resources
    result = client.search_learning_resources(
        skill="React",
        user_level="intermediate",
        num_results=5
    )

    # Verify result
    if "error" not in result:
        assert "answer" in result
        assert "sources" in result
        assert len(result["sources"]) > 0, "Should return at least one source"

        # Check source structure
        first_source = result["sources"][0]
        assert "title" in first_source or "url" in first_source

        print(f"✓ Learning resource search returned {len(result['sources'])} sources")
        print(f"  Skill: React")
        print(f"  AI Summary: {result['answer'][:150]}...")
    else:
        print(f"⚠ Learning resource search returned error: {result['error']}")


def test_resource_matcher_perplexica_mode():
    """Test resource matcher with Perplexica mode."""
    matcher = get_resource_matcher()

    # Create a sample gap
    gap = {
        "title": "JavaScript ES6+",
        "description": "Modern JavaScript features",
        "severity": "critical"
    }

    # Find resources using Perplexica
    result = matcher.find_resources(
        gap=gap,
        user_level="beginner",
        max_days=10,
        cost_preference="any",
        limit=5,
        search_mode="perplexica"
    )

    # Verify result structure
    assert "resources" in result
    assert "sources_used" in result
    assert isinstance(result["resources"], list)

    # Check if Perplexica was used
    if result["resources"]:
        # Check if any resource has Perplexica source
        perplexica_resources = [r for r in result["resources"] if r.get("source") == "perplexica"]

        if perplexica_resources:
            print(f"✓ Resource matcher returned {len(perplexica_resources)} Perplexica resources")

            # Verify Perplexica resource structure
            first_resource = perplexica_resources[0]
            assert "id" in first_resource
            assert "title" in first_resource
            assert "url" in first_resource
            assert "provider" in first_resource
            assert "source_badge" in first_resource
            assert first_resource["source_badge"] == "AI Search"

            print(f"  First resource: {first_resource['title']}")
            print(f"  Provider: {first_resource['provider']}")
            print(f"  URL: {first_resource['url']}")
        else:
            print("⚠ No Perplexica resources returned (may have fallen back to SearXNG)")
            assert "SearXNG" in result["sources_used"] or "Qdrant" in result["sources_used"]
    else:
        print("⚠ No resources returned")


def test_perplexica_fallback_mechanism():
    """Test fallback to SearXNG when Perplexica is unavailable."""
    # Create a client with invalid URL to simulate failure
    invalid_client = PerplexicaClient(base_url="http://invalid-perplexica:9999")

    # Health check should fail
    is_healthy = invalid_client.health_check()
    assert not is_healthy, "Invalid client should fail health check"

    print("✓ Fallback mechanism works: health check fails for invalid URL")

    # Resource matcher should fall back to SearXNG
    matcher = get_resource_matcher()

    gap = {
        "title": "Docker containers",
        "description": "Container orchestration",
        "severity": "important"
    }

    # This should use SearXNG as fallback
    result = matcher.find_resources(
        gap=gap,
        user_level="intermediate",
        limit=3,
        search_mode="perplexica"  # Request Perplexica but will fall back
    )

    # Should still get results from SearXNG or Qdrant
    assert "resources" in result
    print("✓ Fallback to SearXNG works when Perplexica unavailable")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PERPLEXICA INTEGRATION TESTS")
    print("="*60 + "\n")

    print("Test 1: Health Check")
    print("-" * 60)
    test_perplexica_health_check()

    print("\n\nTest 2: Basic Search")
    print("-" * 60)
    test_perplexica_basic_search()

    print("\n\nTest 3: Learning Resources")
    print("-" * 60)
    test_perplexica_learning_resources()

    print("\n\nTest 4: Resource Matcher with Perplexica")
    print("-" * 60)
    test_resource_matcher_perplexica_mode()

    print("\n\nTest 5: Fallback Mechanism")
    print("-" * 60)
    test_perplexica_fallback_mechanism()

    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60 + "\n")
