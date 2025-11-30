"""
Complete Adaptive Questions Pipeline Test
Demonstrates the entire workflow with weak vs strong answers, AI responses, and timing.
"""
import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8001"

# ANSI color codes
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
RESET = '\033[0m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")

def print_section(text):
    """Print a section divider."""
    print(f"\n{YELLOW}{'─'*80}{RESET}")
    print(f"{YELLOW}{text}{RESET}")
    print(f"{YELLOW}{'─'*80}{RESET}")

def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")

def print_timing(label, duration):
    """Print timing information."""
    print(f"{BLUE}⏱️  {label}: {duration:.2f}s{RESET}")

def format_json(data, indent=2):
    """Format JSON for display."""
    return json.dumps(data, indent=indent)


def test_weak_answer_flow():
    """Test the pipeline with weak, vague answers."""
    print_header("TEST 1: WEAK ANSWER FLOW")

    timings = {}

    # Step 1: Start workflow and generate questions
    print_section("Step 1: Generate Deep Dive Questions")

    start_data = {
        "question_id": "test_weak_flow",
        "question_text": "Do you have AWS Lambda experience?",
        "question_data": {},
        "gap_info": {
            "title": "AWS Lambda",
            "description": "Serverless computing with AWS Lambda for building scalable applications"
        },
        "user_id": "test_user_weak",
        "parsed_cv": {"skills": ["Python", "JavaScript", "APIs"]},
        "parsed_jd": {"required_skills": ["AWS Lambda", "Serverless", "Python", "API Gateway"]},
        "experience_check_response": "yes",
        "language": "english"
    }

    start_time = time.time()
    response = requests.post(f"{API_BASE}/api/adaptive-questions/start", json=start_data)
    timings['question_generation'] = time.time() - start_time

    if response.status_code == 200:
        result = response.json()
        prompts = result.get("deep_dive_prompts", [])

        print_success(f"Generated {len(prompts)} deep dive questions")
        print_timing("Question Generation", timings['question_generation'])

        print(f"\n{BOLD}Generated Questions:{RESET}")
        for i, prompt in enumerate(prompts, 1):
            print(f"\n{BOLD}{i}. {prompt['question']}{RESET}")
            print(f"   Type: {prompt['type']}")
            if prompt.get('options'):
                print(f"   Options: {', '.join(prompt['options'][:3])}...")
    else:
        print(f"{RED}✗ Failed to generate questions: {response.status_code}{RESET}")
        return None

    # Step 2: Submit WEAK answers
    print_section("Step 2: Submit Weak Answers (Vague, Minimal)")

    weak_answers = {
        "context": "Work",
        "duration": "A few months",
        "tools": "Basic stuff",
        "achievement": "Made some functions",
        "metrics": ""
    }

    print(f"{BOLD}Weak Answers Submitted:{RESET}")
    for key, value in weak_answers.items():
        print(f"  • {key}: '{value}'")

    submit_data = {
        "question_id": "test_weak_flow",
        "structured_data": weak_answers
    }

    start_time = time.time()
    response = requests.post(f"{API_BASE}/api/adaptive-questions/submit-inputs", json=submit_data)
    timings['answer_generation'] = time.time() - start_time

    if response.status_code == 200:
        result = response.json()
        quality_score = result.get("quality_score", 0)
        generated_answer = result.get("generated_answer", "")
        improvements = result.get("improvement_suggestions", [])

        print_success("Answer generated and evaluated")
        print_timing("Answer Generation + Evaluation", timings['answer_generation'])

        print(f"\n{BOLD}Quality Score: {quality_score}/10{RESET}")
        if quality_score < 7:
            print(f"{YELLOW}⚠️  Score below threshold - needs improvement{RESET}")

        print(f"\n{BOLD}AI-Generated Answer (From Weak Input):{RESET}")
        print(f"{generated_answer[:300]}...")

        print(f"\n{BOLD}AI Improvement Suggestions:{RESET}")
        for i, suggestion in enumerate(improvements[:3], 1):
            print(f"  {i}. {suggestion.get('issue', 'N/A')}")
            print(f"     → Suggestion: {suggestion.get('suggestion', 'N/A')}")
    else:
        print(f"{RED}✗ Failed to submit answers: {response.status_code}{RESET}")
        return None

    # Step 3: Refine with better data
    print_section("Step 3: Refine Answer with Additional Details")

    refinement_data = {
        "duration_detail": "6 months on production system",
        "specific_tools": "AWS Lambda, API Gateway, DynamoDB",
        "metrics": "Reduced API response time by 30%"
    }

    print(f"{BOLD}Additional Data Provided:{RESET}")
    for key, value in refinement_data.items():
        print(f"  • {key}: '{value}'")

    refine_request = {
        "question_id": "test_weak_flow",
        "additional_data": refinement_data
    }

    start_time = time.time()
    response = requests.post(f"{API_BASE}/api/adaptive-questions/refine-answer", json=refine_request)
    timings['refinement'] = time.time() - start_time

    if response.status_code == 200:
        result = response.json()
        new_score = result.get("quality_score", 0)
        refined_answer = result.get("refined_answer", "")

        print_success("Answer refined and re-evaluated")
        print_timing("Refinement + Re-evaluation", timings['refinement'])

        print(f"\n{BOLD}New Quality Score: {new_score}/10{RESET} (was {quality_score}/10)")
        print(f"\n{BOLD}Refined AI-Generated Answer:{RESET}")
        print(f"{refined_answer[:300]}...")

    # Calculate total time
    timings['total'] = sum(timings.values())

    return {
        'flow': 'weak',
        'timings': timings,
        'initial_score': quality_score,
        'refined_score': new_score if response.status_code == 200 else quality_score,
        'generated_answer': generated_answer,
        'refined_answer': refined_answer if response.status_code == 200 else None
    }


def test_strong_answer_flow():
    """Test the pipeline with strong, detailed answers."""
    print_header("TEST 2: STRONG ANSWER FLOW")

    timings = {}

    # Step 1: Start workflow and generate questions
    print_section("Step 1: Generate Deep Dive Questions")

    start_data = {
        "question_id": "test_strong_flow",
        "question_text": "Do you have AWS Lambda experience?",
        "question_data": {},
        "gap_info": {
            "title": "AWS Lambda",
            "description": "Serverless computing with AWS Lambda for building scalable applications"
        },
        "user_id": "test_user_strong",
        "parsed_cv": {"skills": ["Python", "JavaScript", "APIs", "AWS"]},
        "parsed_jd": {"required_skills": ["AWS Lambda", "Serverless", "Python", "API Gateway"]},
        "experience_check_response": "yes",
        "language": "english"
    }

    start_time = time.time()
    response = requests.post(f"{API_BASE}/api/adaptive-questions/start", json=start_data)
    timings['question_generation'] = time.time() - start_time

    if response.status_code == 200:
        result = response.json()
        prompts = result.get("deep_dive_prompts", [])

        print_success(f"Generated {len(prompts)} deep dive questions")
        print_timing("Question Generation", timings['question_generation'])
    else:
        print(f"{RED}✗ Failed to generate questions: {response.status_code}{RESET}")
        return None

    # Step 2: Submit STRONG answers
    print_section("Step 2: Submit Strong Answers (Detailed, Specific, Metrics)")

    strong_answers = {
        "context": "Professional work - E-commerce platform at TechCorp",
        "duration": "18 months across 3 major projects (Oct 2022 - Mar 2024)",
        "tools": "AWS Lambda (Python 3.9), API Gateway, DynamoDB, Step Functions, CloudWatch, S3, SNS, EventBridge",
        "achievement": "Architected and deployed serverless order processing system handling 50,000 orders daily. Built real-time inventory sync system using Lambda + DynamoDB Streams. Implemented automated email notification system with SES.",
        "metrics": "Reduced infrastructure costs by 40% ($15K/month savings), improved API response time from 2000ms to 300ms (85% improvement), achieved 99.9% uptime, reduced deployment time from 2 hours to 15 minutes with CI/CD"
    }

    print(f"{BOLD}Strong Answers Submitted:{RESET}")
    for key, value in strong_answers.items():
        print(f"  • {key}:")
        print(f"    '{value}'")

    submit_data = {
        "question_id": "test_strong_flow",
        "structured_data": strong_answers
    }

    start_time = time.time()
    response = requests.post(f"{API_BASE}/api/adaptive-questions/submit-inputs", json=submit_data)
    timings['answer_generation'] = time.time() - start_time

    if response.status_code == 200:
        result = response.json()
        quality_score = result.get("quality_score", 0)
        generated_answer = result.get("generated_answer", "")
        final_answer = result.get("final_answer")
        improvements = result.get("improvement_suggestions", [])

        print_success("Answer generated and evaluated")
        print_timing("Answer Generation + Evaluation", timings['answer_generation'])

        print(f"\n{BOLD}Quality Score: {quality_score}/10{RESET}")
        if quality_score >= 7:
            print(f"{GREEN}✓ Score meets threshold - answer accepted!{RESET}")

        print(f"\n{BOLD}AI-Generated Answer (From Strong Input):{RESET}")
        answer_to_show = final_answer if final_answer else generated_answer
        print(f"{answer_to_show}")

        if improvements:
            print(f"\n{BOLD}Minor Improvement Suggestions:{RESET}")
            for i, suggestion in enumerate(improvements[:2], 1):
                print(f"  {i}. {suggestion.get('suggestion', 'N/A')}")
        else:
            print(f"\n{GREEN}✓ No improvements needed - answer is excellent!{RESET}")
    else:
        print(f"{RED}✗ Failed to submit answers: {response.status_code}{RESET}")
        return None

    # Calculate total time
    timings['total'] = sum(timings.values())

    return {
        'flow': 'strong',
        'timings': timings,
        'initial_score': quality_score,
        'generated_answer': generated_answer,
        'final_answer': final_answer
    }


def generate_comparison_report(weak_result, strong_result):
    """Generate a comparison report between weak and strong answer flows."""
    print_header("COMPARISON REPORT: WEAK vs STRONG ANSWERS")

    # Timing Comparison
    print_section("⏱️  Timing Comparison")
    print(f"\n{BOLD}{'Stage':<30} {'Weak Flow':<15} {'Strong Flow':<15}{RESET}")
    print(f"{'-'*60}")
    print(f"Question Generation       {weak_result['timings']['question_generation']:>10.2f}s    {strong_result['timings']['question_generation']:>10.2f}s")
    print(f"Answer Generation         {weak_result['timings']['answer_generation']:>10.2f}s    {strong_result['timings']['answer_generation']:>10.2f}s")
    if 'refinement' in weak_result['timings']:
        print(f"Refinement (weak only)    {weak_result['timings']['refinement']:>10.2f}s    {'N/A':>10}")
    print(f"{'-'*60}")
    print(f"{BOLD}TOTAL TIME                {weak_result['timings']['total']:>10.2f}s    {strong_result['timings']['total']:>10.2f}s{RESET}")

    # Quality Score Comparison
    print_section("📊 Quality Score Comparison")
    print(f"\n{BOLD}Weak Answer Flow:{RESET}")
    print(f"  Initial Score: {weak_result['initial_score']}/10 {RED}(Below threshold){RESET}")
    print(f"  After Refinement: {weak_result['refined_score']}/10")
    print(f"  Improvement: +{weak_result['refined_score'] - weak_result['initial_score']}")

    print(f"\n{BOLD}Strong Answer Flow:{RESET}")
    print(f"  Initial Score: {strong_result['initial_score']}/10 {GREEN}(Accepted!){RESET}")
    print(f"  Status: No refinement needed")

    # Answer Quality Comparison
    print_section("📝 Generated Answer Quality")

    print(f"\n{BOLD}Weak Answer (Initial):{RESET}")
    print(f"{weak_result['generated_answer'][:250]}...")
    print(f"\n{YELLOW}→ Generic, lacks specifics, needs more detail{RESET}")

    print(f"\n{BOLD}Strong Answer:{RESET}")
    answer = strong_result.get('final_answer') or strong_result['generated_answer']
    print(f"{answer[:400]}...")
    print(f"\n{GREEN}→ Detailed, specific metrics, professional language{RESET}")

    # Key Takeaways
    print_section("💡 Key Takeaways")
    print(f"""
{BOLD}1. Input Quality Matters:{RESET}
   Strong answers provide:
   • Specific context (company, project type)
   • Concrete timelines (18 months, 3 projects)
   • Technical details (Lambda, DynamoDB, Step Functions)
   • Quantifiable metrics (40% cost reduction, 85% faster)

{BOLD}2. AI Response Adapts:{RESET}
   • Weak input → Generic output + Improvement suggestions
   • Strong input → Professional output + Immediate acceptance

{BOLD}3. Time Efficiency:{RESET}
   • Strong answers: One pass, faster completion
   • Weak answers: Multiple iterations, refinement needed

{BOLD}4. Quality Scores:{RESET}
   • Threshold: 7/10 for acceptance
   • Weak: {weak_result['initial_score']}/10 → {weak_result['refined_score']}/10 (needs work)
   • Strong: {strong_result['initial_score']}/10 (immediate acceptance)
""")


def main():
    """Run the complete pipeline test."""
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}  ADAPTIVE QUESTIONS PIPELINE - COMPLETE END-TO-END TEST{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Base: {API_BASE}")

    # Test weak answer flow
    weak_result = test_weak_answer_flow()

    time.sleep(2)  # Pause between tests

    # Test strong answer flow
    strong_result = test_strong_answer_flow()

    # Generate comparison report
    if weak_result and strong_result:
        generate_comparison_report(weak_result, strong_result)

    print(f"\n{BOLD}{GREEN}{'='*80}{RESET}")
    print(f"{BOLD}{GREEN}  TEST COMPLETE{RESET}")
    print(f"{BOLD}{GREEN}{'='*80}{RESET}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test interrupted by user.{RESET}")
    except Exception as e:
        print(f"\n\n{RED}Unexpected error: {str(e)}{RESET}")
        import traceback
        traceback.print_exc()
