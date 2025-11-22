import time
import json
import os
import hashlib
import httpx
from google import genai
from openai import OpenAI
from dotenv import load_dotenv
from app.config import job_description, get_json_prompt

# Load environment variables
load_dotenv()

# Create output directory for JSON files
OUTPUT_DIR = "json_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create persistent HTTP/2 client with connection pooling for performance
http_client = httpx.Client(
    http2=True,
    timeout=30.0,
    limits=httpx.Limits(
        max_keepalive_connections=10,
        keepalive_expiry=30.0
    )
)

# Initialize clients
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=http_client
)

# Response caching
CACHE_TTL = 300
response_cache = {}
cache_stats = {"hits": 0, "misses": 0}

def get_cache_key(model_name: str, prompt: str) -> str:
    """Generate cache key from model name and prompt hash"""
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
    return f"{model_name}:{prompt_hash}"

def get_cached_response(model_name: str, prompt: str) -> str | None:
    """Check cache for existing response"""
    cache_key = get_cache_key(model_name, prompt)
    if cache_key in response_cache:
        cached_data, timestamp = response_cache[cache_key]
        if time.time() - timestamp < CACHE_TTL:
            cache_stats["hits"] += 1
            return cached_data
        else:
            del response_cache[cache_key]
    cache_stats["misses"] += 1
    return None

def cache_response(model_name: str, prompt: str, response: str):
    """Store response in cache"""
    cache_key = get_cache_key(model_name, prompt)
    response_cache[cache_key] = (response, time.time())

# JSON parsing function
def parse_json_response(response_text: str) -> tuple[dict, bool, str]:
    """Parse JSON response and return (parsed_dict, success, raw_json)"""
    cleaned_text = response_text.strip()

    # Remove markdown code blocks if present
    if cleaned_text.startswith("```"):
        lines = cleaned_text.split("\n")
        if len(lines) > 1:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        elif lines and lines[-1].strip().endswith("```"):
            lines[-1] = lines[-1].replace("```", "").strip()
        cleaned_text = "\n".join(lines).strip()

    # Try parsing as JSON
    try:
        parsed_data = json.loads(cleaned_text)
        return (parsed_data, True, cleaned_text)
    except Exception as e:
        return ({}, False, cleaned_text)

# Helper function to save results
def save_json_output(data, filename, success=True, raw_json=None):
    """Save parsed output and raw JSON to files"""
    output_data = {
        "status": "success" if success else "error",
        "jd_parsed": data if success else None,
        "error": None if success else "Failed to parse response",
        "raw_data": str(raw_json) if not success else None
    }

    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(output_data, f, indent=2)

    # Also save raw JSON output if provided
    if raw_json:
        raw_filename = filename.replace('.json', '-raw-json.txt')
        raw_filepath = os.path.join(OUTPUT_DIR, raw_filename)
        with open(raw_filepath, 'w') as f:
            f.write(raw_json)

# Generate prompt using shared config
prompt = get_json_prompt(job_description)

# ========== GEMINI 2.5 FLASH-LITE (JSON) ==========
print("=" * 70)
print("🔵 GEMINI 2.5 FLASH-LITE (JSON)")
print("=" * 70)

start = time.time()
try:
    model_name = "gemini-2.5-flash-lite"
    cached_text = get_cached_response(model_name, prompt)

    if cached_text:
        print("💾 Cache HIT - using cached response")
        gemini25_response_text = cached_text
    else:
        print("🌐 Cache MISS - calling API")
        gemini25_response = gemini_client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={"temperature": 0.2}
        )
        gemini25_response_text = gemini25_response.text
        cache_response(model_name, prompt, gemini25_response_text)

    gemini25_time = time.time() - start

    print(f"⏱️  Time: {round(gemini25_time, 3)} seconds")
    print(f"📄 Output preview:\n{gemini25_response_text[:300]}...\n")

    # Parse JSON response
    parsed_data, success, cleaned_json = parse_json_response(gemini25_response_text)

    if success:
        print(f"✅ Valid JSON response")
        print(f"📊 Keys found: {list(parsed_data.keys())}")
        print("\n📋 Full JSON Output:")
        print(json.dumps(parsed_data, indent=2))
        save_json_output(parsed_data, "gemini-2-5-flash-lite-json-format.json", success=True, raw_json=gemini25_response_text)
    else:
        print("❌ Could not parse JSON response")
        save_json_output({"error": "Parse failed"}, "gemini-2-5-flash-lite-json-format.json", success=False, raw_json=gemini25_response_text)

except Exception as e:
    print(f"❌ Error: {e}")
    gemini25_time = None

print(f"💾 Saved to: json_outputs/gemini-2-5-flash-lite-json-format.json")
print(f"💾 Saved raw JSON to: json_outputs/gemini-2-5-flash-lite-json-format-raw-json.txt\n")

# ========== RESULTS SUMMARY ==========
print("=" * 70)
print("📊 BENCHMARK RESULTS")
print("=" * 70)

if gemini25_time:
    print(f"⏱️  Execution time: {gemini25_time:.3f}s")
    print(f"🏆 Model: Gemini 2.5 Flash-Lite (JSON format)")
    print(f"💰 Cost: $0.10/$0.40 per 1M tokens (cheapest)")
else:
    print("❌ Benchmark failed")

# Display cache statistics
total_requests = cache_stats["hits"] + cache_stats["misses"]
if total_requests > 0:
    hit_rate = (cache_stats["hits"] / total_requests) * 100
    print(f"\n💾 Cache Performance:")
    print(f"   Hits: {cache_stats['hits']}, Misses: {cache_stats['misses']}")
    print(f"   Hit Rate: {hit_rate:.1f}%")
    if cache_stats["hits"] > 0:
        print(f"   ⚡ Cache saved ~{cache_stats['hits'] * 5}-{cache_stats['hits'] * 15} seconds!")

print("=" * 70)
