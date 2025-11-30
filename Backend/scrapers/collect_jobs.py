"""
Job Collection Script

Collects jobs from JSearch API, filters by complexity, and creates test dataset.
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from api_scrapers import JSearchAPI
from complexity_scorer import calculate_complexity_score, get_complexity_details, filter_by_complexity
from data_cleaner import clean_job_description

load_dotenv()


def collect_jobs_from_jsearch(num_jobs: int = 100) -> list:
    """
    Collect jobs from JSearch API.

    Args:
        num_jobs: Target number of jobs to collect

    Returns:
        List of job dictionaries
    """
    print(f"\n{'='*70}")
    print(f"📡 Collecting {num_jobs} jobs from JSearch API...")
    print(f"{'='*70}\n")

    jsearch = JSearchAPI()
    all_jobs = []

    # JSearch returns ~10 jobs per page
    num_pages = (num_jobs // 10) + 1

    # Search for different types of developer jobs to get diversity
    search_queries = [
        'Python Developer',
        'Backend Developer',
        'Full Stack Developer',
        'Frontend Developer React',
        'DevOps Engineer',
        'Data Engineer',
        'Machine Learning Engineer',
        'Software Engineer',
    ]

    pages_per_query = max(1, num_pages // len(search_queries))

    for query in search_queries:
        print(f"\n🔍 Searching: '{query}' ({pages_per_query} pages)...")

        try:
            jobs = jsearch.search_jobs(query=query, num_pages=pages_per_query)
            all_jobs.extend(jobs)
            print(f"   ✅ Collected {len(jobs)} jobs")

            # Brief pause between queries
            time.sleep(2)

        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            continue

    print(f"\n✅ Total collected: {len(all_jobs)} jobs")
    return all_jobs


def save_jobs_to_jsonl(jobs: list, filename: str):
    """Save jobs to JSONL file."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        for job in jobs:
            f.write(json.dumps(job) + '\n')

    print(f"💾 Saved {len(jobs)} jobs to {filename}")


def main():
    """Main collection pipeline."""

    # Step 1: Collect raw jobs
    print("\n" + "="*70)
    print("STEP 1: COLLECTING RAW JOBS")
    print("="*70)

    raw_jobs = collect_jobs_from_jsearch(num_jobs=100)

    if not raw_jobs:
        print("❌ No jobs collected. Exiting.")
        return

    save_jobs_to_jsonl(raw_jobs, '../data/raw_jobs/jsearch_jobs.jsonl')

    # Step 2: Score complexity and filter
    print("\n" + "="*70)
    print("STEP 2: SCORING COMPLEXITY")
    print("="*70 + "\n")

    for job in raw_jobs:
        if 'description' in job:
            job['complexity_score'] = calculate_complexity_score(job['description'])

    # Sort by complexity
    raw_jobs.sort(key=lambda x: x.get('complexity_score', 0), reverse=True)

    # Show top 10
    print("Top 10 most complex jobs:")
    for i, job in enumerate(raw_jobs[:10], 1):
        score = job.get('complexity_score', 0)
        title = job.get('title', 'Unknown')
        company = job.get('company', 'Unknown')
        print(f"  {i}. {title} at {company} - Score: {score}/100")

    # Filter for complexity ≥60
    complex_jobs = filter_by_complexity(raw_jobs, min_score=60)
    print(f"\n✅ Filtered to {len(complex_jobs)} complex jobs (score ≥60)")

    save_jobs_to_jsonl(complex_jobs, '../data/filtered_jobs/complex_jobs.jsonl')

    # Step 3: Select diverse subset for testing
    print("\n" + "="*70)
    print("STEP 3: CREATING TEST DATASET")
    print("="*70 + "\n")

    # Take top 50-100 most complex jobs
    test_jobs = complex_jobs[:min(100, len(complex_jobs))]

    print(f"Selected {len(test_jobs)} jobs for test dataset")
    print(f"Complexity range: {test_jobs[-1]['complexity_score']}-{test_jobs[0]['complexity_score']}")

    save_jobs_to_jsonl(test_jobs, '../data/test_dataset/job_descriptions.jsonl')

    # Step 4: Show statistics
    print("\n" + "="*70)
    print("STATISTICS")
    print("="*70 + "\n")

    # Complexity distribution
    complexity_ranges = {
        '90-100': 0,
        '80-89': 0,
        '70-79': 0,
        '60-69': 0,
        '<60': 0
    }

    for job in raw_jobs:
        score = job.get('complexity_score', 0)
        if score >= 90:
            complexity_ranges['90-100'] += 1
        elif score >= 80:
            complexity_ranges['80-89'] += 1
        elif score >= 70:
            complexity_ranges['70-79'] += 1
        elif score >= 60:
            complexity_ranges['60-69'] += 1
        else:
            complexity_ranges['<60'] += 1

    print("Complexity Distribution:")
    for range_name, count in complexity_ranges.items():
        pct = (count / len(raw_jobs) * 100) if raw_jobs else 0
        print(f"  {range_name}: {count} ({pct:.1f}%)")

    print(f"\n✅ COMPLETE! Test dataset ready at:")
    print(f"   Backend/data/test_dataset/job_descriptions.jsonl")
    print(f"\n🧪 Run tests with:")
    print(f"   cd Backend/tests/reliability")
    print(f"   python3 endpoint_reliability_test.py \\")
    print(f"     ../../data/test_dataset/job_descriptions.jsonl \\")
    print(f"     ../../data/test_dataset/test_cv.json")


if __name__ == '__main__':
    main()
