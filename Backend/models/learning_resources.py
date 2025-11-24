"""
SQLAlchemy models for Learning Resources System.
Supports adaptive question workflows with learning plans and resource tracking.
"""

from datetime import datetime, date
from typing import List, Optional
from uuid import uuid4
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DECIMAL, DateTime, Date,
    ForeignKey, CheckConstraint, UniqueConstraint, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class LearningResource(Base):
    """
    Represents a course, project, certification, or other learning resource.
    Used to suggest learning paths when users have gaps in their experience.
    """
    __tablename__ = 'learning_resources'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(
        String(50),
        nullable=False,
        # course, project, certification, challenge, tutorial
    )
    provider = Column(String(100))  # Udemy, Coursera, freeCodeCamp, GitHub, etc.
    url = Column(Text)
    duration_days = Column(Integer, nullable=False)
    difficulty = Column(String(50))  # beginner, intermediate, advanced
    cost = Column(String(50))  # free, paid, freemium
    skills_covered = Column(JSONB, nullable=False, default=list)  # Array of skill strings
    prerequisites = Column(JSONB, default=list)  # Array of prerequisite skills
    completion_certificate = Column(Boolean, default=False)
    rating = Column(DECIMAL(3, 2))  # 0-5 stars
    language = Column(String(50), default='english')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    progress_entries = relationship("UserResourceProgress", back_populates="resource")

    __table_args__ = (
        CheckConstraint("type IN ('course', 'project', 'certification', 'challenge', 'tutorial')", name='ck_type'),
        CheckConstraint("difficulty IN ('beginner', 'intermediate', 'advanced')", name='ck_difficulty'),
        CheckConstraint("cost IN ('free', 'paid', 'freemium')", name='ck_cost'),
        CheckConstraint('duration_days > 0', name='ck_duration_positive'),
        CheckConstraint('rating >= 0 AND rating <= 5', name='ck_rating_range'),
    )

    def __repr__(self):
        return f"<LearningResource(id={self.id}, title='{self.title}', type='{self.type}', duration={self.duration_days} days)>"

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'provider': self.provider,
            'url': self.url,
            'duration_days': self.duration_days,
            'difficulty': self.difficulty,
            'cost': self.cost,
            'skills_covered': self.skills_covered,
            'prerequisites': self.prerequisites,
            'completion_certificate': self.completion_certificate,
            'rating': float(self.rating) if self.rating else None,
            'language': self.language,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class UserLearningPlan(Base):
    """
    Represents a user's learning plan to address a specific gap.
    Contains multiple learning resources organized into a timeline.
    """
    __tablename__ = 'user_learning_plans'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(String(255), nullable=False)  # Email or user ID from frontend
    gap_id = Column(String(255))  # Reference to gap from Phase 3 scoring
    gap_title = Column(String(255))
    gap_description = Column(Text)
    resource_ids = Column(JSONB, nullable=False, default=list)  # Array of resource UUIDs
    status = Column(
        String(50),
        nullable=False,
        default='suggested'
        # suggested, in_progress, completed, abandoned
    )
    notes = Column(Text)  # User's notes about the learning plan
    target_completion_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    progress_entries = relationship("UserResourceProgress", back_populates="learning_plan", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('suggested', 'in_progress', 'completed', 'abandoned')", name='ck_plan_status'),
    )

    def __repr__(self):
        return f"<UserLearningPlan(id={self.id}, user='{self.user_id}', gap='{self.gap_title}', status='{self.status}')>"

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'gap_id': self.gap_id,
            'gap_title': self.gap_title,
            'gap_description': self.gap_description,
            'resource_ids': self.resource_ids,
            'status': self.status,
            'notes': self.notes,
            'target_completion_date': self.target_completion_date.isoformat() if self.target_completion_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


class UserResourceProgress(Base):
    """
    Tracks individual resource completion within a learning plan.
    Allows users to mark resources as in-progress, completed, or skipped.
    """
    __tablename__ = 'user_resource_progress'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(String(255), nullable=False)
    learning_plan_id = Column(UUID(as_uuid=True), ForeignKey('user_learning_plans.id', ondelete='CASCADE'))
    resource_id = Column(UUID(as_uuid=True), ForeignKey('learning_resources.id', ondelete='CASCADE'))
    status = Column(
        String(50),
        nullable=False,
        default='not_started'
        # not_started, in_progress, completed, skipped
    )
    progress_percentage = Column(Integer, default=0)  # 0-100
    notes = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    learning_plan = relationship("UserLearningPlan", back_populates="progress_entries")
    resource = relationship("LearningResource", back_populates="progress_entries")

    __table_args__ = (
        CheckConstraint("status IN ('not_started', 'in_progress', 'completed', 'skipped')", name='ck_progress_status'),
        CheckConstraint('progress_percentage >= 0 AND progress_percentage <= 100', name='ck_progress_range'),
        UniqueConstraint('user_id', 'resource_id', name='uq_user_resource'),
    )

    def __repr__(self):
        return f"<UserResourceProgress(user='{self.user_id}', resource={self.resource_id}, status='{self.status}', progress={self.progress_percentage}%)>"

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'learning_plan_id': str(self.learning_plan_id) if self.learning_plan_id else None,
            'resource_id': str(self.resource_id) if self.resource_id else None,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'notes': self.notes,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class AnswerQualityLog(Base):
    """
    Logs answer quality evaluation and refinement process.
    Tracks how answers improve through AI-powered feedback iterations.
    """
    __tablename__ = 'answer_quality_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(String(255))
    question_id = Column(String(255), nullable=False)
    gap_id = Column(String(255))  # Related gap from scoring phase
    original_answer = Column(Text, nullable=False)
    quality_score = Column(Integer)  # 1-10
    quality_issues = Column(JSONB, default=list)  # Array of issue strings
    improvement_suggestions = Column(JSONB, default=list)  # Array of suggestion objects
    refined_answer = Column(Text)  # Final improved answer after refinement
    iteration_count = Column(Integer, default=1)  # Number of refinement iterations
    accepted_by_user = Column(Boolean, default=False)  # Did user accept refined answer
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('quality_score >= 1 AND quality_score <= 10', name='ck_quality_score_range'),
    )

    def __repr__(self):
        return f"<AnswerQualityLog(question='{self.question_id}', score={self.quality_score}, iterations={self.iteration_count})>"

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'question_id': self.question_id,
            'gap_id': self.gap_id,
            'original_answer': self.original_answer,
            'quality_score': self.quality_score,
            'quality_issues': self.quality_issues,
            'improvement_suggestions': self.improvement_suggestions,
            'refined_answer': self.refined_answer,
            'iteration_count': self.iteration_count,
            'accepted_by_user': self.accepted_by_user,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
