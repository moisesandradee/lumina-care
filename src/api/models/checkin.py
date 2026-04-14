# =============================================================================
# ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
# Esta implementação representa uma proposta arquitetural, não código de produção.
# =============================================================================
"""
Lumina Care — Digital Check-in Models
Patient self-report between clinical sessions via the Lumina patient app.

Clinical instruments:
- WHO-5 Wellbeing Index (5 items, 0–5 each → total 0–25, multiply by 4 → 0–100)
  ≤28 = low wellbeing → warrants clinical attention
  29–52 = moderate wellbeing
  >52 = good wellbeing
- Structured symptom prompts (mood, sleep, social engagement)
- Single-item safety screen (self-harm ideation → auto-escalation)

Design principles:
- No free-text stored — only structured, codable responses
- Self-harm flag triggers immediate clinical review regardless of other scores
- Patient receives a safe, non-alarming message — escalation is silent to the system
- All responses are de-identified before any processing
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class MoodLevel(int, Enum):
    VERY_LOW = 1
    LOW = 2
    NEUTRAL = 3
    GOOD = 4
    VERY_GOOD = 5


class SleepQuality(str, Enum):
    VERY_POOR = "very_poor"
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


class DigitalCheckin(BaseModel):
    """
    Patient self-report check-in submitted between clinical sessions.
    Combines WHO-5 Wellbeing Index with structured symptom prompts.

    The WHO-5 is a validated, widely used measure of subjective wellbeing.
    It is NOT a diagnostic instrument — it screens for wellbeing, not disorder.
    """
    patient_id: str

    # WHO-5 Wellbeing Index items (each 0–5: 0=none of the time, 5=all of the time)
    who5_cheerful: int = Field(..., ge=0, le=5, description="I have felt cheerful and in good spirits")
    who5_calm: int = Field(..., ge=0, le=5, description="I have felt calm and relaxed")
    who5_active: int = Field(..., ge=0, le=5, description="I have felt active and vigorous")
    who5_refreshed: int = Field(..., ge=0, le=5, description="I woke up feeling fresh and rested")
    who5_interesting: int = Field(..., ge=0, le=5, description="My daily life has been filled with things that interest me")

    # Structured symptom prompts
    mood_level: MoodLevel
    sleep_quality: SleepQuality
    social_engagement: int = Field(..., ge=1, le=5, description="Social engagement level this week (1=very isolated, 5=very connected)")
    medication_adherence: Optional[bool] = Field(None, description="Took medications as prescribed (null if not applicable)")

    # Safety screen — single item, binary, mandatory
    any_thoughts_of_self_harm: bool = Field(
        ...,
        description=(
            "Have you had any thoughts of harming yourself this week? "
            "A positive response triggers immediate clinical review."
        )
    )

    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CheckinConcernLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SAFETY = "safety"    # Auto-escalation — C-SSRS/self-harm positive


class CheckinAnalysis(BaseModel):
    """Computed clinical analysis of a digital check-in submission."""
    who5_total: int = Field(..., ge=0, le=25, description="WHO-5 raw total (0–25)")
    who5_percentage: float = Field(..., description="WHO-5 as percentage of maximum (0–100)")
    wellbeing_band: str = Field(..., description="low (≤28%) | moderate (29–52%) | high (>52%)")
    concern_signals: list[str] = Field(
        default_factory=list,
        description="List of structured concern signals identified in this check-in"
    )
    concern_level: CheckinConcernLevel
    requires_clinical_review: bool = Field(
        ..., description="True if any threshold is crossed that warrants clinician attention"
    )
    auto_alert_triggered: bool = Field(
        ..., description="True if a safety signal triggered an automatic care team alert"
    )


class CheckinResponse(BaseModel):
    """Response returned to the patient after submitting a check-in."""
    checkin_id: str
    patient_id: str
    received_at: datetime
    analysis: CheckinAnalysis
    message_to_patient: str = Field(
        ...,
        description=(
            "Safe, supportive message shown to the patient. "
            "Never reveals concern level or whether an alert was triggered."
        )
    )
