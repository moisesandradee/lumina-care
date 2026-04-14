# =============================================================================
# ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
# Esta implementação representa uma proposta arquitetural, não código de produção.
# =============================================================================
"""
Lumina Care — Longitudinal Symptom Tracking Models
Tracks serial assessment scores over time to detect clinically meaningful
trajectory patterns and surface deterioration early.

Clinical basis:
- A ≥5 point change on PHQ-9 or GAD-7 is considered clinically significant
  (validated minimal clinically important difference — MCID)
- WHO-5 ≤50 (raw score ≤12.5/25) warrants clinical attention for wellbeing
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TrajectoryPattern(str, Enum):
    SUSTAINED_IMPROVEMENT = "sustained_improvement"
    SUSTAINED_DETERIORATION = "sustained_deterioration"
    ACUTE_DETERIORATION = "acute_deterioration"       # ≥5 point jump in last 1–2 assessments
    FLUCTUATING = "fluctuating"
    STABLE_HIGH = "stable_high"                       # Stable but in clinically elevated range
    STABLE_LOW = "stable_low"                         # Stable and in subclinical range
    INSUFFICIENT_DATA = "insufficient_data"


class SymptomDataPoint(BaseModel):
    """A single timed assessment score — the atomic unit of a symptom trajectory."""
    assessed_at: datetime
    instrument: str = Field(..., description="e.g., 'PHQ-9', 'GAD-7', 'WHO-5'")
    score: int
    severity_label: str
    clinician_id: Optional[str] = None
    source: str = Field("clinical_session", description="'clinical_session' | 'digital_checkin'")


class SymptomTrajectory(BaseModel):
    """
    Computed trajectory for a single clinical instrument over time.
    The trajectory is the core longitudinal signal — it answers:
    'Is this patient getting better, worse, or staying the same?'
    """
    patient_id: str
    instrument: str
    data_points: list[SymptomDataPoint]
    pattern: TrajectoryPattern
    trend_direction: str = Field(..., description="improving | stable | deteriorating | insufficient_data")
    peak_score: int = Field(..., description="Highest recorded score across all data points")
    current_score: int = Field(..., description="Most recent assessment score")
    score_change_first_to_last: Optional[int] = Field(
        None, description="Change from earliest to most recent score (negative = improvement)"
    )
    score_change_90d: Optional[int] = Field(
        None, description="Change over last 3 assessments (proxy for 90-day window)"
    )
    clinical_significance: bool = Field(
        False, description="True if overall change ≥ MCID (5 points for PHQ-9/GAD-7)"
    )


class TrajectoryInsight(BaseModel):
    """
    AI-generated interpretation of a patient's symptom trajectory.
    Surfaces patterns and clinical implications that serial scores alone may not communicate.
    Always advisory — clinician review required.
    """
    patient_id: str
    summary: str
    trajectory_pattern: TrajectoryPattern
    risk_implications: list[str]
    suggested_clinical_focus: list[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    disclaimer: str = Field(
        default=(
            "AI-generated trajectory analysis. Advisory only. "
            "Clinical context and judgment required before care decisions."
        )
    )


class PopulationCohortFilter(BaseModel):
    """Criteria for defining a patient cohort for population analytics."""
    risk_level: Optional[str] = None         # Filter to specific risk level
    care_intensity: Optional[str] = None     # Filter to care intensity
    min_days_enrolled: Optional[int] = None  # Enrolled for at least N days
    trajectory_pattern: Optional[str] = None # Filter to a specific trajectory


class PopulationCohort(BaseModel):
    """
    Aggregate analytics for a subgroup of patients.
    All data is de-identified — no individual patient signals.
    Designed for clinical director and population health views.
    """
    cohort_name: str
    care_team_id: str
    filter_criteria: dict
    patient_count: int
    risk_distribution: dict[str, int]
    trajectory_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Count of patients per trajectory pattern"
    )
    mean_phq9: Optional[float] = None
    mean_gad7: Optional[float] = None
    mean_who5_percentage: Optional[float] = None
    assessment_coverage_30d: dict[str, float] = Field(
        default_factory=dict,
        description="Proportion of cohort assessed per instrument in last 30 days"
    )
    acute_deterioration_count: int = Field(
        0, description="Patients with ACUTE_DETERIORATION trajectory pattern"
    )
    trend_summary: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
