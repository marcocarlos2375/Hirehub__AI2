"""
Test script for /api/adaptive-questions/refine-answer endpoint
Directly tests the backend API to capture full Python stack traces
"""
import requests
import json

API_BASE = "http://localhost:8001"

# Test payload matching frontend structure exactly
payload = {
    "question_id": "test_q1",
    "question_text": "Describe your chatbot project",
    "question_data": {
        "id": "test_q1",
        "question_text": "Describe your chatbot project",
        "title": "AI/Chatbot Development",
        "context_why": "Missing chatbot experience"
    },
    "gap_info": {
        "title": "AI/Chatbot Development",
        "description": "Missing chatbot experience"
    },
    "generated_answer": "I built a chatbot",
    "quality_issues": ["Too vague", "No metrics"],
    "additional_data": {
        "Metrics": "50 users, 87% satisfaction",
        "Technical": "Python, OpenAI API"
    }
}

print("=" * 80)
print("Testing /api/adaptive-questions/refine-answer Endpoint")
print("=" * 80)
print("\n📤 Request Payload:")
print(json.dumps(payload, indent=2))
print("\n" + "=" * 80)

try:
    print("\n🚀 Sending POST request...")
    response = requests.post(
        f"{API_BASE}/api/adaptive-questions/refine-answer",
        json=payload,
        timeout=30
    )

    print(f"\n✅ Response Status: {response.status_code}")

    if response.status_code == 200:
        print("\n✅ SUCCESS - Response Body:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\n❌ ERROR - Status {response.status_code}")
        print("\n📄 Response Body:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)

except requests.exceptions.RequestException as e:
    print(f"\n❌ REQUEST ERROR: {type(e).__name__}")
    print(f"Details: {str(e)}")

    if hasattr(e, 'response') and e.response is not None:
        print(f"\nResponse Status: {e.response.status_code}")
        print(f"\n📄 Response Text:")
        print(e.response.text)

except Exception as e:
    print(f"\n❌ UNEXPECTED ERROR: {type(e).__name__}")
    print(f"Details: {str(e)}")

print("\n" + "=" * 80)
print("Test Complete")
print("=" * 80)
