# =============================================================================
# ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
# Esta implementação representa uma proposta arquitetural, não código de produção.
# =============================================================================
"""
Lumina Care — Patient Data Models
Internal patient representation — no PII stored or transmitted in these models.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class CareStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCHARGED = "discharged"
    ON_HOLD = "on_hold"


class CareIntensity(str, Enum):
    ROUTINE = "routine"
    ENHANCED = "enhanced"
    INTENSIVE = "intensive"
    CRISIS = "crisis"


class Patient(BaseModel):
    """
    Internal patient record.
    Uses internal IDs only — no PII.
    PII is managed in a separate, separately-secured identity system.
    """
    id: str
    external_ref: str = Field(
        ..., description="Opaque reference to external identity system (encrypted)"
    )
    care_team_id: str
    assigned_clinician_id: Optional[str] = None
    assigned_coordinator_id: Optional[str] = None
    care_status: CareStatus = CareStatus.ACTIVE
    care_intensity: CareIntensity = CareIntensity.ROUTINE
    enrollment_date: datetime
    last_contact_date: Optional[datetime] = None
    care_plan_contact_frequency_days: int = Field(
        14, description="Target number of days between care contacts"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CareInteraction(BaseModel):
    """Records a care contact between a patient and their care team."""
    id: str
    patient_id: str
    interaction_type: str = Field(
        ..., description="e.g., 'scheduled_session', 'outreach_call', 'digital_checkin'"
    )
    occurred_at: datetime
    clinician_id: Optional[str] = None
    coordinator_id: Optional[str] = None
    notes_hash: Optional[str] = Field(
        None, description="Hash of encrypted session notes (audit reference only)"
    )
    outcome: Optional[str] = None


class PatientSummary(BaseModel):
    """Lightweight patient summary for queue and list views."""
    id: str
    care_team_id: str
    care_status: CareStatus
    care_intensity: CareIntensity
    days_since_last_contact: Optional[int] = None
    current_risk_level: Optional[str] = None
    assigned_clinician_id: Optional[str] = None
    open_flags: int = 0


class AssessmentRecord(BaseModel):
    """Stored record of a completed clinical assessment."""
    id: str
    patient_id: str
    instrument: str = Field(..., description="e.g., 'PHQ-9', 'GAD-7', 'C-SSRS'")
    scores: dict = Field(..., description="Instrument scores as structured key-value pairs")
    total_score: Optional[float] = None
    severity_label: Optional[str] = None
    completed_at: datetime
    clinician_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
