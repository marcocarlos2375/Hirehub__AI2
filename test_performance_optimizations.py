"""
Test performance optimizations for scoring endpoint.
Tests:
1. Cache hit rate (Optimization #1)
2. Conditional AI extraction for high scores (Optimization #3)
3. Overall speedup measurement
"""

import requests
import json
import time

API_BASE = 'http://localhost:8001'

# Test data for HIGH score (>70% - should trigger optimization #3)
high_score_jd = """Senior Backend Engineer
Requirements: Python, FastAPI, AWS, Docker, PostgreSQL, Redis
Experience: 5-8 years
Tech Stack: Python, FastAPI, AWS, PostgreSQL, Redis, Docker"""

high_score_cv = """John Doe - Senior Software Engineer
Skills: Python, FastAPI, AWS, Docker, PostgreSQL, Redis, Kubernetes
Experience: 8 years building scalable APIs and microservices
Strong cloud expertise with AWS, containerization, and API development"""

# Test data for LOW score (<70% - should use full AI analysis)
low_score_jd = """Senior ML Engineer - Computer Vision
Requirements: PyTorch, TensorFlow, CUDA, C++, Computer Vision
Experience: 5+ years in Deep Learning
PhD preferred"""

low_score_cv = """Jane Smith - Junior Web Developer
Skills: HTML, CSS, JavaScript, React
Experience: 1 year building simple websites
Basic knowledge of frontend frameworks"""

print('=' * 60)
print('SCORING PERFORMANCE OPTIMIZATION TESTS')
print('=' * 60)
print()

# Test Case 1: High Score (>70%) - Should use optimized path
print('TEST 1: High Score Match (>70%) - Optimized Path')
print('-' * 60)

# Parse documents
print('Parsing JD and CV...')
jd_resp = requests.post(f'{API_BASE}/api/parse', json={
    'job_description': high_score_jd,
    'language': 'english'
})
jd_data = jd_resp.json()

cv_resp = requests.post(f'{API_BASE}/api/parse-cv', json={
    'cv_text': high_score_cv,
    'language': 'english'
})
cv_data = cv_resp.json()

# First scoring run (no cache)
print('Calculating score (first run - no cache)...')
start = time.time()
score_resp = requests.post(f'{API_BASE}/api/calculate-score', json={
    'parsed_cv': cv_data,
    'parsed_jd': jd_data,
    'language': 'english'
})
time1 = time.time() - start
score1 = score_resp.json()

print(f'  Time: {time1:.3f}s')
print(f'  Score: {score1["overall_score"]}/100')
print(f'  Model: {score1["model"]}')
print(f'  Optimized: {"YES" if "rule-based" in score1["model"] else "NO"}')
print()

# Second scoring run (should be cached)
print('Calculating score (second run - cached)...')
start = time.time()
score_resp2 = requests.post(f'{API_BASE}/api/calculate-score', json={
    'parsed_cv': cv_data,
    'parsed_jd': jd_data,
    'language': 'english'
})
time2 = time.time() - start
score2 = score_resp2.json()

print(f'  Time: {time2:.3f}s')
print(f'  Speedup: {time1/time2:.1f}x faster')
print(f'  Cache hit: {time2 < 0.1}')
print()

# Test Case 2: Low Score (<70%) - Should use full AI analysis
print('TEST 2: Low Score Match (<70%) - Full AI Analysis')
print('-' * 60)

# Parse documents
print('Parsing JD and CV...')
jd_resp_low = requests.post(f'{API_BASE}/api/parse', json={
    'job_description': low_score_jd,
    'language': 'english'
})
jd_data_low = jd_resp_low.json()

cv_resp_low = requests.post(f'{API_BASE}/api/parse-cv', json={
    'cv_text': low_score_cv,
    'language': 'english'
})
cv_data_low = cv_resp_low.json()

# Scoring run
print('Calculating score (no cache)...')
start = time.time()
score_resp_low = requests.post(f'{API_BASE}/api/calculate-score', json={
    'parsed_cv': cv_data_low,
    'parsed_jd': jd_data_low,
    'language': 'english'
})
time_low = time.time() - start
score_low = score_resp_low.json()

print(f'  Time: {time_low:.3f}s')
print(f'  Score: {score_low["overall_score"]}/100')
print(f'  Model: {score_low["model"]}')
print(f'  Full AI used: {"YES" if "gemini" in score_low["model"].lower() else "NO"}')
print()

# Summary
print('=' * 60)
print('PERFORMANCE SUMMARY')
print('=' * 60)
print(f'High score (>70%) first run:  {time1:.3f}s')
print(f'High score (>70%) cached run: {time2:.3f}s')
print(f'Cache speedup:                {((time1 - time2) / time1 * 100):.0f}%')
print()
print(f'Low score (<70%) run:         {time_low:.3f}s')
print()
print('OPTIMIZATIONS VERIFIED:')
print(f'  ✓ Optimization #1 (Caching):     {time2 < 0.1}')
print(f'  ✓ Optimization #3 (Conditional): {score1["overall_score"] > 70 and "rule-based" in score1["model"]}')
print()
