"""
Debug script to see exactly what gets parsed from the JD.
"""

import requests
import json

API_BASE = "http://localhost:8000"

backend_engineer_jd = """Senior Backend Engineer | TechScale Solutions

Location: San Francisco, CA (hybrid)
Salary: $160,000 - $200,000
Experience Required: 5-8 years

About the Role:
We're building scalable cloud infrastructure for our rapidly growing SaaS platform. Join our backend team to design and implement high-performance APIs and microservices.

Requirements:
- 5-8 years of professional software development experience
- Strong expertise in Python and modern web frameworks (Flask, FastAPI - CRITICAL)
- Experience building RESTful APIs and microservices architecture
- Proficiency with cloud platforms, especially AWS (EC2, Lambda, RDS, S3)
- Strong knowledge of Docker and Kubernetes
- Experience with SQL and NoSQL databases (PostgreSQL, Redis, MongoDB)
- Understanding of CI/CD pipelines and DevOps practices
- Experience with caching strategies and performance optimization
- Agile/Scrum methodology experience
- Strong problem-solving and analytical skills

Tech Stack:
Python, FastAPI, Node.js, PostgreSQL, Redis, AWS, Docker, Kubernetes, Git, CI/CD

Responsibilities:
- Design and develop scalable REST APIs serving millions of requests
- Build and maintain microservices architecture
- Optimize database queries and API performance
- Implement caching layers and improve system reliability
- Lead code reviews and mentor junior developers
- Collaborate with frontend and product teams
- Deploy and monitor production services on AWS
- Participate in on-call rotation and incident response

What We Offer:
- Competitive salary and equity
- Flexible hybrid work environment
- Modern tech stack and clean codebase
- Strong engineering culture
- Career growth opportunities"""

print("Parsing JD...")
response = requests.post(
    f"{API_BASE}/api/parse",
    json={"job_description": backend_engineer_jd, "language": "english"},
    timeout=30
)

parsed_jd = response.json().get('data', {})

print("\n" + "=" * 80)
print("PARSED JD STRUCTURE")
print("=" * 80)
print(json.dumps(parsed_jd, indent=2))

print("\n" + "=" * 80)
print("KEY FIELDS FOR SCORING")
print("=" * 80)
print(f"\ndomain_expertise: {parsed_jd.get('domain_expertise', 'MISSING!')}")
print(f"\nresponsibilities ({len(parsed_jd.get('responsibilities', []))} items):")
for i, resp in enumerate(parsed_jd.get('responsibilities', [])[:3], 1):
    print(f"  {i}. {resp}")
print(f"\ncompany_name: {parsed_jd.get('company_name', 'N/A')}")
print(f"position_title: {parsed_jd.get('position_title', 'N/A')}")
print(f"company_type: {parsed_jd.get('company_type', 'N/A')}")
