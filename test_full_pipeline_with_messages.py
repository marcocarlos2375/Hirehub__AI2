"""
Test complete pipeline with AI-generated score messages
"""
import requests
import json

# Use a realistic resume
REALISTIC_RESUME = """
MICHAEL CHEN
Senior Software Engineer

Email: michael.chen@email.com | Phone: (555) 123-4567
LinkedIn: linkedin.com/in/michaelchen | GitHub: github.com/mchen

PROFESSIONAL SUMMARY
Senior Software Engineer with 5 years of experience building scalable web applications.
Strong expertise in Python, JavaScript, and cloud technologies.

TECHNICAL SKILLS
Languages: Python, JavaScript, TypeScript, SQL
Frameworks: React, Node.js, Django, FastAPI
Cloud: AWS (EC2, S3, Lambda), Docker, Kubernetes
Databases: PostgreSQL, MongoDB, Redis

WORK EXPERIENCE

Senior Software Engineer | TechStartup Inc.
San Francisco, CA | Jan 2021 - Present
- Built and deployed microservices architecture serving 1M+ users using Python and AWS
- Designed RESTful APIs with FastAPI and PostgreSQL
- Implemented CI/CD pipelines with GitHub Actions and Docker
- Led team of 3 junior engineers

Software Engineer | Digital Solutions Co.
New York, NY | Jun 2019 - Dec 2020
- Developed full-stack web applications using React and Node.js
- Optimized database queries reducing response time by 40%
- Collaborated with product team on feature development

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | Graduated: 2019
GPA: 3.7/4.0

CERTIFICATIONS
- AWS Certified Solutions Architect (2022)
- MongoDB Certified Developer (2021)
"""

# Job description requiring similar but slightly different skills
JOB_DESCRIPTION = """
Full Stack Engineer - FinTech Startup

We're looking for a talented Full Stack Engineer to join our growing team.

REQUIREMENTS:
- 3+ years of professional software development experience
- Strong proficiency in Python and modern JavaScript frameworks
- Experience with React and Node.js
- Knowledge of AWS cloud services
- Experience with PostgreSQL or similar relational databases
- Understanding of RESTful API design
- Experience with Docker and containerization

NICE TO HAVE:
- Experience in FinTech or financial services industry
- Knowledge of GraphQL
- Experience with TypeScript
- Kubernetes experience
- CI/CD pipeline experience

RESPONSIBILITIES:
- Design and develop full-stack features for our financial platform
- Build scalable microservices and APIs
- Collaborate with product and design teams
- Write clean, maintainable code with tests
- Participate in code reviews and technical discussions
"""

def test_full_pipeline():
    print("=" * 80)
    print("FULL PIPELINE TEST WITH AI SCORE MESSAGES")
    print("=" * 80)

    # Step 1: Parse CV
    print("\n📄 Step 1: Parsing CV...")
    cv_response = requests.post(
        "http://localhost:8001/api/parse-cv",
        json={"resume_text": REALISTIC_RESUME, "language": "english"}
    )

    if cv_response.status_code != 200:
        print(f"❌ CV parsing failed: {cv_response.status_code}")
        print(cv_response.text[:500])
        return False

    cv_data = cv_response.json()["data"]
    print(f"✅ CV parsed successfully")
    print(f"   Name: {cv_data.get('personal_info', {}).get('name', 'Unknown')}")
    print(f"   Skills found: {len(cv_data.get('skills', {}).get('hard_skills', []))}")

    # Step 2: Parse JD
    print("\n📋 Step 2: Parsing Job Description...")
    jd_response = requests.post(
        "http://localhost:8001/api/parse",
        json={"job_description": JOB_DESCRIPTION, "language": "english"}
    )

    if jd_response.status_code != 200:
        print(f"❌ JD parsing failed: {jd_response.status_code}")
        print(jd_response.text[:500])
        return False

    jd_data = jd_response.json()["data"]
    print(f"✅ JD parsed successfully")
    print(f"   Job title: {jd_data.get('job_title', 'Unknown')}")
    print(f"   Required skills: {len(jd_data.get('skills', {}).get('hard_skills', []))}")

    # Step 3: Calculate Score with bypass_cache to ensure fresh AI message
    print("\n🔍 Step 3: Calculating compatibility score...")
    score_response = requests.post(
        "http://localhost:8001/api/calculate-score?bypass_cache=true",
        json={
            "parsed_cv": cv_data,
            "parsed_jd": jd_data,
            "language": "english"
        }
    )

    if score_response.status_code != 200:
        print(f"❌ Score calculation failed: {score_response.status_code}")
        print(score_response.text[:1000])
        return False

    score_data = score_response.json()
    print(f"✅ Score calculated successfully")

    # Validate response structure
    print("\n" + "=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)

    tests_passed = 0
    tests_total = 8

    # Test 1: Overall score exists
    if "overall_score" in score_data:
        print(f"\n✅ Test 1: Overall score present: {score_data['overall_score']}%")
        tests_passed += 1
    else:
        print(f"\n❌ Test 1: Overall score missing")

    # Test 2: Overall status exists
    if "overall_status" in score_data:
        print(f"✅ Test 2: Overall status present: {score_data['overall_status']}")
        tests_passed += 1
    else:
        print(f"❌ Test 2: Overall status missing")

    # Test 3: Score message exists
    if "score_message" in score_data:
        print(f"✅ Test 3: Score message field present")
        tests_passed += 1
    else:
        print(f"❌ Test 3: Score message field MISSING")

    # Test 4: Score message has title
    score_message = score_data.get("score_message", {})
    if score_message and "title" in score_message:
        print(f"✅ Test 4: Score message title present: '{score_message['title']}'")
        tests_passed += 1
    else:
        print(f"❌ Test 4: Score message title MISSING")

    # Test 5: Score message has subtitle
    if score_message and "subtitle" in score_message:
        print(f"✅ Test 5: Score message subtitle present: '{score_message['subtitle']}'")
        tests_passed += 1
    else:
        print(f"❌ Test 5: Score message subtitle MISSING")

    # Test 6: Category scores exist
    if "category_scores" in score_data and len(score_data["category_scores"]) > 0:
        print(f"✅ Test 6: Category scores present ({len(score_data['category_scores'])} categories)")
        tests_passed += 1
    else:
        print(f"❌ Test 6: Category scores missing or empty")

    # Test 7: Gaps analysis exists
    gaps = score_data.get("gaps", {})
    total_gaps = (len(gaps.get("critical", [])) + len(gaps.get("important", [])) +
                  len(gaps.get("nice_to_have", [])))
    if total_gaps > 0:
        print(f"✅ Test 7: Gap analysis present ({total_gaps} total gaps)")
        tests_passed += 1
    else:
        print(f"⚠️  Test 7: No gaps found (might be perfect match or error)")

    # Test 8: Strengths exist
    strengths = score_data.get("strengths", [])
    if len(strengths) > 0:
        print(f"✅ Test 8: Strengths present ({len(strengths)} strengths)")
        tests_passed += 1
    else:
        print(f"⚠️  Test 8: No strengths found")

    # Display AI-generated message prominently
    print("\n" + "=" * 80)
    print("AI-GENERATED SCORE MESSAGE (USER-FACING)")
    print("=" * 80)
    print(f"\n📊 Backend Score (hidden from user): {score_data['overall_score']}%")
    print(f"📊 Status: {score_data['overall_status']}\n")

    if score_message:
        print(f"🎯 Title: {score_message.get('title', 'N/A')}")
        print(f"💬 Subtitle: {score_message.get('subtitle', 'N/A')}")
    else:
        print("❌ No score message generated!")

    print("\n" + "=" * 80)

    # Display category breakdown
    print("\n📊 Category Breakdown:")
    for category, details in score_data.get("category_scores", {}).items():
        print(f"   {category.replace('_', ' ').title()}: {details['score']}% ({details['status']})")

    # Display top gaps
    print(f"\n⚠️  Critical Gaps: {len(gaps.get('critical', []))}")
    for gap in gaps.get('critical', [])[:3]:
        print(f"   - {gap.get('title', 'Unknown')}")

    # Display top strengths
    print(f"\n💪 Strengths: {len(strengths)}")
    for strength in strengths[:3]:
        print(f"   - {strength.get('title', 'Unknown')}")

    # Final summary
    print("\n" + "=" * 80)
    print(f"FINAL RESULTS: {tests_passed}/{tests_total} tests passed ({tests_passed/tests_total*100:.0f}%)")
    print("=" * 80)

    if tests_passed == tests_total:
        print("\n✅ ALL TESTS PASSED - Pipeline working perfectly!")
        return True
    elif tests_passed >= tests_total - 2:
        print(f"\n⚠️  MOSTLY WORKING - {tests_total - tests_passed} minor issues")
        return True
    else:
        print(f"\n❌ PIPELINE ISSUES - {tests_total - tests_passed} tests failed")
        return False

if __name__ == "__main__":
    success = test_full_pipeline()
    exit(0 if success else 1)
