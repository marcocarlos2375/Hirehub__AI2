"""
Test caching for /api/parse and /api/parse-cv endpoints.
Verifies that repeated parsing requests hit cache and are dramatically faster.
"""

import requests
import time

API_BASE = 'http://localhost:8001'

# Sample job description
jd_text = """Senior Backend Engineer
Requirements: Python, FastAPI, PostgreSQL, Redis, AWS
5+ years experience required
Build scalable APIs and microservices
Design and implement RESTful APIs
Work with cloud infrastructure"""

# Sample CV
cv_text = """John Doe - Senior Software Engineer
8 years experience
Skills: Python, FastAPI, PostgreSQL, Redis, AWS, Docker, Kubernetes
Built high-traffic APIs serving 1M+ requests/day
Architected microservices platform
Experience with cloud deployment"""

print('=' * 70)
print('PARSING ENDPOINTS CACHE TEST')
print('=' * 70)
print()

# Get initial cache stats
initial_stats = requests.get(f'{API_BASE}/cache/stats').json()
print('[Initial Cache Stats]')
print(f'  Total requests: {initial_stats["total_requests"]}')
print(f'  Misses: {initial_stats["misses"]}')
print(f'  L1 hits: {initial_stats["l1_hits"]}')
print(f'  L2 hits (Redis): {initial_stats["l2_hits"]}')
print()

# ===== Test /api/parse (Job Description Parsing) =====
print('=' * 70)
print('TEST 1: /api/parse (Job Description Parsing)')
print('=' * 70)
print()

# First JD parse (should miss cache)
print('[Request 1] Parse JD (first time - should miss cache)...')
start = time.time()
jd_resp1 = requests.post(f'{API_BASE}/api/parse', json={
    'job_description': jd_text,
    'language': 'english'
})
time1 = time.time() - start
jd1 = jd_resp1.json()

print(f'  Status: {"✅ SUCCESS" if jd1["success"] else "❌ FAILED"}')
print(f'  Time: {time1:.3f}s')
print(f'  Model: {jd1["model"]}')
print(f'  Skills extracted: {len(jd1["data"].get("hard_skills", []))} hard skills')
print()

# Second JD parse (same text - should hit cache)
print('[Request 2] Parse SAME JD (should hit cache)...')
start = time.time()
jd_resp2 = requests.post(f'{API_BASE}/api/parse', json={
    'job_description': jd_text,
    'language': 'english'
})
time2 = time.time() - start
jd2 = jd_resp2.json()

print(f'  Status: {"✅ SUCCESS" if jd2["success"] else "❌ FAILED"}')
print(f'  Time: {time2:.3f}s')
print(f'  Speedup: {time1/time2:.0f}x faster!')
print(f'  Cache hit: {"✅ YES" if time2 < 0.1 else "❌ NO"}')
print()

# Third JD parse (same text - should hit L1 cache now)
print('[Request 3] Parse SAME JD again (should hit L1 cache)...')
start = time.time()
jd_resp3 = requests.post(f'{API_BASE}/api/parse', json={
    'job_description': jd_text,
    'language': 'english'
})
time3 = time.time() - start
jd3 = jd_resp3.json()

print(f'  Status: {"✅ SUCCESS" if jd3["success"] else "❌ FAILED"}')
print(f'  Time: {time3:.3f}s')
print(f'  Speedup: {time1/time3:.0f}x faster!')
print()

# ===== Test /api/parse-cv (CV Parsing) =====
print('=' * 70)
print('TEST 2: /api/parse-cv (CV Parsing)')
print('=' * 70)
print()

# First CV parse (should miss cache)
print('[Request 1] Parse CV (first time - should miss cache)...')
start = time.time()
cv_resp1 = requests.post(f'{API_BASE}/api/parse-cv', json={
    'resume_text': cv_text,
    'language': 'english'
})
time4 = time.time() - start
cv1 = cv_resp1.json()

print(f'  Status: {"✅ SUCCESS" if cv1["success"] else "❌ FAILED"}')
print(f'  Time: {time4:.3f}s')
print(f'  Model: {cv1["model"]}')
print(f'  Skills extracted: {len(cv1["data"].get("hard_skills", []))} hard skills')
print()

# Second CV parse (same text - should hit cache)
print('[Request 2] Parse SAME CV (should hit cache)...')
start = time.time()
cv_resp2 = requests.post(f'{API_BASE}/api/parse-cv', json={
    'resume_text': cv_text,
    'language': 'english'
})
time5 = time.time() - start
cv2 = cv_resp2.json()

print(f'  Status: {"✅ SUCCESS" if cv2["success"] else "❌ FAILED"}')
print(f'  Time: {time5:.3f}s')
print(f'  Speedup: {time4/time5:.0f}x faster!')
print(f'  Cache hit: {"✅ YES" if time5 < 0.1 else "❌ NO"}')
print()

# Third CV parse (same text - should hit L1 cache)
print('[Request 3] Parse SAME CV again (should hit L1 cache)...')
start = time.time()
cv_resp3 = requests.post(f'{API_BASE}/api/parse-cv', json={
    'resume_text': cv_text,
    'language': 'english'
})
time6 = time.time() - start
cv3 = cv_resp3.json()

print(f'  Status: {"✅ SUCCESS" if cv3["success"] else "❌ FAILED"}')
print(f'  Time: {time6:.3f}s')
print(f'  Speedup: {time4/time6:.0f}x faster!')
print()

# ===== Final Cache Stats =====
print('=' * 70)
print('CACHE STATISTICS')
print('=' * 70)

final_stats = requests.get(f'{API_BASE}/cache/stats').json()
print(f'Total requests: {final_stats["total_requests"]}')
print(f'Cache misses: {final_stats["misses"]}')
print(f'L1 hits (in-memory): {final_stats["l1_hits"]}')
print(f'L2 hits (Redis): {final_stats["l2_hits"]}')
print(f'Hit rate: {final_stats["hit_rate"]}%')
print()

# ===== Summary =====
print('=' * 70)
print('TEST RESULTS SUMMARY')
print('=' * 70)
print()
print('JD Parsing (/api/parse):')
print(f'  First request:  {time1:.3f}s (cache miss)')
print(f'  Second request: {time2:.3f}s ({time1/time2:.0f}x faster - Redis hit)')
print(f'  Third request:  {time3:.3f}s ({time1/time3:.0f}x faster - L1 hit)')
print()
print('CV Parsing (/api/parse-cv):')
print(f'  First request:  {time4:.3f}s (cache miss)')
print(f'  Second request: {time5:.3f}s ({time4/time5:.0f}x faster - Redis hit)')
print(f'  Third request:  {time6:.3f}s ({time4/time6:.0f}x faster - L1 hit)')
print()

# Determine pass/fail
jd_cache_working = time2 < time1 / 10  # At least 10x faster
cv_cache_working = time5 < time4 / 10  # At least 10x faster
data_consistent = (jd1["data"] == jd2["data"] == jd3["data"] and
                   cv1["data"] == cv2["data"] == cv3["data"])

print('Overall Results:')
print(f'  ✅ JD Cache: {"WORKING" if jd_cache_working else "NOT WORKING"}')
print(f'  ✅ CV Cache: {"WORKING" if cv_cache_working else "NOT WORKING"}')
print(f'  ✅ Data Consistency: {"PASS" if data_consistent else "FAIL"}')
print(f'  ✅ Cache Hit Rate: {final_stats["hit_rate"]}%')
print()

if jd_cache_working and cv_cache_working and data_consistent:
    print('🎉 ALL TESTS PASSED! Parsing endpoints are properly cached.')
else:
    print('⚠️  SOME TESTS FAILED - Check results above')
print()
