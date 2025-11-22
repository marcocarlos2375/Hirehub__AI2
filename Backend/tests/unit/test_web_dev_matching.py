"""
Test if HTML, CSS, JS match with "web development" requirement.
"""

import sys
sys.path.insert(0, '/app')

from core.embeddings import calculate_skills_similarity, get_embedding, calculate_cosine_similarity

print("=" * 80)
print("WEB DEVELOPMENT MATCHING TEST")
print("=" * 80)

# Test 1: Skills similarity calculation
print("\n1. FULL SKILLS SIMILARITY TEST:")
print("-" * 80)

jd_skills = [
    {"skill": "Web Development", "priority": "critical"},
    {"skill": "Frontend Development", "priority": "critical"}
]

cv_skills = ["HTML", "CSS", "JavaScript"]

print(f"JD Requirements: {[s['skill'] for s in jd_skills]}")
print(f"CV Skills: {cv_skills}")

result = calculate_skills_similarity(cv_skills, jd_skills)

print(f"\nResults:")
print(f"  Overall Similarity: {result['overall_similarity']*100:.1f}%")
print(f"  Critical Skills Match: {result['critical_skills_match']*100:.1f}%")
print(f"  Semantic Match Score: {result['semantic_match_score']*100:.1f}%")
print(f"  Missing Critical: {result['missing_critical']}")

if len(result['missing_critical']) == 0:
    print(f"\n✅ SUCCESS: No missing critical skills!")
else:
    print(f"\n❌ ISSUE: Still showing missing critical skills")

# Test 2: Individual embedding similarities
print("\n" + "=" * 80)
print("2. DETAILED EMBEDDING SIMILARITIES:")
print("-" * 80)

test_pairs = [
    ("Web Development", "HTML"),
    ("Web Development", "CSS"),
    ("Web Development", "JavaScript"),
    ("Frontend Development", "HTML"),
    ("Frontend Development", "CSS"),
    ("Frontend Development", "JavaScript"),
]

for jd_term, cv_term in test_pairs:
    jd_emb = get_embedding(jd_term)
    cv_emb = get_embedding(cv_term)
    similarity = calculate_cosine_similarity(jd_emb, cv_emb)

    # Calculate adaptive threshold
    avg_length = (len(jd_term) + len(cv_term)) / 2
    if avg_length < 15:
        threshold = 0.45
    elif avg_length < 50:
        threshold = 0.50
    else:
        threshold = 0.55

    passes = "✅ MATCH" if similarity >= threshold else "❌ NO MATCH"
    print(f"{passes} | {similarity:.3f} (threshold: {threshold:.2f}) | '{jd_term}' vs '{cv_term}'")

# Test 3: Different variations
print("\n" + "=" * 80)
print("3. TESTING VARIATIONS:")
print("-" * 80)

variations = [
    (["HTML", "CSS", "JS"], "Should match"),
    (["HTML5", "CSS3", "JavaScript"], "Should match"),
    (["HTML", "CSS", "JavaScript", "React"], "Should match even better"),
    (["Python", "Django"], "Should NOT match web dev"),
]

for cv_variation, expected in variations:
    result = calculate_skills_similarity(cv_variation, jd_skills)
    print(f"\nCV: {cv_variation}")
    print(f"  Expected: {expected}")
    print(f"  Semantic Score: {result['semantic_match_score']*100:.1f}%")
    print(f"  Missing Critical: {result['missing_critical']}")

print("\n" + "=" * 80)
