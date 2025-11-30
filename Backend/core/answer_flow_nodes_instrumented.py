"""
Instrumented Async Workflow Nodes with Metrics (Phase 3.2).
Adds comprehensive metrics tracking to all workflow nodes.

This module extends answer_flow_nodes_async.py with automatic:
- Performance tracking (latency)
- Cost tracking (LLM token usage)
- Quality tracking (scores, refinements)
- Cache tracking (embeddings, prompts)
- Error tracking (exceptions)
"""

from typing import Dict, Any, List
from datetime import datetime

from core.answer_flow_nodes_async import (
    # Import all original async nodes
    DeepDivePromptsOutput,
    QualityEvaluationOutput,
    AnswerGenerationOutput,
    AnswerRefinementOutput,
    FeedbackItem,
    ImprovementSuggestion
)
from core.answer_flow_state import (
    AdaptiveAnswerState,
    QUALITY_THRESHOLDS,
    MAX_REFINEMENT_ITERATIONS
)
from core.langchain_config import get_async_llm
from core.metrics_collector import get_metrics_collector, track_performance
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


# ========================================
# Helper: Token Estimation
# ========================================

def estimate_tokens(text_or_dict: Any) -> int:
    """
    Estimate token count for cost tracking.

    Rough approximation: 1 token ≈ 4 characters for English.
    More accurate: Use tiktoken library (not adding dependency for Phase 3.2).
    """
    if isinstance(text_or_dict, dict):
        text = str(text_or_dict)
    elif isinstance(text_or_dict, str):
        text = text_or_dict
    else:
        text = str(text_or_dict)

    return max(1, len(text) // 4)


# ========================================
# Instrumented Node 1: Generate Deep Dive Prompts
# ========================================

async def generate_deep_dive_prompts_node_instrumented(
    state: AdaptiveAnswerState
) -> AdaptiveAnswerState:
    """
    Generate deep-dive prompts with metrics tracking (Phase 3.2).

    Tracks:
    - Performance: Latency of prompt generation
    - Cost: Input/output tokens for LLM call
    - Metadata: Gap priority, question ID
    """
    collector = get_metrics_collector()
    gap_priority = state["gap_info"].get("priority", "UNKNOWN")

    # Track performance with context manager
    with track_performance(
        "generate_deep_dive_prompts",
        metadata={
            "gap_priority": gap_priority,
            "question_id": state.get("question_id", "unknown"),
            "session_id": state.get("session_id", "unknown")
        }
    ):
        llm = get_async_llm("fast")
        parser = JsonOutputParser(pydantic_object=DeepDivePromptsOutput)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at generating structured interview questions.

Given a gap/skill, generate 4-6 targeted prompts to extract detailed experience.

Gap: {gap_title}
Description: {gap_description}
Question: {question_text}

Generate prompts that ask about:
1. Where used (work, project, course)
2. Duration/frequency
3. Specific tools/technologies
4. Achievements/results

Return JSON:
{{
  "prompts": [
    {{"type": "select", "title": "Where did you use this?", "options": ["Work", "Side Project", "Course"], "required": true}},
    {{"type": "text", "title": "How long have you been using it?", "placeholder": "e.g., 2 years", "required": true}},
    {{"type": "textarea", "title": "What did you achieve with it?", "placeholder": "Describe results...", "required": true}}
  ]
}}

{format_instructions}"""),
            ("human", "Generate prompts for this gap")
        ])

        chain = prompt | llm | parser

        # Prepare variables
        gap_title = state["gap_info"]["title"]
        gap_description = state["gap_info"].get("description", "")
        question_text = state["question_text"]

        variables = {
            "gap_title": gap_title,
            "gap_description": gap_description,
            "question_text": question_text,
            "format_instructions": parser.get_format_instructions()
        }

        # ASYNC: Use ainvoke
        result = await chain.ainvoke(variables)

        # Track LLM cost
        input_tokens = estimate_tokens(variables)
        output_tokens = estimate_tokens(result)

        collector.record_llm_cost(
            operation="generate_deep_dive_prompts",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_hit=False,  # TODO: Detect cache hits from LLM response metadata
            metadata={
                "gap_priority": gap_priority,
                "question_id": state.get("question_id")
            }
        )

        # Update state
        state["deep_dive_prompts"] = result.get("prompts", [])
        state["current_step"] = "deep_dive"

    return state


# ========================================
# Instrumented Node 2: Evaluate Quality
# ========================================

async def evaluate_quality_node_instrumented(
    state: AdaptiveAnswerState
) -> AdaptiveAnswerState:
    """
    Evaluate answer quality with metrics tracking (Phase 3.2).

    Tracks:
    - Performance: Latency of quality evaluation
    - Cost: LLM tokens
    - Quality: Score, refinement iteration
    """
    collector = get_metrics_collector()
    gap_priority = state["gap_info"].get("priority", "UNKNOWN")
    question_id = state.get("question_id", "unknown")
    refinement_iteration = state.get("refinement_iteration", 0)

    with track_performance(
        "evaluate_quality",
        metadata={
            "gap_priority": gap_priority,
            "question_id": question_id,
            "refinement_iteration": refinement_iteration
        }
    ):
        llm = get_async_llm("quality")
        parser = JsonOutputParser(pydantic_object=QualityEvaluationOutput)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at evaluating resume content quality.

Evaluate this answer for:
1. Specificity (concrete details, versions, tools)
2. Evidence (metrics, timeframes, results)
3. Professional tone (action verbs, clear language)
4. Relevance (addresses the question)

Scoring (1-10):
- 1-3: Very weak
- 4-6: Needs improvement
- 7-8: Good
- 9-10: Excellent

Return JSON:
{{
  "quality_score": 7,
  "issues": [{{"label": "Specificity", "description": "Add specific tool versions"}}],
  "strengths": [{{"label": "Relevance", "description": "Directly addresses question"}}],
  "suggestions": [{{"type": "text", "title": "Add specific versions", "examples": ["Python 3.9", "Docker 20.10"], "help_text": "Include tool versions"}}],
  "is_acceptable": true
}}

{format_instructions}"""),
            ("human", "Evaluate this answer:\n\nQuestion: {question}\nAnswer: {answer}")
        ])

        chain = prompt | llm | parser

        # Get answer from state
        answer = state.get("generated_answer", state.get("refined_answer", ""))

        variables = {
            "question": state["question_text"],
            "answer": answer,
            "format_instructions": parser.get_format_instructions()
        }

        # ASYNC: Use ainvoke
        result = await chain.ainvoke(variables)

        # Track LLM cost
        input_tokens = estimate_tokens(variables)
        output_tokens = estimate_tokens(result)

        collector.record_llm_cost(
            operation="evaluate_quality",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_hit=False,
            metadata={
                "gap_priority": gap_priority,
                "refinement_iteration": refinement_iteration
            }
        )

        # Extract quality feedback
        quality_score = result.get("quality_score", 5)
        is_acceptable = result.get("is_acceptable", quality_score >= 7)

        # Track quality metric
        collector.record_quality(
            question_id=question_id,
            gap_priority=gap_priority,
            quality_score=quality_score,
            refinement_count=refinement_iteration,
            metadata={
                "is_acceptable": is_acceptable,
                "session_id": state.get("session_id")
            }
        )

        # Update state
        state["quality_feedback"] = {
            "quality_score": quality_score,
            "is_acceptable": is_acceptable,
            "issues": result.get("issues", []),
            "strengths": result.get("strengths", []),
            "suggestions": result.get("suggestions", [])
        }
        state["current_step"] = "quality_evaluated"

    return state


# ========================================
# Instrumented Node 3: Generate Professional Answer
# ========================================

async def generate_answer_node_instrumented(
    state: AdaptiveAnswerState
) -> AdaptiveAnswerState:
    """
    Generate professional answer with metrics tracking (Phase 3.2).

    Tracks:
    - Performance: Latency
    - Cost: LLM tokens
    """
    collector = get_metrics_collector()
    gap_priority = state["gap_info"].get("priority", "UNKNOWN")

    with track_performance(
        "generate_answer",
        metadata={
            "gap_priority": gap_priority,
            "question_id": state.get("question_id")
        }
    ):
        llm = get_async_llm("fast")
        parser = JsonOutputParser(pydantic_object=AnswerGenerationOutput)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert resume writer.

Transform user inputs into professional resume bullets.

Format:
**[Project/Skill Name]**
  * Built/Developed [what was created]
  * Engineered [technical approach, tools]
  * Achieved [results, metrics]

Use:
- Strong action verbs (Built, Developed, Led, Engineered)
- Specific technologies from inputs
- Metrics when available
- Professional tone

Return JSON:
{{
  "professional_answer": "[formatted answer]",
  "key_points": ["point1", "point2", "point3"]
}}

{format_instructions}"""),
            ("human", "Generate answer from:\n\nQuestion: {question}\nInputs: {inputs}")
        ])

        chain = prompt | llm | parser

        # Get user inputs
        user_inputs = state.get("user_answer_inputs", {})

        variables = {
            "question": state["question_text"],
            "inputs": str(user_inputs),
            "format_instructions": parser.get_format_instructions()
        }

        # ASYNC: Use ainvoke
        result = await chain.ainvoke(variables)

        # Track LLM cost
        input_tokens = estimate_tokens(variables)
        output_tokens = estimate_tokens(result)

        collector.record_llm_cost(
            operation="generate_answer",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_hit=False,
            metadata={"gap_priority": gap_priority}
        )

        # Update state
        state["generated_answer"] = result.get("professional_answer", "")
        state["key_points"] = result.get("key_points", [])
        state["current_step"] = "answer_generated"

    return state


# ========================================
# Instrumented Node 4: Refine Answer
# ========================================

async def refine_answer_node_instrumented(
    state: AdaptiveAnswerState
) -> AdaptiveAnswerState:
    """
    Refine answer based on feedback with metrics tracking (Phase 3.2).

    Tracks:
    - Performance: Latency
    - Cost: LLM tokens
    - Quality: Pre/post refinement scores
    """
    collector = get_metrics_collector()
    gap_priority = state["gap_info"].get("priority", "UNKNOWN")
    refinement_iteration = state.get("refinement_iteration", 0)

    with track_performance(
        "refine_answer",
        metadata={
            "gap_priority": gap_priority,
            "refinement_iteration": refinement_iteration
        }
    ):
        llm = get_async_llm("fast")
        parser = JsonOutputParser(pydantic_object=AnswerRefinementOutput)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert resume writer improving answers.

Original answer: {original_answer}

Issues to address:
{issues}

Suggestions:
{suggestions}

Refinement data (if provided):
{refinement_data}

Improve the answer to:
1. Address all issues
2. Implement suggestions
3. Add details from refinement data
4. Maintain professional structure

Return JSON:
{{
  "refined_answer": "[improved answer]",
  "improvements_made": ["improvement1", "improvement2"]
}}

{format_instructions}"""),
            ("human", "Refine the answer")
        ])

        chain = prompt | llm | parser

        # Get feedback and refinement data
        quality_feedback = state.get("quality_feedback", {})
        refinement_data = state.get("user_refinement_data", {})

        variables = {
            "original_answer": state.get("generated_answer", ""),
            "issues": str(quality_feedback.get("issues", [])),
            "suggestions": str(quality_feedback.get("suggestions", [])),
            "refinement_data": str(refinement_data),
            "format_instructions": parser.get_format_instructions()
        }

        # ASYNC: Use ainvoke
        result = await chain.ainvoke(variables)

        # Track LLM cost
        input_tokens = estimate_tokens(variables)
        output_tokens = estimate_tokens(result)

        collector.record_llm_cost(
            operation="refine_answer",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_hit=False,
            metadata={
                "gap_priority": gap_priority,
                "refinement_iteration": refinement_iteration
            }
        )

        # Update state
        state["refined_answer"] = result.get("refined_answer", "")
        state["improvements_made"] = result.get("improvements_made", [])
        state["refinement_iteration"] = refinement_iteration + 1
        state["current_step"] = "answer_refined"

    return state


# ========================================
# Instrumented Node 5: Search Learning Resources
# ========================================

async def search_learning_resources_node_instrumented(
    state: AdaptiveAnswerState
) -> AdaptiveAnswerState:
    """
    Search for learning resources with metrics tracking (Phase 3.2).

    Tracks:
    - Performance: Search latency
    - No LLM cost (uses SearXNG)
    """
    collector = get_metrics_collector()
    gap_priority = state["gap_info"].get("priority", "UNKNOWN")

    with track_performance(
        "search_learning_resources",
        metadata={
            "gap_priority": gap_priority,
            "question_id": state.get("question_id")
        }
    ):
        # Import here to avoid circular dependency
        from core.searxng_client import get_searxng_client
        from core.search_query_builder import build_learning_query

        # Build search query
        gap_title = state["gap_info"]["title"]
        user_level = state.get("user_level", "beginner")

        query = build_learning_query(gap_title, user_level)

        # Search
        searxng = get_searxng_client()
        results = searxng.search(query, num_results=10)

        # Update state
        state["learning_resources"] = results[:5]  # Top 5
        state["current_step"] = "resources_found"

    return state


# ========================================
# Node Mapping
# ========================================

INSTRUMENTED_NODES = {
    "generate_deep_dive_prompts": generate_deep_dive_prompts_node_instrumented,
    "evaluate_quality": evaluate_quality_node_instrumented,
    "generate_answer": generate_answer_node_instrumented,
    "refine_answer": refine_answer_node_instrumented,
    "search_learning_resources": search_learning_resources_node_instrumented,
}


# ========================================
# Example Usage
# ========================================

if __name__ == "__main__":
    """
    Example of how instrumented nodes track metrics automatically.

    When integrated into the workflow graph:
    1. Performance tracked via context manager
    2. LLM costs recorded for every call
    3. Quality metrics collected on evaluations
    4. All metrics accessible via /api/metrics/* endpoints
    """
    print("""
    Instrumented Workflow Nodes (Phase 3.2)

    Features:
    - ✅ Automatic performance tracking
    - ✅ LLM cost tracking with token estimation
    - ✅ Quality score recording
    - ✅ Error tracking via context manager
    - ✅ Metadata enrichment (gap priority, session ID)

    Metrics Tracked:
    1. generate_deep_dive_prompts:
       - Latency
       - LLM cost (input/output tokens)
       - Gap priority metadata

    2. evaluate_quality:
       - Latency
       - LLM cost
       - Quality score (0-10)
       - Refinement iteration count

    3. generate_answer:
       - Latency
       - LLM cost
       - Answer generation time

    4. refine_answer:
       - Latency
       - LLM cost
       - Refinement iteration

    5. search_learning_resources:
       - Search latency
       - No LLM cost (SearXNG)

    Integration:
    Replace nodes in adaptive_question_graph.py with instrumented versions
    to automatically populate metrics accessible via /api/metrics/* endpoints.
    """)
