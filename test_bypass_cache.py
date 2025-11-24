"""
Test script to verify bypass_cache parameter works
"""
import requests
import json
import time

SAMPLE_RESUME = """
MICHAEL JOHNSON
Software Engineer

Email: michael@email.com | Phone: (555) 111-2222

PROFESSIONAL SUMMARY
Software Engineer with 3 years of experience in web development.

TECHNICAL SKILLS
Programming: JavaScript, Python
Frontend: React, Vue.js
Backend: Node.js, Django

WORK EXPERIENCE
Software Engineer | TechCo
2021 - Present
- Built web applications
- Worked with APIs
"""

def test_bypass_cache():
    """Test that bypass_cache parameter works correctly"""

    print("Testing bypass_cache parameter...")
    print("=" * 80)

    url_normal = "http://localhost:8001/api/find-domains"
    url_bypass = "http://localhost:8001/api/find-domains?bypass_cache=true"

    payload = {
        "resume_text": SAMPLE_RESUME,
        "language": "english"
    }

    # First request - should hit fresh (no cache)
    print("\n📤 REQUEST 1: Normal (first time - no cache)")
    start1 = time.time()
    response1 = requests.post(url_normal, json=payload, timeout=60)
    time1 = time.time() - start1

    if response1.status_code == 200:
        data1 = response1.json()
        print(f"✅ Success: {data1.get('success')}")
        print(f"⏱️  Time: {time1:.2f}s (fresh API call)")
        print(f"📊 Domains: {data1.get('total_suggested')}")

        # Check for new fields
        if data1.get('domains') and len(data1['domains']) > 0:
            first = data1['domains'][0]
            has_new_fields = all(k in first for k in ['technical_role', 'industry', 'role_skills_to_learn', 'industry_skills_to_learn', 'industry_rationale'])
            print(f"🔍 Has new fields: {'✅ YES' if has_new_fields else '❌ NO'}")
    else:
        print(f"❌ Failed: {response1.status_code}")
        print(response1.text[:200])
        return

    # Second request - should hit cache
    print("\n📤 REQUEST 2: Normal (should hit cache)")
    start2 = time.time()
    response2 = requests.post(url_normal, json=payload, timeout=60)
    time2 = time.time() - start2

    if response2.status_code == 200:
        data2 = response2.json()
        print(f"✅ Success: {data2.get('success')}")
        print(f"⏱️  Time: {time2:.2f}s (should be fast - cached)")
        is_cached = time2 < 1.0  # Cache should be instant
        print(f"🔍 Cached: {'✅ YES' if is_cached else '⚠️  MAYBE (slow)'}")
    else:
        print(f"❌ Failed: {response2.status_code}")

    # Third request - bypass cache
    print("\n📤 REQUEST 3: With bypass_cache=true (force fresh)")
    start3 = time.time()
    response3 = requests.post(url_bypass, json=payload, timeout=60)
    time3 = time.time() - start3

    if response3.status_code == 200:
        data3 = response3.json()
        print(f"✅ Success: {data3.get('success')}")
        print(f"⏱️  Time: {time3:.2f}s (fresh API call, bypassed cache)")
        is_fresh = time3 > 5.0  # Fresh call should take several seconds
        print(f"🔍 Fresh call: {'✅ YES' if is_fresh else '⚠️  MAYBE (too fast)'}")
    else:
        print(f"❌ Failed: {response3.status_code}")

    print(f"\n{'='*80}")
    print("SUMMARY:")
    print(f"  Request 1 (fresh):   {time1:.2f}s")
    print(f"  Request 2 (cached):  {time2:.2f}s")
    print(f"  Request 3 (bypass):  {time3:.2f}s")
    print(f"\n✅ Cache working if: Request 2 much faster than Request 1")
    print(f"✅ Bypass working if: Request 3 similar time to Request 1")
    print(f"{'='*80}")

if __name__ == "__main__":
    test_bypass_cache()
