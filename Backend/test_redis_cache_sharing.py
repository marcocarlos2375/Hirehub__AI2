"""
Test Redis cache sharing across multiple requests.
Simulates multiple users accessing the API and verifies they share the same cache.
"""

import requests
import time

API_BASE = 'http://localhost:8001'

# Sample data
jd_text = """Senior Backend Engineer
Requirements: Python, FastAPI, PostgreSQL, Redis, AWS
5+ years experience required
Build scalable APIs and microservices"""

cv_text = """John Doe - Senior Software Engineer
8 years experience
Skills: Python, FastAPI, PostgreSQL, Redis, AWS, Docker
Built high-traffic APIs serving 1M+ requests/day"""

print('=' * 70)
print('REDIS CACHE SHARING TEST')
print('=' * 70)
print()

# Parse documents once
print('[Step 1] Parsing documents...')
jd_resp = requests.post(f'{API_BASE}/api/parse', json={
    'job_description': jd_text,
    'language': 'english'
})
cv_resp = requests.post(f'{API_BASE}/api/parse-cv', json={
    'cv_text': cv_text,
    'language': 'english'
})

jd_data = jd_resp.json()
cv_data = cv_resp.json()
print('  ✓ Documents parsed')
print()

# User 1: First request (builds cache)
print('[Step 2] User 1 makes request (builds Redis cache)...')
start = time.time()
r1 = requests.post(f'{API_BASE}/api/calculate-score', json={
    'parsed_cv': cv_data,
    'parsed_jd': jd_data,
    'language': 'english'
})
time1 = time.time() - start
score1 = r1.json()

print(f'  Time: {time1:.3f}s')
print(f'  Score: {score1["overall_score"]}/100')
print(f'  Result stored in Redis ✓')
print()

# Check cache stats
stats = requests.get(f'{API_BASE}/cache/stats').json()
print(f'  Cache stats after User 1:')
print(f'    Total requests: {stats["total_requests"]}')
print(f'    Misses: {stats["misses"]}')
print(f'    L1 hits: {stats["l1_hits"]}')
print(f'    L2 hits (Redis): {stats["l2_hits"]}')
print()

# User 2: Same request (should hit Redis cache)
print('[Step 3] User 2 makes SAME request (should hit Redis)...')
start = time.time()
r2 = requests.post(f'{API_BASE}/api/calculate-score', json={
    'parsed_cv': cv_data,
    'parsed_jd': jd_data,
    'language': 'english'
})
time2 = time.time() - start
score2 = r2.json()

print(f'  Time: {time2:.3f}s')
print(f'  Score: {score2["overall_score"]}/100')
print(f'  Speedup: {time1/time2:.1f}x faster than User 1!')
print()

# Check cache stats again
stats = requests.get(f'{API_BASE}/cache/stats').json()
print(f'  Cache stats after User 2:')
print(f'    Total requests: {stats["total_requests"]}')
print(f'    Misses: {stats["misses"]}')
print(f'    L1 hits: {stats["l1_hits"]}')
print(f'    L2 hits (Redis): {stats["l2_hits"]}')
print()

# User 3: Same request again (should be instant from L1 cache now)
print('[Step 4] User 3 makes SAME request (should hit L1 cache)...')
start = time.time()
r3 = requests.post(f'{API_BASE}/api/calculate-score', json={
    'parsed_cv': cv_data,
    'parsed_jd': jd_data,
    'language': 'english'
})
time3 = time.time() - start
score3 = r3.json()

print(f'  Time: {time3:.3f}s')
print(f'  Score: {score3["overall_score"]}/100')
print(f'  Speedup: {time1/time3:.1f}x faster than User 1!')
print()

# Final cache stats
stats = requests.get(f'{API_BASE}/cache/stats').json()
print(f'  Cache stats after User 3:')
print(f'    Total requests: {stats["total_requests"]}')
print(f'    Misses: {stats["misses"]}')
print(f'    L1 hits: {stats["l1_hits"]}')
print(f'    L2 hits (Redis): {stats["l2_hits"]}')
print(f'    Hit rate: {stats["hit_rate"]}%')
print()

# Summary
print('=' * 70)
print('TEST RESULTS')
print('=' * 70)
print(f'User 1 (cache miss):     {time1:.3f}s - Builds Redis cache')
print(f'User 2 (Redis hit):      {time2:.3f}s - {time1/time2:.1f}x faster')
print(f'User 3 (L1 + Redis hit): {time3:.3f}s - {time1/time3:.1f}x faster')
print()
print(f'✅ Cache Hit Rate: {stats["hit_rate"]}%')
print(f'✅ Redis Sharing: {"WORKING" if time2 < time1/10 else "NOT WORKING"}')
print(f'✅ Score Consistency: {"PASS" if score1["overall_score"] == score2["overall_score"] == score3["overall_score"] else "FAIL"}')
print()
