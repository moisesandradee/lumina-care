# =============================================================================
# ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
# Esta implementação representa uma proposta arquitetural, não código de produção.
# =============================================================================
"""
Lumina Care — Risk Analysis Service
Computes multi-dimensional psychosocial risk scores from structured assessment data.

This service uses validated clinical instruments as the basis for scoring.
It does not make clinical diagnoses — it produces advisory risk profiles.

Clinical frameworks used:
- PHQ-9 (Patient Health Questionnaire-9): Depression symptom severity
- GAD-7 (Generalized Anxiety Disorder-7): Anxiety symptom severity
- C-SSRS (Columbia Suicide Severity Rating Scale): Suicidal ideation/behavior
- Care engagement metrics: Appointment adherence, contact recency
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from models.triage import (
    AssessmentBundle,
    RiskDimension,
    RiskLevel,
    TrendDirection,
    RecommendedAction,
    PriorityQueueEntry,
)


class RiskAnalysisService:
    """
    Computes psychosocial risk profiles from structured clinical assessment data.
    All scoring logic is deterministic, auditable, and grounded in validated instruments.
    """

    # PHQ-9 severity thresholds (validated)
    PHQ9_THRESHOLDS = {"low": 4, "mild": 9, "moderate": 14, "moderately_severe": 19}

    # GAD-7 severity thresholds (validated)
    GAD7_THRESHOLDS = {"low": 4, "mild": 9, "moderate": 14}

    # Care engagement thresholds (clinical judgment-based)
    CARE_GAP_WARNING_DAYS = 14
    CARE_GAP_CRITICAL_DAYS = 21
    ADHERENCE_LOW_THRESHOLD = 0.6

    def compute_risk_profile(
        self,
        assessments: AssessmentBundle,
    ) -> tuple[RiskLevel, list[RiskDimension], float]:
        """
        Computes a composite risk profile from an assessment bundle.

        Returns:
            - overall_risk_level: The composite risk level
            - risk_dimensions: List of individual risk dimensions
            - priority_score: Numeric priority score (0–100) for queue ordering
        """
        dimensions: list[RiskDimension] = []
        priority_components: list[float] = []

        # --- Safety dimension (from C-SSRS) ---
        safety_dim = self._score_safety_dimension(assessments)
        dimensions.append(safety_dim)
        priority_components.append(self._dimension_to_priority_weight(safety_dim, weight=3.0))

        # --- Depression symptom dimension (from PHQ-9) ---
        if assessments.phq9:
            depression_dim = self._score_phq9_dimension(assessments.phq9.total_score)
            dimensions.append(depression_dim)
            priority_components.append(self._dimension_to_priority_weight(depression_dim, weight=2.0))

        # --- Anxiety symptom dimension (from GAD-7) ---
        if assessments.gad7:
            anxiety_dim = self._score_gad7_dimension(assessments.gad7.total_score)
            dimensions.append(anxiety_dim)
            priority_components.append(self._dimension_to_priority_weight(anxiety_dim, weight=1.5))

        # --- Care engagement dimension ---
        engagement_dim = self._score_engagement_dimension(
            days_since_contact=assessments.days_since_last_contact,
            adherence_rate=assessments.appointment_adherence_rate,
        )
        dimensions.append(engagement_dim)
        priority_components.append(self._dimension_to_priority_weight(engagement_dim, weight=1.5))

        # --- Composite score ---
        priority_score = min(100.0, sum(priority_components))

        # --- Overall risk level: highest dimension level drives overall ---
        overall_level = self._compute_overall_level(dimensions)

        # C-SSRS positive behavior always escalates to ACUTE
        if assessments.cssrs and assessments.cssrs.behavior_present:
            overall_level = RiskLevel.ACUTE

        return overall_level, dimensions, round(priority_score, 2)

    def determine_trend(
        self,
        current_phq9: Optional[int],
        previous_phq9: Optional[int],
    ) -> TrendDirection:
        """Computes symptom trend from serial PHQ-9 scores."""
        if current_phq9 is None or previous_phq9 is None:
            return TrendDirection.INSUFFICIENT_DATA

        delta = current_phq9 - previous_phq9

        if delta <= -5:
            return TrendDirection.IMPROVING
        elif delta >= 5:
            return TrendDirection.DETERIORATING
        else:
            return TrendDirection.STABLE

    def determine_recommended_action(
        self,
        risk_level: RiskLevel,
        trend: TrendDirection,
        days_since_contact: Optional[int],
    ) -> RecommendedAction:
        """Maps risk profile to a recommended clinical action."""
        if risk_level == RiskLevel.ACUTE:
            return RecommendedAction.IMMEDIATE_ESCALATION

        if risk_level == RiskLevel.HIGH:
            if trend == TrendDirection.DETERIORATING:
                return RecommendedAction.URGENT_CLINICAL_REVIEW
            return RecommendedAction.PRIORITY_CONTACT

        if risk_level == RiskLevel.MODERATE:
            if trend == TrendDirection.DETERIORATING:
                return RecommendedAction.PRIORITY_CONTACT
            if days_since_contact and days_since_contact > self.CARE_GAP_WARNING_DAYS:
                return RecommendedAction.ENHANCED_MONITORING
            return RecommendedAction.ENHANCED_MONITORING

        return RecommendedAction.ROUTINE_FOLLOW_UP

    # -----------------------------------------------------------------------
    # Private scoring methods
    # -----------------------------------------------------------------------

    def _score_safety_dimension(self, assessments: AssessmentBundle) -> RiskDimension:
        if not assessments.cssrs:
            return RiskDimension(
                dimension="safety",
                level=RiskLevel.LOW,
                score=0.0,
                contributing_signals=["No C-SSRS data available"],
            )

        if assessments.cssrs.behavior_present:
            return RiskDimension(
                dimension="safety",
                level=RiskLevel.ACUTE,
                score=1.0,
                contributing_signals=["C-SSRS: suicidal behavior present — immediate escalation indicated"],
            )

        if assessments.cssrs.ideation_present:
            intensity = assessments.cssrs.ideation_intensity or 0
            if intensity >= 4:
                return RiskDimension(
                    dimension="safety",
                    level=RiskLevel.HIGH,
                    score=0.8,
                    contributing_signals=[f"C-SSRS: suicidal ideation present (intensity {intensity}/5)"],
                )
            return RiskDimension(
                dimension="safety",
                level=RiskLevel.MODERATE,
                score=0.5,
                contributing_signals=[f"C-SSRS: suicidal ideation present (intensity {intensity}/5)"],
            )

        return RiskDimension(
            dimension="safety",
            level=RiskLevel.LOW,
            score=0.0,
            contributing_signals=["C-SSRS: no ideation or behavior reported"],
        )

    def _score_phq9_dimension(self, score: int) -> RiskDimension:
        if score >= 20:
            return RiskDimension(
                dimension="depression_symptoms",
                level=RiskLevel.HIGH,
                score=score / 27,
                contributing_signals=[f"PHQ-9: {score}/27 — severe range"],
            )
        elif score >= 15:
            return RiskDimension(
                dimension="depression_symptoms",
                level=RiskLevel.HIGH,
                score=score / 27,
                contributing_signals=[f"PHQ-9: {score}/27 — moderately severe range"],
            )
        elif score >= 10:
            return RiskDimension(
                dimension="depression_symptoms",
                level=RiskLevel.MODERATE,
                score=score / 27,
                contributing_signals=[f"PHQ-9: {score}/27 — moderate range"],
            )
        elif score >= 5:
            return RiskDimension(
                dimension="depression_symptoms",
                level=RiskLevel.LOW,
                score=score / 27,
                contributing_signals=[f"PHQ-9: {score}/27 — mild range"],
            )
        return RiskDimension(
            dimension="depression_symptoms",
            level=RiskLevel.LOW,
            score=0.0,
            contributing_signals=[f"PHQ-9: {score}/27 — minimal symptoms"],
        )

    def _score_gad7_dimension(self, score: int) -> RiskDimension:
        if score >= 15:
            return RiskDimension(
                dimension="anxiety_symptoms",
                level=RiskLevel.HIGH,
                score=score / 21,
                contributing_signals=[f"GAD-7: {score}/21 — severe range"],
            )
        elif score >= 10:
            return RiskDimension(
                dimension="anxiety_symptoms",
                level=RiskLevel.MODERATE,
                score=score / 21,
                contributing_signals=[f"GAD-7: {score}/21 — moderate range"],
            )
        elif score >= 5:
            return RiskDimension(
                dimension="anxiety_symptoms",
                level=RiskLevel.LOW,
                score=score / 21,
                contributing_signals=[f"GAD-7: {score}/21 — mild range"],
            )
        return RiskDimension(
            dimension="anxiety_symptoms",
            level=RiskLevel.LOW,
            score=0.0,
            contributing_signals=[f"GAD-7: {score}/21 — minimal symptoms"],
        )

    def _score_engagement_dimension(
        self,
        days_since_contact: Optional[int],
        adherence_rate: Optional[float],
    ) -> RiskDimension:
        signals = []
        score = 0.0

        if days_since_contact is not None:
            if days_since_contact > self.CARE_GAP_CRITICAL_DAYS:
                score = max(score, 0.8)
                signals.append(f"Care gap: {days_since_contact} days since last contact (>{self.CARE_GAP_CRITICAL_DAYS} day threshold)")
            elif days_since_contact > self.CARE_GAP_WARNING_DAYS:
                score = max(score, 0.5)
                signals.append(f"Care gap approaching: {days_since_contact} days since last contact")

        if adherence_rate is not None:
            if adherence_rate < self.ADHERENCE_LOW_THRESHOLD:
                score = max(score, 0.6)
                signals.append(f"Low appointment adherence: {adherence_rate:.0%}")

        if not signals:
            signals.append("Care engagement within expected parameters")

        if score >= 0.7:
            level = RiskLevel.HIGH
        elif score >= 0.4:
            level = RiskLevel.MODERATE
        else:
            level = RiskLevel.LOW

        return RiskDimension(
            dimension="care_engagement",
            level=level,
            score=score,
            contributing_signals=signals,
        )

    def _dimension_to_priority_weight(self, dim: RiskDimension, weight: float) -> float:
        level_scores = {
            RiskLevel.LOW: 10.0,
            RiskLevel.MODERATE: 30.0,
            RiskLevel.HIGH: 60.0,
            RiskLevel.ACUTE: 100.0,
        }
        return level_scores[dim.level] * weight * dim.score

    def _compute_overall_level(self, dimensions: list[RiskDimension]) -> RiskLevel:
        """Overall level is the maximum across all dimensions."""
        level_order = [RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.ACUTE]
        max_level = RiskLevel.LOW
        for dim in dimensions:
            if level_order.index(dim.level) > level_order.index(max_level):
                max_level = dim.level
        return max_level
