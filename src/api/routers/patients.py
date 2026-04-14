# =============================================================================
# ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
# Esta implementação representa uma proposta arquitetural, não código de produção.
# =============================================================================
"""
Lumina Care — Patients Router
Endpoints for patient data management, assessment submission,
longitudinal trajectory retrieval, and care flag management.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter

from models.patient import PatientSummary, CareStatus, CareIntensity
from models.longitudinal import (
    SymptomDataPoint,
    SymptomTrajectory,
    TrajectoryPattern,
)
from models.alerts import AlertSeverity, AlertStatus, AlertType, CareFlag
from services.longitudinal import LongitudinalAnalysisService

router = APIRouter()
longitudinal_service = LongitudinalAnalysisService()


@router.get(
    "/{patient_id}",
    response_model=PatientSummary,
    summary="Get patient summary",
    description="Retrieve a lightweight patient summary for clinical queue and overview views.",
)
async def get_patient_summary(patient_id: str) -> PatientSummary:
    """Retrieve a patient summary for clinical review."""
    # Production: query patient record from database
    return PatientSummary(
        id=patient_id,
        care_team_id="team_alpha",
        care_status=CareStatus.ACTIVE,
        care_intensity=CareIntensity.ENHANCED,
        days_since_last_contact=8,
        current_risk_level="moderate",
        assigned_clinician_id="clin_dr_tavares",
        open_flags=2,
    )


@router.post(
    "/{patient_id}/assessment",
    summary="Submit clinical assessment",
    description=(
        "Submit a completed clinical assessment for a patient. "
        "Triggers automatic re-scoring of the patient's risk profile "
        "and updates the longitudinal trajectory."
    ),
)
async def submit_assessment(
    patient_id: str,
    instrument: str,
    scores: dict,
    clinician_id: str,
) -> dict:
    """Submit a new clinical assessment for a patient."""
    assessment_id = str(uuid.uuid4())
    # Production: persist to database, trigger async risk re-computation,
    # update longitudinal trajectory, check for alert conditions
    return {
        "assessment_id": assessment_id,
        "patient_id": patient_id,
        "instrument": instrument,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "status": "processing",
        "message": (
            "Assessment received. Risk profile will be updated within 60 seconds. "
            "Longitudinal trajectory will be recomputed."
        ),
    }


@router.get(
    "/{patient_id}/timeline",
    summary="Get patient care timeline",
    description=(
        "Returns a chronological record of care interactions, assessment results, "
        "and digital check-ins. Ordered most recent first."
    ),
)
async def get_patient_timeline(
    patient_id: str,
    limit: int = 30,
) -> dict:
    """Retrieve chronological care timeline for a patient."""
    # Production: query event store ordered by occurred_at DESC
    now = datetime.now(timezone.utc)
    return {
        "patient_id": patient_id,
        "timeline": [
            {
                "event_id": str(uuid.uuid4()),
                "date": (now - timedelta(days=2)).date().isoformat(),
                "type": "digital_checkin",
                "source": "patient_app",
                "summary": "WHO-5: 14/25 (56%) — good wellbeing. No concerns.",
            },
            {
                "event_id": str(uuid.uuid4()),
                "date": (now - timedelta(days=8)).date().isoformat(),
                "type": "scheduled_session",
                "clinician_id": "clin_dr_tavares",
                "notes": "Session completed. CBT session 5/12. Patient reports improved motivation.",
            },
            {
                "event_id": str(uuid.uuid4()),
                "date": (now - timedelta(days=10)).date().isoformat(),
                "type": "assessment",
                "instrument": "PHQ-9",
                "score": 12,
                "severity": "moderate",
                "change_from_previous": -2,
                "clinical_note": "Decreased 2 points from last assessment (14 → 12). Stable trend.",
            },
            {
                "event_id": str(uuid.uuid4()),
                "date": (now - timedelta(days=14)).date().isoformat(),
                "type": "digital_checkin",
                "source": "patient_app",
                "summary": "WHO-5: 10/25 (40%) — moderate wellbeing. Low mood flagged.",
                "triggered_review": True,
            },
            {
                "event_id": str(uuid.uuid4()),
                "date": (now - timedelta(days=22)).date().isoformat(),
                "type": "scheduled_session",
                "clinician_id": "clin_dr_tavares",
                "notes": "Session completed. Reviewed care plan goals. PHQ-9 administered.",
            },
            {
                "event_id": str(uuid.uuid4()),
                "date": (now - timedelta(days=24)).date().isoformat(),
                "type": "assessment",
                "instrument": "PHQ-9",
                "score": 14,
                "severity": "moderate",
                "change_from_previous": 8,
                "clinical_note": "Increased 8 points (6 → 14) — alert triggered.",
            },
            {
                "event_id": str(uuid.uuid4()),
                "date": (now - timedelta(days=24)).date().isoformat(),
                "type": "assessment",
                "instrument": "GAD-7",
                "score": 9,
                "severity": "mild",
            },
        ],
        "total_events": 24,
        "limit": limit,
    }


@router.get(
    "/{patient_id}/longitudinal",
    summary="Get longitudinal symptom trajectories",
    description=(
        "Returns computed symptom trajectories for all available instruments. "
        "Each trajectory classifies the patient's score pattern over time: "
        "sustained improvement, acute deterioration, fluctuating, stable, etc."
    ),
)
async def get_longitudinal_trajectories(patient_id: str) -> dict:
    """
    Retrieve computed longitudinal symptom trajectories for a patient.
    Trajectories are computed from serial assessment data.
    """
    now = datetime.now(timezone.utc)

    # Production: query assessment history from database, compute trajectories
    # Here we compute real trajectory objects from stub data

    phq9_points = [
        SymptomDataPoint(assessed_at=now - timedelta(days=90), instrument="PHQ-9", score=6, severity_label="mild"),
        SymptomDataPoint(assessed_at=now - timedelta(days=60), instrument="PHQ-9", score=8, severity_label="mild"),
        SymptomDataPoint(assessed_at=now - timedelta(days=38), instrument="PHQ-9", score=10, severity_label="moderate"),
        SymptomDataPoint(assessed_at=now - timedelta(days=24), instrument="PHQ-9", score=14, severity_label="moderate"),
        SymptomDataPoint(assessed_at=now - timedelta(days=10), instrument="PHQ-9", score=12, severity_label="moderate"),
    ]

    gad7_points = [
        SymptomDataPoint(assessed_at=now - timedelta(days=90), instrument="GAD-7", score=5, severity_label="mild"),
        SymptomDataPoint(assessed_at=now - timedelta(days=60), instrument="GAD-7", score=7, severity_label="mild"),
        SymptomDataPoint(assessed_at=now - timedelta(days=24), instrument="GAD-7", score=9, severity_label="mild"),
        SymptomDataPoint(assessed_at=now - timedelta(days=10), instrument="GAD-7", score=8, severity_label="mild"),
    ]

    phq9_trajectory = longitudinal_service.compute_trajectory(patient_id, "PHQ-9", phq9_points)
    gad7_trajectory = longitudinal_service.compute_trajectory(patient_id, "GAD-7", gad7_points)

    def trajectory_to_dict(t: SymptomTrajectory) -> dict:
        return {
            "instrument": t.instrument,
            "pattern": t.pattern,
            "trend_direction": t.trend_direction,
            "current_score": t.current_score,
            "peak_score": t.peak_score,
            "score_change_first_to_last": t.score_change_first_to_last,
            "score_change_90d": t.score_change_90d,
            "clinical_significance": t.clinical_significance,
            "data_points": [
                {
                    "assessed_at": p.assessed_at.isoformat(),
                    "score": p.score,
                    "severity_label": p.severity_label,
                }
                for p in t.data_points
            ],
        }

    return {
        "patient_id": patient_id,
        "trajectories": [
            trajectory_to_dict(phq9_trajectory),
            trajectory_to_dict(gad7_trajectory),
        ],
        "computed_at": now.isoformat(),
        "disclaimer": (
            "Trajectory analysis is derived from available assessment data. "
            "Clinical context and judgment are required for interpretation."
        ),
    }


@router.get(
    "/{patient_id}/flags",
    summary="Get open care flags for a patient",
    description="Returns all open clinical flags for a patient, ordered by severity.",
)
async def get_patient_flags(patient_id: str) -> dict:
    """Retrieve open care flags for a specific patient."""
    flags = [
        CareFlag(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            care_team_id="team_alpha",
            alert_type=AlertType.SCORE_DETERIORATION,
            severity=AlertSeverity.URGENT,
            title="PHQ-9 deterioration — 8 point increase",
            description=(
                "PHQ-9 increased from 6 to 14 since last assessment. "
                "Crosses the MCID threshold (≥5 points). "
                "Patient has moved from mild into moderate depression range."
            ),
            triggered_at=datetime.now(timezone.utc) - timedelta(days=10),
            status=AlertStatus.OPEN,
        ),
        CareFlag(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            care_team_id="team_alpha",
            alert_type=AlertType.ASSESSMENT_DUE,
            severity=AlertSeverity.INFO,
            title="GAD-7 reassessment due",
            description="GAD-7 was last administered 38 days ago. Monthly reassessment recommended.",
            triggered_at=datetime.now(timezone.utc) - timedelta(days=8),
            status=AlertStatus.OPEN,
        ),
    ]

    return {
        "patient_id": patient_id,
        "open_flags": [f.model_dump() for f in flags],
        "total_open": len(flags),
        "urgent_count": sum(1 for f in flags if f.severity == AlertSeverity.URGENT),
    }
