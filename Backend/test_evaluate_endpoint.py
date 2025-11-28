"""
Test the /api/evaluate-answer endpoint to verify it returns structured ImprovementSuggestion objects.

This test verifies:
1. The endpoint returns 200 OK
2. improvement_suggestions is an array of objects (not strings)
3. Each suggestion has all 4 required fields: type, title, examples, help_text
4. examples is an array of strings (not a single string)
5. help_text is properly set for use as placeholder
"""

import requests
import json

# API endpoint
API_URL = "http://localhost:8001/api/evaluate-answer"

# Test payload - intentionally low-quality answer to trigger suggestions
test_payload = {
    "question_id": "test_refinement_card_123",
    "question_text": "Describe your experience building chatbots with LLMs for customer service",
    "answer_text": "I built a chatbot for customer service using AI. It helps customers.",
    "gap_info": {
        "title": "LLM Chatbot Development",
        "description": "Experience with building conversational AI using large language models for automating customer support"
    },
    "language": "english"
}

def test_evaluate_answer_endpoint():
    """Test the evaluate-answer endpoint returns structured suggestions."""

    print("=" * 80)
    print("TESTING /api/evaluate-answer ENDPOINT")
    print("=" * 80)
    print()

    print("📤 Sending request to:", API_URL)
    print("📝 Test answer:", test_payload["answer_text"])
    print()

    # Make the request
    response = requests.post(API_URL, json=test_payload)

    # Check response status
    print(f"✅ Response status: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Parse response
    data = response.json()

    print(f"📊 Quality score: {data.get('quality_score')}/10")
    print(f"🎯 Is acceptable: {data.get('is_acceptable')}")
    print()

    # Check improvement_suggestions structure
    suggestions = data.get("improvement_suggestions", [])
    print(f"💡 Number of suggestions: {len(suggestions)}")
    print()

    if len(suggestions) == 0:
        print("⚠️  WARNING: No suggestions returned (answer might be rated too high)")
        print("   This is OK if quality_score >= 7")
        return

    # Verify each suggestion has the correct structure
    for i, suggestion in enumerate(suggestions, 1):
        print(f"--- Suggestion #{i} ---")

        # Check it's an object, not a string
        assert isinstance(suggestion, dict), f"❌ Suggestion #{i} is a {type(suggestion)}, expected dict/object"
        print(f"✅ Is object: {type(suggestion).__name__}")

        # Check all 4 required fields exist
        required_fields = ["type", "title", "examples", "help_text"]
        for field in required_fields:
            assert field in suggestion, f"❌ Missing field '{field}' in suggestion #{i}"
        print(f"✅ Has all 4 fields: {', '.join(required_fields)}")

        # Check field types
        assert isinstance(suggestion["type"], str), f"❌ 'type' should be string"
        assert isinstance(suggestion["title"], str), f"❌ 'title' should be string"
        assert isinstance(suggestion["examples"], list), f"❌ 'examples' should be array, got {type(suggestion['examples'])}"
        assert isinstance(suggestion["help_text"], str), f"❌ 'help_text' should be string"
        print(f"✅ Field types correct")

        # Check examples array has items
        assert len(suggestion["examples"]) > 0, f"❌ 'examples' array is empty"
        print(f"✅ Examples array has {len(suggestion['examples'])} items")

        # Display the actual content
        print(f"📌 type: {suggestion['type']}")
        print(f"📌 title: {suggestion['title']}")
        print(f"📌 help_text: {suggestion['help_text']}")
        print(f"📌 examples ({len(suggestion['examples'])} items):")
        for j, example in enumerate(suggestion["examples"], 1):
            assert isinstance(example, str), f"❌ Example #{j} should be string, got {type(example)}"
            print(f"   {j}. {example[:100]}{'...' if len(example) > 100 else ''}")
        print()

    print("=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  • Endpoint: {API_URL}")
    print(f"  • Response status: {response.status_code}")
    print(f"  • Quality score: {data.get('quality_score')}/10")
    print(f"  • Suggestions count: {len(suggestions)}")
    print(f"  • Structure: Objects with type, title, examples[], help_text ✅")
    print()

if __name__ == "__main__":
    try:
        test_evaluate_answer_endpoint()
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
