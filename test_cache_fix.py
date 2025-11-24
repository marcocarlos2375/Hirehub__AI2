"""
Test script to verify cache fix - uses a brand new resume to bypass cache
"""
import requests
import json

# Brand new resume for testing cache fix
SAMPLE_RESUME = """
SARAH MARTINEZ
Data Engineer

Email: sarah.m@email.com | Phone: (555) 987-6543 | Location: Austin, TX

PROFESSIONAL SUMMARY
Data Engineer with 4 years of experience building data pipelines and ETL systems.
Skilled in Python, SQL, and cloud data platforms.

TECHNICAL SKILLS
Programming: Python, SQL, Scala
Data: Apache Spark, Airflow, Kafka, dbt
Databases: PostgreSQL, MongoDB, Snowflake, Redshift
Cloud: AWS (S3, Glue, EMR), GCP (BigQuery, Dataflow)

WORK EXPERIENCE

Data Engineer | Analytics Corp
Austin, TX | Mar 2021 - Present
- Built data pipelines processing 100M+ records daily
- Implemented real-time streaming with Kafka and Spark
- Optimized Snowflake queries reducing costs by 40%

Junior Data Engineer | StartupXYZ
Austin, TX | Jun 2020 - Feb 2021
- Developed ETL pipelines using Python and Airflow
- Migrated legacy databases to cloud data warehouse

EDUCATION
Bachelor of Science in Computer Science
University of Texas at Austin | Graduated: May 2020
"""

def test_cache_fix():
    """Test that domain finder returns new format with all required fields"""

    print("Testing Domain Finder Cache Fix...")
    print("=" * 80)

    url = "http://localhost:8001/api/find-domains"

    payload = {
        "resume_text": SAMPLE_RESUME,
        "language": "english"
    }

    print(f"\n📤 Sending request to {url}")
    print(f"Resume: Sarah Martinez - Data Engineer")

    try:
        response = requests.post(url, json=payload, timeout=60)

        print(f"\n📥 Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"\n✅ Success: {data.get('success')}")
            print(f"⏱️  Time: {data.get('time_seconds')}s")
            print(f"📊 Total domains: {data.get('total_suggested')}")

            if data.get('domains') and len(data['domains']) > 0:
                first_domain = data['domains'][0]

                print(f"\n{'='*80}")
                print("CHECKING FIRST DOMAIN FOR NEW FIELDS:")
                print(f"{'='*80}\n")

                # Check all required fields
                required_fields = [
                    'domain_name',
                    'technical_role',
                    'industry',
                    'fit_score',
                    'rank',
                    'matching_skills',
                    'skills_to_learn',
                    'role_skills_to_learn',
                    'industry_skills_to_learn',
                    'learning_priority',
                    'time_to_ready',
                    'reasoning',
                    'industry_rationale'
                ]

                missing_fields = []
                present_fields = []

                for field in required_fields:
                    if field in first_domain:
                        present_fields.append(field)
                        value = first_domain[field]
                        if isinstance(value, list):
                            print(f"✅ {field}: [{len(value)} items]")
                        else:
                            print(f"✅ {field}: {value}")
                    else:
                        missing_fields.append(field)
                        print(f"❌ {field}: MISSING")

                print(f"\n{'='*80}")
                if missing_fields:
                    print(f"❌ TEST FAILED: Missing {len(missing_fields)} fields: {', '.join(missing_fields)}")
                else:
                    print(f"✅ TEST PASSED: All {len(required_fields)} required fields present!")
                    print(f"\nFirst domain: {first_domain['domain_name']}")
                    print(f"  Role: {first_domain['technical_role']}")
                    print(f"  Industry: {first_domain['industry']}")
                    print(f"  Fit: {first_domain['fit_score']}%")
                print(f"{'='*80}")
            else:
                print("❌ No domains returned")
        else:
            print(f"\n❌ Request failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text[:500]}")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_cache_fix()
