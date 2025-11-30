#!/usr/bin/env python3
"""
Concurrency Benchmark Test for Parsing Endpoint.
Measures timing at different concurrency levels (1, 2, 5, 10 concurrent requests).

Usage:
    python tests/reliability/test_concurrent_parsing.py

Output:
    Concurrency Level 1:  avg=2.3s  min=2.1s  max=2.5s  success=10/10
    Concurrency Level 2:  avg=2.8s  min=2.2s  max=3.4s  success=10/10
    ...
"""

import asyncio
import httpx
import time
import uuid
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from statistics import mean, stdev
from pathlib import Path
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8001"
CONCURRENCY_LEVELS = [1, 2, 5, 10, 30]
REQUESTS_PER_LEVEL = 10  # 10 requests at each concurrency level
REQUEST_TIMEOUT = 120.0  # LLM calls can be slow, increase for high concurrency


@dataclass
class RequestResult:
    """Result of a single request."""
    elapsed_time: float
    success: bool
    status_code: Optional[int] = None
    error: Optional[str] = None
    parse_result: Optional[dict] = None  # The actual parsing result from API
    request_id: Optional[int] = None  # Request number within batch


@dataclass
class BenchmarkResult:
    """Aggregated results for a concurrency level."""
    concurrency: int
    avg_time: float
    min_time: float
    max_time: float
    std_dev: float
    success_count: int
    total_count: int
    errors: list = field(default_factory=list)
    individual_results: list = field(default_factory=list)  # All individual request results

    def __str__(self):
        return (
            f"Concurrency Level {self.concurrency:2d}: "
            f"avg={self.avg_time:.2f}s  "
            f"min={self.min_time:.2f}s  "
            f"max={self.max_time:.2f}s  "
            f"std={self.std_dev:.2f}s  "
            f"success={self.success_count}/{self.total_count}"
        )


def load_job_descriptions() -> list[str]:
    """Load sample job descriptions and create unique variations."""
    samples_dir = Path(__file__).parent.parent.parent / "data" / "samples" / "job_descriptions"

    job_files = [
        samples_dir / "computer_science_job.txt",
        samples_dir / "logistics_job.txt",
        samples_dir / "medicine_job.txt",
    ]

    base_descriptions = []
    for job_file in job_files:
        if job_file.exists():
            base_descriptions.append(job_file.read_text())

    if not base_descriptions:
        # Fallback if no sample files exist
        base_descriptions = [
            """Senior Software Engineer Position

            We are looking for a Senior Software Engineer to join our team.

            Requirements:
            - 5+ years of experience with Python
            - Experience with FastAPI or Django
            - Knowledge of PostgreSQL and Redis
            - Familiarity with Docker and Kubernetes
            - Strong problem-solving skills

            Responsibilities:
            - Design and implement scalable backend services
            - Write clean, maintainable code
            - Participate in code reviews
            - Mentor junior developers
            """
        ]

    # Create unique variations to avoid cache hits
    # Total needed: max(CONCURRENCY_LEVELS) * REQUESTS_PER_LEVEL = 30 * 10 = 300
    unique_descriptions = []
    for i in range(max(CONCURRENCY_LEVELS) * REQUESTS_PER_LEVEL):
        base = base_descriptions[i % len(base_descriptions)]
        # Add unique identifier to prevent caching
        unique_id = f"\n\n[Benchmark Request ID: {uuid.uuid4().hex[:8]}-{i}]"
        unique_descriptions.append(base + unique_id)

    return unique_descriptions


def get_httpx_client_kwargs() -> dict:
    """Get httpx client kwargs, enabling HTTP/2 if available."""
    kwargs = {}
    try:
        import h2
        kwargs['http2'] = True
    except ImportError:
        pass  # HTTP/2 not available, use HTTP/1.1
    return kwargs


async def make_parse_request(client: httpx.AsyncClient, job_description: str, request_id: int = 0) -> RequestResult:
    """Make a single parse request with timing and capture the parsing result."""
    start = time.perf_counter()
    try:
        response = await client.post(
            f"{BASE_URL}/api/parse",
            json={"job_description": job_description, "language": "english"},
            timeout=REQUEST_TIMEOUT
        )
        elapsed = time.perf_counter() - start

        success = response.status_code == 200
        if not success:
            error_detail = response.text[:200] if response.text else "Unknown error"
            return RequestResult(elapsed, False, response.status_code, error_detail, request_id=request_id)

        # Parse the response JSON to capture the actual parsing result
        parse_result = response.json()
        return RequestResult(elapsed, True, response.status_code, parse_result=parse_result, request_id=request_id)

    except httpx.TimeoutException:
        elapsed = time.perf_counter() - start
        return RequestResult(elapsed, False, error="Timeout", request_id=request_id)
    except Exception as e:
        elapsed = time.perf_counter() - start
        return RequestResult(elapsed, False, error=str(e), request_id=request_id)


async def run_concurrent_batch(
    concurrency: int,
    job_descriptions: list[str]
) -> list[RequestResult]:
    """
    Run requests at the specified concurrency level.

    For concurrency N, we fire N requests simultaneously, wait for all to complete,
    then repeat until we've made REQUESTS_PER_LEVEL total requests.
    """
    results = []
    descriptions_to_use = job_descriptions[:REQUESTS_PER_LEVEL]
    request_counter = 0

    async with httpx.AsyncClient(**get_httpx_client_kwargs()) as client:
        # Process in batches of 'concurrency' size
        for batch_start in range(0, len(descriptions_to_use), concurrency):
            batch_end = min(batch_start + concurrency, len(descriptions_to_use))
            batch_descriptions = descriptions_to_use[batch_start:batch_end]

            # Fire concurrent requests with request IDs
            tasks = [
                make_parse_request(client, jd, request_id=request_counter + i)
                for i, jd in enumerate(batch_descriptions)
            ]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            request_counter += len(batch_descriptions)

    return results


def calculate_benchmark_result(concurrency: int, results: list[RequestResult]) -> BenchmarkResult:
    """Calculate aggregated statistics from request results."""
    times = [r.elapsed_time for r in results]
    successes = [r for r in results if r.success]
    errors = [r.error for r in results if r.error]

    # Store individual results for later export
    individual_results = [
        {
            "request_id": r.request_id,
            "elapsed_time": round(r.elapsed_time, 3),
            "success": r.success,
            "status_code": r.status_code,
            "error": r.error,
            "parse_result": r.parse_result
        }
        for r in results
    ]

    return BenchmarkResult(
        concurrency=concurrency,
        avg_time=mean(times) if times else 0,
        min_time=min(times) if times else 0,
        max_time=max(times) if times else 0,
        std_dev=stdev(times) if len(times) > 1 else 0,
        success_count=len(successes),
        total_count=len(results),
        errors=errors[:5],  # Keep first 5 errors
        individual_results=individual_results
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


async def benchmark_concurrency():
    """Main benchmark function."""
    print("=" * 70)
    print("Concurrency Benchmark Test for /api/parse Endpoint")
    print("=" * 70)
    print(f"Configuration:")
    print(f"  - Base URL: {BASE_URL}")
    print(f"  - Concurrency Levels: {CONCURRENCY_LEVELS}")
    print(f"  - Requests per Level: {REQUESTS_PER_LEVEL}")
    print(f"  - Request Timeout: {REQUEST_TIMEOUT}s")
    print("=" * 70)

    # Health check
    print("\nChecking API health...")
    if not await check_health():
        print("ERROR: API is not healthy. Make sure the server is running.")
        print(f"  Try: curl {BASE_URL}/health")
        return []

    # Load test data
    print("\nLoading test data...")
    job_descriptions = load_job_descriptions()
    print(f"  Loaded {len(job_descriptions)} unique job descriptions")

    # Warm-up request
    print("\nWarm-up request...")
    async with httpx.AsyncClient(**get_httpx_client_kwargs()) as client:
        warmup_result = await make_parse_request(client, job_descriptions[0])
        print(f"  Warm-up: {warmup_result.elapsed_time:.2f}s ({'OK' if warmup_result.success else 'FAILED'})")

    # Run benchmarks
    print("\n" + "-" * 70)
    print("BENCHMARK RESULTS")
    print("-" * 70)

    all_results = []
    for level in CONCURRENCY_LEVELS:
        print(f"\nTesting concurrency level {level}...")

        # Use different job descriptions for each level to avoid cache
        start_idx = CONCURRENCY_LEVELS.index(level) * REQUESTS_PER_LEVEL
        level_descriptions = job_descriptions[start_idx:start_idx + REQUESTS_PER_LEVEL]

        batch_results = await run_concurrent_batch(level, level_descriptions)
        result = calculate_benchmark_result(level, batch_results)
        all_results.append(result)

        print(result)
        if result.errors:
            print(f"    Errors: {result.errors[:3]}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for result in all_results:
        print(result)

    # Calculate throughput
    print("\n" + "-" * 70)
    print("THROUGHPUT ANALYSIS")
    print("-" * 70)
    for result in all_results:
        if result.avg_time > 0:
            throughput = result.concurrency / result.avg_time
            print(f"Concurrency {result.concurrency:2d}: ~{throughput:.2f} requests/second")

    return all_results


def save_results_to_file(results: list[BenchmarkResult]) -> str:
    """
    Save benchmark results to data/results directory as JSON.

    Returns:
        Path to the saved file
    """
    # Create results directory if it doesn't exist
    results_dir = Path(__file__).parent.parent.parent / "data" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"benchmark_parsing_{timestamp}.json"
    filepath = results_dir / filename

    # Prepare data for JSON serialization
    output_data = {
        "benchmark_type": "parsing_endpoint_concurrency",
        "timestamp": datetime.now().isoformat(),
        "configuration": {
            "base_url": BASE_URL,
            "concurrency_levels": CONCURRENCY_LEVELS,
            "requests_per_level": REQUESTS_PER_LEVEL,
            "request_timeout": REQUEST_TIMEOUT
        },
        "results": [
            {
                "concurrency": r.concurrency,
                "avg_time_seconds": round(r.avg_time, 3),
                "min_time_seconds": round(r.min_time, 3),
                "max_time_seconds": round(r.max_time, 3),
                "std_dev_seconds": round(r.std_dev, 3),
                "success_count": r.success_count,
                "total_count": r.total_count,
                "success_rate": round(r.success_count / r.total_count * 100, 1) if r.total_count > 0 else 0,
                "throughput_req_per_sec": round(r.concurrency / r.avg_time, 2) if r.avg_time > 0 else 0,
                "errors": r.errors[:5] if r.errors else [],
                "individual_requests": r.individual_results  # Include all individual parsing results
            }
            for r in results
        ],
        "summary": {
            "total_requests": sum(r.total_count for r in results),
            "total_success": sum(r.success_count for r in results),
            "overall_success_rate": round(
                sum(r.success_count for r in results) / sum(r.total_count for r in results) * 100, 1
            ) if sum(r.total_count for r in results) > 0 else 0
        }
    }

    # Write to file
    with open(filepath, "w") as f:
        json.dump(output_data, f, indent=2)

    return str(filepath)


def main():
    """Entry point."""
    try:
        results = asyncio.run(benchmark_concurrency())

        # Save results to file
        if results:
            filepath = save_results_to_file(results)
            print(f"\n📁 Results saved to: {filepath}")

            # Exit with error if any failures
            total_success = sum(r.success_count for r in results)
            total_requests = sum(r.total_count for r in results)
            if total_success < total_requests:
                print(f"\nWARNING: {total_requests - total_success} requests failed")
                exit(1)
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user")
        exit(130)


if __name__ == "__main__":
    main()
