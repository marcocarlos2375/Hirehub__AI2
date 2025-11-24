"""
Test script for domain finder endpoint with gaming hobby resume
"""
import requests
import json

# Sample resume with gaming hobby for testing role+industry matching
SAMPLE_RESUME_GAMING = """
JOHN DOE
Full-Stack Software Engineer

Email: john.doe@email.com | Phone: (555) 123-4567 | Location: San Francisco, CA
LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe

PROFESSIONAL SUMMARY
Experienced Full-Stack Software Engineer with 5 years of expertise in building scalable web applications
using modern JavaScript frameworks and cloud technologies. Passionate gamer and game developer with
hobby projects in Unity and Unreal Engine.

TECHNICAL SKILLS
Programming Languages: JavaScript, TypeScript, Python, C#
Frontend: React, Vue.js, Next.js, HTML5, CSS3, Tailwind CSS
Backend: Node.js, Express, FastAPI, Django, RESTful APIs, GraphQL
Databases: PostgreSQL, MongoDB, Redis, MySQL
Cloud & DevOps: AWS (EC2, S3, Lambda), Docker, Kubernetes, CI/CD
Game Development: Unity, C#, Game Physics, Multiplayer Networking

WORK EXPERIENCE

Senior Software Engineer | Tech Startup Inc.
San Francisco, CA | Jan 2022 - Present
- Led development of a real-time collaboration platform serving 50K+ daily active users
- Architected microservices architecture reducing API response time by 60%
- Implemented CI/CD pipeline using GitHub Actions

Software Engineer | Digital Solutions Co.
San Francisco, CA | Jun 2020 - Dec 2021
- Developed customer-facing web applications using Vue.js and Django
- Optimized database queries improving page load times by 40%

PERSONAL PROJECTS

Multiplayer Game Server (Hobby Project)
- Built a real-time multiplayer game server using Node.js and WebSockets
- Implemented player matchmaking system supporting 100+ concurrent players
- Used Unity for game client development with C# backend integration

E-Commerce Platform
- Built full-stack e-commerce application with Next.js, Node.js, and PostgreSQL
- Integrated Stripe payment processing

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | Graduated: May 2019
"""

def test_domain_finder():
    """Test the /api/find-domains endpoint"""

    print("Testing Domain Finder Endpoint (Gaming Hobby Resume)...")
    print("=" * 80)

    # API endpoint
    url = "http://localhost:8001/api/find-domains"

    # Request payload
    payload = {
        "resume_text": SAMPLE_RESUME_GAMING,
        "language": "english"
    }

    print(f"\n📤 Sending request to {url}")
    print(f"Resume length: {len(SAMPLE_RESUME_GAMING)} characters")
    print("(Resume includes gaming hobby and Unity projects)")

    try:
        # Make request
        response = requests.post(url, json=payload, timeout=60)

        print(f"\n📥 Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"\n✅ Success: {data.get('success')}")
            print(f"⏱️  Time: {data.get('time_seconds')}s")
            print(f"🤖 Model: {data.get('model')}")
            print(f"📊 Total domains: {data.get('total_suggested')}")

            if data.get('domains'):
                print(f"\n{'='*80}")
                print("ROLE + INDUSTRY COMBINATIONS:")
                print(f"{'='*80}\n")

                for domain in data['domains']:
                    print(f"#{domain['rank']}. {domain['domain_name']} - {domain['fit_score']}% fit")
                    print(f"   Technical Role: {domain.get('technical_role', 'N/A')}")
                    print(f"   Industry: {domain.get('industry', 'N/A')}")
                    print(f"   Learning Priority: {domain['learning_priority']}")
                    print(f"   Time to Ready: {domain['time_to_ready']}")
                    print(f"\n   Role Fit: {domain['reasoning']}")
                    print(f"   Industry Match: {domain.get('industry_rationale', 'N/A')}")

                    print(f"\n   Matching Skills ({len(domain['matching_skills'])}): {', '.join(domain['matching_skills'][:5])}")
                    if len(domain['matching_skills']) > 5:
                        print(f"      ... and {len(domain['matching_skills']) - 5} more")

                    if domain.get('role_skills_to_learn'):
                        print(f"   Role Skills to Learn ({len(domain['role_skills_to_learn'])}): {', '.join(domain['role_skills_to_learn'][:4])}")

                    if domain.get('industry_skills_to_learn'):
                        print(f"   Industry Skills to Learn ({len(domain['industry_skills_to_learn'])}): {', '.join(domain['industry_skills_to_learn'][:4])}")

                    print()

                print(f"{'='*80}")
                print(f"\n✅ TEST PASSED: Generated {len(data['domains'])} role+industry combinations")

                # Check if gaming domain was suggested
                gaming_domains = [d for d in data['domains'] if 'Gaming' in d.get('industry', '')]
                if gaming_domains:
                    print(f"✅ Found {len(gaming_domains)} gaming industry suggestions (based on hobby project)")
                else:
                    print("⚠️  No gaming industry suggestions found")
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
                print(f"Error text: {response.text[:500]}")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_domain_finder()
