# =============================================================================
# ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
# Esta implementação representa uma proposta arquitetural, não código de produção.
# =============================================================================
"""
Lumina Care — Triage Router
Endpoints for psychosocial risk triage and patient priority queue.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Header
from typing import Optional

from models.triage import (
    TriageRequest,
    TriageResponse,
    PriorityQueueResponse,
    PriorityQueueEntry,
    RiskLevel,
    TrendDirection,
    RecommendedAction,
)
from services.risk_analysis import RiskAnalysisService
from services.ai_service import AIService

router = APIRouter()
risk_service = RiskAnalysisService()
ai_service = AIService()


@router.post(
    "/analyze",
    response_model=TriageResponse,
    summary="Analyze patient risk signals",
    description=(
        "Submits patient assessment data for psychosocial risk triage. "
        "Returns a structured risk profile with optional AI-generated signal analysis. "
        "All AI outputs are advisory and require human clinical review."
    ),
)
async def analyze_patient_risk(
    request: TriageRequest,
    x_clinician_id: Optional[str] = Header(None, description="Clinician authorization header"),
) -> TriageResponse:
    """
    Analyze a patient's psychosocial risk from assessment data.

    Combines validated clinical instrument scoring with optional AI analysis.
    Returns risk profile, priority score, and recommended clinical action.
    """
    triage_id = str(uuid.uuid4())

    # Compute rule-based risk profile
    overall_risk, dimensions, priority_score = risk_service.compute_risk_profile(
        request.assessments
    )

    # Determine symptom trend (simplified — would use longitudinal data in production)
    trend = TrendDirection.INSUFFICIENT_DATA

    # Determine recommended action
    recommended_action = risk_service.determine_recommended_action(
        risk_level=overall_risk,
        trend=trend,
        days_since_contact=request.assessments.days_since_last_contact,
    )

    # AI analysis (optional, gracefully skipped if unavailable)
    ai_analysis = None
    if request.include_ai_analysis:
        clinical_signals = _build_clinical_signals_dict(request)
        ai_analysis = ai_service.analyze_triage_signals(
            patient_id=request.patient_id,
            clinical_signals=clinical_signals,
            requesting_clinician_id=request.requesting_clinician_id,
        )

    # Acute safety signals always require override review
    requires_override_review = overall_risk == RiskLevel.ACUTE

    return TriageResponse(
        patient_id=request.patient_id,
        triage_id=triage_id,
        overall_risk_level=overall_risk,
        risk_dimensions=dimensions,
        trend=trend,
        recommended_action=recommended_action,
        priority_score=priority_score,
        ai_analysis=ai_analysis,
        computed_at=datetime.now(timezone.utc),
        requires_override_review=requires_override_review,
    )


@router.get(
    "/queue",
    response_model=PriorityQueueResponse,
    summary="Get prioritized patient queue",
    description=(
        "Returns a priority-ordered queue of patients requiring clinical attention, "
        "based on current risk profiles. Sorted by priority score descending."
    ),
)
async def get_priority_queue(
    care_team_id: str,
    risk_level_filter: Optional[RiskLevel] = None,
    limit: int = 20,
) -> PriorityQueueResponse:
    """
    Retrieve the clinical priority queue for a care team.

    Returns patients ordered by priority score (highest first).
    Optional filter by minimum risk level.
    """
    # In production, this queries the database for the care team's active patients
    # and their most recent triage results. Stub response for MVP.
    stub_entries = [
        PriorityQueueEntry(
            patient_id="pat_001",
            triage_id=str(uuid.uuid4()),
            overall_risk_level=RiskLevel.HIGH,
            priority_score=87.5,
            primary_signal="PHQ-9 score increased 8 points since last assessment",
            days_since_last_contact=12,
            recommended_action=RecommendedAction.PRIORITY_CONTACT,
            computed_at=datetime.now(timezone.utc),
        ),
        PriorityQueueEntry(
            patient_id="pat_007",
            triage_id=str(uuid.uuid4()),
            overall_risk_level=RiskLevel.MODERATE,
            priority_score=54.2,
            primary_signal="Care gap: 19 days since last contact",
            days_since_last_contact=19,
            recommended_action=RecommendedAction.ENHANCED_MONITORING,
            computed_at=datetime.now(timezone.utc),
        ),
    ]

    if risk_level_filter:
        level_order = [RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.ACUTE]
        min_idx = level_order.index(risk_level_filter)
        stub_entries = [
            e for e in stub_entries
            if level_order.index(e.overall_risk_level) >= min_idx
        ]

    high_urgency = sum(
        1 for e in stub_entries
        if e.overall_risk_level in (RiskLevel.HIGH, RiskLevel.ACUTE)
    )

    return PriorityQueueResponse(
        entries=stub_entries[:limit],
        total_count=len(stub_entries),
        high_urgency_count=high_urgency,
        generated_at=datetime.now(timezone.utc),
        care_team_id=care_team_id,
    )


@router.post(
    "/{triage_id}/override",
    summary="Submit clinical override",
    description=(
        "Allows a clinician to override an AI-generated triage assessment. "
        "All overrides are logged with clinician attribution. "
        "Override is always available — clinical judgment supersedes AI output."
    ),
)
async def submit_override(
    triage_id: str,
    clinician_id: str,
    new_risk_level: RiskLevel,
    rationale: str,
):
    """
    Submit a clinical override for a triage assessment.
    Logs the override with clinician attribution and rationale.
    """
    # In production: update risk snapshot, log override to audit table
    return {
        "triage_id": triage_id,
        "override_applied": True,
        "new_risk_level": new_risk_level,
        "overridden_by": clinician_id,
        "rationale": rationale,
        "logged_at": datetime.now(timezone.utc).isoformat(),
        "message": "Override applied and logged. Clinical judgment recorded.",
    }


def _build_clinical_signals_dict(request: TriageRequest) -> dict:
    """
    Builds a de-identified clinical signals dict for AI analysis.
    No PII is included — only structured clinical indicators.
    """
    signals = {
        "days_since_last_contact": request.assessments.days_since_last_contact,
        "appointment_adherence_rate": request.assessments.appointment_adherence_rate,
    }

    if request.assessments.phq9:
        signals["phq9_total_score"] = request.assessments.phq9.total_score
        signals["phq9_severity"] = _phq9_severity_label(request.assessments.phq9.total_score)

    if request.assessments.gad7:
        signals["gad7_total_score"] = request.assessments.gad7.total_score
        signals["gad7_severity"] = _gad7_severity_label(request.assessments.gad7.total_score)

    if request.assessments.cssrs:
        signals["cssrs_ideation_present"] = request.assessments.cssrs.ideation_present
        signals["cssrs_behavior_present"] = request.assessments.cssrs.behavior_present
        signals["cssrs_ideation_intensity"] = request.assessments.cssrs.ideation_intensity

    return signals


def _phq9_severity_label(score: int) -> str:
    if score >= 20: return "severe"
    if score >= 15: return "moderately_severe"
    if score >= 10: return "moderate"
    if score >= 5: return "mild"
    return "minimal"


def _gad7_severity_label(score: int) -> str:
    if score >= 15: return "severe"
    if score >= 10: return "moderate"
    if score >= 5: return "mild"
    return "minimal"
