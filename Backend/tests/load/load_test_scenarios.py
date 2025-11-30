"""
Load Test Scenarios (Phase 3.4).
Defines realistic user scenarios for load testing.
"""

from typing import Dict, Any, List
import random


# ========================================
# Sample Data Generators
# ========================================

def generate_sample_gaps(count: int = 10) -> List[Dict[str, Any]]:
    """Generate sample gaps for testing."""
    gap_templates = [
        {"title": "AWS Lambda", "description": "Serverless computing", "priority": "CRITICAL"},
        {"title": "Docker", "description": "Container platform", "priority": "CRITICAL"},
        {"title": "Kubernetes", "description": "Container orchestration", "priority": "IMPORTANT"},
        {"title": "React", "description": "Frontend framework", "priority": "IMPORTANT"},
        {"title": "PostgreSQL", "description": "Relational database", "priority": "IMPORTANT"},
        {"title": "Redis", "description": "In-memory cache", "priority": "MEDIUM"},
        {"title": "GraphQL", "description": "API query language", "priority": "MEDIUM"},
        {"title": "TypeScript", "description": "Typed JavaScript", "priority": "NICE_TO_HAVE"},
        {"title": "Jest", "description": "Testing framework", "priority": "NICE_TO_HAVE"},
        {"title": "Webpack", "description": "Module bundler", "priority": "LOW"},
    ]

    return gap_templates[:count]


def generate_sample_cv() -> Dict[str, Any]:
    """Generate sample CV for testing."""
    return {
        "job_title": "Software Engineer",
        "work_experience": [
            {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "duration": "2 years",
                "responsibilities": ["Built APIs", "Managed databases"]
            }
        ],
        "skills": ["Python", "FastAPI", "PostgreSQL"],
        "education": [
            {
                "degree": "BS Computer Science",
                "institution": "University",
                "year": "2021"
            }
        ]
    }


def generate_sample_jd() -> Dict[str, Any]:
    """Generate sample job description for testing."""
    return {
        "job_title": "Senior Full Stack Engineer",
        "required_skills": ["AWS", "Docker", "React", "PostgreSQL"],
        "nice_to_have_skills": ["Kubernetes", "Redis", "GraphQL"],
        "experience_required": "3-5 years",
        "responsibilities": [
            "Build scalable microservices",
            "Deploy containerized applications",
            "Mentor junior engineers"
        ]
    }


# ========================================
# Load Test Scenarios
# ========================================

class LoadTestScenario:
    """Base class for load test scenarios."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description


class BaselineLoadScenario(LoadTestScenario):
    """
    Baseline load scenario (Phase 3.4).

    Simulates normal production load:
    - 100 concurrent users
    - 10 questions per user
    - 5-minute duration
    - Expected: p95 < 2s
    """

    def __init__(self):
        super().__init__(
            name="Baseline Load",
            description="Normal production load - 100 concurrent users"
        )
        self.concurrent_users = 100
        self.questions_per_user = 10
        self.duration_minutes = 5
        self.expected_p95_ms = 2000
        self.expected_error_rate = 1.0  # < 1%


class PeakLoadScenario(LoadTestScenario):
    """
    Peak load scenario (Phase 3.4).

    Simulates peak usage:
    - 500 concurrent users
    - 10 questions per user
    - 10-minute duration
    - Expected: p95 < 3s
    """

    def __init__(self):
        super().__init__(
            name="Peak Load",
            description="Peak usage - 500 concurrent users"
        )
        self.concurrent_users = 500
        self.questions_per_user = 10
        self.duration_minutes = 10
        self.expected_p95_ms = 3000
        self.expected_error_rate = 2.0  # < 2%


class StressTestScenario(LoadTestScenario):
    """
    Stress test scenario (Phase 3.4).

    Finds breaking point:
    - 1000 concurrent users
    - Ramp up over 5 minutes
    - 15-minute sustained load
    - Goal: Identify limits
    """

    def __init__(self):
        super().__init__(
            name="Stress Test",
            description="Find breaking point - 1000 concurrent users"
        )
        self.concurrent_users = 1000
        self.ramp_up_minutes = 5
        self.duration_minutes = 15
        self.expected_p95_ms = 5000  # Acceptable degradation
        self.expected_error_rate = 5.0  # < 5%


class BatchGenerationLoadScenario(LoadTestScenario):
    """
    Batch generation load scenario (Phase 3.4).

    Tests batch endpoint:
    - 200 concurrent batch requests
    - 10 gaps per batch
    - Expected: 80%+ cache hit rate
    """

    def __init__(self):
        super().__init__(
            name="Batch Generation Load",
            description="Test batch endpoint - 200 concurrent requests"
        )
        self.concurrent_requests = 200
        self.gaps_per_batch = 10
        self.duration_minutes = 5
        self.expected_cache_hit_rate = 80.0  # 80%+
        self.expected_p95_ms = 5000  # Batch is slower


# ========================================
# Scenario Registry
# ========================================

SCENARIOS = {
    "baseline": BaselineLoadScenario(),
    "peak": PeakLoadScenario(),
    "stress": StressTestScenario(),
    "batch": BatchGenerationLoadScenario(),
}


def get_scenario(name: str) -> LoadTestScenario:
    """Get scenario by name."""
    if name not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {name}")
    return SCENARIOS[name]


def list_scenarios() -> List[str]:
    """List available scenarios."""
    return list(SCENARIOS.keys())


# ========================================
# Example Usage
# ========================================

if __name__ == "__main__":
    """Display available scenarios."""
    print("=" * 80)
    print("Load Test Scenarios (Phase 3.4)")
    print("=" * 80)

    for name, scenario in SCENARIOS.items():
        print(f"\n📊 {scenario.name}")
        print(f"   Key: {name}")
        print(f"   Description: {scenario.description}")

        if hasattr(scenario, 'concurrent_users'):
            print(f"   Concurrent users: {scenario.concurrent_users}")
        if hasattr(scenario, 'concurrent_requests'):
            print(f"   Concurrent requests: {scenario.concurrent_requests}")
        if hasattr(scenario, 'duration_minutes'):
            print(f"   Duration: {scenario.duration_minutes} minutes")
        if hasattr(scenario, 'expected_p95_ms'):
            print(f"   Expected p95: {scenario.expected_p95_ms}ms")

    print("\n" + "=" * 80)
    print(f"Total scenarios: {len(SCENARIOS)}")
    print("=" * 80)
