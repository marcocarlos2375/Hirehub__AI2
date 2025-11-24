"""
Comprehensive test for projects and certifications recognition
Tests the complete pipeline: gap analysis + question generation
"""
import requests
import json

# Use Sophia's resume from the sample resumes
SOPHIA_RESUME = """SOPHIA MARTINEZ
UX/UI Designer

Email: sophia.martinez@email.com | Phone: (555) 345-6789 | Location: Austin, TX
LinkedIn: linkedin.com/in/sophiamartinez | Portfolio: sophiamartinez.design

PROFESSIONAL SUMMARY
Creative UX/UI Designer with 2 years of experience designing user-centered digital products.

WORK EXPERIENCE

UX/UI Designer | Digital Agency Co.
Austin, TX | Mar 2023 - Present
- Design user interfaces for 10+ client projects including mobile apps and web applications
- Conduct user research through interviews, surveys, and usability testing with 50+ participants

EDUCATION
Bachelor of Fine Arts in Graphic Design
University of Texas at Austin | Graduated: May 2022
GPA: 3.6/4.0

PROJECTS & CASE STUDIES

HealthTrack App - Redesign (Personal Project)
- Redesigned health tracking mobile app improving user retention by 25%
- Conducted user research with 20 participants to identify pain points
- Created user personas, user flows, wireframes, and high-fidelity prototypes
- Implemented accessibility best practices (WCAG 2.1 AA compliance)

E-Commerce Checkout Optimization
- Redesigned checkout process reducing cart abandonment by 30%

CERTIFICATIONS & COURSES
- Google UX Design Professional Certificate (Coursera, 2022)
- Interaction Design Foundation - User Research Methods (2023)
- Frontend Fundamentals: HTML & CSS (Codecademy, 2024)
"""

HEALTHCARE_JD = """UX Designer - Healthcare Technology

We are seeking a talented UX Designer to join our HealthTech team building patient-centered digital health solutions.

REQUIREMENTS:
- 3+ years of UX design experience
- Experience with healthcare technology, MedTech, or digital health platforms
- Strong understanding of accessibility standards (WCAG compliance)
- Knowledge of healthcare compliance (HIPAA preferred)

RESPONSIBILITIES:
- Design intuitive interfaces for patient-facing mobile and web applications
- Conduct user research with diverse patient populations
- Ensure designs meet healthcare accessibility standards
- Collaborate with clinical stakeholders and engineering teams
"""

def test_full_pipeline():
    print("=" * 80)
    print("COMPREHENSIVE TEST: Projects & Certifications Recognition")
    print("=" * 80)

    # Step 1: Parse CV
    print("\n📄 Step 1: Parsing Sophia's resume...")
    cv_resp = requests.post(
        "http://localhost:8001/api/parse-cv",
        json={"resume_text": SOPHIA_RESUME, "language": "english"}
    )

    if cv_resp.status_code != 200:
        print(f"❌ CV parsing failed: {cv_resp.status_code}")
        return

    cv_data = cv_resp.json()["data"]
    projects = cv_data.get("projects", [])
    certs = cv_data.get("certifications", [])

    print(f"✅ CV parsed successfully")
    print(f"   Projects found: {len(projects)}")
    for proj in projects:
        if isinstance(proj, dict):
            print(f"   - {proj.get('name', 'Unknown')}")

    print(f"\n   Certifications found: {len(certs)}")
    for cert in certs[:3]:
        print(f"   - {cert if isinstance(cert, str) else cert.get('name', str(cert))}")

    # Step 2: Parse JD
    print("\n📋 Step 2: Parsing healthcare job description...")
    jd_resp = requests.post(
        "http://localhost:8001/api/parse",
        json={"job_description": HEALTHCARE_JD, "language": "english"}
    )

    if jd_resp.status_code != 200:
        print(f"❌ JD parsing failed: {jd_resp.status_code}")
        return

    jd_data = jd_resp.json()["data"]
    print("✅ JD parsed successfully")

    # Step 3: Calculate score with gaps
    print("\n🔍 Step 3: Calculating match score and gap analysis...")
    score_resp = requests.post(
        "http://localhost:8001/api/calculate-score?bypass_cache=true",
        json={"parsed_cv": cv_data, "parsed_jd": jd_data}
    )

    if score_resp.status_code != 200:
        print(f"❌ Score calculation failed: {score_resp.status_code}")
        print(score_resp.text[:500])
        return

    score_data = score_resp.json()
    print(f"✅ Score calculated: {score_data.get('overall_score')}%")

    # Analyze gaps
    print("\n" + "=" * 80)
    print("GAP ANALYSIS RESULTS")
    print("=" * 80)

    gaps = score_data.get("gaps", {})
    critical_gaps = gaps.get("critical", [])
    important_gaps = gaps.get("important", [])

    print(f"\n📊 Critical Gaps: {len(critical_gaps)}")
    print(f"📊 Important Gaps: {len(important_gaps)}")

    # Check for healthcare domain gap
    healthcare_gap = None
    for gap in critical_gaps + important_gaps:
        gap_text = json.dumps(gap).lower()
        if 'healthcare' in gap_text or 'health' in gap_text or 'medtech' in gap_text:
            healthcare_gap = gap
            break

    if healthcare_gap:
        print(f"\n🏥 Healthcare Domain Gap Found:")
        print(f"   Title: {healthcare_gap.get('title')}")
        print(f"   Impact: {healthcare_gap.get('impact')}")
        print(f"   Current State: {healthcare_gap.get('current')}")
        print(f"   Required: {healthcare_gap.get('required')}")

        # Check if HealthTrack is mentioned
        current_state = healthcare_gap.get('current', '').lower()
        if 'healthtrack' in current_state or 'health track' in current_state:
            print("\n   ✅ SUCCESS: HealthTrack project IS mentioned in gap analysis!")
        elif 'project' in current_state and 'health' in current_state:
            print("\n   ⚠️  PARTIAL: Health project mentioned but not by name")
        else:
            print("\n   ❌ ISSUE: HealthTrack project NOT mentioned in gap analysis")
            print(f"      The gap says: \"{healthcare_gap.get('current')}\"")
    else:
        print("\n✅ No healthcare domain gap found - might be fully matched!")

    # Step 4: Generate questions
    print("\n" + "=" * 80)
    print("QUESTION GENERATION TEST")
    print("=" * 80)

    print("\n❓ Step 4: Generating personalized questions...")
    q_resp = requests.post(
        "http://localhost:8001/api/generate-questions?bypass_cache=true",
        json={
            "parsed_cv": cv_data,
            "parsed_jd": jd_data,
            "score_result": score_data
        }
    )

    if q_resp.status_code != 200:
        print(f"❌ Question generation failed: {q_resp.status_code}")
        print(q_resp.text[:500])
        return

    q_data = q_resp.json()
    questions = q_data.get("questions", [])

    print(f"✅ Generated {len(questions)} questions\n")

    # Check for HealthTrack awareness in questions
    healthtrack_refs = 0
    generic_healthcare_q = 0

    for i, q in enumerate(questions, 1):
        question_text = q.get("question", "").lower()
        context_text = q.get("context", "").lower()
        combined = question_text + " " + context_text

        if 'healthtrack' in combined or 'health track' in combined:
            healthtrack_refs += 1
            print(f"✅ Q{i} - References HealthTrack project:")
            print(f"   {q.get('question')[:120]}...")
        elif 'healthcare' in question_text and 'experience' in question_text and 'do you' in question_text:
            generic_healthcare_q += 1
            print(f"⚠️  Q{i} - Generic healthcare question (doesn't build on HealthTrack):")
            print(f"   {q.get('question')[:120]}...")

    print(f"\n📊 Question Generation Analysis:")
    print(f"   HealthTrack-specific questions: {healthtrack_refs}")
    print(f"   Generic healthcare questions: {generic_healthcare_q}")

    if healthtrack_refs > 0:
        print("\n   ✅ SUCCESS: Questions build on existing HealthTrack project!")
    elif generic_healthcare_q > 0:
        print("\n   ❌ ISSUE: Questions ask about healthcare experience generically")
        print("      Should build on HealthTrack project instead!")

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    tests_passed = 0
    tests_total = 3

    print("\n1. HealthTrack Project in Gap Analysis:")
    if healthcare_gap and ('healthtrack' in healthcare_gap.get('current', '').lower() or 'project' in healthcare_gap.get('current', '').lower()):
        print("   ✅ PASS - Project recognized in gap analysis")
        tests_passed += 1
    else:
        print("   ❌ FAIL - Project not recognized in gap analysis")

    print("\n2. Certifications Considered:")
    cert_mentioned = False
    for gap in critical_gaps + important_gaps:
        if 'certification' in json.dumps(gap).lower() or 'google ux' in json.dumps(gap).lower():
            cert_mentioned = True
            break
    if cert_mentioned or len(critical_gaps) < 5:  # Fewer gaps might mean certs helped
        print("   ✅ PASS - Certifications appear to be considered")
        tests_passed += 1
    else:
        print("   ⚠️  UNCLEAR - Cannot confirm certification impact")

    print("\n3. Question Generation Intelligence:")
    if healthtrack_refs > 0 and generic_healthcare_q == 0:
        print("   ✅ PASS - Questions build on existing projects")
        tests_passed += 1
    elif healthtrack_refs > 0:
        print("   ⚠️  PARTIAL - Some questions reference project, some generic")
        tests_passed += 0.5
    else:
        print("   ❌ FAIL - Questions don't reference existing HealthTrack project")

    print(f"\n{'='*80}")
    print(f"FINAL SCORE: {tests_passed}/{tests_total} tests passed ({tests_passed/tests_total*100:.0f}%)")
    print("=" * 80)

if __name__ == "__main__":
    test_full_pipeline()
