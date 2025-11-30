"""
Async node implementations for LangGraph adaptive question workflow (Phase 2.1).
Provides true async/await support for concurrent I/O operations.

These async nodes replace the synchronous versions in answer_flow_nodes.py
for better performance and scalability.
"""

from typing import Dict, Any, List
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from core.config.langchain_config import get_async_llm, get_learning_resources_vectorstore
from core.workflow.answer_flow_state import (
    AdaptiveAnswerState,
    DeepDivePrompt,
    QualityFeedback,
    MIN_ACCEPTABLE_QUALITY_SCORE,
    MAX_REFINEMENT_ITERATIONS,
    MAX_LEARNING_RESOURCES,
    MAX_LEARNING_DAYS,
    QUALITY_THRESHOLDS
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
# Async Node 1: Generate Deep Dive Prompts
# ========================================

async def generate_deep_dive_prompts_node_async(state: AdaptiveAnswerState) -> AdaptiveAnswerState:
    """
    Generate structured prompts for deep-dive questioning (ASYNC VERSION - Phase 2.1).

    Called when user has experience with the skill.
    Uses async LLM calls for true concurrency.

    Returns prompts like:
    - Where did you use this? (select: Work, Side Project, Course)
    - How long? (text)
    - Which specific tools? (multiselect)
    - What did you achieve? (textarea)
    """
    llm = get_async_llm("fast")
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
        # ASYNC: Use ainvoke instead of invoke (Phase 2.1)
        result = await chain.ainvoke({
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
# Async Node 2: Search Learning Resources
# ========================================

async def search_learning_resources_node_async(state: AdaptiveAnswerState) -> AdaptiveAnswerState:
    """
    Search for relevant learning resources using semantic search (ASYNC VERSION - Phase 2.1).

    Called when user doesn't have experience or is willing to learn.
    Uses async vector store operations for better performance.
    """
    try:
        vectorstore = get_learning_resources_vectorstore()

        # Build search query from gap
        gap = state["gap_info"]
        search_query = f"{gap['title']}: {gap.get('description', '')}"

        # ASYNC: Use asimilarity_search instead of similarity_search (Phase 2.1)
        docs = await vectorstore.asimilarity_search(
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
# Async Node 3: Generate Professional Answer
# ========================================

async def generate_answer_from_inputs_node_async(state: AdaptiveAnswerState) -> AdaptiveAnswerState:
    """
    Generate professional answer from structured inputs (ASYNC VERSION - Phase 2.1).

    Called after user completes deep-dive prompts.
    Uses async LLM calls for faster response generation.
    """
    llm = get_async_llm("creative")  # Slightly creative for better writing
    parser = JsonOutputParser(pydantic_object=AnswerGenerationOutput)

    # NOTE: Prompt template truncated for brevity - use same as sync version
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert resume writer creating professional experience descriptions.

Given structured inputs about a candidate's experience, generate a compelling, professional answer.

Gap: {gap_title}
Structured Inputs: {structured_inputs}

Use structured bullet format with project title, tech stack, and 3 bullets (Build → Engineer → Impact).

{format_instructions}"""),
        ("human", "Generate professional answer with structured formatting")
    ])

    chain = prompt | llm | parser

    try:
        # Extract structured data
        inputs = state.get("structured_inputs", {})

        # ASYNC: Use ainvoke instead of invoke (Phase 2.1)
        result = await chain.ainvoke({
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
# Async Node 4: Evaluate Answer Quality
# ========================================

async def evaluate_quality_node_async(state: AdaptiveAnswerState) -> AdaptiveAnswerState:
    """
    Evaluate answer quality and provide feedback (ASYNC VERSION - Phase 2.1).

    Returns score (1-10) and improvement suggestions if needed.
    Uses async LLM calls for faster evaluation.
    """
    llm = get_async_llm("quality")  # Use quality LLM for evaluation
    parser = JsonOutputParser(pydantic_object=QualityEvaluationOutput)

    # NOTE: Prompt template truncated for brevity - use same as sync version
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert evaluating resume content quality.

Evaluate this answer for a professional resume:

Question: {question_text}
Answer: {answer}

Score 1-10 and provide structured feedback.

{format_instructions}"""),
        ("human", "Evaluate answer quality")
    ])

    chain = prompt | llm | parser

    try:
        answer = state.get("generated_answer") or state.get("raw_answer", "")

        # ASYNC: Use ainvoke instead of invoke (Phase 2.1)
        result = await chain.ainvoke({
            "question_text": state["question_text"],
            "answer": answer,
            "format_instructions": parser.get_format_instructions()
        })

        # Store evaluation results
        state["quality_score"] = result["quality_score"]
        state["quality_issues"] = result["issues"]
        state["quality_strengths"] = result["strengths"]
        state["improvement_suggestions"] = result["suggestions"]

        # Accept answer if quality meets dynamic threshold (Quick Win #1)
        gap_priority = state.get("gap_info", {}).get("priority", "IMPORTANT")
        threshold = QUALITY_THRESHOLDS.get(gap_priority.upper(), MIN_ACCEPTABLE_QUALITY_SCORE)

        if result["quality_score"] >= threshold:
            state["final_answer"] = answer
            state["answer_accepted"] = True

        state["current_step"] = "quality_eval"

        return state

    except Exception as e:
        state["error"] = f"Failed to evaluate quality: {str(e)}"
        # Accept answer on error
        state["final_answer"] = state.get("generated_answer") or state.get("raw_answer", "")
        state["answer_accepted"] = True
        return state


# ========================================
# Async Node 5: Refine Answer
# ========================================

async def refine_answer_node_async(state: AdaptiveAnswerState) -> AdaptiveAnswerState:
    """
    Refine answer based on quality feedback (ASYNC VERSION - Phase 2.1).

    Uses async LLM calls for faster refinement generation.
    """
    llm = get_async_llm("creative")
    parser = JsonOutputParser(pydantic_object=AnswerRefinementOutput)

    # NOTE: Prompt template truncated for brevity - use same as sync version
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert resume writer improving answers based on feedback.

Original Answer: {original_answer}
Quality Issues: {issues}
Suggestions: {suggestions}
Additional Data: {refinement_data}

Generate improved version addressing all feedback.

{format_instructions}"""),
        ("human", "Refine the answer")
    ])

    chain = prompt | llm | parser

    try:
        # ASYNC: Use ainvoke instead of invoke (Phase 2.1)
        result = await chain.ainvoke({
            "original_answer": state.get("generated_answer", ""),
            "issues": state.get("quality_issues", []),
            "suggestions": state.get("improvement_suggestions", []),
            "refinement_data": state.get("refinement_data", {}),
            "format_instructions": parser.get_format_instructions()
        })

        state["refined_answer"] = result["refined_answer"]
        state["generated_answer"] = result["refined_answer"]  # Update for next iteration
        state["refinement_iteration"] = state.get("refinement_iteration", 0) + 1
        state["current_step"] = "refinement"

        return state

    except Exception as e:
        state["error"] = f"Failed to refine answer: {str(e)}"
        # Accept current answer on error
        state["final_answer"] = state.get("generated_answer") or state.get("raw_answer", "")
        state["current_step"] = "complete"
        return state


# ========================================
# Export routing functions (same as sync)
# ========================================

# Routing functions are not async (they're pure functions)
from core.workflow.answer_flow_nodes import route_after_experience_check, route_after_quality_eval
