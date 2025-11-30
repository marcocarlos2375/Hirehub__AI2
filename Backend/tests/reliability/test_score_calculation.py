#!/usr/bin/env python3
"""
Score Calculation Benchmark Test for /api/calculate-score Endpoint.
Measures timing for sequential score calculation requests (concurrency=1).

Usage:
    python tests/reliability/test_score_calculation.py

Output:
    Request  1: time=8.23s  score=72%  status=Good Match  success=true
    Request  2: time=7.89s  score=65%  status=Moderate   success=true
    ...
"""

import asyncio
import httpx
import time
import uuid
import json
from dataclasses import dataclass, field
from datetime import datetime
from statistics import mean, stdev
from pathlib import Path
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8001"
NUM_REQUESTS = 10  # Number of sequential score calculations
REQUEST_TIMEOUT = 180.0  # Score calculation can be slow (LLM + embeddings)


@dataclass
class ScoreResult:
    """Result of a single score calculation request."""
    request_id: int
    elapsed_time: float
    success: bool
    status_code: Optional[int] = None
    error: Optional[str] = None
    overall_score: Optional[int] = None
    overall_status: Optional[str] = None
    score_response: Optional[dict] = None  # Full API response


@dataclass
class BenchmarkSummary:
    """Aggregated benchmark results."""
    avg_time: float
    min_time: float
    max_time: float
    std_dev: float
    success_count: int
    total_count: int
    avg_score: Optional[float] = None
    results: list = field(default_factory=list)

    def __str__(self):
        return (
            f"avg={self.avg_time:.2f}s  "
            f"min={self.min_time:.2f}s  "
            f"max={self.max_time:.2f}s  "
            f"std={self.std_dev:.2f}s  "
            f"success={self.success_count}/{self.total_count}"
        )


def load_test_pairs() -> list[tuple[str, str, str]]:
    """
    Load CV and JD pairs for testing.

    Returns:
        List of (cv_text, jd_text, domain_name) tuples
    """
    samples_dir = Path(__file__).parent.parent.parent / "data" / "samples"
    resumes_dir = samples_dir / "resumes"
    jobs_dir = samples_dir / "job_descriptions"

    # Define CV-JD pairs (matching domains)
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
            print(f"Warning: Missing files for {domain}")

    if not loaded_pairs:
        # Fallback sample data
        loaded_pairs = [
            (
                """John Doe - Software Engineer
                5 years experience with Python, FastAPI, PostgreSQL.
                Built scalable microservices handling 1M requests/day.
                BS in Computer Science from MIT.""",
                """Senior Software Engineer
                Requirements:
                - 5+ years Python experience
                - FastAPI or Django
                - PostgreSQL
                - Microservices architecture""",
                "fallback"
            )
        ]

    return loaded_pairs


def get_httpx_client_kwargs() -> dict:
    """Get httpx client kwargs, enabling HTTP/2 if available."""
    kwargs = {}
    try:
        import h2
        kwargs['http2'] = True
    except ImportError:
        pass
    return kwargs


async def parse_document(client: httpx.AsyncClient, text: str, endpoint: str) -> Optional[dict]:
    """
    Parse a document (CV or JD) using the appropriate endpoint.

    Args:
        client: HTTP client
        text: Document text to parse
        endpoint: Either "/api/parse" or "/api/parse-cv"

    Returns:
        Parsed document dict or None if failed
    """
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
            result = response.json()
            return result.get("data")
        else:
            print(f"Parse failed ({endpoint}): {response.status_code}")
            return None
    except Exception as e:
        print(f"Parse error ({endpoint}): {e}")
        return None


async def make_score_request(
    client: httpx.AsyncClient,
    parsed_cv: dict,
    parsed_jd: dict,
    request_id: int
) -> ScoreResult:
    """Make a single score calculation request with timing."""
    start = time.perf_counter()

    # Add unique suffix to avoid cache hits
    unique_cv = parsed_cv.copy()
    if "summary" in unique_cv:
        unique_cv["summary"] = unique_cv.get("summary", "") + f" [Benchmark ID: {uuid.uuid4().hex[:8]}]"
    elif "personal_info" in unique_cv and isinstance(unique_cv["personal_info"], dict):
        unique_cv["personal_info"]["benchmark_id"] = uuid.uuid4().hex[:8]

    try:
        response = await client.post(
            f"{BASE_URL}/api/calculate-score",
            json={
                "parsed_cv": unique_cv,
                "parsed_jd": parsed_jd,
                "language": "english"
            },
            timeout=REQUEST_TIMEOUT
        )
        elapsed = time.perf_counter() - start

        if response.status_code == 200:
            score_response = response.json()
            return ScoreResult(
                request_id=request_id,
                elapsed_time=elapsed,
                success=True,
                status_code=response.status_code,
                overall_score=score_response.get("overall_score"),
                overall_status=score_response.get("overall_status"),
                score_response=score_response
            )
        else:
            error_detail = response.text[:200] if response.text else "Unknown error"
            return ScoreResult(
                request_id=request_id,
                elapsed_time=elapsed,
                success=False,
                status_code=response.status_code,
                error=error_detail
            )

    except httpx.TimeoutException:
        elapsed = time.perf_counter() - start
        return ScoreResult(
            request_id=request_id,
            elapsed_time=elapsed,
            success=False,
            error="Timeout"
        )
    except Exception as e:
        elapsed = time.perf_counter() - start
        return ScoreResult(
            request_id=request_id,
            elapsed_time=elapsed,
            success=False,
            error=str(e)
        )


def calculate_summary(results: list[ScoreResult]) -> BenchmarkSummary:
    """Calculate aggregated statistics from results."""
    times = [r.elapsed_time for r in results]
    successes = [r for r in results if r.success]
    scores = [r.overall_score for r in successes if r.overall_score is not None]

    return BenchmarkSummary(
        avg_time=mean(times) if times else 0,
        min_time=min(times) if times else 0,
        max_time=max(times) if times else 0,
        std_dev=stdev(times) if len(times) > 1 else 0,
        success_count=len(successes),
        total_count=len(results),
        avg_score=mean(scores) if scores else None,
        results=[
            {
                "request_id": r.request_id,
                "elapsed_time": round(r.elapsed_time, 3),
                "success": r.success,
                "status_code": r.status_code,
                "error": r.error,
                "overall_score": r.overall_score,
                "overall_status": r.overall_status,
                "score_response": r.score_response
            }
            for r in results
        ]
    )


async def check_health() -> bool:
    """Check if the API is healthy before running benchmark."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print(f"API Status: {data.get('status', 'unknown')}")
                return data.get('status') == 'healthy'
    except Exception as e:
        print(f"Health check failed: {e}")
    return False


async def benchmark_score_calculation():
    """Main benchmark function."""
    print("=" * 70)
    print("Score Calculation Benchmark Test for /api/calculate-score Endpoint")
    print("=" * 70)
    print(f"Configuration:")
    print(f"  - Base URL: {BASE_URL}")
    print(f"  - Concurrency: 1 (sequential)")
    print(f"  - Number of Requests: {NUM_REQUESTS}")
    print(f"  - Request Timeout: {REQUEST_TIMEOUT}s")
    print("=" * 70)

    # Health check
    print("\nChecking API health...")
    if not await check_health():
        print("ERROR: API is not healthy. Make sure the server is running.")
        print(f"  Try: curl {BASE_URL}/health")
        return []

    # Load test pairs
    print("\nLoading test data...")
    test_pairs = load_test_pairs()
    print(f"  Loaded {len(test_pairs)} CV/JD pairs")

    # Parse documents first
    print("\nParsing documents...")
    parsed_pairs = []

    async with httpx.AsyncClient(**get_httpx_client_kwargs()) as client:
        for cv_text, jd_text, domain in test_pairs:
            print(f"  Parsing {domain}...")

            # Parse JD
            parsed_jd = await parse_document(client, jd_text, "/api/parse")
            if not parsed_jd:
                print(f"    Failed to parse JD for {domain}")
                continue

            # Parse CV
            parsed_cv = await parse_document(client, cv_text, "/api/parse-cv")
            if not parsed_cv:
                print(f"    Failed to parse CV for {domain}")
                continue

            parsed_pairs.append((parsed_cv, parsed_jd, domain))
            print(f"    ✓ {domain} parsed successfully")

    if not parsed_pairs:
        print("ERROR: No valid CV/JD pairs available")
        return []

    print(f"\n  {len(parsed_pairs)} pairs ready for scoring")

    # Run score calculations
    print("\n" + "-" * 70)
    print("BENCHMARK RESULTS")
    print("-" * 70)

    results = []
    async with httpx.AsyncClient(**get_httpx_client_kwargs()) as client:
        for i in range(NUM_REQUESTS):
            # Cycle through available pairs
            parsed_cv, parsed_jd, domain = parsed_pairs[i % len(parsed_pairs)]

            print(f"\nRequest {i+1:2d} ({domain})...", end=" ", flush=True)

            result = await make_score_request(client, parsed_cv, parsed_jd, i)
            results.append(result)

            if result.success:
                print(f"time={result.elapsed_time:.2f}s  score={result.overall_score}%  status={result.overall_status}")
            else:
                print(f"time={result.elapsed_time:.2f}s  FAILED: {result.error}")

    # Calculate summary
    summary = calculate_summary(results)

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(summary)

    if summary.avg_score is not None:
        print(f"\nAverage Score: {summary.avg_score:.1f}%")

    return results, summary


def save_results_to_file(results: list[ScoreResult], summary: BenchmarkSummary) -> str:
    """Save benchmark results to data/results directory as JSON."""
    results_dir = Path(__file__).parent.parent.parent / "data" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"benchmark_scoring_{timestamp}.json"
    filepath = results_dir / filename

    output_data = {
        "benchmark_type": "score_calculation",
        "timestamp": datetime.now().isoformat(),
        "configuration": {
            "base_url": BASE_URL,
            "concurrency": 1,
            "num_requests": NUM_REQUESTS,
            "request_timeout": REQUEST_TIMEOUT
        },
        "summary": {
            "avg_time_seconds": round(summary.avg_time, 3),
            "min_time_seconds": round(summary.min_time, 3),
            "max_time_seconds": round(summary.max_time, 3),
            "std_dev_seconds": round(summary.std_dev, 3),
            "success_count": summary.success_count,
            "total_count": summary.total_count,
            "success_rate": round(summary.success_count / summary.total_count * 100, 1) if summary.total_count > 0 else 0,
            "avg_score": round(summary.avg_score, 1) if summary.avg_score else None
        },
        "individual_results": summary.results
    }

    with open(filepath, "w") as f:
        json.dump(output_data, f, indent=2)

    return str(filepath)


def main():
    """Entry point."""
    try:
        result = asyncio.run(benchmark_score_calculation())

        if result:
            results, summary = result

            # Save results to file
            filepath = save_results_to_file(results, summary)
            print(f"\n📁 Results saved to: {filepath}")

            # Exit with error if any failures
            if summary.success_count < summary.total_count:
                print(f"\nWARNING: {summary.total_count - summary.success_count} requests failed")
                exit(1)
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user")
        exit(130)


if __name__ == "__main__":
    main()
