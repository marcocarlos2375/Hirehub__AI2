"""
Endpoint Reliability Test Runner

Sequential test execution for job descriptions to validate /api/calculate-score endpoint.
Focus: Error isolation, detailed failure analysis, comprehensive reporting.
"""

import json
import time
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict
from error_classifier import ErrorClassifier


class EndpointReliabilityTester:
    """
    Sequential test execution for 50-100 job descriptions.
    Focus: Error isolation and detailed failure analysis.
    """

    def __init__(self,
                 jobs_file: str,
                 cv_file: str,
                 api_base: str = 'http://localhost:8001'):
        """
        Initialize tester.

        Args:
            jobs_file: Path to JSONL file with job descriptions
            cv_file: Path to JSON file with test CV
            api_base: API base URL
        """
        self.jobs = self.load_jobs(jobs_file)
        self.test_cv = self.load_cv(cv_file)
        self.api_base = api_base
        self.results = []
        self.parsed_cv = None  # Cache parsed CV

    def load_jobs(self, jobs_file: str) -> List[Dict]:
        """
        Load jobs from JSONL file.

        Args:
            jobs_file: Path to JSONL file

        Returns:
            List of job dictionaries
        """
        jobs = []
        path = Path(jobs_file)

        if not path.exists():
            print(f"❌ Jobs file not found: {jobs_file}")
            return []

        with open(path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                try:
                    job = json.loads(line.strip())
                    job['test_id'] = i  # Add sequential ID
                    jobs.append(job)
                except json.JSONDecodeError as e:
                    print(f"⚠️  Skipping line {i}: Invalid JSON - {e}")

        print(f"✅ Loaded {len(jobs)} jobs from {jobs_file}")
        return jobs

    def load_cv(self, cv_file: str) -> Dict:
        """
        Load test CV from JSON file.

        Args:
            cv_file: Path to JSON file

        Returns:
            CV dictionary
        """
        path = Path(cv_file)

        if not path.exists():
            print(f"❌ CV file not found: {cv_file}")
            return {}

        with open(path, 'r', encoding='utf-8') as f:
            cv = json.load(f)

        print(f"✅ Loaded test CV from {cv_file}")
        return cv

    async def run_all_tests(self):
        """Run tests sequentially (better for debugging)."""
        print(f"\n{'='*70}")
        print(f"🧪 Starting Endpoint Reliability Test")
        print(f"   Total Jobs: {len(self.jobs)}")
        print(f"   API Base: {self.api_base}")
        print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")

        # Parse CV once and cache
        print("📝 Parsing test CV...")
        self.parsed_cv = await self.parse_cv()

        if not self.parsed_cv:
            print("❌ Failed to parse test CV. Aborting tests.")
            return

        print(f"✅ Test CV parsed successfully\n")

        # Run tests
        start_time = time.time()

        for i, job in enumerate(self.jobs, 1):
            print(f"[{i}/{len(self.jobs)}] Testing: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")

            result = await self.test_single_job(job)
            self.results.append(result)

            # Real-time failure logging
            if not result['success']:
                self.log_failure(job, result)

            # Brief pause between tests
            await asyncio.sleep(0.5)

        total_time = time.time() - start_time

        # Generate and display report
        print(f"\n{'='*70}")
        print(f"✅ Testing Complete")
        print(f"   Total Time: {total_time:.2f}s")
        print(f"{'='*70}\n")

        self.generate_report()

    async def parse_cv(self) -> Optional[Dict]:
        """Parse test CV once and cache."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/api/parse-cv",
                    json={
                        "resume_text": json.dumps(self.test_cv),
                        "language": "english"
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"❌ CV parsing failed: {response.status}")
                        return None

        except Exception as e:
            print(f"❌ CV parsing error: {e}")
            return None

    async def test_single_job(self, job: Dict) -> Dict:
        """
        Test single job description.

        Args:
            job: Job dictionary with 'description' field

        Returns:
            Result dictionary
        """
        start_time = time.time()
        job_id = job.get('test_id', job.get('id', 'unknown'))
        timeout_val = self.get_timeout(job.get('complexity_score', 50))

        try:
            # Step 1: Parse JD
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/api/parse",
                    json={
                        "job_description": job.get('description', ''),
                        "language": "english"
                    },
                    timeout=aiohttp.ClientTimeout(total=timeout_val)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return self.error_result(
                            job_id,
                            'jd_parsing_failed',
                            response.status,
                            error_text,
                            start_time
                        )

                    parsed_jd = await response.json()

            # Step 2: Calculate Score
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/api/calculate-score",
                    json={
                        "parsed_cv": self.parsed_cv,
                        "parsed_jd": parsed_jd,
                        "language": "english"
                    },
                    timeout=aiohttp.ClientTimeout(total=timeout_val)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return self.error_result(
                            job_id,
                            'score_calculation_failed',
                            response.status,
                            error_text,
                            start_time
                        )

                    score_data = await response.json()

            # Success!
            latency = time.time() - start_time
            print(f"   ✅ SUCCESS - Score: {score_data.get('overall_score')}% - {latency:.2f}s")

            return {
                'success': True,
                'job_id': job_id,
                'job_title': job.get('title'),
                'job_company': job.get('company'),
                'complexity_score': job.get('complexity_score'),
                'response_code': 200,
                'latency': latency,
                'score': score_data.get('overall_score'),
                'error_type': None,
                'error_message': None
            }

        except asyncio.TimeoutError:
            latency = time.time() - start_time
            print(f"   ⏱️  TIMEOUT - {latency:.2f}s")
            return self.error_result(job_id, 'timeout', 0, f'Timeout after {timeout_val}s', start_time)

        except Exception as e:
            latency = time.time() - start_time
            print(f"   ❌ ERROR - {str(e)[:50]}... - {latency:.2f}s")
            return self.error_result(job_id, 'unknown', 0, str(e), start_time)

    def error_result(self,
                    job_id: any,
                    error_type: str,
                    response_code: int,
                    error_message: str,
                    start_time: float) -> Dict:
        """Create error result dictionary."""
        return {
            'success': False,
            'job_id': job_id,
            'job_title': None,
            'job_company': None,
            'complexity_score': None,
            'response_code': response_code,
            'latency': time.time() - start_time,
            'score': None,
            'error_type': error_type,
            'error_message': error_message
        }

    def get_timeout(self, complexity_score: int) -> int:
        """
        Tiered timeouts based on complexity.

        Args:
            complexity_score: Complexity score (0-100)

        Returns:
            Timeout in seconds
        """
        if complexity_score >= 80:
            return 120  # 2 minutes for very complex
        elif complexity_score >= 60:
            return 90   # 1.5 minutes for complex
        else:
            return 60   # 1 minute for normal

    def log_failure(self, job: Dict, result: Dict):
        """Log failure to JSONL file for debugging."""
        failure_log = Path('../../data/test_results/failures.jsonl')
        failure_log.parent.mkdir(parents=True, exist_ok=True)

        # Classify error
        error_info = ErrorClassifier.classify(
            result['error_type'],
            result['error_message']
        )

        failure_entry = {
            'timestamp': datetime.now().isoformat(),
            'job_id': result['job_id'],
            'job_title': job.get('title'),
            'job_company': job.get('company'),
            'complexity_score': job.get('complexity_score'),
            'error_classification': error_info,
            'raw_error': result
        }

        with open(failure_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(failure_entry) + '\n')

    def generate_report(self):
        """Generate comprehensive test report."""
        total = len(self.results)
        successes = sum(1 for r in self.results if r['success'])
        failures = total - successes
        success_rate = (successes / total * 100) if total > 0 else 0

        # Categorize errors
        error_types = defaultdict(int)
        error_classifications = defaultdict(int)

        for r in self.results:
            if not r['success']:
                error_types[r['error_type']] += 1

                # Classify error
                error_info = ErrorClassifier.classify(r['error_type'], r['error_message'])
                error_classifications[error_info['category']] += 1

        # Calculate latency stats
        latencies = [r['latency'] for r in self.results if r['success']]

        # Console report
        print(f"\n{'='*70}")
        print(f"📊 TEST REPORT")
        print(f"{'='*70}")
        print(f"\n✅ Summary:")
        print(f"   Total Tests: {total}")
        print(f"   Successes: {successes} ({success_rate:.1f}%)")
        print(f"   Failures: {failures} ({100-success_rate:.1f}%)")

        if latencies:
            print(f"\n⏱️  Latency Stats (successful tests):")
            print(f"   Average: {sum(latencies)/len(latencies):.2f}s")
            print(f"   Min: {min(latencies):.2f}s")
            print(f"   Max: {max(latencies):.2f}s")

        if error_types:
            print(f"\n❌ Error Breakdown:")
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                print(f"   {error_type}: {count} ({count/failures*100:.1f}% of failures)")

        if error_classifications:
            print(f"\n🔍 Error Classifications:")
            for category, count in sorted(error_classifications.items(), key=lambda x: x[1], reverse=True):
                print(f"   {category}: {count}")

        # Save detailed JSON report
        report_file = Path(f'../../data/test_results/run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        report_file.parent.mkdir(parents=True, exist_ok=True)

        report = {
            'summary': {
                'total_tests': total,
                'successes': successes,
                'failures': failures,
                'success_rate': f"{success_rate:.1f}%",
                'timestamp': datetime.now().isoformat()
            },
            'error_breakdown': dict(error_types),
            'error_classifications': dict(error_classifications),
            'latency_stats': {
                'average': sum(latencies) / len(latencies) if latencies else 0,
                'min': min(latencies) if latencies else 0,
                'max': max(latencies) if latencies else 0,
                'count': len(latencies)
            },
            'failed_jobs': [r for r in self.results if not r['success']],
            'all_results': self.results
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Detailed report saved to: {report_file}")
        print(f"{'='*70}\n")

        return report


async def main():
    """Main entry point for running tests."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python endpoint_reliability_test.py <jobs_jsonl_file> [cv_json_file]")
        print("\nExample:")
        print("  python endpoint_reliability_test.py ../../data/test_dataset/job_descriptions.jsonl")
        sys.exit(1)

    jobs_file = sys.argv[1]
    cv_file = sys.argv[2] if len(sys.argv) > 2 else '../../data/test_dataset/test_cv.json'

    tester = EndpointReliabilityTester(jobs_file, cv_file)
    await tester.run_all_tests()


if __name__ == '__main__':
    asyncio.run(main())
