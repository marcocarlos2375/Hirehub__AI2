"""
Error Classifier for Test Results

Categorizes errors by type and provides debugging hints.
"""

from typing import Dict, Optional


class ErrorClassifier:
    """
    Categorize errors for better debugging.
    """

    ERROR_CATEGORIES = {
        'json_parsing': {
            'patterns': ['JSONDecodeError', 'Expecting value', 'line 1 column 1'],
            'severity': 'CRITICAL',
            'likely_cause': 'Gemini returned invalid/incomplete JSON',
            'fix_location': 'main.py lines 2230-2248 (gap analysis) or 1816-1825 (score message)'
        },
        '500_internal_error': {
            'patterns': ['500 Internal Server Error', 'HTTPException'],
            'severity': 'CRITICAL',
            'likely_cause': 'Unhandled exception in endpoint',
            'fix_location': 'main.py /api/calculate-score endpoint (lines 2115-2328)'
        },
        'timeout': {
            'patterns': ['TimeoutError', 'timeout', 'timed out'],
            'severity': 'HIGH',
            'likely_cause': 'Job description too complex, embeddings too slow',
            'fix_location': 'embeddings.py or increase timeout'
        },
        'pydantic_validation': {
            'patterns': ['ValidationError', 'field required', 'validation error'],
            'severity': 'HIGH',
            'likely_cause': 'Parsed JD missing required fields',
            'fix_location': 'Parsing endpoint or Pydantic models'
        },
        'none_comparison': {
            'patterns': ['NoneType', "not supported between instances of 'NoneType'"],
            'severity': 'HIGH',
            'likely_cause': 'Parsed JD has None values for required fields',
            'fix_location': 'main.py experience comparison or similar logic'
        },
        'embedding_error': {
            'patterns': ['embedding', 'vector', 'dimension'],
            'severity': 'MEDIUM',
            'likely_cause': 'Embedding generation failed',
            'fix_location': 'embeddings.py get_embedding function'
        },
        'rate_limit': {
            'patterns': ['rate limit', '429', 'too many requests'],
            'severity': 'MEDIUM',
            'likely_cause': 'API rate limit exceeded',
            'fix_location': 'Add rate limiting or wait between requests'
        }
    }

    @classmethod
    def classify(cls, error_type: str, error_message: str) -> Dict:
        """
        Classify error and provide debugging hints.

        Args:
            error_type: Type of error (e.g., 'score_calculation_failed')
            error_message: Error message text

        Returns:
            Dictionary with category, severity, likely cause, and fix location
        """
        error_str = str(error_message).lower()

        for category, info in cls.ERROR_CATEGORIES.items():
            if any(pattern.lower() in error_str for pattern in info['patterns']):
                return {
                    'category': category,
                    'severity': info['severity'],
                    'likely_cause': info['likely_cause'],
                    'fix_location': info['fix_location'],
                    'error_type': error_type,
                    'error_message': error_message
                }

        return {
            'category': 'unknown',
            'severity': 'MEDIUM',
            'likely_cause': 'Unclassified error',
            'fix_location': 'Review full traceback',
            'error_type': error_type,
            'error_message': error_message
        }

    @classmethod
    def get_severity_color(cls, severity: str) -> str:
        """Get ANSI color code for severity level."""
        colors = {
            'CRITICAL': '\033[91m',  # Red
            'HIGH': '\033[93m',      # Yellow
            'MEDIUM': '\033[94m',    # Blue
            'LOW': '\033[92m',       # Green
        }
        return colors.get(severity, '\033[0m')  # Default: reset

    @classmethod
    def format_error_report(cls, error_info: Dict) -> str:
        """
        Format error information for console display.

        Args:
            error_info: Dictionary from classify()

        Returns:
            Formatted error report string
        """
        color = cls.get_severity_color(error_info['severity'])
        reset = '\033[0m'

        report = f"""
{color}[{error_info['severity']}] {error_info['category'].upper()}{reset}
  Error Type: {error_info['error_type']}
  Likely Cause: {error_info['likely_cause']}
  Fix Location: {error_info['fix_location']}
  Message: {error_info['error_message'][:200]}...
"""
        return report
