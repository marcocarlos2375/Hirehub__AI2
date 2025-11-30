"""
Parsing endpoints for job descriptions and CVs.
"""

import time
import json
import hashlib
from fastapi import APIRouter, HTTPException

from core.logging_config import logger
from core.cache import get_cache
from core.llm_fallback import generate_with_fallback
from core.settings import settings
from app.config import get_json_prompt, get_cv_prompt
from app.models.parsing import (
    ParseRequest,
    ParseResponse,
    CVParseRequest,
    CVParseResponse,
)
from app.utils.markdown import strip_markdown_code_blocks
from app.utils.validation import (
    validate_language,
    validate_text_input,
    SUPPORTED_LANGUAGES,
)

router = APIRouter(prefix="/api", tags=["Parsing"])

cache = get_cache()


@router.post("/parse", response_model=ParseResponse)
async def parse_job(request: ParseRequest):
    """
    Parse a job description using Gemini with JSON format.
    Supports multiple languages: english, french, german, spanish
    """
    try:
        # Validate input
        job_description = validate_text_input(
            request.job_description,
            field_name="Job description",
            min_length=50,
            max_length=6200
        )

        language = validate_language(request.language)

        # Check cache
        jd_hash = hashlib.md5(job_description.encode()).hexdigest()
        cache_key = f"parse:jd:{jd_hash}:{language}"

        try:
            cached_result = cache.get(cache_key)
            if cached_result:
                result_dict = json.loads(cached_result) if isinstance(cached_result, str) else cached_result
                logger.info("JD parsing cache hit")
                return ParseResponse(**result_dict)
        except Exception as cache_error:
            logger.warning(f"JD cache retrieval failed: {cache_error}")

        # Generate prompt and call LLM
        prompt = get_json_prompt(job_description, language)

        start_time = time.time()
        model_name = settings.parsing_model

        response_text, provider = generate_with_fallback(
            prompt=prompt,
            model_gemini=model_name,
            temperature=settings.parsing_temperature
        )

        elapsed_time = time.time() - start_time
        logger.info(f"JD parsing completed using {provider} in {elapsed_time:.2f}s")

        # Parse JSON response
        try:
            cleaned_text = strip_markdown_code_blocks(response_text)
            parsed_data = json.loads(cleaned_text)

            if parsed_data and len(parsed_data) >= 5:
                result = ParseResponse(
                    success=True,
                    data=parsed_data,
                    time_seconds=round(elapsed_time, 3),
                    model=model_name,
                    language=language
                )

                # Cache successful result
                try:
                    cache.set(cache_key, json.dumps(result.model_dump()), ttl=settings.result_cache_ttl)
                    logger.debug("JD parsing result cached")
                except Exception as cache_error:
                    logger.warning(f"JD cache storage failed: {cache_error}")

                return result
            else:
                logger.warning(f"Incomplete JD parsing result: {len(parsed_data) if parsed_data else 0} fields")
                return ParseResponse(
                    success=False,
                    data={"raw_response": response_text[:500]},
                    error="Failed to parse JSON completely",
                    time_seconds=round(elapsed_time, 3),
                    model=model_name,
                    language=language
                )

        except json.JSONDecodeError as parse_error:
            logger.error(f"JD JSON parse error: {parse_error}")
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
        logger.error(f"JD parsing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/parse-cv", response_model=CVParseResponse)
async def parse_cv(request: CVParseRequest):
    """
    Parse a resume/CV using Gemini with JSON format.
    Supports multiple languages: english, french, german, spanish
    """
    try:
        # Validate input
        resume_text = validate_text_input(
            request.resume_text,
            field_name="Resume text",
            min_length=50,
            max_length=6200
        )

        language = validate_language(request.language)

        # Check cache
        cv_hash = hashlib.md5(resume_text.encode()).hexdigest()
        cache_key = f"parse:cv:{cv_hash}:{language}"

        try:
            cached_result = cache.get(cache_key)
            if cached_result:
                result_dict = json.loads(cached_result) if isinstance(cached_result, str) else cached_result
                logger.info("CV parsing cache hit")
                return CVParseResponse(**result_dict)
        except Exception as cache_error:
            logger.warning(f"CV cache retrieval failed: {cache_error}")

        # Generate prompt and call LLM
        prompt = get_cv_prompt(resume_text, language)

        start_time = time.time()
        model_name = settings.parsing_model

        response_text, provider = generate_with_fallback(
            prompt=prompt,
            model_gemini=model_name,
            temperature=settings.parsing_temperature
        )

        elapsed_time = time.time() - start_time
        logger.info(f"CV parsing completed using {provider} in {elapsed_time:.2f}s")

        # Parse JSON response
        try:
            cleaned_text = strip_markdown_code_blocks(response_text)
            parsed_data = json.loads(cleaned_text)

            if parsed_data and len(parsed_data) >= 5:
                result = CVParseResponse(
                    success=True,
                    data=parsed_data,
                    time_seconds=round(elapsed_time, 3),
                    model=model_name,
                    language=language
                )

                # Cache successful result
                try:
                    cache.set(cache_key, json.dumps(result.model_dump()), ttl=settings.result_cache_ttl)
                    logger.debug("CV parsing result cached")
                except Exception as cache_error:
                    logger.warning(f"CV cache storage failed: {cache_error}")

                return result
            else:
                logger.warning(f"Incomplete CV parsing result: {len(parsed_data) if parsed_data else 0} fields")
                return CVParseResponse(
                    success=False,
                    data={"raw_response": response_text[:500]},
                    error="Failed to parse JSON completely",
                    time_seconds=round(elapsed_time, 3),
                    model=model_name,
                    language=language
                )

        except json.JSONDecodeError as parse_error:
            logger.error(f"CV JSON parse error: {parse_error}")
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
        logger.error(f"CV parsing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
