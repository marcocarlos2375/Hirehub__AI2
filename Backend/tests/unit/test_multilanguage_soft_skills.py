"""
Test multi-language soft skills matching.
"""

import sys
sys.path.insert(0, '/app')

from app.main import calculate_soft_skills_match

print("=" * 80)
print("MULTI-LANGUAGE SOFT SKILLS MATCHING TEST")
print("=" * 80)

# Test English
print("\n1. ENGLISH:")
cv_skills_en = ["problem solving", "team collaboration", "critical thinking"]
jd_skills_en = ["problem-solving mindset", "teamwork and collaboration", "critical thinking"]

score_en = calculate_soft_skills_match(cv_skills_en, jd_skills_en, language='english')
print(f"CV: {cv_skills_en}")
print(f"JD: {jd_skills_en}")
print(f"Score: {score_en}%")

# Test French
print("\n2. FRENCH:")
cv_skills_fr = ["résolution de problèmes", "travail en équipe", "pensée critique"]
jd_skills_fr = ["esprit de résolution de problèmes", "collaboration et travail d'équipe", "pensée critique"]

score_fr = calculate_soft_skills_match(cv_skills_fr, jd_skills_fr, language='french')
print(f"CV: {cv_skills_fr}")
print(f"JD: {jd_skills_fr}")
print(f"Score: {score_fr}%")

# Test German
print("\n3. GERMAN:")
cv_skills_de = ["Problemlösung", "Teamarbeit", "kritisches Denken"]
jd_skills_de = ["Problemlösungskompetenz", "Zusammenarbeit im Team", "kritisches Denken"]

score_de = calculate_soft_skills_match(cv_skills_de, jd_skills_de, language='german')
print(f"CV: {cv_skills_de}")
print(f"JD: {jd_skills_de}")
print(f"Score: {score_de}%")

# Test Spanish
print("\n4. SPANISH:")
cv_skills_es = ["resolución de problemas", "trabajo en equipo", "pensamiento crítico"]
jd_skills_es = ["capacidad de resolución de problemas", "colaboración y trabajo en equipo", "pensamiento crítico"]

score_es = calculate_soft_skills_match(cv_skills_es, jd_skills_es, language='spanish')
print(f"CV: {cv_skills_es}")
print(f"JD: {jd_skills_es}")
print(f"Score: {score_es}%")

print("\n" + "=" * 80)
print("Expected: All languages should show 66-100% match")
print("=" * 80)
