import time
import json
import os
import hashlib
import httpx
from google import genai
from openai import OpenAI
from dotenv import load_dotenv
from formats.toon import to_toon, from_toon
from app.config import job_description, TOON_EXAMPLE as TOON_EXAMPLE_SHARED, get_toon_prompt

# Load environment variables
load_dotenv()

# Create output directory for JSON files
OUTPUT_DIR = "json_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create persistent HTTP/2 client with connection pooling for performance
# This reuses connections and enables HTTP/2 for 30-50% speed improvement
http_client = httpx.Client(
    http2=True,  # Enable HTTP/2 for faster requests
    timeout=30.0,  # Longer timeout for LLM requests
    limits=httpx.Limits(
        max_keepalive_connections=10,  # Connection pool size
        keepalive_expiry=30.0  # Keep connections alive for 30 seconds
    )
)

# Initialize clients with optimized HTTP client
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=http_client  # Use persistent HTTP/2 client
)

# Response caching for faster repeated requests
# Cache key: (model_name, prompt_hash) -> (response_text, timestamp)
CACHE_TTL = 300  # Cache responses for 5 minutes
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
        # Check if cache entry is still valid
        if time.time() - timestamp < CACHE_TTL:
            cache_stats["hits"] += 1
            return cached_data
        else:
            # Expired, remove from cache
            del response_cache[cache_key]
    cache_stats["misses"] += 1
    return None

def cache_response(model_name: str, prompt: str, response: str):
    """Store response in cache"""
    cache_key = get_cache_key(model_name, prompt)
    response_cache[cache_key] = (response, time.time())

# TOON format schema example (compressed with concrete values)
TOON_EXAMPLE = """company_name: Acme Corp
position_title: Senior Engineer
location: NYC
work_mode: hybrid
salary_range: string or null
experience_years_required: number
experience_level: junior/mid/senior or null

hard_skills_required[12]{{skill,priority}}:
  Python,critical
  React,important
  AWS,nice

soft_skills_required[6]:
  - Full sentence explaining the soft skill and why it matters

responsibilities[12]:
  - Specific actionable sentence with technical details about what you'll do

tech_stack[10]:
  - Technology name

domain_expertise:
  industry[3]:
    - Industry name
  specific_knowledge[5]:
    - Specific domain knowledge

implicit_requirements[8]:
  - Inferred requirement from context

company_culture_signals[8]:
  - Culture or benefit signal

ats_keywords[15]:
  - Keyword"""

# Helper function to fix array counts in TOON format
def fix_toon_array_counts(toon_text: str) -> str:
    """
    Count actual array items and update the [X] brackets with correct counts.
    Also fixes incomplete {skill,priority} format.
    This fixes LLM counting errors before parsing.
    """
    import re
    lines = toon_text.split('\n')
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is an array declaration line (has [X]: or [X]{...}:)
        if '[' in line and (':' in line) and (']:' in line or '}:' in line) and not line.strip().startswith(('-', ' -')):
            # Extract array name
            parts = line.split('[')
            if len(parts) >= 2:
                array_name = parts[0].strip()

                # Count items in this array
                item_count = 0
                j = i + 1

                # Determine if this is hard_skills (no dashes) or other arrays (with dashes)
                is_hard_skills = 'hard_skills' in array_name

                while j < len(lines):
                    next_line = lines[j].strip()

                    # Stop if we hit the next array or end
                    if next_line and '[' in next_line and ':' in next_line and (']:' in next_line or '}:' in next_line) and not next_line.startswith('-'):
                        break

                    # Count items
                    if is_hard_skills:
                        # hard_skills: count lines with commas (skill,priority format)
                        if next_line and ',' in next_line and not next_line.startswith('-'):
                            item_count += 1
                    else:
                        # Other arrays: count lines starting with dash
                        if next_line.startswith('-'):
                            item_count += 1

                    j += 1

                # Replace the count in brackets
                line = re.sub(r'\[\d+\]', f'[{item_count}]', line)

                # Fix incomplete or missing {skill,priority} format for hard_skills
                if is_hard_skills:
                    if '{skill,priority}' not in line:
                        # Case 1: Has { but incomplete (e.g., [12]{ or [12]{skill or [12]{skill)
                        if '{' in line:
                            # Replace everything from [N]{ to the colon with [N]{skill,priority}:
                            line = re.sub(r'\[\d+\]\{[^:]*', f'[{item_count}]{{skill,priority}}', line)
                        # Case 2: Missing {skill,priority} entirely (e.g., [12]:)
                        else:
                            line = re.sub(r'\[\d+\]:', f'[{item_count}]{{skill,priority}}:', line)

                        # Ensure line ends with colon
                        if not line.endswith(':'):
                            line = line.rstrip() + ':'

        result_lines.append(line)
        i += 1

    return '\n'.join(result_lines)

# Helper function to manually extract fields from TOON text (fallback)
def manual_toon_extract(toon_text: str) -> dict:
    """
    Manually extract fields from TOON format when parser fails.
    Handles both with and without {skill,priority} notation.
    """
    lines = toon_text.split('\n')
    result = {}
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # domain_expertise special handling - CHECK THIS FIRST
        if line.startswith('domain_expertise:'):
            domain = {}
            j = i + 1
            current_subkey = None

            while j < len(lines):
                subline = lines[j].strip()

                # Stop at next top-level field (non-indented field without array brackets)
                if subline and not subline.startswith((' ', '-')) and ':' in subline and '[' not in subline:
                    break

                # Stop at known top-level arrays (not part of domain_expertise)
                if subline and '[' in subline and ']:' in subline:
                    subkey = subline.split('[')[0].strip()
                    # Only industry and specific_knowledge belong to domain_expertise
                    if subkey not in ['industry', 'specific_knowledge']:
                        break
                    current_subkey = subkey
                    domain[subkey] = []
                elif subline.startswith('-') and current_subkey:
                    domain[current_subkey].append(subline[1:].strip())

                j += 1

            if domain:
                result['domain_expertise'] = domain
            i += 1
            continue

        # Simple key-value fields (no arrays)
        if ':' in line and '[' not in line and not line.startswith(('-', ' ')):
            if not line.startswith('domain_expertise'):
                key_val = line.split(':', 1)
                if len(key_val) == 2:
                    key = key_val[0].strip()
                    val = key_val[1].strip()

                    # Parse value
                    if val == 'null' or val == '':
                        result[key] = None
                    elif val.isdigit():
                        result[key] = int(val)
                    else:
                        result[key] = val.strip('"')

        # Array fields - detect any line with [number] or [number]{...}
        # Pattern: field_name[123]: or field_name[123]{skill,priority}:
        if '[' in line and ']:' in line or ('[' in line and ']:' not in line and ']{' in line and '}:' in line):
            if not line.startswith((' ', '-')):
                # This is an array declaration
                array_name = line.split('[')[0].strip()

                # Skip if this is a domain_expertise sub-array (already handled above)
                if array_name in ['industry', 'specific_knowledge'] and 'domain_expertise' in result:
                    i += 1
                    continue

                items = []
                j = i + 1

                # Read items until next array or top-level field
                while j < len(lines):
                    item_line = lines[j].strip()

                    # Empty line, skip
                    if not item_line:
                        j += 1
                        continue

                    # Stop at next array declaration
                    if '[' in item_line and ']:' in item_line and not item_line.startswith((' ', '-')):
                        break

                    # Stop at next top-level field (key: value without brackets)
                    if ':' in item_line and '[' not in item_line and not item_line.startswith((' ', '-')):
                        break

                    # Extract item content
                    if item_line.startswith('-'):
                        # Regular array item with dash
                        items.append(item_line[1:].strip())
                    elif ',' in item_line:
                        # Comma-separated (likely skill,priority)
                        parts = item_line.split(',', 1)
                        if len(parts) == 2:
                            items.append({
                                "skill": parts[0].strip(),
                                "priority": parts[1].strip()
                            })

                    j += 1

                if items:
                    result[array_name] = items

        i += 1

    return result

# Model-specific extraction functions
def extract_gemini_flash_lite(toon_text: str) -> dict:
    """Extract fields specifically for Gemini Flash Lite format"""
    return manual_toon_extract(toon_text)

def extract_gemini_2_5_flash_lite(toon_text: str) -> dict:
    """Extract fields specifically for Gemini 2.5 Flash-Lite format"""
    return manual_toon_extract(toon_text)

def extract_gpt35_turbo(toon_text: str) -> dict:
    """Extract fields specifically for GPT-3.5-Turbo format"""
    return manual_toon_extract(toon_text)

def extract_gemini_flash_full(toon_text: str) -> dict:
    """Extract fields specifically for Gemini 2.0 Flash format"""
    return manual_toon_extract(toon_text)

def extract_gpt4o_mini(toon_text: str) -> dict:
    """Extract fields specifically for GPT-4o-Mini format"""
    return manual_toon_extract(toon_text)

# Helper function to parse TOON response
def parse_toon_response(response_text: str, model_name: str = None) -> tuple[dict, bool, str, str]:
    """Parse TOON or JSON response and return (parsed_dict, success, format_used, fixed_toon)"""
    cleaned_text = response_text.strip()

    # Remove markdown code blocks if present (handle multiple formats)
    if cleaned_text.startswith("```"):
        # Remove opening ``` or ```toon or ```json
        lines = cleaned_text.split("\n")
        if len(lines) > 1:
            # Remove first line (contains ```)
            lines = lines[1:]

        # Remove closing ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        elif lines and lines[-1].strip().endswith("```"):
            # Handle case where ``` is on same line as last content
            lines[-1] = lines[-1].replace("```", "").strip()

        cleaned_text = "\n".join(lines).strip()

    # Save original before fixing (for comparison)
    original_text = cleaned_text

    # Fix array counts before parsing
    cleaned_text = fix_toon_array_counts(cleaned_text)

    # Try parsing as TOON first
    try:
        parsed_data = from_toon(cleaned_text)
        return (parsed_data, True, "TOON", cleaned_text)
    except Exception as e:
        # Fall back to model-specific extraction
        if model_name:
            try:
                print(f"⚠️  TOON parser failed, trying {model_name} extractor...")
                if model_name == "gemini-flash-lite":
                    parsed_data = extract_gemini_flash_lite(cleaned_text)
                elif model_name == "gemini-2-5-flash-lite":
                    parsed_data = extract_gemini_2_5_flash_lite(cleaned_text)
                elif model_name == "gpt35-turbo":
                    parsed_data = extract_gpt35_turbo(cleaned_text)
                elif model_name == "gemini-flash-full":
                    parsed_data = extract_gemini_flash_full(cleaned_text)
                elif model_name == "gpt4o-mini":
                    parsed_data = extract_gpt4o_mini(cleaned_text)
                else:
                    parsed_data = manual_toon_extract(cleaned_text)

                field_count = len(parsed_data) if parsed_data else 0
                print(f"📊 {model_name} extractor got {field_count} fields")
                if parsed_data and field_count > 5:  # At least 5 fields extracted
                    return (parsed_data, True, f"TOON_MANUAL_{model_name.upper()}", cleaned_text)
            except Exception as ex:
                print(f"❌ {model_name} extractor failed: {str(ex)[:100]}")

        # Generic fallback
        try:
            parsed_data = manual_toon_extract(cleaned_text)
            if parsed_data and len(parsed_data) > 5:
                return (parsed_data, True, "TOON_MANUAL", cleaned_text)
        except:
            pass

        # Fall back to JSON
        try:
            parsed_data = json.loads(cleaned_text)
            return (parsed_data, True, "JSON", cleaned_text)
        except:
            return ({}, False, "FAILED", cleaned_text)

# Helper function to save JSON to file
def save_json_output(data: dict, filename: str, success: bool = True, raw_toon: str = None, fixed_toon: str = None):
    """Save parsed JSON data to file in the output directory with standard wrapper"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        with open(filepath, 'w') as f:
            if success:
                # Wrap in standard format
                output = {
                    "status": "success",
                    "jd_parsed": data
                }
                json.dump(output, f, indent=2)
            else:
                # Error format
                output = {
                    "status": "error",
                    "jd_parsed": None,
                    "error": "Failed to parse response",
                    "raw_data": str(data)
                }
                json.dump(output, f, indent=2)
        print(f"💾 Saved to: {filepath}")

        # Also save raw TOON output if provided
        if raw_toon:
            toon_filename = filename.replace('.json', '-raw-toon.txt')
            toon_filepath = os.path.join(OUTPUT_DIR, toon_filename)
            with open(toon_filepath, 'w') as f:
                f.write(raw_toon)
            print(f"💾 Saved TOON to: {toon_filepath}")

        # Also save fixed TOON output if provided (for debugging)
        if fixed_toon:
            fixed_filename = filename.replace('.json', '-fixed-toon.txt')
            fixed_filepath = os.path.join(OUTPUT_DIR, fixed_filename)
            with open(fixed_filepath, 'w') as f:
                f.write(fixed_toon)
            if not success:
                print(f"🔧 Saved fixed TOON to: {fixed_filepath}")
    except Exception as e:
        print(f"❌ Failed to save file: {e}")

# Generate prompt using shared config
prompt = get_toon_prompt(job_description)

# ========== GEMINI 2.5 FLASH-LITE (TOON) ==========
print("=" * 70)
print("🔵 GEMINI 2.5 FLASH-LITE (TOON)")
print("=" * 70)

start = time.time()
try:
    # Check cache first
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
            config={
                "temperature": 0.2
                # Removed response_mime_type to allow TOON format
            }
        )
        gemini25_response_text = gemini25_response.text
        cache_response(model_name, prompt, gemini25_response_text)
    gemini25_time = time.time() - start

    print(f"⏱️  Time: {round(gemini25_time, 3)} seconds")
    print(f"📄 Output preview:\n{gemini25_response_text[:300]}...\n")

    # Parse TOON/JSON response
    parsed_data, success, format_used, fixed_toon = parse_toon_response(gemini25_response_text, model_name="gemini-2-5-flash-lite")

    if success:
        print(f"✅ Valid response (format: {format_used})")
        print(f"📊 Keys found: {list(parsed_data.keys())}")
        print("\n📋 Full JSON Output:")
        print(json.dumps(parsed_data, indent=2))
        save_json_output(parsed_data, "gemini-2-5-flash-lite.json", success=True, raw_toon=gemini25_response_text, fixed_toon=fixed_toon)
    else:
        print("❌ Could not parse response")
        save_json_output({"error": "Parse failed"}, "gemini-2-5-flash-lite.json", success=False, raw_toon=gemini25_response_text, fixed_toon=fixed_toon)

except Exception as e:
    print(f"❌ Error: {e}")
    gemini25_time = None

# ========== RESULTS SUMMARY ==========
print("\n" + "=" * 70)
print("📊 BENCHMARK RESULTS")
print("=" * 70)

if gemini25_time:
    print(f"⏱️  Execution time: {gemini25_time:.3f}s")
    print(f"🏆 Model: Gemini 2.5 Flash-Lite (TOON format)")
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