"""
Test script for detailed gap analysis aligned with pipeline.md format.
Demonstrates categorized gaps, weighted scoring, strengths, and viability assessment.
"""

import json
import requests
import time

# API endpoint (from inside Docker container)
API_URL = "http://localhost:8000/api/calculate-score"

# Sample CV data (from earlier test)
sample_cv = {
    "personal_info": {
        "name": "John Doe",
        "email": "john@example.com"
    },
    "professional_summary": "Senior Software Engineer with 8 years of experience",
    "technical_skills": [
        "Python",
        "JavaScript",
        "React",
        "AWS",
        "Docker",
        "PostgreSQL",
        "REST APIs",
        "Git",
        "CI/CD",
        "TDD",
        "Microservices",
        "Redis",
        "Kubernetes"
    ],
    "tools": ["VS Code", "Postman", "Jenkins"],
    "soft_skills": [
        "Team collaboration",
        "Problem solving",
        "Technical leadership"
    ],
    "work_experience": [
        {
            "role": "Senior Software Engineer",
            "company": "Tech Corp",
            "start_date": "2020",
            "end_date": "Present",
            "duration": "4 years",
            "achievements": [
                "Built scalable microservices handling 1M+ requests/day",
                "Led team of 5 engineers in cloud migration project",
                "Reduced API latency by 60% through optimization",
                "Implemented CI/CD pipeline reducing deployment time by 80%"
            ]
        },
        {
            "role": "Software Engineer",
            "company": "StartupXYZ",
            "start_date": "2016",
            "end_date": "2020",
            "duration": "4 years",
            "achievements": [
                "Developed REST APIs using Python Flask",
                "Integrated payment processing system",
                "Built automated testing framework"
            ]
        }
    ],
    "education": [
        {
            "degree": "B.S. Computer Science",
            "institution": "University of Technology",
            "graduation_date": "2016"
        }
    ]
}

# Sample JD data (modified to create clear gaps)
sample_jd = {
    "company_name": "AI Startup Inc",
    "position_title": "Senior AI/ML Engineer",
    "location": "San Francisco, CA",
    "work_mode": "onsite",
    "salary_range": "$180,000 - $250,000",
    "experience_years_required": 10,
    "experience_level": "senior",
    "hard_skills_required": [
        {"skill": "Python", "priority": "critical"},
        {"skill": "Machine Learning", "priority": "critical"},
        {"skill": "TensorFlow", "priority": "critical"},
        {"skill": "PyTorch", "priority": "critical"},
        {"skill": "NLP", "priority": "important"},
        {"skill": "Computer Vision", "priority": "important"},
        {"skill": "AWS", "priority": "important"},
        {"skill": "Docker", "priority": "important"},
        {"skill": "Kubernetes", "priority": "important"},
        {"skill": "MLOps", "priority": "important"},
        {"skill": "LLMs", "priority": "critical"},
        {"skill": "Vector Databases", "priority": "nice"},
        {"skill": "Rust", "priority": "nice"}
    ],
    "soft_skills_required": [
        "Strong communication skills for explaining complex ML concepts",
        "Ability to work in fast-paced startup environment",
        "Research mindset and continuous learning",
        "Collaboration with cross-functional teams",
        "Leadership and mentoring"
    ],
    "responsibilities": [
        "Design and implement state-of-the-art ML models for production",
        "Build and deploy LLM-based applications",
        "Optimize model performance and inference speed",
        "Collaborate with product team on AI feature development",
        "Conduct ML research and experiments",
        "Mentor junior ML engineers",
        "Establish ML best practices and infrastructure",
        "Present technical findings to leadership"
    ],
    "tech_stack": [
        "Python",
        "TensorFlow",
        "PyTorch",
        "Transformers",
        "AWS SageMaker",
        "Docker",
        "Kubernetes",
        "MLflow"
    ],
    "domain_expertise": {
        "industry": ["Artificial Intelligence", "SaaS", "Enterprise Software"],
        "specific_knowledge": [
            "Large Language Models (LLMs)",
            "Generative AI",
            "ML in production",
            "Model optimization",
            "AI safety and alignment"
        ]
    }
}


def print_header(text, char="="):
    """Print formatted header"""
    print(f"\n{char * 80}")
    print(f"  {text}")
    print(f"{char * 80}\n")


def print_gaps_section(gaps, category_name, icon):
    """Print formatted gaps section"""
    print(f"\n{icon} {category_name.upper()} GAPS (Count: {len(gaps)})")
    print("─" * 80)

    if not gaps:
        print("  ✅ No gaps in this category")
        return

    for i, gap in enumerate(gaps, 1):
        print(f"\n{i}. {gap['title']}")
        print(f"   Current:   {gap['current']}")
        print(f"   Required:  {gap['required']}")
        print(f"   Impact:    {gap['impact']}")
        print(f"   Severity:  {gap['severity']}")
        if gap.get('timeframe_to_address'):
            print(f"   Timeline:  {gap['timeframe_to_address']}")
        print(f"   Can address: {gap['addressability']}")
        print(f"   → {gap['description']}")


def test_detailed_gap_analysis():
    """Test the detailed gap analysis endpoint"""

    print_header("🚀 DETAILED GAP ANALYSIS TEST (Pipeline.md Format)")

    print("📋 Test Configuration:")
    print(f"  Candidate: {sample_cv['personal_info']['name']}")
    print(f"  Experience: 8 years ({len(sample_cv['technical_skills'])} skills)")
    print(f"  Position: {sample_jd['position_title']} at {sample_jd['company_name']}")
    print(f"  Required: {sample_jd['experience_years_required']}+ years")
    print(f"  Location: {sample_jd['location']} ({sample_jd['work_mode']})")

    # Make API request
    print("\n🔄 Sending request to API...")
    start_time = time.time()

    try:
        response = requests.post(
            API_URL,
            json={
                "parsed_cv": sample_cv,
                "parsed_jd": sample_jd,
                "language": "english"
            },
            timeout=120
        )

        elapsed = time.time() - start_time

        if response.status_code != 200:
            print(f"\n❌ Error: HTTP {response.status_code}")
            print(response.text)
            return

        result = response.json()

        print(f"✅ Response received in {elapsed:.2f}s")

        # Display results in pipeline.md format
        print_header("📊 OVERALL ASSESSMENT")

        print(f"  Overall Score: {result['overall_score']}/100")
        print(f"  Status: {result['overall_status']}")
        print(f"  Processing Time: {result['time_seconds']:.2f}s")
        print(f"  Model: {result['model']}")

        # Category Scores
        print_header("📈 CATEGORY BREAKDOWN", "-")

        category_scores = result.get('category_scores', {})
        total_weight = 0

        for category, details in category_scores.items():
            score = details['score']
            weight = details['weight']
            status = details['status']
            weighted_contribution = score * weight
            total_weight += weight

            category_display = category.replace('_', ' ').title()
            print(f"  {category_display:.<35} {score:>3}/100  ({weight:.0%})  [{status}]")
            print(f"    → Weighted contribution: {weighted_contribution:.1f} points")

        print(f"\n  Total weight: {total_weight:.2%}")

        # Gaps Analysis
        print_header("🚨 GAP ANALYSIS")

        gaps = result.get('gaps', {})

        print_gaps_section(gaps.get('critical', []), "CRITICAL", "🚨")
        print_gaps_section(gaps.get('important', []), "IMPORTANT", "⚠️ ")
        print_gaps_section(gaps.get('nice_to_have', []), "NICE-TO-HAVE", "💡")
        print_gaps_section(gaps.get('logistical', []), "LOGISTICAL", "🚧")

        # Gap Summary
        total_gaps = (len(gaps.get('critical', [])) +
                     len(gaps.get('important', [])) +
                     len(gaps.get('nice_to_have', [])) +
                     len(gaps.get('logistical', [])))

        print(f"\n📊 Gap Summary:")
        print(f"   Total Gaps Identified: {total_gaps}")
        print(f"   • Critical: {len(gaps.get('critical', []))}")
        print(f"   • Important: {len(gaps.get('important', []))}")
        print(f"   • Nice-to-have: {len(gaps.get('nice_to_have', []))}")
        print(f"   • Logistical: {len(gaps.get('logistical', []))}")

        # Strengths
        print_header("✨ STRENGTHS")

        strengths = result.get('strengths', [])
        for i, strength in enumerate(strengths, 1):
            print(f"{i}. {strength['title']}")
            print(f"   {strength['description']}")
            print(f"   Evidence: {strength['evidence']}\n")

        # Application Viability
        print_header("🎯 APPLICATION VIABILITY")

        viability = result.get('application_viability', {})
        print(f"  Current Likelihood: {viability.get('current_likelihood', 'Unknown')}")
        print(f"\n  Key Blockers:")
        for blocker in viability.get('key_blockers', []):
            print(f"    • {blocker}")

        # Similarity Metrics
        print_header("📐 SIMILARITY METRICS", "-")

        metrics = result.get('similarity_metrics', {})
        print(f"  Overall Embedding Similarity: {metrics.get('overall_embedding_similarity', 0):.3f}")
        print(f"  Skills (Hybrid):              {metrics.get('skills_cosine_similarity', 0):.3f}")
        print(f"    ├─ Exact Match:             {metrics.get('exact_keyword_match', 0):.3f}")
        print(f"    ├─ Fuzzy Match:             {metrics.get('fuzzy_keyword_match', 0):.3f}")
        print(f"    └─ Semantic Match:          {metrics.get('semantic_skills_match', 0):.3f}")
        print(f"  Experience:                   {metrics.get('experience_cosine_similarity', 0):.3f}")
        print(f"  Experience (Weighted):        {metrics.get('experience_weighted_similarity', 0):.3f}")

        # Cache Stats
        if 'cache_stats' in metrics:
            cache = metrics['cache_stats']
            print(f"\n  Cache Performance:")
            print(f"    Hit Rate: {cache.get('hit_rate', 0):.1f}%")
            print(f"    L1 Hits: {cache.get('l1_hits', 0)}")
            print(f"    Total Requests: {cache.get('total_requests', 0)}")

        # Save detailed JSON
        print_header("💾 SAVING DETAILED OUTPUT")

        output_file = "detailed_gap_analysis_result.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"  ✅ Full response saved to: {output_file}")

        print("\n" + "=" * 80)
        print("  ✅ Test completed successfully!")
        print("=" * 80 + "\n")

    except requests.exceptions.Timeout:
        print(f"\n❌ Request timed out after 120 seconds")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_detailed_gap_analysis()
