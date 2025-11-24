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
1. Include skill name + user level + resource type (course/tutorial/project)
2. Add year "{current_year}" or "2025" for fresh, up-to-date content
3. Use site: filters to target trusted learning platforms
4. Vary queries to cover different resource types:
   - Query 1: Focus on courses (Udemy, Coursera, Pluralsight)
   - Query 2: Focus on tutorials/projects (freeCodeCamp, Dev.to, Medium)
   - Query 3: Focus on videos/docs (YouTube, official documentation)

Output ONLY a JSON array of strings, nothing else:
["query 1", "query 2", "query 3"]

Example for "React" beginner:
[
  "React beginner course 2025 site:udemy.com OR site:coursera.org",
  "React tutorial hands-on project beginner site:freecodecamp.org OR site:dev.to",
  "React complete guide beginner {current_year} site:youtube.com"
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
