"""
Test to verify that Sophia Martinez's HealthTrack App project
is properly recognized as healthcare domain expertise
"""
import requests
import json

# Sophia's resume with HealthTrack App project
SOPHIA_RESUME = """SOPHIA MARTINEZ
UX/UI Designer

Email: sophia.martinez@email.com | Phone: (555) 345-6789 | Location: Austin, TX
LinkedIn: linkedin.com/in/sophiamartinez | Portfolio: sophiamartinez.design
Behance: behance.net/sophiamartinez

PROFESSIONAL SUMMARY
Creative UX/UI Designer with 2 years of experience designing user-centered digital products. Passionate about creating intuitive interfaces that solve real user problems. Strong background in user research, wireframing, prototyping, and design systems. Eager to explore product management and design engineering roles.

DESIGN SKILLS
Design Tools: Figma, Adobe XD, Sketch, Adobe Photoshop, Adobe Illustrator
Prototyping: Figma, Framer, InVision, Principle
Research: User Interviews, Usability Testing, A/B Testing, Surveys, Personas, Journey Mapping
Front-end: HTML5, CSS3, JavaScript basics, Tailwind CSS, Framer Motion
Collaboration: Jira, Confluence, Miro, FigJam, Notion

WORK EXPERIENCE

UX/UI Designer | Digital Agency Co.
Austin, TX | Mar 2023 - Present
- Design user interfaces for 10+ client projects including mobile apps and web applications
- Conduct user research through interviews, surveys, and usability testing with 50+ participants
- Create wireframes, high-fidelity mockups, and interactive prototypes using Figma
- Collaborate with developers to ensure design implementation matches specifications
- Established design system with 30+ reusable components reducing design time by 40%
- Present design concepts to stakeholders and iterate based on feedback

Junior UX Designer | StartupXYZ
Austin, TX | Jun 2022 - Feb 2023
- Redesigned onboarding flow increasing user activation rate by 35%
- Created responsive designs for web and mobile platforms (iOS and Android)
- Conducted competitive analysis and user testing sessions
- Worked closely with product managers to define features and requirements
- Maintained design documentation and style guides

EDUCATION
Bachelor of Fine Arts in Graphic Design
University of Texas at Austin | Graduated: May 2022
Minor: Human-Computer Interaction
GPA: 3.6/4.0

PROJECTS & CASE STUDIES

HealthTrack App - Redesign (Personal Project)
- Redesigned health tracking mobile app improving user retention by 25%
- Conducted user research with 20 participants to identify pain points
- Created user personas, user flows, wireframes, and high-fidelity prototypes
- Implemented accessibility best practices (WCAG 2.1 AA compliance)

E-Commerce Checkout Optimization
- Redesigned checkout process reducing cart abandonment by 30%
- Performed A/B testing comparing 3 different design variations
- Collaborated with front-end developers to implement final design
- Measured success with analytics and user feedback

TECHNICAL SKILLS
- Basic HTML/CSS: Can implement simple designs and collaborate effectively with developers
- Framer: Built interactive prototypes and simple websites with no-code tools
- Responsive Design: Mobile-first approach, understanding of breakpoints and adaptive layouts
- Design Tokens: Experience with design-to-development handoff using tokens and variables

CERTIFICATIONS & COURSES
- Google UX Design Professional Certificate (Coursera, 2022)
- Interaction Design Foundation - User Research Methods (2023)
- Frontend Fundamentals: HTML & CSS (Codecademy, 2024)

ACHIEVEMENTS
- Dribbble Featured Designer (Top 10% in Austin, 2024)
- Won "Best User Experience" Award at University Design Competition (2022)
- Published 2 design articles on Medium with 5K+ combined reads"""

# Healthcare UX Designer job description
JOB_DESCRIPTION = """UX Designer - Healthcare Technology

We are seeking a talented UX Designer to join our HealthTech team building patient-centered digital health solutions.

REQUIREMENTS:
- 3+ years of UX design experience
- Experience with healthcare technology, MedTech, or digital health platforms
- Strong understanding of accessibility standards (WCAG compliance)
- Experience conducting user research with patients and healthcare providers
- Proficiency in Figma, Adobe XD, or Sketch
- Knowledge of healthcare compliance (HIPAA preferred)
- Portfolio demonstrating user-centered design process

RESPONSIBILITIES:
- Design intuitive interfaces for patient-facing mobile and web applications
- Conduct user research with diverse patient populations
- Ensure designs meet healthcare accessibility standards
- Collaborate with clinical stakeholders and engineering teams
- Create design systems for healthcare products
- Iterate designs based on user testing and feedback

NICE TO HAVE:
- Experience with digital patient-reported outcomes (PROs)
- Knowledge of clinical workflows
- Healthcare industry certifications
"""

def test_gap_analysis():
    print("=" * 80)
    print("Testing Gap Analysis: Sophia Martinez's HealthTrack Project Recognition")
    print("=" * 80)

    # Parse CV
    print("\n1. Parsing Sophia's resume...")
    parse_response = requests.post(
        "http://localhost:8001/api/parse-cv",
        json={
            "resume_text": SOPHIA_RESUME,
            "language": "english"
        }
    )

    if parse_response.status_code != 200:
        print(f"❌ CV parsing failed: {parse_response.status_code}")
        print(parse_response.text)
        return

    cv_response = parse_response.json()
    cv_data = cv_response.get('data', {})
    print(f"✅ CV parsed successfully")
    print(f"   Projects found: {len(cv_data.get('projects', []))}")

    # Check if HealthTrack project was extracted
    projects = cv_data.get('projects', [])
    healthtrack_found = False
    for proj in projects:
        if isinstance(proj, dict) and 'name' in proj:
            if 'HealthTrack' in proj['name']:
                healthtrack_found = True
                print(f"   ✅ HealthTrack project found: {proj['name']}")
                print(f"      Description: {proj.get('description', '')[:100]}...")
                break

    if not healthtrack_found:
        print("   ⚠️  HealthTrack project not found in parsed CV")

    # Parse Job Description
    print("\n2. Parsing healthcare job description...")
    jd_response = requests.post(
        "http://localhost:8001/api/parse",
        json={
            "job_description": JOB_DESCRIPTION,
            "language": "english"
        }
    )

    if jd_response.status_code != 200:
        print(f"❌ JD parsing failed: {jd_response.status_code}")
        return

    jd_response_data = jd_response.json()
    jd_data = jd_response_data.get('data', {})
    print("✅ JD parsed successfully")

    # Calculate Score with Gap Analysis
    print("\n3. Calculating match score with gap analysis...")
    score_response = requests.post(
        "http://localhost:8001/api/calculate-score?bypass_cache=true",
        json={
            "parsed_cv": cv_data,
            "parsed_jd": jd_data
        }
    )

    if score_response.status_code != 200:
        print(f"❌ Score calculation failed: {score_response.status_code}")
        print(score_response.text)
        return

    score_data = score_response.json()
    print("✅ Score calculated successfully")
    print(f"\n   Overall Match Score: {score_data.get('overall_score', 0)}%")

    # Check gap analysis for healthcare domain expertise
    print("\n4. Analyzing Domain Expertise Gap...")
    gap_analysis = score_data.get('gaps', {})

    # DEBUG: Print full gaps structure
    print(f"\n   DEBUG: Full gaps structure:")
    import json as json_lib
    print(json_lib.dumps(gap_analysis, indent=2)[:1000])

    critical_gaps = gap_analysis.get('critical', [])
    important_gaps = gap_analysis.get('important', [])
    minor_gaps = gap_analysis.get('minor', [])

    print(f"\n   Critical Gaps: {len(critical_gaps)}")
    print(f"   Important Gaps: {len(important_gaps)}")
    print(f"   Minor Gaps: {len(minor_gaps)}")

    # Find healthcare/domain expertise gap
    healthcare_gap = None
    for gap in critical_gaps + important_gaps + minor_gaps:
        if 'domain' in gap.get('gap_name', '').lower() or 'healthcare' in gap.get('gap_name', '').lower():
            healthcare_gap = gap
            break

    if healthcare_gap:
        print(f"\n   📊 Healthcare Domain Gap Found:")
        print(f"      Name: {healthcare_gap.get('gap_name')}")
        print(f"      Gap Percentage: {healthcare_gap.get('gap_percentage')}%")
        print(f"      Severity: {healthcare_gap.get('severity')}")
        print(f"      Current: {healthcare_gap.get('current_state')}")
        print(f"      Required: {healthcare_gap.get('required_state')}")
        print(f"      Reasoning: {healthcare_gap.get('reasoning')}")
        print(f"      Time to Close: {healthcare_gap.get('time_to_close')}")

        # Check if gap was reduced thanks to HealthTrack project
        if healthcare_gap.get('gap_percentage', 100) <= 5:
            print(f"\n   ✅ SUCCESS: Healthcare domain gap is minimal ({healthcare_gap.get('gap_percentage')}%)")
            print(f"      This suggests the HealthTrack project was recognized!")
        elif healthcare_gap.get('gap_percentage', 100) <= 15:
            print(f"\n   ⚠️  PARTIAL: Healthcare domain gap is moderate ({healthcare_gap.get('gap_percentage')}%)")
            print(f"      HealthTrack project may have been partially recognized")
        else:
            print(f"\n   ❌ FAILURE: Healthcare domain gap is still high ({healthcare_gap.get('gap_percentage')}%)")
            print(f"      HealthTrack project may not have been recognized")
    else:
        print("\n   ℹ️  No specific healthcare domain gap found")
        print("      This could mean either:")
        print("      1. ✅ The healthcare domain was fully matched (no gap)")
        print("      2. ❌ The gap detection didn't identify healthcare as important")

    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)

if __name__ == "__main__":
    test_gap_analysis()
