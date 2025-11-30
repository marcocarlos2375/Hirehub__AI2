"""
Pre-cached role categorizations to reduce LLM API calls.
These cover the most common job roles encountered in job descriptions.
"""

from typing import Optional
from core.config.logging_config import logger

# Pre-cached role categorizations
# Maps common job titles (lowercase) to their category
ROLE_CATEGORY_CACHE = {
    # Engineering / Software Development
    "software engineer": "Engineering",
    "software developer": "Engineering",
    "full stack developer": "Engineering",
    "full-stack developer": "Engineering",
    "fullstack developer": "Engineering",
    "frontend developer": "Engineering",
    "front-end developer": "Engineering",
    "backend developer": "Engineering",
    "back-end developer": "Engineering",
    "web developer": "Engineering",
    "mobile developer": "Engineering",
    "ios developer": "Engineering",
    "android developer": "Engineering",
    "platform engineer": "Engineering",
    "systems engineer": "Engineering",
    "devops engineer": "Engineering",
    "site reliability engineer": "Engineering",
    "sre": "Engineering",
    "cloud engineer": "Engineering",
    "infrastructure engineer": "Engineering",
    "embedded engineer": "Engineering",
    "embedded software engineer": "Engineering",
    "firmware engineer": "Engineering",
    "qa engineer": "Engineering",
    "quality assurance engineer": "Engineering",
    "test engineer": "Engineering",
    "automation engineer": "Engineering",
    "security engineer": "Engineering",
    "application security engineer": "Engineering",
    "release engineer": "Engineering",
    "build engineer": "Engineering",
    "game developer": "Engineering",
    "graphics engineer": "Engineering",
    "blockchain developer": "Engineering",
    "smart contract developer": "Engineering",

    # Data & Analytics
    "data scientist": "Data",
    "data analyst": "Data",
    "data engineer": "Data",
    "machine learning engineer": "Data",
    "ml engineer": "Data",
    "ai engineer": "Data",
    "artificial intelligence engineer": "Data",
    "business intelligence analyst": "Data",
    "bi analyst": "Data",
    "analytics engineer": "Data",
    "data architect": "Data",
    "research scientist": "Data",
    "research engineer": "Data",
    "nlp engineer": "Data",
    "computer vision engineer": "Data",
    "deep learning engineer": "Data",
    "mlops engineer": "Data",
    "statistician": "Data",

    # Product
    "product manager": "Product",
    "product owner": "Product",
    "technical product manager": "Product",
    "senior product manager": "Product",
    "associate product manager": "Product",
    "group product manager": "Product",
    "director of product": "Product",
    "vp of product": "Product",
    "chief product officer": "Product",
    "product designer": "Product",

    # Design
    "ux designer": "Design",
    "ui designer": "Design",
    "ui/ux designer": "Design",
    "ux/ui designer": "Design",
    "user experience designer": "Design",
    "user interface designer": "Design",
    "product designer": "Design",
    "visual designer": "Design",
    "graphic designer": "Design",
    "interaction designer": "Design",
    "design lead": "Design",
    "creative director": "Design",
    "art director": "Design",
    "brand designer": "Design",
    "motion designer": "Design",
    "ux researcher": "Design",

    # Management / Leadership
    "engineering manager": "Management",
    "software engineering manager": "Management",
    "technical lead": "Management",
    "tech lead": "Management",
    "team lead": "Management",
    "director of engineering": "Management",
    "vp of engineering": "Management",
    "chief technology officer": "Management",
    "cto": "Management",
    "chief information officer": "Management",
    "cio": "Management",
    "architect": "Management",
    "software architect": "Management",
    "solutions architect": "Management",
    "enterprise architect": "Management",
    "technical architect": "Management",
    "principal engineer": "Management",
    "staff engineer": "Management",
    "distinguished engineer": "Management",

    # Sales & Marketing
    "sales representative": "Sales",
    "account executive": "Sales",
    "sales manager": "Sales",
    "business development": "Sales",
    "bdm": "Sales",
    "account manager": "Sales",
    "customer success manager": "Sales",
    "solutions engineer": "Sales",
    "sales engineer": "Sales",
    "pre-sales engineer": "Sales",
    "marketing manager": "Marketing",
    "digital marketing manager": "Marketing",
    "growth marketer": "Marketing",
    "content marketer": "Marketing",
    "seo specialist": "Marketing",
    "marketing analyst": "Marketing",
    "brand manager": "Marketing",

    # Operations
    "operations manager": "Operations",
    "technical operations": "Operations",
    "it operations": "Operations",
    "system administrator": "Operations",
    "network administrator": "Operations",
    "database administrator": "Operations",
    "dba": "Operations",
    "support engineer": "Operations",
    "technical support": "Operations",
    "help desk": "Operations",

    # Finance
    "financial analyst": "Finance",
    "accountant": "Finance",
    "controller": "Finance",
    "cfo": "Finance",
    "chief financial officer": "Finance",
    "treasurer": "Finance",
    "finance manager": "Finance",

    # HR
    "human resources": "HR",
    "hr manager": "HR",
    "recruiter": "HR",
    "talent acquisition": "HR",
    "people operations": "HR",
    "hr business partner": "HR",

    # Legal & Compliance
    "legal counsel": "Legal",
    "general counsel": "Legal",
    "compliance officer": "Legal",
    "contract manager": "Legal",
    "paralegal": "Legal",

    # Consulting
    "consultant": "Consulting",
    "management consultant": "Consulting",
    "strategy consultant": "Consulting",
    "technology consultant": "Consulting",
    "senior consultant": "Consulting",
    "principal consultant": "Consulting",
}


def get_cached_role_category(role: str) -> Optional[str]:
    """
    Get category for a role from pre-built cache.

    Args:
        role: Job role/title to categorize

    Returns:
        Category string if found in cache, None otherwise
    """
    if not role:
        return None

    # Normalize the role
    normalized = role.lower().strip()

    # Try exact match first
    if normalized in ROLE_CATEGORY_CACHE:
        return ROLE_CATEGORY_CACHE[normalized]

    # Try partial match (role contained in cache key or vice versa)
    for cached_role, category in ROLE_CATEGORY_CACHE.items():
        if cached_role in normalized or normalized in cached_role:
            return category

    return None


def categorize_role_with_cache(role: str, llm_fallback_fn=None) -> str:
    """
    Categorize a role, using cache first, then LLM fallback if not found.

    Args:
        role: Job role/title to categorize
        llm_fallback_fn: Optional function to call for LLM categorization

    Returns:
        Category string
    """
    # Try cache first
    cached = get_cached_role_category(role)
    if cached:
        logger.debug(f"Role cache hit for '{role}' -> {cached}")
        return cached

    # If we have a fallback function, use it
    if llm_fallback_fn:
        logger.debug(f"Role cache miss for '{role}', using LLM fallback")
        return llm_fallback_fn(role)

    # Default fallback
    logger.debug(f"Role cache miss for '{role}', no fallback available, returning 'Other'")
    return "Other"


__all__ = [
    'ROLE_CATEGORY_CACHE',
    'get_cached_role_category',
    'categorize_role_with_cache',
]
