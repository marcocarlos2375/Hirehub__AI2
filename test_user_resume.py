"""
Quick test to verify the domain finder works with a fresh resume
"""
import requests
import json

# Simple test resume
TEST_RESUME = """
Alex Smith
Full-Stack Developer

Email: alex@email.com
Phone: (555) 999-8888

SUMMARY
Full-Stack Developer with 4 years of experience building web applications.

SKILLS
- JavaScript, TypeScript, Python
- React, Vue.js, Node.js
- PostgreSQL, MongoDB
- AWS, Docker

EXPERIENCE
Full-Stack Developer | WebCo
2020 - Present
- Built web applications with React and Node.js
- Managed PostgreSQL databases
- Deployed to AWS
"""

def test_domain_finder():
    print("Testing Domain Finder API (Fresh Resume)...")
    print("=" * 80)

    url = "http://localhost:8001/api/find-domains"

    payload = {
        "resume_text": TEST_RESUME,
        "language": "english"
    }

    try:
        response = requests.post(url, json=payload, timeout=60)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            print(f"⏱️  Time: {data.get('time_seconds')}s")
            print(f"📊 Domains: {data.get('total_suggested')}")

            if data.get('domains') and len(data['domains']) > 0:
                first = data['domains'][0]

                # Check for all required fields
                required = ['domain_name', 'technical_role', 'industry', 'role_skills_to_learn',
                           'industry_skills_to_learn', 'industry_rationale']

                missing = [f for f in required if f not in first]

                if missing:
                    print(f"\n❌ MISSING FIELDS: {', '.join(missing)}")
                    print("This means the old cached response is still being returned!")
                else:
                    print(f"\n✅ ALL REQUIRED FIELDS PRESENT!")
                    print(f"\nFirst domain: {first['domain_name']}")
                    print(f"  Role: {first['technical_role']}")
                    print(f"  Industry: {first['industry']}")
                    print(f"  Fit: {first['fit_score']}%")
        else:
            print(f"\n❌ Error: {response.status_code}")
            error_data = response.json()
            print(json.dumps(error_data, indent=2)[:500])

    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_domain_finder()
