"""
Test multi-domain provider recognition and web search.
Tests medical, logistics, business, and academic domains.
"""
import requests
import json
import time

API_BASE = "http://localhost:8001"


def test_multi_domain_search(domain: str, skill: str, user_level: str = "beginner"):
    """Test web search for different professional domains."""
    print(f"\n{'='*60}")
    print(f"Testing: {domain.upper()} Domain - '{skill}'")
    print('='*60)

    data = {
        "gap": {
            "title": skill,
            "description": f"Learning {skill} for {domain} professionals"
        },
        "user_level": user_level,
        "max_days": 30,
        "cost_preference": "any",
        "limit": 5,
        "search_mode": "hybrid"  # Use hybrid to get both local + web
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
            sources_used = result.get("sources_used", [])

            print(f"✅ Success ({duration:.2f}s)")
            print(f"   Found: {len(resources)} resources")
            print(f"   Sources: {', '.join(sources_used) if sources else 'N/A'}")

            # Count providers by category
            provider_counts = {}
            for r in resources:
                provider = r.get("provider", "Unknown")
                provider_counts[provider] = provider_counts.get(provider, 0) + 1

            if resources:
                print(f"\n   Top {min(5, len(resources))} Resources:")
                for i, r in enumerate(resources[:5], 1):
                    source_badge = r.get("source_badge", "Unknown")
                    provider = r.get("provider", "Unknown")
                    print(f"   {i}. [{source_badge}] {r['title']}")
                    print(f"      Provider: {provider} | Type: {r.get('type', 'N/A')} | "
                          f"Duration: {r.get('duration_days', 0)} days | Cost: {r.get('cost', 'N/A')}")
                    print(f"      URL: {r.get('url', 'N/A')[:70]}...")

                print(f"\n   Providers Found:")
                for provider, count in sorted(provider_counts.items()):
                    print(f"      - {provider}: {count}")
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


def run_multi_domain_tests():
    """Run tests across multiple professional domains."""
    print("\n" + "="*60)
    print("MULTI-DOMAIN PROVIDER RECOGNITION TEST SUITE")
    print("="*60)

    test_cases = [
        # Medical & Healthcare
        ("Medical", "Medical Terminology", "beginner"),
        ("Medical", "Pharmacology", "intermediate"),
        ("Medical", "Clinical Skills", "beginner"),

        # Logistics & Supply Chain
        ("Logistics", "Supply Chain Management", "intermediate"),
        ("Logistics", "Warehouse Operations", "beginner"),
        ("Logistics", "Transportation Management", "intermediate"),

        # Business & Management
        ("Business", "Project Management", "intermediate"),
        ("Business", "Financial Analysis", "beginner"),
        ("Business", "Leadership Skills", "intermediate"),

        # Academic & Student
        ("Academic", "Calculus", "beginner"),
        ("Academic", "World History", "intermediate"),
        ("Academic", "Chemistry Basics", "beginner"),

        # Design & Creative
        ("Design", "Graphic Design", "beginner"),
        ("Design", "UI/UX Design", "intermediate"),

        # Language Learning
        ("Language", "Spanish for Beginners", "beginner"),
        ("Language", "Business English", "intermediate"),

        # Software Development (original domain)
        ("Technology", "Python Programming", "beginner"),
        ("Technology", "React Development", "intermediate")
    ]

    results = []
    for i, (domain, skill, level) in enumerate(test_cases, 1):
        print(f"\n[Test {i}/{len(test_cases)}]")
        success = test_multi_domain_search(domain, skill, level)
        results.append((domain, skill, success))

        # Rate limiting - wait between requests
        if i < len(test_cases):
            time.sleep(3)

    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)

    passed = sum(1 for _, _, success in results if success)
    total = len(results)

    # Group by domain
    domain_results = {}
    for domain, skill, success in results:
        if domain not in domain_results:
            domain_results[domain] = {"passed": 0, "total": 0}
        domain_results[domain]["total"] += 1
        if success:
            domain_results[domain]["passed"] += 1

    for domain in sorted(domain_results.keys()):
        stats = domain_results[domain]
        status = "✅" if stats["passed"] == stats["total"] else "⚠️"
        print(f"{status} {domain}: {stats['passed']}/{stats['total']} tests passed")

    print(f"\n Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 All domains tested successfully! Multi-domain support is working!")
    elif passed >= total * 0.75:
        print("\n⚠️  Most tests passed. Some domains may need additional providers.")
    else:
        print("\n❌ Multiple failures. Check SearXNG and provider list.")

    print("="*60)


if __name__ == "__main__":
    try:
        run_multi_domain_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
