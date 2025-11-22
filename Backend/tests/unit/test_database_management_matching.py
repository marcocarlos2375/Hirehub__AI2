"""
Test that SQL, Doctrine, Firebase match with "Database Management" requirement.
This tests the fix for missing_important skills.
"""

import sys
sys.path.insert(0, '/app')

from core.embeddings import calculate_skills_similarity

print("=" * 80)
print("DATABASE MANAGEMENT MATCHING TEST")
print("=" * 80)

# Test case from user's issue
print("\n1. USER'S CASE:")
print("-" * 80)

jd_skills = [
    {"skill": "Database Management", "priority": "important"},
    {"skill": "PHP", "priority": "critical"},
    {"skill": "Vue.js", "priority": "critical"}
]

cv_skills = [
    "SQL",
    "Doctrine",  # ORM
    "Firebase",  # NoSQL
    "PHP",
    "Vue.js"
]

print(f"JD Requirements: {[s['skill'] + ' (' + s['priority'] + ')' for s in jd_skills]}")
print(f"CV Skills: {cv_skills}")

result = calculate_skills_similarity(cv_skills, jd_skills)

print(f"\nResults:")
print(f"  Overall Similarity: {result['overall_similarity']*100:.1f}%")
print(f"  Critical Skills Match: {result['critical_skills_match']*100:.1f}%")
print(f"  Important Skills Match: {result['important_skills_match']*100:.1f}%")
print(f"  Semantic Match Score: {result['semantic_match_score']*100:.1f}%")
print(f"\n  Missing Critical: {result['missing_critical']}")
print(f"  Missing Important: {result['missing_important']}")

if len(result['missing_important']) == 0:
    print(f"\n✅ SUCCESS: 'Database Management' is NOT in missing_important!")
else:
    print(f"\n❌ ISSUE: Still showing missing important skills")

# Test 2: More specific database skills
print("\n" + "=" * 80)
print("2. ADDITIONAL DATABASE VARIATIONS:")
print("-" * 80)

test_cases = [
    (["SQL", "MySQL", "PostgreSQL"], "Relational databases"),
    (["MongoDB", "Firebase", "DynamoDB"], "NoSQL databases"),
    (["SQL", "Doctrine", "TypeORM"], "Database + ORMs"),
    (["Database Administration", "SQL"], "Admin skills"),
]

for cv_variation, description in test_cases:
    result = calculate_skills_similarity(
        cv_variation,
        [{"skill": "Database Management", "priority": "important"}]
    )
    print(f"\nCV: {cv_variation}")
    print(f"  Description: {description}")
    print(f"  Important Match: {result['important_skills_match']*100:.1f}%")
    print(f"  Missing Important: {result['missing_important']}")

print("\n" + "=" * 80)
print("EXPECTED: All database-related skills should NOT be in missing_important")
print("=" * 80)
