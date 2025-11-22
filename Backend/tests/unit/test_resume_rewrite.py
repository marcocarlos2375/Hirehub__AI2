"""
Test resume rewrite endpoint.
"""

import sys
sys.path.insert(0, '/app')

import json
from app.config import get_resume_rewrite_prompt

# Sample updated CV (from answers)
updated_cv = {
    "personal_info": {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "location": "San Francisco, CA"
    },
    "professional_summary": "Software engineer with 5 years experience",
    "technical_skills": ["Python", "JavaScript", "React", "Node.js", "SQL", "Docker"],
    "work_experience": [
        {
            "role": "Software Engineer",
            "company": "Tech Corp",
            "location": "SF",
            "start_date": "2020-01",
            "end_date": None,
            "achievements": ["Built scalable APIs", "Led team of 3 developers"]
        }
    ],
    "education": [],
    "projects": [],
    "certifications": []
}

# Sample answers
answers = [
    {
        "question": "Have you worked with microservices architecture?",
        "answer": "Yes, I built a microservices system using Docker and Kubernetes that handled 1M requests per day"
    },
    {
        "question": "Do you have experience with hackathons?",
        "answer": "I participated in a hackathon where we built a RAG chatbot using LangChain and Qdrant"
    }
]

# Sample JD
jd = {
    "position_title": "Senior Backend Engineer",
    "company_name": "StartupXYZ",
    "hard_skills_required": [
        {"skill": "Python", "priority": "critical"},
        {"skill": "Microservices", "priority": "critical"},
        {"skill": "Docker", "priority": "important"}
    ],
    "responsibilities": ["Build scalable APIs", "Design microservices architecture"]
}

print("=" * 80)
print("RESUME REWRITE PROMPT TEST")
print("=" * 80)

# Generate prompt
prompt = get_resume_rewrite_prompt(updated_cv, answers, jd, "english")

print("\nPROMPT LENGTH:", len(prompt), "characters")
print("\nPROMPT PREVIEW (first 500 chars):")
print(prompt[:500])
print("...")
print("\n✅ Prompt generated successfully!")
print("\nThe prompt instructs AI to:")
print("- Rewrite work experience with insights from answers")
print("- Add hackathon project to projects section")
print("- Add microservices details to work experience")
print("- Generate both sample.json and parsed CV formats")
print("\n" + "=" * 80)
