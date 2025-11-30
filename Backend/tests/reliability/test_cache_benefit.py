#!/usr/bin/env python3
"""
Warm-up Benefit Test for /api/calculate-score Endpoint.
Tests if subsequent DIFFERENT CV/JD pairs are faster than the first due to:
- Embedding model warm-up (loaded in memory)
- HTTP connection pools ready
- LLM API connections established

Usage:
    python tests/reliability/test_cache_benefit.py

Expected Output:
    PAIR 1: computer_science (COLD START)
      time=18.5s  score=62%
    PAIR 2: logistics (AFTER WARM-UP)
      time=12.3s  score=67%  (33% faster!)
    ...
"""

import asyncio
import httpx
import time
import json
from dataclasses import dataclass
from datetime import datetime
from statistics import mean
from pathlib import Path
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8001"
REQUEST_TIMEOUT = 180.0


@dataclass
class PairResult:
    """Result for a single CV/JD pair."""
    domain: str
    elapsed_time: float
    score: Optional[int] = None
    success: bool = True
    error: Optional[str] = None
    is_cold_start: bool = False


def load_test_pairs() -> list[tuple[str, str, str]]:
    """Load all CV/JD pairs for testing."""
    samples_dir = Path(__file__).parent.parent.parent / "data" / "samples"
    resumes_dir = samples_dir / "resumes"
    jobs_dir = samples_dir / "job_descriptions"

    pairs = [
        ("computer_science_resume.txt", "computer_science_job.txt", "computer_science"),
        ("logistics_resume.txt", "logistics_job.txt", "logistics"),
        ("medicine_resume.txt", "medicine_job.txt", "medicine"),
    ]

    loaded_pairs = []
    for cv_file, jd_file, domain in pairs:
        cv_path = resumes_dir / cv_file
        jd_path = jobs_dir / jd_file

        if cv_path.exists() and jd_path.exists():
            cv_text = cv_path.read_text()
            jd_text = jd_path.read_text()
            loaded_pairs.append((cv_text, jd_text, domain))
        else:
            print(f"  Warning: Missing files for {domain}")

    return loaded_pairs


def get_httpx_client_kwargs() -> dict:
    """Get httpx client kwargs."""
    kwargs = {}
    try:
        import h2
        kwargs['http2'] = True
    except ImportError:
        pass
    return kwargs


async def clear_score_cache() -> bool:
    """Clear the score cache to ensure a fresh start."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/api/cache/clear", timeout=10.0)
            if response.status_code == 200:
                print("  Cache cleared successfully")
                return True
            else:
                print(f"  Warning: Could not clear cache ({response.status_code})")
                return False
    except Exception as e:
        print(f"  Warning: Cache clear failed: {e}")
        return False


async def parse_document(client: httpx.AsyncClient, text: str, endpoint: str) -> Optional[dict]:
    """Parse a document using the API."""
    try:
        if endpoint == "/api/parse":
            payload = {"job_description": text, "language": "english"}
        else:
            payload = {"resume_text": text, "language": "english"}

        response = await client.post(
            f"{BASE_URL}{endpoint}",
            json=payload,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            return response.json().get("data")
        return None
    except Exception as e:
        print(f"Parse error: {e}")
        return None


async def make_score_request(
    client: httpx.AsyncClient,
    parsed_cv: dict,
    parsed_jd: dict
) -> tuple[float, Optional[int], Optional[str]]:
    """Make a score calculation request. Returns (elapsed_time, score, error)."""
    start = time.perf_counter()

    try:
        response = await client.post(
            f"{BASE_URL}/api/calculate-score",
            json={
                "parsed_cv": parsed_cv,
                "parsed_jd": parsed_jd,
                "language": "english"
            },
            timeout=REQUEST_TIMEOUT
        )
        elapsed = time.perf_counter() - start

        if response.status_code == 200:
            score_response = response.json()
            return elapsed, score_response.get("overall_score"), None
        else:
            return elapsed, None, response.text[:200]

    except Exception as e:
        elapsed = time.perf_counter() - start
        return elapsed, None, str(e)


async def check_health() -> bool:
    """Check API health."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print(f"  API Status: {data.get('status')}")
                print(f"  Redis Connected: {data.get('redis_connected', False)}")
                return data.get('status') == 'healthy'
    except Exception as e:
        print(f"  Health check failed: {e}")
    return False


async def test_single_pair(
    client: httpx.AsyncClient,
    cv_text: str,
    jd_text: str,
    domain: str,
    is_cold_start: bool = False
) -> PairResult:
    """Test a single CV/JD pair (one request only)."""
    # Parse documents
    parsed_jd = await parse_document(client, jd_text, "/api/parse")
    parsed_cv = await parse_document(client, cv_text, "/api/parse-cv")

    if not parsed_cv or not parsed_jd:
        return PairResult(
            domain=domain,
            elapsed_time=0,
            success=False,
            error="Failed to parse documents",
            is_cold_start=is_cold_start
        )

    # Make ONE score request
    elapsed_time, score, error = await make_score_request(client, parsed_cv, parsed_jd)

    if error:
        return PairResult(
            domain=domain,
            elapsed_time=elapsed_time,
            success=False,
            error=error,
            is_cold_start=is_cold_start
        )

    return PairResult(
        domain=domain,
        elapsed_time=elapsed_time,
        score=score,
        success=True,
        is_cold_start=is_cold_start
    )


async def run_warmup_benefit_test():
    """Main test function."""
    print("=" * 70)
    print("Warm-up Benefit Test for /api/calculate-score")
    print("=" * 70)
    print("Testing if DIFFERENT CV/JD pairs are faster after first request")
    print("  - PAIR 1: Cold start (everything initializing)")
    print("  - PAIR 2+: Should be faster (warm-up benefit)")
    print("=" * 70)

    # Health check
    print("\nChecking API health...")
    if not await check_health():
        print("ERROR: API is not healthy")
        return None

    # Clear cache for completely cold start
    print("\nClearing cache for cold start...")
    await clear_score_cache()
    await asyncio.sleep(1)

    # Load test pairs
    print("\nLoading test pairs...")
    test_pairs = load_test_pairs()
    print(f"  Loaded {len(test_pairs)} CV/JD pairs")

    if not test_pairs:
        print("ERROR: No test pairs available")
        return None

    # Test each pair (ONE request per pair)
    print("\n" + "-" * 70)
    print("WARM-UP BENEFIT TEST RESULTS")
    print("-" * 70)

    results = []
    async with httpx.AsyncClient(**get_httpx_client_kwargs()) as client:
        for i, (cv_text, jd_text, domain) in enumerate(test_pairs):
            is_cold_start = (i == 0)
            label = "COLD START" if is_cold_start else "AFTER WARM-UP"

            print(f"\nPAIR {i+1}: {domain} ({label})")

            result = await test_single_pair(client, cv_text, jd_text, domain, is_cold_start)
            results.append(result)

            if result.success:
                if is_cold_start:
                    print(f"  time={result.elapsed_time:.3f}s  score={result.score}%")
                else:
                    # Calculate improvement vs cold start
                    cold_time = results[0].elapsed_time
                    improvement = ((cold_time - result.elapsed_time) / cold_time) * 100
                    if improvement > 0:
                        print(f"  time={result.elapsed_time:.3f}s  score={result.score}%  ({improvement:.0f}% faster than cold start!)")
                    else:
                        print(f"  time={result.elapsed_time:.3f}s  score={result.score}%  (no improvement)")
            else:
                print(f"  FAILED: {result.error}")

    # Analysis
    print("\n" + "=" * 70)
    print("WARM-UP BENEFIT ANALYSIS")
    print("=" * 70)

    successful = [r for r in results if r.success]
    if len(successful) >= 2:
        cold_time = successful[0].elapsed_time
        warm_times = [r.elapsed_time for r in successful[1:]]
        avg_warm_time = mean(warm_times)

        improvement = ((cold_time - avg_warm_time) / cold_time) * 100

        print(f"\nFirst request (cold start):    {cold_time:.3f}s")
        print(f"Subsequent requests (avg):     {avg_warm_time:.3f}s")

        if improvement > 0:
            print(f"Warm-up benefit:               {improvement:.0f}% faster after first request")
            if improvement > 20:
                print(f"\n  SIGNIFICANT WARM-UP BENEFIT DETECTED!")
            elif improvement > 10:
                print(f"\n  Moderate warm-up benefit detected")
            else:
                print(f"\n  Minor warm-up benefit detected")
        else:
            print(f"\n  NO warm-up benefit detected (subsequent requests were not faster)")

    return results


def save_results(results: list[PairResult]) -> str:
    """Save results to file."""
    results_dir = Path(__file__).parent.parent.parent / "data" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"warmup_benefit_{timestamp}.json"
    filepath = results_dir / filename

    successful = [r for r in results if r.success]
    cold_time = successful[0].elapsed_time if successful else 0
    warm_times = [r.elapsed_time for r in successful[1:]] if len(successful) > 1 else []
    avg_warm = mean(warm_times) if warm_times else 0
    improvement = ((cold_time - avg_warm) / cold_time * 100) if cold_time > 0 and avg_warm > 0 else 0

    output_data = {
        "test_type": "warmup_benefit",
        "endpoint": "/api/calculate-score",
        "timestamp": datetime.now().isoformat(),
        "analysis": {
            "cold_start_time": round(cold_time, 3),
            "avg_warm_time": round(avg_warm, 3),
            "improvement_percent": round(improvement, 1),
            "warmup_benefit_detected": improvement > 10
        },
        "results": [
            {
                "domain": r.domain,
                "elapsed_time": round(r.elapsed_time, 3),
                "score": r.score,
                "success": r.success,
                "is_cold_start": r.is_cold_start,
                "error": r.error
            }
            for r in results
        ]
    }

    with open(filepath, "w") as f:
        json.dump(output_data, f, indent=2)

    return str(filepath)


def main():
    """Entry point."""
    try:
        results = asyncio.run(run_warmup_benefit_test())

        if results:
            filepath = save_results(results)
            print(f"\n  Results saved to: {filepath}")
    except KeyboardInterrupt:
        print("\nTest interrupted")
        exit(130)


if __name__ == "__main__":
    main()
