"""
Debug why domain and industry are scoring 0% despite having data.
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

john_doe_cv = """John Doe
Email: john.doe@email.com | Phone: (555) 123-4567
Location: San Francisco, CA | LinkedIn: linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Senior Software Engineer with 8 years of experience building scalable systems and leading technical projects. Strong expertise in Python, JavaScript, cloud infrastructure, and microservices architecture.

TECHNICAL SKILLS
Languages: Python, JavaScript, SQL
Frameworks: React, Node.js, Flask, FastAPI
Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD, Git
Databases: PostgreSQL, Redis, MongoDB
Methodologies: Microservices, REST APIs, TDD, Agile

WORK EXPERIENCE

Senior Software Engineer | Tech Corp | 2020 - Present (4 years)
- Built scalable microservices handling 1M+ requests per day
- Led team of 5 engineers in cloud migration project from on-premise to AWS
- Reduced API latency by 60% through caching and optimization strategies
- Implemented CI/CD pipeline reducing deployment time by 80%
- Designed and developed REST APIs used by 50+ internal services

Software Engineer | StartupXYZ | 2016 - 2020 (4 years)
- Developed REST APIs using Python Flask for e-commerce platform
- Integrated payment processing system (Stripe) handling $2M+ monthly transactions
- Built automated testing framework improving code coverage from 40% to 85%
- Collaborated with frontend team on React-based admin dashboard

EDUCATION
B.S. Computer Science | University of Technology | 2016
GPA: 3.7/4.0

SOFT SKILLS
- Team collaboration and cross-functional communication
- Problem solving and analytical thinking
- Technical leadership and mentoring
- Adaptable to fast-paced environments"""

# Parse both
jd_resp = requests.post(f"{API_BASE}/api/parse", json={"job_description": backend_engineer_jd, "language": "english"}, timeout=30)
cv_resp = requests.post(f"{API_BASE}/api/parse-cv", json={"resume_text": john_doe_cv, "language": "english"}, timeout=30)

parsed_jd = jd_resp.json().get('data', {})
parsed_cv = cv_resp.json().get('data', {})

print("=" * 80)
print("DOMAIN EXPERTISE MATCHING DEBUG")
print("=" * 80)

# Check domain fields
jd_industries = parsed_jd.get('domain_expertise', {}).get('industry', [])
jd_knowledge = parsed_jd.get('domain_expertise', {}).get('specific_knowledge', [])

print(f"\nJD Domain:")
print(f"  Industries: {jd_industries}")
print(f"  Specific Knowledge: {jd_knowledge}")

cv_summary = parsed_cv.get('professional_summary', '')
cv_achievements = []
for exp in parsed_cv.get('work_experience', []):
    cv_achievements.extend(exp.get('achievements', []))

print(f"\nCV Content to Match Against:")
print(f"  Summary: {cv_summary[:150]}...")
print(f"  Achievements (first 2):")
for ach in cv_achievements[:2]:
    print(f"    - {ach}")

# Check matches
print(f"\nLooking for matches...")
for industry in jd_industries:
    found_in_summary = industry.lower() in cv_summary.lower()
    found_in_ach = any(industry.lower() in ach.lower() for ach in cv_achievements)
    print(f"  '{industry}': in summary={found_in_summary}, in achievements={found_in_ach}")

for knowledge in jd_knowledge:
    found_in_summary = knowledge.lower() in cv_summary.lower()
    found_in_ach = any(knowledge.lower() in ach.lower() for ach in cv_achievements)
    print(f"  '{knowledge}': in summary={found_in_summary}, in achievements={found_in_ach}")

print("\n" + "=" * 80)
print("INDUSTRY MATCHING DEBUG")
print("=" * 80)

print(f"\nJD Company: {parsed_jd.get('company_name', 'N/A')}")
print(f"JD Position: {parsed_jd.get('position_title', 'N/A')}")
print(f"JD Industry from domain: {jd_industries}")

print(f"\nCV Companies:")
for exp in parsed_cv.get('work_experience', []):
    company = exp.get('company', 'N/A')
    role = exp.get('role', 'N/A')
    print(f"  - {company} ({role})")
