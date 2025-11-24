"""
Shared configuration for TOON and JSON benchmark tests.
This file centralizes the job description and prompt templates to avoid duplication.
"""

# TOON format schema example (compressed with concrete values)
TOON_EXAMPLE = """company_name: Acme Corp
position_title: Senior Engineer
location: NYC
work_mode: hybrid
salary_range: string or null
experience_years_required: number
experience_level: junior/mid/senior or null

hard_skills_required[12]{{skill,priority}}:
  Python,critical
  React,important
  AWS,nice

soft_skills_required[6]:
  - Full sentence explaining the soft skill and why it matters

responsibilities[12]:
  - Specific actionable sentence with technical details about what you'll do

tech_stack[10]:
  - Technology name

domain_expertise:
  industry[3]:
    - Industry name
  specific_knowledge[5]:
    - Specific domain knowledge

implicit_requirements[8]:
  - Inferred requirement from context

company_culture_signals[8]:
  - Culture or benefit signal

ats_keywords[15]:
  - Keyword"""


# Job description to test with
job_description = """
Software Engineer | Blockchain- job post
Omen.
2.0
2.0 out of 5 stars
New York, NY 10036
$100,000 - $200,000 a year - Full-time
Omen.
New York, NY 10036
$100,000 - $200,000 a year
Profile insights
Here’s how the job qualifications align with your profile.
Skills

Solidity
 (Required)

Software engineering
 (Required)

Scalable systems
 (Required)
+ show more

Do you have experience in Solidity?
&nbsp;
Job details
Here’s how the job details align with your profile.
Pay

$100,000 - $200,000 a year
Job type

Full-time
&nbsp;
Benefits
Pulled from the full job description
Relocation assistance
&nbsp;
Full job description
We are backed by a tier 1 VC building the rails to put real world assetson-chain. By bridging real-world assets (RWAs) with decentralized infrastructure, we’re creating the foundation for trading, lending, and building on top of tokenized alternative assets at light speed.

If you’ve ever wanted to work at the intersection of high-performance backend systems, crypto infrastructure, and financial engineering, this is the place. We’re building the future of global markets.

What You’ll Do

Design and build smart contracts for token issuance, trading, custody, and compliance for on-chain real estate and other RWA markets.
Develop tokenization frameworks for fractional ownership, synthetic exposures, derivatives, and perpetual products.
Implement and extend token standards (ERC-20, ERC-721, ERC-1155, ERC-4626, and custom RWA standards) for production systems.
Integrate with L2s, bridges, and oracles (e.g., Chainlink, LayerZero, Hyperlane) to enable secure cross-chain RWA flows.
Work with custody & wallet primitives including MPC wallets, account abstraction (ERC-4337), and institutional custody providers.
Own security for on-chain components: write robust tests, collaborate on audits, and design against common attack vectors (reentrancy, flash loans, oracle manipulation, bridge exploits).
Collaborate with cross-functional teams: backend engineers, security researchers, compliance, and product to bring complex RWA structures on-chain end-to-end.
Requirements

Strong experience writing Solidity smart contracts for production systems.
Deep understanding of Ethereum and at least one major L2 (Arbitrum, Optimism, Base, zkSync, etc.).
Hands-on experience with smart contract tooling: Foundry and/or Hardhat, OpenZeppelin libraries, test frameworks.
Solid grasp of token standards and tokenomics: ERC-20, ERC-721, ERC-1155, ERC-4626, and patterns for fractional ownership and RWAs.
Familiarity with cross-chain infrastructure (bridges, oracles) and their security assumptions.
Practical understanding of custody models (custodial wallets, MPC, multisig setups like Gnosis Safe/Fireblocks).
Strong focus on security best practices and experience defending against common DeFi / smart contract attack vectors.
Ability to work closely with product and legal/compliance teams to translate RWA structures into on-chain representations.
Tech Stack

Blockchain & Tokenization

Ethereum (Solidity, Foundry, Hardhat, OpenZeppelin)
L2s (Arbitrum, Optimism, Base, zkSync)
Token standards (ERC-20, ERC-721, ERC-1155, ERC-4626, custom RWA standards)
Cross-chain bridges and oracles (Chainlink, LayerZero, Hyperlane)
Custody frameworks, MPC wallets, account abstraction (ERC-4337)
Financial Systems

FIX Protocol, SWIFT integrations
Custodian and broker-dealer APIs
Settlement layers (USDC, stablecoin rails)
Derivatives & trading infra (order books, matching engines, perpetual futures)
Who You Are

Driven: You don’t wait for instructions and are obsessed with problem solving.
Builder at heart: You want to build systems that billions will eventually rely on.
Crypto-native or crypto-curious: You understand or are eager to master token standards, DeFi protocols, and security best practices.
Obsessed with scale and reliability: 99.99% uptime, high-throughput systems, and secure smart contract integrations are your standard.
Hungry for impact: You want to join early and shape the DNA of a generational company.
Company Philosophy

We are all here to genuinely do our life’s best work, and it will not be easy
We are assembling the Avengers. Everyone here is a super star and is world-class
We are redefining the financial markets! Everyone is a visionary and creative
The bar is set extremely high, some would say too high but excellence is not for everyone
Job Type: Full-time

Pay: $100,000.00 - $200,000.00 per year

Benefits:

Relocation assistance
Application Question(s):

Why do you want to work at Omen?
Ability to Relocate:

New York, NY 10036: Relocate before starting work (Preferred)
Work Location: In person


"""


def get_toon_prompt(job_desc: str) -> str:
    """
    Generate TOON format prompt for job description extraction.

    Args:
        job_desc: The job description text to extract from

    Returns:
        Formatted prompt string for TOON extraction
    """
    return f"""You are an expert information extraction system.
Analyze the job description and extract ALL relevant details accurately.

Return in TOON format:

{TOON_EXAMPLE}

RULES:
⚠️ CRITICAL: hard_skills_required[COUNT]{{skill,priority}}: <- MUST include {{skill,priority}}!

- Return only TOON (no markdown)
- Replace [COUNT] with actual number: if 12 items → [12]
- Array format: hard_skills = skill,priority (NO dashes) | All others = - item (MUST have "- ")
- Full explanatory sentences for soft_skills/responsibilities with technical details
- Concise for implicit_requirements/culture_signals

PRIORITY RULES:
- critical: "X+ years required" OR core to role (Java, Spring Boot for Java role)
- important: Explicitly mentioned in requirements (API design, CI/CD, TDD)
- nice: "Desired", "plus", "bonus" OR enhancement skills (additional tools)

EXTRACTION:
- hard_skills (12-15): languages, frameworks, tools, methodologies, patterns - extract from requirements AND responsibilities
- soft_skills (5-6): communication, problem-solving, leadership - write as FULL SENTENCES explaining why it matters
- responsibilities (10-12): SPECIFIC sentences with technical context (what tech, what outcome, with whom)
- tech_stack (8-10): all technologies mentioned including databases, cloud, version control

ARRAY SIZE REQUIREMENTS (MINIMUM):
hard_skills 12-15 | soft_skills 5-6 | responsibilities 10-12 | tech_stack 8-10 | keywords 12-15 | implicit_requirements 5-8 | culture_signals 5-8 | industry 1-3 | specific_knowledge 3-5

✅ CHECKLIST: 12+ hard_skills? Correct priorities? Specific responsibilities? Full sentence soft_skills?

JOB DESCRIPTION:
{job_desc}
"""


def get_json_prompt(job_desc: str, language: str = "english") -> str:
    """
    Generate JSON format prompt for job description extraction.

    Args:
        job_desc: The job description text to extract from
        language: Language for the output (english, french, german, spanish)

    Returns:
        Formatted prompt string for JSON extraction
    """

    # Language-specific instructions
    language_instructions = {
        "english": {
            "instruction": "Parse this job description and return a valid JSON object. All text values in the JSON (responsibilities, soft_skills_required, etc.) must be written in ENGLISH.",
            "note_responsibilities": "Use full, specific sentences in ENGLISH describing what the role does",
            "note_soft_skills": "Full sentences in ENGLISH explaining the soft skill",
            "note_phrases": "Concise phrases in ENGLISH"
        },
        "french": {
            "instruction": "Analysez cette description de poste et retournez un objet JSON valide. Toutes les valeurs textuelles dans le JSON (responsibilities, soft_skills_required, etc.) doivent être écrites en FRANÇAIS.",
            "note_responsibilities": "Utilisez des phrases complètes et spécifiques en FRANÇAIS décrivant ce que le rôle fait",
            "note_soft_skills": "Phrases complètes en FRANÇAIS expliquant la compétence interpersonnelle",
            "note_phrases": "Phrases concises en FRANÇAIS"
        },
        "german": {
            "instruction": "Analysieren Sie diese Stellenbeschreibung und geben Sie ein gültiges JSON-Objekt zurück. Alle Textwerte im JSON (responsibilities, soft_skills_required, usw.) müssen auf DEUTSCH geschrieben werden.",
            "note_responsibilities": "Verwenden Sie vollständige, spezifische Sätze auf DEUTSCH, die beschreiben, was die Rolle tut",
            "note_soft_skills": "Vollständige Sätze auf DEUTSCH, die die Soft Skill erklären",
            "note_phrases": "Prägnante Phrasen auf DEUTSCH"
        },
        "spanish": {
            "instruction": "Analice esta descripción de trabajo y devuelva un objeto JSON válido. Todos los valores de texto en el JSON (responsibilities, soft_skills_required, etc.) deben escribirse en ESPAÑOL.",
            "note_responsibilities": "Use oraciones completas y específicas en ESPAÑOL describiendo lo que hace el rol",
            "note_soft_skills": "Oraciones completas en ESPAÑOL explicando la habilidad interpersonal",
            "note_phrases": "Frases concisas en ESPAÑOL"
        }
    }

    lang = language.lower()
    if lang not in language_instructions:
        lang = "english"

    lang_data = language_instructions[lang]

    return f"""{lang_data["instruction"]}

CRITICAL REQUIREMENTS:
- Return ONLY valid JSON (no markdown, no commentary)
- Use the EXACT field names shown below (keep field names in English)
- ALL text values (descriptions, skills, responsibilities, etc.) must be in {language.upper()}
- Arrays must have between MIN and MAX items as specified
- hard_skills_required must be an array of objects with "skill" and "priority" fields
- priority values: "critical", "important", or "nice"

JSON SCHEMA:
{{
  "company_name": "string",
  "position_title": "string",
  "location": "string",
  "work_mode": "remote|hybrid|onsite",
  "salary_range": "string or null",
  "experience_years_required": number,
  "experience_level": "junior|mid|senior or null",
  "hard_skills_required": [
    {{"skill": "string", "priority": "critical|important|nice"}}
  ],
  "soft_skills_required": ["string"],
  "responsibilities": ["string"],
  "tech_stack": ["string"],
  "domain_expertise": {{
    "industry": ["string"],
    "specific_knowledge": ["string"]
  }},
  "implicit_requirements": ["string"],
  "company_culture_signals": ["string"],
  "ats_keywords": ["string"]
}}

ARRAY SIZE REQUIREMENTS (MIN-MAX):
- hard_skills_required: 12-15 items
- soft_skills_required: 5-6 items
- responsibilities: 8 items maximum (prioritize the most important ones and be specific and detailed)
- tech_stack: 8-10 items
- industry: 1-3 items
- specific_knowledge: 3-5 items
- implicit_requirements: 5-8 items
- company_culture_signals: 5-8 items
- ats_keywords: 12-15 items

IMPORTANT NOTES:
- responsibilities: {lang_data["note_responsibilities"]}
- soft_skills_required: {lang_data["note_soft_skills"]}
- implicit_requirements & company_culture_signals: {lang_data["note_phrases"]}
- hard_skills_required: Extract technical skills with appropriate priority levels
- Return ONLY the JSON object, no additional text

JOB DESCRIPTION:
{job_desc}
"""

def get_cv_prompt(resume_text: str, language: str = "english") -> str:
    """
    Generate JSON format prompt for CV/resume parsing.

    Args:
        resume_text: The resume/CV text to extract from
        language: Language for the output (english, french, german, spanish)

    Returns:
        Formatted prompt string for CV extraction
    """

    # Language-specific instructions
    language_instructions = {
        "english": {
            "instruction": "Parse this resume/CV and return a valid JSON object. All text values must be in ENGLISH.",
            "note": "Extract information in ENGLISH"
        },
        "french": {
            "instruction": "Analysez ce CV et retournez un objet JSON valide. Toutes les valeurs textuelles doivent être en FRANÇAIS.",
            "note": "Extraire les informations en FRANÇAIS"
        },
        "german": {
            "instruction": "Analysieren Sie diesen Lebenslauf und geben Sie ein gültiges JSON-Objekt zurück. Alle Textwerte müssen auf DEUTSCH sein.",
            "note": "Informationen auf DEUTSCH extrahieren"
        },
        "spanish": {
            "instruction": "Analice este currículum y devuelva un objeto JSON válido. Todos los valores de texto deben estar en ESPAÑOL.",
            "note": "Extraer información en ESPAÑOL"
        }
    }

    lang = language.lower()
    if lang not in language_instructions:
        lang = "english"

    lang_data = language_instructions[lang]

    return f"""{lang_data["instruction"]}

CRITICAL REQUIREMENTS:
- Return ONLY valid JSON (no markdown, no commentary)
- Use the EXACT field names shown below (keep field names in English)
- ALL text values must be in {language.upper()}
- Extract ALL information present in the resume
- If information is not present, use null or empty array

JSON SCHEMA:
{{
  "personal_info": {{
    "name": "string",
    "email": "string or null",
    "phone": "string or null",
    "location": "string or null",
    "linkedin": "string (URL) or null",
    "github": "string (URL) or null",
    "portfolio": "string (URL) or null"
  }},
  "professional_summary": "string or null",
  "technical_skills": ["skill1", "skill2"],
  "tools": ["tool1", "tool2"],
  "soft_skills": ["skill1", "skill2"],
  "work_experience": [
    {{
      "role": "string",
      "company": "string",
      "location": "string or null",
      "start_date": "string",
      "end_date": "string or 'Present'",
      "duration": "string (e.g., '2 years 3 months')",
      "achievements": ["achievement1", "achievement2"]
    }}
  ],
  "education": [
    {{
      "degree": "string",
      "institution": "string",
      "location": "string or null",
      "graduation_date": "string or null",
      "gpa": "string or null",
      "honors": "string or null"
    }}
  ],
  "projects": [
    {{
      "name": "string",
      "description": "string",
      "technologies": ["tech1", "tech2"],
      "link": "string (URL) or null"
    }}
  ],
  "certifications": ["certification name with date if available"],
  "languages": [
    {{
      "language": "string",
      "proficiency": "native|fluent|professional|intermediate|basic"
    }}
  ],
  "internships": [
    {{
      "role": "string",
      "company": "string",
      "duration": "string",
      "description": "string"
    }}
  ],
  "publications": [
    {{
      "title": "string",
      "publication": "string",
      "date": "string or null",
      "link": "string (URL) or null"
    }}
  ]
}}

EXTRACTION GUIDELINES:
- personal_info: Extract contact details carefully
- professional_summary: Brief overview of candidate's profile (2-3 sentences)
- technical_skills: Programming languages, frameworks, technologies (10-20 items)
- tools: Software, platforms, development tools (5-15 items)
- soft_skills: Communication, leadership, teamwork, etc. (3-6 items)
- work_experience: Focus on achievements and impact, not just responsibilities
- education: Include all degrees, GPA if mentioned
- projects: Personal, academic, or professional projects with tech stack
- certifications: AWS, Google, Microsoft, etc. with dates if available
- languages: Spoken languages with proficiency level
- internships: Include if present, especially for junior candidates
- publications: Research papers, blog posts, technical articles

IMPORTANT:
- {lang_data["note"]}
- Be comprehensive - extract ALL skills and experiences mentioned
- For achievements, use action verbs and quantify results when possible
- Return ONLY the JSON object, no additional text

RESUME/CV TEXT:
{resume_text}
"""

def get_detailed_gap_analysis_prompt(cv_toon: str, jd_toon: str, similarity_metrics: dict, language: str = "english") -> str:
    """
    Generate detailed gap analysis prompt aligned with pipeline.md format.
    Returns comprehensive gap categorization, scoring, and viability assessment.

    Args:
        cv_toon: CV data in TOON format
        jd_toon: Job description data in TOON format
        similarity_metrics: Pre-calculated embedding similarity metrics
        language: Language for output (currently only English supported for gap analysis)

    Returns:
        Formatted prompt string for detailed gap analysis
    """

    return f"""You are an expert recruiter and career advisor analyzing CV/JD compatibility.

CANDIDATE CV (TOON format):
{cv_toon}

JOB DESCRIPTION (TOON format):
{jd_toon}

EMBEDDING SIMILARITY SCORES (for context):
- Overall embedding similarity: {similarity_metrics['overall_embedding_similarity']}
- Skills similarity: {similarity_metrics['skills_cosine_similarity']}
- Experience similarity: {similarity_metrics['experience_cosine_similarity']}
- Critical skills match: {similarity_metrics['critical_skills_match']}
- Exact keyword match: {similarity_metrics.get('exact_keyword_match', 'N/A')}
- Missing critical skills: {similarity_metrics.get('missing_critical_skills', [])}

TASK: Provide comprehensive gap analysis with detailed categorization and scoring.

RETURN ONLY VALID JSON with this exact structure:

{{
  "overall_score": 0-100,
  "overall_status": "STRONG FIT|MODERATE FIT|WEAK FIT|POOR FIT",

  "category_scores": {{
    "hard_skills": {{
      "score": 0-100,
      "weight": 0.35,
      "status": "Strong|Good|Fair|Below Target|Poor"
    }},
    "soft_skills": {{
      "score": 0-100,
      "weight": 0.15,
      "status": "Strong|Good|Fair|Below Target|Poor"
    }},
    "experience_level": {{
      "score": 0-100,
      "weight": 0.20,
      "status": "Strong|Good|Fair|Below Target|Poor"
    }},
    "domain_expertise": {{
      "score": 0-100,
      "weight": 0.15,
      "status": "Strong|Good|Fair|Below Target|Poor"
    }},
    "portfolio_quality": {{
      "score": 0-100,
      "weight": 0.10,
      "status": "Strong|Good|Fair|Below Target|Poor"
    }},
    "location_logistics": {{
      "score": 0-100,
      "weight": 0.05,
      "status": "Strong|Good|Fair|Below Target|Poor"
    }}
  }},

  "gaps": {{
    "critical": [
      {{
        "id": "gap_001",
        "title": "Short descriptive title",
        "current": "What candidate currently has",
        "required": "What job requires",
        "impact": "-X% score",
        "severity": "CRITICAL|HIGH",
        "description": "Detailed explanation of the gap and why it matters",
        "addressability": "learnable|time-dependent|logistical",
        "timeframe_to_address": "X weeks/months/years (optional)"
      }}
    ],
    "important": [
      {{
        "id": "gap_xxx",
        "title": "Short title",
        "current": "Current state",
        "required": "Required state",
        "impact": "-X% score",
        "severity": "MEDIUM",
        "description": "Explanation",
        "addressability": "learnable|time-dependent|logistical",
        "timeframe_to_address": "X weeks/months (optional)"
      }}
    ],
    "nice_to_have": [
      {{
        "id": "gap_xxx",
        "title": "Short title",
        "current": "Current state",
        "required": "Desired state",
        "impact": "-X% score",
        "severity": "LOW",
        "description": "Why it would be beneficial",
        "addressability": "learnable"
      }}
    ],
    "logistical": [
      {{
        "id": "gap_xxx",
        "title": "Logistical barrier",
        "current": "Current situation",
        "required": "Job requirement",
        "impact": "-X% score",
        "severity": "HIGH|MEDIUM|LOW",
        "description": "Explanation of logistical challenge",
        "addressability": "logistical"
      }}
    ]
  }},

  "strengths": [
    {{
      "title": "Strength area",
      "description": "What makes this a strength",
      "evidence": "Specific evidence from CV (years, projects, achievements)"
    }}
  ],

  "application_viability": {{
    "current_likelihood": "X-Y% (e.g., 30-40%)",
    "key_blockers": ["List of main barriers to getting interview/offer"]
  }}
}}

CRITICAL INSTRUCTIONS:

1. SCORING METHODOLOGY:
   - Overall Score = Σ(Category_Score × Category_Weight)
   - Hard Skills (35%): Technical skills match (languages, frameworks, tools)
   - Soft Skills (15%): Communication, leadership, collaboration demonstrated
   - Experience Level (20%): Years and depth of relevant experience
   - Domain Expertise (15%): Industry/domain-specific knowledge
   - Portfolio Quality (10%): Projects, achievements, impact demonstrated
   - Location/Logistics (5%): Location match, work mode, availability

   Status Thresholds:
   - Strong: 85-100
   - Good: 70-84
   - Fair: 50-69
   - Below Target: 30-49
   - Poor: 0-29

2. GAP CATEGORIZATION:

   CRITICAL GAPS (typically 3-7 gaps):
   - May disqualify application or significantly harm chances
   - Examples: Experience level mismatch (3 years vs 5+ required)
              Missing critical domain expertise (no AI experience for AI role)
              Lack of required advanced skills (basic vs expert level needed)
              Fundamental skill gaps (missing primary tech stack)
   - Impact: -8% to -20% per gap
   - Severity: CRITICAL or HIGH

   IMPORTANT GAPS (typically 5-10 gaps):
   - Required but candidate might compensate with other strengths
   - Examples: Missing specific libraries/tools mentioned in JD
              Intermediate vs advanced proficiency in key skills
              Some missing soft skills or methodologies
              Partial domain knowledge
   - Impact: -3% to -8% per gap
   - Severity: MEDIUM

   NICE-TO-HAVE GAPS (typically 2-5 gaps):
   - Would strengthen application but not critical
   - Examples: Bonus skills mentioned as "plus" or "nice to have"
              Additional tools/technologies
              Extra certifications
              Specialized knowledge outside core requirements
   - Impact: -1% to -3% per gap
   - Severity: LOW

   LOGISTICAL GAPS (typically 0-4 gaps):
   - Non-technical barriers
   - Examples: Location mismatch (San Francisco vs NYC)
              Work mode preference (remote vs on-site required)
              Visa/work authorization needs
              Salary expectations mismatch
              Availability/start date conflicts
   - Impact: Variable (-5% to -15% depending on flexibility)
   - Severity: Variable

3. ADDRESSABILITY:
   - learnable: Can acquire through courses, practice, projects (weeks to months)
   - time-dependent: Requires actual work experience over time (months to years)
   - logistical: Requires life/situation changes (relocation, visa, etc.)

4. STRENGTHS:
   - List 4-8 key strengths where candidate matches or exceeds requirements
   - Include specific evidence from CV (years, quantified achievements, project complexity)
   - Focus on both technical and soft skills
   - Highlight unique value propositions

5. APPLICATION VIABILITY:
   - current_likelihood: Realistic assessment (e.g., "30-40%", "60-70%")
   - key_blockers: Top 3-5 barriers preventing interview/offer
   - Be honest and data-driven

6. IMPACT CALCULATION:
   - Each gap should have quantified impact on overall score
   - Impact should reflect severity and importance to role
   - Total gap impact should roughly equal: (100 - overall_score)

VALIDATION CHECKLIST:
✓ All scores between 0-100
✓ Category weights sum to 1.0
✓ Each gap has all required fields
✓ At least 3 strengths identified
✓ Gap IDs are unique (gap_001, gap_002, etc.)
✓ Impacts quantified as percentages
✓ Addressability correctly categorized
✓ Application likelihood is realistic

Return ONLY the JSON object, no markdown, no commentary."""

def get_compressed_gap_analysis_prompt(cv_toon: str, jd_toon: str, similarity_metrics: dict, overall_score: int = None, language: str = "english") -> str:
    """
    Compressed gap analysis prompt for performance optimization.
    Only requests gaps and strengths - category scores calculated separately.

    ~60% smaller than detailed prompt for faster Gemini processing.

    Args:
        cv_toon: CV data in TOON format
        jd_toon: Job description data in TOON format
        similarity_metrics: Pre-calculated embedding similarity metrics
        overall_score: Overall compatibility score (0-100) to guide gap count
        language: Language for output (currently only English supported)

    Returns:
        Compressed prompt string focusing on gaps and strengths only
    """

    # Determine gap count requirements based on score
    if overall_score is not None:
        if overall_score < 30:
            gap_guidance = """
⚠️ MANDATORY GAP COUNT REQUIREMENTS (Score <30% = POOR FIT):
❗ YOU MUST GENERATE MINIMUM 15-25 CRITICAL GAPS (non-negotiable!)
❗ COMPREHENSIVE ANALYSIS REQUIRED - Be extremely detailed and granular

REQUIRED APPROACH (YOU MUST FOLLOW):
1. Identify EVERY single missing skill as a SEPARATE gap (no grouping!)
2. For EACH category with score <30%, list MULTIPLE specific gaps:
   * Hard Skills: Each missing technical skill = individual CRITICAL gap
   * Soft Skills: Each missing soft skill = individual IMPORTANT gap
   * Industry mismatch: 2-3 CRITICAL gaps explaining why wrong industry
   * Role mismatch: 2-3 CRITICAL gaps explaining why wrong role type
   * Domain: 2-3 CRITICAL gaps for missing domain knowledge
   * Experience: Multiple gaps (relevance, domain fit, achievements)
3. Do NOT combine/group related issues - be granular and specific!
4. If you generate less than 15 CRITICAL gaps, YOU ARE DOING IT WRONG!

✅ Quality check: Count your gaps before responding. Minimum 15 CRITICAL required."""
        elif overall_score < 50:
            gap_guidance = """
GAP COUNT REQUIREMENTS (Score 30-50% = WEAK FIT):
- Expect 8-15 CRITICAL gaps
- Identify major skill gaps individually
- List primary mismatches in experience, domain, industry
- Be specific but can group closely related minor issues"""
        elif overall_score < 70:
            gap_guidance = """
GAP COUNT REQUIREMENTS (Score 50-70% = MODERATE FIT):
- Expect 3-8 CRITICAL gaps
- Focus on the most impactful skill and experience gaps
- Group minor related issues together"""
        else:
            gap_guidance = """
GAP COUNT REQUIREMENTS (Score >70% = GOOD FIT):
- Expect 0-3 CRITICAL gaps
- Focus only on true deal-breakers"""
    else:
        gap_guidance = ""

    return f"""Expert recruiter analyzing CV/JD gaps.

{gap_guidance}

⚠️  CRITICAL INSTRUCTION - DOMAIN EXPERTISE ASSESSMENT:
When evaluating domain expertise and industry experience, you MUST consider ALL of the following from the CV:
1. **Work Experience**: Job roles and companies in the target industry
2. **Personal Projects**: Side projects, portfolio work, and hobby projects demonstrating domain knowledge
3. **Certifications**: Industry-specific certifications and training
4. **Education**: Relevant coursework, minors, or specializations

EXAMPLE: If the JD requires "Healthcare Technology" experience and the CV shows:
- A personal project called "HealthTrack App - health tracking mobile app with WCAG compliance"
- This DOES demonstrate Healthcare domain interest and knowledge
- Do NOT say "No experience in Healthcare" - acknowledge the project as valid domain exposure

PROJECTS and CERTIFICATIONS count as domain expertise, especially for career changers and junior candidates!

CV (TOON):
{cv_toon}

JD (TOON):
{jd_toon}

CONTEXT (similarity scores):
- Overall: {similarity_metrics['overall_embedding_similarity']}
- Skills: {similarity_metrics['skills_cosine_similarity']}
- Critical match: {similarity_metrics['critical_skills_match']}
- Important match: {similarity_metrics['important_skills_match']}
- Missing critical: {similarity_metrics.get('missing_critical_skills', [])}
- Missing important: {similarity_metrics.get('missing_important_skills', [])}

RETURN JSON:
{{
  "gaps": {{
    "critical": [
      {{"id": "gap_001", "title": "Short title", "current": "What candidate has", "required": "What job needs", "impact": "-X%", "severity": "CRITICAL|HIGH", "description": "Max 100 words why it matters", "addressability": "learnable|time-dependent|logistical", "timeframe_to_address": "X months (optional)"}}
    ],
    "important": [
      {{"id": "gap_xxx", "title": "...", "current": "...", "required": "...", "impact": "-X%", "severity": "MEDIUM", "description": "Max 80 words", "addressability": "...", "timeframe_to_address": "..."}}
    ],
    "nice_to_have": [
      {{"id": "gap_xxx", "title": "...", "current": "...", "required": "...", "impact": "-X%", "severity": "LOW", "description": "Max 60 words", "addressability": "learnable"}}
    ],
    "logistical": [
      {{"id": "gap_xxx", "title": "...", "current": "...", "required": "...", "impact": "-X%", "severity": "HIGH|MEDIUM|LOW", "description": "Max 60 words", "addressability": "logistical"}}
    ]
  }},
  "strengths": [
    {{"title": "Strength area", "description": "Why it's valuable (max 60 words)", "evidence": "CV evidence (max 80 words)"}}
  ],
  "application_viability": {{
    "current_likelihood": "X-Y%",
    "key_blockers": ["Top 3-5 barriers"]
  }}
}}

GAP CATEGORIES:
- CRITICAL: Deal-breakers, -8% to -20% impact, CRITICAL/HIGH severity
  Ex: Missing primary tech stack, wrong experience level (3yr vs 10yr required), no domain expertise
- IMPORTANT: Required but compensatable, -3% to -8%, MEDIUM severity
  Ex: Missing specific tools, intermediate vs advanced proficiency
- NICE-TO-HAVE: Bonuses, -1% to -3%, LOW severity
  Ex: "Plus" skills, extra certifications
- LOGISTICAL: Non-technical barriers, variable impact
  Ex: Location mismatch, work mode, visa needs

ADDRESSABILITY:
- learnable: Courses/practice (weeks-months)
- time-dependent: Work experience (months-years)
- logistical: Life changes (relocation, visa)

STRENGTHS (4-8 items):
- Technical + soft skills where candidate matches/exceeds
- Include specific CV evidence (years, achievements, metrics)

VIABILITY:
- Realistic likelihood (30-40%, 60-70%, etc.)
- Top 3-5 blockers preventing interview/offer

BREVITY: Keep descriptions concise per word limits. Focus on impact and evidence.

Return ONLY valid JSON, no markdown."""

def get_question_generation_prompt(cv_toon: str, jd_toon: str, gaps: dict, rag_context: list, overall_score: int = None, language: str = "english") -> str:
    """
    Generate prompt for creating personalized questions based on gaps.
    Uses RAG context from similar past experiences to improve question quality.

    Args:
        cv_toon: CV in TOON format
        jd_toon: Job description in TOON format
        gaps: Categorized gaps from Phase 3
        rag_context: Similar experiences from Qdrant vector DB
        overall_score: Overall compatibility score (0-100) to guide question count
        language: Output language

    Returns:
        Formatted prompt string for question generation
    """

    # Format RAG context
    rag_examples = ""
    if rag_context:
        rag_examples = "\n\nSIMILAR PAST EXPERIENCES (RAG Context):\n"
        for i, exp in enumerate(rag_context, 1):
            rag_examples += f"\nExample {i} (similarity: {exp['score']:.2f}):\n"
            rag_examples += f"{exp['text']}\n"
            meta = exp.get('metadata', {})
            if meta:
                rag_examples += f"  Gap Type: {meta.get('gap_type', 'N/A')}\n"
                rag_examples += f"  Impact: {meta.get('impact', 'N/A')}\n"
    else:
        rag_examples = "\n\nNOTE: No RAG context available (early user). Generate questions based on gaps alone.\n"

    # Format gaps
    critical_gaps = gaps.get('critical', [])
    important_gaps = gaps.get('important', [])
    nice_to_have_gaps = gaps.get('nice_to_have', [])

    gaps_summary = f"""
CRITICAL GAPS ({len(critical_gaps)}):
"""
    for gap in critical_gaps:
        gaps_summary += f"  - {gap.get('title', 'Unknown')}: {gap.get('impact', 'N/A')} (Current: {gap.get('current', 'N/A')}, Required: {gap.get('required', 'N/A')})\n"

    gaps_summary += f"\nIMPORTANT GAPS ({len(important_gaps)}):\n"
    for gap in important_gaps:
        gaps_summary += f"  - {gap.get('title', 'Unknown')}: {gap.get('impact', 'N/A')} (Current: {gap.get('current', 'N/A')}, Required: {gap.get('required', 'N/A')})\n"

    if nice_to_have_gaps:
        gaps_summary += f"\nNICE-TO-HAVE GAPS ({len(nice_to_have_gaps)}):\n"
        for gap in nice_to_have_gaps[:3]:  # Limit to top 3
            gaps_summary += f"  - {gap.get('title', 'Unknown')}: {gap.get('impact', 'N/A')}\n"

    return f"""You are an expert career advisor helping a candidate uncover "hidden experience" to improve their job match.

CANDIDATE CV (TOON):
{cv_toon}

JOB DESCRIPTION (TOON):
{jd_toon}

IDENTIFIED GAPS FROM PHASE 3:
{gaps_summary}
{rag_examples}

⚠️  CRITICAL INSTRUCTION - CONSIDER EXISTING PROJECTS & CERTIFICATIONS:
Before asking questions, FIRST check if the candidate already has relevant experience in their CV that addresses the gaps:
1. **Personal Projects**: Check the CV's "projects" section - they may have side projects demonstrating skills/domain knowledge
2. **Certifications**: Check "certifications" - they may have completed relevant training or courses
3. **Education**: Check coursework, minors, thesis projects that relate to the gaps

If the CV already shows relevant projects or certifications that partially address a gap:
- DON'T ask if they have experience with that technology/domain - they already listed it!
- INSTEAD, ask deeper questions about that existing project/certification to uncover MORE detail
- Example: If CV shows "HealthTrack App" (healthcare project), ask about HIPAA compliance considerations, not "Do you have healthcare experience?"

TASK: Generate 5-11 personalized questions to uncover hidden experience that might close these gaps.

QUESTION GENERATION RULES:

1. PRIORITIZE BY IMPACT:
   - Focus on CRITICAL gaps first (+10% to +20% potential impact)
   - Then HIGH priority gaps (+6% to +9% impact)
   - Include 1-2 MEDIUM priority questions (+3% to +5% impact)

2. ADAPTIVE TARGET COUNT (based on overall score from Phase 3):
   {f'''⚠️ Score <30% (POOR FIT): YOU MUST GENERATE EXACTLY 9-11 QUESTIONS (MINIMUM 9 REQUIRED!)
     * 4 CRITICAL priority questions (MANDATORY - address biggest gaps)
     * 4-5 HIGH priority questions (MANDATORY - uncover hidden relevant experience)
     * 1-2 MEDIUM priority questions
     ❗ If you generate fewer than 9 questions, YOU ARE DOING IT WRONG!''' if overall_score and overall_score < 30 else f'''- Score 30-50% (WEAK FIT): Generate 7-9 questions
     * 3 CRITICAL priority questions
     * 3-4 HIGH priority questions
     * 1-2 MEDIUM priority questions''' if overall_score and overall_score < 50 else f'''- Score 51-70% (MODERATE FIT): Generate 5-7 questions
     * 2 CRITICAL priority questions
     * 2-3 HIGH priority questions
     * 1-2 MEDIUM priority questions''' if overall_score and overall_score < 70 else f'''- Score >70% (GOOD FIT): Generate 3-5 questions
     * 0-1 CRITICAL priority questions
     * 2-3 HIGH priority questions
     * 1 MEDIUM priority question''' if overall_score and overall_score >= 70 else '''- Default: Generate 6-11 questions
     * 2-4 CRITICAL priority questions
     * 3-5 HIGH priority questions
     * 1-2 MEDIUM priority questions'''}

3. QUESTION STRUCTURE:
   Each question must uncover experiences the candidate might have but didn't list on their CV:
   - Side projects, hackathons, or personal learning
   - Work experiences not highlighted or framed differently
   - Freelance or volunteer work
   - Academic projects or courses
   - Brief exposures or experimentation

4. QUESTION STYLE:
   - Open-ended to encourage detailed responses
   - Include specific sub-points or examples to jog memory
   - Show empathy: "Even if it was just for a side project..."
   - Make it easy to admit partial knowledge: "Even light exposure counts"

5. CONTEXT/WHY:
   - Explain why this question matters for the JD
   - Reference specific job requirements
   - Show how answering "yes" could improve their score

6. USE RAG CONTEXT:
   - If RAG examples are provided, use them to inform question phrasing
   - Reference similar situations from past candidates
   - Learn from what questions successfully uncovered hidden experience

7. EXAMPLES FIELD (CRITICAL - NOT QUESTIONS!):
   - Provide 3 concrete examples of work/projects/experiences the candidate MIGHT have done
   - Examples should be SPECIFIC scenarios describing actual work, NOT questions
   - Each example should be 1-2 sentences describing a realistic project/task
   - Examples help jog the candidate's memory about similar experiences they've had
   - Format as statements, not questions: "Built X using Y" NOT "Have you built X?"
   - Make examples diverse:
     * 1 professional work example (production systems, client projects)
     * 1 side project or hackathon example (personal learning, experiments)
     * 1 academic or learning example (courses, tutorials, practice projects)
   - Examples should be realistic and achievable at the candidate's level
   - Use action verbs: "Built", "Implemented", "Optimized", "Developed", "Architected", "Designed"

   GOOD EXAMPLES:
   - "Optimized database queries reducing response time from 2s to 200ms using query analysis and indexing"
   - "Built a real-time chat application with WebSockets, Redis pub/sub, and React for a hackathon"
   - "Implemented caching layer with Redis for a high-traffic API serving 50K requests/hour"

   BAD EXAMPLES (Don't do this - these are questions, not examples):
   - "Have you worked with Redis caching?"
   - "Did you optimize database queries before?"
   - "Were you involved in performance improvements?"

OUTPUT FORMAT (JSON):
{{
  "questions": [
    {{
      "id": "q1",
      "number": 1,
      "title": "Short descriptive title (e.g., 'Next.js Advanced Features')",
      "priority": "CRITICAL|HIGH|MEDIUM",
      "impact": "+X% if yes",
      "question_text": "Main question text with specific sub-points:\\n- Sub-point 1\\n- Sub-point 2\\n- Sub-point 3\\n\\nEven if it was just for learning or experimentation!",
      "context_why": "Why this matters: The JD specifically requires [specific requirement]. If you have this experience, we can highlight it.",
      "examples": [
        "Professional: Built/Optimized/Implemented [specific technical achievement with metrics]",
        "Side Project: Developed/Created [personal project with specific technologies]",
        "Learning: Experimented with/Practiced [technology/technique in learning context]"
      ]
    }}
  ]
}}

PRIORITY ASSIGNMENT RULES:
- CRITICAL: Missing skills/experience with -10% to -20% impact from gaps
- HIGH: Important skills/experience with -6% to -9% impact
- MEDIUM: Nice-to-have or soft skills with -3% to -5% impact

VALIDATION:
- All questions must have unique IDs (q1, q2, q3, ...)
- Number field must match ID number
- All required fields must be present
- Impact must be quantified as percentage
- Questions must be actionable and specific

Return ONLY the JSON object, no markdown formatting."""


def get_answer_analysis_prompt(cv_toon: str, jd_toon: str, questions_and_answers: list, language: str = "english") -> str:
    """
    Generate prompt for analyzing candidate answers and extracting uncovered experiences.
    This updates the CV with newly discovered information.
    """
    qa_text = ""
    for qa in questions_and_answers:
        qa_text += f"\n{'='*60}\n"
        qa_text += f"Q{qa['number']}: {qa['title']} ({qa['priority']} - {qa['impact']})\n"
        qa_text += f"{qa['question']}\n\n"
        qa_text += f"ANSWER ({qa['answer_type']}):\n{qa['answer']}\n"

    return f"""You are an expert career advisor analyzing a candidate's answers to uncover "hidden experience" not mentioned in their original CV.

ORIGINAL CV (TOON):
{cv_toon}

JOB REQUIREMENTS (TOON):
{jd_toon}

QUESTIONS ASKED & ANSWERS RECEIVED:
{qa_text}

TASK: Analyze each answer and extract NEW information that was NOT in the original CV.

For each answer, identify:
1. **New skills/technologies** mentioned (e.g., "used Next.js in a side project")
2. **New experiences** (e.g., "led a team of 3", "worked on AI hackathon")
3. **Depth of knowledge** (e.g., "experimented with RAG", "built production API")
4. **Context that changes interpretation** (e.g., "2 years but very complex projects")

IMPORTANT RULES:
- Only extract information that is GENUINELY NEW (not already in CV)
- Be specific: include project names, technologies, timeframes
- Quantify impact where possible
- Distinguish between:
  - STRONG signals: production experience, completion, measurable results
  - MODERATE signals: side projects, experimentation, learning
  - WEAK signals: "interested in", "planning to", "heard about"

OUTPUT FORMAT (JSON):
{{
  "uncovered_experiences": [
    {{
      "category": "skills|experience|projects|education|context",
      "description": "Specific description of what was discovered",
      "relevance_to_job": "How this addresses job requirements",
      "impact_level": "STRONG|MODERATE|WEAK",
      "evidence": "Direct quote from answer"
    }}
  ],
  "cv_updates": {{
    "skills": ["New skill 1", "New skill 2"],
    "projects": [
      {{
        "title": "Project name",
        "description": "What they did",
        "technologies": ["Tech 1"],
        "impact": "Result or learning"
      }}
    ],
    "additional_context": [
      {{
        "section": "work_experience|education|etc",
        "index": 0,
        "additional_info": "Context to add to existing entry"
      }}
    ]
  }},
  "summary": "1-2 sentence summary of what was uncovered"
}}

IMPORTANT:
- If an answer is vague or doesn't reveal new information, mark impact as WEAK or omit
- Focus on ACTIONABLE, CONCRETE discoveries
- Empty arrays are OK if nothing substantial was found
- Be honest: don't inflate weak signals

Return ONLY the JSON object, no markdown formatting."""


def get_resume_rewrite_prompt(updated_cv_toon: str, answers: list, jd_toon: str, language: str = "english") -> str:
    """
    Generate prompt for rewriting resume incorporating insights from user answers.
    Uses TOON format for all inputs to reduce tokens.
    Outputs BOTH sample.json format (camelCase, HTML) AND parsed CV format (snake_case).

    Args:
        updated_cv_toon: Parsed CV in TOON format with updates from answers
        answers: List of question-answer pairs
        jd_toon: Parsed job description in TOON format
        language: Output language

    Returns:
        Prompt string for AI to rewrite resume
    """
    # Convert answers to TOON format
    from formats.toon import to_toon
    qa_toon = to_toon(answers)

    return f"""You are an expert resume writer. Rewrite the candidate's resume incorporating insights from their answers to make it stronger and more tailored to the job.

CURRENT CV (TOON format - compressed):
{updated_cv_toon}

JOB REQUIREMENTS (TOON format - compressed):
{jd_toon}

ANSWERS PROVIDED BY CANDIDATE (TOON format - compressed):
{qa_toon}

TASK: Generate a comprehensive, professionally rewritten resume in sample_format (camelCase, HTML descriptions).
The parsed_format will be automatically derived from this, so focus on generating high-quality sample_format only.

REWRITING RULES:
1. **Rewrite ALL work experience descriptions** incorporating answer insights AND ATS keywords
   - Enhance existing responsibilities with keywords from job description
   - Example: "Built APIs" → "Developed RESTful APIs using Python and FastAPI"
   - Use keywords from JD's ats_keywords field naturally in descriptions
   - ONLY enhance what user actually did - NEVER add fake responsibilities
2. **Add new sections** mentioned in answers (projects, hackathons, certifications)
3. **Use achievement-focused language** - but ONLY based on what user actually said
4. **Format job descriptions in HTML** for sample_format (use <ul>, <li>, <strong>, <em>)
5. **Keep professional tone** - avoid exaggeration and invented details
6. **Handle empty sections** gracefully (use [] or null)
7. **Maintain chronological order** and dates from original CV
8. **Extract ALL skills** mentioned in answers and add to skills array
9. **Incorporate ATS keywords naturally** from JD into ALL descriptions (work experience, projects, summary)

PROJECT WRITING RULES (CRITICAL):
- Write 2-4 sentences per project description based ONLY on user's answer
- Use professional action verbs: "Developed", "Built", "Implemented", "Architected", "Engineered"
- Naturally incorporate ATS keywords from the job description into project descriptions
- DO NOT invent metrics, user counts, performance numbers, or timeframes
- If user mentions specific technologies, include them; otherwise infer related tech
- For achievements array: provide [SUGGESTED] placeholders or realistic examples
- Example good description: "Developed a chatbot leveraging Retrieval-Augmented Generation (RAG) architecture using LangChain and Qdrant vector database for semantic search capabilities."
- Example bad description: "Built a chatbot" (too short, no keywords)

EXAMPLE ENHANCEMENTS FROM ANSWERS:

**Work Experience Enhancement (with ATS keywords):**
- Original CV: "Built APIs for customer service"
- Answer: "I led a team of 3 developers on microservices migration"
- JD Keywords: "RESTful APIs", "Microservices", "Python", "FastAPI", "Docker"
- Rewritten: "Architected and developed RESTful APIs using Python and FastAPI for customer service microservices. Led a team of 3 developers through microservices migration, implementing Docker containerization and CI/CD pipelines."

**Project Addition:**
- Answer: "I participated in a hackathon building a RAG chatbot"
  → Add to projects section with description incorporating RAG, LangChain, Vector Databases
  → Add these skills to skills array
  → Mention in professional summary if relevant to JD

**Certification Addition:**
- Answer: "I have a certification in AWS Solutions Architect"
  → Add to certifications section with credential info

OUTPUT FORMAT (JSON) - Generate ONLY sample_format:
{{
  "sample_format": {{
    "content": {{
      "personalInfo": {{
        "jobTitle": "...",
        "firstName": "...",
        "lastName": "...",
        "email": "...",
        "phone": "...",
        "location": "...",
        "socialLinks": {{"linkedin": "...", "github": "..."}},
        ...
      }},
      "professionalSummary": "Enhanced 3-4 sentence summary incorporating key achievements from answers",
      "careerObjective": "Optional: career goals if mentioned in answers, else null",
      "employmentHistory": [
        {{
          "jobTitle": "...",
          "company": "...",
          "location": "...",
          "startDate": "YYYY-MM",
          "endDate": "YYYY-MM or empty string if current",
          "currentlyWorking": true/false,
          "description": "<ul><li>Achievement-focused bullet point with <strong>metrics</strong></li><li>Incorporated insights from answers</li></ul>"
        }}
      ],
      "education": [...],
      "skills": [
        {{"skill": "JavaScript", "level": "Advanced", "category": "Programming Languages"}},
        {{"skill": "NEW_SKILL_FROM_ANSWERS", "level": "Intermediate", "category": "..."}}
      ],
      "technicalStack": ["React", "Node.js", "..."],
      "languages": [{{"language": "English", "proficiency": "Native"}}],
      "certifications": [
        {{"title": "...", "issuer": "...", "date": "...", "credential": "..."}}
      ],
      "projects": [
        {{
          "title": "RAG-Powered Chatbot",
          "description": "<p>Developed a chatbot leveraging <strong>Retrieval-Augmented Generation (RAG)</strong> architecture using LangChain and Qdrant vector database. Implemented semantic search capabilities to retrieve relevant information from a knowledge base. Utilized OpenAI embeddings for natural language understanding and context-aware responses.</p>",
          "technologies": ["Python", "LangChain", "Qdrant", "OpenAI", "RAG", "Vector Databases"],
          "achievements": [
            "[SUGGESTED] Implemented efficient vector similarity search",
            "[SUGGESTED] Integrated with existing knowledge base systems",
            "[SUGGESTED] Optimized response accuracy through iterative testing"
          ],
          "role": "Developer",
          "startDate": "YYYY-MM",
          "endDate": "YYYY-MM",
          "url": null
        }}
      ],
      "publications": [],
      "references": [],
      "hobbies": [],
      "internships": [],
      "customSections": {{
        "awards": [],
        "volunteering": [],
        "conferences": []
      }}
    }}
  }},
  "enhancements_made": [
    "Added hackathon project: RAG Chatbot",
    "Enhanced Senior Developer role with team leadership details",
    "Added 5 new skills: RAG, LangChain, Vector Databases, FastAPI, Qdrant",
    "Added AWS Solutions Architect certification",
    "Rewrote professional summary to highlight AI/ML experience"
  ]
}}

IMPORTANT - DO NOT INVENT INFORMATION:
- Base ALL descriptions on user's actual answers - NO invented metrics, dates, or achievements
- For achievements: use [SUGGESTED] prefix for placeholders based on typical outcomes
- Write descriptions professionally (2-4 sentences) but stay truthful to user's answers
- Incorporate ATS keywords from job description naturally into descriptions
- Use HTML formatting for descriptions (use <p>, <ul>, <li>, <strong> tags)
- Empty sections should be [] or null, not omitted
- Dates format: "YYYY-MM" or "YYYY-MM-DD" (use actual dates from CV or null if not provided)
- All skills from answers MUST appear in the output

Return ONLY the JSON object, no markdown formatting."""


def get_domain_finder_prompt(resume_text: str, language: str = "english") -> str:
    """
    Generate prompt for domain/career path finder based on resume.
    Suggests 8-10 domains ranked by fit and provides skill gap analysis for each.

    Args:
        resume_text: The resume/CV text to analyze
        language: Language for the output (english, french, german, spanish)

    Returns:
        Formatted prompt string for domain finder
    """

    language_instructions = {
        "english": {
            "instruction": "Analyze this resume and suggest 8-10 career domains/industries where this candidate could apply for jobs.",
            "note": "All text values must be in ENGLISH"
        },
        "french": {
            "instruction": "Analysez ce CV et suggérez 8-10 domaines de carrière/industries où ce candidat pourrait postuler.",
            "note": "Toutes les valeurs textuelles doivent être en FRANÇAIS"
        },
        "german": {
            "instruction": "Analysieren Sie diesen Lebenslauf und schlagen Sie 8-10 Karrieredomänen/Branchen vor, in denen sich dieser Kandidat bewerben könnte.",
            "note": "Alle Textwerte müssen auf DEUTSCH sein"
        },
        "spanish": {
            "instruction": "Analice este currículum y sugiera 8-10 dominios de carrera/industrias donde este candidato podría solicitar empleos.",
            "note": "Todos los valores de texto deben estar en ESPAÑOL"
        }
    }

    lang = language.lower()
    if lang not in language_instructions:
        lang = "english"

    lang_data = language_instructions[lang]

    return f"""{lang_data["instruction"]} Suggest specific ROLE + INDUSTRY combinations.

CRITICAL REQUIREMENTS:
- Return ONLY valid JSON (no markdown, no commentary)
- {lang_data["note"]}
- Suggest 8-10 SPECIFIC role+industry combinations (e.g., "Backend Developer - Gaming", not just "Backend Engineering")
- Each suggestion must be a TECHNICAL ROLE paired with a SPECIFIC INDUSTRY
- Analyze resume work experience AND hobbies/projects to determine industry interests
- Match technical role specificity to experience level (Junior: broad, Senior: specific)

STEP 1: ANALYZE RESUME FOR INDUSTRIES
Extract industry signals from:
1. **Work Experience**: Which industries did they work in? (Gaming, Finance, Healthcare, etc.)
2. **Personal Projects/Hobbies**: Side projects, hackathons, portfolio items (e.g., "built a game" → Gaming interest)
3. **Technical Skills**: Skills that hint at industries (Unity/Unreal → Gaming, payment APIs → FinTech, HIPAA → Healthcare)

STEP 2: DETERMINE EXPERIENCE LEVEL & ROLE SPECIFICITY
- **Junior/Mid (0-5 years)**: Use broad roles
  Examples: "Backend Developer", "Frontend Engineer", "Full-Stack Developer"
- **Senior (5-10 years)**: Use specific roles
  Examples: "Senior Backend Engineer", "Lead Frontend Developer", "Principal Full-Stack Engineer"
- **Staff/Principal (10+ years)**: Use architect/leadership roles
  Examples: "Staff Engineer", "Solutions Architect", "Engineering Manager"

STEP 3: TECHNICAL ROLES (choose based on skills)
- Backend Developer/Engineer (APIs, databases, server-side)
- Frontend Developer/Engineer (UI, React, Vue, mobile apps)
- Full-Stack Developer/Engineer (both frontend + backend)
- DevOps Engineer (CI/CD, cloud infrastructure, containers)
- Data Engineer (data pipelines, ETL, warehousing)
- Data Scientist (ML, analytics, statistics)
- ML/AI Engineer (machine learning, deep learning)
- Mobile Developer (iOS, Android, React Native, Flutter)
- QA/Test Engineer (automation, testing frameworks)
- Security Engineer (cybersecurity, penetration testing)
- Site Reliability Engineer (SRE) (monitoring, uptime, scalability)
- Cloud Architect (cloud design, multi-cloud strategies)
- Solutions Architect (enterprise architecture)
- Technical Product Manager (technical leadership + product)

STEP 4: INDUSTRIES (match to resume)
- **Gaming**: Game engines (Unity, Unreal), multiplayer, game physics
- **FinTech/Finance**: Payment processing, trading, banking, crypto, fraud detection
- **HealthTech/Healthcare**: Electronic health records, HIPAA, telemedicine, medical devices
- **EdTech/Education**: Learning management systems, online courses, educational apps
- **E-commerce/Retail**: Shopping carts, inventory, logistics, marketplaces
- **Media & Entertainment**: Streaming, content delivery, social media, music/video platforms
- **Enterprise SaaS**: B2B software, productivity tools, CRM, HR systems
- **Cybersecurity**: Threat detection, encryption, penetration testing, compliance
- **IoT/Hardware**: Embedded systems, sensors, device management, firmware
- **Transportation/Mobility**: Ride-sharing, logistics, autonomous vehicles, fleet management
- **Real Estate/PropTech**: Property management, rental platforms, real estate marketplaces
- **Social Impact/Non-Profit**: Civic tech, sustainability, climate tech, accessibility
- **Advertising/MarTech**: Ad tech, marketing automation, analytics platforms
- **Travel/Hospitality**: Booking platforms, hotel management, travel planning
- **Food & Delivery**: Restaurant tech, food delivery, kitchen automation

JSON SCHEMA:
{{
  "domains": [
    {{
      "domain_name": "Technical Role - Industry (e.g., 'Backend Developer - Gaming')",
      "technical_role": "string (e.g., 'Backend Developer', 'Senior API Engineer')",
      "industry": "string (e.g., 'Gaming', 'FinTech', 'HealthTech')",
      "fit_score": 0-100,
      "rank": 1-10,
      "matching_skills": ["Combined list of role skills + industry skills they already have"],
      "skills_to_learn": ["REQUIRED: Combined list of ALL skills to learn (merge role_skills_to_learn + industry_skills_to_learn)"],
      "role_skills_to_learn": ["Technical skills needed for the ROLE (Node.js, Docker, Kubernetes, etc.)"],
      "industry_skills_to_learn": ["Domain knowledge needed for the INDUSTRY (Unity backend, payment APIs, HIPAA, etc.)"],
      "learning_priority": "HIGH|MEDIUM|LOW",
      "time_to_ready": "string (e.g., '2-3 months', '6-12 months')",
      "reasoning": "1-2 sentences why this ROLE fits their skills",
      "industry_rationale": "1-2 sentences why this INDUSTRY matches (based on work experience, projects, or hobbies)"
    }}
  ]
}}

ANALYSIS GUIDELINES:

1. **COMBINING ROLE + INDUSTRY**:
   - Match technical skills to role (Backend, Frontend, DevOps, etc.)
   - Match work history/projects/hobbies to industry (Gaming, FinTech, etc.)
   - Create combinations that are both technically feasible AND aligned with interests
   - Example: "Built Unity games" + "Node.js backend skills" = "Backend Developer - Gaming"

2. **FIT SCORE (0-100)**:
   - Consider BOTH role skills AND industry knowledge
   - 85-100: Perfect match (strong role skills + relevant industry experience/interest)
   - 70-84: Good match (strong role skills + some industry connection)
   - 55-69: Moderate match (adequate role skills + tangential industry interest)
   - 40-54: Weak match (some transferable skills + new industry)

3. **MATCHING SKILLS** (5-12 items):
   - Include BOTH technical role skills AND industry-specific skills
   - Example for "Backend Developer - Gaming":
     - Role: Node.js, PostgreSQL, Redis, Docker, REST APIs
     - Industry: Unity backend integration, WebSockets, real-time networking

4. **SKILLS TO LEARN** - Provide THREE lists:

   **skills_to_learn** (6-12 items): REQUIRED - Merge role_skills_to_learn + industry_skills_to_learn into one combined list

   **role_skills_to_learn** (3-6 items): Technical skills needed for the ROLE
   - Example for Backend Developer: gRPC, Kubernetes, Microservices, Service Mesh

   **industry_skills_to_learn** (3-6 items): Domain knowledge for the INDUSTRY
   - Example for Gaming: Unity multiplayer backend, Game server architecture, Player matchmaking, Anti-cheat systems
   - Example for FinTech: Payment gateway APIs, PCI compliance, Fraud detection, KYC/AML regulations
   - Example for HealthTech: HIPAA compliance, HL7/FHIR standards, Medical data security, EHR integration

   **IMPORTANT**: skills_to_learn must equal role_skills_to_learn + industry_skills_to_learn combined

5. **LEARNING PRIORITY**:
   - HIGH: Missing critical skills for EITHER role OR industry
   - MEDIUM: Missing important skills but can compensate
   - LOW: Minor gaps, easy to learn

6. **TIME TO READY**:
   - "0-1 months": Perfect match, ready now
   - "1-2 months": Minor gaps to close
   - "2-3 months": Some focused learning needed
   - "3-6 months": Moderate reskilling required
   - "6-12 months": Significant learning needed
   - "1-2 years": Major career pivot

7. **REASONING** (for the ROLE):
   - Explain why their technical skills match this role
   - Reference specific technologies/experiences
   - Example: "Your Node.js, PostgreSQL, and Docker experience aligns perfectly with backend engineering requirements"

8. **INDUSTRY_RATIONALE** (for the INDUSTRY):
   - Explain why this industry matches based on:
     - Work experience in similar industry
     - Personal projects/hobbies (e.g., "Based on your Unity game project")
     - Interest signals (e.g., "Your experience with payment APIs suggests FinTech interest")
   - If no direct connection, explain transferable domain knowledge
   - Example: "Your Unity side project and game networking hobby indicate strong interest in gaming industry"

RANKING STRATEGY:
- Prioritize combinations where:
  1. Strong role skills match (they can do the job)
  2. Clear industry interest (work experience, projects, or hobbies)
  3. Realistic path to entry (not too many gaps)

VALIDATION CHECKLIST:
✓ Exactly 8-10 ROLE + INDUSTRY combinations
✓ Each domain_name format: "Role - Industry"
✓ All have technical_role and industry fields filled
✓ Both role_skills_to_learn AND industry_skills_to_learn present
✓ industry_rationale explains why THIS industry (not just the role)
✓ Mix of industries (don't suggest all gaming or all fintech)

IMPORTANT:
- Be specific with role names based on experience level
- Prioritize industries where they have work experience or personal projects
- Include diverse industries to give them options
- Split skills clearly: ROLE skills vs INDUSTRY domain knowledge
- Industry rationale must be evidence-based (cite projects, work history, hobbies)

RESUME TEXT:
{resume_text}

Return ONLY the JSON object, no additional text."""
