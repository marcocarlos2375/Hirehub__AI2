"""
Debug industry extraction to see what AI extracts from CV companies.
"""

import sys
sys.path.insert(0, '/app')

from app.main import extract_industries_with_ai

# Test CV companies
cv_companies = [
    "Tech Corp",
    "StartupXYZ"
]

# Test JD company
jd_company = "TechScale Solutions"

print("=" * 80)
print("INDUSTRY EXTRACTION DEBUG")
print("=" * 80)

print("\nJD Company:")
jd_industries = extract_industries_with_ai(jd_company)
print(f"  '{jd_company}' → {jd_industries}")

print("\nCV Companies:")
for company in cv_companies:
    industries = extract_industries_with_ai(company)
    print(f"  '{company}' → {industries}")

print("\n" + "=" * 80)
print("Expected: Both should extract 'Technology' or 'Software'")
print("=" * 80)
