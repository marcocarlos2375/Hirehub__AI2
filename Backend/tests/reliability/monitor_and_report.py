#!/usr/bin/env python3
"""
Monitor test execution and generate a comprehensive text report.
"""
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

def get_latest_result_file():
    """Find the most recent test result JSON file."""
    results_dir = Path(__file__).parent.parent.parent / 'data' / 'test_results'
    json_files = list(results_dir.glob('run_*.json'))
    if not json_files:
        return None
    return max(json_files, key=lambda p: p.stat().st_mtime)

def count_api_calls():
    """Count total API calls from Docker logs."""
    try:
        result = subprocess.run(
            ['docker', 'logs', 'test-hirehub-adaptive-api'],
            capture_output=True,
            text=True,
            timeout=10
        )
        score_calls = result.stdout.count('POST /api/calculate-score')
        parse_calls = result.stdout.count('POST /api/parse')
        return score_calls, parse_calls
    except Exception as e:
        return 0, 0

def check_test_running():
    """Check if test process is still running."""
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return 'endpoint_reliability_test.py' in result.stdout
    except Exception:
        return False

def generate_report(output_file='/tmp/test_report.txt'):
    """Generate comprehensive test report."""

    with open(output_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("HIREHUBAI SCORING ENDPOINT RELIABILITY TEST REPORT\n")
        f.write("="*80 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Check if test is running
        is_running = check_test_running()
        f.write(f"Test Status: {'🟢 RUNNING' if is_running else '🔴 COMPLETED/STOPPED'}\n\n")

        # Get API call counts
        score_calls, parse_calls = count_api_calls()
        f.write("-"*80 + "\n")
        f.write("API ACTIVITY\n")
        f.write("-"*80 + "\n")
        f.write(f"Total /api/parse calls:          {parse_calls}\n")
        f.write(f"Total /api/calculate-score calls: {score_calls}\n")
        f.write(f"Estimated jobs tested:            {score_calls} out of 33\n")
        f.write(f"Progress:                         {min(100, int(score_calls/33*100))}%\n\n")

        # Check for latest results file
        latest_result = get_latest_result_file()

        if latest_result:
            f.write("-"*80 + "\n")
            f.write("LATEST TEST RESULTS\n")
            f.write("-"*80 + "\n")
            f.write(f"Results file: {latest_result.name}\n")
            f.write(f"File modified: {datetime.fromtimestamp(latest_result.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            try:
                with open(latest_result, 'r') as rf:
                    data = json.load(rf)

                # Summary
                summary = data.get('summary', {})
                f.write("SUMMARY:\n")
                f.write(f"  Total Tests:     {summary.get('total_tests', 0)}\n")
                f.write(f"  Successes:       {summary.get('successes', 0)}\n")
                f.write(f"  Failures:        {summary.get('failures', 0)}\n")
                f.write(f"  Success Rate:    {summary.get('success_rate', '0%')}\n")
                f.write(f"  Timestamp:       {summary.get('timestamp', 'N/A')}\n\n")

                # Latency stats
                latency = data.get('latency_stats', {})
                if latency:
                    f.write("LATENCY STATISTICS:\n")
                    f.write(f"  Average:         {latency.get('average', 0):.2f}s\n")
                    f.write(f"  Min:             {latency.get('min', 0):.2f}s\n")
                    f.write(f"  Max:             {latency.get('max', 0):.2f}s\n")
                    f.write(f"  Total Requests:  {latency.get('count', 0)}\n\n")

                # Error breakdown
                error_breakdown = data.get('error_breakdown', {})
                if error_breakdown:
                    f.write("ERROR BREAKDOWN:\n")
                    for error_type, count in error_breakdown.items():
                        f.write(f"  {error_type}: {count}\n")
                    f.write("\n")

                # Error classifications
                error_class = data.get('error_classifications', {})
                if error_class:
                    f.write("ERROR CLASSIFICATIONS:\n")
                    for category, details in error_class.items():
                        f.write(f"  {category}:\n")
                        f.write(f"    Count:       {details.get('count', 0)}\n")
                        f.write(f"    Severity:    {details.get('severity', 'N/A')}\n")
                        f.write(f"    Cause:       {details.get('likely_cause', 'N/A')}\n")
                        f.write(f"    Fix Location: {details.get('fix_location', 'N/A')}\n\n")

                # Failed jobs
                failed_jobs = data.get('failed_jobs', [])
                if failed_jobs:
                    f.write("-"*80 + "\n")
                    f.write(f"FAILED JOBS ({len(failed_jobs)})\n")
                    f.write("-"*80 + "\n")
                    for i, job in enumerate(failed_jobs, 1):
                        f.write(f"\n{i}. Job ID: {job.get('job_id')}\n")
                        f.write(f"   Title:      {job.get('job_title', 'N/A')}\n")
                        f.write(f"   Company:    {job.get('job_company', 'N/A')}\n")
                        f.write(f"   Complexity: {job.get('complexity_score', 'N/A')}/100\n")
                        f.write(f"   Error Type: {job.get('error_type', 'N/A')}\n")
                        f.write(f"   Error Msg:  {job.get('error_message', 'N/A')[:200]}\n")
                else:
                    f.write("✅ NO FAILED JOBS! All tests passed successfully.\n\n")

                # Top 10 successful jobs
                all_results = data.get('all_results', [])
                successful = [r for r in all_results if r.get('success')]
                if successful:
                    f.write("-"*80 + "\n")
                    f.write(f"SUCCESSFUL JOBS (showing up to 10 of {len(successful)})\n")
                    f.write("-"*80 + "\n")
                    for i, job in enumerate(successful[:10], 1):
                        f.write(f"\n{i}. {job.get('job_title', 'N/A')} at {job.get('job_company', 'N/A')}\n")
                        f.write(f"   Complexity:    {job.get('complexity_score', 'N/A')}/100\n")
                        f.write(f"   Score:         {job.get('score', 'N/A')}%\n")
                        f.write(f"   Latency:       {job.get('latency', 0):.2f}s\n")
                        f.write(f"   Response Code: {job.get('response_code', 'N/A')}\n")

            except Exception as e:
                f.write(f"Error reading results file: {e}\n\n")
        else:
            f.write("-"*80 + "\n")
            f.write("NO RESULTS FILE FOUND YET\n")
            f.write("-"*80 + "\n")
            f.write("Test is still running and hasn't saved results yet.\n")
            f.write("Results will be saved to Backend/data/test_results/ when complete.\n\n")

        # Docker logs (recent errors)
        f.write("-"*80 + "\n")
        f.write("RECENT DOCKER LOGS (ERRORS/WARNINGS)\n")
        f.write("-"*80 + "\n")
        try:
            result = subprocess.run(
                ['docker', 'logs', '--since', '10m', 'test-hirehub-adaptive-api'],
                capture_output=True,
                text=True,
                timeout=10
            )
            errors = [line for line in result.stderr.split('\n') if 'ERROR' in line or 'Exception' in line]
            if errors:
                for error in errors[-20:]:  # Last 20 errors
                    f.write(f"  {error}\n")
            else:
                f.write("  ✅ No errors found in recent logs!\n")
        except Exception as e:
            f.write(f"  Could not fetch Docker logs: {e}\n")

        f.write("\n" + "="*80 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*80 + "\n")

    print(f"✅ Report saved to: {output_file}")
    return output_file

if __name__ == '__main__':
    # Monitor until test completes
    print("🔍 Monitoring test execution...")

    while check_test_running():
        print("⏳ Test still running... checking again in 30 seconds")
        time.sleep(30)

    print("\n🎉 Test completed! Generating final report...\n")
    time.sleep(5)  # Give time for results to be written

    report_file = generate_report()

    # Display the report
    print("\n" + "="*80)
    print("DISPLAYING REPORT:")
    print("="*80 + "\n")
    with open(report_file, 'r') as f:
        print(f.read())
