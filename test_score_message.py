"""
Test AI-generated encouraging score messages
"""
import requests
import json

# Simple test CV and JD
SIMPLE_CV = {
    "personal_info": {"name": "John Doe"},
    "skills": {
        "hard_skills": [
            {"skill": "Python", "priority": "critical"},
            {"skill": "JavaScript", "priority": "important"}
        ]
    },
    "experience": [
        {"company": "Tech Corp", "position": "Developer", "duration": "2 years"}
    ]
}

SIMPLE_JD = {
    "job_title": "Senior Python Developer",
    "skills": {
        "hard_skills": [
            {"skill": "Python", "priority": "critical"},
            {"skill": "JavaScript", "priority": "important"},
            {"skill": "React", "priority": "critical"},
            {"skill": "AWS", "priority": "important"}
        ]
    },
    "experience_required": "3-5 years"
}

def test_score_message():
    print("=" * 80)
    print("Testing AI-Generated Score Messages")
    print("=" * 80)

    print("\nCalculating score with bypass_cache=true...")
    response = requests.post(
        "http://localhost:8001/api/calculate-score?bypass_cache=true",
        json={
            "parsed_cv": SIMPLE_CV,
            "parsed_jd": SIMPLE_JD,
            "language": "english"
        }
    )

    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(response.text[:500])
        return

    data = response.json()

    print(f"\n✅ Score calculation successful!")
    print(f"\nNumeric Score (backend only): {data.get('overall_score')}%")
    print(f"Status: {data.get('overall_status')}")

    # Check for score_message
    score_message = data.get('score_message')

    if score_message:
        print("\n" + "=" * 80)
        print("AI-GENERATED MESSAGE (User-Facing)")
        print("=" * 80)
        print(f"\nTitle: {score_message.get('title')}")
        print(f"Subtitle: {score_message.get('subtitle')}")
        print("\n" + "=" * 80)
        print("✅ SUCCESS: AI-generated message is working!")
        print("=" * 80)
    else:
        print("\n❌ FAILURE: No score_message in response")
        print(f"Response keys: {list(data.keys())}")

if __name__ == "__main__":
    test_score_message()
