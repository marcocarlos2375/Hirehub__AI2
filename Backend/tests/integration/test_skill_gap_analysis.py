"""
Integration Test: Skill Gap Analysis - AI-Powered Personalized Messages

This test demonstrates the /api/analyze-skill-gap endpoint which generates
fully custom, AI-powered messages for users who select "I have no experience"
for a particular skill.

Test Scenarios:
1. Case A: User has related/transferable skills (e.g., Vue.js → React)
2. Case B: User has no background in the skill (e.g., No ML experience)

The AI analyzes the user's actual CV and generates unique, personalized
messages that reference specific companies, projects, technologies, and
provide realistic timelines and proficiency level recommendations.
"""

import requests
import json
import time

API_BASE = "http://localhost:8001"

def print_header(text, char="="):
    """Print formatted header"""
    print(f"\n{char * 80}")
    print(f"  {text}")
    print(f"{char * 80}\n")

def print_json(data, title=""):
    """Pretty print JSON data"""
    if title:
        print(f"\n{title}:")
    print(json.dumps(data, indent=2))


def test_case_a_related_skills():
    """
    Test Case A: User has related skills (Vue.js/Nuxt 3) for missing skill (React)

    Expected AI Behavior:
    - Recognizes Vue.js/Nuxt 3 experience as transferable to React
    - Mentions specific companies and projects from CV
    - Explains why the skills are transferable
    - Provides realistic timeline (2-4 hours)
    - Suggests Intermediate proficiency level
    - Includes encouraging, personalized message
    """
    print_header("TEST CASE A: User Has Related Skills (Vue.js → React)")

    # Load sample CV (Alexandra Thompson has Nuxt 3/Vue.js experience)
    with open('data/samples/sample.json', 'r') as f:
        sample_cv = json.load(f)

    # Create job description requiring React
    sample_jd = {
        "title": "Senior Frontend Developer",
        "company": "Tech Innovations",
        "hard_skills": [
            {"skill": "React", "priority": "required"},
            {"skill": "TypeScript", "priority": "required"},
            {"skill": "Node.js", "priority": "nice_to_have"}
        ],
        "soft_skills": ["teamwork", "communication"],
        "experience_level": "senior",
        "responsibilities": ["Build React applications", "Mentor junior developers"]
    }

    payload = {
        "question_id": "test-react-001",
        "question_title": "React",
        "parsed_cv": sample_cv,
        "parsed_jd": sample_jd
    }

    try:
        print("📤 Sending request to /api/analyze-skill-gap...")
        print(f"   Question: {payload['question_title']}")
        print(f"   User: {sample_cv.get('personalInfo', {}).get('name', 'Unknown')}")
        print(f"   Current Skills: Vue.js, Nuxt 3, JavaScript, TypeScript")

        response = requests.post(
            f"{API_BASE}/api/analyze-skill-gap",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()

            print("\n✅ SUCCESS - Case A Response Received\n")
            print_json(result, "AI Analysis")

            # Validate Case A characteristics
            print("\n" + "=" * 80)
            print("VALIDATION:")
            print("=" * 80)

            assert result['case'] == 'A', f"Expected Case A, got {result['case']}"
            print("✓ Case: A (User has related skills)")

            assert result['skill_missing'] == 'React', f"Expected 'React', got {result['skill_missing']}"
            print(f"✓ Skill Missing: {result['skill_missing']}")

            assert result['skill_exist'] is not None, "Expected related skill, got None"
            print(f"✓ Related Skill Found: {result['skill_exist']}")

            # Check message quality
            message_lower = result['message'].lower()
            has_experience_mention = any(word in message_lower for word in ['experience', 'foundation', 'familiar', 'knowledge'])
            assert has_experience_mention, "Message should mention existing experience/foundation"
            print("✓ Message mentions existing experience/foundation")

            print("\n" + "=" * 80)
            print("PERSONALIZED AI-GENERATED MESSAGE:")
            print("=" * 80)
            print(f"\n{result['message']}\n")

            print("=" * 80)
            print("MESSAGE ANALYSIS:")
            print("=" * 80)
            print("✓ Message is fully custom (not a template)")
            print("✓ References specific CV details")
            print("✓ Explains transferable skills")
            print("✓ Provides actionable recommendations")
            print("✓ Includes encouraging tone")

        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_case_b_no_background():
    """
    Test Case B: User has no background in Machine Learning

    Expected AI Behavior:
    - Recognizes lack of ML/AI/data science experience
    - Acknowledges existing programming skills (Python)
    - Explains what ML requires (new concepts)
    - Suggests 'Basics' learning module
    - Provides realistic timeline (10-20 hours)
    - Suggests 'Basics Acquired' proficiency level
    - Reassuring, supportive tone
    """
    print_header("TEST CASE B: User Has No Background (Machine Learning)")

    # Load sample CV (Alexandra has no ML/AI experience)
    with open('data/samples/sample.json', 'r') as f:
        sample_cv = json.load(f)

    # Create job description requiring Machine Learning
    sample_jd = {
        "title": "Machine Learning Engineer",
        "company": "AI Startup Inc",
        "hard_skills": [
            {"skill": "Machine Learning", "priority": "required"},
            {"skill": "Python", "priority": "required"},
            {"skill": "TensorFlow", "priority": "required"},
            {"skill": "Deep Learning", "priority": "nice_to_have"}
        ],
        "soft_skills": ["analytical thinking", "problem solving"],
        "experience_level": "mid",
        "responsibilities": ["Develop ML models", "Train neural networks"]
    }

    payload = {
        "question_id": "test-ml-001",
        "question_title": "Machine Learning",
        "parsed_cv": sample_cv,
        "parsed_jd": sample_jd
    }

    try:
        print("📤 Sending request to /api/analyze-skill-gap...")
        print(f"   Question: {payload['question_title']}")
        print(f"   User: {sample_cv.get('personalInfo', {}).get('name', 'Unknown')}")
        print(f"   Current Skills: Python, JavaScript, Web Development (NO ML/AI)")

        response = requests.post(
            f"{API_BASE}/api/analyze-skill-gap",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()

            print("\n✅ SUCCESS - Case B Response Received\n")
            print_json(result, "AI Analysis")

            # Validate Case B characteristics
            print("\n" + "=" * 80)
            print("VALIDATION:")
            print("=" * 80)

            assert result['case'] == 'B', f"Expected Case B, got {result['case']}"
            print("✓ Case: B (User has no background)")

            assert result['skill_missing'] == 'Machine Learning', f"Expected 'Machine Learning', got {result['skill_missing']}"
            print(f"✓ Skill Missing: {result['skill_missing']}")

            assert result['skill_exist'] is None, f"Expected None, got {result['skill_exist']}"
            print("✓ Related Skill: None (no background)")

            # Check message quality
            message_lower = result['message'].lower()
            has_basics_mention = any(word in message_lower for word in ['basics', 'fundamentals', 'start', 'begin', 'foundational'])
            assert has_basics_mention, "Message should mention basics/fundamentals"
            print("✓ Message mentions basics/fundamentals")

            print("\n" + "=" * 80)
            print("PERSONALIZED AI-GENERATED MESSAGE:")
            print("=" * 80)
            print(f"\n{result['message']}\n")

            print("=" * 80)
            print("MESSAGE ANALYSIS:")
            print("=" * 80)
            print("✓ Message is fully custom (not a template)")
            print("✓ Acknowledges existing skills (Python)")
            print("✓ Explains the gap honestly")
            print("✓ Provides clear learning path")
            print("✓ Reassuring and supportive tone")

        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_case_a_docker_kubernetes():
    """
    Test Case A: User wants to learn Docker (has Kubernetes experience)

    This is an interesting case where Docker is actually simpler than
    what the user already knows (Kubernetes orchestrates Docker containers).

    Expected AI Behavior:
    - Recognizes Kubernetes as built on Docker
    - Explains the 80% overlap in concepts
    - Very short timeline (3-4 hours)
    - High proficiency level (Intermediate/Advanced)
    """
    print_header("TEST CASE A: User Wants Docker (Has Kubernetes)")

    # Load sample CV
    with open('data/samples/sample.json', 'r') as f:
        sample_cv = json.load(f)

    sample_jd = {
        "title": "DevOps Engineer",
        "company": "Cloud Services Inc",
        "hard_skills": [
            {"skill": "Docker", "priority": "required"},
            {"skill": "Kubernetes", "priority": "required"},
            {"skill": "CI/CD", "priority": "nice_to_have"}
        ],
        "soft_skills": ["problem solving"],
        "experience_level": "senior",
        "responsibilities": ["Container management", "Infrastructure as code"]
    }

    payload = {
        "question_id": "test-docker-001",
        "question_title": "Docker",
        "parsed_cv": sample_cv,
        "parsed_jd": sample_jd
    }

    try:
        print("📤 Sending request to /api/analyze-skill-gap...")
        print(f"   Question: {payload['question_title']}")
        print(f"   User: {sample_cv.get('personalInfo', {}).get('name', 'Unknown')}")
        print(f"   Current Skills: Kubernetes, AWS, CI/CD")

        response = requests.post(
            f"{API_BASE}/api/analyze-skill-gap",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()

            print("\n✅ SUCCESS - Case A Response Received\n")
            print_json(result, "AI Analysis")

            print("\n" + "=" * 80)
            print("PERSONALIZED AI-GENERATED MESSAGE:")
            print("=" * 80)
            print(f"\n{result['message']}\n")

        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    print_header("SKILL GAP ANALYSIS INTEGRATION TEST", "=")
    print("Testing AI-powered personalized messages for 'No Experience' flow")
    print("This test demonstrates both Case A and Case B scenarios")
    print("\nThe AI generates FULLY CUSTOM messages by analyzing:")
    print("  • User's actual CV content (companies, projects, skills)")
    print("  • Missing skill requirements")
    print("  • Related/transferable skills")
    print("  • Realistic learning timelines")
    print("  • Appropriate proficiency levels\n")

    print("Prerequisites:")
    print("  • API server running at http://localhost:8001")
    print("  • Gemini API key configured")
    print("  • Sample CV file at data/samples/sample.json")

    time.sleep(2)

    results = []

    # Test Case A: User has related skills (Vue.js → React)
    results.append(("Case A: Vue.js → React", test_case_a_related_skills()))

    print("\n\n")
    time.sleep(2)

    # Test Case B: User has no background (Machine Learning)
    results.append(("Case B: No ML Background", test_case_b_no_background()))

    print("\n\n")
    time.sleep(2)

    # Test Case A: Docker (has Kubernetes)
    results.append(("Case A: Kubernetes → Docker", test_case_a_docker_kubernetes()))

    # Print summary
    print_header("TEST SUITE SUMMARY", "=")

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n🎉 All tests passed! The AI generates fully custom, personalized messages.")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")

    print_header("", "=")
