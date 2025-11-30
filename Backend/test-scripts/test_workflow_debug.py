"""Debug script to see what the workflow is returning."""
import requests
import json

API_BASE = "http://localhost:8001"

# Test 1: Has experience
print("=" * 60)
print("TEST 1: User has experience with React")
print("=" * 60)

data = {
    "question_id": "test_has_exp",
    "question_text": "Do you have React experience?",
    "question_data": {},
    "gap_info": {
        "title": "React",
        "description": "Need to learn React for frontend development"
    },
    "user_id": "test_user_debug",
    "parsed_cv": {"skills": ["Python", "FastAPI"]},
    "parsed_jd": {"required_skills": ["React", "JavaScript"]},
    "experience_check_response": "yes",
    "language": "english"
}

response = requests.post(f"{API_BASE}/api/adaptive-questions/start", json=data)
print(f"Status: {response.status_code}")
print(f"\nResponse:")
print(json.dumps(response.json(), indent=2))

# Test 2: Willing to learn
print("\n" + "=" * 60)
print("TEST 2: User willing to learn Vue.js")
print("=" * 60)

data2 = {
    "question_id": "test_willing",
    "question_text": "Are you willing to learn Vue.js?",
    "question_data": {},
    "gap_info": {
        "title": "Vue.js",
        "description": "Want to learn Vue.js for new project"
    },
    "user_id": "test_user_debug",
    "parsed_cv": {"skills": ["Python", "FastAPI"]},
    "parsed_jd": {"required_skills": ["Vue.js", "JavaScript"]},
    "experience_check_response": "willing_to_learn",
    "language": "english"
}

response2 = requests.post(f"{API_BASE}/api/adaptive-questions/start", json=data2)
print(f"Status: {response2.status_code}")
print(f"\nResponse:")
print(json.dumps(response2.json(), indent=2))
