"""
Lumina Care — RiskAnalysisService Unit Tests

Covers all deterministic scoring logic:
- PHQ-9 boundary conditions (every severity band)
- GAD-7 boundary conditions (every severity band)
- C-SSRS safety dimension (no data / ideation / behavior)
- Care engagement dimension (care gap and adherence thresholds)
- compute_risk_profile composite scoring and C-SSRS ACUTE override
- determine_trend PHQ-9 delta logic
- determine_recommended_action risk × trend combinations
- _dimension_to_priority_weight level-to-score mapping
- _compute_overall_level max-dimension rule
"""

import sys
import os
import pytest
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.triage import (
    AssessmentBundle,
    CSSRSInput,
    GAD7Input,
    PHQ9Input,
    RiskLevel,
    RiskDimension,
    TrendDirection,
    RecommendedAction,
)
from services.risk_analysis import RiskAnalysisService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

NOW = datetime.now(timezone.utc)


def make_phq9(score: int) -> PHQ9Input:
    return PHQ9Input(total_score=score, assessed_at=NOW)


def make_gad7(score: int) -> GAD7Input:
    return GAD7Input(total_score=score, assessed_at=NOW)


def make_cssrs(
    ideation: bool = False,
    behavior: bool = False,
    intensity: int | None = None,
) -> CSSRSInput:
    return CSSRSInput(
        ideation_present=ideation,
        behavior_present=behavior,
        ideation_intensity=intensity,
        assessed_at=NOW,
    )


def minimal_bundle(**kwargs) -> AssessmentBundle:
    """Returns a bare AssessmentBundle with all optionals None unless overridden."""
    return AssessmentBundle(**kwargs)


@pytest.fixture
def service() -> RiskAnalysisService:
    return RiskAnalysisService()


# ===========================================================================
# PHQ-9 scoring
# ===========================================================================


class TestScorePHQ9Dimension:
    """
    PHQ-9 severity bands (validated clinical thresholds):
      0–4   → minimal  → LOW
      5–9   → mild     → LOW
      10–14 → moderate → MODERATE
      15–19 → mod. severe → HIGH
      20–27 → severe   → HIGH
    """

    @pytest.mark.parametrize("score", [0, 1, 4])
    def test_minimal_range_is_low(self, service, score):
        dim = service._score_phq9_dimension(score)
        assert dim.level == RiskLevel.LOW
        assert "minimal" in dim.contributing_signals[0]

    @pytest.mark.parametrize("score", [5, 7, 9])
    def test_mild_range_is_low(self, service, score):
        dim = service._score_phq9_dimension(score)
        assert dim.level == RiskLevel.LOW
        assert "mild" in dim.contributing_signals[0]

    @pytest.mark.parametrize("score", [10, 12, 14])
    def test_moderate_range_is_moderate(self, service, score):
        dim = service._score_phq9_dimension(score)
        assert dim.level == RiskLevel.MODERATE

    @pytest.mark.parametrize("score", [15, 17, 19])
    def test_moderately_severe_range_is_high(self, service, score):
        dim = service._score_phq9_dimension(score)
        assert dim.level == RiskLevel.HIGH
        assert "moderately severe" in dim.contributing_signals[0]

    @pytest.mark.parametrize("score", [20, 23, 27])
    def test_severe_range_is_high(self, service, score):
        dim = service._score_phq9_dimension(score)
        assert dim.level == RiskLevel.HIGH
        assert "severe" in dim.contributing_signals[0]

    def test_score_normalised_to_27(self, service):
        dim = service._score_phq9_dimension(27)
        assert dim.score == pytest.approx(27 / 27)

    def test_minimal_score_is_zero(self, service):
        dim = service._score_phq9_dimension(0)
        assert dim.score == 0.0

    def test_boundary_9_to_10(self, service):
        """Score 9 → LOW, score 10 → MODERATE — exact boundary."""
        assert service._score_phq9_dimension(9).level == RiskLevel.LOW
        assert service._score_phq9_dimension(10).level == RiskLevel.MODERATE

    def test_boundary_14_to_15(self, service):
        """Score 14 → MODERATE, score 15 → HIGH."""
        assert service._score_phq9_dimension(14).level == RiskLevel.MODERATE
        assert service._score_phq9_dimension(15).level == RiskLevel.HIGH

    def test_boundary_19_to_20(self, service):
        """Score 19 → HIGH (moderately severe), score 20 → HIGH (severe)."""
        assert service._score_phq9_dimension(19).level == RiskLevel.HIGH
        assert service._score_phq9_dimension(20).level == RiskLevel.HIGH

    def test_dimension_name(self, service):
        dim = service._score_phq9_dimension(10)
        assert dim.dimension == "depression_symptoms"

    def test_phq9_thresholds_constant_matches_scoring_logic(self, service):
        """
        Regression: PHQ9_THRESHOLDS is defined on the class but the scoring
        method hardcodes boundaries. This test ensures they stay in sync.
        """
        t = RiskAnalysisService.PHQ9_THRESHOLDS
        # score at threshold boundary + 1 should be at the next band
        assert service._score_phq9_dimension(t["low"] + 1).level == RiskLevel.LOW  # mild
        assert service._score_phq9_dimension(t["mild"] + 1).level == RiskLevel.MODERATE
        assert service._score_phq9_dimension(t["moderate"] + 1).level == RiskLevel.HIGH
        assert service._score_phq9_dimension(t["moderately_severe"] + 1).level == RiskLevel.HIGH


# ===========================================================================
# GAD-7 scoring
# ===========================================================================


class TestScoreGAD7Dimension:
    """
    GAD-7 severity bands:
      0–4  → minimal → LOW
      5–9  → mild    → LOW
      10–14 → moderate → MODERATE
      15–21 → severe  → HIGH
    """

    @pytest.mark.parametrize("score", [0, 2, 4])
    def test_minimal_range_is_low(self, service, score):
        dim = service._score_gad7_dimension(score)
        assert dim.level == RiskLevel.LOW
        assert "minimal" in dim.contributing_signals[0]

    @pytest.mark.parametrize("score", [5, 7, 9])
    def test_mild_range_is_low(self, service, score):
        dim = service._score_gad7_dimension(score)
        assert dim.level == RiskLevel.LOW
        assert "mild" in dim.contributing_signals[0]

    @pytest.mark.parametrize("score", [10, 12, 14])
    def test_moderate_range_is_moderate(self, service, score):
        dim = service._score_gad7_dimension(score)
        assert dim.level == RiskLevel.MODERATE

    @pytest.mark.parametrize("score", [15, 18, 21])
    def test_severe_range_is_high(self, service, score):
        dim = service._score_gad7_dimension(score)
        assert dim.level == RiskLevel.HIGH

    def test_boundary_9_to_10(self, service):
        assert service._score_gad7_dimension(9).level == RiskLevel.LOW
        assert service._score_gad7_dimension(10).level == RiskLevel.MODERATE

    def test_boundary_14_to_15(self, service):
        assert service._score_gad7_dimension(14).level == RiskLevel.MODERATE
        assert service._score_gad7_dimension(15).level == RiskLevel.HIGH

    def test_score_normalised_to_21(self, service):
        dim = service._score_gad7_dimension(21)
        assert dim.score == pytest.approx(21 / 21)

    def test_dimension_name(self, service):
        dim = service._score_gad7_dimension(10)
        assert dim.dimension == "anxiety_symptoms"


# ===========================================================================
# C-SSRS safety dimension
# ===========================================================================


class TestScoreSafetyDimension:
    def test_no_cssrs_data_returns_low(self, service):
        bundle = minimal_bundle()
        dim = service._score_safety_dimension(bundle)
        assert dim.level == RiskLevel.LOW
        assert dim.score == 0.0
        assert any("No C-SSRS" in s for s in dim.contributing_signals)

    def test_behavior_present_returns_acute(self, service):
        bundle = minimal_bundle(cssrs=make_cssrs(behavior=True))
        dim = service._score_safety_dimension(bundle)
        assert dim.level == RiskLevel.ACUTE
        assert dim.score == 1.0
        assert any("behavior present" in s for s in dim.contributing_signals)

    def test_high_intensity_ideation_returns_high(self, service):
        """Ideation with intensity >= 4 should be HIGH."""
        for intensity in (4, 5):
            bundle = minimal_bundle(cssrs=make_cssrs(ideation=True, intensity=intensity))
            dim = service._score_safety_dimension(bundle)
            assert dim.level == RiskLevel.HIGH, f"intensity={intensity}"
            assert dim.score == 0.8

    def test_low_intensity_ideation_returns_moderate(self, service):
        """Ideation with intensity < 4 should be MODERATE."""
        for intensity in (0, 1, 2, 3):
            bundle = minimal_bundle(cssrs=make_cssrs(ideation=True, intensity=intensity))
            dim = service._score_safety_dimension(bundle)
            assert dim.level == RiskLevel.MODERATE, f"intensity={intensity}"
            assert dim.score == 0.5

    def test_ideation_without_intensity_defaults_to_moderate(self, service):
        """
        ideation_present=True with no intensity → intensity defaults to 0
        via `assessments.cssrs.ideation_intensity or 0`, which is < 4 → MODERATE.
        """
        bundle = minimal_bundle(cssrs=make_cssrs(ideation=True, intensity=None))
        dim = service._score_safety_dimension(bundle)
        assert dim.level == RiskLevel.MODERATE

    def test_no_ideation_no_behavior_returns_low(self, service):
        bundle = minimal_bundle(cssrs=make_cssrs(ideation=False, behavior=False))
        dim = service._score_safety_dimension(bundle)
        assert dim.level == RiskLevel.LOW
        assert dim.score == 0.0

    def test_behavior_present_takes_precedence_over_ideation(self, service):
        """behavior_present=True always wins regardless of ideation state."""
        bundle = minimal_bundle(
            cssrs=make_cssrs(ideation=True, behavior=True, intensity=1)
        )
        dim = service._score_safety_dimension(bundle)
        assert dim.level == RiskLevel.ACUTE


# ===========================================================================
# Care engagement dimension
# ===========================================================================


class TestScoreEngagementDimension:
    def test_no_data_returns_low(self, service):
        dim = service._score_engagement_dimension(None, None)
        assert dim.level == RiskLevel.LOW
        assert dim.score == 0.0

    def test_within_warning_threshold_returns_low(self, service):
        """days_since_contact <= CARE_GAP_WARNING_DAYS → no penalty."""
        dim = service._score_engagement_dimension(
            days_since_contact=RiskAnalysisService.CARE_GAP_WARNING_DAYS,
            adherence_rate=None,
        )
        assert dim.level == RiskLevel.LOW

    def test_exceeds_warning_threshold_returns_moderate(self, service):
        """days > 14 but <= 21 → score 0.5 → MODERATE."""
        dim = service._score_engagement_dimension(
            days_since_contact=RiskAnalysisService.CARE_GAP_WARNING_DAYS + 1,
            adherence_rate=None,
        )
        assert dim.level == RiskLevel.MODERATE
        assert dim.score == pytest.approx(0.5)

    def test_exceeds_critical_threshold_returns_high(self, service):
        """days > 21 → score 0.8 → HIGH."""
        dim = service._score_engagement_dimension(
            days_since_contact=RiskAnalysisService.CARE_GAP_CRITICAL_DAYS + 1,
            adherence_rate=None,
        )
        assert dim.level == RiskLevel.HIGH
        assert dim.score == pytest.approx(0.8)

    def test_low_adherence_returns_moderate(self, service):
        """adherence < 0.6 → score 0.6 → HIGH (score 0.6 >= 0.4 but < 0.7 is MODERATE)."""
        dim = service._score_engagement_dimension(
            days_since_contact=None,
            adherence_rate=RiskAnalysisService.ADHERENCE_LOW_THRESHOLD - 0.01,
        )
        # score 0.6 → level boundary: score >= 0.7 → HIGH, score >= 0.4 → MODERATE
        assert dim.level == RiskLevel.MODERATE
        assert dim.score == pytest.approx(0.6)

    def test_adherence_at_threshold_is_not_penalised(self, service):
        """adherence == 0.6 (not strictly below threshold) → no penalty."""
        dim = service._score_engagement_dimension(
            days_since_contact=None,
            adherence_rate=RiskAnalysisService.ADHERENCE_LOW_THRESHOLD,
        )
        assert dim.level == RiskLevel.LOW

    def test_critical_gap_dominates_low_adherence(self, service):
        """Both conditions fire; max() should pick the higher score (0.8 over 0.6)."""
        dim = service._score_engagement_dimension(
            days_since_contact=RiskAnalysisService.CARE_GAP_CRITICAL_DAYS + 5,
            adherence_rate=0.4,
        )
        assert dim.score == pytest.approx(0.8)
        assert dim.level == RiskLevel.HIGH

    def test_boundary_21_days_is_not_critical(self, service):
        """Exactly 21 days is NOT > CARE_GAP_CRITICAL_DAYS (21), so only warning fires."""
        dim = service._score_engagement_dimension(
            days_since_contact=RiskAnalysisService.CARE_GAP_CRITICAL_DAYS,
            adherence_rate=None,
        )
        assert dim.score == pytest.approx(0.5)
        assert dim.level == RiskLevel.MODERATE

    def test_contributing_signals_populated(self, service):
        dim = service._score_engagement_dimension(days_since_contact=30, adherence_rate=None)
        assert len(dim.contributing_signals) > 0
        assert any("30" in s for s in dim.contributing_signals)


# ===========================================================================
# compute_risk_profile — composite scoring
# ===========================================================================


class TestComputeRiskProfile:
    def test_all_low_risk_inputs(self, service):
        bundle = AssessmentBundle(
            phq9=make_phq9(3),
            gad7=make_gad7(3),
            cssrs=make_cssrs(ideation=False, behavior=False),
            days_since_last_contact=5,
            appointment_adherence_rate=0.9,
        )
        level, dims, score = service.compute_risk_profile(bundle)
        assert level == RiskLevel.LOW
        assert score >= 0.0

    def test_cssrs_behavior_overrides_everything_to_acute(self, service):
        """
        Critical safety test: behavior_present=True must produce ACUTE overall
        regardless of all other dimension levels.
        """
        bundle = AssessmentBundle(
            phq9=make_phq9(0),       # minimal depression
            gad7=make_gad7(0),       # minimal anxiety
            cssrs=make_cssrs(behavior=True),  # behavior present
            days_since_last_contact=1,
            appointment_adherence_rate=1.0,
        )
        level, dims, score = service.compute_risk_profile(bundle)
        assert level == RiskLevel.ACUTE

    def test_requires_override_review_set_for_acute(self, service):
        """Verify the flag that drives clinical override is tied to ACUTE level."""
        bundle = AssessmentBundle(
            cssrs=make_cssrs(behavior=True),
        )
        level, _, _ = service.compute_risk_profile(bundle)
        # The triage router uses `level == RiskLevel.ACUTE` for requires_override_review
        assert level == RiskLevel.ACUTE

    def test_high_phq9_elevates_overall_level(self, service):
        bundle = AssessmentBundle(
            phq9=make_phq9(22),
            days_since_last_contact=5,
            appointment_adherence_rate=0.9,
        )
        level, _, _ = service.compute_risk_profile(bundle)
        assert level == RiskLevel.HIGH

    def test_optional_instruments_absent(self, service):
        """No PHQ-9, no GAD-7, no CSSRS — only safety and engagement dimensions."""
        bundle = minimal_bundle(days_since_last_contact=5, appointment_adherence_rate=0.9)
        level, dims, score = service.compute_risk_profile(bundle)
        assert level == RiskLevel.LOW
        assert len(dims) == 2  # safety + engagement

    def test_priority_score_capped_at_100(self, service):
        """Priority score must never exceed 100 regardless of input severity."""
        bundle = AssessmentBundle(
            phq9=make_phq9(27),
            gad7=make_gad7(21),
            cssrs=make_cssrs(behavior=True, ideation=True, intensity=5),
            days_since_last_contact=100,
            appointment_adherence_rate=0.0,
        )
        _, _, score = service.compute_risk_profile(bundle)
        assert score <= 100.0

    def test_priority_score_is_rounded_to_two_decimals(self, service):
        bundle = AssessmentBundle(phq9=make_phq9(13), days_since_last_contact=10)
        _, _, score = service.compute_risk_profile(bundle)
        assert score == round(score, 2)

    def test_overall_level_is_max_of_dimensions(self, service):
        """MODERATE PHQ-9 + HIGH GAD-7 → overall should be HIGH."""
        bundle = AssessmentBundle(
            phq9=make_phq9(12),   # MODERATE
            gad7=make_gad7(16),   # HIGH
        )
        level, _, _ = service.compute_risk_profile(bundle)
        assert level == RiskLevel.HIGH

    def test_dimensions_list_contains_all_provided_instruments(self, service):
        bundle = AssessmentBundle(
            phq9=make_phq9(10),
            gad7=make_gad7(10),
            cssrs=make_cssrs(),
        )
        _, dims, _ = service.compute_risk_profile(bundle)
        names = [d.dimension for d in dims]
        assert "depression_symptoms" in names
        assert "anxiety_symptoms" in names
        assert "safety" in names
        assert "care_engagement" in names


# ===========================================================================
# determine_trend
# ===========================================================================


class TestDetermineTrend:
    def test_none_current_returns_insufficient_data(self, service):
        assert service.determine_trend(None, 10) == TrendDirection.INSUFFICIENT_DATA

    def test_none_previous_returns_insufficient_data(self, service):
        assert service.determine_trend(10, None) == TrendDirection.INSUFFICIENT_DATA

    def test_both_none_returns_insufficient_data(self, service):
        assert service.determine_trend(None, None) == TrendDirection.INSUFFICIENT_DATA

    @pytest.mark.parametrize("delta", [-5, -7, -10])
    def test_drop_of_5_or_more_is_improving(self, service, delta):
        assert service.determine_trend(10 + delta, 10) == TrendDirection.IMPROVING

    @pytest.mark.parametrize("delta", [5, 7, 10])
    def test_increase_of_5_or_more_is_deteriorating(self, service, delta):
        assert service.determine_trend(10 + delta, 10) == TrendDirection.DETERIORATING

    @pytest.mark.parametrize("delta", [-4, -1, 0, 1, 4])
    def test_change_less_than_5_is_stable(self, service, delta):
        assert service.determine_trend(10 + delta, 10) == TrendDirection.STABLE

    def test_boundary_minus_5_is_improving(self, service):
        assert service.determine_trend(5, 10) == TrendDirection.IMPROVING

    def test_boundary_minus_4_is_stable(self, service):
        assert service.determine_trend(6, 10) == TrendDirection.STABLE

    def test_boundary_plus_5_is_deteriorating(self, service):
        assert service.determine_trend(15, 10) == TrendDirection.DETERIORATING

    def test_boundary_plus_4_is_stable(self, service):
        assert service.determine_trend(14, 10) == TrendDirection.STABLE


# ===========================================================================
# determine_recommended_action
# ===========================================================================


class TestDetermineRecommendedAction:
    def test_acute_always_immediate_escalation(self, service):
        for trend in TrendDirection:
            action = service.determine_recommended_action(RiskLevel.ACUTE, trend, None)
            assert action == RecommendedAction.IMMEDIATE_ESCALATION

    def test_high_deteriorating_is_urgent_clinical_review(self, service):
        action = service.determine_recommended_action(
            RiskLevel.HIGH, TrendDirection.DETERIORATING, None
        )
        assert action == RecommendedAction.URGENT_CLINICAL_REVIEW

    def test_high_stable_is_priority_contact(self, service):
        action = service.determine_recommended_action(
            RiskLevel.HIGH, TrendDirection.STABLE, None
        )
        assert action == RecommendedAction.PRIORITY_CONTACT

    def test_high_improving_is_priority_contact(self, service):
        action = service.determine_recommended_action(
            RiskLevel.HIGH, TrendDirection.IMPROVING, None
        )
        assert action == RecommendedAction.PRIORITY_CONTACT

    def test_moderate_deteriorating_is_priority_contact(self, service):
        action = service.determine_recommended_action(
            RiskLevel.MODERATE, TrendDirection.DETERIORATING, None
        )
        assert action == RecommendedAction.PRIORITY_CONTACT

    def test_moderate_stable_is_enhanced_monitoring(self, service):
        action = service.determine_recommended_action(
            RiskLevel.MODERATE, TrendDirection.STABLE, days_since_contact=5
        )
        assert action == RecommendedAction.ENHANCED_MONITORING

    def test_low_any_trend_is_routine_follow_up(self, service):
        for trend in TrendDirection:
            action = service.determine_recommended_action(RiskLevel.LOW, trend, None)
            assert action == RecommendedAction.ROUTINE_FOLLOW_UP

    def test_moderate_stable_with_large_care_gap_is_still_enhanced_monitoring(self, service):
        """
        Regression: the care-gap branch inside MODERATE/non-deteriorating returns
        ENHANCED_MONITORING just like the fallback, making the branch unreachable.
        Both code paths should return the same action.
        """
        action_with_gap = service.determine_recommended_action(
            RiskLevel.MODERATE, TrendDirection.STABLE, days_since_contact=30
        )
        action_without_gap = service.determine_recommended_action(
            RiskLevel.MODERATE, TrendDirection.STABLE, days_since_contact=1
        )
        assert action_with_gap == action_without_gap == RecommendedAction.ENHANCED_MONITORING


# ===========================================================================
# _dimension_to_priority_weight
# ===========================================================================


class TestDimensionToPriorityWeight:
    def make_dim(self, level: RiskLevel, score: float) -> RiskDimension:
        return RiskDimension(
            dimension="test", level=level, score=score, contributing_signals=[]
        )

    def test_low_level_weight(self, service):
        dim = self.make_dim(RiskLevel.LOW, 1.0)
        assert service._dimension_to_priority_weight(dim, weight=1.0) == pytest.approx(10.0)

    def test_moderate_level_weight(self, service):
        dim = self.make_dim(RiskLevel.MODERATE, 1.0)
        assert service._dimension_to_priority_weight(dim, weight=1.0) == pytest.approx(30.0)

    def test_high_level_weight(self, service):
        dim = self.make_dim(RiskLevel.HIGH, 1.0)
        assert service._dimension_to_priority_weight(dim, weight=1.0) == pytest.approx(60.0)

    def test_acute_level_weight(self, service):
        dim = self.make_dim(RiskLevel.ACUTE, 1.0)
        assert service._dimension_to_priority_weight(dim, weight=1.0) == pytest.approx(100.0)

    def test_zero_score_produces_zero_weight(self, service):
        """
        Safety dimension with no data returns score=0.0.
        This intentionally contributes nothing to the priority score.
        """
        dim = self.make_dim(RiskLevel.LOW, 0.0)
        assert service._dimension_to_priority_weight(dim, weight=3.0) == pytest.approx(0.0)

    def test_weight_multiplier_applied(self, service):
        dim = self.make_dim(RiskLevel.MODERATE, 1.0)
        assert service._dimension_to_priority_weight(dim, weight=2.0) == pytest.approx(60.0)


# ===========================================================================
# _compute_overall_level
# ===========================================================================


class TestComputeOverallLevel:
    def make_dims(self, *levels: RiskLevel) -> list[RiskDimension]:
        return [
            RiskDimension(dimension="d", level=lvl, score=0.5, contributing_signals=[])
            for lvl in levels
        ]

    def test_single_low_dimension(self, service):
        assert service._compute_overall_level(self.make_dims(RiskLevel.LOW)) == RiskLevel.LOW

    def test_max_level_wins(self, service):
        dims = self.make_dims(RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH)
        assert service._compute_overall_level(dims) == RiskLevel.HIGH

    def test_acute_wins_over_all(self, service):
        dims = self.make_dims(RiskLevel.ACUTE, RiskLevel.HIGH, RiskLevel.LOW)
        assert service._compute_overall_level(dims) == RiskLevel.ACUTE

    def test_all_same_level(self, service):
        dims = self.make_dims(RiskLevel.MODERATE, RiskLevel.MODERATE)
        assert service._compute_overall_level(dims) == RiskLevel.MODERATE
