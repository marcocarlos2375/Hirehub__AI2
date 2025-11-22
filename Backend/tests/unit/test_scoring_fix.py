"""
Test to verify improved scoring system.
Software Developer vs Doctor JD should now score 5-12% instead of 50%.
"""

import requests
import json

API_BASE = "http://localhost:8000"

# Software Developer CV
software_dev_cv = {
    "personal_info": {
        "name": "John Developer",
        "email": "john@example.com",
        "location": "San Francisco, CA"
    },
    "professional_summary": "Experienced software engineer specializing in full-stack web development with expertise in Python, React, and cloud technologies.",
    "technical_skills": [
        "Python", "JavaScript", "React", "Node.js", "AWS", "Docker",
        "PostgreSQL", "Git", "REST APIs", "CI/CD"
    ],
    "soft_skills": ["Agile", "Git", "Code Review", "API Design", "Testing"],
    "work_experience": [
        {
            "role": "Senior Software Engineer",
            "company": "Tech Corp Software Solutions",
            "duration": "3 years",
            "achievements": [
                "Built scalable web applications",
                "Improved system performance by 40%",
                "Led team of 5 developers"
            ]
        },
        {
            "role": "Software Developer",
            "company": "Digital Innovations",
            "duration": "2 years",
            "achievements": [
                "Developed RESTful APIs",
                "Implemented CI/CD pipelines"
            ]
        }
    ],
    "education": [
        {
            "degree": "BS Computer Science",
            "institution": "Stanford University",
            "graduation_date": "2018"
        }
    ],
    "projects": [
        {"name": "E-commerce Platform", "description": "Built using React and Node.js"},
        {"name": "Data Analytics Dashboard", "description": "Python and PostgreSQL"},
        {"name": "Mobile App", "description": "React Native"}
    ],
    "certifications": ["AWS Certified Developer"],
    "languages": ["English", "Spanish"]
}

# Doctor Job Description
doctor_jd = {
    "company_name": "City Hospital",
    "company_type": "Healthcare",
    "position_title": "Physician - Internal Medicine",
    "location": "New York, NY",
    "work_mode": "onsite",
    "experience_years_required": 5,
    "hard_skills_required": [
        {"skill": "Internal Medicine", "priority": "required"},
        {"skill": "Patient Care", "priority": "required"},
        {"skill": "Diagnosis", "priority": "required"},
        {"skill": "Medical Records", "priority": "required"}
    ],
    "soft_skills_required": [
        "Patient Communication",
        "Bedside Manner",
        "Medical Ethics",
        "Emergency Response",
        "Clinical Decision Making"
    ],
    "tech_stack": ["EMR Systems", "Medical Imaging Software"],
    "responsibilities": [
        "Diagnose and treat patients",
        "Manage patient care plans",
        "Collaborate with medical staff",
        "Maintain medical records"
    ],
    "domain_expertise": {
        "industry": ["Healthcare", "Medical"],
        "specific_knowledge": ["Internal Medicine", "Clinical Practice", "Patient Care"]
    },
    "education_requirements": {
        "degree": "MD",
        "field": "Medicine",
        "required": True
    }
}

def test_software_dev_vs_doctor():
    """Test that software developer scores very low against doctor JD"""
    print("\n" + "=" * 80)
    print("🧪 TESTING IMPROVED SCORING SYSTEM")
    print("=" * 80)
    print("\n📋 Scenario: Software Developer CV vs Doctor Job Description")
    print("Expected: 5-12% (previously was ~50%)")
    print("\n")

    # Call the API
    payload = {
        "parsed_cv": software_dev_cv,
        "parsed_jd": doctor_jd
    }

    try:
        response = requests.post(
            f"{API_BASE}/api/calculate-score",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            overall_score = result['overall_score']

            print("✅ API Response Received\n")
            print(f"📊 OVERALL SCORE: {overall_score}%\n")

            # Print category breakdown
            print("📈 Category Breakdown:")
            print("-" * 80)
            categories = result.get('category_scores', {})
            for category, details in categories.items():
                score = details.get('score', 0)
                weight = details.get('weight', 0) * 100
                weighted_contribution = score * details.get('weight', 0)
                print(f"  {category.replace('_', ' ').title():25} {score:3}% (weight: {weight:4.1f}%) → {weighted_contribution:5.1f} pts")

            print("-" * 80)

            # Evaluation
            print("\n🎯 Evaluation:")
            if overall_score <= 12:
                print(f"  ✅ EXCELLENT! Score is {overall_score}% (within expected 5-12% range)")
                print("  ✅ The scoring system correctly identifies this as a VERY POOR match")
            elif overall_score <= 20:
                print(f"  ⚠️  GOOD: Score is {overall_score}% (slightly higher than expected 5-12%)")
                print("  ✅ Still a significant improvement from the old ~50%")
            elif overall_score <= 35:
                print(f"  ⚠️  IMPROVED: Score is {overall_score}% (better than old 50%, but could be lower)")
            else:
                print(f"  ❌ NEEDS WORK: Score is {overall_score}% (still too high)")
                print("  ❌ Expected <12% for completely mismatched roles")

            # Show specific issues if score is still high
            if overall_score > 12:
                print("\n🔍 High-scoring categories (potential issues):")
                for category, details in categories.items():
                    score = details.get('score', 0)
                    if score > 30:
                        print(f"  - {category.replace('_', ' ').title()}: {score}%")

            return result

        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    test_software_dev_vs_doctor()
    print("\n" + "=" * 80)
    print("✨ Test Complete!")
    print("=" * 80 + "\n")
