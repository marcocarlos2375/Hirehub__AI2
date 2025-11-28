"""
Learning Resource Matcher with Semantic Search.
Finds relevant courses, projects, and certifications for skill gaps using vector similarity.
"""

from typing import List, Dict, Any, Optional, Literal
from datetime import datetime, timedelta
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, Session
import os

from core.langchain_config import get_learning_resources_vectorstore, get_embeddings
from core.perplexica_client import get_perplexica_client
from models.learning_resources import LearningResource, UserLearningPlan, Base


class ResourceMatcher:
    """
    Matches learning resources to skill gaps using:
    1. Semantic search (vector similarity)
    2. Rule-based filtering (duration, cost, difficulty)
    3. Personalized ranking based on user level
    """

    def __init__(self, db_url: Optional[str] = None):
        """
        Initialize resource matcher.

        Args:
            db_url: PostgreSQL connection string. If None, uses env var DATABASE_URL
        """
        self.vectorstore = get_learning_resources_vectorstore()
        self.embeddings = get_embeddings()

        # Database connection
        if db_url is None:
            db_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/hirehub")

        self.engine = create_engine(db_url)
        SessionLocal = sessionmaker(bind=self.engine)
        self.db: Session = SessionLocal()

    def find_resources(
        self,
        gap: Dict[str, Any],
        user_level: Literal["beginner", "intermediate", "advanced"] = "intermediate",
        max_days: int = 10,
        cost_preference: Literal["free", "paid", "any"] = "any",
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Find learning resources for a specific gap.

        Args:
            gap: Gap information with title, description, required skills
            user_level: User's current skill level
            max_days: Maximum duration in days
            cost_preference: Cost filter
            limit: Maximum number of resources to return

        Returns:
            Dictionary with resources and learning path timeline
        """
        # Build search query
        gap_title = gap.get("title", "")
        gap_description = gap.get("description", "")
        required_skills = gap.get("required", "")

        search_query = f"{gap_title}: {gap_description}. Required skills: {required_skills}"

        try:
            # Vector search (get more candidates for post-filtering)
            docs = self.vectorstore.similarity_search(
                search_query,
                k=limit * 4  # Get more candidates for filtering
            )

            # Convert to structured format and apply filters
            resources = []
            for doc in docs:
                metadata = doc.metadata

                # Apply filters
                duration = metadata.get("duration_days", 0)
                cost = metadata.get("cost", "")

                # Filter by max_days
                if duration > max_days:
                    continue

                # Filter by cost preference
                if cost_preference != "any" and cost != cost_preference:
                    # Allow "free" preference to also include "freemium"
                    if not (cost_preference == "free" and cost == "freemium"):
                        continue

                resource = {
                    "id": metadata.get("id"),
                    "title": metadata.get("title"),
                    "description": doc.page_content,
                    "type": metadata.get("type"),
                    "provider": metadata.get("provider"),
                    "url": metadata.get("url"),
                    "duration_days": duration,
                    "difficulty": metadata.get("difficulty"),
                    "cost": cost,
                    "skills_covered": metadata.get("skills_covered", []),
                    "rating": metadata.get("rating"),
                    "completion_certificate": metadata.get("completion_certificate", False),
                }
                resources.append(resource)

            # Rank resources
            ranked_resources = self._rank_resources(resources, user_level, gap)

            # Take top N
            top_resources = ranked_resources[:limit]

            # Generate learning path
            learning_path = self._generate_learning_path(top_resources, max_days)

            return {
                "resources": top_resources,
                "learning_path": learning_path,
                "total_resources": len(top_resources),
                "total_duration_days": learning_path["total_days"],
                "estimated_completion": learning_path["estimated_completion"]
            }

        except Exception as e:
            print(f"Error finding resources: {str(e)}")
            return {
                "resources": [],
                "learning_path": {},
                "total_resources": 0,
                "total_duration_days": 0,
                "error": str(e)
            }

    def _rank_resources(
        self,
        resources: List[Dict[str, Any]],
        user_level: str,
        gap: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Rank resources based on relevance, difficulty match, and quality.

        Ranking factors:
        - Difficulty match (beginner → beginner/intermediate, etc.)
        - Rating (higher is better)
        - Type diversity (prefer mix of course + project)
        - Completion certificate (bonus for certifications)
        """
        scored_resources = []

        for resource in resources:
            score = 0.0

            # Difficulty match (30 points)
            difficulty = resource.get("difficulty", "intermediate")
            if difficulty == user_level:
                score += 30
            elif (user_level == "beginner" and difficulty == "intermediate") or \
                 (user_level == "advanced" and difficulty == "intermediate"):
                score += 20
            else:
                score += 10

            # Rating (25 points)
            rating = resource.get("rating", 0)
            if rating:
                score += (rating / 5.0) * 25

            # Type diversity (20 points)
            resource_type = resource.get("type", "")
            if resource_type == "project":
                score += 20  # Prefer hands-on projects
            elif resource_type == "course":
                score += 18
            elif resource_type == "certification":
                score += 15

            # Completion certificate (15 points)
            if resource.get("completion_certificate"):
                score += 15

            # Cost (10 points - free is better)
            cost = resource.get("cost", "paid")
            if cost == "free":
                score += 10
            elif cost == "freemium":
                score += 5

            scored_resources.append({
                **resource,
                "_score": score
            })

        # Sort by score descending
        scored_resources.sort(key=lambda x: x["_score"], reverse=True)

        # Remove score from output
        for r in scored_resources:
            r.pop("_score", None)

        return scored_resources

    def _generate_learning_path(
        self,
        resources: List[Dict[str, Any]],
        max_days: int
    ) -> Dict[str, Any]:
        """
        Generate a timeline for the learning path.

        Strategy:
        1. Start with a course (theory/foundation)
        2. Follow with a project (hands-on practice)
        3. Optionally add certification (validation)
        """
        timeline = []
        current_day = 1
        total_days = 0

        # Separate by type
        courses = [r for r in resources if r["type"] == "course"]
        projects = [r for r in resources if r["type"] == "project"]
        certifications = [r for r in resources if r["type"] == "certification"]

        # Add first course
        if courses:
            course = courses[0]
            duration = course["duration_days"]
            timeline.append({
                "resource_id": course["id"],
                "resource_title": course["title"],
                "type": "course",
                "start_day": current_day,
                "end_day": current_day + duration - 1,
                "duration_days": duration
            })
            current_day += duration
            total_days += duration

        # Add first project
        if projects and (current_day + projects[0]["duration_days"] - 1) <= max_days:
            project = projects[0]
            duration = project["duration_days"]
            timeline.append({
                "resource_id": project["id"],
                "resource_title": project["title"],
                "type": "project",
                "start_day": current_day,
                "end_day": current_day + duration - 1,
                "duration_days": duration
            })
            current_day += duration
            total_days += duration

        # Add certification if time allows
        if certifications and (current_day + certifications[0]["duration_days"] - 1) <= max_days:
            cert = certifications[0]
            duration = cert["duration_days"]
            timeline.append({
                "resource_id": cert["id"],
                "resource_title": cert["title"],
                "type": "certification",
                "start_day": current_day,
                "end_day": current_day + duration - 1,
                "duration_days": duration
            })
            total_days += duration

        # Calculate estimated completion date
        estimated_completion = (datetime.now() + timedelta(days=total_days)).date().isoformat()

        return {
            "timeline": timeline,
            "total_days": total_days,
            "estimated_completion": estimated_completion,
            "resources_in_path": len(timeline)
        }

    def save_learning_plan(
        self,
        user_id: str,
        gap: Dict[str, Any],
        resource_ids: List[str],
        notes: Optional[str] = None
    ) -> str:
        """
        Save a learning plan to the database.

        Args:
            user_id: User identifier
            gap: Gap information
            resource_ids: List of selected resource IDs
            notes: Optional user notes

        Returns:
            Created learning plan ID
        """
        try:
            # Create learning plan
            plan = UserLearningPlan(
                user_id=user_id,
                gap_id=gap.get("id"),
                gap_title=gap.get("title"),
                gap_description=gap.get("description"),
                resource_ids=resource_ids,
                status="suggested",
                notes=notes
            )

            self.db.add(plan)
            self.db.commit()
            self.db.refresh(plan)

            return str(plan.id)

        except Exception as e:
            self.db.rollback()
            print(f"Error saving learning plan: {str(e)}")
            raise

    def get_user_learning_plans(
        self,
        user_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all learning plans for a user.

        Args:
            user_id: User identifier
            status: Optional status filter

        Returns:
            List of learning plans
        """
        try:
            query = self.db.query(UserLearningPlan).filter(
                UserLearningPlan.user_id == user_id
            )

            if status:
                query = query.filter(UserLearningPlan.status == status)

            plans = query.order_by(UserLearningPlan.created_at.desc()).all()

            return [plan.to_dict() for plan in plans]

        except Exception as e:
            print(f"Error getting learning plans: {str(e)}")
            return []

    def get_learning_plan_details(
        self,
        plan_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a learning plan including resources.

        Args:
            plan_id: Learning plan ID

        Returns:
            Learning plan with populated resource details
        """
        try:
            plan = self.db.query(UserLearningPlan).filter(
                UserLearningPlan.id == plan_id
            ).first()

            if not plan:
                return None

            # Get resources
            resource_ids = plan.resource_ids
            resources = self.db.query(LearningResource).filter(
                LearningResource.id.in_(resource_ids)
            ).all()

            plan_dict = plan.to_dict()
            plan_dict["resources"] = [r.to_dict() for r in resources]

            return plan_dict

        except Exception as e:
            print(f"Error getting plan details: {str(e)}")
            return None

    def update_plan_status(
        self,
        plan_id: str,
        status: str
    ) -> bool:
        """
        Update learning plan status.

        Args:
            plan_id: Learning plan ID
            status: New status (suggested, in_progress, completed, abandoned)

        Returns:
            True if successful
        """
        try:
            plan = self.db.query(UserLearningPlan).filter(
                UserLearningPlan.id == plan_id
            ).first()

            if not plan:
                return False

            plan.status = status

            if status == "completed":
                plan.completed_at = datetime.utcnow()

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            print(f"Error updating plan status: {str(e)}")
            return False

    def find_resources_with_web_search(
        self,
        gap: Dict[str, Any],
        user_level: str = "beginner",
        max_days: int = 30,
        cost_preference: str = "any",
        limit: int = 5,
        search_mode: str = "perplexica"  # Changed default to perplexica
    ) -> Dict[str, Any]:
        """
        Find resources using hybrid approach: local DB + web search via SearXNG or Perplexica AI.

        Args:
            gap: Gap information (title, description)
            user_level: User's skill level
            max_days: Maximum duration in days
            cost_preference: Cost filter (free, freemium, paid, any)
            limit: Number of results to return
            search_mode: Search strategy ("local_only", "web_only", "hybrid", "perplexica")

        Returns:
            Dictionary with resources, learning_path, and metadata
        """
        from core.searxng_client import get_searxng_client
        from core.search_query_builder import get_query_builder

        all_resources = []
        sources_used = []

        # 1. Local database search (if not web_only)
        if search_mode in ["local_only", "hybrid"]:
            try:
                local_results = self.find_resources(gap, user_level, max_days, cost_preference, limit)
                local_resources = local_results.get("resources", [])

                # Mark as local source
                for r in local_resources:
                    r["source"] = "local"
                    r["source_badge"] = "Curated"
                    r["confidence"] = "verified"

                all_resources.extend(local_resources)
                if local_resources:
                    sources_used.append("local_database")

            except Exception as e:
                print(f"Local search error: {str(e)}")

        # 2. Web search via SearXNG (if not local_only)
        if search_mode in ["web_only", "hybrid"]:
            try:
                searxng = get_searxng_client()

                # Check if SearXNG is healthy
                if not searxng.health_check():
                    print("SearXNG not available, skipping web search")
                else:
                    # Generate optimized queries using AI
                    query_builder = get_query_builder()
                    queries = query_builder.generate_queries(gap, user_level, num_queries=2)

                    # Search with each query
                    web_results = []
                    for query in queries:
                        results = searxng.search(
                            query=query,
                            num_results=limit * 2
                        )
                        web_results.extend(results)

                    if web_results:
                        sources_used.append("searxng_web")

                    # Parse web results into resource format
                    parsed_web = self._parse_web_results(web_results, user_level, max_days, cost_preference)
                    all_resources.extend(parsed_web)

            except Exception as e:
                print(f"Web search error: {str(e)}")

        # 2.5. Perplexica AI Search (new mode)
        if search_mode == "perplexica":
            try:
                use_perplexica = os.getenv("USE_PERPLEXICA", "true").lower() == "true"

                if use_perplexica:
                    perplexica = get_perplexica_client()

                    # Check health before using
                    if perplexica.health_check():
                        perplexica_result = perplexica.search_learning_resources(
                            skill=gap.get("title", ""),
                            user_level=user_level,
                            num_results=limit * 2
                        )

                        # Parse Perplexica results
                        parsed_perplexica = self._parse_perplexica_results(
                            perplexica_result,
                            max_days,
                            cost_preference
                        )
                        all_resources.extend(parsed_perplexica)

                        if parsed_perplexica:
                            sources_used.append("Perplexica")

                        print(f"Perplexica returned {len(parsed_perplexica)} resources")
                    else:
                        print("Perplexica health check failed, falling back to SearXNG")
                        # Fallback to SearXNG
                        search_mode = "web_only"
                else:
                    print("USE_PERPLEXICA=false, using SearXNG")
                    search_mode = "web_only"

            except Exception as e:
                print(f"Perplexica error: {e}, falling back to SearXNG")
                search_mode = "web_only"

            # If fallback triggered, run SearXNG search
            if search_mode == "web_only":
                try:
                    searxng = get_searxng_client()
                    if searxng.health_check():
                        query_builder = get_query_builder()
                        queries = query_builder.generate_queries(gap, user_level, num_queries=2)

                        web_results = []
                        for query in queries:
                            results = searxng.search(query=query, num_results=limit * 2)
                            web_results.extend(results)

                        if web_results:
                            sources_used.append("searxng_web_fallback")

                        parsed_web = self._parse_web_results(web_results, user_level, max_days, cost_preference)
                        all_resources.extend(parsed_web)
                except Exception as e:
                    print(f"Fallback search error: {str(e)}")

        # 3. Deduplicate by URL
        seen_urls = set()
        unique_resources = []
        for r in all_resources:
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_resources.append(r)

        # 4. Rank all resources together
        ranked = self._rank_resources(unique_resources, user_level, gap)

        # 5. Take top N
        top_resources = ranked[:limit]

        # 6. Generate learning path
        learning_path = self._generate_learning_path(top_resources, max_days)

        return {
            "resources": top_resources,
            "learning_path": learning_path,
            "total_resources": len(top_resources),
            "total_duration_days": learning_path.get("total_days", 0),
            "estimated_completion": learning_path.get("estimated_completion"),
            "sources_used": sources_used,
            "search_mode": search_mode
        }

    def _parse_web_results(
        self,
        web_results: List[Dict],
        user_level: str,
        max_days: int,
        cost_preference: str
    ) -> List[Dict[str, Any]]:
        """
        Parse SearXNG results into resource format with AI metadata estimation.

        Args:
            web_results: Raw results from SearXNG
            user_level: User's skill level
            max_days: Maximum duration filter
            cost_preference: Cost preference filter

        Returns:
            List of parsed resources with estimated metadata
        """
        from core.langchain_config import get_langchain_config

        parsed = []
        llm = get_langchain_config().llm_fast

        for result in web_results:
            title = result.get("title", "")
            url = result.get("url", "")
            description = result.get("description", "")

            if not url or not title:
                continue

            # Extract provider from URL
            provider = self._extract_provider(url)

            # Use AI to estimate metadata
            metadata = self._estimate_metadata(title, description, url, user_level, llm)

            # Apply filters
            duration = metadata.get("duration_days", 5)
            cost = metadata.get("cost", "unknown")

            # Filter by max_days
            if duration > max_days:
                continue

            # Filter by cost preference
            if cost_preference != "any":
                if cost_preference == "free" and cost not in ["free", "freemium"]:
                    continue
                elif cost_preference != "free" and cost != cost_preference:
                    continue

            resource = {
                "id": f"web_{hash(url) % 1000000}",
                "title": title,
                "description": description[:200],
                "url": url,
                "provider": provider,
                "source": "searxng",
                "source_badge": "Web",
                "confidence": metadata.get("confidence", "medium"),
                "type": metadata.get("type", "course"),
                "difficulty": metadata.get("difficulty", user_level),
                "duration_days": duration,
                "cost": cost,
                "rating": metadata.get("rating", 0),
                "skills_covered": [],
                "completion_certificate": metadata.get("certificate", False)
            }

            parsed.append(resource)

        return parsed

    def _extract_provider(self, url: str) -> str:
        """Extract provider name from URL."""
        providers = {
            # Technology & Software Development
            "udemy.com": "Udemy",
            "coursera.org": "Coursera",
            "freecodecamp.org": "freeCodeCamp",
            "youtube.com": "YouTube",
            "github.com": "GitHub",
            "pluralsight.com": "Pluralsight",
            "linkedin.com": "LinkedIn Learning",
            "medium.com": "Medium",
            "dev.to": "Dev.to",
            "edx.org": "edX",
            "udacity.com": "Udacity",
            "codecademy.com": "Codecademy",
            "skillshare.com": "Skillshare",
            "egghead.io": "Egghead",
            "frontendmasters.com": "Frontend Masters",
            "treehouse.com": "Treehouse",
            "datacamp.com": "DataCamp",
            "kaggle.com": "Kaggle",

            # Medical & Healthcare
            "khanacademy.org": "Khan Academy",
            "medscape.com": "Medscape",
            "uptodate.com": "UpToDate",
            "bmj.com": "BMJ Learning",
            "nejm.org": "NEJM",
            "osmosis.org": "Osmosis",
            "lecturio.com": "Lecturio Medical",
            "amboss.com": "AMBOSS",
            "healthstream.com": "HealthStream",
            "nurse.com": "Nurse.com",
            "medlineplus.gov": "MedlinePlus",
            "cdc.gov": "CDC",
            "nih.gov": "NIH",

            # Logistics & Supply Chain
            "apics.org": "APICS",
            "cscmp.org": "CSCMP",
            "logisticsmgmt.com": "Logistics Management",
            "supplychainbrain.com": "Supply Chain Brain",
            "inboundlogistics.com": "Inbound Logistics",
            "supplychaindive.com": "Supply Chain Dive",
            "asq.org": "ASQ",
            "iise.org": "IISE",

            # Business & Management
            "hbr.org": "Harvard Business Review",
            "wharton.upenn.edu": "Wharton Online",
            "businessinsider.com": "Business Insider",
            "ted.com": "TED",
            "masterclass.com": "MasterClass",
            "investopedia.com": "Investopedia",
            "entrepreneur.com": "Entrepreneur",
            "inc.com": "Inc. Magazine",
            "forbes.com": "Forbes",
            "pmi.org": "PMI",
            "asana.com": "Asana",

            # Academic & Research
            "ocw.mit.edu": "MIT OpenCourseWare",
            "academicearth.org": "Academic Earth",
            "oyc.yale.edu": "Open Yale Courses",
            "open.edu": "Open University",
            "futurelearn.com": "FutureLearn",
            "alison.com": "Alison",
            "openculture.com": "Open Culture",
            "class-central.com": "Class Central",
            "stanford.edu": "Stanford Online",
            "harvard.edu": "Harvard Online",
            "berkeley.edu": "UC Berkeley",

            # Professional Certifications
            "comptia.org": "CompTIA",
            "shrm.org": "SHRM",
            "aia.org": "AIA",
            "iiba.org": "IIBA",
            "isaca.org": "ISACA",
            "isc2.org": "ISC2",
            "axelos.com": "AXELOS",

            # Language Learning
            "duolingo.com": "Duolingo",
            "babbel.com": "Babbel",
            "rosettastone.com": "Rosetta Stone",
            "busuu.com": "Busuu",
            "memrise.com": "Memrise",

            # Science & Engineering
            "brilliant.org": "Brilliant",
            "brightstorm.com": "Brightstorm",
            "phys.org": "Phys.org",
            "sciencedirect.com": "ScienceDirect",
            "nature.com": "Nature",
            "ieee.org": "IEEE",

            # Finance & Accounting
            "cpa.com": "CPA",
            "aicpa.org": "AICPA",
            "cfainstitute.org": "CFA Institute",
            "investopedia.com": "Investopedia Academy",

            # Legal & Law
            "law.cornell.edu": "Cornell Law",
            "justia.com": "Justia",
            "aba.org": "ABA",

            # Design & Creative
            "domestika.com": "Domestika",
            "creativelive.com": "CreativeLive",
            "lynda.com": "Lynda",
            "canva.com": "Canva Design School",
            "behance.net": "Behance",
            "dribbble.com": "Dribbble",

            # General Education
            "coursesites.com": "CourseSites",
            "studyportals.com": "Study Portals",
            "mooc-list.com": "MOOC List",
            "openlearn.com": "OpenLearn",
            "saylor.org": "Saylor Academy",

            # Professional Development
            "toastmasters.org": "Toastmasters",
            "skillsoft.com": "Skillsoft",
            "udemy.com": "Udemy Business",
            "goconqr.com": "GoConqr",
            "mindtools.com": "Mind Tools"
        }

        url_lower = url.lower()
        for domain, name in providers.items():
            if domain in url_lower:
                return name

        return "Web"

    def _parse_perplexica_results(
        self,
        perplexica_result: Dict[str, Any],
        max_days: int,
        cost_preference: str
    ) -> List[Dict[str, Any]]:
        """
        Parse Perplexica AI-synthesized results into resource format.

        Args:
            perplexica_result: Result from Perplexica with 'answer' and 'sources'
            max_days: Maximum duration filter
            cost_preference: Cost preference filter

        Returns:
            List of parsed resources from Perplexica sources
        """
        from core.langchain_config import get_langchain_config

        parsed = []
        sources = perplexica_result.get("sources", [])
        ai_answer = perplexica_result.get("answer", "")

        if not sources:
            return parsed

        llm = get_langchain_config().llm_fast

        for source in sources:
            # Perplexica sources have nested structure: metadata.title and metadata.url
            source_metadata = source.get("metadata", {})
            title = source_metadata.get("title", "")
            url = source_metadata.get("url", "")

            # Get page content for additional context
            page_content = source.get("pageContent", "")

            if not url or not title:
                continue

            # Extract provider from URL
            provider = self._extract_provider(url)

            # Skip forums and discussion platforms - prioritize learning platforms
            forum_domains = [
                'reddit.com', 'facebook.com', 'stackoverflow.com',
                'quora.com', 'discourse.org', 'github.com/issues',
                'dev.to', 'hashnode.com', 'medium.com/@'  # Skip personal blog posts
            ]
            if any(domain in url.lower() for domain in forum_domains):
                continue

            # Use Perplexica's AI context + source info to estimate metadata
            # Combine page content and AI answer for richer context
            context_description = f"{page_content}\n\nAI Context: {ai_answer[:300]}"

            # Use AI to estimate resource metadata with Perplexica context
            resource_metadata = self._estimate_metadata(title, context_description, url, "beginner", llm)

            # Apply filters
            duration = resource_metadata.get("duration_days", 5)
            cost = resource_metadata.get("cost", "unknown")

            # Filter by max_days
            if duration > max_days:
                continue

            # Filter by cost preference
            if cost_preference != "any":
                if cost_preference == "free" and cost not in ["free", "freemium"]:
                    continue
                elif cost_preference != "free" and cost != cost_preference:
                    continue

            resource = {
                "id": f"perplexica_{hash(url) % 1000000}",
                "title": title,
                "description": page_content[:200] if page_content else ai_answer[:200],
                "url": url,
                "provider": provider,
                "source": "perplexica",
                "source_badge": "AI Search",
                "confidence": "high",  # Perplexica uses AI synthesis, higher confidence
                "type": resource_metadata.get("type", "course"),
                "difficulty": resource_metadata.get("difficulty", "beginner"),
                "duration_days": duration,
                "cost": cost,
                "rating": resource_metadata.get("rating", 4.2),  # Slightly higher default for AI-curated
                "skills_covered": [],
                "completion_certificate": resource_metadata.get("certificate", False),
                "ai_summary": ai_answer[:300]  # Include AI context for this resource
            }

            parsed.append(resource)

        return parsed

    def _estimate_metadata(
        self,
        title: str,
        description: str,
        url: str,
        user_level: str,
        llm
    ) -> Dict[str, Any]:
        """
        Use AI to estimate resource metadata from title/description.

        Args:
            title: Resource title
            description: Resource description
            url: Resource URL
            user_level: Target user level
            llm: Language model instance

        Returns:
            Dictionary with estimated metadata
        """
        prompt = f"""Analyze this learning resource and estimate metadata:

Title: {title}
Description: {description}
URL: {url}

Estimate the following and return ONLY valid JSON:
1. type: "course", "tutorial", "project", "video", or "documentation"
2. difficulty: "beginner", "intermediate", or "advanced"
3. duration_days: Estimated days to complete (1-30)
4. cost: "free", "freemium", or "paid" (check title/URL for keywords)
5. rating: Estimated quality 0-5 (default 4.0)
6. certificate: true if completion certificate mentioned, false otherwise
7. confidence: "high", "medium", or "low" based on available info

Return only this JSON:
{{"type": "course", "difficulty": "beginner", "duration_days": 5, "cost": "free", "rating": 4.0, "certificate": false, "confidence": "medium"}}
"""

        try:
            response = llm.invoke(prompt)
            content = response.content.strip()

            # Remove markdown if present
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1] if len(lines) > 2 else lines)

            import json
            metadata = json.loads(content)
            return metadata
        except Exception as e:
            print(f"Metadata estimation error: {str(e)}")
            # Fallback defaults
            return {
                "type": "course",
                "difficulty": user_level,
                "duration_days": 5,
                "cost": "unknown",
                "rating": 4.0,
                "certificate": False,
                "confidence": "low"
            }


# Singleton instance
_matcher = None


def get_resource_matcher() -> ResourceMatcher:
    """Get singleton resource matcher instance."""
    global _matcher
    if _matcher is None:
        _matcher = ResourceMatcher()
    return _matcher


# Convenience functions
def find_resources_for_gap(gap: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Find resources for a gap."""
    matcher = get_resource_matcher()
    return matcher.find_resources(gap, **kwargs)


def save_user_learning_plan(user_id: str, gap: Dict[str, Any], resource_ids: List[str]) -> str:
    """Save a learning plan."""
    matcher = get_resource_matcher()
    return matcher.save_learning_plan(user_id, gap, resource_ids)
