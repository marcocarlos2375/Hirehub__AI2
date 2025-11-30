"""
Data Cleaner for Job Descriptions

Cleans raw job descriptions from web scraping:
- Remove HTML tags and entities
- Normalize Unicode characters
- Remove excessive whitespace
- Fix encoding issues
- Remove LinkedIn/Indeed UI artifacts
"""

import re
import html
import unicodedata
from typing import Optional


def remove_html_tags(text: str) -> str:
    """
    Remove HTML tags from text.

    Args:
        text: Raw text with potential HTML tags

    Returns:
        Text with HTML tags removed
    """
    # Remove script and style tags completely
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

    # Remove all HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Decode HTML entities
    text = html.unescape(text)

    return text


def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode characters to their closest ASCII equivalents.

    Args:
        text: Text with potential Unicode issues

    Returns:
        Normalized text
    """
    # Normalize to NFKD form (compatibility decomposition)
    text = unicodedata.normalize('NFKD', text)

    # Try to encode/decode to handle special characters
    try:
        text = text.encode('ascii', 'ignore').decode('ascii')
    except:
        pass

    return text


def remove_excessive_whitespace(text: str) -> str:
    """
    Remove excessive whitespace while preserving paragraph structure.

    Args:
        text: Text with potential whitespace issues

    Returns:
        Text with normalized whitespace
    """
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)

    # Replace multiple newlines with max 2 newlines
    text = re.sub(r'\n\n+', '\n\n', text)

    # Remove leading/trailing whitespace per line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    # Remove leading/trailing whitespace overall
    text = text.strip()

    return text


def remove_linkedin_artifacts(text: str) -> str:
    """
    Remove LinkedIn UI artifacts that appear in scraped text.

    Args:
        text: Text potentially containing LinkedIn artifacts

    Returns:
        Cleaned text
    """
    artifacts = [
        r'Apply\s*Save\s*Save.*?at.*?\n',
        r'See how you compare to \d+ others who clicked apply',
        r'Access exclusive applicant insights.*?\n',
        r'Retry Premium for.*?\n',
        r'People you can reach out to.*?\n',
        r'\d+ people clicked apply',
        r'Promoted by hirer.*?\n',
        r'Responses managed off LinkedIn',
        r'Show more options',
        r'Job search faster with Premium',
        r'About the company.*?company logo',
        r'\d+,?\d* followers',
        r'Follow\s*Software Devel',  # Truncated text artifacts
    ]

    for pattern in artifacts:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)

    return text


def remove_indeed_artifacts(text: str) -> str:
    """
    Remove Indeed UI artifacts.

    Args:
        text: Text potentially containing Indeed artifacts

    Returns:
        Cleaned text
    """
    artifacts = [
        r'Job Type:.*?\n',
        r'Posted \d+ days ago',
        r'Urgently hiring',
        r'Responsive employer',
        r'Report job',
        r'Save job',
        r'Apply now',
        r'\d+ reviews',
    ]

    for pattern in artifacts:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return text


def clean_job_description(text: str, remove_unicode: bool = False) -> Optional[str]:
    """
    Complete cleaning pipeline for job descriptions.

    Args:
        text: Raw job description text
        remove_unicode: Whether to convert Unicode to ASCII (default: False, preserves € symbols etc.)

    Returns:
        Cleaned text, or None if text is empty/invalid
    """
    if not text or not isinstance(text, str):
        return None

    # Step 1: Remove HTML
    text = remove_html_tags(text)

    # Step 2: Remove LinkedIn artifacts
    text = remove_linkedin_artifacts(text)

    # Step 3: Remove Indeed artifacts
    text = remove_indeed_artifacts(text)

    # Step 4: Normalize Unicode (optional - we may want to keep € symbols for complexity scoring)
    if remove_unicode:
        text = normalize_unicode(text)

    # Step 5: Clean whitespace
    text = remove_excessive_whitespace(text)

    # Validation: Must have at least 50 characters after cleaning
    if len(text) < 50:
        return None

    return text


def extract_job_title(raw_text: str) -> Optional[str]:
    """
    Extract job title from raw scraped text.
    Usually the first substantial line.

    Args:
        raw_text: Raw job description text

    Returns:
        Job title or None
    """
    lines = raw_text.split('\n')

    for line in lines:
        line = line.strip()
        # Job titles are usually 2-10 words, not too long
        if 5 <= len(line) <= 100:
            # Exclude lines that look like URLs or metadata
            if not re.search(r'http|www\.|@|\d{4}-\d{2}-\d{2}', line):
                return line

    return None


def extract_company_name(raw_text: str) -> Optional[str]:
    """
    Extract company name from raw scraped text.
    Often appears after job title or in specific patterns.

    Args:
        raw_text: Raw job description text

    Returns:
        Company name or None
    """
    # Pattern 1: "at [Company]"
    match = re.search(r'at\s+([A-Z][A-Za-z0-9\s&.]+?)(?:\s+·|\s+\n)', raw_text)
    if match:
        return match.group(1).strip()

    # Pattern 2: "[JobTitle] · [Company]"
    match = re.search(r'·\s+([A-Z][A-Za-z0-9\s&.]+?)(?:\s+·|\s+\n)', raw_text)
    if match:
        return match.group(1).strip()

    return None


def validate_cleaned_job(job: dict) -> bool:
    """
    Validate that a cleaned job has all required fields.

    Args:
        job: Job dictionary with 'description' field

    Returns:
        True if valid, False otherwise
    """
    if not job or not isinstance(job, dict):
        return False

    if 'description' not in job:
        return False

    desc = job['description']
    if not desc or not isinstance(desc, str):
        return False

    # Must be at least 50 characters
    if len(desc) < 50:
        return False

    # Must have at least 10 words
    if len(desc.split()) < 10:
        return False

    return True
