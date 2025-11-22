"""
Complete end-to-end pipeline test: JD parsing → CV parsing → Scoring → Questions → Answers
Tests all 5 phases with software developer vs doctor scenario (low score ~16%)
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

# Test data
doctor_jd_text = """
Physician - Internal Medicine
City Hospital, New York, NY

We are seeking a board-certified physician specializing in Internal Medicine.

Requirements:
- MD degree from accredited medical school
- 5+ years clinical experience in Internal Medicine
- Board certification in Internal Medicine
- Strong patient communication skills
- Experience with EMR systems
- Bedside manner and empathy
- Emergency response capabilities
- Clinical decision-making expertise

Responsibilities:
- Diagnose and treat patients
- Manage patient care plans
- Collaborate with medical staff
- Maintain detailed medical records
- Provide compassionate patient care
"""

software_dev_cv_text = """
John Developer
john@example.com | San Francisco, CA

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years specializing in full-stack web development.
Expert in Python, React, and cloud technologies.

TECHNICAL SKILLS
- Languages: Python, JavaScript, TypeScript
- Frontend: React, Next.js, Vue.js
- Backend: Node.js, FastAPI, Django
- Cloud: AWS, Docker, Kubernetes
- Databases: PostgreSQL, MongoDB, Redis
- Tools: Git, CI/CD, Agile

SOFT SKILLS
- Agile methodology
- Code review
- API design
- Testing and QA
- Team collaboration

WORK EXPERIENCE
Senior Software Engineer | Tech Corp Software Solutions | 2021-Present (3 years)
- Built scalable web applications serving 1M+ users
- Improved system performance by 40%
- Led team of 5 developers
- Implemented microservices architecture

Software Developer | Digital Innovations | 2019-2021 (2 years)
- Developed RESTful APIs and GraphQL endpoints
- Implemented CI/CD pipelines
- Reduced deployment time by 60%

EDUCATION
BS Computer Science | Stanford University | 2019

PROJECTS
- E-commerce Platform (React + Node.js)
- Data Analytics Dashboard (Python + PostgreSQL)
- Mobile App (React Native)

CERTIFICATIONS
- AWS Certified Solutions Architect
- AWS Certified Developer
"""

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def test_phase1_jd_parsing():
    """Phase 1: Parse job description"""
    print_section("PHASE 1: JD PARSING")

    try:
        response = requests.post(
            f"{API_BASE}/api/parse",
            json={"job_description": doctor_jd_text},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})  # Extract data from wrapper
            print(f"✅ JD Parsed Successfully")
            print(f"   Position: {data.get('position_title', 'N/A')}")
            print(f"   Company: {data.get('company_name', 'N/A')}")
            print(f"   Required Skills: {len(data.get('hard_skills_required', []))} skills")
            print(f"   Parsing Time: {result.get('time_seconds', 0):.2f}s")
            return data  # Return the actual data, not the wrapper
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_phase2_cv_parsing():
    """Phase 2: Parse CV"""
    print_section("PHASE 2: CV PARSING")

    try:
        response = requests.post(
            f"{API_BASE}/api/parse-cv",
            json={"resume_text": software_dev_cv_text},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})  # Extract data from wrapper
            print(f"✅ CV Parsed Successfully")
            print(f"   Name: {data.get('personal_info', {}).get('name', 'N/A')}")
            print(f"   Technical Skills: {len(data.get('technical_skills', []))} skills")
            print(f"   Work Experience: {len(data.get('work_experience', []))} positions")
            print(f"   Projects: {len(data.get('projects', []))} projects")
            print(f"   Parsing Time: {result.get('time_seconds', 0):.2f}s")
            return data  # Return the actual data, not the wrapper
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_phase3_scoring(parsed_cv, parsed_jd):
    """Phase 3: Calculate compatibility score"""
    print_section("PHASE 3: COMPATIBILITY SCORING")

    try:
        response = requests.post(
            f"{API_BASE}/api/calculate-score",
            json={"parsed_cv": parsed_cv, "parsed_jd": parsed_jd},
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            overall_score = result.get('overall_score', 0)

            print(f"✅ Score Calculated Successfully")
            print(f"\n📊 OVERALL SCORE: {overall_score}%")
            print(f"   Status: {result.get('overall_status', 'N/A')}")
            print(f"   Calculation Time: {result.get('time_seconds', 0):.2f}s\n")

            print("📈 8-Category Breakdown:")
            print("-" * 80)
            categories = result.get('category_scores', {})
            for category, details in categories.items():
                score = details.get('score', 0)
                weight = details.get('weight', 0) * 100
                weighted = score * details.get('weight', 0)
                print(f"  {category.replace('_', ' ').title():25} {score:3}% (weight: {weight:4.1f}%) → {weighted:5.1f} pts")
            print("-" * 80)

            # Check gaps
            gaps = result.get('gaps', {})
            critical_count = len(gaps.get('critical', []))
            important_count = len(gaps.get('important', []))
            nice_count = len(gaps.get('nice_to_have', []))

            print(f"\n🔍 Gap Analysis:")
            print(f"   CRITICAL gaps: {critical_count}")
            print(f"   IMPORTANT gaps: {important_count}")
            print(f"   NICE-TO-HAVE gaps: {nice_count}")
            print(f"   Total gaps: {critical_count + important_count + nice_count}")

            # Verify adaptive gap count for low scores
            if overall_score < 30:
                if critical_count >= 15:
                    print(f"   ✅ Adaptive gap analysis working (expected 15-25 for <30% score)")
                else:
                    print(f"   ⚠️  Gap count lower than expected (expected 15-25 for <30% score)")

            return result
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_phase4_questions(parsed_cv, parsed_jd, score_result):
    """Phase 4: Generate smart questions"""
    print_section("PHASE 4: SMART QUESTION GENERATION")

    try:
        response = requests.post(
            f"{API_BASE}/api/generate-questions",
            json={
                "parsed_cv": parsed_cv,
                "parsed_jd": parsed_jd,
                "score_result": score_result,
                "language": "english"
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            total_questions = result.get('total_questions', 0)
            critical_count = result.get('critical_count', 0)
            high_count = result.get('high_count', 0)
            medium_count = result.get('medium_count', 0)

            print(f"✅ Questions Generated Successfully")
            print(f"\n📋 QUESTION SUMMARY:")
            print(f"   Total Questions: {total_questions}")
            print(f"   CRITICAL: {critical_count}")
            print(f"   HIGH: {high_count}")
            print(f"   MEDIUM: {medium_count}")
            print(f"   RAG Context Used: {result.get('rag_context_used', False)}")
            print(f"   Generation Time: {result.get('time_seconds', 0):.2f}s")

            # Verify adaptive question count for low scores
            overall_score = score_result.get('overall_score', 0)
            if overall_score < 30:
                if total_questions >= 9:
                    print(f"   ✅ Adaptive question count working (expected 9-11 for <30% score)")
                else:
                    print(f"   ⚠️  Question count lower than expected (expected 9-11 for <30% score)")

            # Show first 2 questions
            questions = result.get('questions', [])
            if questions:
                print(f"\n📝 Sample Questions:")
                for i, q in enumerate(questions[:2], 1):
                    print(f"\n   Question {i} [{q.get('priority', 'N/A')}]: {q.get('title', 'N/A')}")
                    print(f"   Impact: {q.get('impact', 'N/A')}")
                    print(f"   Question: {q.get('question_text', 'N/A')[:150]}...")

            return result
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_phase5_answers(parsed_cv, parsed_jd, questions_result):
    """Phase 5: Submit answers and get updated score"""
    print_section("PHASE 5: ANSWER SUBMISSION & SCORE UPDATE")

    questions = questions_result.get('questions', [])
    if not questions:
        print("❌ No questions available")
        return None

    # Create sample answers for first 2 questions
    answers = []
    for q in questions[:2]:
        answers.append({
            "question_id": q.get('id'),
            "answer_text": f"Yes, I have some experience with {q.get('title')}. I worked on a personal project where I explored this area during my free time.",
            "answer_type": "text"
        })

    print(f"Submitting {len(answers)} sample answers...")

    try:
        response = requests.post(
            f"{API_BASE}/api/submit-answers",
            json={
                "parsed_cv": parsed_cv,
                "parsed_jd": parsed_jd,
                "questions": questions,
                "answers": answers,
                "original_score": 16,
                "language": "english"
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()

            print(f"✅ Answers Submitted Successfully")
            print(f"\n📊 UPDATED SCORE: {result.get('updated_score', 0)}%")
            print(f"   Original Score: {result.get('original_score', 0)}%")
            print(f"   Improvement: +{result.get('score_improvement', 0)}")
            print(f"   Processing Time: {result.get('time_seconds', 0):.2f}s")

            # Show uncovered experiences
            uncovered = result.get('uncovered_experiences', [])
            if uncovered:
                print(f"\n💎 Uncovered Experiences ({len(uncovered)}):")
                for exp in uncovered:
                    print(f"   - {exp}")
            else:
                print(f"\n   No new experiences uncovered from sample answers")

            return result
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Run complete end-to-end pipeline test"""
    print("\n" + "🚀" * 40)
    print("  COMPLETE PIPELINE TEST: Software Developer vs Doctor Position")
    print("  Expected Score: ~16% (massive mismatch)")
    print("  Expected Gaps: 15-25 CRITICAL gaps")
    print("  Expected Questions: 9-11 questions")
    print("🚀" * 40)

    start_time = time.time()

    # Phase 1: Parse JD
    parsed_jd = test_phase1_jd_parsing()
    if not parsed_jd:
        print("\n❌ Pipeline failed at Phase 1")
        return

    # Phase 2: Parse CV
    parsed_cv = test_phase2_cv_parsing()
    if not parsed_cv:
        print("\n❌ Pipeline failed at Phase 2")
        return

    # Phase 3: Calculate Score
    score_result = test_phase3_scoring(parsed_cv, parsed_jd)
    if not score_result:
        print("\n❌ Pipeline failed at Phase 3")
        return

    # Phase 4: Generate Questions
    questions_result = test_phase4_questions(parsed_cv, parsed_jd, score_result)
    if not questions_result:
        print("\n❌ Pipeline failed at Phase 4")
        return

    # Phase 5: Submit Answers
    answers_result = test_phase5_answers(parsed_cv, parsed_jd, questions_result)
    if not answers_result:
        print("\n❌ Pipeline failed at Phase 5")
        return

    total_time = time.time() - start_time

    # Final Summary
    print_section("PIPELINE TEST SUMMARY")
    print(f"✅ All 5 phases completed successfully!")
    print(f"⏱️  Total Pipeline Time: {total_time:.2f}s\n")

    print("Phase Breakdown:")
    print(f"  1. JD Parsing:       {parsed_jd.get('time_seconds', 0):.2f}s")
    print(f"  2. CV Parsing:       {parsed_cv.get('time_seconds', 0):.2f}s")
    print(f"  3. Scoring:          {score_result.get('time_seconds', 0):.2f}s")
    print(f"  4. Questions:        {questions_result.get('time_seconds', 0):.2f}s")
    print(f"  5. Answer Analysis:  {answers_result.get('time_seconds', 0):.2f}s")

    print("\nKey Metrics:")
    print(f"  - Final Score: {score_result.get('overall_score', 0)}%")
    print(f"  - Total Gaps: {len(score_result.get('gaps', {}).get('critical', [])) + len(score_result.get('gaps', {}).get('important', []))}")
    print(f"  - Questions Generated: {questions_result.get('total_questions', 0)}")
    print(f"  - Score Improvement: +{answers_result.get('score_improvement', 0)}")

    print("\n✨ Pipeline test complete!")

if __name__ == "__main__":
    main()
