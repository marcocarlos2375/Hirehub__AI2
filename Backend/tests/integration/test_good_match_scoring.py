"""
Test the improved scoring logic with the "good match" sample (Backend Engineer vs Backend Developer CV).
Expected score: 75-82% (was 43% before fixes).
"""

import requests
import json

API_BASE = "http://localhost:8000"

# Backend Engineer JD (should be good match for John Doe CV)
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

# John Doe CV (Backend Engineer with 8 years)
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


def test_good_match_scoring():
    """Test that backend engineer JD scores 75-82% against backend engineer CV"""
    print("\n" + "=" * 80)
    print("🧪 TESTING IMPROVED SCORING LOGIC")
    print("=" * 80)
    print("\nScenario: Backend Engineer JD vs Backend Engineer CV")
    print("Expected Score: 75-82% (was 43% before fixes)")
    print("\n")

    # Step 1: Parse JD
    print("Step 1: Parsing Job Description...")
    try:
        jd_response = requests.post(
            f"{API_BASE}/api/parse",
            json={"job_description": backend_engineer_jd, "language": "english"},
            timeout=30
        )

        if jd_response.status_code != 200:
            print(f"❌ JD Parsing failed: {jd_response.status_code}")
            print(jd_response.text)
            return

        parsed_jd = jd_response.json().get('data', {})
        print(f"✅ JD Parsed: {parsed_jd.get('position_title', 'N/A')}")
        print(f"   Company: {parsed_jd.get('company_name', 'N/A')}")
        print(f"   Hard Skills Required: {len(parsed_jd.get('hard_skills_required', []))} skills")
        print(f"   Soft Skills Required: {len(parsed_jd.get('soft_skills_required', []))} skills")

    except Exception as e:
        print(f"❌ Error parsing JD: {e}")
        return

    # Step 2: Parse CV
    print("\nStep 2: Parsing CV...")
    try:
        cv_response = requests.post(
            f"{API_BASE}/api/parse-cv",
            json={"resume_text": john_doe_cv, "language": "english"},
            timeout=30
        )

        if cv_response.status_code != 200:
            print(f"❌ CV Parsing failed: {cv_response.status_code}")
            print(cv_response.text)
            return

        parsed_cv = cv_response.json().get('data', {})
        print(f"✅ CV Parsed: {parsed_cv.get('personal_info', {}).get('name', 'N/A')}")
        print(f"   Technical Skills: {len(parsed_cv.get('technical_skills', []))} skills")
        print(f"   Soft Skills: {len(parsed_cv.get('soft_skills', []))} skills")
        print(f"   Work Experience: {len(parsed_cv.get('work_experience', []))} positions")

    except Exception as e:
        print(f"❌ Error parsing CV: {e}")
        return

    # Step 3: Calculate Score
    print("\nStep 3: Calculating Compatibility Score...")
    try:
        score_response = requests.post(
            f"{API_BASE}/api/calculate-score",
            json={"parsed_cv": parsed_cv, "parsed_jd": parsed_jd},
            timeout=60
        )

        if score_response.status_code != 200:
            print(f"❌ Scoring failed: {score_response.status_code}")
            print(score_response.text)
            return

        result = score_response.json()
        overall_score = result.get('overall_score', 0)

        print(f"\n{'=' * 80}")
        print(f"📊 OVERALL SCORE: {overall_score}%")
        print(f"   Status: {result.get('overall_status', 'N/A')}")
        print(f"   Calculation Time: {result.get('time_seconds', 0):.2f}s")
        print(f"{'=' * 80}\n")

        # Category breakdown
        print("📈 8-Category Breakdown:")
        print("-" * 80)

        categories = result.get('category_scores', {})
        for category, details in categories.items():
            score = details.get('score', 0)
            weight = details.get('weight', 0) * 100
            weighted = score * details.get('weight', 0)
            status = details.get('status', 'N/A')

            # Highlight improvements
            improvement = ""
            if category == 'soft_skills' and score > 50:
                improvement = " ✨ IMPROVED (was 0%)"
            elif category == 'hard_skills' and score > 75:
                improvement = " ✨ IMPROVED (was 50%)"
            elif category == 'industry_match' and score > 50:
                improvement = " ✨ IMPROVED (was 0%)"
            elif category == 'domain_expertise' and score > 50:
                improvement = " ✨ IMPROVED (was 33%)"

            print(f"  {category.replace('_', ' ').title():25} {score:3}% ({status:15}) weight: {weight:4.1f}% → {weighted:5.1f} pts{improvement}")

        print("-" * 80)

        # Evaluation
        print(f"\n🎯 Evaluation:")
        if overall_score >= 75 and overall_score <= 85:
            print(f"  ✅ EXCELLENT! Score is {overall_score}% (within expected 75-82% range)")
            print(f"  ✅ Scoring logic improvements are working!")
        elif overall_score >= 70:
            print(f"  ✅ GOOD! Score is {overall_score}% (close to expected 75-82%)")
            print(f"  ✅ Significant improvement from previous 43%")
        elif overall_score >= 60:
            print(f"  ⚠️  IMPROVED: Score is {overall_score}% (better than 43%, but expected 75-82%)")
            print(f"  💡 Some categories may need further tuning")
        else:
            print(f"  ❌ NEEDS MORE WORK: Score is {overall_score}% (still below expected 75-82%)")
            print(f"  ❌ Check which categories are still scoring low")

        # Show key improvements
        print(f"\n🔍 Key Category Scores:")
        print(f"  Hard Skills: {categories.get('hard_skills', {}).get('score', 0)}% (expected 80-85%)")
        print(f"  Soft Skills: {categories.get('soft_skills', {}).get('score', 0)}% (expected 85-95%)")
        print(f"  Domain: {categories.get('domain_expertise', {}).get('score', 0)}% (expected 65-70%)")
        print(f"  Industry: {categories.get('industry_match', {}).get('score', 0)}% (expected 85-95%)")

        return result

    except Exception as e:
        print(f"❌ Error calculating score: {e}")
        return None


if __name__ == "__main__":
    test_good_match_scoring()
    print("\n" + "=" * 80)
    print("✨ Test Complete!")
    print("=" * 80 + "\n")
