# =============================================================================
# ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
# Esta implementação representa uma proposta arquitetural, não código de produção.
# =============================================================================
"""
Lumina Care — Care Plan Models
Structured, goal-oriented care plans generated from patient risk profiles.

Design principles:
- AI generates recommendations; clinicians own the plan
- Goals are measurable and time-bound (linked to clinical instruments)
- Interventions are typed and traceable
- Every plan version is preserved for audit
- Clinical override is always available and logged
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class InterventionType(str, Enum):
    PSYCHOTHERAPY = "psychotherapy"
    MEDICATION_REVIEW = "medication_review"
    CRISIS_PLAN = "crisis_plan"
    PEER_SUPPORT = "peer_support"
    DIGITAL_MONITORING = "digital_monitoring"
    CARE_COORDINATOR_CONTACT = "care_coordinator_contact"
    ASSESSMENT_SCHEDULE = "assessment_schedule"
    FAMILY_ENGAGEMENT = "family_engagement"
    SAFE_MESSAGING = "safe_messaging"                # Crisis-safe communication protocol
    PSYCHIATRIC_REFERRAL = "psychiatric_referral"


class GoalStatus(str, Enum):
    ACTIVE = "active"
    ACHIEVED = "achieved"
    PAUSED = "paused"
    DISCONTINUED = "discontinued"


class CarePlanGoal(BaseModel):
    """A measurable, time-bound clinical goal — the 'why' of the care plan."""
    id: str
    description: str
    target_metric: Optional[str] = Field(None, description="e.g., 'PHQ-9', 'GAD-7', 'WHO-5'")
    target_value: Optional[float] = Field(None, description="Numeric target (e.g., PHQ-9 < 9)")
    baseline_value: Optional[float] = Field(None, description="Score at care plan creation")
    current_value: Optional[float] = Field(None, description="Most recent score for this metric")
    status: GoalStatus = GoalStatus.ACTIVE
    target_date: Optional[datetime] = None
    progress_notes: Optional[str] = None


class PlannedIntervention(BaseModel):
    """A discrete care intervention — the 'how' of the care plan."""
    id: str
    intervention_type: InterventionType
    description: str
    frequency: str = Field(..., description="e.g., 'Weekly', 'Biweekly', 'As needed'")
    responsible_role: str = Field(..., description="e.g., 'Clinician', 'Care Coordinator', 'Patient'")
    start_date: datetime
    end_date: Optional[datetime] = None
    active: bool = True
    rationale: str = Field(..., description="Evidence basis or clinical reasoning for this intervention")


class CarePlan(BaseModel):
    """
    A structured, versioned care plan for a patient.
    AI generates recommendations; the clinician owns, adapts, and approves.
    Every change creates a new version — the full history is preserved.
    """
    id: str
    patient_id: str
    care_team_id: str
    created_by_clinician_id: str
    created_at: datetime
    updated_at: datetime
    risk_level_at_creation: str
    goals: list[CarePlanGoal]
    interventions: list[PlannedIntervention]
    contact_frequency_days: int = Field(
        14, description="Target days between scheduled care contacts"
    )
    review_date: datetime = Field(
        ..., description="When this plan should be formally reviewed and updated"
    )
    ai_recommendation_summary: Optional[str] = None
    ai_recommendation_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    clinician_override_notes: Optional[str] = Field(
        None, description="Clinician modifications to AI recommendation, with rationale"
    )
    version: int = Field(1, description="Incremented on every plan update")


class CarePlanRecommendationRequest(BaseModel):
    """Input for AI care plan generation."""
    patient_id: str
    current_risk_level: str
    risk_dimensions: list[dict]
    trend: str
    days_since_last_contact: Optional[int] = None
    existing_plan_summary: Optional[str] = None
    requesting_clinician_id: str


class CarePlanRecommendationResponse(BaseModel):
    """
    AI-generated care plan recommendations.
    Advisory only — must be reviewed, adapted, and approved by the clinician.
    """
    patient_id: str
    recommended_contact_frequency_days: int
    suggested_interventions: list[dict]
    suggested_goals: list[dict]
    ai_rationale: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    disclaimer: str = Field(
        default=(
            "AI-generated recommendations. Advisory only. "
            "Clinician must review, adapt, and explicitly approve before activation. "
            "Clinical authority is always preserved."
        )
    )
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
