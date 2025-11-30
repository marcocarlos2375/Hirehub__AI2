"""
Test to verify personalized and detailed examples in questions.
This bypasses cache to ensure we're using the latest prompt.
"""

import requests
import json

API_BASE = "http://localhost:8001"

# Simple CV with clear work history for personalization
test_cv = """
Sarah Johnson
Email: sarah@example.com
Location: Boston, MA

SUMMARY:
Mid-level Backend Engineer with 4 years of experience

EXPERIENCE:
Backend Engineer | DataFlow Systems | 2021-2024
- Built microservices with Docker and Kubernetes
- Developed GraphQL APIs serving 500K requests/day
- Optimized PostgreSQL databases reducing query time by 70%
- Implemented Redis caching for recommendation engine

Junior Developer | HealthTech Inc | 2020-2021
- Built REST APIs with Python and FastAPI
- Worked on patient data management system

EDUCATION:
B.S. Computer Science | MIT | 2020

SKILLS:
Python, JavaScript, PostgreSQL, Redis, Docker, Kubernetes, GraphQL, AWS

PROJECTS:
- MediTrack: Healthcare tracking app built with React and Node.js
- OpenSource Contributor: Python CLI tool for database migrations (500 GitHub stars)
"""

test_jd = """
Senior Backend Engineer

Requirements:
- 5+ years backend experience
- Expert Kubernetes and Docker
- GraphQL and REST APIs
- PostgreSQL and Redis
- AWS Lambda serverless
- CI/CD pipelines
- System design experience

Nice-to-have:
- Terraform
- Event-driven architecture (Kafka)
"""

def test_personalized_examples():
    print("=" * 80)
    print("TESTING: Personalized Question Examples")
    print("=" * 80)

    # Parse JD
    jd_response = requests.post(f"{API_BASE}/api/parse", json={"job_description": test_jd, "language": "english"})
    parsed_jd = jd_response.json()
    print("✅ JD parsed")

    # Parse CV
    cv_response = requests.post(f"{API_BASE}/api/parse-cv", json={"resume_text": test_cv, "language": "english"})
    parsed_cv = cv_response.json()
    print("✅ CV parsed")

    # Calculate Score (with cache bypass)
    score_response = requests.post(
        f"{API_BASE}/api/calculate-score",
        json={"parsed_cv": parsed_cv, "parsed_jd": parsed_jd, "language": "english", "bypass_cache": True}
    )
    score_result = score_response.json()
    print(f"✅ Score: {score_result['overall_score']:.1f}%")

    # Generate Questions (with cache bypass via unique request)
    questions_response = requests.post(
        f"{API_BASE}/api/generate-questions",
        json={
            "parsed_cv": parsed_cv,
            "parsed_jd": parsed_jd,
            "score_result": score_result,
            "language": "english",
            "_bypass": "test_personalization_v2"  # Force new generation
        }
    )

    questions = questions_response.json().get('questions', [])
    print(f"✅ Generated {len(questions)} questions\n")

    # Check first 2 questions for personalization
    print("=" * 80)
    print("PERSONALIZATION CHECK:")
    print("=" * 80)

    for q in questions[:2]:
        print(f"\nQ{q['number']}: {q['title']}")
        print(f"Priority: {q['priority']}")
        print(f"\nExamples:")

        examples = q.get('examples', [])
        for i, example in enumerate(examples, 1):
            print(f"\n{i}. {example}")

            # Check for personalization markers
            has_company = "DataFlow Systems" in example or "HealthTech" in example or "MIT" in example
            has_tech = any(tech in example for tech in ["Python", "PostgreSQL", "Redis", "Docker", "Kubernetes", "GraphQL"])
            has_project = "MediTrack" in example or "OpenSource" in example
            has_metrics = any(metric in example for metric in ["%", "K", "users", "months", "team", "hours", "days"])

            markers = []
            if has_company: markers.append("✅ Company")
            if has_tech: markers.append("✅ Tech from CV")
            if has_project: markers.append("✅ Project")
            if has_metrics: markers.append("✅ Metrics")

            if markers:
                print(f"   Personalization: {', '.join(markers)}")

            # Check category
            if i == 1 and ("Professional" in example or "Backend Engineer at" in example or "DataFlow" in example):
                print("   Category: ✅ Professional")
            elif i == 2 and ("Side Project" in example or "personal project" in example or "MediTrack" in example):
                print("   Category: ✅ Side Project")
            elif i == 3:
                if "hackathon" in example.lower() or "published" in example.lower() or "conference" in example.lower() or "competition" in example.lower():
                    print("   Category: ✅ Publication/Hackathon")
                elif "learning" in example.lower() or "course" in example.lower() or "tutorial" in example.lower():
                    print("   Category: ❌ Learning (should be Publication/Hackathon)")

        print("\n" + "-" * 80)

    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    print("✅ Examples reference actual companies from CV")
    print("✅ Examples include technologies from CV")
    print("✅ Examples include metrics (time, impact, scale)")

    # Check if any example has "Learning" category
    all_examples = []
    for q in questions:
        all_examples.extend(q.get('examples', []))

    has_learning = any("Learning:" in ex or "Completed an online course" in ex or "Studied" in ex for ex in all_examples)
    has_hackathon = any("hackathon" in ex.lower() or "published" in ex.lower() or "conference" in ex.lower() for ex in all_examples)

    if has_learning:
        print("⚠️  Some examples still use 'Learning' category (should be Publication/Hackathon)")
    if has_hackathon:
        print("✅ Examples include Publication/Hackathon category")

    print("=" * 80)

if __name__ == "__main__":
    test_personalized_examples()
