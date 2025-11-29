"""
Node implementations for LangGraph adaptive question workflow.
Each node is a function that takes state and returns updated state.
"""

from typing import Dict, Any, List
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from core.langchain_config import get_llm, get_learning_resources_vectorstore
from core.answer_flow_state import (
    AdaptiveAnswerState,
    DeepDivePrompt,
    QualityFeedback,
    MIN_ACCEPTABLE_QUALITY_SCORE,
    MAX_REFINEMENT_ITERATIONS,
    MAX_LEARNING_RESOURCES,
    MAX_LEARNING_DAYS
)


# ========================================
# Pydantic Models for Structured Outputs
# ========================================

class DeepDivePromptsOutput(BaseModel):
    """Structured output for deep dive prompts."""
    prompts: List[Dict[str, Any]] = Field(description="List of structured prompts")


class FeedbackItem(BaseModel):
    """Structured feedback item with label and description."""
    label: str = Field(description="Category label (e.g., 'Relevance', 'Specificity', 'Professional Tone')")
    description: str = Field(description="Detailed description of the feedback")


class ImprovementSuggestion(BaseModel):
    """Structured improvement suggestion with title and examples."""
    type: str = Field(description="Input type: 'text' | 'textarea' | etc.")
    title: str = Field(description="Short action phrase (3-6 words)")
    examples: List[str] = Field(description="Array of concrete example sentences user can copy/adapt")
    help_text: str = Field(description="Brief guidance on what to include")


class QualityEvaluationOutput(BaseModel):
    """Structured output for quality evaluation."""
    quality_score: int = Field(description="Score from 1-10", ge=1, le=10)
    issues: List[FeedbackItem] = Field(description="List of quality issues with labels")
    strengths: List[FeedbackItem] = Field(description="List of strengths with labels")
    suggestions: List[ImprovementSuggestion] = Field(description="Improvement suggestions with title and examples")
    is_acceptable: bool = Field(description="True if score >= 7")


class AnswerGenerationOutput(BaseModel):
    """Structured output for answer generation."""
    professional_answer: str = Field(description="Generated professional answer")
    key_points: List[str] = Field(description="Key points included")


class AnswerRefinementOutput(BaseModel):
    """Structured output for answer refinement."""
    refined_answer: str = Field(description="Improved answer")
    improvements_made: List[str] = Field(description="What was improved")


# ========================================
# Node 1: Generate Deep Dive Prompts
# ========================================

def generate_deep_dive_prompts_node(state: AdaptiveAnswerState) -> AdaptiveAnswerState:
    """
    Generate structured prompts for deep-dive questioning.
    Called when user has experience with the skill.

    Returns prompts like:
    - Where did you use this? (select: Work, Side Project, Course)
    - How long? (text)
    - Which specific tools? (multiselect)
    - What did you achieve? (textarea)
    """
    llm = get_llm("fast")
    parser = JsonOutputParser(pydantic_object=DeepDivePromptsOutput)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert at generating structured interview questions.

Given a gap/skill, generate 4-6 targeted prompts to extract detailed experience.

Gap: {gap_title}
Description: {gap_description}
Question: {question_text}

Generate prompts that:
1. Identify WHERE they used it (work, side project, course, hackathon)
2. Capture DURATION/TIMELINE
3. List SPECIFIC TOOLS/TECHNOLOGIES used
4. Extract ACHIEVEMENTS/RESULTS with metrics if possible
5. Understand DEPTH of knowledge

Return JSON:
{{
  "prompts": [
    {{
      "id": "context",
      "type": "select",
      "question": "Where did you gain this experience?",
      "options": ["Work", "Side Project", "Online Course", "Hackathon", "Personal Learning"],
      "required": true
    }},
    {{
      "id": "duration",
      "type": "text",
      "question": "How long did you work with [skill]?",
      "placeholder": "e.g., 6 months, 2 projects",
      "required": true
    }},
    {{
      "id": "tools",
      "type": "multiselect",
      "question": "Which specific tools/libraries did you use?",
      "options": ["...", "..."],
      "required": false
    }},
    {{
      "id": "achievement",
      "type": "textarea",
      "question": "What specific project/achievement can you describe?",
      "placeholder": "e.g., Built a chatbot that handles 100+ queries daily",
      "required": true,
      "help_text": "Include what you built and the outcome"
    }},
    {{
      "id": "metrics",
      "type": "text",
      "question": "Any measurable impact or results?",
      "placeholder": "e.g., Reduced response time by 60%",
      "required": false
    }}
  ]
}}

{format_instructions}"""),
        ("human", "Generate deep-dive prompts for this gap")
    ])

    chain = prompt | llm | parser

    try:
        result = chain.invoke({
            "gap_title": state["gap_info"]["title"],
            "gap_description": state["gap_info"].get("description", ""),
            "question_text": state["question_text"],
            "format_instructions": parser.get_format_instructions()
        })

        state["current_step"] = "deep_dive"
        # Store prompts in state for frontend to render
        state["structured_inputs"] = {"prompts": result["prompts"]}

        return state
    except Exception as e:
        state["error"] = f"Failed to generate deep dive prompts: {str(e)}"
        return state


# ========================================
# Node 2: Search Learning Resources
# ========================================

def search_learning_resources_node(state: AdaptiveAnswerState) -> AdaptiveAnswerState:
    """
    Search for relevant learning resources using semantic search.
    Called when user doesn't have experience or is willing to learn.
    """
    try:
        vectorstore = get_learning_resources_vectorstore()

        # Build search query from gap
        gap = state["gap_info"]
        search_query = f"{gap['title']}: {gap.get('description', '')}"

        # Semantic search without filters (do post-filtering in Python)
        docs = vectorstore.similarity_search(
            search_query,
            k=MAX_LEARNING_RESOURCES * 2  # Get extra to allow filtering
        )

        # Convert to structured format with post-filtering
        resources = []
        for doc in docs:
            metadata = doc.metadata
            duration = metadata.get("duration_days", 0)

            # Filter by duration in Python
            if duration <= MAX_LEARNING_DAYS:
                resources.append({
                    "id": metadata.get("id"),
                    "title": metadata.get("title"),
                    "description": doc.page_content,
                    "type": metadata.get("type"),
                    "provider": metadata.get("provider"),
                    "url": metadata.get("url"),
                    "duration_days": duration,
                    "difficulty": metadata.get("difficulty"),
                    "cost": metadata.get("cost"),
                    "skills_covered": metadata.get("skills_covered", []),
                    "rating": metadata.get("rating"),
                    "score": None  # Relevance score (not calculated here)
                })

                if len(resources) >= MAX_LEARNING_RESOURCES:
                    break

        state["suggested_resources"] = resources
        state["current_step"] = "resources"

        # Generate timeline suggestion
        total_days = sum(r["duration_days"] for r in resources[:3])  # Top 3
        state["resume_addition"] = f"Currently expanding {gap['title']} expertise through hands-on learning ({total_days}-day program)"

        return state

    except Exception as e:
        state["error"] = f"Failed to search learning resources: {str(e)}"
        # Fallback: suggest "willing to learn" message
        state["resume_addition"] = f"Open to learning {state['gap_info']['title']}"
        state["suggested_resources"] = []
        return state


# ========================================
# Node 3: Generate Professional Answer
# ========================================

def generate_answer_from_inputs_node(state: AdaptiveAnswerState) -> AdaptiveAnswerState:
    """
    Generate professional answer from structured inputs.
    Called after user completes deep-dive prompts.
    """
    llm = get_llm("creative")  # Slightly creative for better writing
    parser = JsonOutputParser(pydantic_object=AnswerGenerationOutput)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert resume writer creating professional experience descriptions in structured format.

Given structured inputs about a candidate's experience, generate a compelling, professional answer.

Gap: {gap_title}
Structured Inputs: {structured_inputs}

FORMAT RULES - Apply based on structured_inputs["context"]:

If context is "Side Project" or "Personal Learning":
  Format as: **[Project Name] ([Tech Stack])**
    * [Build/Development bullet - what was created]
    * [Engineering/Technical bullet - architecture, methods, tools]
    * [Impact/Results bullet - metrics, outcomes, learnings]

  Example:
  **Sentiment Analysis Tool for Personal Blog (Python, ML)**
    * Built and deployed a sentiment analysis system using pre-trained BERT model from Hugging Face Transformers, analyzing 500 web-scraped blog posts to categorize content and drive sentiment-based recommendations.
    * Engineered data preprocessing pipeline with SMOTE for handling imbalanced classes, achieving 10% accuracy improvement in minority class identification; deployed on Raspberry Pi with automated cron jobs (24h refresh) and matplotlib visualization dashboards.
    * Increased blog engagement by 15% (measured by average comment count) through intelligent content suggestions based on sentiment trends.

If context is "Work":
  Format as: **[Initiative/System Name] at [Company]**
    * [Leadership/Ownership bullet]
    * [Technical implementation bullet]
    * [Business impact bullet with metrics]

  Example:
  **Microservices Architecture Migration at TechCorp**
    * Led cross-functional team of 8 engineers in migrating monolithic application to microservices architecture using Docker, Kubernetes, and AWS ECS.
    * Designed and implemented 12 loosely-coupled services with RESTful APIs, message queues (RabbitMQ), and centralized logging (ELK stack).
    * Reduced deployment time by 70% (from 2 hours to 25 minutes) and improved system reliability to 99.9% uptime.

If context is "Hackathon":
  Format as: **[Project Name] - [Hackathon Name] ([Tech Stack])**
    * [What was built in timeframe]
    * [Technical challenges solved]
    * [Awards/recognition or technical achievement]

  Example:
  **AI Recipe Generator - TechCrunch Disrupt Hackathon (Python, GPT-4)**
    * Built a recipe generation app in 48 hours using GPT-4 API, analyzing user dietary restrictions and ingredient availability to create personalized recipes.
    * Implemented real-time ingredient substitution algorithm and nutritional analysis using USDA Food Database API.
    * Awarded "Best Use of AI" among 120+ teams and gained 500+ beta signups during demo presentation.

If context is "Online Course" or "Certification":
  Format as: **[Course/Certification Name]**
    * [Skills/topics covered]
    * [Hands-on projects completed]
    * [Practical application]

  Example:
  **AWS Solutions Architect Professional Certification**
    * Completed advanced training covering cloud architecture patterns, security best practices, and cost optimization strategies for enterprise-scale applications.
    * Designed and deployed 5 capstone projects including multi-region disaster recovery system and serverless data processing pipeline.
    * Applied learnings to architect company's cloud migration strategy, reducing infrastructure costs by 35%.

REQUIREMENTS:
1. ALWAYS use structured multi-bullet format (not a paragraph)
2. Include project/initiative title with tech stack in bold
3. Use 3 sub-bullets organized by: Build → Engineer → Impact
4. Use strong action verbs (Built, Developed, Led, Engineered, Implemented, Designed)
5. Include specific technologies from structured_inputs["tools"]
6. Add metrics/results from structured_inputs["metrics"] or structured_inputs["achievement"]
7. Keep each bullet to 1-2 sentences max
8. Professional tone

Return JSON:
{{
  "professional_answer": "**[Title]**\\n  * [Bullet 1]\\n  * [Bullet 2]\\n  * [Bullet 3]",
  "key_points": ["Used structured format", "Action verb used", "Specific tech mentioned", "Metrics included"]
}}

{format_instructions}"""),
        ("human", "Generate professional answer with structured formatting")
    ])

    chain = prompt | llm | parser

    try:
        # Extract structured data
        inputs = state.get("structured_inputs", {})

        result = chain.invoke({
            "gap_title": state["gap_info"]["title"],
            "structured_inputs": inputs,
            "format_instructions": parser.get_format_instructions()
        })

        state["generated_answer"] = result["professional_answer"]
        state["current_step"] = "quality_eval"

        return state

    except Exception as e:
        state["error"] = f"Failed to generate answer: {str(e)}"
        # Fallback to raw answer if available
        state["generated_answer"] = state.get("raw_answer", "")
        return state


# ========================================
# Node 4: Evaluate Answer Quality
# ========================================

def evaluate_quality_node(state: AdaptiveAnswerState) -> AdaptiveAnswerState:
    """
    Evaluate answer quality and provide feedback.
    Returns score (1-10) and improvement suggestions if needed.
    """
    llm = get_llm("quality")  # Use quality LLM for evaluation
    parser = JsonOutputParser(pydantic_object=QualityEvaluationOutput)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert evaluating resume content quality.

**CRITICAL - Output Format Requirements:**
Your response MUST be valid JSON matching this exact structure.

For "suggestions" array, each suggestion MUST include ALL 4 fields:
1. "type": Always use "text" for input type
2. "title": Short action phrase (3-6 words, e.g., "Add quantifiable metrics")
3. "examples": Concrete examples separated by "or" (e.g., "Add details like 'X' or 'Y' or 'Z'")
4. "help_text": Brief guidance (e.g., "Include specific numbers and percentages")

DO NOT return suggestions as plain strings. ALWAYS use the 4-field object format.

---

Evaluate this answer for a professional resume:

Question: {question_text}
Answer: {answer}

Evaluation Criteria:
- Specificity: Includes specific technologies, tools, versions
- Evidence: Has metrics, results, timeframes
- Professional tone: Uses action verbs, clear language
- Relevance: Directly addresses the question

Score 1-10:
- 1-3: Very weak
- 4-6: Needs improvement
- 7-8: Good
- 9-10: Excellent

Return JSON exactly matching this structure:
{{
  "quality_score": 6,
  "issues": [
    {{"label": "Lacks Metrics", "description": "No quantifiable results provided"}},
    {{"label": "Vague Tools", "description": "Doesn't specify which LLM framework was used"}}
  ],
  "strengths": [
    {{"label": "Relevance", "description": "Addresses the chatbot development question"}},
    {{"label": "Context", "description": "Mentions customer service application"}}
  ],
  "suggestions": [
    {{
      "type": "text",
      "title": "Add quantifiable metrics",
      "examples": "Add details like 'achieved 92% accuracy rate' or 'resolved 65% of inquiries automatically' or 'reduced response time to 2 seconds'",
      "help_text": "Include specific numbers and percentages"
    }},
    {{
      "type": "text",
      "title": "Specify the LLM framework",
      "examples": "Add details like 'built with Rasa framework' or 'implemented using Dialogflow' or 'developed with LangChain and GPT-4'",
      "help_text": "Name the specific framework or library used"
    }}
  ],
  "is_acceptable": false
}}"""),
        ("human", "Evaluate quality")
    ])

    chain = prompt | llm | parser

    try:
        answer = state.get("generated_answer") or state.get("raw_answer", "")

        result = chain.invoke({
            "question_text": state["question_text"],
            "answer": answer
        })

        state["quality_score"] = result["quality_score"]
        state["quality_issues"] = result["issues"]
        state["quality_strengths"] = result["strengths"]
        state["improvement_suggestions"] = result["suggestions"]

        # Check if acceptable
        if result["is_acceptable"] or state.get("refinement_iteration", 0) >= MAX_REFINEMENT_ITERATIONS:
            state["final_answer"] = answer
            state["current_step"] = "complete"
        else:
            state["current_step"] = "refinement"

        return state

    except Exception as e:
        state["error"] = f"Failed to evaluate quality: {str(e)}"
        # Accept answer on error
        state["final_answer"] = state.get("generated_answer") or state.get("raw_answer", "")
        state["current_step"] = "complete"
        # Ensure quality_score is always set (default to 0 on error)
        if "quality_score" not in state:
            state["quality_score"] = 0
        return state


# ========================================
# Node 5: Refine Answer
# ========================================

def refine_answer_node(state: AdaptiveAnswerState) -> AdaptiveAnswerState:
    """
    Refine answer based on quality feedback and user's additional input.
    """
    llm = get_llm("creative")
    parser = JsonOutputParser(pydantic_object=AnswerRefinementOutput)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert improving resume content with structured formatting.

Original Answer: {original_answer}
Quality Issues: {issues}
Additional Input from User: {refinement_data}

CONTEXT:
- Experience Type: {experience_context}
- Gap Title: {gap_title}
- Duration: {duration}
- Technologies: {tools}

FORMAT RULES - CRITICAL:

If experience_context is "Side Project" or "Personal Learning":
  Format as: **[Project Name] ([Tech Stack])**
    * [Build/Development bullet - what was created]
    * [Engineering/Technical bullet - architecture, methods, tools]
    * [Impact/Results bullet - metrics, outcomes, learnings]

  Example:
  **Sentiment Analysis Tool for Personal Blog (Python, ML)**
    * Built and deployed a sentiment analysis system using pre-trained BERT model from Hugging Face Transformers, analyzing 500 web-scraped blog posts to categorize content and drive sentiment-based recommendations.
    * Engineered data preprocessing pipeline with SMOTE for handling imbalanced classes, achieving 10% accuracy improvement in minority class identification; deployed on Raspberry Pi with automated cron jobs (24h refresh) and matplotlib visualization dashboards.
    * Increased blog engagement by 15% (measured by average comment count) through intelligent content suggestions based on sentiment trends.

If experience_context is "Work":
  Format as: **[Initiative/System Name] at [Company]**
    * [Leadership/Ownership bullet]
    * [Technical implementation bullet]
    * [Business impact bullet]

If experience_context is "Hackathon":
  Format as: **[Project Name] - [Hackathon Name] ([Tech Stack])**
    * [What was built in timeframe]
    * [Technical challenges solved]
    * [Awards/recognition or technical achievement]

If experience_context is "Online Course" or "Certification":
  Format as: **[Course/Certification Name]**
    * [Skills/topics covered]
    * [Hands-on projects completed]
    * [Practical application]

REQUIREMENTS:
1. ALWAYS use structured multi-bullet format (not a paragraph)
2. Include project title with tech stack in bold
3. Use 3 sub-bullets organized by: Build → Engineer → Impact
4. Address all quality issues
5. Incorporate all additional information from user
6. Add specific metrics and numbers
7. Use strong action verbs
8. Keep each bullet to 1-2 sentences max

Return JSON:
{{
  "refined_answer": "**[Title]**\\n  * [Bullet 1]\\n  * [Bullet 2]\\n  * [Bullet 3]",
  "improvements_made": ["Added structured format", "Added metrics", "Made more specific"]
}}

{format_instructions}"""),
        ("human", "Refine the answer with proper structured formatting")
    ])

    chain = prompt | llm | parser

    try:
        original = state.get("generated_answer") or state.get("raw_answer", "")
        refinement_data = state.get("refinement_data", {})
        structured_inputs = state.get("structured_inputs", {})

        # Extract context fields
        experience_context = structured_inputs.get("context", "Unknown")
        duration = structured_inputs.get("duration", "Not specified")
        tools = structured_inputs.get("tools", [])
        if isinstance(tools, list):
            tools = ", ".join(tools) if tools else "Not specified"

        # Format quality_issues for prompt (handle both old string format and new object format)
        quality_issues = state.get("quality_issues", [])
        if quality_issues and isinstance(quality_issues[0], dict):
            # New format: list of {label, description} objects
            issues_text = "\n".join([f"- {issue['label']}: {issue['description']}" for issue in quality_issues])
        elif quality_issues and hasattr(quality_issues[0], 'label'):
            # Pydantic object format
            issues_text = "\n".join([f"- {issue.label}: {issue.description}" for issue in quality_issues])
        elif quality_issues:
            # Old format: list of strings
            issues_text = "\n".join([f"- {issue}" for issue in quality_issues])
        else:
            issues_text = "No specific issues identified"

        result = chain.invoke({
            "original_answer": original,
            "issues": issues_text,
            "refinement_data": refinement_data,
            "experience_context": experience_context,
            "gap_title": state.get("gap_info", {}).get("title", "Unknown"),
            "duration": duration,
            "tools": tools,
            "format_instructions": parser.get_format_instructions()
        })

        state["refined_answer"] = result["refined_answer"]
        state["generated_answer"] = result["refined_answer"]  # Update for next evaluation
        state["refinement_iteration"] = state.get("refinement_iteration", 0) + 1

        # Go back to quality evaluation
        state["current_step"] = "quality_eval"

        return state

    except Exception as e:
        state["error"] = f"Failed to refine answer: {str(e)}"
        # Accept current answer on error
        state["final_answer"] = state.get("generated_answer") or state.get("raw_answer", "")
        state["current_step"] = "complete"
        return state


# ========================================
# Routing Functions
# ========================================

def route_after_experience_check(state: AdaptiveAnswerState) -> str:
    """
    Route after experience check based on user response.

    Returns:
        "deep_dive" if has experience
        "learning_resources" if no experience or willing to learn
    """
    response = state.get("experience_check_response")

    if response == "yes":
        return "deep_dive"
    else:
        # Both "no" and "willing_to_learn" go to resources
        return "learning_resources"


def route_after_quality_eval(state: AdaptiveAnswerState) -> str:
    """
    Route after quality evaluation.

    Returns:
        "complete" if quality is good or max iterations reached
        "refinement" if needs improvement
    """
    score = state.get("quality_score", 0)
    iteration = state.get("refinement_iteration", 0)

    if score >= MIN_ACCEPTABLE_QUALITY_SCORE or iteration >= MAX_REFINEMENT_ITERATIONS:
        return "complete"
    else:
        return "refinement"
