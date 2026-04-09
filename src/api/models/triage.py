# =============================================================================
# ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
# Esta implementação representa uma proposta arquitetural, não código de produção.
# =============================================================================
"""
Lumina Care — Triage Data Models
Pydantic models for triage request/response schemas.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    ACUTE = "acute"


class TrendDirection(str, Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    DETERIORATING = "deteriorating"
    INSUFFICIENT_DATA = "insufficient_data"


class RecommendedAction(str, Enum):
    ROUTINE_FOLLOW_UP = "routine_follow_up"
    ENHANCED_MONITORING = "enhanced_monitoring"
    PRIORITY_CONTACT = "priority_contact"
    URGENT_CLINICAL_REVIEW = "urgent_clinical_review"
    IMMEDIATE_ESCALATION = "immediate_escalation"


# ---------------------------------------------------------------------------
# Assessment Input Models
# ---------------------------------------------------------------------------

class PHQ9Input(BaseModel):
    """Patient Health Questionnaire-9 scores."""
    total_score: int = Field(..., ge=0, le=27, description="PHQ-9 total score (0–27)")
    assessed_at: datetime
    clinician_id: Optional[str] = None

    @field_validator("total_score")
    @classmethod
    def validate_phq9_range(cls, v: int) -> int:
        if v < 0 or v > 27:
            raise ValueError("PHQ-9 score must be between 0 and 27")
        return v


class GAD7Input(BaseModel):
    """Generalized Anxiety Disorder-7 scores."""
    total_score: int = Field(..., ge=0, le=21, description="GAD-7 total score (0–21)")
    assessed_at: datetime
    clinician_id: Optional[str] = None


class CSSRSInput(BaseModel):
    """Columbia Suicide Severity Rating Scale flags."""
    ideation_present: bool = Field(..., description="Any suicidal ideation present")
    ideation_intensity: Optional[int] = Field(
        None, ge=0, le=5, description="Ideation intensity 0–5"
    )
    behavior_present: bool = Field(..., description="Any suicidal behavior present")
    assessed_at: datetime
    clinician_id: Optional[str] = None


class AssessmentBundle(BaseModel):
    """Bundle of one or more clinical assessment instruments."""
    phq9: Optional[PHQ9Input] = None
    gad7: Optional[GAD7Input] = None
    cssrs: Optional[CSSRSInput] = None
    days_since_last_contact: Optional[int] = Field(
        None, ge=0, description="Days since last recorded care contact"
    )
    appointment_adherence_rate: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Proportion of scheduled appointments attended (0–1)"
    )


# ---------------------------------------------------------------------------
# Triage Request
# ---------------------------------------------------------------------------

class TriageRequest(BaseModel):
    """
    Request to triage a patient based on clinical assessment data.
    All patient references use internal IDs — no PII in this payload.
    """
    patient_id: str = Field(..., description="Internal patient identifier (not PII)")
    assessments: AssessmentBundle
    include_ai_analysis: bool = Field(
        True, description="Whether to include AI-powered signal analysis"
    )
    requesting_clinician_id: str = Field(..., description="Clinician requesting the triage")


# ---------------------------------------------------------------------------
# Triage Response Models
# ---------------------------------------------------------------------------

class RiskDimension(BaseModel):
    """A single dimension of the psychosocial risk profile."""
    dimension: str = Field(..., description="Risk dimension name (e.g., 'safety', 'functioning')")
    level: RiskLevel
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized dimension score")
    contributing_signals: list[str] = Field(default_factory=list)


class AISignalAnalysis(BaseModel):
    """
    AI-generated clinical signal analysis.
    Always advisory — requires human clinical review.
    """
    summary: str = Field(..., description="Human-readable signal summary")
    key_signals: list[str] = Field(..., description="Identified clinical signals")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence estimate")
    reasoning: str = Field(..., description="Explanation of the analysis")
    evidence_refs: list[str] = Field(default_factory=list, description="Clinical framework references")
    escalation_required: bool = Field(
        ..., description="Whether immediate human escalation is indicated"
    )
    disclaimer: str = Field(
        default=(
            "This analysis is AI-generated and advisory only. "
            "Clinical judgment and human review are required before any care decision."
        )
    )
    model_version: str = Field(..., description="AI model version used")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class TriageResponse(BaseModel):
    """
    Complete triage response for a patient.
    Includes risk profile, trend, and optional AI analysis.
    """
    patient_id: str
    triage_id: str = Field(..., description="Unique identifier for this triage run")
    overall_risk_level: RiskLevel
    risk_dimensions: list[RiskDimension]
    trend: TrendDirection
    recommended_action: RecommendedAction
    priority_score: float = Field(
        ..., ge=0.0, le=100.0,
        description="Numeric priority score for queue ordering (higher = higher priority)"
    )
    ai_analysis: Optional[AISignalAnalysis] = None
    computed_at: datetime = Field(default_factory=datetime.utcnow)
    requires_override_review: bool = Field(
        False, description="Whether this triage was automatically flagged for mandatory clinician review"
    )


# ---------------------------------------------------------------------------
# Priority Queue
# ---------------------------------------------------------------------------

class PriorityQueueEntry(BaseModel):
    """A single entry in the clinical priority queue."""
    patient_id: str
    triage_id: str
    overall_risk_level: RiskLevel
    priority_score: float
    primary_signal: str = Field(..., description="Most significant risk signal driving priority")
    days_since_last_contact: Optional[int] = None
    recommended_action: RecommendedAction
    computed_at: datetime


class PriorityQueueResponse(BaseModel):
    """Paginated priority queue for a care team."""
    entries: list[PriorityQueueEntry]
    total_count: int
    high_urgency_count: int = Field(
        ..., description="Number of entries at HIGH or ACUTE risk level"
    )
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    care_team_id: str
