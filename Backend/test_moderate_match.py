"""
Test script with a moderate match (60-70% score) to verify LOW priority questions
are generated for nice-to-have gaps.
"""

import requests
import json

# API endpoint
API_BASE = "http://localhost:8001"

# Test CV - Mid-level developer with good foundation
test_cv = """
Sarah Johnson
Email: sarah@example.com
Phone: (555) 123-4567
Location: Boston, MA

SUMMARY:
Mid-level Backend Engineer with 4 years of experience building scalable microservices.

EXPERIENCE:
Backend Engineer | TechCorp | 2021-2024 (3 years)
- Built microservices architecture using Docker and Kubernetes
- Developed GraphQL and REST APIs serving 500K requests/day
- Implemented PostgreSQL optimization strategies (query indexing, materialized views)
- Set up CI/CD pipelines with GitHub Actions
- Built Redis caching layer reducing latency by 60%
- Worked with AWS Lambda for serverless functions
- Collaborated with team of 8 engineers using Agile methodology

Junior Developer | StartupCo | 2020-2021 (1 year)
- Developed backend services with Node.js and Express
- Implemented authentication and authorization systems
- Worked with MongoDB and PostgreSQL databases

EDUCATION:
B.S. Computer Science | Tech University | 2020
- Relevant coursework: Distributed Systems, Database Design, Algorithms

SKILLS:
- Languages: JavaScript, Python, TypeScript, Go (basic)
- Backend: Node.js, Express, FastAPI
- Containerization: Docker, Kubernetes
- Databases: PostgreSQL, MongoDB, Redis
- Cloud: AWS (EC2, Lambda, S3, RDS)
- CI/CD: GitHub Actions, Jenkins
- API: GraphQL, REST
- Tools: Git, npm, Docker Compose
- Soft Skills: Problem-solving, Team collaboration, Communication

PROJECTS:
- Built event-driven notification system handling 100K events/day
- Optimized database queries reducing response time from 3s to 300ms
"""

# Test JD - Senior role but candidate has most requirements
test_jd = """
Senior Backend Engineer

Location: Boston, MA (Hybrid - 3 days onsite)
Start Date: Flexible (within 1 month)
Work Authorization: US citizens or valid work visa holders

About the Role:
We're seeking a Senior Backend Engineer to join our platform team.

Requirements:
- 4+ years backend development experience (REQUIRED)
- Strong Kubernetes and Docker experience (REQUIRED)
- Production GraphQL API development
- PostgreSQL database optimization
- Redis caching strategies
- AWS serverless architecture (Lambda)
- CI/CD pipeline management
- System design experience
- Strong problem-solving and communication skills
- Experience with high-traffic systems (500K+ requests/day)

Nice-to-have:
- Terraform or infrastructure as code experience
- Event-driven architecture (Kafka, RabbitMQ, SNS/SQS)
- Rust or Go advanced programming
- Experience with monitoring tools (Datadog, New Relic)
- GraphQL federation experience

The ideal candidate will have experience in SaaS or cloud platforms.
"""

def test_moderate_match():
    """Test with a moderate match to ensure LOW questions are generated"""

    print("=" * 80)
    print("TESTING: Moderate Match - LOW Priority Questions")
    print("=" * 80)

    # Step 1: Parse JD
    print("\n[1/4] Parsing Job Description...")
    jd_response = requests.post(
        f"{API_BASE}/api/parse",
        json={"job_description": test_jd, "language": "english"}
    )

    if jd_response.status_code != 200:
        print(f"❌ JD Parsing failed: {jd_response.text}")
        return

    parsed_jd = jd_response.json()
    print(f"✅ JD parsed successfully")

    # Step 2: Parse CV
    print("\n[2/4] Parsing CV...")
    cv_response = requests.post(
        f"{API_BASE}/api/parse-cv",
        json={"resume_text": test_cv, "language": "english"}
    )

    if cv_response.status_code != 200:
        print(f"❌ CV Parsing failed: {cv_response.text}")
        return

    parsed_cv = cv_response.json()
    print(f"✅ CV parsed successfully")

    # Step 3: Calculate Score
    print("\n[3/4] Calculating Compatibility Score...")
    score_response = requests.post(
        f"{API_BASE}/api/calculate-score",
        json={
            "parsed_cv": parsed_cv,
            "parsed_jd": parsed_jd,
            "language": "english"
        }
    )

    if score_response.status_code != 200:
        print(f"❌ Score calculation failed: {score_response.text}")
        return

    score_result = score_response.json()
    print(f"✅ Score calculated: {score_result['overall_score']:.1f}%")

    # Analyze gaps
    gaps = score_result.get('gaps', {})
    print(f"\n   Gap Analysis:")
    print(f"   - Critical gaps: {len(gaps.get('critical', []))}")
    print(f"   - Important gaps: {len(gaps.get('important', []))}")
    print(f"   - Nice-to-have gaps: {len(gaps.get('nice_to_have', []))}")
    print(f"   - Logistical gaps: {len(gaps.get('logistical', []))}")

    # Step 4: Generate Questions
    print("\n[4/4] Generating Questions...")
    questions_response = requests.post(
        f"{API_BASE}/api/generate-questions",
        json={
            "parsed_cv": parsed_cv,
            "parsed_jd": parsed_jd,
            "score_result": score_result,
            "language": "english"
        }
    )

    if questions_response.status_code != 200:
        print(f"❌ Question generation failed: {questions_response.text}")
        return

    questions_result = questions_response.json()
    questions = questions_result.get('questions', [])
    print(f"✅ Generated {len(questions)} questions")

    # Analyze question priorities
    print(f"\n{'=' * 80}")
    print("QUESTION PRIORITY BREAKDOWN:")
    print(f"{'=' * 80}")

    priority_counts = {}
    for q in questions:
        priority = q.get('priority', 'UNKNOWN')
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    print(f"\nQuestion Count by Priority:")
    for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'LOGISTICAL']:
        count = priority_counts.get(priority, 0)
        status = "✅" if count > 0 else "❌"
        print(f"  {status} {priority}: {count} questions")

    # Print LOW and LOGISTICAL questions
    print(f"\n{'=' * 80}")
    print("LOW PRIORITY QUESTIONS (Nice-to-have gaps):")
    print(f"{'=' * 80}")

    low_questions = [q for q in questions if q.get('priority') == 'LOW']
    if low_questions:
        for q in low_questions:
            print(f"\n  Q{q.get('number', '?')}: {q.get('title', 'Untitled')}")
            print(f"  Question: {q.get('question_text', 'N/A')[:150]}...")
    else:
        print("\n  No LOW priority questions generated")

    print(f"\n{'=' * 80}")
    print("LOGISTICAL QUESTIONS:")
    print(f"{'=' * 80}")

    logistical_questions = [q for q in questions if q.get('priority') == 'LOGISTICAL']
    if logistical_questions:
        for q in logistical_questions:
            print(f"\n  Q{q.get('number', '?')}: {q.get('title', 'Untitled')}")
            print(f"  Question: {q.get('question_text', 'N/A')}")
    else:
        print("\n  No LOGISTICAL questions generated")

    # Final verification
    print(f"\n{'=' * 80}")
    print("VERIFICATION RESULTS:")
    print(f"{'=' * 80}")

    has_low = priority_counts.get('LOW', 0) > 0
    has_logistical = priority_counts.get('LOGISTICAL', 0) > 0

    print(f"\n{'✅' if has_low else '❌'} Nice-to-have gaps generate LOW questions")
    print(f"{'✅' if has_logistical else '❌'} Logistical gaps generate LOGISTICAL questions")

    if has_low and has_logistical:
        print(f"\n{'=' * 80}")
        print("🎉 SUCCESS: All gap types generate appropriate questions!")
        print(f"{'=' * 80}")
    else:
        print(f"\n{'=' * 80}")
        print("⚠️  Some gap types still missing questions")
        print(f"{'=' * 80}")

if __name__ == "__main__":
    test_moderate_match()
