"""
Test script for domain finder endpoint
"""
import requests
import json

# Sample resume for testing (modified to bypass cache)
SAMPLE_RESUME = """
JOHN DOE.
Software Engineer

Email: john.doe@email.com | Phone: (555) 123-4567 | Location: San Francisco, CA
LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe

PROFESSIONAL SUMMARY
Experienced Full-Stack Software Engineer with 5 years of expertise in building scalable web applications
using modern JavaScript frameworks and cloud technologies. Proven track record of delivering high-quality
code and collaborating with cross-functional teams to solve complex technical challenges.

TECHNICAL SKILLS
Programming Languages: JavaScript, TypeScript, Python, Java
Frontend: React, Vue.js, Next.js, HTML5, CSS3, Tailwind CSS
Backend: Node.js, Express, FastAPI, Django, RESTful APIs, GraphQL
Databases: PostgreSQL, MongoDB, Redis, MySQL
Cloud & DevOps: AWS (EC2, S3, Lambda), Docker, Kubernetes, CI/CD (GitHub Actions, Jenkins)
Tools & Technologies: Git, Webpack, Babel, Jest, Cypress, Postman

WORK EXPERIENCE

Senior Software Engineer | Tech Startup Inc.
San Francisco, CA | Jan 2022 - Present
- Led development of a real-time collaboration platform serving 50K+ daily active users using React, Node.js, and WebSockets
- Architected and implemented microservices architecture reducing API response time by 60%
- Mentored team of 3 junior developers and conducted code reviews to maintain code quality
- Implemented CI/CD pipeline using GitHub Actions, reducing deployment time from 2 hours to 15 minutes

Software Engineer | Digital Solutions Co.
San Francisco, CA | Jun 2020 - Dec 2021
- Developed and maintained customer-facing web applications using Vue.js and Django
- Optimized database queries improving page load times by 40%
- Collaborated with product team to implement new features based on user feedback
- Wrote comprehensive unit and integration tests achieving 85% code coverage

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | Graduated: May 2019
GPA: 3.7/4.0
"""

def test_domain_finder():
    """Test the /api/find-domains endpoint"""

    print("Testing Domain Finder Endpoint...")
    print("=" * 80)

    # API endpoint
    url = "http://localhost:8001/api/find-domains"

    # Request payload
    payload = {
        "resume_text": SAMPLE_RESUME,
        "language": "english"
    }

    print(f"\n📤 Sending request to {url}")
    print(f"Resume length: {len(SAMPLE_RESUME)} characters")

    try:
        # Make request
        response = requests.post(url, json=payload, timeout=30)

        print(f"\n📥 Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"\n✅ Success: {data.get('success')}")
            print(f"⏱️  Time: {data.get('time_seconds')}s")
            print(f"🤖 Model: {data.get('model')}")
            print(f"🌐 Language: {data.get('language')}")
            print(f"📊 Total domains: {data.get('total_suggested')}")

            if data.get('domains'):
                print(f"\n{'='*80}")
                print("SUGGESTED DOMAINS:")
                print(f"{'='*80}\n")

                for domain in data['domains']:
                    print(f"#{domain['rank']}. {domain['domain_name']} - {domain['fit_score']}% fit")
                    print(f"   Learning Priority: {domain['learning_priority']}")
                    print(f"   Time to Ready: {domain['time_to_ready']}")
                    print(f"   Reasoning: {domain['reasoning']}")
                    print(f"   Matching Skills ({len(domain['matching_skills'])}): {', '.join(domain['matching_skills'][:5])}")
                    if len(domain['matching_skills']) > 5:
                        print(f"      ... and {len(domain['matching_skills']) - 5} more")
                    print(f"   Skills to Learn ({len(domain['skills_to_learn'])}): {', '.join(domain['skills_to_learn'][:5])}")
                    if len(domain['skills_to_learn']) > 5:
                        print(f"      ... and {len(domain['skills_to_learn']) - 5} more")
                    print()

                print(f"{'='*80}")
                print(f"\n✅ TEST PASSED: Successfully generated {len(data['domains'])} domain suggestions")
            else:
                print("\n❌ No domains returned")
                if data.get('error'):
                    print(f"Error: {data['error']}")
        else:
            print(f"\n❌ Request failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_domain_finder()
