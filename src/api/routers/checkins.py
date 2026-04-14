# =============================================================================
# ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
# Esta implementação representa uma proposta arquitetural, não código de produção.
# =============================================================================
"""
Lumina Care — Digital Check-in Router
Patient self-report between clinical sessions via the Lumina patient app.

Check-ins bridge the gap between scheduled sessions:
- WHO-5 Wellbeing Index tracks subjective wellbeing weekly
- Structured mood, sleep, and engagement prompts surface early signals
- Single-item safety screen provides a between-session C-SSRS proxy
- Any positive safety flag triggers a silent auto-alert to the care team

Design: patients see a supportive, non-alarming response.
Clinical alerts happen silently in the background.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter

from models.checkin import (
    CheckinAnalysis,
    CheckinConcernLevel,
    CheckinResponse,
    DigitalCheckin,
)

router = APIRouter()


@router.post(
    "/",
    response_model=CheckinResponse,
    summary="Submit a digital patient check-in",
    description=(
        "Patients submit structured self-report check-ins between sessions. "
        "Combines WHO-5 Wellbeing Index with mood, sleep, engagement, and safety prompts. "
        "Positive safety flag (self-harm ideation) triggers immediate silent alert to care team. "
        "Patient receives a safe, supportive response regardless of concern level."
    ),
)
async def submit_checkin(checkin: DigitalCheckin) -> CheckinResponse:
    """Process a patient digital check-in and compute wellbeing analysis."""
    checkin_id = str(uuid.uuid4())

    # WHO-5 scoring (0–25 raw → multiply by 4 for 0–100 scale)
    who5_total = (
        checkin.who5_cheerful
        + checkin.who5_calm
        + checkin.who5_active
        + checkin.who5_refreshed
        + checkin.who5_interesting
    )
    who5_pct = (who5_total / 25) * 100

    if who5_pct <= 28:
        wellbeing_band = "low"
    elif who5_pct <= 52:
        wellbeing_band = "moderate"
    else:
        wellbeing_band = "high"

    # Build structured concern signals
    concern_signals: list[str] = []

    if checkin.any_thoughts_of_self_harm:
        concern_signals.append("Safety flag: self-harm ideation reported — immediate clinical review triggered")

    if who5_pct <= 28:
        concern_signals.append(f"WHO-5 low wellbeing ({who5_pct:.0f}% of max — threshold ≤28%)")

    if checkin.mood_level <= 2:
        concern_signals.append(f"Low mood reported (level {checkin.mood_level}/5)")

    if checkin.sleep_quality in ("very_poor", "poor"):
        concern_signals.append(f"Poor sleep quality reported ({checkin.sleep_quality.replace('_', ' ')})")

    if checkin.social_engagement <= 2:
        concern_signals.append(f"Low social engagement (level {checkin.social_engagement}/5)")

    if checkin.medication_adherence is False:
        concern_signals.append("Medication non-adherence reported")

    # Determine concern level and review/alert flags
    auto_alert = checkin.any_thoughts_of_self_harm

    if auto_alert:
        concern_level = CheckinConcernLevel.SAFETY
        requires_review = True
    elif len(concern_signals) >= 3 or who5_pct <= 28:
        concern_level = CheckinConcernLevel.HIGH
        requires_review = True
    elif len(concern_signals) >= 2:
        concern_level = CheckinConcernLevel.MODERATE
        requires_review = True
    elif len(concern_signals) >= 1:
        concern_level = CheckinConcernLevel.LOW
        requires_review = False
    else:
        concern_level = CheckinConcernLevel.NONE
        requires_review = False

    # Patient-facing message — always supportive, never alarming
    if auto_alert:
        message = (
            "Thank you for sharing how you're feeling. "
            "Your care team has been notified and will reach out to you shortly. "
            "If you need immediate support, please contact a crisis line."
        )
    elif requires_review:
        message = (
            "Thank you for checking in. Your responses have been shared with your care team, "
            "who will review them before your next session. "
            "Keep going — we're here with you."
        )
    else:
        message = (
            "Thank you for checking in. "
            "Your care team can see your responses. "
            "See you at your next session."
        )

    return CheckinResponse(
        checkin_id=checkin_id,
        patient_id=checkin.patient_id,
        received_at=datetime.now(timezone.utc),
        analysis=CheckinAnalysis(
            who5_total=who5_total,
            who5_percentage=round(who5_pct, 1),
            wellbeing_band=wellbeing_band,
            concern_signals=concern_signals,
            concern_level=concern_level,
            requires_clinical_review=requires_review,
            auto_alert_triggered=auto_alert,
        ),
        message_to_patient=message,
    )


@router.get(
    "/{patient_id}",
    summary="Get digital check-in history for a patient",
    description="Returns a patient's check-in history ordered by submission date, most recent first.",
)
async def get_checkin_history(patient_id: str, limit: int = 10) -> dict:
    """Retrieve the digital check-in history for a patient."""
    # Production: query check-in store, join with concern analysis
    return {
        "patient_id": patient_id,
        "checkins": [
            {
                "checkin_id": str(uuid.uuid4()),
                "submitted_at": "2024-03-22T14:00:00Z",
                "who5_score": 14,
                "who5_percentage": 56.0,
                "wellbeing_band": "high",
                "mood_level": 4,
                "sleep_quality": "good",
                "concern_signals": [],
                "concern_level": "none",
                "required_review": False,
            },
            {
                "checkin_id": str(uuid.uuid4()),
                "submitted_at": "2024-03-15T11:30:00Z",
                "who5_score": 10,
                "who5_percentage": 40.0,
                "wellbeing_band": "moderate",
                "mood_level": 2,
                "sleep_quality": "poor",
                "concern_signals": ["Low mood reported (level 2/5)", "Poor sleep quality reported"],
                "concern_level": "moderate",
                "required_review": True,
            },
            {
                "checkin_id": str(uuid.uuid4()),
                "submitted_at": "2024-03-08T09:45:00Z",
                "who5_score": 8,
                "who5_percentage": 32.0,
                "wellbeing_band": "low",
                "mood_level": 2,
                "sleep_quality": "very_poor",
                "concern_signals": [
                    "WHO-5 low wellbeing (32% of max — threshold ≤28%)",
                    "Low mood reported (level 2/5)",
                    "Poor sleep quality reported (very poor)",
                ],
                "concern_level": "high",
                "required_review": True,
            },
        ],
        "total": 8,
        "requires_review_count": 2,
    }
