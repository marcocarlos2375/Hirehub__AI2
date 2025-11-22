"""
Test cross-language skill matching (German JD, English CV).
This tests the fix for semantic matching in missing_critical calculation.
"""

import sys
sys.path.insert(0, '/app')

from core.embeddings import calculate_skills_similarity

print("=" * 80)
print("CROSS-LANGUAGE SKILL MATCHING TEST")
print("=" * 80)

# Simulate German JD with critical skills
print("\n1. GERMAN JD CRITICAL SKILLS:")
jd_skills_german = [
    {"skill": "Webentwicklung", "priority": "critical"},  # Web development
    {"skill": "Frontend-Entwicklung", "priority": "critical"},  # Frontend development
    {"skill": "Python", "priority": "critical"},
    {"skill": "React", "priority": "important"}
]

print("JD Skills (German):")
for skill in jd_skills_german:
    print(f"  - {skill['skill']} ({skill['priority']})")

# Simulate English CV with frontend skills
print("\n2. ENGLISH CV SKILLS:")
cv_skills_english = [
    "Vue.js",
    "ReactJS",
    "HTML5",
    "CSS3",
    "JavaScript",
    "PHP 7",
    "Python",
    "WordPress",
    "Shopware"
]

print("CV Skills (English):")
for skill in cv_skills_english:
    print(f"  - {skill}")

# Calculate similarity
print("\n3. CALCULATING SIMILARITY...")
result = calculate_skills_similarity(cv_skills_english, jd_skills_german)

print("\n4. RESULTS:")
print(f"Overall Similarity: {result['overall_similarity']*100:.1f}%")
print(f"Critical Skills Match: {result['critical_skills_match']*100:.1f}%")
print(f"Exact Match Score: {result['exact_match_score']*100:.1f}%")
print(f"Fuzzy Match Score: {result['fuzzy_match_score']*100:.1f}%")
print(f"Semantic Match Score: {result['semantic_match_score']*100:.1f}%")
print(f"\nMatched Skills (exact): {result['matched_skills']}")
print(f"Missing Critical Skills: {result['missing_critical']}")

print("\n" + "=" * 80)
print("EXPECTED RESULTS:")
print("- 'Webentwicklung' should NOT be in missing_critical")
print("  (CV has Vue.js, ReactJS, HTML5, CSS3, JavaScript - all web dev)")
print("- 'Frontend-Entwicklung' should NOT be in missing_critical")
print("  (CV has Vue.js, ReactJS, HTML5, CSS3 - all frontend)")
print("- 'Python' should NOT be in missing_critical (exact match)")
print("- Missing critical should be EMPTY or nearly empty")
print("=" * 80)
