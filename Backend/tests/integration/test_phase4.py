"""
Test script for Phase 4 endpoints
Run with: python test_phase4.py
"""

import requests
import json

API_BASE = "http://localhost:8000"

# Sample data (minimal for testing)
sample_cv = {
    "personal_info": {"name": "Test Candidate", "email": "test@example.com"},
    "technical_skills": ["Python", "JavaScript", "React"],
    "work_experience": [{
        "role": "Software Engineer",
        "company": "Tech Corp",
        "duration": "2 years",
        "achievements": ["Built web apps"]
    }],
    "education": [{
        "degree": "BS Computer Science",
        "institution": "University",
        "graduation_date": "2020"
    }],
    "projects": [],
    "certifications": [],
    "languages": []
}

sample_jd = {
    "company_name": "Startup Inc",
    "position_title": "Full Stack Developer",
    "location": "San Francisco",
    "experience_years_required": 5,
    "hard_skills_required": [
        {"skill": "Next.js", "priority": "required"},
        {"skill": "AI/ML", "priority": "required"}
    ],
    "tech_stack": ["Next.js", "React", "Node.js", "AI"],
    "responsibilities": ["Build features", "Work with AI"],
    "domain_expertise": {
        "industry": ["Tech", "AI"],
        "specific_knowledge": ["LLMs", "RAG"]
    }
}

sample_score_result = {
    "success": True,
    "overall_score": 65,
    "category_scores": {
        "skills_match": 70,
        "experience": 60
    },
    "gaps": {
        "critical": [
            {
                "title": "Next.js Advanced Features",
                "description": "Missing Next.js SSR/SSG experience",
                "impact": "-15%",
                "severity": "critical",
                "category": "skills"
            }
        ],
        "important": [
            {
                "title": "AI/ML Experience",
                "description": "No AI/ML background listed",
                "impact": "-10%",
                "severity": "important",
                "category": "domain"
            }
        ],
        "nice_to_have": []
    },
    "strengths": ["JavaScript", "React"],
    "time_seconds": 2.5,
    "model": "test"
}

def test_generate_questions():
    """Test /api/generate-questions endpoint"""
    print("\n🧪 Testing /api/generate-questions...")

    payload = {
        "parsed_cv": sample_cv,
        "parsed_jd": sample_jd,
        "score_result": sample_score_result,
        "language": "english"
    }

    try:
        response = requests.post(
            f"{API_BASE}/api/generate-questions",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Generated {data['total_questions']} questions")
            print(f"   - Critical: {data['critical_count']}")
            print(f"   - High: {data['high_count']}")
            print(f"   - Medium: {data['medium_count']}")
            print(f"   - RAG context used: {data['rag_context_used']}")
            print(f"   - Time: {data['time_seconds']}s")
            print(f"\n📋 First question:")
            if data['questions']:
                q = data['questions'][0]
                print(f"   {q['number']}. [{q['priority']}] {q['title']}")
                print(f"   Impact: {q['impact']}")
                print(f"   Question: {q['question_text'][:100]}...")
            return data
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_transcribe_audio():
    """Test /api/transcribe-audio endpoint"""
    print("\n🧪 Testing /api/transcribe-audio...")
    print("⚠️  Skipping - requires actual audio file")
    print("   To test: upload a .webm/.mp3 file via frontend")
    return None

def test_submit_answers(questions_data):
    """Test /api/submit-answers endpoint"""
    print("\n🧪 Testing /api/submit-answers...")

    if not questions_data or not questions_data.get('questions'):
        print("❌ Skipping - no questions available")
        return None

    # Create sample answers
    answers = []
    for q in questions_data['questions'][:2]:  # Answer first 2 questions
        answers.append({
            "question_id": q['id'],
            "answer_text": f"Yes, I have experience with {q['title']}. I worked on a side project using these technologies.",
            "answer_type": "text"
        })

    payload = {
        "parsed_cv": sample_cv,
        "parsed_jd": sample_jd,
        "questions": questions_data['questions'],
        "answers": answers,
        "original_score": 65,
        "language": "english"
    }

    try:
        response = requests.post(
            f"{API_BASE}/api/submit-answers",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"   - Updated score: {data['updated_score']}")
            print(f"   - Score improvement: +{data['score_improvement']}")
            print(f"   - Time: {data['time_seconds']}s")
            if data['uncovered_experiences']:
                print(f"\n💎 Uncovered experiences:")
                for exp in data['uncovered_experiences']:
                    print(f"   - {exp}")
            return data
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("=" * 70)
    print("🚀 Phase 4 Endpoint Testing")
    print("=" * 70)

    # Test 1: Generate questions
    questions_data = test_generate_questions()

    # Test 2: Transcribe audio (manual test)
    test_transcribe_audio()

    # Test 3: Submit answers
    if questions_data:
        test_submit_answers(questions_data)

    print("\n" + "=" * 70)
    print("✨ Testing complete!")
    print("=" * 70)
    print("\n📌 Next steps:")
    print("   1. Go to http://localhost:3001")
    print("   2. Upload a real JD and CV")
    print("   3. Wait for Phase 3 to complete (score calculation)")
    print("   4. Phase 4 will auto-start and generate questions")
    print("   5. Answer questions using text or voice")
    print("   6. Submit and see updated score!")
    print()

if __name__ == "__main__":
    main()
