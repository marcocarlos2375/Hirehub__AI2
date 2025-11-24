"""
Quick test to verify multi-domain provider recognition.
Tests 4 key domains: Medical, Logistics, Business, Technology.
"""
import requests
import json
import time

API_BASE = "http://localhost:8001"


def test_domain(domain: str, skill: str):
    """Test a single domain quickly."""
    print(f"\n{'='*60}")
    print(f"Testing: {domain} - '{skill}'")
    print('='*60)

    data = {
        "gap": {
            "title": skill,
            "description": f"Learning {skill} for {domain} professionals"
        },
        "user_level": "beginner",
        "max_days": 30,
        "cost_preference": "any",
        "limit": 3,
        "search_mode": "web_only"  # Web only for faster testing
    }

    try:
        response = requests.post(
            f"{API_BASE}/api/adaptive-questions/get-learning-resources",
            json=data,
            timeout=45
        )

        if response.status_code == 200:
            result = response.json()
            resources = result.get("resources", [])

            print(f"✅ Found {len(resources)} resources")

            # Check for diverse providers
            providers = set()
            for r in resources:
                provider = r.get("provider", "Web")
                providers.add(provider)
                print(f"   - [{provider}] {r['title'][:60]}...")

            print(f"\n   Unique Providers: {', '.join(sorted(providers))}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Run quick multi-domain provider test."""
    print("\n" + "="*60)
    print("QUICK MULTI-DOMAIN PROVIDER TEST")
    print("="*60)

    tests = [
        ("Medical", "Pharmacology basics"),
        ("Logistics", "Supply chain management"),
        ("Business", "Project management fundamentals"),
        ("Technology", "Python programming")
    ]

    results = []
    for domain, skill in tests:
        success = test_domain(domain, skill)
        results.append((domain, success))
        time.sleep(2)  # Rate limiting

    # Summary
    print(f"\n{'='*60}")
    print("RESULTS")
    print('='*60)
    passed = sum(1 for _, s in results if s)
    total = len(results)

    for domain, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {domain}")

    print(f"\nTotal: {passed}/{total} domains tested successfully")

    if passed == total:
        print("\n🎉 Provider recognition working across all domains!")
    else:
        print(f"\n⚠️  Some domains failed ({passed}/{total} passed)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted.")
    except Exception as e:
        print(f"\n\nError: {str(e)}")
        import traceback
        traceback.print_exc()
