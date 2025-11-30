"""
API-based Job Scrapers

Collects job descriptions from free public APIs:
- Adzuna API (free tier: 250 requests/month)
- JSearch API via RapidAPI (free tier: 150 requests/month)
- Reed API (free tier: 100 requests/month)

All APIs require free registration to get API keys.
"""

import os
import requests
import time
from typing import List, Dict, Optional
from data_cleaner import clean_job_description


class AdzunaAPI:
    """
    Adzuna Job Search API
    https://developer.adzuna.com

    Free tier: 250 requests/month
    Coverage: US, UK, AU, CA, and more
    """

    BASE_URLS = {
        'us': 'https://api.adzuna.com/v1/api/jobs/us/search/1',
        'uk': 'https://api.adzuna.com/v1/api/jobs/gb/search/1',
        'ca': 'https://api.adzuna.com/v1/api/jobs/ca/search/1',
    }

    def __init__(self, app_id: Optional[str] = None, app_key: Optional[str] = None):
        """
        Initialize Adzuna API client.

        Args:
            app_id: Adzuna App ID (from environment if not provided)
            app_key: Adzuna App Key (from environment if not provided)
        """
        self.app_id = app_id or os.getenv('ADZUNA_APP_ID')
        self.app_key = app_key or os.getenv('ADZUNA_APP_KEY')

        if not self.app_id or not self.app_key:
            raise ValueError("Adzuna API credentials not found. Set ADZUNA_APP_ID and ADZUNA_APP_KEY environment variables.")

    def search_jobs(self,
                   query: str = 'python developer',
                   country: str = 'us',
                   results: int = 10) -> List[Dict]:
        """
        Search for jobs using Adzuna API.

        Args:
            query: Search query (e.g., 'python developer')
            country: Country code ('us', 'uk', 'ca')
            results: Number of results to return (max 50 per request)

        Returns:
            List of job dictionaries
        """
        base_url = self.BASE_URLS.get(country, self.BASE_URLS['us'])

        params = {
            'app_id': self.app_id,
            'app_key': self.app_key,
            'what': query,
            'results_per_page': min(results, 50),
            'content-type': 'application/json'
        }

        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            jobs = []

            for job in data.get('results', []):
                cleaned_desc = clean_job_description(job.get('description', ''))

                if cleaned_desc:
                    jobs.append({
                        'id': job.get('id'),
                        'title': job.get('title'),
                        'company': job.get('company', {}).get('display_name'),
                        'location': job.get('location', {}).get('display_name'),
                        'description': cleaned_desc,
                        'url': job.get('redirect_url'),
                        'source': 'adzuna',
                        'country': country
                    })

            return jobs

        except requests.exceptions.RequestException as e:
            print(f"❌ Adzuna API error: {e}")
            return []


class JSearchAPI:
    """
    JSearch API via RapidAPI
    https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch

    Free tier: 150 requests/month
    Coverage: Global (LinkedIn, Indeed aggregator)
    """

    BASE_URL = 'https://jsearch.p.rapidapi.com/search'

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize JSearch API client.

        Args:
            api_key: RapidAPI key (from environment if not provided)
        """
        self.api_key = api_key or os.getenv('RAPIDAPI_KEY')

        if not self.api_key:
            raise ValueError("RapidAPI key not found. Set RAPIDAPI_KEY environment variable.")

        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
        }

    def search_jobs(self,
                   query: str = 'Python Developer',
                   num_pages: int = 1) -> List[Dict]:
        """
        Search for jobs using JSearch API.

        Args:
            query: Search query
            num_pages: Number of pages (10 jobs per page)

        Returns:
            List of job dictionaries
        """
        all_jobs = []

        for page in range(1, num_pages + 1):
            params = {
                'query': query,
                'page': str(page),
                'num_pages': '1'
            }

            try:
                response = requests.get(
                    self.BASE_URL,
                    headers=self.headers,
                    params=params,
                    timeout=10
                )
                response.raise_for_status()

                data = response.json()

                for job in data.get('data', []):
                    cleaned_desc = clean_job_description(job.get('job_description', ''))

                    if cleaned_desc:
                        all_jobs.append({
                            'id': job.get('job_id'),
                            'title': job.get('job_title'),
                            'company': job.get('employer_name'),
                            'location': f"{job.get('job_city', '')}, {job.get('job_country', '')}".strip(', '),
                            'description': cleaned_desc,
                            'url': job.get('job_apply_link'),
                            'source': 'jsearch',
                            'remote': job.get('job_is_remote', False)
                        })

                # Rate limiting: Wait 1 second between pages
                if page < num_pages:
                    time.sleep(1)

            except requests.exceptions.RequestException as e:
                print(f"❌ JSearch API error (page {page}): {e}")
                break

        return all_jobs


class ReedAPI:
    """
    Reed Job Search API
    https://www.reed.co.uk/developers

    Free tier: 100 requests/month
    Coverage: UK jobs
    """

    BASE_URL = 'https://www.reed.co.uk/api/1.0/search'

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Reed API client.

        Args:
            api_key: Reed API key (from environment if not provided)
        """
        self.api_key = api_key or os.getenv('REED_API_KEY')

        if not self.api_key:
            raise ValueError("Reed API key not found. Set REED_API_KEY environment variable.")

    def search_jobs(self,
                   keywords: str = 'Python Developer',
                   results: int = 10) -> List[Dict]:
        """
        Search for jobs using Reed API.

        Args:
            keywords: Search keywords
            results: Number of results (max 100 per request)

        Returns:
            List of job dictionaries
        """
        params = {
            'keywords': keywords,
            'resultsToTake': min(results, 100)
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                auth=(self.api_key, ''),  # API key as username, empty password
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            jobs = []

            for job in data.get('results', []):
                # Reed API doesn't include full description in search results
                # Need to make additional request for each job
                job_id = job.get('jobId')
                full_job = self._get_job_details(job_id)

                if full_job:
                    jobs.append(full_job)

                # Rate limiting: Wait 0.5 seconds between detail requests
                time.sleep(0.5)

            return jobs

        except requests.exceptions.RequestException as e:
            print(f"❌ Reed API error: {e}")
            return []

    def _get_job_details(self, job_id: int) -> Optional[Dict]:
        """Get full job details including description."""
        url = f'https://www.reed.co.uk/api/1.0/jobs/{job_id}'

        try:
            response = requests.get(
                url,
                auth=(self.api_key, ''),
                timeout=10
            )
            response.raise_for_status()

            job = response.json()
            cleaned_desc = clean_job_description(job.get('jobDescription', ''))

            if cleaned_desc:
                return {
                    'id': job.get('jobId'),
                    'title': job.get('jobTitle'),
                    'company': job.get('employerName'),
                    'location': job.get('locationName'),
                    'description': cleaned_desc,
                    'url': job.get('jobUrl'),
                    'source': 'reed',
                    'country': 'uk'
                }

            return None

        except requests.exceptions.RequestException:
            return None


def collect_from_all_apis(target_count: int = 70) -> List[Dict]:
    """
    Collect jobs from all available APIs.

    Args:
        target_count: Total number of jobs to collect (default: 70)

    Returns:
        List of collected job dictionaries
    """
    all_jobs = []

    # Try Adzuna (target: 30 jobs)
    try:
        print("📡 Collecting from Adzuna API...")
        adzuna = AdzunaAPI()

        # Search in multiple countries
        for country in ['us', 'uk']:
            jobs = adzuna.search_jobs(query='software developer', country=country, results=15)
            all_jobs.extend(jobs)
            print(f"   ✅ Collected {len(jobs)} jobs from Adzuna {country.upper()}")
            time.sleep(2)  # Rate limiting

    except Exception as e:
        print(f"   ⚠️  Adzuna unavailable: {e}")

    # Try JSearch (target: 30 jobs)
    try:
        print("📡 Collecting from JSearch API...")
        jsearch = JSearchAPI()

        jobs = jsearch.search_jobs(query='Python Developer', num_pages=3)
        all_jobs.extend(jobs)
        print(f"   ✅ Collected {len(jobs)} jobs from JSearch")

    except Exception as e:
        print(f"   ⚠️  JSearch unavailable: {e}")

    # Try Reed (target: 10 jobs)
    try:
        print("📡 Collecting from Reed API...")
        reed = ReedAPI()

        jobs = reed.search_jobs(keywords='Backend Developer', results=10)
        all_jobs.extend(jobs)
        print(f"   ✅ Collected {len(jobs)} jobs from Reed")

    except Exception as e:
        print(f"   ⚠️  Reed unavailable: {e}")

    print(f"\n✅ Total collected from APIs: {len(all_jobs)} jobs")

    return all_jobs
