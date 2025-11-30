"""
State definitions for LangGraph adaptive question workflow.
Defines the state machine structure for intelligent question answering.
"""

from typing import TypedDict, Literal, Optional, List, Dict, Any, Union
from datetime import datetime


class AdaptiveAnswerState(TypedDict, total=False):
    """
    State for the adaptive question answering workflow.
    This state is passed through all nodes in the LangGraph.

    Flow:
        1. check_experience → has_experience? → deep_dive OR skip
        2. deep_dive → generate_answer → evaluate_quality
        3. evaluate_quality → quality_good? → END OR refine_answer → evaluate_quality
    """

    # Input data
    question_id: str
    question_text: str
    question_data: Dict[str, Any]  # Full question object from Phase 4
    gap_info: Dict[str, Any]  # Gap details from Phase 3
    user_id: str
    parsed_cv: Dict[str, Any]
    parsed_jd: Dict[str, Any]
    language: str

    # Session management (Quick Win #5: State Persistence Prep)
    session_id: Optional[str]  # UUID for session tracking and resume capability

    # Flow control
    current_step: str  # "experience_check", "deep_dive", "quality_eval", "refinement", "complete"
    has_experience: Optional[bool]  # True or False
    chosen_path: Optional[Literal["deep_dive", "skip"]]

    # User input from experience check
    experience_check_response: Optional[str]  # "yes" or "no"

    # Deep dive data (if has_experience = True)
    structured_inputs: Optional[Dict[str, Any]]  # Responses to structured prompts
    # Example: {
    #   "context": "Work",
    #   "duration": "6 months",
    #   "specific_tools": ["OpenAI API", "LangChain"],
    #   "achievement": "Built chatbot with 85% accuracy",
    #   "metrics": "Reduced support tickets by 40%"
    # }

    raw_answer: Optional[str]  # Free-text answer from user

    # Answer generation
    generated_answer: Optional[str]  # AI-generated professional answer from structured inputs

    # Quality validation
    quality_score: Optional[int]  # 1-10
    quality_issues: Optional[List[Union[str, Dict[str, str]]]]  # List of {label, description} objects or strings for backwards compatibility
    quality_strengths: Optional[List[str]]  # What's good about the answer
    improvement_suggestions: Optional[List[Dict[str, Any]]]  # Structured prompts for improvement
    # Example suggestions: [
    #   {"type": "text", "prompt": "What specific achievement did you accomplish?"},
    #   {"type": "select", "prompt": "What was the impact?", "options": ["...", "..."]}
    # ]

    # Refinement loop
    refinement_iteration: int  # Counts iterations (max 2)
    refinement_data: Optional[Dict[str, Any]]  # Additional data from refinement prompts
    refined_answer: Optional[str]  # Improved answer after refinement

    # Final output
    final_answer: Optional[str]  # Accepted professional answer
    answer_accepted: bool  # Did user accept the final answer?

    # Metadata
    started_at: datetime
    completed_at: Optional[datetime]
    total_time_seconds: Optional[float]
    error: Optional[str]  # Error message if something fails


# Routing decision types
RoutingDecision = Literal["deep_dive", "skip", "END"]
QualityRoutingDecision = Literal["good", "needs_improvement", "max_iterations"]


class ExperienceCheckInput(TypedDict):
    """Input for experience check step."""
    question_text: str
    gap_title: str
    gap_description: str


class DeepDivePrompt(TypedDict):
    """Structured prompt for deep dive questions."""
    id: str
    type: Literal["text", "textarea", "select", "multiselect", "number"]
    question: str
    placeholder: Optional[str]
    options: Optional[List[str]]  # For select/multiselect
    required: bool
    help_text: Optional[str]


class QualityFeedback(TypedDict):
    """Feedback from quality evaluation."""
    quality_score: int
    issues: List[str]
    strengths: List[str]
    suggestions: List[Dict[str, Any]]
    is_acceptable: bool  # True if score >= 7


class AnswerRefinement(TypedDict):
    """Result of answer refinement."""
    refined_answer: str
    improvements_made: List[str]
    new_quality_score: int


# Error types for graceful handling
class WorkflowError(Exception):
    """Base exception for workflow errors."""
    pass


class MaxIterationsError(WorkflowError):
    """Raised when max refinement iterations reached."""
    pass


class UserCancelledError(WorkflowError):
    """Raised when user cancels the flow."""
    pass


# Constants
MAX_REFINEMENT_ITERATIONS = 2
MIN_ACCEPTABLE_QUALITY_SCORE = 7  # Default fallback

# Dynamic quality thresholds based on gap priority
QUALITY_THRESHOLDS = {
    "CRITICAL": 8,      # Higher bar for critical gaps (deal-breakers)
    "HIGH": 7,          # Standard threshold for high priority
    "IMPORTANT": 7,     # Standard threshold
    "MEDIUM": 6,        # More lenient for medium priority
    "NICE_TO_HAVE": 6,  # More lenient for nice-to-have skills
    "LOW": 5,           # Very lenient for low priority
    "LOGISTICAL": 5     # Very lenient for logistical gaps
}
