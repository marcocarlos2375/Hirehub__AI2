"""
Test AI-generated SPECIFIC score messages with bypass_cache
"""
import requests
import json

# Realistic resume
RESUME = """
MICHAEL CHEN
Senior Software Engineer

Email: michael.chen@email.com
LinkedIn: linkedin.com/in/michaelchen

PROFESSIONAL SUMMARY
Senior Software Engineer with 5 years of experience building scalable web applications.

TECHNICAL SKILLS
Languages: Python, JavaScript, TypeScript
Frameworks: React, Django, FastAPI
Cloud: AWS (EC2, S3, Lambda), Docker

WORK EXPERIENCE

Senior Software Engineer | TechStartup Inc.
San Francisco, CA | Jan 2021 - Present
- Built microservices architecture serving 1M+ users using Python and AWS
- Designed RESTful APIs with FastAPI and PostgreSQL

Software Engineer | Digital Solutions Co.
New York, NY | Jun 2019 - Dec 2020
- Developed full-stack web applications using React and Node.js

PROJECTS
HealthTrack App Redesign (Personal Project)
- Redesigned health tracking mobile app improving user retention by 25%
"""

# Job requiring different skills
JOB = """
Full Stack Engineer - FinTech Startup

REQUIREMENTS:
- 3+ years of experience
- Python and JavaScript
- React and Node.js
- AWS cloud services
- PostgreSQL

NICE TO HAVE:
- FinTech industry experience
- GraphQL
- Kubernetes

We're building a financial platform for small businesses.
"""

print("=" * 80)
print("Testing SPECIFIC AI Messages (bypass_cache=true)")
print("=" * 80)

# Parse CV
cv_resp = requests.post("http://localhost:8001/api/parse-cv",
                        json={"resume_text": RESUME, "language": "english"})
cv_data = cv_resp.json()["data"]
print(f"\n✅ CV parsed: {cv_data.get('personal_info', {}).get('name')}")

# Parse JD
jd_resp = requests.post("http://localhost:8001/api/parse",
                        json={"job_description": JOB, "language": "english"})
jd_data = jd_resp.json()["data"]
print(f"✅ JD parsed")

# Calculate score WITH BYPASS to get fresh AI message
print(f"\n🔍 Calculating score with FRESH AI message generation...")
score_resp = requests.post(
    "http://localhost:8001/api/calculate-score?bypass_cache=true",
    json={"parsed_cv": cv_data, "parsed_jd": jd_data}
)

if score_resp.status_code != 200:
    print(f"❌ Error: {score_resp.status_code}")
    print(score_resp.text[:500])
    exit(1)

data = score_resp.json()

print("\n" + "=" * 80)
print("AI-GENERATED MESSAGE (Should be SPECIFIC)")
print("=" * 80)
print(f"\n📊 Score: {data['overall_score']}% ({data['overall_status']})")
print(f"\n🎯 Title: {data['score_message']['title']}")
print(f"💬 Subtitle: {data['score_message']['subtitle']}")

print("\n" + "=" * 80)
print("SPECIFICITY CHECK")
print("=" * 80)

message_text = (data['score_message']['title'] + " " + data['score_message']['subtitle']).lower()

# Check if it references specific things
checks = {
    "TechStartup mentioned": "techstartup" in message_text or "tech startup" in message_text,
    "Digital Solutions mentioned": "digital solutions" in message_text,
    "HealthTrack project mentioned": "healthtrack" in message_text or "health track" in message_text,
    "Microservices mentioned": "microservices" in message_text or "microservice" in message_text,
    "AWS mentioned": "aws" in message_text,
    "FinTech gap mentioned": "fintech" in message_text or "financial" in message_text,
    "GraphQL gap mentioned": "graphql" in message_text,
    "Kubernetes gap mentioned": "kubernetes" in message_text or "k8s" in message_text,
}

passed = sum(checks.values())
total = len(checks)

for check, result in checks.items():
    icon = "✅" if result else "❌"
    print(f"{icon} {check}")

print(f"\n📊 Specificity Score: {passed}/{total} ({passed/total*100:.0f}%)")

if passed >= 3:
    print("\n✅ Message is SPECIFIC enough!")
else:
    print("\n❌ Message is too GENERIC - needs more specific references")

print("\n" + "=" * 80)
