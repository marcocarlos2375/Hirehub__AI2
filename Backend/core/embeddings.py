"""
Optimized embedding utilities for semantic similarity calculations.
Uses Google's text-embedding-004 model with multiple optimizations:
- Two-tier caching (in-memory + Redis)
- Hybrid keyword + semantic matching
- Batch embedding generation
- Individual skill embeddings with matrix matching
- Recency-weighted experience scoring
"""

import os
import numpy as np
from google import genai
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Tuple, Optional
from core.cache import get_cache
from core.embeddings_fallback import get_embedding_with_fallback

load_dotenv()

# Initialize Gemini client
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize cache (will try Redis if available, else in-memory only)
cache = get_cache(redis_url=os.getenv("REDIS_URL"))  # Set REDIS_URL in .env if available


def get_embedding(text: str, use_cache: bool = True) -> list[float]:
    """
    Generate embedding vector for given text using Google text-embedding-004.
    Uses two-tier caching for performance (90%+ speedup on cache hits).

    Args:
        text: Text to embed
        use_cache: Whether to use cache (default: True)

    Returns:
        List of floats representing the embedding vector (768 dimensions)
    """
    if not text or len(text.strip()) == 0:
        # Return zero vector for empty text
        return [0.0] * 768

    # NON-BLOCKING: Check cache first (two-tier: L1 + L2)
    # Cache failures don't crash embedding generation - we fall back to fresh generation
    if use_cache:
        try:
            cached_embedding = cache.get(text)
            if cached_embedding is not None:
                return cached_embedding
        except Exception as cache_error:
            # Log warning but continue to fresh generation
            print(f"⚠️  Embedding cache retrieval failed: {cache_error}. Generating fresh embedding.")
            # Continue to fresh generation below

    # Generate new embedding with Gemini → OpenAI fallback
    try:
        embedding, provider = get_embedding_with_fallback(text)

        # Note: provider is "gemini", "openai", or "zero_fallback"
        # Only log if not using primary provider
        if provider != "gemini":
            print(f"✅ Embedding generated using {provider}")

        # NON-BLOCKING: Store in cache (two-tier: L1 + L2)
        # Cache storage failures don't crash - embedding is still returned
        if use_cache:
            try:
                cache.set(text, embedding)
            except Exception as cache_error:
                # Log warning but don't crash - embedding is still returned
                print(f"⚠️  Embedding cache storage failed: {cache_error}. Result not cached, but returned.")

        return embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return [0.0] * 768


def get_embeddings_batch(texts: List[str], use_cache: bool = True) -> List[list[float]]:
    """
    Generate multiple embeddings in parallel (3-4x faster than sequential).
    Uses ThreadPoolExecutor for concurrent API calls.

    Args:
        texts: List of texts to embed
        use_cache: Whether to use cache

    Returns:
        List of embedding vectors
    """
    if not texts:
        return []

    # Process in parallel
    with ThreadPoolExecutor(max_workers=min(len(texts), 8)) as executor:
        embeddings = list(executor.map(
            lambda text: get_embedding(text, use_cache=use_cache),
            texts
        ))

    return embeddings


def calculate_cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity score between 0 and 1
    """
    # Convert to numpy arrays
    a = np.array(vec1)
    b = np.array(vec2)

    # Calculate cosine similarity
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    similarity = dot_product / (norm_a * norm_b)

    # Ensure result is between 0 and 1
    return max(0.0, min(1.0, float(similarity)))


def exact_keyword_match(cv_skills: List[str], jd_skills: List[str]) -> Tuple[float, List[str]]:
    """
    Calculate exact keyword match score (case-insensitive).

    Args:
        cv_skills: Skills from CV
        jd_skills: Skills from JD

    Returns:
        Tuple of (match_score, matched_skills)
    """
    if not cv_skills or not jd_skills:
        return 0.0, []

    # Normalize to lowercase for comparison
    cv_lower = {s.lower().strip() for s in cv_skills}
    jd_lower = {s.lower().strip() for s in jd_skills}

    # Find exact matches
    exact_matches = cv_lower & jd_lower

    # Calculate score
    score = len(exact_matches) / len(jd_lower) if jd_lower else 0.0

    return score, list(exact_matches)


def fuzzy_keyword_match(cv_skills: List[str], jd_skills: List[str]) -> Tuple[float, List[Tuple[str, str]]]:
    """
    Calculate fuzzy/partial keyword match (e.g., "Python 3.11" matches "Python").

    Args:
        cv_skills: Skills from CV
        jd_skills: Skills from JD

    Returns:
        Tuple of (match_score, partial_matches)
    """
    if not cv_skills or not jd_skills:
        return 0.0, []

    cv_lower = [s.lower().strip() for s in cv_skills]
    jd_lower = [s.lower().strip() for s in jd_skills]

    partial_matches = []

    for jd_skill in jd_lower:
        for cv_skill in cv_lower:
            # Check if either is substring of the other
            if jd_skill in cv_skill or cv_skill in jd_skill:
                # Avoid exact matches (already counted)
                if jd_skill != cv_skill:
                    partial_matches.append((cv_skill, jd_skill))
                    break  # Only count once per JD skill

    # Calculate score
    score = len(partial_matches) / len(jd_lower) if jd_lower else 0.0

    return score, partial_matches


def calculate_skill_match_matrix(cv_skills: List[str], jd_skills: List[str]) -> np.ndarray:
    """
    Calculate pairwise similarity matrix between CV and JD skills.
    Each CV skill is compared to each JD skill.

    Args:
        cv_skills: List of skills from CV
        jd_skills: List of skills from JD

    Returns:
        Matrix of shape (len(cv_skills), len(jd_skills)) with similarities
    """
    if not cv_skills or not jd_skills:
        return np.zeros((len(cv_skills) if cv_skills else 1, len(jd_skills) if jd_skills else 1))

    # Generate embeddings in batch (parallel)
    cv_embeddings = get_embeddings_batch(cv_skills)
    jd_embeddings = get_embeddings_batch(jd_skills)

    # Calculate similarity matrix
    matrix = np.zeros((len(cv_skills), len(jd_skills)))

    for i, cv_emb in enumerate(cv_embeddings):
        for j, jd_emb in enumerate(jd_embeddings):
            matrix[i, j] = calculate_cosine_similarity(cv_emb, jd_emb)

    return matrix


def calculate_skills_similarity(cv_skills: List[str], jd_skills: List[dict]) -> dict:
    """
    OPTIMIZED: Hybrid keyword + semantic matching with individual skill embeddings.
    Combines exact matching, fuzzy matching, and semantic similarity.

    Args:
        cv_skills: List of skills from CV
        jd_skills: List of skill objects from JD with 'skill' and 'priority' fields

    Returns:
        Dictionary with similarity scores and matched skills
    """
    if not cv_skills or not jd_skills:
        return {
            "overall_similarity": 0.0,
            "critical_skills_match": 0.0,
            "important_skills_match": 0.0,
            "exact_match_score": 0.0,
            "fuzzy_match_score": 0.0,
            "semantic_match_score": 0.0,
            "matched_skills": [],
            "missing_critical": [],
            "missing_important": []
        }

    # Extract JD skill names and group by priority
    jd_skill_names = [s["skill"] for s in jd_skills]
    critical_skills = [s["skill"] for s in jd_skills if s.get("priority") == "critical"]
    important_skills = [s["skill"] for s in jd_skills if s.get("priority") == "important"]

    # ===== OPTIMIZATION 1: Exact Keyword Matching =====
    exact_score, exact_matches = exact_keyword_match(cv_skills, jd_skill_names)

    # ===== OPTIMIZATION 2: Fuzzy Keyword Matching =====
    fuzzy_score, fuzzy_matches = fuzzy_keyword_match(cv_skills, jd_skill_names)

    # ===== OPTIMIZATION 3: Individual Skill Embeddings =====
    # PERFORMANCE OPTIMIZATION: Generate ALL embeddings ONCE, reuse for subsets
    # Calculate pairwise similarity matrix (full matrix with ALL JD skills)
    similarity_matrix = calculate_skill_match_matrix(cv_skills, jd_skill_names)

    # For each JD skill, find best matching CV skill (max similarity)
    best_matches = []
    for j in range(len(jd_skill_names)):
        if similarity_matrix.shape[0] > 0:
            max_sim = np.max(similarity_matrix[:, j])
            best_cv_idx = np.argmax(similarity_matrix[:, j])
            best_matches.append((cv_skills[best_cv_idx], jd_skill_names[j], max_sim))

    # Average semantic similarity
    semantic_score = np.mean([match[2] for match in best_matches]) if best_matches else 0.0

    # ===== HYBRID SCORE: 25% exact, 20% fuzzy, 55% semantic =====
    # Heavily favor semantic matching to catch related skills with different wording
    # (e.g., "REST APIs" vs "RESTful API design", "Python" vs "Python 3", "AWS" vs "AWS (EC2, Lambda)")
    overall_similarity = 0.25 * exact_score + 0.20 * fuzzy_score + 0.55 * semantic_score

    # ===== Calculate priority-specific scores =====
    # OPTIMIZATION: Extract subsets from full matrix (NO new embeddings!)
    # Critical skills
    if critical_skills:
        critical_exact, _ = exact_keyword_match(cv_skills, critical_skills)
        critical_fuzzy, _ = fuzzy_keyword_match(cv_skills, critical_skills)

        # OPTIMIZED: Extract critical columns from full similarity matrix
        critical_indices = [i for i, s in enumerate(jd_skills) if s.get("priority") == "critical"]
        if critical_indices and similarity_matrix.size > 0:
            critical_matrix = similarity_matrix[:, critical_indices]
            critical_semantic = np.mean([np.max(critical_matrix[:, j]) for j in range(len(critical_indices))])
        else:
            critical_matrix = np.array([])
            critical_semantic = 0.0

        critical_match = 0.4 * critical_exact + 0.2 * critical_fuzzy + 0.4 * critical_semantic
    else:
        critical_match = 0.0
        critical_matrix = np.array([])

    # Important skills
    if important_skills:
        important_exact, _ = exact_keyword_match(cv_skills, important_skills)
        important_fuzzy, _ = fuzzy_keyword_match(cv_skills, important_skills)

        # OPTIMIZED: Extract important columns from full similarity matrix
        important_indices = [i for i, s in enumerate(jd_skills) if s.get("priority") == "important"]
        if important_indices and similarity_matrix.size > 0:
            important_matrix = similarity_matrix[:, important_indices]
            important_semantic = np.mean([np.max(important_matrix[:, j]) for j in range(len(important_indices))])
        else:
            important_matrix = np.array([])
            important_semantic = 0.0

        important_match = 0.4 * important_exact + 0.2 * important_fuzzy + 0.4 * important_semantic
    else:
        important_match = 0.0
        important_matrix = np.array([])

    # Find missing critical skills (check exact, fuzzy, AND semantic matches)
    cv_skills_lower = [s.lower() for s in cv_skills]
    missing_critical = []

    for i, skill in enumerate(critical_skills):
        # Check if not in exact matches
        if skill.lower() not in cv_skills_lower:
            # Check if not in fuzzy matches
            is_fuzzy_match = any(
                skill.lower() in cv.lower() or cv.lower() in skill.lower()
                for cv in cv_skills
            )
            if not is_fuzzy_match:
                # Check if not in semantic matches (using critical_matrix if available)
                has_semantic_match = False
                if critical_matrix.size > 0 and i < critical_matrix.shape[1]:
                    # Get best semantic similarity for this critical skill
                    best_semantic_sim = np.max(critical_matrix[:, i])

                    # Get best matching CV skill for adaptive threshold calculation
                    best_cv_idx = np.argmax(critical_matrix[:, i])
                    best_cv_skill = cv_skills[best_cv_idx] if best_cv_idx < len(cv_skills) else ""

                    # Calculate adaptive threshold (same logic as domain/industry matching)
                    avg_length = (len(skill) + len(best_cv_skill)) / 2
                    if avg_length < 15:
                        threshold = 0.45
                    elif avg_length < 50:
                        threshold = 0.50
                    else:
                        threshold = 0.55

                    # Consider it matched if above threshold
                    if best_semantic_sim >= threshold:
                        has_semantic_match = True

                # Only add to missing if no exact, fuzzy, or semantic match
                if not has_semantic_match:
                    missing_critical.append(skill)

    # Find missing important skills (same logic as critical)
    missing_important = []

    for i, skill in enumerate(important_skills):
        # Check if not in exact matches
        if skill.lower() not in cv_skills_lower:
            # Check if not in fuzzy matches
            is_fuzzy_match = any(
                skill.lower() in cv.lower() or cv.lower() in skill.lower()
                for cv in cv_skills
            )
            if not is_fuzzy_match:
                # Check if not in semantic matches (using important_matrix if available)
                has_semantic_match = False
                if important_matrix.size > 0 and i < important_matrix.shape[1]:
                    # Get best semantic similarity for this important skill
                    best_semantic_sim = np.max(important_matrix[:, i])

                    # Get best matching CV skill for adaptive threshold calculation
                    best_cv_idx = np.argmax(important_matrix[:, i])
                    best_cv_skill = cv_skills[best_cv_idx] if best_cv_idx < len(cv_skills) else ""

                    # Calculate adaptive threshold
                    avg_length = (len(skill) + len(best_cv_skill)) / 2
                    if avg_length < 15:
                        threshold = 0.45
                    elif avg_length < 50:
                        threshold = 0.50
                    else:
                        threshold = 0.55

                    # Consider it matched if above threshold
                    if best_semantic_sim >= threshold:
                        has_semantic_match = True

                # Only add to missing if no exact, fuzzy, or semantic match
                if not has_semantic_match:
                    missing_important.append(skill)

    return {
        "overall_similarity": round(overall_similarity, 3),
        "critical_skills_match": round(critical_match, 3),
        "important_skills_match": round(important_match, 3),
        "exact_match_score": round(exact_score, 3),
        "fuzzy_match_score": round(fuzzy_score, 3),
        "semantic_match_score": round(semantic_score, 3),
        "matched_skills": list(exact_matches),
        "missing_critical": missing_critical,
        "missing_important": missing_important
    }


def calculate_experience_similarity(cv_experience: List[dict], jd_responsibilities: List[str]) -> dict:
    """
    OPTIMIZED: Recency-weighted experience similarity with chunking.
    Recent jobs are weighted higher (1.0 → 0.75 → 0.5 → ...).

    Args:
        cv_experience: List of work experience objects from CV
        jd_responsibilities: List of responsibility descriptions from JD

    Returns:
        Dictionary with overall score and per-job scores
    """
    if not cv_experience or not jd_responsibilities:
        return {
            "overall_similarity": 0.0,
            "weighted_similarity": 0.0,
            "per_job_scores": []
        }

    # ===== OPTIMIZATION 4: Recency Weighting =====
    # Most recent job = 1.0, second = 0.75, third = 0.5, fourth = 0.35, etc.
    recency_weights = [1.0, 0.75, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]

    weighted_scores = []
    per_job_scores = []

    # Batch preparation: Collect all texts to embed
    exp_texts = []
    for exp in cv_experience[:len(recency_weights)]:  # Limit to weighted jobs
        if isinstance(exp, dict):
            # Combine role, company, and achievements
            desc_parts = []
            if exp.get("role"):
                desc_parts.append(exp["role"])
            if exp.get("achievements"):
                if isinstance(exp["achievements"], list):
                    desc_parts.extend(exp["achievements"])
                else:
                    desc_parts.append(str(exp["achievements"]))

            # Chunk to optimal embedding size (512 chars)
            exp_text = " ".join(desc_parts)[:512]
            exp_texts.append(exp_text)

    # Generate all experience embeddings in batch
    exp_embeddings = get_embeddings_batch(exp_texts) if exp_texts else []

    # Generate all responsibility embeddings in batch
    resp_embeddings = get_embeddings_batch(jd_responsibilities)

    # Calculate per-job scores
    for i, exp_embedding in enumerate(exp_embeddings):
        recency_weight = recency_weights[i] if i < len(recency_weights) else 0.1

        # Compare this job to all responsibilities
        resp_similarities = []
        for resp_embedding in resp_embeddings:
            sim = calculate_cosine_similarity(exp_embedding, resp_embedding)
            resp_similarities.append(sim)

        # Use max similarity (best matching responsibility)
        max_similarity = max(resp_similarities) if resp_similarities else 0.0
        weighted_score = max_similarity * recency_weight

        weighted_scores.append(weighted_score)
        per_job_scores.append({
            "job_index": i,
            "similarity": round(max_similarity, 3),
            "recency_weight": recency_weight,
            "weighted_score": round(weighted_score, 3)
        })

    # Overall scores
    overall_similarity = np.mean([score["similarity"] for score in per_job_scores]) if per_job_scores else 0.0
    weighted_similarity = np.mean(weighted_scores) if weighted_scores else 0.0

    return {
        "overall_similarity": round(overall_similarity, 3),
        "weighted_similarity": round(weighted_similarity, 3),
        "per_job_scores": per_job_scores
    }


def calculate_overall_compatibility(parsed_cv: dict, parsed_jd: dict) -> dict:
    """
    Calculate overall compatibility between CV and JD using optimized hybrid approach.
    Includes all optimizations: caching, hybrid matching, batch processing, recency weighting.

    Args:
        parsed_cv: Parsed CV data
        parsed_jd: Parsed JD data

    Returns:
        Dictionary with comprehensive similarity metrics and cache statistics
    """
    # Extract relevant fields
    cv_skills = parsed_cv.get("technical_skills", [])
    jd_skills = parsed_jd.get("hard_skills_required", [])

    cv_experience = parsed_cv.get("work_experience", [])
    jd_responsibilities = parsed_jd.get("responsibilities", [])

    # Calculate skills similarity (with hybrid matching)
    skills_metrics = calculate_skills_similarity(cv_skills, jd_skills)

    # Calculate experience similarity (with recency weighting)
    experience_metrics = calculate_experience_similarity(cv_experience, jd_responsibilities)

    # Calculate weighted overall similarity
    # Weight: 40% skills hybrid, 25% experience weighted, 20% critical skills, 15% exact matches
    overall_similarity = (
        0.40 * skills_metrics["overall_similarity"] +
        0.25 * experience_metrics["weighted_similarity"] +
        0.20 * skills_metrics["critical_skills_match"] +
        0.15 * skills_metrics["exact_match_score"]
    )

    # Get cache statistics
    cache_stats = cache.get_stats()

    return {
        "overall_embedding_similarity": round(overall_similarity, 3),
        "skills_cosine_similarity": skills_metrics["overall_similarity"],
        "experience_cosine_similarity": experience_metrics["overall_similarity"],
        "experience_weighted_similarity": experience_metrics["weighted_similarity"],
        "critical_skills_match": skills_metrics["critical_skills_match"],
        "important_skills_match": skills_metrics["important_skills_match"],
        "exact_keyword_match": skills_metrics["exact_match_score"],
        "fuzzy_keyword_match": skills_metrics["fuzzy_match_score"],
        "semantic_skills_match": skills_metrics["semantic_match_score"],
        "missing_critical_skills": skills_metrics["missing_critical"],
        "missing_important_skills": skills_metrics["missing_important"],
        "matched_skills": skills_metrics["matched_skills"],
        "cache_stats": cache_stats
    }


def get_cache_statistics() -> dict:
    """
    Get embedding cache performance statistics.

    Returns:
        Dictionary with cache hit rates and counts
    """
    return cache.get_stats()


def clear_cache():
    """Clear all embedding caches."""
    cache.clear()
