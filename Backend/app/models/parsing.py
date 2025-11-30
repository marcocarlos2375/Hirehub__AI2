"""
Pydantic models for parsing endpoints.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ParseRequest(BaseModel):
    """Request model for job description parsing."""
    job_description: str = Field(..., min_length=50, description="Job description text to parse")
    language: str = Field("english", description="Language for parsing (english, french, german, spanish)")


class ParseResponse(BaseModel):
    """Response model for job description parsing."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    time_seconds: float
    model: str
    language: str


class CVParseRequest(BaseModel):
    """Request model for CV/resume parsing."""
    resume_text: str = Field(..., min_length=50, description="Resume/CV text to parse")
    language: str = Field("english", description="Language for parsing (english, french, german, spanish)")


class CVParseResponse(BaseModel):
    """Response model for CV/resume parsing."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    time_seconds: float
    model: str
    language: str


class ParsedJobDescription(BaseModel):
    """Validated structure for parsed job description."""
    company_name: Optional[str] = None
    position_title: Optional[str] = None
    location: Optional[str] = None
    work_mode: Optional[str] = None
    salary_range: Optional[str] = None
    experience_years_required: Optional[int] = None
    experience_level: Optional[str] = None
    hard_skills_required: List[Dict[str, str]] = Field(default_factory=list)
    soft_skills_required: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    domain_expertise: Optional[Dict[str, Any]] = None
    implicit_requirements: List[str] = Field(default_factory=list)
    company_culture_signals: List[str] = Field(default_factory=list)
    ats_keywords: List[str] = Field(default_factory=list)


class ParsedCV(BaseModel):
    """Validated structure for parsed CV."""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: Optional[str] = None
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    work_experience: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    languages: List[Dict[str, str]] = Field(default_factory=list)
