# =============================================================================
# ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
# Esta implementação representa uma proposta arquitetural, não código de produção.
# =============================================================================
"""
Lumina Care — Longitudinal Analysis Service
Detects trajectory patterns in serial clinical assessment data.

Core clinical insight: a single score tells you where a patient is.
A trajectory tells you where they are going.

This service answers:
- Is this patient improving, deteriorating, or fluctuating?
- Is deterioration acute (recent) or sustained (over time)?
- Has the change crossed the clinically meaningful threshold (MCID)?
"""

from __future__ import annotations

from typing import Optional

from models.longitudinal import (
    SymptomDataPoint,
    SymptomTrajectory,
    TrajectoryPattern,
)


class LongitudinalAnalysisService:
    """
    Analyzes sequences of clinical assessment scores to identify
    clinically meaningful trajectory patterns.

    All logic is deterministic and auditable.
    """

    # A ≥5 point change on PHQ-9 or GAD-7 is the validated MCID
    # (Minimal Clinically Important Difference)
    CLINICAL_SIGNIFICANCE_THRESHOLD = 5

    # A jump of ≥5 points within the last 1–2 assessments = acute deterioration
    ACUTE_DETERIORATION_THRESHOLD = 5

    # Score bands by instrument — used to classify STABLE_HIGH vs STABLE_LOW
    ELEVATED_THRESHOLDS = {
        "PHQ-9": 10,   # ≥10 = moderate/severe depression
        "GAD-7": 10,   # ≥10 = moderate/severe anxiety
        "WHO-5": 13,   # ≤12 (25-point scale) = low wellbeing (≤50% of max)
    }

    def compute_trajectory(
        self,
        patient_id: str,
        instrument: str,
        data_points: list[SymptomDataPoint],
    ) -> SymptomTrajectory:
        """
        Compute a symptom trajectory from a time-ordered series of assessment scores.

        Requires at least 2 data points to compute a meaningful trajectory.
        With <2 points, returns INSUFFICIENT_DATA pattern.
        """
        if not data_points:
            return SymptomTrajectory(
                patient_id=patient_id,
                instrument=instrument,
                data_points=[],
                pattern=TrajectoryPattern.INSUFFICIENT_DATA,
                trend_direction="insufficient_data",
                peak_score=0,
                current_score=0,
            )

        sorted_points = sorted(data_points, key=lambda p: p.assessed_at)
        scores = [p.score for p in sorted_points]

        current_score = scores[-1]
        peak_score = max(scores)
        score_change_first_to_last = scores[-1] - scores[0]

        # 90-day proxy: change from 3 assessments ago (if available)
        score_change_90d: Optional[int] = None
        if len(sorted_points) >= 3:
            score_change_90d = scores[-1] - scores[-3]

        if len(sorted_points) < 2:
            return SymptomTrajectory(
                patient_id=patient_id,
                instrument=instrument,
                data_points=sorted_points,
                pattern=TrajectoryPattern.INSUFFICIENT_DATA,
                trend_direction="insufficient_data",
                peak_score=peak_score,
                current_score=current_score,
                score_change_first_to_last=score_change_first_to_last,
                score_change_90d=score_change_90d,
                clinical_significance=False,
            )

        pattern = self._classify_pattern(scores, instrument)
        trend = self._classify_trend(scores)
        clinical_significance = abs(score_change_first_to_last) >= self.CLINICAL_SIGNIFICANCE_THRESHOLD

        return SymptomTrajectory(
            patient_id=patient_id,
            instrument=instrument,
            data_points=sorted_points,
            pattern=pattern,
            trend_direction=trend,
            peak_score=peak_score,
            current_score=current_score,
            score_change_first_to_last=score_change_first_to_last,
            score_change_90d=score_change_90d,
            clinical_significance=clinical_significance,
        )

    def _classify_pattern(self, scores: list[int], instrument: str) -> TrajectoryPattern:
        """
        Classify the overall shape of a score sequence.

        Priority order:
        1. Acute deterioration (recent jump — highest clinical urgency)
        2. Sustained monotonic improvement or deterioration
        3. Stable high or low (narrow band, but level matters)
        4. Fluctuating (everything else)
        """
        if len(scores) < 2:
            return TrajectoryPattern.INSUFFICIENT_DATA

        # 1. Acute deterioration — jump ≥ threshold in the last interval
        if scores[-1] - scores[-2] >= self.ACUTE_DETERIORATION_THRESHOLD:
            return TrajectoryPattern.ACUTE_DETERIORATION

        # Use most recent 3 scores for stability assessment
        recent = scores[-3:] if len(scores) >= 3 else scores
        overall_change = scores[-1] - scores[0]

        # 2. Stable band (recent scores within ±2 points of each other)
        if max(recent) - min(recent) <= 2:
            elevated_threshold = self.ELEVATED_THRESHOLDS.get(instrument, 10)
            if scores[-1] >= elevated_threshold:
                return TrajectoryPattern.STABLE_HIGH
            return TrajectoryPattern.STABLE_LOW

        # 3. Sustained monotonic improvement (all consecutive steps non-increasing)
        if overall_change <= -self.CLINICAL_SIGNIFICANCE_THRESHOLD and all(
            scores[i] >= scores[i + 1] for i in range(len(scores) - 1)
        ):
            return TrajectoryPattern.SUSTAINED_IMPROVEMENT

        # 4. Sustained monotonic deterioration (all consecutive steps non-decreasing)
        if overall_change >= self.CLINICAL_SIGNIFICANCE_THRESHOLD and all(
            scores[i] <= scores[i + 1] for i in range(len(scores) - 1)
        ):
            return TrajectoryPattern.SUSTAINED_DETERIORATION

        # 5. Default: fluctuating
        return TrajectoryPattern.FLUCTUATING

    def _classify_trend(self, scores: list[int]) -> str:
        """
        Classify the overall directional trend.
        Uses first-to-last change with MCID threshold.
        """
        if len(scores) < 2:
            return "insufficient_data"
        delta = scores[-1] - scores[0]
        if delta <= -self.CLINICAL_SIGNIFICANCE_THRESHOLD:
            return "improving"
        if delta >= self.CLINICAL_SIGNIFICANCE_THRESHOLD:
            return "deteriorating"
        return "stable"

    def compute_population_trajectory_distribution(
        self,
        trajectories: list[SymptomTrajectory],
    ) -> dict[str, int]:
        """
        Aggregate trajectory patterns across a patient population.
        Used for population health analytics in the team director view.
        """
        distribution: dict[str, int] = {pattern.value: 0 for pattern in TrajectoryPattern}
        for trajectory in trajectories:
            distribution[trajectory.pattern.value] += 1
        return distribution
