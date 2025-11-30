"""
Test with an almost perfect match (>70%) to verify ALL nice-to-have gaps generate questions.
"""

import requests
import json

API_BASE = "http://localhost:8001"

# Simple CV and JD that will score high
test_cv = """
Sarah Johnson
Backend Engineer with 5 years experience

EXPERIENCE:
Senior Backend Engineer | TechCorp | 2019-2024 (5 years)
- Built microservices with Kubernetes and Docker
- Developed GraphQL APIs
- Optimized PostgreSQL databases
- Implemented Redis caching
- AWS Lambda serverless functions
- CI/CD with GitHub Actions
- Led team of 3 engineers
- System design and architecture

SKILLS:
Python, JavaScript, Node.js, Kubernetes, Docker, PostgreSQL, Redis, AWS Lambda, GraphQL, GitHub Actions

LOCATION: Boston, MA
"""

test_jd = """
Senior Backend Engineer
Location: Boston, MA (Hybrid)

Requirements:
- 5 years backend experience
- Kubernetes and Docker
- GraphQL APIs
- PostgreSQL
- Redis caching
- AWS Lambda
- CI/CD pipelines
- Leadership skills

Nice-to-have:
- Terraform
- Kafka
- Rust
- Go
"""

def test_perfect_match():
    print("=" * 80)
    print("TESTING: High Score - All Nice-to-Have Gaps")
    print("=" * 80)

    # Parse JD
    jd_response = requests.post(f"{API_BASE}/api/parse", json={"job_description": test_jd, "language": "english"})
    parsed_jd = jd_response.json()
    print("✅ JD parsed")

    # Parse CV
    cv_response = requests.post(f"{API_BASE}/api/parse-cv", json={"resume_text": test_cv, "language": "english"})
    parsed_cv = cv_response.json()
    print("✅ CV parsed")

    # Calculate Score
    score_response = requests.post(f"{API_BASE}/api/calculate-score", json={"parsed_cv": parsed_cv, "parsed_jd": parsed_jd, "language": "english"})
    score_result = score_response.json()
    score = score_result['overall_score']
    print(f"✅ Score: {score:.1f}%")

    # Check gaps
    gaps = score_result.get('gaps', {})
    nice_to_have = gaps.get('nice_to_have', [])
    print(f"\n   Nice-to-have gaps: {len(nice_to_have)}")
    for gap in nice_to_have:
        print(f"     - {gap.get('title', 'Unknown')}")

    # Generate Questions
    questions_response = requests.post(
        f"{API_BASE}/api/generate-questions",
        json={"parsed_cv": parsed_cv, "parsed_jd": parsed_jd, "score_result": score_result, "language": "english"}
    )

    questions = questions_response.json().get('questions', [])
    print(f"\n✅ Generated {len(questions)} questions")

    # Count LOW priority
    low_questions = [q for q in questions if q.get('priority') == 'LOW']
    print(f"\n{'=' * 80}")
    print(f"LOW PRIORITY QUESTIONS: {len(low_questions)}")
    print(f"{'=' * 80}")

    for q in low_questions:
        print(f"\n  Q{q.get('number')}: {q.get('title')}")
        print(f"  {q.get('question_text', '')[:100]}...")

    # Verify
    print(f"\n{'=' * 80}")
    print("VERIFICATION:")
    print(f"{'=' * 80}")
    print(f"  Score: {score:.1f}%")
    print(f"  Nice-to-have gaps: {len(nice_to_have)}")
    print(f"  LOW questions: {len(low_questions)}")

    if score >= 70:
        if len(low_questions) == len(nice_to_have) and len(nice_to_have) > 0:
            print(f"\n  ✅ SUCCESS: {len(low_questions)} LOW questions for {len(nice_to_have)} nice-to-have gaps!")
        else:
            print(f"\n  ⚠️  Expected {len(nice_to_have)} but got {len(low_questions)}")
    else:
        if len(low_questions) >= 1:
            print(f"\n  ✅ At least 1 LOW question generated (score <70%)")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    test_perfect_match()
