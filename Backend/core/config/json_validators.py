"""
JSON Response Validators with Pydantic Schemas.
Provides validation for all AI-generated JSON responses with retry support.
"""

import json
from typing import Optional, List, Dict, Any, Type, TypeVar
from pydantic import BaseModel, Field, ValidationError


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class JSONValidationError(Exception):
    """Raised when JSON validation fails after all retries."""
    pass


# =============================================================================
# RESPONSE SCHEMAS - Pydantic models for AI responses
# =============================================================================

# --- Score Message Schema ---
class ScoreMessageResponse(BaseModel):
    """Schema for generate_score_message() response."""
    title: str
    subtitle: str


# --- Gap Analysis Schemas ---
class GapItem(BaseModel):
    """Single gap item in gap analysis."""
    gap: str
    impact: str = ""
    suggestion: str = ""


class GapsCollection(BaseModel):
    """Collection of gaps by severity."""
    critical: List[GapItem] = Field(default_factory=list)
    important: List[GapItem] = Field(default_factory=list)
    nice_to_have: List[GapItem] = Field(default_factory=list)
    logistical: List[GapItem] = Field(default_factory=list)


class StrengthItem(BaseModel):
    """Single strength item."""
    strength: str
    evidence: str = ""


class GapAnalysisResponse(BaseModel):
    """Schema for gap analysis response."""
    gaps: GapsCollection
    strengths: List[StrengthItem] = Field(default_factory=list)
    overall_assessment: str = ""
    application_viability: str = ""


# --- Question Generation Schema ---
class QuestionItemSchema(BaseModel):
    """Schema for a single question."""
    id: str
    question: str
    category: str
    priority: str
    related_gap: str = ""
    deep_dive_prompts: List[str] = Field(default_factory=list)


class QuestionsResponse(BaseModel):
    """Schema for question generation response."""
    questions: List[QuestionItemSchema]


# --- Answer Evaluation Schema ---
class AnswerEvaluationResponse(BaseModel):
    """Schema for answer quality evaluation."""
    quality_score: int = Field(ge=0, le=10)
    quality_issues: List[str] = Field(default_factory=list)
    quality_strengths: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)


# --- Answer Analysis Schema ---
class UncoveredExperience(BaseModel):
    """Uncovered experience from answer analysis."""
    skill: str
    context: str = ""
    level: str = ""


class CVUpdates(BaseModel):
    """CV updates from answer analysis."""
    skills: List[str] = Field(default_factory=list)
    experiences: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)


class AnswerAnalysisResponse(BaseModel):
    """Schema for answer analysis response."""
    uncovered_experiences: List[UncoveredExperience] = Field(default_factory=list)
    cv_updates: CVUpdates = Field(default_factory=CVUpdates)


# --- Industry Extraction Schema ---
# Note: For simple list responses, we validate directly in validate_json_response


# --- Skill Gap Analysis Schema ---
class SkillGapAnalysisSchema(BaseModel):
    """Schema for skill gap analysis response."""
    case: str
    skill_missing: str
    skill_exist: Optional[str] = None
    intro: str
    key_points: List[str]
    message: str


# --- Domain Finder Schema ---
class DomainMatchSchema(BaseModel):
    """Single domain match."""
    domain: str
    relevance_score: int = Field(ge=0, le=100)
    key_skills_matched: List[str] = Field(default_factory=list)
    potential_roles: List[str] = Field(default_factory=list)
    growth_outlook: str = ""


class DomainFinderSchema(BaseModel):
    """Schema for domain finder response."""
    domains: List[DomainMatchSchema]


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

T = TypeVar('T', bound=BaseModel)


def validate_json_response(
    response_text: str,
    validator: Type[T]
) -> tuple[Optional[dict], Optional[str]]:
    """
    Validate JSON response against Pydantic schema.

    Args:
        response_text: Raw JSON string from AI
        validator: Pydantic model class for validation

    Returns:
        tuple: (parsed_dict, error_message)
            - If valid: (dict, None)
            - If invalid: (None, error_description)
    """
    try:
        # First, try to parse as JSON
        data = json.loads(response_text)

        # Validate against schema
        validated = validator.model_validate(data)
        return validated.model_dump(), None

    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {str(e)}"

    except ValidationError as e:
        # Extract concise error message
        errors = e.errors()
        error_msgs = [f"{err['loc']}: {err['msg']}" for err in errors[:3]]  # First 3 errors
        return None, f"Schema validation failed: {'; '.join(error_msgs)}"

    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


def clean_json_response(response_text: str) -> str:
    """
    Clean AI response text that may contain markdown code blocks.

    Args:
        response_text: Raw response from AI

    Returns:
        Cleaned JSON string
    """
    cleaned = response_text.strip()

    # Remove markdown code blocks
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove opening line (```json or ```)
        if len(lines) > 1:
            lines = lines[1:]
        # Remove closing ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        elif lines and lines[-1].strip().endswith("```"):
            lines[-1] = lines[-1].replace("```", "").strip()
        cleaned = "\n".join(lines).strip()

    return cleaned


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Exceptions
    'JSONValidationError',

    # Schema classes
    'ScoreMessageResponse',
    'GapItem',
    'GapsCollection',
    'StrengthItem',
    'GapAnalysisResponse',
    'QuestionItemSchema',
    'QuestionsResponse',
    'AnswerEvaluationResponse',
    'UncoveredExperience',
    'CVUpdates',
    'AnswerAnalysisResponse',
    'SkillGapAnalysisSchema',
    'DomainMatchSchema',
    'DomainFinderSchema',

    # Functions
    'validate_json_response',
    'clean_json_response',
]
