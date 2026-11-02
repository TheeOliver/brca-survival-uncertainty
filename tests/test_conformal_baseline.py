import numpy as np
import pytest

from brca.conformal.baseline import restricted_km_interval
from brca.conformal.survival import (
    PredictionIntervals,
    coverage_summary,
    paired_interval_comparison,
)


def labels(times, events=None):
    times = np.asarray(times, dtype=float)
    if events is None:
        events = np.ones(len(times), dtype=bool)
    result = np.empty(len(times), dtype=[("event", bool), ("time", float)])
    result["event"] = events
    result["time"] = times
    return result


def test_restricted_km_interval_uses_event_quantiles_and_common_horizon_mass():
    # Four event masses of 0.25 make the 25th/75th percentiles 1 and 3.
    assert restricted_km_interval(labels([1, 2, 3, 4]), 0.5, 3.5) == (1.0, 3.0)
    # With a 2.5-month restriction, the remaining KM mass maps to that endpoint.
    assert restricted_km_interval(labels([1, 2, 3, 4]), 0.1, 2.5) == (1.0, 2.5)


def test_restricted_km_interval_respects_censoring_and_ties():
    y = labels([1, 2, 2, 4], [True, False, True, True])
    lower, upper = restricted_km_interval(y, 0.5, 3.0)
    assert 0 < lower <= upper <= 3


def test_restricted_km_interval_validates_inputs_and_handles_no_events():
    assert restricted_km_interval(labels([1, 2], [False, False]), 0.1, 5) == (5.0, 5.0)
    with pytest.raises(ValueError, match="alpha"):
        restricted_km_interval(labels([1]), 1.0, 5)
    with pytest.raises(ValueError, match="finite positive horizon"):
        restricted_km_interval(labels([1]), 0.1, np.inf)


def test_full_horizon_reference_and_near_full_fraction_are_reported():
    y = labels([10, 20, 30, 40], [True, False, True, False])
    full = PredictionIntervals(np.zeros(4), np.full(4, 100), 0.1, 0, 100, "trivial")
    report = coverage_summary(
        y,
        full,
        labels([150, 160]),
        bootstrap_replicates=20,
        seed=4,
        confidence_level=0.95,
        min_censoring_survival=0.05,
        minimum_bootstrap_success_fraction=0.9,
        near_full_width_fraction=0.9,
    )
    assert report["full_support_fraction"] == 1
    assert report["near_full_horizon_fraction"] == 1
    assert report["near_full_horizon_fraction_ci"] == [1, 1]
    assert report["width_median_months"] == 100


def test_paired_baseline_comparison_labels_and_near_full_delta_are_correct():
    y_test = labels([10, 30, 40, 60])
    y_train = labels([100, 120])
    baseline = PredictionIntervals(np.zeros(4), np.full(4, 100), 0.1, 50, 100, "km")
    model = PredictionIntervals(np.zeros(4), np.full(4, 50), 0.1, 23, 100, "model")
    report = paired_interval_comparison(
        y_test,
        baseline,
        model,
        y_train,
        bootstrap_replicates=30,
        seed=5,
        confidence_level=0.95,
        min_censoring_survival=0.05,
        minimum_bootstrap_success_fraction=0.9,
        reference_label="predictor_free_km",
        comparison_label="cox_clinical",
        near_full_width_fraction=0.9,
    )
    assert report["direction"] == "cox_clinical_minus_predictor_free_km"
    assert report["n_cal_reference"] == 50
    assert report["n_cal_comparison"] == 23
    assert "n_cal_clinical" not in report
    assert report["differences"]["width_median_months"]["estimate"] == -50
    assert report["differences"]["near_full_horizon_fraction"]["estimate"] == -1
