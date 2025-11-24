"""
Comprehensive Integration Tests for Adaptive Questions API Endpoints.

Tests all 6 endpoints of the adaptive question system:
1. POST /api/adaptive-questions/start
2. POST /api/adaptive-questions/submit-inputs
3. POST /api/adaptive-questions/refine-answer
4. POST /api/adaptive-questions/get-learning-resources
5. POST /api/adaptive-questions/save-learning-plan
6. POST /api/adaptive-questions/get-learning-plans
"""

import requests
import json
import time
from typing import Dict, Any, List
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8001"
COLORS = {
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
}


def colored(text: str, color: str) -> str:
    """Add color to text for terminal output."""
    return f"{COLORS.get(color, '')}{text}{COLORS['RESET']}"


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{colored('='*80, 'BLUE')}")
    print(colored(f"  {text}", 'BOLD'))
    print(f"{colored('='*80, 'BLUE')}\n")


def print_test_result(test_name: str, passed: bool, duration_ms: float, details: str = ""):
    """Print a formatted test result."""
    status = colored("✅ PASS", "GREEN") if passed else colored("❌ FAIL", "RED")
    print(f"{status} | {test_name} ({duration_ms:.0f}ms)")
    if details:
        print(f"     {colored(details, 'YELLOW')}")


def make_request(endpoint: str, data: Dict[str, Any], test_name: str) -> tuple[bool, Dict, float]:
    """
    Make an API request and return success status, response, and duration.

    Returns:
        tuple: (success: bool, response_data: dict, duration_ms: float)
    """
    url = f"{API_BASE_URL}{endpoint}"
    start_time = time.time()

    try:
        response = requests.post(url, json=data, headers={"Content-Type": "application/json"}, timeout=60)
        duration_ms = (time.time() - start_time) * 1000

        if response.status_code == 200:
            return True, response.json(), duration_ms
        else:
            error_msg = f"Status {response.status_code}: {response.text[:200]}"
            return False, {"error": error_msg}, duration_ms
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        return False, {"error": str(e)}, duration_ms


# Test Data
TEST_USER_ID = f"test_user_{int(datetime.now().timestamp())}"


def test_1_start_workflow_with_experience():
    """Test 1: Start workflow when user has experience (should return deep_dive_prompts)."""
    print_header("TEST 1: Start Workflow - User Has Experience")

    data = {
        "question_id": "test_aws_yes",
        "question_text": "Do you have AWS Lambda experience?",
        "question_data": {},
        "gap_info": {
            "title": "AWS Lambda",
            "description": "Serverless computing with AWS Lambda"
        },
        "user_id": TEST_USER_ID,
        "parsed_cv": {"skills": ["Python", "FastAPI"]},
        "parsed_jd": {"required_skills": ["AWS Lambda", "Python", "Serverless"]},
        "experience_check_response": "yes",
        "language": "english"
    }

    success, response, duration = make_request("/api/adaptive-questions/start", data, "Start with experience")

    if success:
        # Validate response structure
        has_prompts = "deep_dive_prompts" in response
        has_correct_step = response.get("current_step") == "deep_dive"
        prompts_count = len(response.get("deep_dive_prompts", []))

        if has_prompts and has_correct_step and 4 <= prompts_count <= 6:
            print_test_result("Start workflow (has experience)", True, duration,
                            f"Returned {prompts_count} deep dive prompts")
            print(f"\n{colored('Sample prompt:', 'BLUE')}")
            print(f"  {json.dumps(response['deep_dive_prompts'][0], indent=2)}")
            return True, response
        else:
            print_test_result("Start workflow (has experience)", False, duration,
                            f"Invalid response: {list(response.keys())}")
            return False, response
    else:
        print_test_result("Start workflow (has experience)", False, duration, response.get("error", "Unknown error"))
        return False, response


def test_2_start_workflow_willing_to_learn():
    """Test 2: Start workflow when user willing to learn (should return suggested_resources)."""
    print_header("TEST 2: Start Workflow - User Willing to Learn")

    data = {
        "question_id": "test_react_no",
        "question_text": "Do you have React experience?",
        "question_data": {},
        "gap_info": {
            "title": "React",
            "description": "Frontend JavaScript framework"
        },
        "user_id": TEST_USER_ID,
        "parsed_cv": {"skills": ["HTML", "CSS", "JavaScript"]},
        "parsed_jd": {"required_skills": ["React", "Redux", "TypeScript"]},
        "experience_check_response": "willing_to_learn",
        "language": "english"
    }

    success, response, duration = make_request("/api/adaptive-questions/start", data, "Start willing to learn")

    if success:
        # Validate response structure
        has_resources = "suggested_resources" in response
        has_correct_step = response.get("current_step") == "resources"
        resources_count = len(response.get("suggested_resources", []))

        if has_resources and has_correct_step and resources_count >= 3:
            print_test_result("Start workflow (willing to learn)", True, duration,
                            f"Returned {resources_count} learning resources")
            print(f"\n{colored('Sample resource:', 'BLUE')}")
            resource = response['suggested_resources'][0]
            print(f"  Title: {resource.get('title')}")
            print(f"  Type: {resource.get('type')} | Duration: {resource.get('duration_days')} days")
            print(f"  Difficulty: {resource.get('difficulty')} | Cost: {resource.get('cost')}")
            return True, response
        else:
            print_test_result("Start workflow (willing to learn)", False, duration,
                            f"Invalid response: {list(response.keys())}")
            return False, response
    else:
        print_test_result("Start workflow (willing to learn)", False, duration, response.get("error", "Unknown error"))
        return False, response


def test_3_submit_structured_inputs():
    """Test 3: Submit structured inputs from deep dive prompts."""
    print_header("TEST 3: Submit Structured Inputs")

    data = {
        "question_id": "test_aws_yes",
        "structured_data": {
            "context": "Work",
            "duration": "6 months across 3 projects",
            "tools": ["AWS Lambda", "API Gateway", "DynamoDB", "Python", "CloudWatch"],
            "achievement": "Built a serverless REST API for processing customer data in real-time",
            "metrics": "Handled 5000 requests/minute, reduced infrastructure costs by 60%, improved response time to 200ms"
        }
    }

    success, response, duration = make_request("/api/adaptive-questions/submit-inputs", data, "Submit inputs")

    if success:
        # Validate response structure
        has_answer = "generated_answer" in response
        has_score = "quality_score" in response
        score = response.get("quality_score", 0)

        if has_answer and has_score:
            is_good_quality = score >= 7
            status_text = "Good quality (≥7)" if is_good_quality else "Needs refinement (<7)"
            print_test_result("Submit structured inputs", True, duration,
                            f"Quality score: {score}/10 - {status_text}")
            print(f"\n{colored('Generated answer:', 'BLUE')}")
            print(f"  {response['generated_answer'][:200]}...")

            if not is_good_quality and "improvement_suggestions" in response:
                print(f"\n{colored('Improvement suggestions:', 'YELLOW')}")
                for suggestion in response['improvement_suggestions'][:2]:
                    print(f"  - {suggestion}")

            return True, response
        else:
            print_test_result("Submit structured inputs", False, duration,
                            f"Invalid response: {list(response.keys())}")
            return False, response
    else:
        print_test_result("Submit structured inputs", False, duration, response.get("error", "Unknown error"))
        return False, response


def test_4_get_learning_resources():
    """Test 4: Get learning resources on-demand for any gap."""
    print_header("TEST 4: Get Learning Resources (On-Demand)")

    data = {
        "gap": {
            "title": "Docker & Kubernetes",
            "description": "Container orchestration and microservices deployment"
        },
        "user_level": "beginner",
        "max_days": 7,
        "cost_preference": "free",
        "limit": 5
    }

    success, response, duration = make_request("/api/adaptive-questions/get-learning-resources", data, "Get resources")

    if success:
        # Validate response structure
        has_resources = "resources" in response
        has_timeline = "timeline" in response
        resources_count = len(response.get("resources", []))

        if has_resources and has_timeline and resources_count > 0:
            print_test_result("Get learning resources", True, duration,
                            f"Returned {resources_count} resources with timeline")
            print(f"\n{colored('Timeline:', 'BLUE')}")
            for item in response['timeline'][:3]:
                print(f"  {item}")

            print(f"\n{colored('Sample resource:', 'BLUE')}")
            resource = response['resources'][0]
            print(f"  Title: {resource.get('title')}")
            print(f"  Score: {resource.get('score')}/100 | Type: {resource.get('type')}")
            return True, response
        else:
            print_test_result("Get learning resources", False, duration,
                            f"Invalid response: {list(response.keys())}")
            return False, response
    else:
        print_test_result("Get learning resources", False, duration, response.get("error", "Unknown error"))
        return False, response


def test_5_save_learning_plan():
    """Test 5: Save a learning plan for a user."""
    print_header("TEST 5: Save Learning Plan")

    # First, get some resources to save
    get_resources_data = {
        "gap": {"title": "Python", "description": "Python programming"},
        "user_level": "beginner",
        "max_days": 10,
        "cost_preference": "any",
        "limit": 3
    }

    success_get, response_get, _ = make_request("/api/adaptive-questions/get-learning-resources",
                                                  get_resources_data, "Get resources for plan")

    if not success_get or not response_get.get("resources"):
        print_test_result("Save learning plan", False, 0, "Failed to get resources first")
        return False, {}

    resource_ids = [r["id"] for r in response_get["resources"][:2]]

    # Now save the plan
    data = {
        "user_id": TEST_USER_ID,
        "gap_info": {
            "title": "Python",
            "description": "Python programming fundamentals"
        },
        "selected_resource_ids": resource_ids,
        "notes": "Will complete during Q1 2025"
    }

    success, response, duration = make_request("/api/adaptive-questions/save-learning-plan", data, "Save plan")

    if success:
        # Validate response structure
        has_plan_id = "plan_id" in response
        has_status = "status" in response

        if has_plan_id and has_status:
            print_test_result("Save learning plan", True, duration,
                            f"Plan ID: {response['plan_id']}")
            return True, response
        else:
            print_test_result("Save learning plan", False, duration,
                            f"Invalid response: {list(response.keys())}")
            return False, response
    else:
        print_test_result("Save learning plan", False, duration, response.get("error", "Unknown error"))
        return False, response


def test_6_get_learning_plans():
    """Test 6: Retrieve all learning plans for a user."""
    print_header("TEST 6: Get User Learning Plans")

    data = {
        "user_id": TEST_USER_ID,
        "status": "suggested"
    }

    success, response, duration = make_request("/api/adaptive-questions/get-learning-plans", data, "Get plans")

    if success:
        # Validate response structure
        has_plans = "plans" in response
        plans = response.get("plans", [])

        if has_plans:
            print_test_result("Get user learning plans", True, duration,
                            f"Returned {len(plans)} plan(s)")

            if plans:
                print(f"\n{colored('Sample plan:', 'BLUE')}")
                plan = plans[0]
                print(f"  Gap: {plan.get('gap_title')}")
                print(f"  Resources: {len(plan.get('resources', []))}")
                print(f"  Status: {plan.get('status')}")

            return True, response
        else:
            print_test_result("Get user learning plans", False, duration,
                            f"Invalid response: {list(response.keys())}")
            return False, response
    else:
        print_test_result("Get user learning plans", False, duration, response.get("error", "Unknown error"))
        return False, response


def test_7_refine_answer():
    """Test 7: Refine an answer that scored below 7."""
    print_header("TEST 7: Refine Answer (Quality Improvement)")

    # First submit a basic answer
    submit_data = {
        "question_id": "test_refine",
        "structured_data": {
            "context": "Side Project",
            "duration": "2 weeks",
            "tools": ["React"],
            "achievement": "Made a todo app",
            "metrics": "Works fine"
        }
    }

    success_submit, response_submit, _ = make_request("/api/adaptive-questions/submit-inputs",
                                                        submit_data, "Submit basic answer")

    if not success_submit:
        print_test_result("Refine answer", False, 0, "Failed to submit initial answer")
        return False, {}

    initial_score = response_submit.get("quality_score", 10)
    print(f"  Initial score: {initial_score}/10")

    # Now refine it
    refine_data = {
        "question_id": "test_refine",
        "additional_data": {
            "specific_technologies": "Used React Hooks, Context API, and Local Storage for state management",
            "business_impact": "Created a responsive todo app with 95% mobile usability score, deployed to Vercel",
            "challenges_overcome": "Implemented drag-and-drop functionality, optimized re-renders using useMemo"
        }
    }

    success, response, duration = make_request("/api/adaptive-questions/refine-answer", refine_data, "Refine answer")

    if success:
        # Validate response structure
        has_refined = "refined_answer" in response
        has_score = "quality_score" in response
        refined_score = response.get("quality_score", 0)

        if has_refined and has_score:
            improved = refined_score > initial_score
            improvement_text = f"Improved from {initial_score} to {refined_score}" if improved else f"Score: {refined_score}"
            print_test_result("Refine answer", True, duration, improvement_text)

            print(f"\n{colored('Refined answer:', 'BLUE')}")
            print(f"  {response['refined_answer'][:200]}...")

            return True, response
        else:
            print_test_result("Refine answer", False, duration,
                            f"Invalid response: {list(response.keys())}")
            return False, response
    else:
        print_test_result("Refine answer", False, duration, response.get("error", "Unknown error"))
        return False, response


def run_all_tests():
    """Run all integration tests and print summary."""
    print(colored("\n" + "="*80, "BOLD"))
    print(colored("  ADAPTIVE QUESTIONS API - INTEGRATION TEST SUITE", "BOLD"))
    print(colored("="*80, "BOLD"))
    print(f"\nAPI Base URL: {API_BASE_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run all tests
    test_results = []

    test_results.append(("Test 1: Start (Has Experience)", *test_1_start_workflow_with_experience()[:1]))
    test_results.append(("Test 2: Start (Willing to Learn)", *test_2_start_workflow_willing_to_learn()[:1]))
    test_results.append(("Test 3: Submit Structured Inputs", *test_3_submit_structured_inputs()[:1]))
    test_results.append(("Test 4: Get Learning Resources", *test_4_get_learning_resources()[:1]))
    test_results.append(("Test 5: Save Learning Plan", *test_5_save_learning_plan()[:1]))
    test_results.append(("Test 6: Get User Plans", *test_6_get_learning_plans()[:1]))
    test_results.append(("Test 7: Refine Answer", *test_7_refine_answer()[:1]))

    # Print summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)
    pass_rate = (passed / total * 100) if total > 0 else 0

    print(f"Total Tests: {total}")
    print(f"{colored(f'Passed: {passed}', 'GREEN')}")
    print(f"{colored(f'Failed: {total - passed}', 'RED')}")
    print(f"Pass Rate: {pass_rate:.1f}%\n")

    if passed == total:
        print(colored("🎉 ALL TESTS PASSED! 🎉", "GREEN"))
        print(colored("\nThe Adaptive Questions API is fully functional and ready for use!", "GREEN"))
    else:
        print(colored("⚠️  SOME TESTS FAILED", "RED"))
        print(colored("\nFailed tests:", "RED"))
        for test_name, success in test_results:
            if not success:
                print(f"  - {test_name}")

    print(colored("\n" + "="*80, "BOLD"))

    return pass_rate == 100.0


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(colored("\n\n⚠️  Tests interrupted by user", "YELLOW"))
        exit(1)
    except Exception as e:
        print(colored(f"\n\n❌ Unexpected error: {str(e)}", "RED"))
        import traceback
        traceback.print_exc()
        exit(1)
