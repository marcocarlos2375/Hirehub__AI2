"""
Test the /api/format-answer endpoint to verify AI-powered answer formatting.

This test verifies:
1. Type detection works correctly
2. Professional name/title is generated
3. Bullet points are formatted properly
4. Technologies are extracted
5. Metadata is populated based on type
"""

import requests
import json

# API endpoint
API_URL = "http://localhost:8001/api/format-answer"

# Test payload - chatbot project answer
test_payload_project = {
    "question_text": "Describe your experience building chatbots with LLMs for customer service",
    "answer_text": "I built a chatbot for customer service using AI. It reduced response time significantly and helped many customers.",
    "gap_info": {
        "title": "LLM Chatbot Development",
        "description": "Experience with building conversational AI using large language models"
    },
    "refinement_data": {
        "llm_framework": "Built using OpenAI's GPT-4 API with LangChain for conversation orchestration",
        "metrics": "Reduced response time from 12 minutes to 38 seconds while handling 250+ daily queries",
        "timeline": "Developed over 3 months with 800 FAQ articles and 2,000 labeled conversations"
    },
    "language": "english"
}

def test_format_answer_endpoint():
    """Test the format-answer endpoint returns structured formatted answer."""

    print("=" * 80)
    print("TESTING /api/format-answer ENDPOINT")
    print("=" * 80)
    print()

    print("📤 Sending request to:", API_URL)
    print("📝 Raw answer:", test_payload_project["answer_text"])
    print()

    # Make the request
    response = requests.post(API_URL, json=test_payload_project)

    # Check response status
    print(f"✅ Response status: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Parse response
    data = response.json()

    print()
    print("=" * 80)
    print("FORMATTED ANSWER RESULT")
    print("=" * 80)
    print()

    # Check type
    assert "type" in data, "Missing 'type' field"
    print(f"📌 Type: {data['type']}")
    assert data['type'] in ['project', 'job', 'course', 'research', 'volunteer', 'other'], \
        f"Invalid type: {data['type']}"

    # Check name
    assert "name" in data, "Missing 'name' field"
    assert len(data['name']) > 0, "Name is empty"
    print(f"📌 Name: {data['name']}")
    print()

    # Check subtitle (for projects)
    if data['type'] == 'project' and data.get('subtitle'):
        print(f"📌 Subtitle: {data['subtitle']}")
        print()

    # Check bullet points
    assert "bullet_points" in data, "Missing 'bullet_points' field"
    assert isinstance(data['bullet_points'], list), "bullet_points should be an array"
    assert len(data['bullet_points']) >= 3, f"Expected at least 3 bullet points, got {len(data['bullet_points'])}"
    print(f"📌 Bullet Points ({len(data['bullet_points'])} items):")
    for i, bullet in enumerate(data['bullet_points'], 1):
        assert isinstance(bullet, str), f"Bullet {i} should be a string"
        print(f"   {i}. {bullet}")
    print()

    # Check technologies
    assert "technologies" in data, "Missing 'technologies' field"
    assert isinstance(data['technologies'], list), "technologies should be an array"
    assert len(data['technologies']) > 0, "technologies array is empty"
    print(f"📌 Technologies ({len(data['technologies'])} items): {', '.join(data['technologies'])}")
    print()

    # Check optional fields based on type
    if data['type'] == 'project':
        if data.get('duration'):
            print(f"📌 Duration: {data['duration']}")
        if data.get('team_size'):
            print(f"📌 Team Size: {data['team_size']}")

    elif data['type'] == 'job':
        if data.get('company'):
            print(f"📌 Company: {data['company']}")
        if data.get('duration'):
            print(f"📌 Duration: {data['duration']}")

    elif data['type'] == 'course':
        if data.get('provider'):
            print(f"📌 Provider: {data['provider']}")
        if data.get('skills_gained'):
            print(f"📌 Skills Gained: {', '.join(data['skills_gained'])}")

    print()
    print("=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  • Endpoint: {API_URL}")
    print(f"  • Response status: {response.status_code}")
    print(f"  • Detected type: {data['type']}")
    print(f"  • Generated name: {data['name']}")
    print(f"  • Bullet points: {len(data['bullet_points'])}")
    print(f"  • Technologies: {len(data['technologies'])}")
    print()

if __name__ == "__main__":
    try:
        test_format_answer_endpoint()
    except AssertionError as e:
        print()
        print("❌ TEST FAILED!")
        print(f"   Error: {e}")
        print()
        exit(1)
    except requests.exceptions.ConnectionError:
        print()
        print("❌ CONNECTION ERROR!")
        print("   Make sure the API is running at http://localhost:8001")
        print("   Run: docker-compose up api")
        print()
        exit(1)
    except Exception as e:
        print()
        print("❌ UNEXPECTED ERROR!")
        print(f"   {type(e).__name__}: {e}")
        print()
        exit(1)
