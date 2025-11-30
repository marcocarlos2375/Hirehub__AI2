"""
Complexity Scorer for Job Descriptions

Scores job descriptions 0-100 based on characteristics that stress-test the scoring endpoint:
- Length (word count)
- Technical skill density
- Special characters (currency, percentages, numbers)
- AI/LLM references (Gemini, Claude, GPT)
- Funding/company stage indicators
- Industry-specific jargon

Higher scores = more likely to trigger edge cases and bugs.
"""

import re
from typing import List, Dict

# Comprehensive tech skills list for matching
TECH_KEYWORDS = [
    # Programming Languages
    'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Go', 'Rust',
    'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala', 'Elixir', 'Clojure', 'Haskell',
    'R', 'MATLAB', 'Julia', 'Perl', 'Dart', 'Lua', 'Shell', 'Bash',

    # Frontend
    'React', 'Vue', 'Angular', 'Svelte', 'Next.js', 'Nuxt', 'jQuery',
    'HTML', 'CSS', 'Tailwind', 'Bootstrap', 'SASS', 'LESS', 'Webpack',

    # Backend/Frameworks
    'FastAPI', 'Django', 'Flask', 'Express', 'Node.js', 'Spring', 'Rails',
    '.NET', 'ASP.NET', 'Laravel', 'Symfony', 'Phoenix', 'Gin', 'Echo',

    # Databases
    'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Cassandra', 'DynamoDB',
    'Oracle', 'SQL Server', 'MariaDB', 'CouchDB', 'Neo4j', 'Elasticsearch',

    # Cloud/DevOps
    'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Ansible',
    'Jenkins', 'GitLab CI', 'GitHub Actions', 'CircleCI', 'Travis CI',

    # Data/ML
    'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'Spark',
    'Hadoop', 'Kafka', 'Airflow', 'dbt', 'Snowflake', 'Databricks',

    # Tools/Other
    'Git', 'Linux', 'Nginx', 'GraphQL', 'REST API', 'gRPC', 'RabbitMQ',
    'Celery', 'Microservices', 'Lambda', 'S3', 'EC2', 'Route 53', 'CloudFront'
]

# AI/LLM references that can confuse the AI models
LLM_KEYWORDS = [
    'Gemini', 'Claude', 'GPT', 'ChatGPT', 'OpenAI', 'LLM', 'AI model',
    'Anthropic', 'Google AI', 'machine learning model', 'neural network',
    'transformer', 'BERT', 'GPT-3', 'GPT-4', 'Llama', 'Mistral', 'Cohere'
]

# Funding/company stage indicators
FUNDING_PATTERNS = [
    r'Series [A-D]', r'Pre-seed', r'Seed', r'\$\d+M', r'\$\d+B',
    r'Fortune \d+', r'unicorn', r'funding', r'valuation', r'IPO',
    r'Series A', r'Series B', r'venture-backed', r'Y Combinator'
]

# Industry-specific jargon
INDUSTRY_JARGON = [
    'fintech', 'blockchain', 'crypto', 'DeFi', 'Web3', 'NFT',
    'healthcare', 'HIPAA', 'GDPR', 'SOC 2', 'ISO 27001', 'compliance',
    'biotech', 'pharma', 'clinical', 'FDA', 'medical device',
    'e-commerce', 'marketplace', 'SaaS', 'B2B', 'B2C', 'D2C',
    'edtech', 'insurtech', 'proptech', 'agtech', 'cleantech'
]


def calculate_complexity_score(job_description: str) -> int:
    """
    Score job description complexity (0-100).
    Higher scores = more likely to stress-test the system.

    Args:
        job_description: Raw job description text

    Returns:
        Complexity score (0-100)
    """
    if not job_description or len(job_description.strip()) == 0:
        return 0

    score = 0

    # 1. Length: 500+ words (+20 points)
    word_count = len(job_description.split())
    if word_count >= 500:
        score += 20
    elif word_count >= 300:
        score += 10
    elif word_count >= 100:
        score += 5

    # 2. Technical skills: 8+ unique skills (+20 points)
    skill_count = sum(1 for kw in TECH_KEYWORDS if kw.lower() in job_description.lower())
    if skill_count >= 8:
        score += 20
    elif skill_count >= 5:
        score += 10
    elif skill_count >= 3:
        score += 5

    # 3. Special characters (+15 points)
    has_currency = any(c in job_description for c in ['$', '€', '¥', '£', '¢'])
    has_percentages = '%' in job_description
    has_numbers_in_text = bool(re.search(r'\d+[KMB]?\+?', job_description))

    special_char_count = sum([has_currency, has_percentages, has_numbers_in_text])
    if special_char_count >= 2:
        score += 15
    elif special_char_count == 1:
        score += 7

    # 4. AI/LLM references (+15 points) - These can confuse AI models
    llm_matches = sum(1 for kw in LLM_KEYWORDS if kw in job_description)
    if llm_matches >= 2:
        score += 15
    elif llm_matches == 1:
        score += 7

    # 5. Funding/company stage indicators (+15 points)
    funding_matches = sum(1 for pattern in FUNDING_PATTERNS
                         if re.search(pattern, job_description, re.IGNORECASE))
    if funding_matches >= 2:
        score += 15
    elif funding_matches == 1:
        score += 7

    # 6. Industry jargon (+15 points)
    jargon_matches = sum(1 for kw in INDUSTRY_JARGON if kw.lower() in job_description.lower())
    if jargon_matches >= 3:
        score += 15
    elif jargon_matches >= 2:
        score += 10
    elif jargon_matches == 1:
        score += 5

    return min(score, 100)


def get_complexity_details(job_description: str) -> Dict[str, any]:
    """
    Get detailed breakdown of complexity score.
    Useful for debugging and understanding why a job scored high/low.

    Args:
        job_description: Raw job description text

    Returns:
        Dictionary with score breakdown
    """
    if not job_description or len(job_description.strip()) == 0:
        return {
            'total_score': 0,
            'word_count': 0,
            'details': 'Empty job description'
        }

    word_count = len(job_description.split())

    # Count matches for each category
    skills_found = [kw for kw in TECH_KEYWORDS if kw.lower() in job_description.lower()]
    llm_refs = [kw for kw in LLM_KEYWORDS if kw in job_description]
    funding_matches = [pattern for pattern in FUNDING_PATTERNS
                      if re.search(pattern, job_description, re.IGNORECASE)]
    jargon_found = [kw for kw in INDUSTRY_JARGON if kw.lower() in job_description.lower()]

    # Special characters
    has_currency = any(c in job_description for c in ['$', '€', '¥', '£', '¢'])
    has_percentages = '%' in job_description
    has_numbers = bool(re.search(r'\d+[KMB]?\+?', job_description))

    return {
        'total_score': calculate_complexity_score(job_description),
        'word_count': word_count,
        'technical_skills_found': len(skills_found),
        'skills_sample': skills_found[:5],  # Show first 5
        'llm_references': llm_refs,
        'funding_indicators': len(funding_matches),
        'industry_jargon': jargon_found,
        'special_characters': {
            'has_currency': has_currency,
            'has_percentages': has_percentages,
            'has_numbers': has_numbers
        }
    }


def filter_by_complexity(jobs: List[Dict], min_score: int = 60) -> List[Dict]:
    """
    Filter jobs by minimum complexity score.

    Args:
        jobs: List of job dictionaries with 'description' field
        min_score: Minimum complexity score (default: 60)

    Returns:
        Filtered list of complex jobs
    """
    filtered = []

    for job in jobs:
        if 'description' not in job:
            continue

        score = calculate_complexity_score(job['description'])

        if score >= min_score:
            # Add complexity score to job metadata
            job['complexity_score'] = score
            filtered.append(job)

    # Sort by complexity (highest first)
    filtered.sort(key=lambda x: x['complexity_score'], reverse=True)

    return filtered
