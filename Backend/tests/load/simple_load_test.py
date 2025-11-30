"""
Simple Load Testing (Phase 3.4).
Lightweight load testing without external dependencies.

Uses Python asyncio for concurrent requests.
For production, consider using Locust or k6.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import statistics


# ========================================
# Load Test Results
# ========================================

@dataclass
class RequestResult:
    """Single request result."""
    duration_ms: float
    success: bool
    error: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class LoadTestResults:
    """Aggregated load test results."""
    scenario_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    duration_seconds: float
    requests_per_second: float
    avg_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    error_rate_percent: float

    def passes_criteria(
        self,
        max_p95_ms: float,
        max_error_rate: float
    ) -> bool:
        """Check if results meet acceptance criteria."""
        return (
            self.p95_latency_ms <= max_p95_ms and
            self.error_rate_percent <= max_error_rate
        )


# ========================================
# Simple Load Tester
# ========================================

class SimpleLoadTester:
    """
    Simple load testing framework (Phase 3.4).

    Features:
    - Concurrent async requests
    - Latency tracking (p50, p95, p99)
    - Error rate calculation
    - Ramp-up support
    - Results reporting
    """

    def __init__(self, scenario_name: str = "test"):
        self.scenario_name = scenario_name
        self.results: List[RequestResult] = []

    async def simulate_request(
        self,
        request_func,
        *args,
        **kwargs
    ) -> RequestResult:
        """
        Simulate a single request.

        Args:
            request_func: Async function to call
            *args, **kwargs: Arguments to pass to function

        Returns:
            RequestResult with timing and success status
        """
        start_time = time.time()

        try:
            # Call the request function
            await request_func(*args, **kwargs)

            duration_ms = (time.time() - start_time) * 1000

            return RequestResult(
                duration_ms=duration_ms,
                success=True
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            return RequestResult(
                duration_ms=duration_ms,
                success=False,
                error=str(e)
            )

    async def run_concurrent_requests(
        self,
        request_func,
        num_requests: int,
        concurrency: int,
        *args,
        **kwargs
    ) -> List[RequestResult]:
        """
        Run concurrent requests in batches.

        Args:
            request_func: Async function to call
            num_requests: Total number of requests
            concurrency: Max concurrent requests
            *args, **kwargs: Arguments to pass to function

        Returns:
            List of RequestResult
        """
        results = []

        # Process requests in batches
        for i in range(0, num_requests, concurrency):
            batch_size = min(concurrency, num_requests - i)

            # Create batch of concurrent requests
            batch = [
                self.simulate_request(request_func, *args, **kwargs)
                for _ in range(batch_size)
            ]

            # Execute batch
            batch_results = await asyncio.gather(*batch)
            results.extend(batch_results)

            # Brief pause between batches to avoid overwhelming
            await asyncio.sleep(0.01)

        return results

    async def run_load_test(
        self,
        request_func,
        total_requests: int,
        concurrent_users: int,
        *args,
        **kwargs
    ) -> LoadTestResults:
        """
        Run load test.

        Args:
            request_func: Async function to test
            total_requests: Total number of requests
            concurrent_users: Max concurrent requests
            *args, **kwargs: Arguments to pass to function

        Returns:
            LoadTestResults with aggregated statistics
        """
        print(f"\n🔥 Starting load test: {self.scenario_name}")
        print(f"   Total requests: {total_requests}")
        print(f"   Concurrent users: {concurrent_users}")

        start_time = time.time()

        # Run concurrent requests
        self.results = await self.run_concurrent_requests(
            request_func,
            total_requests,
            concurrent_users,
            *args,
            **kwargs
        )

        duration_seconds = time.time() - start_time

        # Calculate statistics
        return self._calculate_results(duration_seconds)

    def _calculate_results(self, duration_seconds: float) -> LoadTestResults:
        """Calculate aggregated results."""
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total - successful

        # Get latencies
        latencies = [r.duration_ms for r in self.results]

        # Calculate percentiles
        latencies_sorted = sorted(latencies)
        p95_index = int(len(latencies_sorted) * 0.95)
        p99_index = int(len(latencies_sorted) * 0.99)

        return LoadTestResults(
            scenario_name=self.scenario_name,
            total_requests=total,
            successful_requests=successful,
            failed_requests=failed,
            duration_seconds=duration_seconds,
            requests_per_second=total / duration_seconds if duration_seconds > 0 else 0,
            avg_latency_ms=statistics.mean(latencies) if latencies else 0,
            median_latency_ms=statistics.median(latencies) if latencies else 0,
            p95_latency_ms=latencies_sorted[p95_index] if latencies_sorted else 0,
            p99_latency_ms=latencies_sorted[p99_index] if latencies_sorted else 0,
            min_latency_ms=min(latencies) if latencies else 0,
            max_latency_ms=max(latencies) if latencies else 0,
            error_rate_percent=(failed / total * 100) if total > 0 else 0
        )

    def print_results(self, results: LoadTestResults):
        """Print formatted results."""
        print(f"\n" + "=" * 80)
        print(f"Load Test Results: {results.scenario_name}")
        print("=" * 80)

        print(f"\n📊 Summary:")
        print(f"   Total requests: {results.total_requests}")
        print(f"   Successful: {results.successful_requests}")
        print(f"   Failed: {results.failed_requests}")
        print(f"   Error rate: {results.error_rate_percent:.2f}%")
        print(f"   Duration: {results.duration_seconds:.2f}s")
        print(f"   Throughput: {results.requests_per_second:.2f} req/s")

        print(f"\n⏱️  Latency Statistics:")
        print(f"   Average: {results.avg_latency_ms:.2f}ms")
        print(f"   Median: {results.median_latency_ms:.2f}ms")
        print(f"   P95: {results.p95_latency_ms:.2f}ms")
        print(f"   P99: {results.p99_latency_ms:.2f}ms")
        print(f"   Min: {results.min_latency_ms:.2f}ms")
        print(f"   Max: {results.max_latency_ms:.2f}ms")


# ========================================
# Example Load Tests
# ========================================

async def example_fast_operation():
    """Simulate fast operation (100ms)."""
    await asyncio.sleep(0.1)


async def example_slow_operation():
    """Simulate slow operation (500ms)."""
    await asyncio.sleep(0.5)


async def example_failing_operation():
    """Simulate operation that sometimes fails."""
    if time.time() % 10 < 1:  # ~10% failure rate
        raise Exception("Simulated failure")
    await asyncio.sleep(0.2)


# ========================================
# Run Example Load Tests
# ========================================

async def run_baseline_load_test():
    """
    Run baseline load test (Phase 3.4).

    Scenario: 100 concurrent users, 1000 total requests
    Expected: p95 < 200ms, error rate < 1%
    """
    print("=" * 80)
    print("Baseline Load Test")
    print("=" * 80)

    tester = SimpleLoadTester("Baseline")

    results = await tester.run_load_test(
        request_func=example_fast_operation,
        total_requests=1000,
        concurrent_users=100
    )

    tester.print_results(results)

    # Check acceptance criteria
    passes = results.passes_criteria(
        max_p95_ms=200,
        max_error_rate=1.0
    )

    if passes:
        print(f"\n✅ PASS: Baseline load test passed acceptance criteria")
    else:
        print(f"\n❌ FAIL: Baseline load test failed acceptance criteria")
        if results.p95_latency_ms > 200:
            print(f"   • P95 latency too high: {results.p95_latency_ms:.2f}ms > 200ms")
        if results.error_rate_percent > 1.0:
            print(f"   • Error rate too high: {results.error_rate_percent:.2f}% > 1%")

    print("=" * 80)


async def run_peak_load_test():
    """
    Run peak load test (Phase 3.4).

    Scenario: 500 concurrent users, 5000 total requests
    Expected: p95 < 600ms, error rate < 2%
    """
    print("\n" + "=" * 80)
    print("Peak Load Test")
    print("=" * 80)

    tester = SimpleLoadTester("Peak")

    results = await tester.run_load_test(
        request_func=example_slow_operation,
        total_requests=5000,
        concurrent_users=500
    )

    tester.print_results(results)

    # Check acceptance criteria
    passes = results.passes_criteria(
        max_p95_ms=600,
        max_error_rate=2.0
    )

    if passes:
        print(f"\n✅ PASS: Peak load test passed acceptance criteria")
    else:
        print(f"\n❌ FAIL: Peak load test failed acceptance criteria")

    print("=" * 80)


async def run_stress_test():
    """
    Run stress test (Phase 3.4).

    Scenario: 1000 concurrent users, 10000 total requests
    Goal: Find breaking point
    """
    print("\n" + "=" * 80)
    print("Stress Test")
    print("=" * 80)

    tester = SimpleLoadTester("Stress")

    results = await tester.run_load_test(
        request_func=example_failing_operation,
        total_requests=10000,
        concurrent_users=1000
    )

    tester.print_results(results)

    print(f"\n📊 Stress Test Analysis:")
    print(f"   System handled {results.successful_requests}/{results.total_requests} requests")
    print(f"   Error rate: {results.error_rate_percent:.2f}%")

    if results.error_rate_percent < 5:
        print(f"   ✅ System stable under stress")
    elif results.error_rate_percent < 10:
        print(f"   ⚠️  System degraded but operational")
    else:
        print(f"   ❌ System breaking point reached")

    print("=" * 80)


# ========================================
# Main Test Runner
# ========================================

async def run_all_load_tests():
    """Run all load test scenarios."""
    await run_baseline_load_test()
    await run_peak_load_test()
    await run_stress_test()

    print("\n" + "=" * 80)
    print("🎉 All load tests complete!")
    print("=" * 80)


if __name__ == "__main__":
    """Run load tests."""
    asyncio.run(run_all_load_tests())
