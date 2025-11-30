"""
Test that the 422 error in refinement API is fixed.
Simulates the exact request structure from the frontend.
"""

import requests
import json

API_BASE = "http://localhost:8001"

def test_refinement_422_fix():
    print("=" * 80)
    print("TESTING: 422 Error Fix in Answer Refinement API")
    print("=" * 80)

    # Simulate the exact request structure from frontend
    request_data = {
        "question_id": "q1",
        "question_text": "Describe your experience with AWS Lambda",
        "question_data": {
            "id": "q1",
            "title": "AWS Lambda Experience",
            "priority": "CRITICAL"
        },
        "gap_info": {
            "title": "AWS Lambda",
            "description": "Serverless computing with AWS Lambda"
        },
        "generated_answer": "I worked with AWS Lambda at my previous company.",
        "quality_issues": [
            {
                "label": "Lacks Specificity",
                "description": "Answer doesn't mention specific Lambda functions or use cases"
            },
            {
                "label": "Missing Metrics",
                "description": "No quantifiable outcomes or performance metrics provided"
            }
        ],
        "additional_data": {
            "suggestion_1": "Built serverless API with Lambda functions",
            "suggestion_2": "Processed 10K events per day",
            "suggestion_3": "Reduced infrastructure costs by 40%"
        }
    }

    print("\nRequest Payload:")
    print(json.dumps(request_data, indent=2))
    print("\n" + "=" * 80)

    try:
        response = requests.post(
            f"{API_BASE}/api/adaptive-questions/refine-answer",
            json=request_data,
            timeout=30
        )

        print(f"\nResponse Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ SUCCESS: Request accepted (422 error is FIXED!)")
            result = response.json()
            print("\nResponse Data:")
            print(json.dumps(result, indent=2))
        elif response.status_code == 422:
            print("❌ FAILED: Still getting 422 error")
            print("\nError Response:")
            print(response.text)
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print(response.text)

    except requests.exceptions.Timeout:
        print("⚠️  Request timed out (API might be processing)")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    # Wait for API to be ready
    import time
    print("Waiting for API to be ready...")
    time.sleep(8)

    test_refinement_422_fix()
