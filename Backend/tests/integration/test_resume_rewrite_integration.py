"""
Test resume rewrite endpoint integration.
"""

import sys
sys.path.insert(0, '/app')

import json
from app.config import get_resume_rewrite_prompt
from formats.toon import to_toon

# Sample updated CV (from answers analysis)
updated_cv = {
    "personal_info": {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "location": "San Francisco, CA",
        "linkedin": "linkedin.com/in/johndoe",
        "github": "github.com/johndoe"
    },
    "professional_summary": "Software engineer with 5 years experience in full-stack development",
    "technical_skills": ["Python", "JavaScript", "React", "Node.js", "SQL", "Docker"],
    "work_experience": [
        {
            "role": "Software Engineer",
            "company": "Tech Corp",
            "location": "SF",
            "start_date": "2020-01",
            "end_date": None,
            "achievements": [
                "Built scalable APIs",
                "Led team of 3 developers on microservices migration handling 1M requests/day"
            ]
        },
        {
            "role": "Junior Developer",
            "company": "StartupXYZ",
            "location": "SF",
            "start_date": "2018-06",
            "end_date": "2019-12",
            "achievements": [
                "Developed frontend features in React",
                "Participated in code reviews"
            ]
        }
    ],
    "education": [
        {
            "degree": "BS Computer Science",
            "institution": "UC Berkeley",
            "location": "Berkeley, CA",
            "graduation_date": "2018-05",
            "gpa": "3.8"
        }
    ],
    "projects": [
        {
            "name": "RAG Chatbot Hackathon",
            "description": "Built a RAG-based chatbot using LangChain and Qdrant",
            "technologies": ["Python", "LangChain", "Qdrant", "FastAPI", "OpenAI"],
            "link": None
        }
    ],
    "certifications": [],
    "languages": [
        {"language": "English", "proficiency": "Native"},
        {"language": "Spanish", "proficiency": "Intermediate"}
    ]
}

# Sample questions and answers
questions = [
    {
        "id": "q1",
        "number": 1,
        "title": "Microservices Experience",
        "priority": "CRITICAL",
        "impact": "High impact on technical skills",
        "question_text": "Have you worked with microservices architecture?",
        "context_why": "Job requires microservices",
        "examples": ["Docker", "Kubernetes", "Service mesh"]
    },
    {
        "id": "q2",
        "number": 2,
        "title": "Hackathon Projects",
        "priority": "HIGH",
        "impact": "Shows initiative",
        "question_text": "Do you have experience with hackathons?",
        "context_why": "Company values innovation",
        "examples": ["AI projects", "Open source"]
    }
]

answers = [
    {
        "question_id": "q1",
        "answer_text": "Yes, I led a team of 3 developers on microservices migration using Docker and Kubernetes that handled 1M requests per day",
        "answer_type": "text"
    },
    {
        "question_id": "q2",
        "answer_text": "I participated in a hackathon where we built a RAG chatbot using LangChain and Qdrant vector database",
        "answer_type": "text"
    }
]

# Sample JD
jd = {
    "position_title": "Senior Backend Engineer",
    "company_name": "StartupXYZ",
    "hard_skills_required": [
        {"skill": "Python", "priority": "critical"},
        {"skill": "Microservices", "priority": "critical"},
        {"skill": "Docker", "priority": "important"},
        {"skill": "Kubernetes", "priority": "important"}
    ],
    "responsibilities": [
        "Build scalable APIs",
        "Design microservices architecture",
        "Lead backend team"
    ]
}

print("=" * 80)
print("RESUME REWRITE INTEGRATION TEST")
print("=" * 80)

# Convert CV and JD to TOON format
cv_toon = to_toon(updated_cv)
jd_toon = to_toon(jd)

print("\n1. UPDATED CV (TOON FORMAT):")
print("-" * 80)
print(cv_toon[:500] + "...")
print(f"Total length: {len(cv_toon)} characters")

print("\n2. JOB DESCRIPTION (TOON FORMAT):")
print("-" * 80)
print(jd_toon[:300] + "...")
print(f"Total length: {len(jd_toon)} characters")

# Match questions with answers
questions_and_answers = []
for question in questions:
    answer = next(
        (a for a in answers if a["question_id"] == question["id"]),
        None
    )
    if answer:
        questions_and_answers.append({
            'question': question["question_text"],
            'answer': answer["answer_text"]
        })

print("\n3. QUESTIONS AND ANSWERS:")
print("-" * 80)
for qa in questions_and_answers:
    print(f"Q: {qa['question']}")
    print(f"A: {qa['answer']}\n")

# Convert Q&A to TOON format
qa_toon = to_toon(questions_and_answers)
print("\n3b. Q&A IN TOON FORMAT:")
print("-" * 80)
print(qa_toon)
print(f"Total length: {len(qa_toon)} characters")

# Generate prompt
prompt = get_resume_rewrite_prompt(
    updated_cv_toon=cv_toon,
    answers=questions_and_answers,
    jd_toon=jd_toon,
    language="english"
)

print("\n4. PROMPT GENERATED:")
print("-" * 80)
print(f"Prompt length: {len(prompt)} characters")
print(f"\nFirst 1000 characters:")
print(prompt[:1000])
print("...")

print("\n5. PROMPT STRUCTURE CHECK:")
print("-" * 80)
print(f"✓ Contains CV in TOON format: {'CURRENT CV (TOON format' in prompt}")
print(f"✓ Contains JD in TOON format: {'JOB REQUIREMENTS (TOON format' in prompt}")
print(f"✓ Contains Q&A: {'ANSWERS PROVIDED BY CANDIDATE' in prompt}")
print(f"✓ Requests sample_format: {'sample_format' in prompt}")
print(f"✓ Requests parsed_format: {'parsed_format' in prompt}")
print(f"✓ Requests enhancements_made: {'enhancements_made' in prompt}")
print(f"✓ Requests JSON output: {'Return ONLY the JSON object' in prompt}")

print("\n6. EXPECTED OUTPUT STRUCTURE:")
print("-" * 80)
print("""
{
  "sample_format": {
    "content": {
      "personalInfo": {...},
      "professionalSummary": "...",
      "employmentHistory": [...],
      "skills": [...],
      "projects": [...],
      ...
    }
  },
  "parsed_format": {
    "personal_info": {...},
    "professional_summary": "...",
    "work_experience": [...],
    "technical_skills": [...],
    "projects": [...],
    ...
  },
  "enhancements_made": [
    "Enhanced work experience with microservices details",
    "Added RAG chatbot hackathon project",
    "Added LangChain, Qdrant to skills",
    ...
  ]
}
""")

print("\n7. TOKEN SAVINGS WITH TOON:")
print("-" * 80)
cv_json = json.dumps(updated_cv)
jd_json = json.dumps(jd)
qa_json = json.dumps(questions_and_answers)
print(f"CV JSON length: {len(cv_json)} chars")
print(f"CV TOON length: {len(cv_toon)} chars")
print(f"CV savings: {len(cv_json) - len(cv_toon)} chars ({((len(cv_json) - len(cv_toon)) / len(cv_json) * 100):.1f}%)")
print(f"\nJD JSON length: {len(jd_json)} chars")
print(f"JD TOON length: {len(jd_toon)} chars")
print(f"JD savings: {len(jd_json) - len(jd_toon)} chars ({((len(jd_json) - len(jd_toon)) / len(jd_json) * 100):.1f}%)")
print(f"\nQ&A JSON length: {len(qa_json)} chars")
print(f"Q&A TOON length: {len(qa_toon)} chars")
print(f"Q&A savings: {len(qa_json) - len(qa_toon)} chars ({((len(qa_json) - len(qa_toon)) / len(qa_json) * 100):.1f}%)")
print(f"\nTOTAL JSON length: {len(cv_json) + len(jd_json) + len(qa_json)} chars")
print(f"TOTAL TOON length: {len(cv_toon) + len(jd_toon) + len(qa_toon)} chars")
total_savings = (len(cv_json) + len(jd_json) + len(qa_json)) - (len(cv_toon) + len(jd_toon) + len(qa_toon))
total_percent = (total_savings / (len(cv_json) + len(jd_json) + len(qa_json))) * 100
print(f"TOTAL savings: {total_savings} chars ({total_percent:.1f}%)")

print("\n" + "=" * 80)
print("✅ Resume rewrite integration test complete!")
print("=" * 80)
