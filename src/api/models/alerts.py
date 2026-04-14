# =============================================================================
# ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
# Esta implementação representa uma proposta arquitetural, não código de produção.
# =============================================================================
"""
Lumina Care — Alert & Care Flag Models
Structured event-driven alerting for clinical risk signals.

Alert types cover the full spectrum of care signals:
- Risk escalation (triage-driven)
- Care continuity gaps (contact recency)
- Assessment score deterioration (≥5 point change)
- Safety signals (C-SSRS positive)
- Digital check-in concerns (WHO-5 low, self-harm flag)
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    URGENT = "urgent"
    CRITICAL = "critical"


class AlertType(str, Enum):
    RISK_ESCALATION = "risk_escalation"               # Risk level increased
    CARE_GAP = "care_gap"                             # No contact > threshold
    SCORE_DETERIORATION = "score_deterioration"       # PHQ-9/GAD-7 jump ≥ 5 pts
    SAFETY_SIGNAL = "safety_signal"                   # C-SSRS positive
    ASSESSMENT_DUE = "assessment_due"                 # Assessment overdue
    MISSED_APPOINTMENT = "missed_appointment"         # Patient no-show
    DIGITAL_CHECKIN_CONCERN = "digital_checkin_concern"  # WHO-5 low / self-harm flag


class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class CareFlag(BaseModel):
    """A clinical flag requiring attention by the care team."""
    id: str
    patient_id: str
    care_team_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    triggered_at: datetime
    status: AlertStatus = AlertStatus.OPEN
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    auto_resolved: bool = False
    triage_id: Optional[str] = Field(None, description="Link to triggering triage run")


class AlertAcknowledgement(BaseModel):
    alert_id: str
    clinician_id: str
    notes: Optional[str] = None


class AlertResolution(BaseModel):
    alert_id: str
    clinician_id: str
    resolution_notes: str


class AlertSummaryResponse(BaseModel):
    """Summary of active care alerts for a care team."""
    care_team_id: str
    total_open: int
    critical_count: int
    urgent_count: int
    alerts: list[CareFlag]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
