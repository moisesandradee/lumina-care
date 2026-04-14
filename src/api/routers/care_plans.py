# =============================================================================
# ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
# Esta implementação representa uma proposta arquitetural, não código de produção.
# =============================================================================
"""
Lumina Care — Care Plans Router
Adaptive, AI-assisted care plan generation and management.

Workflow:
  1. Triage produces risk profile
  2. Clinician requests AI recommendation (POST /recommend)
  3. AI generates structured suggestions (interventions + goals + cadence)
  4. Clinician reviews, adapts, and approves (POST /{patient_id})
  5. Plan is stored, versioned, and linked to ongoing triage runs
  6. Risk changes auto-trigger plan review recommendations

Clinical authority: the clinician owns the plan. AI recommends. Clinician decides.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Header

from models.care_plan import (
    CarePlan,
    CarePlanGoal,
    CarePlanRecommendationRequest,
    CarePlanRecommendationResponse,
    GoalStatus,
    InterventionType,
    PlannedIntervention,
)

router = APIRouter()


@router.get(
    "/{patient_id}",
    response_model=CarePlan,
    summary="Get active care plan for a patient",
    description="Returns the current active care plan including goals, interventions, and AI recommendation context.",
)
async def get_care_plan(patient_id: str) -> CarePlan:
    """Retrieve the active care plan for a patient."""
    now = datetime.now(timezone.utc)
    return CarePlan(
        id=str(uuid.uuid4()),
        patient_id=patient_id,
        care_team_id="team_alpha",
        created_by_clinician_id="clin_dr_tavares",
        created_at=now - timedelta(days=30),
        updated_at=now - timedelta(days=7),
        risk_level_at_creation="moderate",
        contact_frequency_days=14,
        review_date=now + timedelta(days=14),
        goals=[
            CarePlanGoal(
                id=str(uuid.uuid4()),
                description="Reduce depressive symptoms to mild range",
                target_metric="PHQ-9",
                target_value=9.0,
                baseline_value=14.0,
                current_value=12.0,
                status=GoalStatus.ACTIVE,
                target_date=now + timedelta(days=60),
                progress_notes="Score decreased 2 points in last 4 weeks. On track.",
            ),
            CarePlanGoal(
                id=str(uuid.uuid4()),
                description="Maintain WHO-5 wellbeing above 50% threshold",
                target_metric="WHO-5",
                target_value=13.0,
                baseline_value=9.0,
                current_value=11.0,
                status=GoalStatus.ACTIVE,
                target_date=now + timedelta(days=90),
            ),
        ],
        interventions=[
            PlannedIntervention(
                id=str(uuid.uuid4()),
                intervention_type=InterventionType.PSYCHOTHERAPY,
                description="Weekly CBT sessions focused on behavioural activation",
                frequency="Weekly",
                responsible_role="Clinician",
                start_date=now - timedelta(days=30),
                rationale=(
                    "PHQ-9 in moderate range (12/27). CBT with behavioural activation "
                    "is a first-line evidence-based intervention for moderate depression."
                ),
                active=True,
            ),
            PlannedIntervention(
                id=str(uuid.uuid4()),
                intervention_type=InterventionType.DIGITAL_MONITORING,
                description="Weekly digital check-in via Lumina patient app (WHO-5 + mood tracking)",
                frequency="Weekly",
                responsible_role="Care Coordinator",
                start_date=now - timedelta(days=30),
                rationale=(
                    "Enables between-session symptom monitoring. "
                    "Any WHO-5 ≤28% or low mood triggers an alert for clinical review."
                ),
                active=True,
            ),
            PlannedIntervention(
                id=str(uuid.uuid4()),
                intervention_type=InterventionType.ASSESSMENT_SCHEDULE,
                description="Monthly PHQ-9 and GAD-7 reassessment",
                frequency="Monthly",
                responsible_role="Clinician",
                start_date=now - timedelta(days=30),
                rationale=(
                    "Monthly reassessment tracks response to intervention. "
                    "A ≥5 point increase triggers automatic risk escalation."
                ),
                active=True,
            ),
        ],
        ai_recommendation_summary=(
            "PHQ-9 in moderate range (12/27) with a stable trend over the last 30 days. "
            "Current weekly session cadence is appropriate for moderate risk. "
            "Recommend maintaining biweekly coordinator check-ins and monthly formal reassessment. "
            "If PHQ-9 increases ≥5 points, consider step-up to intensive care."
        ),
        ai_recommendation_confidence=0.81,
        version=2,
    )


@router.post(
    "/recommend",
    response_model=CarePlanRecommendationResponse,
    summary="Generate AI care plan recommendations",
    description=(
        "Generates advisory care plan recommendations based on a patient's risk profile. "
        "Output includes suggested interventions, measurable goals, and contact frequency. "
        "All recommendations require clinician review and explicit approval before activation."
    ),
)
async def get_care_plan_recommendation(
    request: CarePlanRecommendationRequest,
    x_clinician_id: Optional[str] = Header(None),
) -> CarePlanRecommendationResponse:
    """Generate AI-powered care plan recommendations from a patient's risk profile."""
    # Production: delegate to AIService.generate_care_plan_recommendation(request)
    # which calls Claude API with the structured risk profile

    risk = request.current_risk_level
    frequency = 7 if risk in ("high", "acute") else (10 if risk == "moderate" else 14)

    session_frequency = "Weekly" if risk in ("high", "acute") else "Biweekly"
    include_crisis_plan = risk == "acute"

    suggested_interventions = [
        {
            "type": InterventionType.PSYCHOTHERAPY,
            "description": f"{session_frequency} therapy sessions",
            "frequency": session_frequency,
            "rationale": f"Evidence-based for {risk} risk profile. Prioritises symptom reduction and coping skill development.",
        },
        {
            "type": InterventionType.DIGITAL_MONITORING,
            "description": "Weekly digital check-in (WHO-5 + safety screen)",
            "frequency": "Weekly",
            "rationale": "Enables between-session monitoring. Self-harm flag triggers immediate alert.",
        },
    ]
    if include_crisis_plan:
        suggested_interventions.insert(0, {
            "type": InterventionType.CRISIS_PLAN,
            "description": "Collaborative safety planning with patient",
            "frequency": "One-time (review at each session)",
            "rationale": "Acute risk level requires documented crisis plan with patient-identified safety strategies.",
        })

    return CarePlanRecommendationResponse(
        patient_id=request.patient_id,
        recommended_contact_frequency_days=frequency,
        suggested_interventions=suggested_interventions,
        suggested_goals=[
            {
                "description": "Reduce primary symptom score by ≥5 points (MCID) within 60 days",
                "target_metric": "PHQ-9 or GAD-7 (primary presenting instrument)",
                "rationale": "5-point change represents a clinically meaningful improvement.",
            },
            {
                "description": "Maintain WHO-5 wellbeing above 50% threshold (score ≥13/25)",
                "target_metric": "WHO-5",
                "rationale": "WHO-5 ≤50% signals wellbeing concern regardless of symptom score.",
            },
        ],
        ai_rationale=(
            f"Patient presents at {risk} risk level with {request.trend} trend. "
            f"Recommended contact frequency of every {frequency} days is calibrated to risk intensity. "
            f"{'Crisis planning is indicated given acute risk level. ' if include_crisis_plan else ''}"
            "All recommendations are advisory — clinician review and adaptation is expected."
        ),
        confidence=0.77,
    )


@router.put(
    "/{patient_id}",
    summary="Create or update a patient care plan",
    description=(
        "Saves a clinician-approved care plan. This may incorporate AI recommendations "
        "with clinician modifications. Override notes capture any deviations from AI output."
    ),
)
async def upsert_care_plan(
    patient_id: str,
    plan: CarePlan,
    x_clinician_id: Optional[str] = Header(None),
) -> dict:
    """Create or update a care plan with clinician approval."""
    return {
        "patient_id": patient_id,
        "plan_id": plan.id,
        "version": plan.version,
        "approved_by": x_clinician_id or plan.created_by_clinician_id,
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "message": "Care plan saved and activated. Review date set.",
        "review_date": plan.review_date.isoformat(),
    }
