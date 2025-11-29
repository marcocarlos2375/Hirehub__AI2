"""
AI-powered search query generation for optimal learning resource discovery.
Uses LLM to craft smart search queries tailored to user needs.
"""
import json
from typing import Dict, Any, List
from datetime import datetime
from core.langchain_config import get_langchain_config


class SearchQueryBuilder:
    """Generate optimized search queries using AI."""

    def __init__(self):
        """Initialize with LLM from LangChain config."""
        config = get_langchain_config()
        self.llm = config.llm_fast  # Use fast model for query generation

    def generate_queries(
        self,
        gap: Dict[str, Any],
        user_level: str,
        num_queries: int = 3
    ) -> List[str]:
        """
        Generate multiple optimized search queries for a skill gap.

        Args:
            gap: Skill gap info with title and description
            user_level: User's experience level (beginner/intermediate/advanced)
            num_queries: Number of queries to generate (default: 3)

        Returns:
            List of optimized search query strings
        """
        gap_title = gap.get("title", "")
        gap_description = gap.get("description", "")
        current_year = datetime.now().year

        prompt = f"""Generate {num_queries} optimized search queries to find high-quality learning resources on the web.

Skill Gap: {gap_title}
Description: {gap_description}
User Level: {user_level}
Current Year: {current_year}

Requirements for each query:
1. ALWAYS include educational keywords: "course", "tutorial", "learn", or "bootcamp"
2. For programming languages (Rust, Python, Go, etc.), ALWAYS add "programming course" or "tutorial"
3. Add year "{current_year}" or "2025" for fresh, up-to-date content
4. Use site: filters to target trusted learning platforms (coursera.org, udemy.com, edx.org, linkedin.com/learning)
5. Vary queries to cover different resource types:
   - Query 1: Focus on courses (Coursera, edX, Udacity)
   - Query 2: Focus on tutorials/bootcamps (Udemy, LinkedIn Learning)
   - Query 3: Focus on specialized platforms (AWS Training, Google Career Certificates)

CRITICAL: Generic terms like "Rust", "Go", "Python" MUST include "course" or "tutorial" to signal educational intent!

Output ONLY a JSON array of strings, nothing else:
["query 1", "query 2", "query 3"]

Example for "React" beginner:
[
  "React beginner course 2025 site:coursera.org OR site:edx.org",
  "React programming tutorial {user_level} site:udemy.com OR site:linkedin.com",
  "learn React from scratch {current_year} site:aws.amazon.com OR site:grow.google"
]

Example for "Rust" beginner:
[
  "Rust programming course beginner 2025 site:coursera.org OR site:edx.org",
  "Rust tutorial hands-on project {user_level} site:udacity.com OR site:linkedin.com",
  "learn Rust from scratch {current_year} site:training.linuxfoundation.org"
]

Generate {num_queries} queries for {gap_title} ({user_level} level):"""

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()

            # Remove markdown code blocks if present
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1] if len(lines) > 2 else lines)

            # Parse JSON array
            queries = json.loads(content)

            if isinstance(queries, list) and len(queries) > 0:
                return queries[:num_queries]
            else:
                # Fallback to simple query
                return [self._fallback_query(gap_title, user_level)]

        except json.JSONDecodeError as e:
            print(f"Query generation JSON parse error: {str(e)}")
            print(f"Response content: {content[:200]}")
            return [self._fallback_query(gap_title, user_level)]
        except Exception as e:
            print(f"Query generation error: {str(e)}")
            return [self._fallback_query(gap_title, user_level)]

    def _fallback_query(self, skill: str, level: str) -> str:
        """
        Generate a simple fallback query when AI generation fails.

        Args:
            skill: Skill/technology name
            level: User experience level

        Returns:
            Simple search query string
        """
        current_year = datetime.now().year

        # Detect if this is a programming language (generic term that needs educational context)
        programming_languages = {
            'rust', 'python', 'go', 'java', 'javascript', 'typescript',
            'c++', 'c#', 'csharp', 'ruby', 'php', 'swift', 'kotlin', 'scala',
            'perl', 'r', 'julia', 'haskell', 'elixir', 'dart', 'lua',
            'objective-c', 'assembly', 'fortran', 'cobol', 'lisp', 'erlang'
        }

        skill_lower = skill.lower()
        is_programming_language = any(lang in skill_lower for lang in programming_languages)

        if is_programming_language:
            # For programming languages, ALWAYS add "course" to signal educational intent
            return f"{skill} programming course {level} {current_year} site:coursera.org OR site:udemy.com OR site:edx.org"
        else:
            # For other skills, use generic query
            return f"{skill} {level} course tutorial {current_year} site:udemy.com OR site:coursera.org OR site:freecodecamp.org"

    def generate_single_query(
        self,
        gap: Dict[str, Any],
        user_level: str,
        query_type: str = "general"
    ) -> str:
        """
        Generate a single optimized query for a specific resource type.

        Args:
            gap: Skill gap information
            user_level: User's experience level
            query_type: Type of resources to target
                       ("courses", "tutorials", "videos", "projects", "general")

        Returns:
            Single optimized search query
        """
        gap_title = gap.get("title", "")
        current_year = datetime.now().year

        # Platform mappings for different query types
        platforms = {
            "courses": "site:udemy.com OR site:coursera.org OR site:pluralsight.com OR site:linkedin.com/learning",
            "tutorials": "site:freecodecamp.org OR site:dev.to OR site:medium.com OR site:css-tricks.com",
            "videos": "site:youtube.com OR site:egghead.io OR site:frontendmasters.com",
            "projects": "site:github.com OR site:freecodecamp.org OR site:realpython.com",
            "general": "site:udemy.com OR site:coursera.org OR site:freecodecamp.org OR site:youtube.com"
        }

        platform_filter = platforms.get(query_type, platforms["general"])

        # Construct query
        query = f"{gap_title} {user_level} {query_type if query_type != 'general' else 'course tutorial'} {current_year} {platform_filter}"

        return query


# Singleton instance
_query_builder = None

def get_query_builder() -> SearchQueryBuilder:
    """
    Get or create query builder singleton.

    Returns:
        SearchQueryBuilder instance
    """
    global _query_builder
    if _query_builder is None:
        _query_builder = SearchQueryBuilder()
    return _query_builder
