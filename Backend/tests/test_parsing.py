"""
Test script for parsing resumes and job descriptions.
Results are saved to data/results/
"""

import os
import json
import httpx
from pathlib import Path
from datetime import datetime

# Resume order control via environment variable
# RESUME_ORDER=medicine|computer_science|logistics
RESUME_ORDER = os.environ.get("RESUME_ORDER", None)

# API Configuration
API_BASE_URL = "http://localhost:8001"

# Directories
SAMPLES_DIR = Path("data/samples")
RESULTS_DIR = Path("data/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def read_file(filepath: str) -> str:
    """Read text file content."""
    with open(filepath, "r") as f:
        return f.read()

def save_result(filename: str, data: dict):
    """Save result as JSON file."""
    filepath = RESULTS_DIR / filename
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  Saved: {filepath}")

def parse_job_description(job_text: str, language: str = "english") -> dict:
    """Call job description parsing API."""
    response = httpx.post(
        f"{API_BASE_URL}/api/parse",
        json={"job_description": job_text, "language": language},
        timeout=60.0
    )
    response.raise_for_status()
    return response.json()

def parse_resume(resume_text: str, language: str = "english") -> dict:
    """Call resume parsing API."""
    response = httpx.post(
        f"{API_BASE_URL}/api/parse-cv",
        json={"resume_text": resume_text, "language": language},
        timeout=60.0
    )
    response.raise_for_status()
    return response.json()

def test_job_parsing():
    """Test job description parsing for all sample files."""
    print("\n" + "=" * 60)
    print("TESTING JOB DESCRIPTION PARSING")
    print("=" * 60)

    job_files = list((SAMPLES_DIR / "job_descriptions").glob("*.txt"))
    results = {}

    for job_file in job_files:
        print(f"\nParsing: {job_file.name}")
        try:
            job_text = read_file(job_file)
            result = parse_job_description(job_text)
            results[job_file.stem] = {
                "status": "success",
                "file": str(job_file),
                "parsed_at": datetime.now().isoformat(),
                "result": result
            }
            print(f"  Status: SUCCESS")
            data = result.get('data', {})
            print(f"  Job Title: {data.get('title', 'N/A')}")
            print(f"  Company: {data.get('company', 'N/A')}")

            # Save individual result
            save_result(f"job_parsed_{job_file.stem}.json", results[job_file.stem])

        except Exception as e:
            results[job_file.stem] = {
                "status": "error",
                "file": str(job_file),
                "error": str(e)
            }
            print(f"  Status: ERROR - {e}")

    # Save combined results
    save_result("all_job_parsing_results.json", results)
    return results

def get_ordered_resume_files():
    """Get resume files in specified order based on RESUME_ORDER env var."""
    all_files = list((SAMPLES_DIR / "resumes").glob("*.txt"))

    if not RESUME_ORDER:
        return all_files

    # Define order based on which resume should be first
    order_map = {
        "medicine": ["medicine_resume.txt", "computer_science_resume.txt", "logistics_resume.txt"],
        "computer_science": ["computer_science_resume.txt", "logistics_resume.txt", "medicine_resume.txt"],
        "logistics": ["logistics_resume.txt", "medicine_resume.txt", "computer_science_resume.txt"],
    }

    if RESUME_ORDER not in order_map:
        print(f"  Warning: Unknown RESUME_ORDER '{RESUME_ORDER}', using default order")
        return all_files

    ordered = []
    for filename in order_map[RESUME_ORDER]:
        for f in all_files:
            if f.name == filename:
                ordered.append(f)
                break

    print(f"  Resume order: {[f.name for f in ordered]}")
    return ordered

def test_resume_parsing():
    """Test resume parsing for all sample files."""
    print("\n" + "=" * 60)
    print("TESTING RESUME PARSING")
    print("=" * 60)

    resume_files = get_ordered_resume_files()
    results = {}

    for resume_file in resume_files:
        print(f"\nParsing: {resume_file.name}")
        try:
            resume_text = read_file(resume_file)
            result = parse_resume(resume_text)
            results[resume_file.stem] = {
                "status": "success",
                "file": str(resume_file),
                "parsed_at": datetime.now().isoformat(),
                "result": result
            }
            print(f"  Status: SUCCESS")

            data = result.get('data', {})
            print(f"  Name: {data.get('full_name', 'N/A')}")
            print(f"  Title: {data.get('professional_title', 'N/A')}")
            print(f"  Experience: {len(data.get('work_experience', []))} positions")

            # Save individual result
            save_result(f"resume_parsed_{resume_file.stem}.json", results[resume_file.stem])

        except Exception as e:
            results[resume_file.stem] = {
                "status": "error",
                "file": str(resume_file),
                "error": str(e)
            }
            print(f"  Status: ERROR - {e}")

    # Save combined results
    save_result("all_resume_parsing_results.json", results)
    return results

def main():
    """Run all parsing tests."""
    print("\n" + "=" * 60)
    print("PARSING TEST SUITE")
    print(f"Started at: {datetime.now().isoformat()}")
    print(f"API URL: {API_BASE_URL}")
    print("=" * 60)

    # Check if API is running
    try:
        response = httpx.get(f"{API_BASE_URL}/health", timeout=5.0)
        print(f"\nAPI Status: {response.json().get('status', 'unknown')}")
    except Exception as e:
        print(f"\nERROR: Cannot connect to API at {API_BASE_URL}")
        print(f"Make sure the API is running: uvicorn app.main:app --port 8001")
        return

    # Run tests
    job_results = test_job_parsing()
    resume_results = test_resume_parsing()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    job_success = sum(1 for r in job_results.values() if r["status"] == "success")
    resume_success = sum(1 for r in resume_results.values() if r["status"] == "success")

    print(f"\nJob Descriptions: {job_success}/{len(job_results)} parsed successfully")
    print(f"Resumes: {resume_success}/{len(resume_results)} parsed successfully")
    print(f"\nResults saved to: {RESULTS_DIR.absolute()}")
    print("=" * 60)

if __name__ == "__main__":
    main()
