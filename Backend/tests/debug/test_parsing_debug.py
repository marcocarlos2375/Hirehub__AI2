"""
Debug script to test parsing endpoints directly and see raw responses.
"""

import requests
import json

API_BASE = "http://localhost:8000"

# Test JD parsing
jd_text = """Physician - Internal Medicine
City Hospital, New York, NY

We are seeking a board-certified physician specializing in Internal Medicine.

Requirements:
- MD degree from accredited medical school
- 5+ years clinical experience in Internal Medicine
- Board certification in Internal Medicine
- Strong patient communication skills
- Experience with EMR systems
- Bedside manner and empathy
- Emergency response capabilities
- Clinical decision-making expertise

Responsibilities:
- Diagnose and treat patients
- Manage patient care plans
- Collaborate with medical staff
- Maintain detailed medical records
- Provide compassionate patient care
"""

print("=" * 80)
print("Testing JD Parsing")
print("=" * 80)

try:
    response = requests.post(
        f"{API_BASE}/api/parse",
        json={"job_description": jd_text, "language": "english"},
        timeout=30
    )

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"\nSuccess: {result.get('success')}")
        print(f"Time: {result.get('time_seconds')}s")
        print(f"Model: {result.get('model')}")

        data = result.get('data', {})
        print(f"\n=== PARSED DATA ===")
        print(f"Position: {data.get('position_title', 'N/A')}")
        print(f"Company: {data.get('company_name', 'N/A')}")
        print(f"Location: {data.get('location', 'N/A')}")
        print(f"Hard Skills: {len(data.get('hard_skills_required', []))} items")
        print(f"Soft Skills: {len(data.get('soft_skills_required', []))} items")
        print(f"Responsibilities: {len(data.get('responsibilities', []))} items")

        # Print first 3 hard skills
        hard_skills = data.get('hard_skills_required', [])
        if hard_skills:
            print(f"\nFirst 3 Hard Skills:")
            for skill in hard_skills[:3]:
                print(f"  - {skill}")

        # Print full JSON (formatted)
        print(f"\n=== FULL JSON RESPONSE ===")
        print(json.dumps(data, indent=2)[:1000])  # First 1000 chars

    else:
        print(f"\nError: {response.text}")

except Exception as e:
    print(f"\nException: {e}")

print("\n" + "=" * 80)
