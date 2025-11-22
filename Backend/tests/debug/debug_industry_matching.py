"""
Debug industry matching with adaptive thresholds.
"""

import sys
sys.path.insert(0, '/app')

from app.main import extract_industries_with_ai, get_adaptive_similarity_threshold
from core.embeddings import get_embedding, calculate_cosine_similarity

print("=" * 80)
print("INDUSTRY MATCHING DEBUG (with adaptive thresholds)")
print("=" * 80)

# Simulate what happens during scoring
jd_company = "TechScale Solutions"
jd_domain_industries = ["SaaS"]  # From parsed JD

cv_companies = ["Tech Corp", "StartupXYZ"]

print("\n1. EXTRACTING INDUSTRIES:")
print("-" * 80)

# JD industries
print(f"\nJD Industries:")
print(f"  From domain_expertise: {jd_domain_industries}")

extracted_from_company = extract_industries_with_ai(jd_company)
print(f"  From company name '{jd_company}': {extracted_from_company}")

# Combine (this is what the code does)
jd_industries = set(jd_domain_industries + extracted_from_company)
print(f"  COMBINED JD industries: {list(jd_industries)}")

# CV industries
print(f"\nCV Industries:")
cv_industries = set()
for company in cv_companies:
    industries = extract_industries_with_ai(company)
    print(f"  From '{company}': {industries}")
    cv_industries.update(industries)

print(f"  COMBINED CV industries: {list(cv_industries)}")

print("\n2. EXACT MATCHING:")
print("-" * 80)
jd_lower = {i.lower() for i in jd_industries}
cv_lower = {i.lower() for i in cv_industries}
exact_matches = jd_lower & cv_lower
print(f"JD: {jd_lower}")
print(f"CV: {cv_lower}")
print(f"Exact matches: {exact_matches}")

if exact_matches:
    print(f"✅ EXACT MATCH FOUND! Score = 100%")
else:
    print(f"❌ No exact matches, proceeding to semantic matching...")

    print("\n3. SEMANTIC MATCHING (with adaptive thresholds):")
    print("-" * 80)

    for jd_ind in jd_industries:
        jd_emb = get_embedding(jd_ind)

        print(f"\nChecking '{jd_ind}':")

        best_similarity = 0.0
        best_cv_ind = ""

        for cv_ind in cv_industries:
            cv_emb = get_embedding(cv_ind)
            similarity = calculate_cosine_similarity(jd_emb, cv_emb)

            print(f"  vs '{cv_ind}': {similarity:.3f}", end="")

            if similarity > best_similarity:
                best_similarity = similarity
                best_cv_ind = cv_ind

        # Calculate adaptive threshold
        threshold = get_adaptive_similarity_threshold(jd_ind, best_cv_ind)
        avg_len = (len(jd_ind) + len(best_cv_ind)) / 2

        print(f"\n  Best match: '{best_cv_ind}' with {best_similarity:.3f}")
        print(f"  Avg length: {avg_len:.1f} chars → Threshold: {threshold:.2f}")

        if best_similarity >= threshold:
            print(f"  ✅ MATCH (similarity {best_similarity:.3f} >= threshold {threshold:.2f})")
        else:
            print(f"  ❌ NO MATCH (similarity {best_similarity:.3f} < threshold {threshold:.2f})")

print("\n" + "=" * 80)
