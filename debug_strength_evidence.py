"""
Debug what evidence is actually in the strengths
"""
import requests
import json

RESUME = """
MICHAEL CHEN
Senior Software Engineer

WORK EXPERIENCE
Senior Software Engineer | TechStartup Inc.
- Built microservices architecture serving 1M+ users using Python and AWS

PROJECTS
HealthTrack App Redesign
- Redesigned health tracking mobile app improving user retention by 25%
"""

JOB = "Full Stack Engineer - FinTech. Need Python, AWS, GraphQL, FinTech experience."

cv_resp = requests.post("http://localhost:8001/api/parse-cv",
                        json={"resume_text": RESUME, "language": "english"})
jd_resp = requests.post("http://localhost:8001/api/parse",
                        json={"job_description": JOB, "language": "english"})

score_resp = requests.post(
    "http://localhost:8001/api/calculate-score?bypass_cache=true",
    json={"parsed_cv": cv_resp.json()["data"], "parsed_jd": jd_resp.json()["data"]}
)

data = score_resp.json()

print("=" * 80)
print("STRENGTHS WITH EVIDENCE")
print("=" * 80)
for i, strength in enumerate(data.get("strengths", [])[:5], 1):
    print(f"\n{i}. {strength.get('title')}")
    print(f"   Description: {strength.get('description')[:100]}...")
    print(f"   Evidence: {strength.get('evidence')}")

print("\n" + "=" * 80)
print("CRITICAL GAPS")
print("=" * 80)
for i, gap in enumerate(data.get("gaps", {}).get("critical", [])[:5], 1):
    print(f"\n{i}. {gap.get('title')}")
    print(f"   Current: '{gap.get('current')}'")
    print(f"   Required: '{gap.get('required')}'")
    print(f"   Impact: {gap.get('impact')}")
