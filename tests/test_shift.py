"""Synthetic covariate-shift and observable-coverage contracts."""

import json

import numpy as np
import pandas as pd
import pytest
from sksurv.util import Surv

from brca.conformal.survival import PredictionIntervals, coverage_summary
from brca.evaluation.shift import (
    covariate_shift_report,
    shift_weights,
    weighted_interval_report,
)


def interval_fixture():
    y = Surv.from_arrays(event=[True, False, False, True], time=[2.0, 3.0, 10.0, 8.0])
    intervals = PredictionIntervals(
        np.array([1.0, 2.0, 7.0, 0.0]), np.array([4.0, 10.0, 10.0, 5.0]), 0.1, 100, 10.0
    )
    return y, intervals


def report(y, intervals, weights, **kwargs):
    settings = dict(
        bootstrap_replicates=40,
        seed=141,
        confidence_level=0.95,
        minimum_success_fraction=0.9,
    )
    return weighted_interval_report(y, intervals, weights, **(settings | kwargs))


def test_uniform_weights_reproduce_existing_observable_summary():
    y, intervals = interval_fixture()
    shifted = report(y, intervals, np.ones(len(y)))
    original = coverage_summary(
        y,
        intervals,
        y_train=y,
        confidence_level=0.95,
        min_censoring_survival=0.05,
        minimum_bootstrap_success_fraction=0.9,
        bootstrap_replicates=40,
        seed=141,
    )
    correspondence = {
        "coverage_lower_bound": "observable_coverage_lower",
        "coverage_upper_bound": "observable_coverage_upper",
        "median_width": "width_median_months",
    }
    for key, original_key in correspondence.items():
        assert shifted["estimates"][key]["estimate"] == pytest.approx(original[original_key])
    assert shifted["estimates"]["mean_width"]["estimate"] == pytest.approx(intervals.width.mean())
    assert shifted["effective_sample_size"] == pytest.approx(4)
    assert shifted["maximum_normalized_weight"] == pytest.approx(0.25)
    assert json.loads(json.dumps(shifted, allow_nan=False)) == shifted


def test_weight_scale_invariance_including_bootstrap():
    y, intervals = interval_fixture()
    weights = np.array([1, 3, 2, 5], dtype=float)
    first, second = report(y, intervals, weights), report(y, intervals, weights * 1e250)
    for key, value in first["estimates"].items():
        assert value["estimate"] == pytest.approx(second["estimates"][key]["estimate"])
        np.testing.assert_allclose(value["ci"], second["estimates"][key]["ci"])
    assert first["effective_sample_size"] == pytest.approx(second["effective_sample_size"])


@pytest.mark.parametrize(
    "weights", [[0, 1, 1, 1], [-1, 1, 1, 1], [1, np.nan, 1, 1], [1], [np.inf] * 4]
)
def test_rejects_invalid_weights(weights):
    y, intervals = interval_fixture()
    with pytest.raises(ValueError, match="Weights"):
        report(y, intervals, weights)


def test_extreme_weights_report_small_effective_sample_size():
    y, intervals = interval_fixture()
    result = report(y, intervals, [1e10, 1, 1, 1])
    assert result["effective_sample_size"] == pytest.approx(1, abs=1e-8)
    assert result["maximum_normalized_weight"] > 0.999999
    assert result["estimates"]["coverage_lower_bound"]["estimate"] > 0.999999


def test_covariate_enrichment_can_reveal_undercoverage_of_frozen_intervals():
    # A distinct covariate group has the only miss. Giving that group higher
    # population mass changes coverage without changing any fitted interval.
    frame = pd.DataFrame({"group": ["common"] * 9 + ["rare"]})
    y = Surv.from_arrays(event=np.ones(10, bool), time=[5.0] * 9 + [9.0])
    intervals = PredictionIntervals(np.ones(10), np.full(10, 6.0), 0.1, 100, 10.0)
    weights = shift_weights(
        frame,
        frame,
        {"kind": "categorical_multiplier", "column": "group", "value": "rare", "factor": 9},
    )
    baseline = report(y, intervals, np.ones(10), bootstrap_replicates=0)
    enriched = report(y, intervals, weights, bootstrap_replicates=0)
    assert baseline["estimates"]["coverage_lower_bound"]["estimate"] == pytest.approx(0.9)
    assert enriched["estimates"]["coverage_lower_bound"]["estimate"] == pytest.approx(0.5)
    assert enriched["estimates"]["coverage_upper_bound"]["estimate"] == pytest.approx(0.5)
    assert enriched["estimates"]["mean_width"]["estimate"] == pytest.approx(5)


def test_censoring_bounds_use_open_left_compatible_boundary():
    y = Surv.from_arrays(event=[False] * 4, time=[3.0, 3.0, 3.0, 10.0])
    intervals = PredictionIntervals(
        np.array([0.0, 0.0, 4.0, 10.0]), np.array([3.0, 10.0, 9.0, 10.0]), 0.1, 100, 10.0
    )
    result = report(y, intervals, [1, 2, 3, 4])
    assert result["estimates"]["coverage_lower_bound"]["estimate"] == pytest.approx(0.6)
    assert result["estimates"]["coverage_upper_bound"]["estimate"] == pytest.approx(0.9)
    assert result["estimates"]["mean_width"]["estimate"] == pytest.approx(3.8)


def test_shifted_population_preserves_weighted_latent_coverage_bounds():
    rng = np.random.default_rng(541)
    latent = rng.uniform(1, 100, 1000)
    censoring = rng.uniform(1, 100, 1000)
    y = Surv.from_arrays(event=latent <= censoring, time=np.minimum(latent, censoring))
    lower = rng.uniform(0, 50, 1000)
    upper = rng.uniform(50, 100, 1000)
    intervals = PredictionIntervals(lower, upper, 0.1, 200, 100.0)
    weights = np.exp(2 * latent / 100)
    result = report(y, intervals, weights, bootstrap_replicates=0)
    truth = np.average((lower <= latent) & (latent <= upper), weights=weights)
    assert result["estimates"]["coverage_lower_bound"]["estimate"] <= truth
    assert result["estimates"]["coverage_upper_bound"]["estimate"] >= truth


def test_paired_bootstrap_preserves_constant_width_difference():
    y, intervals = interval_fixture()
    other = PredictionIntervals(intervals.lower, intervals.upper + 1, 0.1, 100, 11.0)
    first = report(y, intervals, np.ones(4), bootstrap_strata=y["event"])
    second = report(y, other, np.ones(4), bootstrap_strata=y["event"])
    for key in ["mean_width", "median_width"]:
        np.testing.assert_allclose(
            np.asarray(second["estimates"][key]["ci"]) - first["estimates"][key]["ci"], [1, 1]
        )


def test_age_tilts_use_training_location_scale_and_expected_direction():
    train = pd.DataFrame({"age": [40, 50, 60, 70]})
    test = pd.DataFrame({"age": [40, 50, 60, 70, np.nan]})
    settings = {"kind": "age_tilt", "column": "age", "beta": 0.5, "z_clip": 2}
    older = shift_weights(train, test, settings)
    younger = shift_weights(train, test, settings | {"beta": -0.5})
    assert (np.diff(older[:4]) > 0).all()
    np.testing.assert_allclose(older * younger, 1)
    assert older[-1] == pytest.approx(1)
    shifted = shift_weights(train, pd.DataFrame({"age": [70, 100]}), settings)
    assert shifted[0] == older[3]
    assert shifted[1] == pytest.approx(np.exp(1))
    np.testing.assert_array_equal(shift_weights(train, test, {"kind": "baseline"}), np.ones(5))


def test_categorical_multiplier_and_invalid_scenario():
    frame = pd.DataFrame({"pam50": ["basal", "lumA", None]})
    scenario = {"kind": "categorical_multiplier", "column": "pam50", "value": "basal", "factor": 2}
    np.testing.assert_array_equal(shift_weights(frame, frame, scenario), [2, 1, 1])
    with pytest.raises(ValueError, match="positive"):
        shift_weights(frame, frame, scenario | {"factor": 0})
    with pytest.raises(ValueError, match="Unknown"):
        shift_weights(frame, frame, {"kind": "unknown"})
    with pytest.raises(ValueError, match="variance"):
        shift_weights(
            pd.DataFrame({"age": [50, 50]}),
            pd.DataFrame({"age": [30, 40]}),
            {"kind": "age_tilt", "column": "age", "beta": 1, "z_clip": 2},
        )


def test_covariate_report_identical_populations_and_shift():
    source = pd.DataFrame({"age": np.arange(20), "pam50": ["basal"] * 10 + ["lumA"] * 10})
    same = covariate_shift_report(source, source, ["age"], ["pam50"], 2)
    assert same["numeric"]["age"]["standardized_mean_difference"] == 0
    assert same["categorical"]["pam50"]["total_variation_distance"] == 0
    target = pd.DataFrame({"age": np.arange(20) + 40, "pam50": ["basal"] * 20})
    changed = covariate_shift_report(source, target, ["age"], ["pam50"], 2)
    assert changed["numeric"]["age"]["standardized_mean_difference"] > 0
    assert changed["numeric"]["age"]["target_fraction_inside_source_range"] == 0
    assert changed["categorical"]["pam50"]["total_variation_distance"] == 0.5
    assert json.loads(json.dumps(changed, allow_nan=False)) == changed


def test_covariate_report_missingness_small_counts_and_no_outcome_access():
    source = pd.DataFrame({"age": [30, 40, np.nan], "group": ["a", "a", None], "event": [1, 0, 1]})
    target = pd.DataFrame({"age": [np.nan] * 3, "group": ["a", "b", None]})
    result = covariate_shift_report(source, target, ["age"], ["group"], 2)
    assert result["numeric"]["age"]["status"] == "insufficient_observed_values"
    assert result["numeric"]["age"]["target_missing_fraction"] == 1
    levels = result["categorical"]["group"]["categories"]
    assert all(level["status"] == "suppressed_small_group" for level in levels)
    assert all(level["n_target"] is None and level["target_fraction"] is None for level in levels)
    assert json.loads(json.dumps(result, allow_nan=False)) == result


def test_zero_numeric_variance_is_explicit():
    source, target = pd.DataFrame({"age": [30, 30]}), pd.DataFrame({"age": [40, 40]})
    result = covariate_shift_report(source, target, ["age"], [], 2)
    assert result["numeric"]["age"]["status"] == "zero_pooled_variance"
    assert result["numeric"]["age"]["standardized_mean_difference"] is None


def test_nonfinite_features_and_bad_quantiles_are_rejected():
    source, target = pd.DataFrame({"age": [30, 40]}), pd.DataFrame({"age": [np.inf, 40]})
    with pytest.raises(ValueError, match="Infinite"):
        covariate_shift_report(source, target, ["age"], [], 2)
    with pytest.raises(ValueError, match="quantiles"):
        covariate_shift_report(source, source, ["age"], [], 2, source_quantiles=[0.9, 0.1])
