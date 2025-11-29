"""
Test script to verify all gap types (critical, important, nice-to-have, logistical)
generate questions after implementing the fix.
"""

import requests
import json

# API endpoint
API_BASE = "http://localhost:8001"

# Test CV - Junior developer with some basic skills
test_cv = """
John Smith
Email: john@example.com
Phone: (555) 123-4567
Location: San Francisco, CA

SUMMARY:
Junior Full-stack Developer with 2 years of experience building web applications.

EXPERIENCE:
Software Developer | TechStartup Inc. | 2022-2024
- Built web applications using React and Node.js
- Implemented REST APIs with Express
- Worked with MongoDB databases
- Deployed applications to AWS EC2

Intern | WebDev Co. | 2021-2022
- Developed frontend features using HTML, CSS, JavaScript
- Fixed bugs and improved UI/UX

EDUCATION:
B.S. Computer Science | State University | 2021

SKILLS:
- Languages: JavaScript, Python (basic), HTML, CSS
- Frontend: React, Vue.js
- Backend: Node.js, Express
- Database: MongoDB
- Tools: Git, npm
"""

# Test JD - Senior role requiring advanced skills (will create gaps)
test_jd = """
Senior Backend Engineer

Location: New York, NY (Onsite required)
Start Date: Immediate (within 2 weeks)
Work Authorization: Must be authorized to work in US

About the Role:
We're seeking a Senior Backend Engineer to lead our microservices architecture.

Requirements:
- 5+ years backend development experience (REQUIRED)
- Expert-level Kubernetes and Docker experience (REQUIRED)
- Production experience with GraphQL APIs
- PostgreSQL database optimization
- Redis caching implementation
- AWS Lambda and serverless architecture
- CI/CD pipeline setup (Jenkins/GitHub Actions)
- System design and architecture experience
- Strong problem-solving and communication skills
- Experience with high-traffic systems (1M+ requests/day)

Nice-to-have:
- Terraform infrastructure as code
- Event-driven architecture (Kafka/RabbitMQ)
- Go or Rust programming

The ideal candidate will have healthcare or fintech domain experience.
"""

def test_complete_pipeline():
    """Test the complete pipeline: parse -> score -> questions"""

    print("=" * 80)
    print("TESTING: All Gap Types Generate Questions")
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

    # Print gap details
    for gap_type in ['critical', 'important', 'nice_to_have', 'logistical']:
        gap_list = gaps.get(gap_type, [])
        if gap_list:
            print(f"\n   {gap_type.upper()} GAPS:")
            for gap in gap_list[:3]:  # Show first 3
                print(f"     - {gap.get('title', 'Unknown')}: {gap.get('impact', gap.get('description', 'N/A'))}")

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
    print("QUESTION ANALYSIS:")
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

    # Print questions by priority
    print(f"\n{'=' * 80}")
    print("GENERATED QUESTIONS:")
    print(f"{'=' * 80}")

    for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'LOGISTICAL']:
        priority_questions = [q for q in questions if q.get('priority') == priority]
        if priority_questions:
            print(f"\n{priority} PRIORITY ({len(priority_questions)} questions):")
            for q in priority_questions:
                print(f"\n  Q{q.get('number', '?')}: {q.get('title', 'Untitled')}")
                print(f"  Priority: {q.get('priority', 'N/A')}")
                print(f"  Question: {q.get('question_text', 'N/A')[:100]}...")
                if q.get('context_why'):
                    print(f"  Why: {q.get('context_why', '')[:80]}...")

    # Final verification
    print(f"\n{'=' * 80}")
    print("VERIFICATION RESULTS:")
    print(f"{'=' * 80}")

    has_critical = priority_counts.get('CRITICAL', 0) > 0
    has_important = priority_counts.get('HIGH', 0) > 0 or priority_counts.get('MEDIUM', 0) > 0
    has_nice_to_have = priority_counts.get('LOW', 0) > 0
    has_logistical = priority_counts.get('LOGISTICAL', 0) > 0

    print(f"\n{'✅' if has_critical else '❌'} Critical gaps generate CRITICAL questions")
    print(f"{'✅' if has_important else '❌'} Important gaps generate HIGH/MEDIUM questions")
    print(f"{'✅' if has_nice_to_have else '❌'} Nice-to-have gaps generate LOW questions")
    print(f"{'✅' if has_logistical else '❌'} Logistical gaps generate LOGISTICAL questions")

    all_passed = has_critical and has_important and has_nice_to_have and has_logistical

    print(f"\n{'=' * 80}")
    if all_passed:
        print("🎉 SUCCESS: All gap types generate questions!")
    else:
        print("⚠️  PARTIAL SUCCESS: Some gap types are missing questions")
        if not has_nice_to_have:
            print("   ⚠️  Missing LOW priority questions for nice-to-have gaps")
        if not has_logistical:
            print("   ⚠️  Missing LOGISTICAL questions for logistical gaps")
    print(f"{'=' * 80}")

    # Save results to file
    with open('/Users/carlosid/PycharmProjects/test/Backend/test_results_all_gaps.json', 'w') as f:
        json.dump({
            'score_result': score_result,
            'questions_result': questions_result,
            'priority_counts': priority_counts
        }, f, indent=2)

    print(f"\n📄 Full results saved to: Backend/test_results_all_gaps.json")

if __name__ == "__main__":
    test_complete_pipeline()
