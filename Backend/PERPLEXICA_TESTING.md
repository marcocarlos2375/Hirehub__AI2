# Perplexica Testing Guide

## Overview

This guide shows you how to test the Perplexica AI-powered search integration with Gemini models.

---

## Method 1: Integration Test Suite (Recommended)

Run the comprehensive test suite that validates all Perplexica functionality:

```bash
cd Backend

# Run tests inside the API container
docker-compose exec api python test_perplexica_simple.py
```

**What it tests:**
- ✅ Health check (Perplexica service availability)
- ✅ Basic AI search (direct Perplexica client)
- ✅ Learning resource discovery (specialized search)
- ✅ Resource matcher integration (full pipeline)
- ✅ Fallback mechanism (SearXNG backup)

**Expected output:**
```
============================================================
PERPLEXICA INTEGRATION TESTS
============================================================

TEST 1: Perplexica Health Check
✓ PASSED: Perplexica service is healthy

TEST 2: Perplexica Basic Search
✓ PASSED: Search returned results
  - Answer length: 4025 chars
  - Sources found: 15

TEST 3: Learning Resource Discovery
✓ PASSED: Learning resources found
  - Skill: React
  - Sources: 10

TEST 4: Resource Matcher with Perplexica
✓ PASSED: Resource matcher executed

TEST 5: Fallback Mechanism
✓ PASSED: Health check correctly fails for invalid URL

============================================================
ALL TESTS PASSED! (5/5)
```

---

## Method 2: Direct API Testing

Test via HTTP requests to your FastAPI endpoints:

### Test Learning Resource Search

```bash
curl -s -X POST 'http://localhost:8001/api/adaptive-questions/get-learning-resources' \
  -H 'Content-Type: application/json' \
  -d '{
    "gap": {
      "title": "React",
      "description": "Frontend framework",
      "severity": "critical"
    },
    "user_level": "beginner",
    "max_days": 10,
    "cost_preference": "free",
    "limit": 5,
    "search_mode": "perplexica"
  }' | python3 -m json.tool
```

**What to look for:**
- `resources` array should contain learning resources
- Each resource should have: `title`, `url`, `provider`, `type`, `difficulty`
- `sources_used` should include "Perplexica" if AI search worked
- If Perplexica fails, it falls back to SearXNG automatically

---

## Method 3: Direct Perplexica Client Testing

Test the Perplexica client directly in Python:

```bash
docker-compose exec api python3
```

Then in the Python shell:

```python
from core.perplexica_client import get_perplexica_client

# Get client
client = get_perplexica_client()

# Test health
print("Health:", client.health_check())

# Test basic search
result = client.search(
    query="Best Python courses for beginners 2025",
    focus_mode="webSearch"
)
print("Answer:", result['answer'][:200])
print("Sources:", len(result['sources']))

# Test learning resource search
result = client.search_learning_resources(
    skill="Docker",
    user_level="intermediate"
)
print("AI Summary:", result['answer'][:200])
print("Sources found:", len(result['sources']))
```

**Expected output:**
```python
Health: True
Answer: Python is a popular programming language suitable for beginners...
Sources: 15
AI Summary: To learn Docker in 2025, there are numerous resources available...
Sources found: 10
```

---

## Method 4: Check Perplexica Logs

Monitor Perplexica activity in real-time:

```bash
# Watch logs
docker-compose logs -f perplexica

# Check for errors
docker-compose logs perplexica | grep -i error

# Check for Gemini provider initialization
docker-compose logs perplexica | grep -i gemini
```

**Good logs:**
```
✓ SearXNG started successfully
✓ Perplexica Ready in 298ms
✓ No "Invalid provider id" errors
✓ No "Invalid Model Selected" errors
```

**Bad logs:**
```
✗ Error in getting search results: Invalid provider id
✗ Error Loading Gemini Chat Model. Invalid Model Selected
```

---

## Method 5: Check Perplexica Configuration

Verify Gemini provider is configured correctly:

```bash
# Check config file
docker-compose exec perplexica cat /home/perplexica/data/config.json | python3 -m json.tool
```

**What to look for:**
```json
{
  "modelProviders": [
    {
      "id": "0b892904-e752-4e89-ab60-484ef8989843",
      "name": "Google Gemini",
      "type": "gemini",
      "chatModels": [],
      "embeddingModels": [],
      "config": {
        "apiKey": "AIzaSy..."  // Your Gemini API key
      }
    }
  ]
}
```

**Key points:**
- ✅ Provider `type` should be `"gemini"`
- ✅ Provider `id` is the UUID used by the Python client
- ✅ `apiKey` should be your actual Gemini API key
- ✅ `chatModels` and `embeddingModels` can be empty (models are validated at runtime)

---

## Method 6: Test via Frontend

If you have the frontend running:

1. Navigate to the adaptive questions flow
2. Select "Willing to Learn" for a skill gap
3. The system should fetch learning resources using Perplexica
4. Check browser DevTools Network tab for API calls to `/api/adaptive-questions/get-learning-resources`
5. Response should contain `"search_mode": "perplexica"` and AI-powered resources

---

## Troubleshooting

### Issue: "Invalid provider id" Error

**Cause:** Python client is using wrong provider UUID

**Fix:**
1. Check config: `docker-compose exec perplexica cat /home/perplexica/data/config.json`
2. Find Gemini provider UUID
3. Update `core/perplexica_client.py` line 117 with correct UUID
4. Restart: `docker-compose restart api`

### Issue: "Invalid Model Selected" Error

**Cause:** Wrong model name format

**Fix:**
- Use full Google API format: `"models/gemini-2.0-flash-exp"`
- Not: `"gemini-2.0-flash-exp"` (missing "models/" prefix)

### Issue: Empty Results

**Causes:**
1. Perplexica not running
2. No Gemini API key set
3. Network connectivity issues

**Fixes:**
```bash
# Check service status
docker-compose ps perplexica

# Restart Perplexica
docker-compose restart perplexica

# Verify API key
docker-compose exec perplexica env | grep GEMINI_API_KEY

# Check connectivity
docker-compose exec perplexica curl -I https://generativelanguage.googleapis.com
```

### Issue: Fallback to SearXNG

**This is normal!** Perplexica automatically falls back to SearXNG if:
- Perplexica health check fails
- Gemini API rate limits hit
- Network issues

**Check fallback:**
```python
# In test results, look for:
"sources_used": ["SearXNG"]  # ← Fallback activated
# vs
"sources_used": ["Perplexica"]  # ← AI search working
```

---

## Performance Benchmarks

Typical response times:

| Test | Expected Time | What's Happening |
|------|--------------|------------------|
| Health Check | < 1s | Quick ping |
| Basic Search | 3-8s | AI synthesis + web search |
| Learning Resources | 4-10s | Optimized query + AI |
| Resource Matcher | 5-12s | Full pipeline + parsing |

**Note:** First request may be slower (cold start). Subsequent requests are faster.

---

## Success Criteria

Your Perplexica integration is working correctly if:

✅ All 5 integration tests pass
✅ API endpoint returns resources with `search_mode="perplexica"`
✅ No "Invalid provider id" errors in logs
✅ No "Invalid Model Selected" errors in logs
✅ AI-synthesized answers are returned (not just raw search results)
✅ Source citations include proper URLs and titles
✅ Fallback to SearXNG works when Perplexica unavailable

---

## Quick Health Check Command

Run this one-liner to verify everything is working:

```bash
docker-compose exec api python -c "
from core.perplexica_client import get_perplexica_client
client = get_perplexica_client()
result = client.search('Python tutorial')
print('✓ Health:', client.health_check())
print('✓ Answer:', len(result.get('answer', '')) > 0)
print('✓ Sources:', len(result.get('sources', [])))
print('Status: ALL GOOD' if result.get('answer') else 'Status: ERROR')
"
```

**Expected output:**
```
✓ Health: True
✓ Answer: True
✓ Sources: 10-15
Status: ALL GOOD
```

---

## Advanced: Comparing Perplexica vs SearXNG

Test both modes side-by-side:

```bash
docker-compose exec api python -c "
from core.resource_matcher import get_resource_matcher
import time

matcher = get_resource_matcher()
gap = {'title': 'React', 'description': 'Frontend framework'}

# Test Perplexica
start = time.time()
result_p = matcher.find_resources_with_web_search(
    gap=gap, user_level='beginner', limit=5, search_mode='perplexica'
)
time_p = time.time() - start

# Test SearXNG
start = time.time()
result_s = matcher.find_resources_with_web_search(
    gap=gap, user_level='beginner', limit=5, search_mode='web_only'
)
time_s = time.time() - start

print(f'Perplexica: {result_p[\"total_resources\"]} resources in {time_p:.2f}s')
print(f'SearXNG:    {result_s[\"total_resources\"]} resources in {time_s:.2f}s')
print(f'Overhead:   +{time_p - time_s:.2f}s ({((time_p/time_s-1)*100):.0f}% slower)')
"
```

---

## Monitoring in Production

For production monitoring:

1. **Set up alerts** for "Invalid provider id" errors
2. **Monitor API latency** (Perplexica adds 2-8s)
3. **Track fallback rate** (should be < 5%)
4. **Watch Gemini API usage** in Google Cloud Console
5. **Monitor token consumption** (each search uses ~1500-3000 tokens)

---

## Need Help?

1. Check logs: `docker-compose logs perplexica --tail 50`
2. Run health check: `curl http://localhost:3002`
3. Verify config: `cat Backend/.env | grep GEMINI`
4. Run integration tests: `python test_perplexica_simple.py`
5. Check this guide's troubleshooting section

---

**Last Updated:** 2025-11-28
**Perplexica Version:** Latest (from GitHub)
**Model:** Gemini 2.0 Flash Experimental
