"""
Test example relevance for NLP and Computer Vision questions.
Verifies that examples directly relate to the skill being asked about.
"""

import requests
import json

API_BASE = "http://localhost:8001"

# CV without NLP/CV experience
test_cv = """
John Developer
Backend Engineer

EXPERIENCE:
Senior Backend Engineer | TechCorp | 2020-2024
- Built REST APIs with Python and FastAPI
- Optimized PostgreSQL databases
- Implemented Redis caching
- Deployed with Docker and Kubernetes

SKILLS:
Python, FastAPI, PostgreSQL, Redis, Docker, Kubernetes, AWS
"""

# JD requiring NLP and Computer Vision
test_jd = """
AI/ML Engineer

Requirements:
- Python programming
- REST API development
- Natural Language Processing (NLP)
- Computer Vision
- PostgreSQL
- Docker

Nice-to-have:
- PyTorch
- TensorFlow
"""

def test_example_relevance():
    print("=" * 80)
    print("TESTING: Example Relevance for NLP/Computer Vision")
    print("=" * 80)

    # Parse JD
    jd_response = requests.post(f"{API_BASE}/api/parse", json={"job_description": test_jd, "language": "english"})
    parsed_jd = jd_response.json()
    print("✅ JD parsed")

    # Parse CV
    cv_response = requests.post(f"{API_BASE}/api/parse-cv", json={"resume_text": test_cv, "language": "english"})
    parsed_cv = cv_response.json()
    print("✅ CV parsed")

    # Calculate Score
    score_response = requests.post(f"{API_BASE}/api/calculate-score", json={"parsed_cv": parsed_cv, "parsed_jd": parsed_jd, "language": "english"})
    score_result = score_response.json()
    score = score_result['overall_score']
    print(f"✅ Score: {score:.1f}%")

    # Generate Questions (with cache bypass)
    questions_response = requests.post(
        f"{API_BASE}/api/generate-questions",
        json={
            "parsed_cv": parsed_cv,
            "parsed_jd": parsed_jd,
            "score_result": score_result,
            "language": "english",
            "_bypass": "test_relevance_v1"
        }
    )

    questions = questions_response.json().get('questions', [])
    print(f"✅ Generated {len(questions)} questions\n")

    # Find NLP/CV related questions
    nlp_cv_questions = []
    for q in questions:
        title = q.get('title', '').lower()
        question_text = q.get('question_text', '').lower()
        if 'nlp' in title or 'natural language' in title or 'computer vision' in title or 'nlp' in question_text or 'computer vision' in question_text:
            nlp_cv_questions.append(q)

    print(f"Found {len(nlp_cv_questions)} NLP/Computer Vision questions\n")
    print("=" * 80)

    # Analyze each NLP/CV question
    for q in nlp_cv_questions:
        print(f"\nQuestion {q.get('number')}: {q.get('title')}")
        print(f"Priority: {q.get('priority')}")
        print(f"\nExamples:")

        examples = q.get('examples', [])
        all_relevant = True
        issues = []

        for i, example in enumerate(examples, 1):
            print(f"\n{i}. {example}")

            # Check for NLP-specific terms
            nlp_terms = ['nlp', 'spacy', 'nltk', 'sentiment', 'tokenization', 'named entity', 'ner', 'text classification',
                         'language model', 'bert', 'gpt', 'transformer', 'word embedding', 'topic modeling', 'text analysis',
                         'entity extraction', 'pos tagging', 'lemmatization', 'stemming']

            # Check for CV-specific terms
            cv_terms = ['computer vision', 'opencv', 'image processing', 'face detection', 'object detection', 'yolo',
                       'cnn', 'convolution', 'image classification', 'segmentation', 'bounding box', 'haar cascade',
                       'feature extraction', 'edge detection', 'image recognition', 'ocr', 'qr code', 'barcode',
                       'thumbnail', 'resize', 'crop', 'filter', 'pixel']

            example_lower = example.lower()
            has_nlp = any(term in example_lower for term in nlp_terms)
            has_cv = any(term in example_lower for term in cv_terms)

            # Check for bad patterns
            has_vague = any(phrase in example_lower for phrase in ['could have', 'might have', 'possibly', 'may have'])
            has_wrong_topic = any(topic in example_lower for topic in ['caching', 'database optimization', 'microservices architecture', 'rest api'])
            has_display_only = 'display' in example_lower and not any(cv in example_lower for cv in cv_terms)

            if has_nlp or has_cv:
                print(f"   ✅ Relevant: Uses {'NLP' if has_nlp else 'CV'} specific terms")
            else:
                print(f"   ❌ NOT RELEVANT: No NLP/CV specific terms")
                all_relevant = False
                issues.append(f"Example {i} lacks NLP/CV terminology")

            if has_vague:
                print(f"   ⚠️  Vague: Uses speculative language")
                issues.append(f"Example {i} uses speculative language")

            if has_wrong_topic:
                print(f"   ❌ WRONG TOPIC: About caching/database/REST, not NLP/CV!")
                all_relevant = False
                issues.append(f"Example {i} is about wrong topic entirely")

            if has_display_only:
                print(f"   ⚠️  Weak: Only about displaying, not analyzing")
                issues.append(f"Example {i} only about displaying, not CV analysis")

        print("\n" + "-" * 80)

        if all_relevant and not issues:
            print("✅ ALL EXAMPLES RELEVANT")
        else:
            print("❌ ISSUES FOUND:")
            for issue in issues:
                print(f"   - {issue}")

    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("=" * 80)

    if nlp_cv_questions:
        print(f"Tested {len(nlp_cv_questions)} NLP/Computer Vision questions")
        print("\nExpected improvements:")
        print("✅ Examples should use NLP/CV specific libraries (spaCy, NLTK, OpenCV, etc.)")
        print("✅ Examples should mention actual NLP/CV techniques (sentiment analysis, face detection, etc.)")
        print("✅ No speculative language ('could have', 'might have')")
        print("✅ No completely unrelated topics (caching papers for NLP questions)")
    else:
        print("⚠️  No NLP/Computer Vision questions found")

    print("=" * 80)

if __name__ == "__main__":
    test_example_relevance()
