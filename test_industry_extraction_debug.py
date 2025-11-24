"""
Debug script to test industry extraction from projects
"""
import requests
import json

# Test with Sophia's HealthTrack project
TEST_CV = {
    "projects": [
        {
            "name": "HealthTrack App - Redesign (Personal Project)",
            "description": "Redesigned health tracking mobile app improving user retention by 25%. Conducted user research with 20 participants to identify pain points. Created user personas, user flows, wireframes, and high-fidelity prototypes. Implemented accessibility best practices (WCAG 2.1 AA compliance).",
            "technologies": ["User Research", "User Personas", "User Flows", "Wireframing", "Prototyping", "Accessibility"]
        }
    ]
}

TEST_JD = {
    "domain_expertise": {
        "industry": ["Healthcare Technology", "MedTech", "Digital Health"]
    }
}

def test_industry_extraction():
    print("=" * 80)
    print("Testing Industry Extraction from HealthTrack Project")
    print("=" * 80)

    print("\n1. Testing with minimal CV containing only HealthTrack project...")
    print(f"   Project name: {TEST_CV['projects'][0]['name']}")
    print(f"   Project description: {TEST_CV['projects'][0]['description'][:100]}...")

    print("\n2. Testing industry match calculation...")
    # We need to use the internal calculate_industry_match function
    # Since it's not exposed as an API endpoint, we'll test the full scoring

    response = requests.post(
        "http://localhost:8001/api/calculate-score?bypass_cache=true",
        json={
            "parsed_cv": TEST_CV,
            "parsed_jd": TEST_JD
        }
    )

    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return

    result = response.json()
    print(f"✅ Response received")
    print(f"\n   Overall Score: {result.get('overall_score')}%")

    # Check category scores for domain expertise
    category_scores = result.get('category_scores', {})
    if 'domain_expertise' in category_scores:
        domain_score = category_scores['domain_expertise']
        print(f"\n   Domain Expertise Score: {domain_score.get('score')}%")
        print(f"   Weight: {domain_score.get('weight')}%")
        print(f"   Status: {domain_score.get('status')}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_industry_extraction()
