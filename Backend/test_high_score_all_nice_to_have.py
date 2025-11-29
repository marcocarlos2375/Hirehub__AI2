"""
Test script with a high score (>70%) to verify ALL nice-to-have gaps generate
LOW priority questions.
"""

import requests
import json

# API endpoint
API_BASE = "http://localhost:8001"

# Test CV - Senior developer with excellent match
test_cv = """
Michael Chen
Email: michael@example.com
Phone: (555) 987-6543
Location: Seattle, WA

SUMMARY:
Senior Backend Engineer with 6 years of experience building scalable microservices and distributed systems.

EXPERIENCE:
Senior Backend Engineer | CloudTech Corp | 2020-2024 (4 years)
- Architected and built microservices handling 2M+ requests/day
- Expert-level Kubernetes and Docker orchestration for 50+ services
- Developed GraphQL and REST APIs with 99.9% uptime
- Implemented advanced PostgreSQL optimization (query planning, partitioning, indexing)
- Built multi-layer Redis caching strategies reducing latency by 70%
- Designed and deployed AWS Lambda serverless functions
- Set up comprehensive CI/CD pipelines with GitHub Actions and Jenkins
- Led team of 4 engineers, conducted code reviews and mentoring
- Optimized database queries achieving sub-100ms response times
- Strong problem-solving and communication with cross-functional teams

Backend Engineer | StartupX | 2018-2020 (2 years)
- Built RESTful APIs with Node.js and Python FastAPI
- Worked with PostgreSQL, MongoDB, and Redis databases
- Deployed applications to AWS (EC2, Lambda, S3, RDS)
- Implemented authentication and authorization systems

EDUCATION:
M.S. Computer Science | University of Washington | 2018
B.S. Computer Science | State University | 2016

SKILLS:
- Languages: JavaScript, TypeScript, Python, Go
- Backend: Node.js, Express, FastAPI, Django
- Containerization: Docker, Kubernetes (CKA certified)
- Databases: PostgreSQL, MongoDB, Redis, DynamoDB
- Cloud: AWS (EC2, Lambda, S3, RDS, CloudFormation)
- CI/CD: GitHub Actions, Jenkins, CircleCI
- API: GraphQL, REST, gRPC
- Monitoring: DataDog, New Relic, CloudWatch
- Tools: Git, Docker Compose, Postman
- Soft Skills: Leadership, Mentoring, Problem-solving, Communication

PROJECTS:
- Built event-driven notification system with SQS/SNS handling 500K events/day
- Designed and implemented API gateway serving 100+ microservices
- Optimized database queries reducing response time from 5s to 80ms

CERTIFICATIONS:
- AWS Certified Solutions Architect
- Certified Kubernetes Administrator (CKA)
"""

# Test JD - Senior role that the candidate matches well
test_jd = """
Senior Backend Engineer

Location: Seattle, WA (Hybrid - 2 days onsite)
Start Date: Flexible
Work Authorization: US citizens or valid work visa holders

About the Role:
We're seeking a Senior Backend Engineer to join our platform team and help scale our infrastructure.

Requirements:
- 5+ years backend development experience (REQUIRED)
- Expert-level Kubernetes and Docker experience (REQUIRED)
- Production GraphQL API development
- PostgreSQL database optimization
- Redis caching strategies
- AWS serverless architecture (Lambda)
- CI/CD pipeline management
- System design and architecture experience
- Leadership and mentoring experience
- Strong problem-solving and communication skills
- Experience with high-traffic systems (1M+ requests/day)

Nice-to-have:
- Terraform infrastructure as code experience
- Event-driven architecture (Kafka, RabbitMQ, SQS/SNS)
- Rust programming experience
- Experience with monitoring tools (Datadog, New Relic)
- gRPC protocol experience
- Microservices architecture patterns

The ideal candidate will have experience in SaaS or cloud platforms.
"""

def test_high_score_all_nice_to_have():
    """Test with a high score to verify ALL nice-to-have gaps get questions"""

    print("=" * 80)
    print("TESTING: High Score - ALL Nice-to-Have Gaps Get Questions")
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
    score = score_result['overall_score']
    print(f"✅ Score calculated: {score:.1f}%")

    # Analyze gaps
    gaps = score_result.get('gaps', {})
    nice_to_have_gaps = gaps.get('nice_to_have', [])

    print(f"\n   Gap Analysis:")
    print(f"   - Critical gaps: {len(gaps.get('critical', []))}")
    print(f"   - Important gaps: {len(gaps.get('important', []))}")
    print(f"   - Nice-to-have gaps: {len(nice_to_have_gaps)}")
    print(f"   - Logistical gaps: {len(gaps.get('logistical', []))}")

    if nice_to_have_gaps:
        print(f"\n   NICE-TO-HAVE GAPS (Expected {len(nice_to_have_gaps)} LOW questions):")
        for i, gap in enumerate(nice_to_have_gaps, 1):
            print(f"     {i}. {gap.get('title', 'Unknown')}: {gap.get('impact', 'N/A')}")

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

    # Print LOW priority questions
    print(f"\n{'=' * 80}")
    print(f"LOW PRIORITY QUESTIONS (Nice-to-have gaps):")
    print(f"{'=' * 80}")

    low_questions = [q for q in questions if q.get('priority') == 'LOW']
    if low_questions:
        print(f"\nGenerated {len(low_questions)} LOW priority questions:")
        for q in low_questions:
            print(f"\n  Q{q.get('number', '?')}: {q.get('title', 'Untitled')}")
            print(f"  Question: {q.get('question_text', 'N/A')[:120]}...")
    else:
        print("\n  No LOW priority questions generated")

    # Final verification
    print(f"\n{'=' * 80}")
    print("VERIFICATION RESULTS:")
    print(f"{'=' * 80}")

    low_count = priority_counts.get('LOW', 0)
    expected_low = len(nice_to_have_gaps)

    print(f"\n  Score: {score:.1f}%")
    print(f"  Nice-to-have gaps: {expected_low}")
    print(f"  LOW priority questions generated: {low_count}")

    if score >= 70:
        if low_count == expected_low and expected_low > 0:
            print(f"\n  ✅ SUCCESS: Generated LOW question for EVERY nice-to-have gap!")
            print(f"     Expected {expected_low}, Got {low_count} - Perfect match!")
        elif low_count > 0 and low_count < expected_low:
            print(f"\n  ⚠️  PARTIAL: Generated {low_count} LOW questions but expected {expected_low}")
            print(f"     Missing {expected_low - low_count} questions")
        else:
            print(f"\n  ❌ FAILED: No LOW questions generated despite {expected_low} nice-to-have gaps")
    else:
        print(f"\n  ℹ️  Score <70% ({score:.1f}%), so minimum 1 LOW question is expected")
        if low_count >= 1:
            print(f"  ✅ SUCCESS: Generated {low_count} LOW questions (minimum 1 required)")
        else:
            print(f"  ❌ FAILED: No LOW questions generated")

    print(f"\n{'=' * 80}")

if __name__ == "__main__":
    test_high_score_all_nice_to_have()
