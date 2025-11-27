import time
import json
import os
import re
import httpx
import tempfile
import hashlib
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from google import genai
from openai import OpenAI
from dotenv import load_dotenv
from formats.toon import to_toon, from_toon
from app.config import get_toon_prompt, get_json_prompt, get_cv_prompt, get_detailed_gap_analysis_prompt, get_compressed_gap_analysis_prompt, get_question_generation_prompt, get_answer_analysis_prompt, get_resume_rewrite_prompt, get_domain_finder_prompt
from core.embeddings import calculate_overall_compatibility
from core.vector_store import get_qdrant_manager
from core.cache import get_cache
from core.gemini_cache import generate_with_cache, get_prompt_cache_stats

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Job Parser API",
    description="API for parsing job descriptions using Gemini 2.5 Flash-Lite",
    version="2.0.0"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:3002", "http://127.0.0.1:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Initialize cache for score caching (99% speedup on cache hits)
cache = get_cache()

# TOON format schema example
TOON_EXAMPLE = """company_name: string or null
position_title: string or null
location: string or null
work_mode: remote/hybrid/onsite or null
salary_range: string or null
experience_years_required: number
experience_level: junior/mid/senior or null

hard_skills_required[3]{{skill,priority}}:
  Python,critical
  React,important
  AWS,nice

soft_skills_required[...]:
  - string

responsibilities[...]:
  - string

tech_stack[...]:
  - string

domain_expertise:
  industry[...]:
    - string
  specific_knowledge[...]:
    - string

implicit_requirements[...]:
  - string

company_culture_signals[...]:
  - string

ats_keywords[...]:
  - string"""

# Prompt template - using TOON format
def create_prompt(job_description: str) -> str:
    return f"""You are an information extraction system.
Analyze the following job description and extract all relevant details.

Return your response in TOON format. TOON is a compact data format that reduces tokens.

Here is the structure you should follow (shown in TOON format):

{TOON_EXAMPLE}

RULES:
⚠️ CRITICAL FORMAT REQUIREMENT - DO NOT SKIP:
   hard_skills_required[COUNT]{{skill,priority}}: <- MUST include {{skill,priority}} after the count!
   Example: hard_skills_required[12]{{skill,priority}}:
   NEVER write: hard_skills_required[12]: (missing {{skill,priority}})

- Return only TOON data (no markdown/commentary)
- [...] = array limits (MIN=minimum required, MAX=maximum allowed): hard_skills 12 MIN 15 MAX, responsibilities 10 MIN 12 MAX, soft_skills 5 MIN 6 MAX, tech_stack 8 MIN 10 MAX, keywords 12 MIN 15 MAX, implicit_requirements 5 MIN 8 MAX, culture_signals 5 MIN 8 MAX, industry 1 MIN 3 MAX, specific_knowledge 3 MIN 5 MAX
- IMPORTANT: Replace [...] with actual count - COUNT THE ITEMS YOURSELF! If you have 5 items write [5], if you have 12 items write [12]
- ⚠️ VERIFY: The number in brackets MUST EXACTLY match the number of items in the array. Count before writing!
- After the colon, list skills as: skill_name,priority (one per line, NO dashes)
- Array formats: hard_skills = skill,critical (NO dashes, NO prefix) | All others = - item (MUST have "- " before EVERY item)
- CRITICAL: Check EVERY array item has "- " prefix except hard_skills - missing dashes break parsing!
- Full sentences for responsibilities/soft_skills - be specific and detailed for responsibilities
- Concise OK for implicit_requirements/culture_signals
- null for missing values

========================================
REMINDER: hard_skills_required[12]{{skill,priority}}: <- Include {{skill,priority}} !
========================================

JOB DESCRIPTION:
{job_description}
"""

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

# Helper function to parse TOON response and convert to JSON
def parse_toon_response(response_text: str) -> tuple[dict, bool, str]:
    """
    Parse TOON or JSON response and return (parsed_dict, success, format_used)

    Returns:
        tuple: (parsed_data as dict, success as bool, format as str)
    """
    # Strip markdown code blocks if present
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

    # Fix array counts before parsing
    cleaned_text = fix_toon_array_counts(cleaned_text)

    # Try parsing as TOON first
    try:
        parsed_data = from_toon(cleaned_text)
        return (parsed_data, True, "TOON")
    except Exception as toon_error:
        # Fall back to JSON parsing
        try:
            parsed_data = json.loads(cleaned_text)
            return (parsed_data, True, "JSON")
        except Exception as json_error:
            # Both failed
            return ({}, False, "FAILED")

# Request/Response models
class JobDescription(BaseModel):
    job_description: str

class BenchmarkResult(BaseModel):
    model: str
    time_seconds: float
    valid_json: bool
    output_preview: str
    error: str = None

class CompareResponse(BaseModel):
    results: list[BenchmarkResult]
    fastest_model: str
    speedup: float

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Job Parser API",
        "version": "2.0.0",
        "model": "gemini-2.5-flash-lite"
    }

# New simple parse endpoint for frontend
class ParseRequest(BaseModel):
    job_description: str
    language: str = "english"  # Default to English

class ParseResponse(BaseModel):
    success: bool
    data: dict | None = None
    error: str | None = None
    time_seconds: float
    model: str
    language: str

@app.post("/api/parse", response_model=ParseResponse)
async def parse_job(request: ParseRequest):
    """
    Parse a job description using Gemini 2.5 Flash-Lite with JSON format.
    This is the main endpoint for the frontend.
    Supports multiple languages: english, french, german, spanish
    """
    try:
        # Validate input
        if not request.job_description or len(request.job_description.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Job description must be at least 50 characters"
            )

        # Auto-truncate if over 6200 characters
        job_description = request.job_description[:6200] if len(request.job_description) > 6200 else request.job_description

        # Validate language
        supported_languages = ["english", "french", "german", "spanish"]
        language = request.language.lower()
        if language not in supported_languages:
            language = "english"

        # CACHE: Check if this JD parsing is cached
        jd_hash = hashlib.md5(job_description.encode()).hexdigest()
        cache_key = f"parse:jd:{jd_hash}:{language}"

        cached_result = cache.get(cache_key)
        if cached_result:
            result_dict = json.loads(cached_result)
            return ParseResponse(**result_dict)

        # Generate JSON prompt using shared config with language
        prompt = get_json_prompt(job_description, language)

        # Call Gemini 2.5 Flash-Lite
        start_time = time.time()
        model_name = "gemini-2.5-flash-lite"

        response = gemini_client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={"temperature": 0.2}
        )

        response_text = response.text
        elapsed_time = time.time() - start_time

        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            cleaned_text = response_text.strip()

            if cleaned_text.startswith("```"):
                lines = cleaned_text.split("\n")
                if len(lines) > 1:
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                elif lines and lines[-1].strip().endswith("```"):
                    lines[-1] = lines[-1].replace("```", "").strip()
                cleaned_text = "\n".join(lines).strip()

            # Parse JSON
            parsed_data = json.loads(cleaned_text)

            if parsed_data and len(parsed_data) >= 5:
                result = ParseResponse(
                    success=True,
                    data=parsed_data,
                    time_seconds=round(elapsed_time, 3),
                    model=model_name,
                    language=language
                )

                # CACHE: Store successful parse result (30 days TTL)
                cache.set(cache_key, json.dumps(result.dict()), ttl=2592000)

                return result
            else:
                return ParseResponse(
                    success=False,
                    data={"raw_response": response_text[:500]},
                    error="Failed to parse JSON completely",
                    time_seconds=round(elapsed_time, 3),
                    model=model_name,
                    language=language
                )

        except Exception as parse_error:
            return ParseResponse(
                success=False,
                data={"raw_response": response_text[:500]},
                error=f"Parse error: {str(parse_error)}",
                time_seconds=round(elapsed_time, 3),
                model=model_name,
                language=language
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# CV Parsing endpoint
class CVParseRequest(BaseModel):
    resume_text: str
    language: str = "english"

class CVParseResponse(BaseModel):
    success: bool
    data: dict | None = None
    error: str | None = None
    time_seconds: float
    model: str
    language: str

@app.post("/api/parse-cv", response_model=CVParseResponse)
async def parse_cv(request: CVParseRequest):
    """
    Parse a resume/CV using Gemini 2.5 Flash-Lite with JSON format.
    Supports multiple languages: english, french, german, spanish
    """
    try:
        # Validate input
        if not request.resume_text or len(request.resume_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Resume text must be at least 50 characters"
            )

        # Auto-truncate if over 6200 characters
        resume_text = request.resume_text[:6200] if len(request.resume_text) > 6200 else request.resume_text

        # Validate language
        supported_languages = ["english", "french", "german", "spanish"]
        language = request.language.lower()
        if language not in supported_languages:
            language = "english"

        # CACHE: Check if this CV parsing is cached
        cv_hash = hashlib.md5(resume_text.encode()).hexdigest()
        cache_key = f"parse:cv:{cv_hash}:{language}"

        cached_result = cache.get(cache_key)
        if cached_result:
            result_dict = json.loads(cached_result)
            return CVParseResponse(**result_dict)

        # Generate CV prompt using shared config with language
        prompt = get_cv_prompt(resume_text, language)

        # Call Gemini 2.5 Flash-Lite
        start_time = time.time()
        model_name = "gemini-2.5-flash-lite"

        response = gemini_client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={"temperature": 0.2}
        )

        response_text = response.text
        elapsed_time = time.time() - start_time

        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            cleaned_text = response_text.strip()

            if cleaned_text.startswith("```"):
                lines = cleaned_text.split("\n")
                if len(lines) > 1:
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                elif lines and lines[-1].strip().endswith("```"):
                    lines[-1] = lines[-1].replace("```", "").strip()
                cleaned_text = "\n".join(lines).strip()

            # Parse JSON
            parsed_data = json.loads(cleaned_text)

            if parsed_data and len(parsed_data) >= 3:
                result = CVParseResponse(
                    success=True,
                    data=parsed_data,
                    time_seconds=round(elapsed_time, 3),
                    model=model_name,
                    language=language
                )

                # CACHE: Store successful parse result (30 days TTL)
                cache.set(cache_key, json.dumps(result.dict()), ttl=2592000)

                return result
            else:
                return CVParseResponse(
                    success=False,
                    data={"raw_response": response_text[:500]},
                    error="Failed to parse CV JSON completely",
                    time_seconds=round(elapsed_time, 3),
                    model=model_name,
                    language=language
                )

        except Exception as parse_error:
            return CVParseResponse(
                success=False,
                data={"raw_response": response_text[:500]},
                error=f"Parse error: {str(parse_error)}",
                time_seconds=round(elapsed_time, 3),
                model=model_name,
                language=language
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# Domain Finder endpoint
class DomainMatch(BaseModel):
    domain_name: str  # Format: "Role - Industry"
    technical_role: str  # e.g., "Backend Developer", "Senior API Engineer"
    industry: str  # e.g., "Gaming", "FinTech", "HealthTech"
    fit_score: int
    rank: int
    matching_skills: list[str]  # Combined role + industry skills
    skills_to_learn: list[str]  # Combined list (for backwards compatibility)
    role_skills_to_learn: list[str]  # Technical skills needed for role
    industry_skills_to_learn: list[str]  # Domain knowledge for industry
    learning_priority: str
    time_to_ready: str
    reasoning: str  # Why this ROLE fits
    industry_rationale: str  # Why this INDUSTRY matches

class DomainFinderRequest(BaseModel):
    resume_text: str
    language: str = "english"

class DomainFinderResponse(BaseModel):
    success: bool
    domains: list[DomainMatch] | None = None
    total_suggested: int
    error: str | None = None
    time_seconds: float
    model: str
    language: str

@app.post("/api/find-domains", response_model=DomainFinderResponse)
async def find_domains(request: DomainFinderRequest, bypass_cache: bool = False):
    """
    Analyze resume and suggest 8-10 career domains/industries ranked by fit.
    For each domain, provides skill gap analysis and time-to-ready estimate.
    Supports multiple languages: english, french, german, spanish

    Args:
        request: DomainFinderRequest with resume_text and language
        bypass_cache: If True, skip cache lookup and force fresh analysis (useful for testing/updates)
    """
    try:
        # Validate input
        if not request.resume_text or len(request.resume_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Resume text must be at least 50 characters"
            )

        # Auto-truncate if over 6200 characters
        resume_text = request.resume_text[:6200] if len(request.resume_text) > 6200 else request.resume_text

        # Validate language
        supported_languages = ["english", "french", "german", "spanish"]
        language = request.language.lower()
        if language not in supported_languages:
            language = "english"

        # CACHE: Check if this domain analysis is cached (skip if bypass_cache=True)
        resume_hash = hashlib.md5(resume_text.encode()).hexdigest()
        cache_key = f"domains:{resume_hash}:{language}"

        if not bypass_cache:
            cached_result = cache.get(cache_key)
            if cached_result:
                result_dict = json.loads(cached_result)
                return DomainFinderResponse(**result_dict)

        # Generate domain finder prompt
        prompt = get_domain_finder_prompt(resume_text, language)

        # Call Gemini 2.5 Flash-Lite
        start_time = time.time()
        model_name = "gemini-2.5-flash-lite"

        response = gemini_client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={"temperature": 0.3}
        )

        response_text = response.text
        elapsed_time = time.time() - start_time

        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            cleaned_text = response_text.strip()

            if cleaned_text.startswith("```"):
                lines = cleaned_text.split("\n")
                if len(lines) > 1:
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                elif lines and lines[-1].strip().endswith("```"):
                    lines[-1] = lines[-1].replace("```", "").strip()
                cleaned_text = "\n".join(lines).strip()

            # Parse JSON
            parsed_data = json.loads(cleaned_text)

            # Validate domains array
            if "domains" in parsed_data and isinstance(parsed_data["domains"], list) and len(parsed_data["domains"]) >= 8:
                domains = [DomainMatch(**domain) for domain in parsed_data["domains"]]

                result = DomainFinderResponse(
                    success=True,
                    domains=domains,
                    total_suggested=len(domains),
                    time_seconds=round(elapsed_time, 3),
                    model=model_name,
                    language=language
                )

                # CACHE: Store successful result (1 hour TTL for easier testing/updates)
                cache.set(cache_key, json.dumps(result.dict()), ttl=3600)

                return result
            else:
                return DomainFinderResponse(
                    success=False,
                    domains=None,
                    total_suggested=0,
                    error="Failed to generate sufficient domain suggestions (expected 8-10)",
                    time_seconds=round(elapsed_time, 3),
                    model=model_name,
                    language=language
                )

        except Exception as parse_error:
            return DomainFinderResponse(
                success=False,
                domains=None,
                total_suggested=0,
                error=f"Parse error: {str(parse_error)}. Raw response: {response_text[:200]}",
                time_seconds=round(elapsed_time, 3),
                model=model_name,
                language=language
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# Compatibility Score Calculation endpoint (Hybrid approach)

# New detailed models for pipeline.md aligned gap analysis
class GapItem(BaseModel):
    id: str
    title: str
    current: str
    required: str
    impact: str
    severity: str
    description: str
    addressability: str
    timeframe_to_address: str | None = None

class CategorizedGaps(BaseModel):
    critical: list[GapItem]
    important: list[GapItem]
    nice_to_have: list[GapItem]
    logistical: list[GapItem]

class CategoryScore(BaseModel):
    score: int
    weight: float
    status: str

class StrengthItem(BaseModel):
    title: str
    description: str
    evidence: str

class ApplicationViability(BaseModel):
    current_likelihood: str
    key_blockers: list[str]

# Request/Response models
class ScoreRequest(BaseModel):
    parsed_cv: dict
    parsed_jd: dict
    language: str = "english"

class ScoreMessage(BaseModel):
    title: str
    subtitle: str

class ScoreResponse(BaseModel):
    success: bool
    overall_score: int
    overall_status: str  # NEW: STRONG FIT, MODERATE FIT, etc.
    score_message: ScoreMessage  # NEW: AI-generated encouraging messages
    category_scores: dict[str, CategoryScore]  # NEW: Detailed with weights and status
    gaps: CategorizedGaps  # NEW: Categorized gaps
    strengths: list[StrengthItem]  # NEW: Structured strengths
    application_viability: ApplicationViability  # NEW: Viability assessment
    similarity_metrics: dict  # Keep for backward compatibility
    time_seconds: float
    model: str


# ===== COVER LETTER GENERATION MODELS =====

class CoverLetterRequest(BaseModel):
    parsed_resume: dict  # The parsed/rewritten resume in structured format
    parsed_jd: dict  # Parsed job description
    score_data: dict = None  # Optional: gaps and strengths from score analysis
    language: str = "english"

class CoverLetterResponse(BaseModel):
    success: bool
    cover_letter: str  # The generated cover letter text
    word_count: int
    time_seconds: float
    model: str


# ===== PHASE 4: SMART QUESTIONS MODELS =====

class QuestionItem(BaseModel):
    id: str  # "q1", "q2", etc.
    number: int
    title: str
    priority: str  # "CRITICAL", "HIGH", "MEDIUM"
    impact: str  # "+15% if yes"
    question_text: str
    context_why: str
    examples: list[str]

class GenerateQuestionsRequest(BaseModel):
    parsed_cv: dict
    parsed_jd: dict
    score_result: dict  # Full ScoreResponse from Phase 3
    language: str = "english"

class GenerateQuestionsResponse(BaseModel):
    success: bool
    questions: list[QuestionItem]
    total_questions: int
    critical_count: int
    high_count: int
    medium_count: int
    rag_context_used: bool  # Whether RAG found similar experiences
    time_seconds: float
    model: str

class QuestionAnswer(BaseModel):
    question_id: str
    answer_text: str
    answer_type: str  # "text" or "voice"
    transcription_time: float | None = None  # If voice

class SubmitAnswersRequest(BaseModel):
    parsed_cv: dict
    parsed_jd: dict
    questions: list[QuestionItem]
    answers: list[QuestionAnswer]
    original_score: int
    language: str = "english"

class SubmitAnswersResponse(BaseModel):
    success: bool
    updated_score: int
    score_improvement: int  # e.g., +16
    category_improvements: dict[str, int]
    uncovered_experiences: list[str]  # What was discovered
    updated_cv: dict  # CV with updates from answers
    time_seconds: float
    model: str

class EvaluateAnswerRequest(BaseModel):
    question_id: str
    question_text: str
    answer_text: str
    gap_info: dict  # {title: str, description: str}
    language: str = "english"

class EvaluateAnswerResponse(BaseModel):
    success: bool
    question_id: str
    answer_text: str
    quality_score: int  # 1-10
    quality_issues: list[str]
    quality_strengths: list[str]
    improvement_suggestions: list[str]
    is_acceptable: bool  # score >= 7
    time_seconds: float
    model: str
    error: str | None = None

class RewriteResumeRequest(BaseModel):
    updated_cv: dict  # CV with updates from answers
    questions: list[QuestionItem]  # Questions that were asked
    answers: list[QuestionAnswer]  # User's answers
    parsed_jd: dict  # Job description
    language: str = "english"

class RewriteResumeResponse(BaseModel):
    success: bool
    sample_format: dict  # camelCase, HTML descriptions
    parsed_format: dict  # snake_case, plain text
    enhancements_made: list[str]  # List of what was added/improved
    time_seconds: float
    model: str

class TranscribeAudioResponse(BaseModel):
    success: bool
    transcribed_text: str
    time_seconds: float
    model: str
    error: str | None = None


# ===== HYBRID SCORING HELPER FUNCTIONS =====

def extract_years_from_duration(duration_str: str) -> float:
    """Extract years from duration string like '4 years', '2 years 3 months', etc."""
    if not duration_str:
        return 0.0

    years = 0.0
    duration_lower = duration_str.lower()

    # Extract years
    import re
    year_match = re.search(r'(\d+)\s*year', duration_lower)
    if year_match:
        years += int(year_match.group(1))

    # Extract months and convert to years
    month_match = re.search(r'(\d+)\s*month', duration_lower)
    if month_match:
        years += int(month_match.group(1)) / 12.0

    return years


def calculate_total_experience_years(cv: dict) -> int:
    """Calculate total years of experience from CV"""
    total_years = 0.0

    work_experience = cv.get('work_experience', [])
    for exp in work_experience:
        if isinstance(exp, dict):
            duration = exp.get('duration', '')
            total_years += extract_years_from_duration(duration)

    return int(total_years)


def get_status_label(score: int) -> str:
    """Convert score to status label"""
    if score >= 85:
        return "Strong"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Fair"
    elif score >= 30:
        return "Below Target"
    else:
        return "Poor"


# Multi-language stop words for soft skills matching
STOP_WORDS_BY_LANGUAGE = {
    'english': {'and', 'or', 'the', 'a', 'an', 'in', 'with', 'of', 'to', 'for', 'at', 'by', 'is', 'are'},
    'french': {'et', 'ou', 'le', 'la', 'les', 'un', 'une', 'de', 'des', 'du', 'dans', 'avec', 'pour', 'par', 'sur', 'en', 'au', 'aux'},
    'german': {'und', 'oder', 'der', 'die', 'das', 'ein', 'eine', 'den', 'dem', 'des', 'in', 'mit', 'von', 'zu', 'für', 'bei', 'auf', 'im', 'am', 'zum', 'zur', 'vom'},
    'spanish': {'y', 'o', 'el', 'la', 'los', 'las', 'un', 'una', 'de', 'del', 'en', 'con', 'para', 'por', 'sobre', 'al', 'a', 'los'}
}


def calculate_soft_skills_match(cv_soft_skills: list, jd_soft_skills: list, language: str = 'english') -> int:
    """
    Calculate soft skills match using token-based fuzzy matching.
    Handles cases like "problem solving" matching "problem-solving mindset".
    Supports multiple languages with language-specific stop words.

    Args:
        cv_soft_skills: List of soft skill strings from CV
        jd_soft_skills: List of soft skill strings from JD
        language: Language code (english, french, german, spanish)

    Returns:
        Match score from 0-100
    """
    if not cv_soft_skills or not jd_soft_skills:
        return 0

    def tokenize(skill: str) -> set:
        """Tokenize and normalize a soft skill string."""
        # Get language-specific stop words
        stop_words = STOP_WORDS_BY_LANGUAGE.get(language.lower(), STOP_WORDS_BY_LANGUAGE['english'])
        # Replace hyphens with spaces, lowercase, split, and remove stop words
        tokens = set(skill.lower().replace('-', ' ').split())
        return tokens - stop_words

    # Tokenize all skills
    cv_tokens = [tokenize(s) for s in cv_soft_skills]
    jd_tokens = [tokenize(s) for s in jd_soft_skills]

    # Check token overlap (need at least 1 common meaningful word)
    matches = 0
    for jd_token_set in jd_tokens:
        for cv_token_set in cv_tokens:
            # If they share at least 1 token, consider it a match
            if len(jd_token_set & cv_token_set) >= 1:
                matches += 1
                break  # Count each JD skill only once

    # Calculate percentage
    return int((matches / len(jd_soft_skills)) * 100)


def get_adaptive_similarity_threshold(text1: str, text2: str) -> float:
    """
    Calculate adaptive threshold based on text length.
    Short phrases get lower thresholds, long sentences get higher thresholds.

    Args:
        text1: First text to compare
        text2: Second text to compare

    Returns:
        Similarity threshold between 0.45 and 0.55
    """
    avg_length = (len(text1) + len(text2)) / 2

    if avg_length < 15:  # Very short (e.g., "SaaS", "Technology")
        return 0.45
    elif avg_length < 50:  # Medium (e.g., "Scalable cloud infrastructure")
        return 0.50
    else:  # Long sentences
        return 0.55


def calculate_domain_match(cv: dict, jd: dict) -> int:
    """Calculate domain expertise match score"""
    # Check if CV mentions JD's industry or domain knowledge
    cv_summary = cv.get('professional_summary', '').lower()
    cv_achievements = []

    for exp in cv.get('work_experience', []):
        if isinstance(exp, dict) and 'achievements' in exp:
            achievements = exp['achievements']
            if isinstance(achievements, list):
                cv_achievements.extend([str(a).lower() for a in achievements])

    jd_industries = jd.get('domain_expertise', {}).get('industry', [])
    jd_knowledge = jd.get('domain_expertise', {}).get('specific_knowledge', [])

    # Simple keyword matching
    matches = 0
    total = len(jd_industries) + len(jd_knowledge)

    if total == 0:
        # Fallback: Extract domain from JD responsibilities if domain_expertise is missing
        jd_responsibilities = jd.get('responsibilities', [])
        if jd_responsibilities:
            # Get CV text for comparison
            cv_text = (cv_summary + ' ' + ' '.join(cv_achievements)).lower()
            jd_text = ' '.join(jd_responsibilities).lower()

            # Extract meaningful words (>4 chars, excluding common words)
            common_words = {'build', 'develop', 'create', 'manage', 'work', 'team', 'collaborate', 'implement', 'design', 'maintain', 'support', 'ensure', 'provide'}
            cv_words = {w for w in cv_text.split() if len(w) > 4 and w not in common_words}
            jd_words = {w for w in jd_text.split() if len(w) > 4 and w not in common_words}

            # Calculate overlap
            overlap = len(cv_words & jd_words)
            return min(70, overlap * 3)  # Cap at 70%, each matching word = 3%

        return 50  # Neutral if no domain info at all (changed from 0)

    # OPTIMIZATION: Use batched semantic embeddings for domain matching
    from core.embeddings import get_embeddings_batch, calculate_cosine_similarity

    # Combine CV content into sentences
    cv_sentences = [cv_summary] + cv_achievements
    cv_sentences = [s for s in cv_sentences if s]  # Remove empty

    # OPTIMIZED: Batch generate ALL embeddings at once (CV + JD requirements)
    # Collect all texts to embed
    all_texts = cv_sentences + list(jd_industries) + list(jd_knowledge)

    # Generate all embeddings in ONE batch call (parallel API calls)
    all_embeddings = get_embeddings_batch(all_texts)

    # Split embeddings back into CV and JD groups
    num_cv = len(cv_sentences)
    num_industries = len(jd_industries)

    cv_embeddings = all_embeddings[:num_cv]
    industry_embeddings = all_embeddings[num_cv:num_cv + num_industries]
    knowledge_embeddings = all_embeddings[num_cv + num_industries:]

    # Check each JD industry requirement using semantic similarity
    for industry, industry_embedding in zip(jd_industries, industry_embeddings):
        # Find best match with any CV sentence
        best_similarity = 0.0
        best_cv_sentence = ""
        for i, cv_emb in enumerate(cv_embeddings):
            similarity = calculate_cosine_similarity(industry_embedding, cv_emb)
            if similarity > best_similarity:
                best_similarity = similarity
                best_cv_sentence = cv_sentences[i]

        # Use adaptive threshold based on text length
        threshold = get_adaptive_similarity_threshold(industry, best_cv_sentence)
        if best_similarity >= threshold:
            matches += 1

    # Check each JD knowledge requirement using semantic similarity
    for knowledge, knowledge_embedding in zip(jd_knowledge, knowledge_embeddings):
        # Find best match with any CV sentence
        best_similarity = 0.0
        best_cv_sentence = ""
        for i, cv_emb in enumerate(cv_embeddings):
            similarity = calculate_cosine_similarity(knowledge_embedding, cv_emb)
            if similarity > best_similarity:
                best_similarity = similarity
                best_cv_sentence = cv_sentences[i]

        # Use adaptive threshold based on text length
        threshold = get_adaptive_similarity_threshold(knowledge, best_cv_sentence)
        if best_similarity >= threshold:
            matches += 1

    return min(100, int((matches / total) * 100))


def calculate_portfolio_quality(cv: dict) -> int:
    """Calculate portfolio quality score based on projects and achievements"""
    score = 0  # Start from 0 (changed from 50)

    # Projects
    projects = cv.get('projects', [])
    if len(projects) >= 3:
        score += 20
    elif len(projects) >= 1:
        score += 10

    # Achievements with quantifiable metrics
    achievement_count = 0
    quantified_count = 0

    for exp in cv.get('work_experience', []):
        if isinstance(exp, dict) and 'achievements' in exp:
            achievements = exp['achievements']
            if isinstance(achievements, list):
                achievement_count += len(achievements)
                # Check for numbers/percentages (quantified achievements)
                for ach in achievements:
                    if isinstance(ach, str) and any(char.isdigit() for char in ach):
                        quantified_count += 1

    if quantified_count >= 5:
        score += 20
    elif quantified_count >= 3:
        score += 10
    elif quantified_count >= 1:
        score += 5

    # Publications/certifications
    if cv.get('publications') or cv.get('certifications'):
        score += 10

    return min(100, score)


def calculate_logistics_match(cv: dict, jd: dict) -> int:
    """Calculate location/logistics compatibility score"""
    score = 50  # Start neutral (changed from 100)

    cv_location = (cv.get('personal_info', {}).get('location') or '').lower()
    jd_location = (jd.get('location') or '').lower()
    jd_work_mode = (jd.get('work_mode') or '').lower()

    # Location match
    if cv_location and jd_location:
        # Extract city/state from locations
        if cv_location not in jd_location and jd_location not in cv_location:
            # Different locations
            if jd_work_mode == 'remote':
                score -= 0  # No penalty for remote
            elif jd_work_mode == 'hybrid':
                score -= 20  # Some penalty for hybrid
            else:  # onsite
                score -= 40  # Significant penalty for onsite

    return max(0, score)


# OPTIMIZATION #2: Removed in-memory caches - now using persistent Redis cache
# Old: _industry_cache = {}, _role_cache = {}
# Now using cache.get()/cache.set() with "ind:" and "role:" prefixes


def extract_industries_with_ai(text: str) -> list[str]:
    """
    Use Gemini AI to extract and normalize industries from text.
    Returns list of standard industry names.

    OPTIMIZATION #2: Uses persistent Redis cache (10-15% improvement)
    """
    if not text or len(text.strip()) < 3:
        return []

    # OPTIMIZATION #2: Check persistent Redis cache first
    cache_key = f"ind:{text[:100]}"  # Prefix for industry extraction
    cached_result = cache.get(cache_key)
    if cached_result:
        # Redis cache stores JSON, deserialize if string
        if isinstance(cached_result, str):
            return json.loads(cached_result)
        return cached_result

    try:
        prompt = f"""Extract and normalize the industry or business sector from this text.

Text: "{text}"

Instructions:
- Identify the primary industry/sector (e.g., Technology, Healthcare, Finance, Education, Retail, Manufacturing, etc.)
- Return ONLY a JSON array of industry names, no other text
- Use standard industry categories
- If multiple industries, list all (max 3)
- If unclear, return empty array []

Example output: ["Technology", "Software"]
Example output: ["Healthcare", "Medical"]
Example output: ["Finance"]

Return only the JSON array:"""

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config={"temperature": 0.1}  # Low temperature for consistency
        )

        result_text = response.text.strip()

        # Parse JSON response
        industries = json.loads(result_text)

        if not isinstance(industries, list):
            industries = []

        # Normalize to lowercase for comparison
        industries = [ind.lower().strip() for ind in industries if ind]

        # OPTIMIZATION #2: Store in persistent Redis cache (TTL: 30 days)
        cache.set(cache_key, json.dumps(industries), ttl=2592000)

        return industries

    except Exception as e:
        print(f"Error extracting industries with AI: {e}")
        return []


def extract_role_category_with_ai(role: str) -> str:
    """
    Use Gemini AI to categorize a job role into a standard category.
    Returns normalized role category.

    OPTIMIZATION #2: Uses persistent Redis cache (10-15% improvement)
    """
    if not role or len(role.strip()) < 2:
        return ""

    # OPTIMIZATION #2: Check persistent Redis cache first
    role_key = f"role:{role.lower().strip()}"  # Prefix for role extraction
    cached_result = cache.get(role_key)
    if cached_result:
        # Redis cache stores JSON, deserialize if string
        if isinstance(cached_result, str):
            return json.loads(cached_result).strip('"')  # Remove JSON quotes
        return str(cached_result)

    try:
        prompt = f"""Categorize this job role into ONE standard category.

Role: "{role}"

Standard categories:
- Developer (software engineers, programmers, coders)
- Manager (directors, team leads, supervisors)
- Designer (UX, UI, graphic designers, creative)
- Data Scientist (data analysts, data engineers, ML engineers)
- Doctor (physicians, surgeons, medical doctors)
- Nurse (RN, nursing staff, healthcare workers)
- Teacher (professors, instructors, educators)
- Sales (account executives, business development)
- Marketing (growth, brand, content marketers)
- Other (if none of the above fit)

Return ONLY the category name, nothing else. One word only.

Example: Developer
Example: Doctor
Example: Marketing

Return:"""

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config={"temperature": 0.1}  # Low temperature for consistency
        )

        category = response.text.strip().lower()

        # Validate category
        valid_categories = {
            'developer', 'manager', 'designer', 'data scientist',
            'doctor', 'nurse', 'teacher', 'sales', 'marketing', 'other'
        }

        if category not in valid_categories:
            # Try to match partial
            for valid in valid_categories:
                if valid in category or category in valid:
                    category = valid
                    break
            else:
                category = 'other'

        # OPTIMIZATION #2: Store in persistent Redis cache (TTL: 30 days)
        cache.set(role_key, json.dumps(category), ttl=2592000)

        return category

    except Exception as e:
        print(f"Error extracting role category with AI: {e}")
        return 'other'


def calculate_industry_match(cv: dict, jd: dict) -> int:
    """
    Calculate industry/domain matching score.
    Compares CV's industry experience vs JD's industry requirements.
    """
    # Extract JD industry from multiple sources (combine all)
    jd_industries = set()

    # Source 1: From domain expertise
    domain_info = jd.get('domain_expertise', {})
    if isinstance(domain_info, dict):
        industries = domain_info.get('industry', [])
        if isinstance(industries, list):
            jd_industries.update(i.lower().strip() for i in industries)

    # Source 2: From company type
    if 'company_type' in jd:
        jd_industries.add(jd['company_type'].lower().strip())

    # Source 3: ALWAYS extract from company name (in addition to above)
    company_name = jd.get('company_name', '')
    if company_name:
        extracted_industries = extract_industries_with_ai(company_name)
        if extracted_industries:
            jd_industries.update(i.lower().strip() for i in extracted_industries)

    # Still no industries? Return neutral score
    if not jd_industries:
        return 50

    # OPTIMIZATION: Extract CV industries from work experience using parallel AI calls
    cv_industries = set()
    work_exp = cv.get('work_experience', [])

    if isinstance(work_exp, list) and work_exp:
        # Collect ALL texts to extract (companies, roles, achievements)
        extraction_tasks = []

        for exp in work_exp:
            # Extract industries from company name
            if 'company' in exp:
                extraction_tasks.append(str(exp['company']))

            # Extract industries from role title
            if 'role' in exp:
                extraction_tasks.append(str(exp['role']))

            # Also check achievements for industry context
            if 'achievements' in exp and isinstance(exp['achievements'], list):
                achievements_text = ' '.join(str(a) for a in exp['achievements'][:2])
                if achievements_text.strip():
                    extraction_tasks.append(achievements_text)

        # PARALLEL EXECUTION: Run all extractions concurrently
        if extraction_tasks:
            with ThreadPoolExecutor(max_workers=min(len(extraction_tasks), 8)) as executor:
                results = list(executor.map(extract_industries_with_ai, extraction_tasks))

            # Aggregate all results
            for industries_list in results:
                cv_industries.update(industries_list)

    # OPTIMIZATION: Extract CV industries from PROJECTS (personal/portfolio/side projects)
    # Projects demonstrate domain interest and practical knowledge, especially for career changers
    projects = cv.get('projects', [])

    # DEBUG: Log projects found
    print(f"[DEBUG] Found {len(projects) if isinstance(projects, list) else 0} projects in CV")

    if isinstance(projects, list) and projects:
        project_tasks = []

        for proj in projects:
            if isinstance(proj, dict):
                # Extract industries from project name (e.g., "HealthTrack App" → Healthcare)
                if 'name' in proj:
                    project_tasks.append(str(proj['name']))

                # Extract industries from project description (e.g., "health tracking mobile app" → HealthTech)
                if 'description' in proj:
                    project_tasks.append(str(proj['description']))

                # Extract from technologies/tech stack (e.g., "WCAG accessibility" → Healthcare signal)
                if 'technologies' in proj and isinstance(proj['technologies'], list):
                    tech_text = ' '.join(str(t) for t in proj['technologies'][:5])  # Limit to first 5 to avoid noise
                    if tech_text.strip():
                        project_tasks.append(tech_text)

        # PARALLEL EXECUTION: Run all project extractions concurrently
        if project_tasks:
            with ThreadPoolExecutor(max_workers=min(len(project_tasks), 8)) as executor:
                results = list(executor.map(extract_industries_with_ai, project_tasks))

            # Aggregate project industry results
            for industries_list in results:
                cv_industries.update(industries_list)

            # DEBUG: Log extracted industries from projects
            print(f"[DEBUG] Extracted {len(cv_industries)} industries from projects: {cv_industries}")

    # OPTIMIZATION: Extract CV industries from CERTIFICATIONS
    # Certifications demonstrate formal domain knowledge and commitment to industry
    certifications = cv.get('certifications', [])

    if isinstance(certifications, list) and certifications:
        cert_tasks = []

        for cert in certifications:
            if isinstance(cert, dict):
                # Extract industries from certification name (e.g., "AWS Certified Solutions Architect" → Cloud)
                if 'name' in cert:
                    cert_tasks.append(str(cert['name']))

                # Extract from issuing organization (e.g., "Project Management Institute" → Project Management)
                if 'issuer' in cert:
                    cert_tasks.append(str(cert['issuer']))

                # Extract from certification description if available
                if 'description' in cert:
                    cert_tasks.append(str(cert['description']))

            elif isinstance(cert, str):
                # Handle simple string certifications
                cert_tasks.append(cert)

        # PARALLEL EXECUTION: Run all certification extractions concurrently
        if cert_tasks:
            with ThreadPoolExecutor(max_workers=min(len(cert_tasks), 8)) as executor:
                results = list(executor.map(extract_industries_with_ai, cert_tasks))

            # Aggregate certification industry results
            for industries_list in results:
                cv_industries.update(industries_list)

    # Calculate overlap using semantic embeddings
    if not cv_industries:
        return 0  # No industry experience found

    from core.embeddings import get_embedding, calculate_cosine_similarity

    # Convert sets to lists
    jd_industries_list = list(jd_industries)
    cv_industries_list = list(cv_industries)

    # Use hybrid matching: exact + semantic for non-exact matches
    matches = 0

    for jd_ind in jd_industries_list:
        # Check exact match first (fast)
        if jd_ind.lower() in [cv.lower() for cv in cv_industries_list]:
            matches += 1
            continue

        # No exact match - try semantic matching
        jd_embedding = get_embedding(jd_ind)

        best_similarity = 0.0
        best_cv_ind = ""
        for cv_ind in cv_industries_list:
            cv_embedding = get_embedding(cv_ind)
            similarity = calculate_cosine_similarity(jd_embedding, cv_embedding)
            if similarity > best_similarity:
                best_similarity = similarity
                best_cv_ind = cv_ind

        # Use adaptive threshold based on text length
        # E.g., "SaaS" (short) vs "Technology" (short) → threshold = 0.45
        threshold = get_adaptive_similarity_threshold(jd_ind, best_cv_ind)
        if best_similarity >= threshold:
            matches += 1

    if matches > 0:
        match_ratio = matches / len(jd_industries_list)
        return int(match_ratio * 100)

    return 0


def calculate_role_similarity(cv: dict, jd: dict) -> int:
    """
    Calculate role/job title similarity score.
    Compares CV's job roles vs JD's position title.
    """
    # Extract JD role
    jd_role = jd.get('position_title', '').lower().strip()

    if not jd_role:
        return 50  # Neutral if no position specified

    # Extract CV roles from work experience
    cv_roles = []
    work_exp = cv.get('work_experience', [])
    if isinstance(work_exp, list):
        for exp in work_exp:
            if 'role' in exp:
                cv_roles.append(str(exp['role']))

    if not cv_roles:
        return 0  # No work experience

    # OPTIMIZATION: Parallelize role category extraction for all roles
    # Categorize JD role + all CV roles concurrently
    all_roles = [jd_role] + cv_roles

    with ThreadPoolExecutor(max_workers=min(len(all_roles), 8)) as executor:
        categories = list(executor.map(extract_role_category_with_ai, all_roles))

    jd_category = categories[0]  # First result is JD role category
    cv_categories = categories[1:]  # Rest are CV role categories

    # Check if any CV role matches the category
    max_score = 0
    for cv_role, cv_category in zip(cv_roles, cv_categories):
        if jd_category and cv_category == jd_category:
            # Same category - high score
            max_score = max(max_score, 90)
        elif cv_category and jd_category and cv_category != jd_category and cv_category != 'other' and jd_category != 'other':
            # Different categories (both specific) - very low score
            max_score = max(max_score, 5)
        else:
            # Use semantic similarity as fallback (for 'other' categories or edge cases)
            try:
                from core.embeddings import calculate_hybrid_similarity
                similarity = calculate_hybrid_similarity(cv_role.lower(), jd_role, 'roles')
                max_score = max(max_score, int(similarity * 100))
            except:
                pass

    return min(100, max_score)


def calculate_category_scores_from_metrics(
    similarity_metrics: dict,
    parsed_cv: dict,
    parsed_jd: dict,
    language: str = 'english'
) -> dict[str, CategoryScore]:
    """
    Calculate category scores using hybrid approach (embeddings + rules).
    Much faster than asking Gemini - essentially instant.
    """

    # Hard Skills (30% weight - reduced from 35%) - from hybrid embedding matching
    hard_skills_score = int(similarity_metrics['skills_cosine_similarity'] * 100)

    # Soft Skills (10% weight - reduced from 15%) - using fuzzy token-based matching
    soft_skills_score = calculate_soft_skills_match(
        parsed_cv.get('soft_skills', []),
        parsed_jd.get('soft_skills_required', []),
        language=language
    )

    # Experience Level (15% weight - reduced from 20%) - from years comparison with domain relevance
    cv_years = calculate_total_experience_years(parsed_cv)
    jd_years = parsed_jd.get('experience_years_required', 0)
    if jd_years > 0:
        experience_ratio = min(1.2, cv_years / jd_years)  # Cap at 1.2 (20% bonus for extra experience)
        # Lower base multiplier from 85 to 70
        experience_score = int(experience_ratio * 70)  # More conservative
    else:
        experience_score = 0  # Changed from 70 to 0
    experience_score = min(100, experience_score)

    # Domain Expertise (10% weight - reduced from 15%) - from keyword matching
    domain_score = calculate_domain_match(parsed_cv, parsed_jd)

    # Industry Match (15% weight - NEW!) - from industry/sector matching
    industry_score = calculate_industry_match(parsed_cv, parsed_jd)

    # Role Similarity (10% weight - NEW!) - from job title/role matching
    role_score = calculate_role_similarity(parsed_cv, parsed_jd)

    # Portfolio Quality (7% weight - reduced from 10%) - from achievements & projects
    portfolio_score = calculate_portfolio_quality(parsed_cv)

    # Location/Logistics (3% weight - reduced from 5%) - from location match
    logistics_score = calculate_logistics_match(parsed_cv, parsed_jd)

    return {
        "hard_skills": CategoryScore(
            score=hard_skills_score,
            weight=0.30,  # 30%
            status=get_status_label(hard_skills_score)
        ),
        "soft_skills": CategoryScore(
            score=soft_skills_score,
            weight=0.10,  # 10%
            status=get_status_label(soft_skills_score)
        ),
        "experience_level": CategoryScore(
            score=experience_score,
            weight=0.15,  # 15%
            status=get_status_label(experience_score)
        ),
        "domain_expertise": CategoryScore(
            score=domain_score,
            weight=0.10,  # 10%
            status=get_status_label(domain_score)
        ),
        "industry_match": CategoryScore(
            score=industry_score,
            weight=0.15,  # 15% (NEW!)
            status=get_status_label(industry_score)
        ),
        "role_similarity": CategoryScore(
            score=role_score,
            weight=0.10,  # 10% (NEW!)
            status=get_status_label(role_score)
        ),
        "portfolio_quality": CategoryScore(
            score=portfolio_score,
            weight=0.07,  # 7%
            status=get_status_label(portfolio_score)
        ),
        "location_logistics": CategoryScore(
            score=logistics_score,
            weight=0.03,  # 3%
            status=get_status_label(logistics_score)
        )
    }


def calculate_weighted_score(category_scores: dict[str, CategoryScore]) -> int:
    """Calculate overall weighted score from category scores"""
    total = sum(
        details.score * details.weight
        for details in category_scores.values()
    )
    return int(round(total))


def get_overall_status(score: int) -> str:
    """Map overall score to user-friendly status label"""
    if score >= 75:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Moderate"
    else:
        return "Needs Work"


def generate_score_message(overall_score: int, gaps: dict, strengths: list, overall_status: str) -> dict:
    """
    Generate encouraging, personalized messages for the compatibility score using Gemini.

    Args:
        overall_score: The numeric score (0-100)
        gaps: Categorized gaps from analysis
        strengths: List of candidate strengths
        overall_status: The status label (STRONG FIT, MODERATE FIT, etc.)

    Returns:
        dict with 'title' and 'subtitle' keys
    """
    # Summarize strengths (max 3) WITH EVIDENCE (project/company names)
    strengths_summary = ""
    if strengths and len(strengths) > 0:
        top_strengths = strengths[:3]
        strengths_summary = "\n".join([
            f"- {s.get('title', 'Unknown')}: {s.get('description', '')[:80]}\n  Evidence: {s.get('evidence', 'N/A')[:100]}"
            for s in top_strengths
        ])
    else:
        strengths_summary = "- (No specific strengths identified yet)"

    # Summarize critical gaps (max 3) WITH CURRENT vs REQUIRED
    critical_gaps = gaps.get('critical', [])
    critical_gaps_summary = ""
    if critical_gaps:
        top_gaps = critical_gaps[:3]
        critical_gaps_summary = "\n".join([
            f"- {g.get('title', 'Unknown')}\n  Current: '{g.get('current', 'None')}' → Required: '{g.get('required', 'Unknown')}'\n  Impact: {g.get('impact', 'N/A')}"
            for g in top_gaps
        ])
    else:
        critical_gaps_summary = "- (No critical gaps identified)"

    # Guidance based on score range - BE SPECIFIC AND HONEST
    score_guidance = ""
    if overall_score >= 75:
        score_guidance = "Strong match - reference SPECIFIC projects/companies that align with job requirements"
    elif overall_score >= 60:
        score_guidance = "Solid foundation - acknowledge specific strengths, be clear about specific gaps to address"
    elif overall_score >= 40:
        score_guidance = "Significant gaps - be honest about major missing skills, reference any relevant projects"
    else:
        score_guidance = "Major mismatch - use phrases like 'significant mismatch' or 'substantial gaps', list specific missing requirements"

    prompt = f"""You are a career advisor providing SPECIFIC, HONEST feedback about job compatibility.

CRITICAL INSTRUCTION: You MUST copy exact company names, project names, numbers, and technologies from the Evidence field below. DO NOT generalize. DO NOT say "your experience" - say "your work at [Company]" or "your [Project] project".

SCORE: {overall_score}%
STATUS: {overall_status}

CANDIDATE STRENGTHS (USE EXACT NAMES FROM EVIDENCE):
{strengths_summary}

KEY GAPS TO ADDRESS (USE EXACT REQUIRED SKILLS):
{critical_gaps_summary}

TASK: Generate a title and subtitle that references SPECIFIC evidence from above.

TONE REQUIREMENTS:
- Encouraging & growth-focused: Emphasize potential and learning opportunities
- Honest & realistic: Acknowledge challenges without sugar-coating
- Action-oriented: Suggest next steps or focus areas
- Achievement-focused: Highlight existing strengths and experience

SCORE RANGE GUIDANCE ({overall_score}%):
{score_guidance}

CRITICAL PERSONALIZATION REQUIREMENTS (MANDATORY - DO NOT SKIP):
1. **COPY company names from Evidence**: e.g., "TechStartup Inc.", "Digital Solutions", "HealthTrack App"
2. **COPY numbers from Evidence**: e.g., "1M+ users", "25% improvement", "5 years"
3. **COPY exact missing skills**: e.g., "GraphQL", "FinTech domain", "Kubernetes"
4. **Use format**: "Your [specific thing] from [company/project] is strong, but you need [exact gap list]"
5. **For scores <40%**: Say "significant mismatch" or "major gaps" - be BRUTALLY honest

EXAMPLES (SPECIFIC, NOT GENERIC):

For 78% - Backend role, strong Python + microservices:
{{
  "title": "Strong Match for Backend Engineering",
  "subtitle": "Your microservices work at TechStartup (1M+ users) and AWS experience align well—minor gaps in Kubernetes can be addressed"
}}

For 52% - Full stack role, has Python but missing GraphQL:
{{
  "title": "Solid Backend Skills, Frontend Gaps",
  "subtitle": "Your Python and PostgreSQL expertise from Digital Solutions is valuable, but you'll need to learn GraphQL and TypeScript"
}}

For 28% - FinTech role, has projects but no domain knowledge:
{{
  "title": "Technical Skills Present, Domain Gap",
  "subtitle": "Your HealthTrack App project shows product sense, but you lack the required FinTech domain knowledge and compliance experience"
}}

For 15% - Senior role, junior experience:
{{
  "title": "Significant Experience Mismatch",
  "subtitle": "Your 2 years of experience doesn't meet the 5+ year requirement—focus on similar roles at mid-level first"
}}

IMPORTANT:
- Title: 3-8 words, engaging but HONEST (use "mismatch" for low scores)
- Subtitle: 15-30 words, SPECIFIC (mention projects/companies/skills by name)
- Use format: "Your [specific thing from evidence] is good for [X], but you need [specific gaps]"
- For low scores: Be direct about mismatches, don't sugarcoat

Return ONLY valid JSON with this exact structure:
{{
  "title": "Your engaging title here",
  "subtitle": "Your specific, actionable subtitle here"
}}"""

    try:
        # Use gemini-2.5-flash-lite with JSON response mode
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config={
                "temperature": 0.7,  # Slightly creative for varied messages
                "response_mime_type": "application/json"
            }
        )

        result = json.loads(response.text)

        # Validate response has required fields
        if "title" in result and "subtitle" in result:
            return {
                "title": result["title"],
                "subtitle": result["subtitle"]
            }
        else:
            # Fallback if AI doesn't return proper format
            return get_fallback_message(overall_score)

    except Exception as e:
        print(f"Error generating score message: {e}")
        return get_fallback_message(overall_score)


def get_fallback_message(score: int) -> dict:
    """Fallback messages if AI generation fails"""
    if score >= 75:
        return {
            "title": "Excellent Match for This Role",
            "subtitle": "Your experience and skills align strongly with the position requirements"
        }
    elif score >= 60:
        return {
            "title": "Strong Potential Candidate",
            "subtitle": "You have a solid foundation—let's identify areas to strengthen your application"
        }
    elif score >= 40:
        return {
            "title": "Promising Foundation to Build On",
            "subtitle": "Your relevant experience provides a starting point—answering questions may reveal more strengths"
        }
    else:
        return {
            "title": "Growth Opportunity Identified",
            "subtitle": "This role presents a chance to expand your skillset—let's explore your transferable experience"
        }


# ===== COVER LETTER GENERATION =====

def convert_parsed_resume_to_text(parsed_resume: dict) -> str:
    """
    Convert structured parsed resume to plain text format for AI processing.
    Extracts all 12 sections from the parsed resume.
    """
    personal_info = parsed_resume.get('personal_info', {})

    text = f"{personal_info.get('name', '')}\n"
    if personal_info.get('email'): text += f"{personal_info['email']} | "
    if personal_info.get('phone'): text += f"{personal_info['phone']} | "
    if personal_info.get('location'): text += personal_info['location']
    text += '\n'

    # Social Links
    if personal_info.get('linkedin'): text += f"LinkedIn: {personal_info['linkedin']}\n"
    if personal_info.get('github'): text += f"GitHub: {personal_info['github']}\n"
    if personal_info.get('portfolio'): text += f"Portfolio: {personal_info['portfolio']}\n"
    text += '\n'

    # Professional Summary
    if parsed_resume.get('professional_summary'):
        text += f"PROFESSIONAL SUMMARY\n{parsed_resume['professional_summary']}\n\n"

    # Work Experience
    if parsed_resume.get('experience') and len(parsed_resume['experience']) > 0:
        text += "WORK EXPERIENCE\n"
        for job in parsed_resume['experience']:
            text += f"{job.get('position') or job.get('role')} at {job.get('company')}\n"
            if job.get('location'): text += f"{job['location']}\n"
            text += f"{job.get('start_date')} - {job.get('end_date', 'Present')} ({job.get('duration', '')})\n"
            if job.get('achievements'):
                for achievement in job['achievements']:
                    text += f"• {achievement}\n"
            text += '\n'

    # Projects
    if parsed_resume.get('projects') and len(parsed_resume['projects']) > 0:
        text += "PROJECTS\n"
        for project in parsed_resume['projects']:
            text += f"{project.get('name') or project.get('title')}\n"
            text += f"{project.get('description')}\n"
            if project.get('technologies'):
                text += f"Technologies: {', '.join(project['technologies'])}\n"
            if project.get('link'): text += f"Link: {project['link']}\n"
            text += '\n'

    # Technical Skills
    if parsed_resume.get('technical_skills') and len(parsed_resume['technical_skills']) > 0:
        text += f"TECHNICAL SKILLS\n{', '.join(parsed_resume['technical_skills'])}\n\n"

    # Tools
    if parsed_resume.get('tools') and len(parsed_resume['tools']) > 0:
        text += f"TOOLS & PLATFORMS\n{', '.join(parsed_resume['tools'])}\n\n"

    # Soft Skills
    if parsed_resume.get('soft_skills') and len(parsed_resume['soft_skills']) > 0:
        text += f"SOFT SKILLS\n{', '.join(parsed_resume['soft_skills'])}\n\n"

    # Skills (from skills object if structured differently)
    if parsed_resume.get('skills'):
        skills = parsed_resume['skills']
        if skills.get('hard_skills') and len(skills['hard_skills']) > 0:
            text += "HARD SKILLS\n"
            text += ', '.join([s.get('skill') for s in skills['hard_skills']]) + '\n\n'

    # Education
    if parsed_resume.get('education') and len(parsed_resume['education']) > 0:
        text += "EDUCATION\n"
        for edu in parsed_resume['education']:
            text += f"{edu.get('degree')} - {edu.get('institution')}\n"
            if edu.get('location'): text += f"{edu['location']}\n"
            if edu.get('graduation_date'): text += f"Graduated: {edu['graduation_date']}\n"
            if edu.get('gpa'): text += f"GPA: {edu['gpa']}\n"
            if edu.get('honors'): text += f"{edu['honors']}\n"
            text += '\n'

    # Certifications
    if parsed_resume.get('certifications') and len(parsed_resume['certifications']) > 0:
        text += "CERTIFICATIONS\n"
        for cert in parsed_resume['certifications']:
            text += f"• {cert}\n"
        text += '\n'

    # Languages
    if parsed_resume.get('languages') and len(parsed_resume['languages']) > 0:
        text += "LANGUAGES\n"
        for lang in parsed_resume['languages']:
            text += f"• {lang.get('language')} - {lang.get('proficiency')}\n"
        text += '\n'

    # Internships
    if parsed_resume.get('internships') and len(parsed_resume['internships']) > 0:
        text += "INTERNSHIPS\n"
        for internship in parsed_resume['internships']:
            text += f"{internship.get('role')} at {internship.get('company')}\n"
            text += f"Duration: {internship.get('duration')}\n"
            text += f"{internship.get('description')}\n\n"

    # Publications
    if parsed_resume.get('publications') and len(parsed_resume['publications']) > 0:
        text += "PUBLICATIONS\n"
        for pub in parsed_resume['publications']:
            text += f"\"{pub.get('title')}\" - {pub.get('publication')}\n"
            if pub.get('date'): text += f"Published: {pub['date']}\n"
            if pub.get('link'): text += f"Link: {pub['link']}\n"
            text += '\n'

    return text


def generate_cover_letter(
    parsed_resume: dict,
    parsed_jd: dict,
    score_data: dict = None
) -> str:
    """
    Generate a personalized cover letter using Gemini AI.

    Args:
        parsed_resume: The parsed/rewritten resume in structured format
        parsed_jd: Parsed job description
        score_data: Optional score analysis data (gaps and strengths)

    Returns:
        str: Generated cover letter (300-400 words, 4 paragraphs)
    """
    # Convert parsed resume to text
    rewritten_resume = convert_parsed_resume_to_text(parsed_resume)

    # Extract key information from JD
    company_name = parsed_jd.get('company', 'the company')
    job_title = parsed_jd.get('job_title', 'this position')

    # Build context from score data if available
    strengths_context = ""
    gaps_context = ""

    if score_data:
        # Get top 2 strengths
        strengths = score_data.get('strengths', [])[:2]
        if strengths:
            strengths_context = "TOP STRENGTHS:\n" + "\n".join([
                f"- {s.get('title')}: {s.get('description')[:80]}\n  Evidence: {s.get('evidence', 'N/A')[:100]}"
                for s in strengths
            ])

        # Get top 2 gaps to address
        critical_gaps = score_data.get('gaps', {}).get('critical', [])[:2]
        if critical_gaps:
            gaps_context = "KEY GAPS TO ADDRESS:\n" + "\n".join([
                f"- {g.get('title')}: {g.get('description', '')[:80]}"
                for g in critical_gaps
            ])

    prompt = f"""You are a professional career writer creating a compelling cover letter.

TASK: Write a personalized 300-400 word cover letter with EXACTLY 4 paragraphs.

INPUTS:
COMPANY: {company_name}
ROLE: {job_title}

REWRITTEN RESUME:
{rewritten_resume[:1500]}

{strengths_context}

{gaps_context}

CRITICAL REQUIREMENTS:
1. **Tone**: Professional, enthusiastic, and confident
2. **Length**: 300-400 words, EXACTLY 4 paragraphs
3. **Personalization**: Use SPECIFIC details from the resume (company names, projects, numbers, achievements)
4. **Structure**:
   - Paragraph 1: Professional opening expressing genuine interest in the role and company
   - Paragraph 2: Highlight 2-3 most relevant experiences/achievements with specific examples
   - Paragraph 3: Address how you meet key requirements OR show growth mindset for any gaps
   - Paragraph 4: Confident closing with enthusiasm and call to action

5. **Content Focus**:
   - Reference specific job requirements
   - Tell a brief professional story
   - Highlight strengths with evidence
   - Show awareness of any gaps with growth mindset
   - Use active, achievement-focused language

6. **Formatting**: Return ONLY the cover letter text, no extra fields. Use professional business letter formatting.

EXAMPLE STRUCTURE (adapt to this candidate):

Dear Hiring Manager,

I am writing to express my strong interest in the [Job Title] position at [Company]. With [X years] of experience in [field] and a proven track record of [specific achievement], I am excited about the opportunity to contribute to [company's mission/goal].

In my recent role at [Company], I [specific achievement with numbers]. For example, [concrete example from resume]. Additionally, my work on [project name] resulted in [measurable outcome], demonstrating my ability to [relevant skill for job].

I am particularly drawn to this role because [reason related to job requirements]. While I am actively developing my expertise in [gap area if any], my strong foundation in [strength areas] and quick learning ability position me well to excel. I am committed to [growth statement].

I would welcome the opportunity to discuss how my background in [key areas] aligns with [Company]'s needs. Thank you for considering my application. I look forward to speaking with you soon.

Sincerely,
[Candidate Name]

NOW GENERATE THE COVER LETTER:"""

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config={
                "temperature": 0.7,
                "response_mime_type": "text/plain"
            }
        )

        cover_letter = response.text.strip()

        # Validate it's not empty
        if cover_letter and len(cover_letter) > 100:
            return cover_letter
        else:
            return get_fallback_cover_letter(company_name, job_title)

    except Exception as e:
        print(f"Error generating cover letter: {e}")
        return get_fallback_cover_letter(company_name, job_title)


def get_fallback_cover_letter(company_name: str, job_title: str) -> str:
    """Fallback cover letter template if AI generation fails"""
    return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. After reviewing the role requirements and learning about your organization, I am excited about the opportunity to contribute my skills and experience to your team.

Throughout my career, I have developed a comprehensive skill set that aligns well with the requirements of this position. My experience has equipped me with the technical expertise and professional capabilities necessary to make meaningful contributions from day one. I have consistently delivered results in fast-paced environments and am passionate about continuous learning and growth.

I am particularly drawn to this opportunity because it represents an excellent match between my background and your needs. I am confident that my combination of technical skills, problem-solving abilities, and collaborative approach would enable me to add value to your team while continuing to develop professionally.

I would welcome the opportunity to discuss how my qualifications align with {company_name}'s objectives. Thank you for considering my application. I look forward to the possibility of speaking with you soon.

Sincerely,
[Your Name]"""


@app.post("/api/calculate-score", response_model=ScoreResponse)
async def calculate_score(request: ScoreRequest, bypass_cache: bool = False):
    """
    Calculate compatibility score between CV and JD using hybrid approach:
    - Vector embeddings for quantitative similarity
    - Gemini for qualitative analysis

    OPTIMIZATION: Full result caching with CV+JD hash (99% speedup on cache hits)
    """
    try:
        start_time = time.time()

        # OPTIMIZATION #1: Check cache first (99% speedup on cache hits)
        # Generate deterministic cache key from CV + JD content + language
        cv_hash = hashlib.md5(json.dumps(request.parsed_cv, sort_keys=True).encode()).hexdigest()
        jd_hash = hashlib.md5(json.dumps(request.parsed_jd, sort_keys=True).encode()).hexdigest()
        cache_key = f"score:{cv_hash}:{jd_hash}:{request.language}"

        # Check cache (skip if bypass_cache=True)
        if not bypass_cache:
            cached_result = cache.get(cache_key)
            if cached_result:
                # Deserialize cached result
                result_dict = json.loads(cached_result) if isinstance(cached_result, str) else cached_result
                # Update time to show it was instant
                result_dict['time_seconds'] = round(time.time() - start_time, 3)
                return ScoreResponse(**result_dict)

        # Phase 1: Calculate embedding-based similarity (fast - ~1-2s)
        similarity_metrics = calculate_overall_compatibility(
            request.parsed_cv,
            request.parsed_jd
        )

        # Phase 2a: Calculate category scores using hybrid approach (instant!)
        # This replaces asking Gemini for category scores - much faster
        category_scores = calculate_category_scores_from_metrics(
            similarity_metrics,
            request.parsed_cv,
            request.parsed_jd,
            language=request.language
        )
        overall_score = calculate_weighted_score(category_scores)
        overall_status = get_overall_status(overall_score)

        # Phase 2b: Full Gemini AI analysis for gaps + strengths (ALWAYS)
        # Convert to TOON format for token efficiency (40-50% reduction)
        cv_toon = to_toon(request.parsed_cv)
        jd_toon = to_toon(request.parsed_jd)

        # Use compressed prompt (60% smaller - only gaps + strengths)
        analysis_prompt = get_compressed_gap_analysis_prompt(
            cv_toon=cv_toon,
            jd_toon=jd_toon,
            similarity_metrics=similarity_metrics,
            overall_score=overall_score,  # Pass score for adaptive gap requirements
            language=request.language
        )

        model_name = "gemini-2.5-flash-lite"
        # Use explicit prompt caching for 90% discount on repeated prompts
        response = generate_with_cache(
            prompt=analysis_prompt,
            model=model_name,
            temperature=0.1,
            cache_ttl=300  # 5 minutes cache
        )

        # Parse Gemini response
        cleaned_text = response.text.strip()
        if cleaned_text.startswith("```"):
            lines = cleaned_text.split("\n")
            if len(lines) > 1:
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned_text = "\n".join(lines).strip()

        analysis_result = json.loads(cleaned_text)

        elapsed_time = time.time() - start_time

        # Parse categorized gaps
        gaps_data = analysis_result.get("gaps", {})
        categorized_gaps = CategorizedGaps(
            critical=[GapItem(**gap) for gap in gaps_data.get("critical", [])],
            important=[GapItem(**gap) for gap in gaps_data.get("important", [])],
            nice_to_have=[GapItem(**gap) for gap in gaps_data.get("nice_to_have", [])],
            logistical=[GapItem(**gap) for gap in gaps_data.get("logistical", [])]
        )

        # Parse strengths
        strengths_data = analysis_result.get("strengths", [])
        strengths = [StrengthItem(**strength) for strength in strengths_data]

        # Parse application viability
        viability_data = analysis_result.get("application_viability", {})
        application_viability = ApplicationViability(**viability_data)

        # Generate AI-powered encouraging message for the score
        score_message_dict = generate_score_message(
            overall_score=overall_score,
            gaps=gaps_data,
            strengths=strengths_data,
            overall_status=overall_status
        )
        score_message = ScoreMessage(**score_message_dict)

        # Build response
        response = ScoreResponse(
            success=True,
            overall_score=overall_score,  # From hybrid calculation
            overall_status=overall_status,  # From hybrid calculation
            score_message=score_message,  # AI-generated encouraging message
            category_scores=category_scores,  # From hybrid calculation
            gaps=categorized_gaps,  # From Gemini
            strengths=strengths,  # From Gemini
            application_viability=application_viability,  # From Gemini
            similarity_metrics=similarity_metrics,
            time_seconds=round(elapsed_time, 3),
            model=model_name
        )

        # OPTIMIZATION #1: Store in cache (TTL: 30 days = 2592000 seconds)
        # This provides 99% speedup on subsequent requests with same CV+JD
        cache.set(cache_key, json.dumps(response.dict()), ttl=2592000)

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating score: {str(e)}"
        )

@app.post("/api/generate-questions", response_model=GenerateQuestionsResponse)
async def generate_questions(request: GenerateQuestionsRequest):
    """
    Phase 4: Generate personalized questions based on gaps from Phase 3.
    Uses RAG (Qdrant) to find similar past experiences and improve question quality.
    """
    try:
        start_time = time.time()

        # Step 1: Initialize Qdrant manager
        qdrant = get_qdrant_manager()

        # Step 2: Extract gaps from score_result
        gaps = request.score_result.get("gaps", {})
        critical_gaps = gaps.get("critical", [])
        important_gaps = gaps.get("important", [])

        # Step 3: Search Qdrant for similar experiences (RAG)
        rag_context = []
        rag_used = False

        # Search for experiences related to each critical and important gap
        for gap in critical_gaps + important_gaps[:3]:  # Limit to avoid too much context
            gap_title = gap.get("title", "")
            gap_description = gap.get("description", "")
            search_query = f"{gap_title}: {gap_description}"

            similar_experiences = qdrant.search_similar_experiences(
                query=search_query,
                limit=2,  # Top 2 similar experiences per gap
                score_threshold=0.7  # Only high-quality matches
            )

            if similar_experiences:
                rag_context.extend(similar_experiences)
                rag_used = True

        # Remove duplicates and limit total RAG context
        seen_texts = set()
        unique_rag_context = []
        for exp in rag_context:
            if exp['text'] not in seen_texts:
                seen_texts.add(exp['text'])
                unique_rag_context.append(exp)
                if len(unique_rag_context) >= 5:  # Max 5 RAG examples
                    break

        # Step 4: Convert CV and JD to TOON format
        cv_toon = to_toon(request.parsed_cv)
        jd_toon = to_toon(request.parsed_jd)

        # Step 5: Generate question prompt
        overall_score = request.score_result.get("overall_score", None)
        question_prompt = get_question_generation_prompt(
            cv_toon=cv_toon,
            jd_toon=jd_toon,
            gaps=gaps,
            rag_context=unique_rag_context,
            overall_score=overall_score,  # Pass score for adaptive question count
            language=request.language
        )

        # Step 6: Call Gemini to generate questions (with explicit prompt caching)
        model_name = "gemini-2.5-flash-lite"  # Faster model for better performance
        response = generate_with_cache(
            prompt=question_prompt,
            model=model_name,
            temperature=0.3,  # Balanced creativity and consistency
            cache_ttl=300  # 5 minutes cache
        )

        # Step 7: Parse response
        cleaned_text = response.text.strip()
        if cleaned_text.startswith("```"):
            lines = cleaned_text.split("\n")
            if len(lines) > 1:
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned_text = "\n".join(lines).strip()

        questions_data = json.loads(cleaned_text)

        # Step 8: Parse and validate questions
        questions = []
        for q_data in questions_data.get("questions", []):
            question = QuestionItem(**q_data)
            questions.append(question)

        # Step 9: Calculate counts by priority
        critical_count = sum(1 for q in questions if q.priority == "CRITICAL")
        high_count = sum(1 for q in questions if q.priority == "HIGH")
        medium_count = sum(1 for q in questions if q.priority == "MEDIUM")

        elapsed_time = time.time() - start_time

        return GenerateQuestionsResponse(
            success=True,
            questions=questions,
            total_questions=len(questions),
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            rag_context_used=rag_used,
            time_seconds=round(elapsed_time, 3),
            model=model_name
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating questions: {str(e)}"
        )


@app.post("/api/transcribe-audio", response_model=TranscribeAudioResponse)
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """
    Phase 4: Transcribe audio answer using OpenAI Whisper API.
    Accepts audio file (webm, mp3, wav, m4a, etc.) and returns transcribed text.
    """
    start_time = time.time()
    temp_file_path = None

    try:
        # Validate file
        if not audio_file:
            raise HTTPException(status_code=400, detail="No audio file provided")

        # Check file size (max 25MB for Whisper API)
        content = await audio_file.read()
        file_size_mb = len(content) / (1024 * 1024)
        if file_size_mb > 25:
            raise HTTPException(
                status_code=400,
                detail=f"File too large ({file_size_mb:.1f}MB). Maximum size is 25MB."
            )

        # Get file extension from filename or default to webm
        file_extension = Path(audio_file.filename).suffix if audio_file.filename else ".webm"
        if not file_extension:
            file_extension = ".webm"

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Try Parakeet first (if enabled), fallback to Whisper
        use_parakeet = os.getenv("USE_PARAKEET", "false").lower() == "true"
        parakeet_url = os.getenv("PARAKEET_URL", "http://parakeet:8002")
        model_used = "whisper-1"

        if use_parakeet:
            try:
                # Call Parakeet service
                with open(temp_file_path, "rb") as audio_file_obj:
                    parakeet_response = httpx.post(
                        f"{parakeet_url}/transcribe",
                        files={"file": (audio_file.filename, audio_file_obj, audio_file.content_type)},
                        data={"language": request.language} if request.language else {},
                        timeout=60.0
                    )

                if parakeet_response.status_code == 200:
                    parakeet_data = parakeet_response.json()
                    transcribed_text = parakeet_data["text"]
                    model_used = "parakeet-v3"
                    print(f"✅ Parakeet transcription successful ({parakeet_data.get('duration', 0):.2f}s)")
                else:
                    raise Exception(f"Parakeet returned status {parakeet_response.status_code}")

            except Exception as parakeet_error:
                print(f"⚠️  Parakeet failed, falling back to Whisper: {parakeet_error}")
                # Fallback to Whisper
                with open(temp_file_path, "rb") as audio_file_obj:
                    transcription = openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file_obj,
                        response_format="text"
                    )
                transcribed_text = transcription.strip() if isinstance(transcription, str) else transcription.text.strip()
                model_used = "whisper-1 (fallback)"
        else:
            # Use OpenAI Whisper API directly
            with open(temp_file_path, "rb") as audio_file_obj:
                transcription = openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file_obj,
                    response_format="text"
                )
            transcribed_text = transcription.strip() if isinstance(transcription, str) else transcription.text.strip()

        elapsed_time = time.time() - start_time

        return TranscribeAudioResponse(
            success=True,
            transcribed_text=transcribed_text,
            time_seconds=round(elapsed_time, 3),
            model=model_used
        )

    except HTTPException:
        raise
    except Exception as e:
        elapsed_time = time.time() - start_time
        return TranscribeAudioResponse(
            success=False,
            transcribed_text="",
            time_seconds=round(elapsed_time, 3),
            model="whisper-1",
            error=str(e)
        )
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                print(f"Warning: Failed to delete temporary file {temp_file_path}: {cleanup_error}")


@app.post("/api/evaluate-answer", response_model=EvaluateAnswerResponse)
async def evaluate_answer(request: EvaluateAnswerRequest):
    """
    Evaluate the quality of a single answer using AI.
    Returns quality score (1-10), issues, strengths, and improvement suggestions.
    """
    start_time = time.time()

    try:
        # Create evaluation prompt
        evaluation_prompt = f"""You are an expert career coach evaluating a candidate's answer to a job application question.

**Question Context:**
Gap Title: {request.gap_info.get('title', 'N/A')}
Gap Description: {request.gap_info.get('description', 'N/A')}

**Question Asked:**
{request.question_text}

**Candidate's Answer:**
{request.answer_text}

**Your Task:**
Evaluate this answer on a scale of 1-10 based on:
1. Specificity (mentions concrete technologies, tools, or methodologies)
2. Evidence (includes metrics, results, timeframes, or tangible outcomes)
3. Professional language (uses action verbs, clear structure)
4. Relevance (directly addresses the gap/question)

**Scoring Guidelines:**
- 1-3: Very weak (vague, no details, generic)
- 4-6: Needs improvement (some details but missing key elements)
- 7-8: Good (specific, has evidence, professional)
- 9-10: Excellent (highly specific, strong metrics, exemplary)

Return a JSON object with:
{{
  "quality_score": <number 1-10>,
  "quality_issues": [<list of specific issues found>],
  "quality_strengths": [<list of positive aspects>],
  "improvement_suggestions": [<concrete suggestions for improvement>]
}}

**CRITICAL: Provide STRONG, SPECIFIC examples with REAL numbers, NOT generic placeholders:**

Examples of WEAK vs STRONG suggestions:

❌ WEAK: "Add metrics (e.g., number of users, success rate)"
✅ STRONG: "Add specific metrics like 'Tested with 50 beta users achieving 87% query resolution rate' or 'Processed 2,000+ daily requests with <300ms average response time'"

❌ WEAK: "Quantify the impact"
✅ STRONG: "Specify measurable business outcomes like 'Reduced support tickets by 42% (from 120 to 70 per week)' or 'Saved team 15 hours/week in manual customer responses'"

❌ WEAK: "Mention the timeline"
✅ STRONG: "Add project scope and duration like '6-month development across 3 agile sprints' or 'Delivered MVP in 8 weeks, scaled to production in 4 months'"

❌ WEAK: "Include technical details"
✅ STRONG: "Specify architecture and scale like 'Built microservices handling 10K requests/sec using Node.js + Redis' or 'Deployed on AWS ECS with auto-scaling (5-20 containers based on load)'"

**Rules for every suggestion:**
1. Use ACTION VERBS (Add, Specify, Include, Describe)
2. Provide REALISTIC NUMBERS (42%, 500 users, 8 weeks, $85K, 15 hours/week)
3. Show PROFESSIONAL SCALE (team size, business impact, technical metrics)
4. Give 2-3 specific example formats candidate can copy/adapt
5. Avoid vague terms: "many", "some", "significant", "various"

Language: {request.language}
"""

        # Call Gemini to evaluate
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=evaluation_prompt
        )

        # Extract JSON from response
        response_text = response.text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        # Parse JSON
        evaluation_data = json.loads(response_text)

        quality_score = evaluation_data.get("quality_score", 5)
        quality_issues = evaluation_data.get("quality_issues", [])
        quality_strengths = evaluation_data.get("quality_strengths", [])
        improvement_suggestions = evaluation_data.get("improvement_suggestions", [])

        elapsed_time = time.time() - start_time

        return EvaluateAnswerResponse(
            success=True,
            question_id=request.question_id,
            answer_text=request.answer_text,
            quality_score=quality_score,
            quality_issues=quality_issues,
            quality_strengths=quality_strengths,
            improvement_suggestions=improvement_suggestions,
            is_acceptable=quality_score >= 7,
            time_seconds=round(elapsed_time, 2),
            model="gemini-2.0-flash-exp"
        )

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        print(f"Response text: {response_text}")
        return EvaluateAnswerResponse(
            success=False,
            question_id=request.question_id,
            answer_text=request.answer_text,
            quality_score=5,
            quality_issues=["Failed to parse evaluation response"],
            quality_strengths=[],
            improvement_suggestions=["Try providing more specific details"],
            is_acceptable=False,
            time_seconds=round(time.time() - start_time, 2),
            model="gemini-2.0-flash-exp",
            error=f"JSON parse error: {str(e)}"
        )
    except Exception as e:
        print(f"Error evaluating answer: {str(e)}")
        return EvaluateAnswerResponse(
            success=False,
            question_id=request.question_id,
            answer_text=request.answer_text,
            quality_score=0,
            quality_issues=[],
            quality_strengths=[],
            improvement_suggestions=[],
            is_acceptable=False,
            time_seconds=round(time.time() - start_time, 2),
            model="gemini-2.0-flash-exp",
            error=str(e)
        )


@app.post("/api/submit-answers", response_model=SubmitAnswersResponse)
async def submit_answers(request: SubmitAnswersRequest):
    """
    Phase 4: Analyze candidate answers, extract uncovered experiences,
    update CV, and recalculate compatibility score.
    """
    start_time = time.time()

    try:
        # Step 1: Format questions and answers for analysis
        questions_and_answers = []
        for question in request.questions:
            # Find the corresponding answer
            answer = next(
                (a for a in request.answers if a.question_id == question.id),
                None
            )
            if answer:
                questions_and_answers.append({
                    "number": question.number,
                    "title": question.title,
                    "priority": question.priority,
                    "impact": question.impact,
                    "question": question.question_text,
                    "answer": answer.answer_text,
                    "answer_type": answer.answer_type
                })

        # Step 2: Convert CV/JD to TOON format
        cv_toon = to_toon(request.parsed_cv)
        jd_toon = to_toon(request.parsed_jd)

        # Step 3: Generate answer analysis prompt
        analysis_prompt = get_answer_analysis_prompt(
            cv_toon, jd_toon, questions_and_answers, request.language
        )

        # Step 4: Call Gemini to analyze answers
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=analysis_prompt,
            config={"temperature": 0.3}
        )

        # Step 5: Parse the analysis
        response_text = response.text.strip()
        cleaned_text = response_text.strip('```json').strip('```').strip()
        analysis_data = json.loads(cleaned_text)

        uncovered_experiences_list = analysis_data.get("uncovered_experiences", [])
        cv_updates = analysis_data.get("cv_updates", {})

        # Step 6: Update the parsed CV with new information
        updated_cv = request.parsed_cv.copy()

        # Add new skills
        new_skills = cv_updates.get("skills", [])
        if new_skills:
            if "skills" not in updated_cv:
                updated_cv["skills"] = []
            # Add skills that aren't already present
            existing_skills_lower = [s.lower() for s in updated_cv.get("skills", [])]
            for skill in new_skills:
                if skill.lower() not in existing_skills_lower:
                    updated_cv["skills"].append(skill)

        # Add new projects
        new_projects = cv_updates.get("projects", [])
        if new_projects:
            if "projects" not in updated_cv:
                updated_cv["projects"] = []
            updated_cv["projects"].extend(new_projects)

        # Add additional context to existing sections
        additional_contexts = cv_updates.get("additional_context", [])
        for context in additional_contexts:
            section = context.get("section")
            index = context.get("index", 0)
            additional_info = context.get("additional_info", "")

            if section in updated_cv and isinstance(updated_cv[section], list):
                if 0 <= index < len(updated_cv[section]):
                    # Add to existing entry
                    if isinstance(updated_cv[section][index], dict):
                        if "additional_notes" not in updated_cv[section][index]:
                            updated_cv[section][index]["additional_notes"] = []
                        updated_cv[section][index]["additional_notes"].append(additional_info)

        # Step 7: Recalculate score with updated CV
        # Calculate new compatibility score
        new_score_result = calculate_overall_compatibility(
            parsed_cv=updated_cv,
            parsed_jd=request.parsed_jd
        )

        new_overall_score = new_score_result.get('overall_score', request.original_score)

        # Step 8: Calculate improvements
        score_improvement = new_overall_score - request.original_score

        # Calculate category improvements (simplified - you could do detailed per-category)
        category_improvements = {}

        # Map uncovered experiences to categories
        for exp in uncovered_experiences_list:
            category = exp.get("category", "other")
            impact_level = exp.get("impact_level", "WEAK")

            # Estimate category improvement based on impact level
            impact_points = 0
            if impact_level == "STRONG":
                impact_points = 5
            elif impact_level == "MODERATE":
                impact_points = 3
            elif impact_level == "WEAK":
                impact_points = 1

            if category not in category_improvements:
                category_improvements[category] = 0
            category_improvements[category] += impact_points

        # Step 9: Format uncovered experiences for response
        uncovered_text_list = []
        for exp in uncovered_experiences_list:
            if exp.get("impact_level") in ["STRONG", "MODERATE"]:
                uncovered_text_list.append(exp.get("description", ""))

        elapsed_time = time.time() - start_time

        # Step 10: Store the successful answer experience in Qdrant for RAG
        if score_improvement > 0:
            qdrant = get_qdrant_manager()
            for exp in uncovered_experiences_list:
                if exp.get("impact_level") in ["STRONG", "MODERATE"]:
                    experience_text = f"Candidate {exp.get('description')}. Impact: +{score_improvement}%. Relevance: {exp.get('relevance_to_job')}"
                    qdrant.store_experience(
                        experience_text=experience_text,
                        metadata={
                            "gap_type": exp.get("category", "other"),
                            "skill": exp.get("category", "other"),
                            "impact": f"+{score_improvement}%",
                            "priority": "MEDIUM",
                            "source": "user_submission"
                        }
                    )

        return SubmitAnswersResponse(
            success=True,
            updated_score=new_overall_score,
            score_improvement=score_improvement,
            category_improvements=category_improvements,
            uncovered_experiences=uncovered_text_list,
            updated_cv=updated_cv,
            time_seconds=round(elapsed_time, 3),
            model="gemini-2.0-flash-exp"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing answers: {str(e)}"
        )


def convert_sample_to_parsed_format(sample_format: dict) -> dict:
    """
    Convert sample_format (camelCase, HTML) to parsed_format (snake_case, plain text).
    Strips HTML tags and converts field names.
    """
    import re

    def strip_html(text: str) -> str:
        """Remove HTML tags from text"""
        if not isinstance(text, str):
            return text
        return re.sub(r'<[^>]+>', '', text).strip()

    def camel_to_snake(name: str) -> str:
        """Convert camelCase to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    content = sample_format.get("content", {})

    # Extract and convert personal info
    personal_info_source = content.get("personalInfo", {})
    personal_info = {
        "name": f"{personal_info_source.get('firstName', '')} {personal_info_source.get('lastName', '')}".strip(),
        "email": personal_info_source.get("email"),
        "phone": personal_info_source.get("phone"),
        "location": personal_info_source.get("location"),
        "linkedin": personal_info_source.get("socialLinks", {}).get("linkedin"),
        "github": personal_info_source.get("socialLinks", {}).get("github"),
        "portfolio": personal_info_source.get("socialLinks", {}).get("portfolio")
    }

    # Extract work experience
    work_experience = []
    for job in content.get("employmentHistory", []):
        work_experience.append({
            "role": job.get("jobTitle"),
            "company": job.get("company"),
            "location": job.get("location"),
            "start_date": job.get("startDate"),
            "end_date": job.get("endDate") if job.get("endDate") else None,
            "achievements": [strip_html(job.get("description", ""))]
        })

    # Extract projects
    projects = []
    for proj in content.get("projects", []):
        projects.append({
            "name": proj.get("title"),
            "description": strip_html(proj.get("description", "")),
            "technologies": proj.get("technologies", []),
            "achievements": proj.get("achievements", [])
        })

    # Extract education
    education = []
    for edu in content.get("education", []):
        education.append({
            "degree": edu.get("degree"),
            "institution": edu.get("institution"),
            "location": edu.get("location"),
            "graduation_date": edu.get("graduationDate"),
            "gpa": edu.get("gpa"),
            "honors": edu.get("honors")
        })

    # Extract skills
    technical_skills = [skill.get("skill") for skill in content.get("skills", []) if skill.get("category") in ["Programming Languages", "Frameworks", "Tools", "Technologies", None]]

    # Extract certifications
    certifications = []
    for cert in content.get("certifications", []):
        certifications.append({
            "name": cert.get("title"),
            "issuer": cert.get("issuer"),
            "date": cert.get("date"),
            "credential_id": cert.get("credential")
        })

    return {
        "personal_info": personal_info,
        "professional_summary": strip_html(content.get("professionalSummary", "")),
        "work_experience": work_experience,
        "education": education,
        "technical_skills": technical_skills or content.get("technicalStack", []),
        "soft_skills": [],
        "projects": projects,
        "certifications": certifications,
        "languages": content.get("languages", [])
    }


@app.post("/api/rewrite-resume", response_model=RewriteResumeResponse)
async def rewrite_resume(request: RewriteResumeRequest):
    """
    Phase 5: Rewrite resume incorporating insights from answers.
    Generates sample.json format (camelCase, HTML) and converts to parsed CV format (snake_case).
    Uses TOON format in prompt to reduce tokens and faster model for performance.
    """
    try:
        start_time = time.time()

        # Match questions with answers
        questions_and_answers = []
        for question in request.questions:
            answer = next(
                (a for a in request.answers if a.question_id == question.id),
                None
            )
            if answer:
                questions_and_answers.append({
                    'question': question.question_text,
                    'answer': answer.answer_text
                })

        # Convert CV and JD to TOON format for the prompt
        cv_toon = to_toon(request.updated_cv)
        jd_toon = to_toon(request.parsed_jd)

        # Generate resume rewrite prompt with TOON format
        rewrite_prompt = get_resume_rewrite_prompt(
            updated_cv_toon=cv_toon,
            answers=questions_and_answers,
            jd_toon=jd_toon,
            language=request.language
        )

        # Call Gemini AI to rewrite resume (with explicit prompt caching)
        model_name = "gemini-2.5-flash-lite"
        response = generate_with_cache(
            prompt=rewrite_prompt,
            model=model_name,
            temperature=0.3,  # Slightly creative for better writing
            cache_ttl=300  # 5 minutes cache
        )

        # Parse response
        cleaned_text = response.text.strip()
        if cleaned_text.startswith("```"):
            lines = cleaned_text.split("\n")
            if len(lines) > 1:
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned_text = "\n".join(lines).strip()

        result = json.loads(cleaned_text)

        # Convert sample_format to parsed_format (strip HTML, camelCase -> snake_case)
        parsed_format = convert_sample_to_parsed_format(result.get("sample_format", {}))

        elapsed_time = time.time() - start_time

        return RewriteResumeResponse(
            success=True,
            sample_format=result.get("sample_format", {}),
            parsed_format=parsed_format,
            enhancements_made=result.get("enhancements_made", []),
            time_seconds=round(elapsed_time, 3),
            model=model_name
        )

    except Exception as e:
        print(f"Error rewriting resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error rewriting resume: {str(e)}"
        )


@app.post("/api/generate-cover-letter", response_model=CoverLetterResponse)
async def generate_cover_letter_endpoint(request: CoverLetterRequest):
    """
    Generate a personalized cover letter based on rewritten resume and job description.

    This endpoint should be called after resume rewrite is complete.
    """
    try:
        start_time = time.time()

        # Validate inputs
        if not request.parsed_resume or not request.parsed_jd:
            raise HTTPException(
                status_code=400,
                detail="Both parsed_resume and parsed_jd are required"
            )

        # Generate cover letter
        cover_letter_text = generate_cover_letter(
            parsed_resume=request.parsed_resume,
            parsed_jd=request.parsed_jd,
            score_data=request.score_data
        )

        # Count words
        word_count = len(cover_letter_text.split())

        elapsed_time = time.time() - start_time

        return CoverLetterResponse(
            success=True,
            cover_letter=cover_letter_text,
            word_count=word_count,
            time_seconds=round(elapsed_time, 3),
            model="gemini-2.5-flash-lite"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating cover letter: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating cover letter: {str(e)}"
        )


@app.post("/benchmark/gemini")
async def benchmark_gemini(job: JobDescription):
    """Benchmark Gemini 2.0 Flash Lite model with TOON format"""
    try:
        prompt = create_prompt(job.job_description)

        start = time.time()
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config={
                "temperature": 0.2
                # Removed response_mime_type to allow TOON format
            }
        )
        elapsed = time.time() - start

        # Parse TOON/JSON response
        parsed_data, success, format_used = parse_toon_response(response.text)

        # Convert to JSON for API response (backward compatibility)
        if success:
            json_output = json.dumps(parsed_data, indent=2)
        else:
            json_output = response.text

        return BenchmarkResult(
            model="gemini-2.0-flash-lite",
            time_seconds=round(elapsed, 3),
            valid_json=success,
            output_preview=json_output[:300] + "..." if len(json_output) > 300 else json_output
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/benchmark/gpt35")
async def benchmark_gpt35(job: JobDescription):
    """Benchmark GPT-3.5-Turbo model with TOON format"""
    try:
        prompt = create_prompt(job.job_description)

        start = time.time()
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            # Removed response_format to allow TOON format
            temperature=0.2
        )
        elapsed = time.time() - start

        content = response.choices[0].message.content

        # Parse TOON/JSON response
        parsed_data, success, format_used = parse_toon_response(content)

        # Convert to JSON for API response (backward compatibility)
        if success:
            json_output = json.dumps(parsed_data, indent=2)
        else:
            json_output = content

        return BenchmarkResult(
            model="gpt-3.5-turbo",
            time_seconds=round(elapsed, 3),
            valid_json=success,
            output_preview=json_output[:300] + "..." if len(json_output) > 300 else json_output
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/benchmark/gemini-flash")
async def benchmark_gemini_flash(job: JobDescription):
    """Benchmark Gemini 2.0 Flash (Full) model with TOON format"""
    try:
        prompt = create_prompt(job.job_description)

        start = time.time()
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config={
                "temperature": 0.2
                # Removed response_mime_type to allow TOON format
            }
        )
        elapsed = time.time() - start

        # Parse TOON/JSON response
        parsed_data, success, format_used = parse_toon_response(response.text)

        # Convert to JSON for API response (backward compatibility)
        if success:
            json_output = json.dumps(parsed_data, indent=2)
        else:
            json_output = response.text

        return BenchmarkResult(
            model="gemini-2.0-flash-exp",
            time_seconds=round(elapsed, 3),
            valid_json=success,
            output_preview=json_output[:300] + "..." if len(json_output) > 300 else json_output
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/benchmark/gpt4o-mini")
async def benchmark_gpt4o_mini(job: JobDescription):
    """Benchmark GPT-4o-Mini model with TOON format"""
    try:
        prompt = create_prompt(job.job_description)

        start = time.time()
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            # Removed response_format to allow TOON format
            temperature=0.2
        )
        elapsed = time.time() - start

        content = response.choices[0].message.content

        # Parse TOON/JSON response
        parsed_data, success, format_used = parse_toon_response(content)

        # Convert to JSON for API response (backward compatibility)
        if success:
            json_output = json.dumps(parsed_data, indent=2)
        else:
            json_output = content

        return BenchmarkResult(
            model="gpt-4o-mini",
            time_seconds=round(elapsed, 3),
            valid_json=success,
            output_preview=json_output[:300] + "..." if len(json_output) > 300 else json_output
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/benchmark/compare")
async def benchmark_compare(job: JobDescription):
    """Compare all 4 models: Gemini 2.0 Flash Lite, Gemini 2.0 Flash, GPT-3.5-Turbo, GPT-4o-Mini"""
    results = []

    # Benchmark Gemini Flash Lite
    try:
        gemini_result = await benchmark_gemini(job)
        results.append(gemini_result)
    except Exception as e:
        results.append(BenchmarkResult(
            model="gemini-2.0-flash-lite",
            time_seconds=0,
            valid_json=False,
            output_preview="",
            error=str(e)
        ))

    # Benchmark Gemini Flash (Full)
    try:
        gemini_flash_result = await benchmark_gemini_flash(job)
        results.append(gemini_flash_result)
    except Exception as e:
        results.append(BenchmarkResult(
            model="gemini-2.0-flash-exp",
            time_seconds=0,
            valid_json=False,
            output_preview="",
            error=str(e)
        ))

    # Benchmark GPT-3.5-Turbo
    try:
        gpt35_result = await benchmark_gpt35(job)
        results.append(gpt35_result)
    except Exception as e:
        results.append(BenchmarkResult(
            model="gpt-3.5-turbo",
            time_seconds=0,
            valid_json=False,
            output_preview="",
            error=str(e)
        ))

    # Benchmark GPT-4o-Mini
    try:
        gpt4mini_result = await benchmark_gpt4o_mini(job)
        results.append(gpt4mini_result)
    except Exception as e:
        results.append(BenchmarkResult(
            model="gpt-4o-mini",
            time_seconds=0,
            valid_json=False,
            output_preview="",
            error=str(e)
        ))

    # Determine fastest
    valid_results = [r for r in results if r.error is None and r.time_seconds > 0]
    if not valid_results:
        raise HTTPException(status_code=500, detail="All benchmarks failed")

    fastest = min(valid_results, key=lambda x: x.time_seconds)
    slowest = max(valid_results, key=lambda x: x.time_seconds)
    speedup = round(slowest.time_seconds / fastest.time_seconds, 2)

    return CompareResponse(
        results=results,
        fastest_model=fastest.model,
        speedup=speedup
    )

@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY")),
        "openai_api_configured": bool(os.getenv("OPENAI_API_KEY")),
        "redis_connected": cache.redis_client is not None
    }

@app.get("/cache/stats")
async def get_cache_stats():
    """
    Get cache performance statistics.
    Shows hit rates, total requests, and cache effectiveness.
    Includes both application-level caching and Gemini prompt caching stats.
    """
    # Get application-level cache stats (Redis + in-memory)
    app_cache_stats = cache.get_stats()

    # Get Gemini prompt cache stats (explicit caching)
    prompt_cache_stats = get_prompt_cache_stats()

    # Combine both
    return {
        **app_cache_stats,
        "prompt_caching": prompt_cache_stats
    }

@app.post("/api/cache/clear-domains")
async def clear_domains_cache():
    """
    Clear all domain finder cache entries.
    Useful for invalidating stale cache after prompt updates.
    """
    cleared_count = 0

    # Clear from L1 (in-memory) cache
    if hasattr(cache, '_l1_cache'):
        domain_keys = [k for k in list(cache._l1_cache.keys()) if k.startswith('domains:')]
        for key in domain_keys:
            del cache._l1_cache[key]
            cleared_count += 1

    # Clear from L2 (Redis) cache
    if cache.redis_client:
        try:
            for key in cache.redis_client.scan_iter("domains:*"):
                cache.redis_client.delete(key)
                cleared_count += 1
        except Exception as e:
            return {
                "success": False,
                "error": f"Redis error: {str(e)}",
                "l1_cleared": cleared_count
            }

    return {
        "success": True,
        "message": f"Cleared {cleared_count} domain finder cache entries",
        "entries_cleared": cleared_count,
        "cache_type": "domains"
    }


# ========================================
# Adaptive Question Flow Endpoints
# ========================================

class StartAdaptiveQuestionRequest(BaseModel):
    question_id: str
    question_text: str
    question_data: dict
    gap_info: dict
    user_id: str
    parsed_cv: dict
    parsed_jd: dict
    experience_check_response: str  # "yes", "no", or "willing_to_learn"
    language: str = "english"

class DeepDivePromptItem(BaseModel):
    id: str
    type: str  # "text", "textarea", "select", "multiselect", "number"
    question: str
    placeholder: Optional[str] = None
    options: Optional[list[str]] = None
    required: bool = True
    help_text: Optional[str] = None

class LearningResourceItem(BaseModel):
    id: str
    title: str
    description: str
    type: str  # "course", "project", "certification"
    provider: str
    url: str
    duration_days: int
    difficulty: str  # "beginner", "intermediate", "advanced"
    cost: str  # "free", "paid", "freemium"
    skills_covered: list[str]
    rating: Optional[float] = None
    score: Optional[int] = None  # Relevance score (0-100)

class AdaptiveQuestionResponse(BaseModel):
    question_id: str
    current_step: str
    deep_dive_prompts: list[DeepDivePromptItem] = []
    suggested_resources: list[LearningResourceItem] = []
    resume_addition: Optional[str] = None
    error: Optional[str] = None


@app.post("/api/adaptive-questions/start", response_model=AdaptiveQuestionResponse)
async def start_adaptive_question(request: StartAdaptiveQuestionRequest):
    """
    Start adaptive question flow.

    Based on experience_check_response:
    - "yes" → Returns deep_dive_prompts for detailed questioning
    - "no" or "willing_to_learn" → Returns suggested_resources
    """
    try:
        from core.adaptive_question_graph import AdaptiveQuestionWorkflow, create_initial_state

        # Create initial state
        initial_state = create_initial_state(
            question_id=request.question_id,
            question_text=request.question_text,
            question_data=request.question_data,
            gap_info=request.gap_info,
            user_id=request.user_id,
            parsed_cv=request.parsed_cv,
            parsed_jd=request.parsed_jd,
            experience_check_response=request.experience_check_response,
            language=request.language
        )

        # Run workflow
        workflow = AdaptiveQuestionWorkflow()
        final_state = workflow.run_sync(initial_state)

        # Build response based on path taken
        response_data = {
            "question_id": request.question_id,
            "current_step": final_state.get("current_step", "unknown"),
            "error": final_state.get("error")
        }

        # If deep dive path
        if final_state.get("structured_inputs", {}).get("prompts"):
            # Ensure prompts have required fields with defaults
            validated_prompts = []
            for i, prompt in enumerate(final_state["structured_inputs"]["prompts"]):
                try:
                    # Ensure required fields exist
                    validated_prompt = {
                        "id": prompt.get("id", f"prompt_{i}"),
                        "type": prompt.get("type", "text"),
                        "question": prompt.get("question", ""),
                        "placeholder": prompt.get("placeholder"),
                        "options": prompt.get("options"),
                        "required": prompt.get("required", True),
                        "help_text": prompt.get("help_text")
                    }
                    validated_prompts.append(DeepDivePromptItem(**validated_prompt))
                except Exception as e:
                    print(f"Warning: Skipping invalid prompt {i}: {str(e)}")
                    continue
            response_data["deep_dive_prompts"] = validated_prompts

        # If learning resources path
        if final_state.get("suggested_resources"):
            # Ensure resources have required fields with defaults
            validated_resources = []
            for i, resource in enumerate(final_state["suggested_resources"]):
                try:
                    # Ensure required fields exist
                    validated_resource = {
                        "id": resource.get("id", f"resource_{i}"),
                        "title": resource.get("title", ""),
                        "description": resource.get("description", ""),
                        "type": resource.get("type", "course"),
                        "provider": resource.get("provider", "Unknown"),
                        "url": resource.get("url", ""),
                        "duration_days": resource.get("duration_days", 0),
                        "difficulty": resource.get("difficulty", "beginner"),
                        "cost": resource.get("cost", "free"),
                        "skills_covered": resource.get("skills_covered", []),
                        "rating": resource.get("rating"),
                        "score": resource.get("score")
                    }
                    validated_resources.append(LearningResourceItem(**validated_resource))
                except Exception as e:
                    print(f"Warning: Skipping invalid resource {i}: {str(e)}")
                    continue
            response_data["suggested_resources"] = validated_resources
            response_data["resume_addition"] = final_state.get("resume_addition")

        return AdaptiveQuestionResponse(**response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")


class SubmitStructuredInputsRequest(BaseModel):
    question_id: str
    structured_data: dict  # User's responses to deep dive prompts


class SubmitStructuredInputsResponse(BaseModel):
    question_id: str
    generated_answer: str
    quality_score: int = None
    quality_issues: list[str] = None
    quality_strengths: list[str] = None
    improvement_suggestions: list[dict] = None
    final_answer: str = None  # Set if quality is acceptable
    current_step: str
    error: str = None


@app.post("/api/adaptive-questions/submit-inputs", response_model=SubmitStructuredInputsResponse)
async def submit_structured_inputs(request: SubmitStructuredInputsRequest):
    """
    Submit structured inputs (deep dive answers) and get generated professional answer.

    Returns quality evaluation and either:
    - final_answer (if quality >= 7/10)
    - improvement_suggestions (if quality < 7/10)
    """
    try:
        from core.adaptive_question_graph import AdaptiveQuestionWorkflow, add_structured_inputs_to_state
        from core.answer_flow_state import AdaptiveAnswerState

        # TODO: Retrieve workflow state from session/database by question_id
        # For now, we'll create a simplified flow
        # In production, you'd store state in Redis or database

        # Create workflow and process from generate_answer node
        workflow = AdaptiveQuestionWorkflow()

        # Simplified state for continuation (in production, load from storage)
        state: AdaptiveAnswerState = {
            "question_id": request.question_id,
            "structured_inputs": request.structured_data,
            "current_step": "generate_answer",
            "gap_info": {},  # Would be loaded from storage
            "question_text": "",  # Would be loaded from storage
        }

        # Run from generate_answer node
        from core.answer_flow_nodes import generate_answer_from_inputs_node, evaluate_quality_node

        # Generate answer
        state = generate_answer_from_inputs_node(state)

        # Evaluate quality
        state = evaluate_quality_node(state)

        return SubmitStructuredInputsResponse(
            question_id=request.question_id,
            generated_answer=state.get("generated_answer", ""),
            quality_score=state.get("quality_score"),
            quality_issues=state.get("quality_issues", []),
            quality_strengths=state.get("quality_strengths", []),
            improvement_suggestions=state.get("improvement_suggestions", []),
            final_answer=state.get("final_answer"),
            current_step=state.get("current_step", "unknown"),
            error=state.get("error")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer generation error: {str(e)}")


class SubmitRefinementDataRequest(BaseModel):
    question_id: str
    question_text: str
    question_data: dict
    gap_info: dict
    additional_data: dict  # Additional data from user
    generated_answer: str
    quality_issues: list[str] = []


class SubmitRefinementDataResponse(BaseModel):
    question_id: str
    refined_answer: str
    quality_score: Optional[int] = None
    final_answer: Optional[str] = None
    current_step: str
    iteration: int
    error: Optional[str] = None


@app.post("/api/adaptive-questions/refine-answer", response_model=SubmitRefinementDataResponse)
async def refine_answer(request: SubmitRefinementDataRequest):
    """
    Submit refinement data to improve answer quality.

    Max 2 refinement iterations. After that, accepts current answer.
    """
    try:
        from core.answer_flow_nodes import refine_answer_node
        from core.answer_flow_state import AdaptiveAnswerState

        # TODO: Load state from storage
        state: AdaptiveAnswerState = {
            "question_id": request.question_id,
            "question_text": request.question_text,
            "question_data": request.question_data,
            "gap_info": request.gap_info,
            "user_id": "",  # Not used in refinement
            "parsed_cv": {},  # Not used in refinement
            "parsed_jd": {},  # Not used in refinement
            "language": "english",  # Default
            "refinement_data": request.additional_data,
            "current_step": "refinement",
            "refinement_iteration": 0,  # Would be loaded from storage
            "generated_answer": request.generated_answer,
            "quality_issues": request.quality_issues,
            "started_at": datetime.now(),  # Required field
            "answer_accepted": False,  # Required field
        }

        # Refine answer (AI rewrite only - no re-evaluation)
        state = refine_answer_node(state)

        # Skip re-evaluation - return rewritten answer directly
        return SubmitRefinementDataResponse(
            question_id=request.question_id,
            refined_answer=state.get("refined_answer", ""),
            quality_score=None,  # No re-evaluation
            final_answer=None,
            current_step="answer_generation",  # Return to answer input step
            iteration=1,
            error=state.get("error")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refinement error: {str(e)}")


class GetLearningResourcesRequest(BaseModel):
    gap: dict  # Gap information
    user_level: str = "intermediate"  # "beginner", "intermediate", "advanced"
    max_days: int = 10
    cost_preference: str = "any"  # "free", "paid", "any"
    limit: int = 5
    search_mode: str = "hybrid"  # "local_only", "web_only", "hybrid"


class LearningPathStep(BaseModel):
    resource_id: str
    resource_title: str
    type: str
    start_day: int
    end_day: int
    duration_days: int


class LearningPath(BaseModel):
    timeline: list[LearningPathStep]
    total_days: int
    estimated_completion: str
    resources_in_path: int


class GetLearningResourcesResponse(BaseModel):
    resources: list[LearningResourceItem]
    timeline: list  # Flattened from learning_path.timeline
    total_resources: int
    total_duration_days: int
    estimated_completion: str
    error: str = None


@app.post("/api/adaptive-questions/get-learning-resources", response_model=GetLearningResourcesResponse)
async def get_learning_resources(request: GetLearningResourcesRequest):
    """
    Get learning resources for a specific gap using semantic search.

    Returns:
    - Ranked resources (courses, projects, certifications)
    - Learning path timeline
    - Estimated completion date
    """
    try:
        from core.resource_matcher import get_resource_matcher

        matcher = get_resource_matcher()

        # Use hybrid search if search_mode is hybrid or web_only
        if request.search_mode in ["hybrid", "web_only"]:
            result = matcher.find_resources_with_web_search(
                gap=request.gap,
                user_level=request.user_level,
                max_days=request.max_days,
                cost_preference=request.cost_preference,
                limit=request.limit,
                search_mode=request.search_mode
            )
        else:
            result = matcher.find_resources(
                gap=request.gap,
                user_level=request.user_level,
                max_days=request.max_days,
                cost_preference=request.cost_preference,
                limit=request.limit
            )

        if result.get("error"):
            return GetLearningResourcesResponse(
                resources=[],
                timeline=[],
                total_resources=0,
                total_duration_days=0,
                estimated_completion="",
                error=result["error"]
            )

        return GetLearningResourcesResponse(
            resources=[LearningResourceItem(**r) for r in result["resources"]],
            timeline=result["learning_path"]["timeline"],
            total_resources=result["total_resources"],
            total_duration_days=result["total_duration_days"],
            estimated_completion=result["estimated_completion"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resource matching error: {str(e)}")


class SaveLearningPlanRequest(BaseModel):
    user_id: str
    gap_info: dict
    selected_resource_ids: list[str]
    notes: str = None


class SaveLearningPlanResponse(BaseModel):
    plan_id: str
    status: str  # "success" or "error"
    error: str = None


@app.post("/api/adaptive-questions/save-learning-plan", response_model=SaveLearningPlanResponse)
async def save_learning_plan(request: SaveLearningPlanRequest):
    """
    Save a learning plan for the user.

    Stores selected resources and gap information for later tracking.
    """
    try:
        from core.resource_matcher import get_resource_matcher

        matcher = get_resource_matcher()
        plan_id = matcher.save_learning_plan(
            user_id=request.user_id,
            gap=request.gap_info,
            resource_ids=request.selected_resource_ids,
            notes=request.notes
        )

        return SaveLearningPlanResponse(
            plan_id=plan_id,
            status="success"
        )

    except Exception as e:
        return SaveLearningPlanResponse(
            plan_id="",
            status="error",
            error=f"Failed to save learning plan: {str(e)}"
        )


class GetLearningPlansRequest(BaseModel):
    user_id: str
    status: str = None  # Optional: "suggested", "in_progress", "completed", "abandoned"


class LearningPlanItem(BaseModel):
    id: str
    gap_title: str
    gap_description: str
    resource_ids: list[str]
    resources: list[dict] = []  # Full resource objects
    status: str
    created_at: str
    notes: str = None


class GetLearningPlansResponse(BaseModel):
    plans: list[LearningPlanItem]
    total: int


@app.post("/api/adaptive-questions/get-learning-plans", response_model=GetLearningPlansResponse)
async def get_learning_plans(request: GetLearningPlansRequest):
    """
    Get all learning plans for a user.

    Optionally filter by status.
    """
    try:
        from core.resource_matcher import get_resource_matcher

        matcher = get_resource_matcher()
        plans = matcher.get_user_learning_plans(
            user_id=request.user_id,
            status=request.status
        )

        return GetLearningPlansResponse(
            plans=[
                LearningPlanItem(
                    id=str(p["id"]),
                    gap_title=p["gap_title"],
                    gap_description=p["gap_description"],
                    resource_ids=p["resource_ids"],
                    resources=p.get("resources", []),
                    status=p["status"],
                    created_at=(
                        p["created_at"].isoformat() if hasattr(p.get("created_at"), "isoformat")
                        else str(p.get("created_at", ""))
                    ),
                    notes=p.get("notes")
                )
                for p in plans
            ],
            total=len(plans)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving learning plans: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Log cache status on startup"""
    redis_status = "✅ connected" if cache.redis_client else "❌ not connected (using in-memory only)"
    print(f"\n{'='*60}")
    print(f"Cache Status: Redis {redis_status}")
    if cache.redis_client:
        print(f"Redis URL: {os.getenv('REDIS_URL')}")
        print(f"Cache sharing: ENABLED (all users share same cache)")
        print(f"Cache persistence: ENABLED (survives restarts)")
    else:
        print(f"⚠️  WARNING: Redis not connected!")
        print(f"   Cache will NOT be shared across workers/restarts")
        print(f"   Set REDIS_URL in .env to enable shared caching")
    print(f"{'='*60}\n")
