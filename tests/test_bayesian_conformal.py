import numpy as np
import pytest

from brca.evaluation.bayesian_conformal import _pair_summary, _validate_comparison_report


def labels(times, events):
    result = np.empty(len(times), dtype=[("event", bool), ("time", float)])
    result["event"] = events
    result["time"] = times
    return result


def test_bayesian_pair_uses_same_endpoints_and_reports_calibration_gain():
    y_test = labels([12, 40, 70, 110, 130, 90], [True, False, True, False, True, True])
    y_train = labels([180, 200, 220, 240], [False, False, False, False])
    calibration_state = {
        "alpha": 0.1,
        "n_cal": 50,
        "horizon": 120.0,
        "quantile": 10.0,
        "quantile_is_infinite": False,
        "method": "conservative",
        "stratum_counts": {"False": 20, "True": 30},
        "stratum_quantiles": {"False": 8.0, "True": 10.0},
    }
    common = {
        "bootstrap_replicates": 30,
        "seed": 123,
        "confidence_level": 0.95,
        "min_censoring_survival": 0.05,
        "minimum_bootstrap_success_fraction": 0.9,
        "bootstrap_strata": y_test["event"],
    }

    result = _pair_summary(
        y_test,
        y_train,
        np.array([10, 20, 30, 40, 50, 60], dtype=float),
        np.array([50, 60, 70, 80, 90, 100], dtype=float),
        0.1,
        120.0,
        calibration_state,
        common=common,
    )

    native = result["posterior_predictive"]
    calibrated = result["conformalized"]
    paired = result["paired_conformal_minus_posterior_predictive"]
    assert native["n_test"] == calibrated["n_test"] == paired["n_test"] == len(y_test)
    assert native["n_cal"] == 0
    assert calibrated["n_cal"] == calibration_state["n_cal"]
    assert result["calibration"]["quantile_months"] == 10.0
    assert calibrated["width_median_months"] > native["width_median_months"]
    assert paired["same_patient_resamples"] is True
    assert paired["differences"]["width_median_months"]["estimate"] > 0
    assert paired["differences"]["width_median_months"]["ci"] is not None


def test_zero_calibration_quantile_preserves_native_intervals():
    y_test = labels([12, 40, 70, 110], [True, False, True, True])
    y_train = labels([180, 200, 220], [False, False, False])
    calibration_state = {
        "alpha": 0.1,
        "n_cal": 50,
        "horizon": 120.0,
        "quantile": 0.0,
        "quantile_is_infinite": False,
        "method": "conservative",
        "stratum_counts": {"False": 2, "True": 2},
        "stratum_quantiles": {"False": 0.0, "True": 0.0},
    }
    common = {
        "bootstrap_replicates": 20,
        "seed": 123,
        "confidence_level": 0.95,
        "min_censoring_survival": 0.05,
        "minimum_bootstrap_success_fraction": 0.9,
        "bootstrap_strata": y_test["event"],
    }

    result = _pair_summary(
        y_test,
        y_train,
        np.array([10, 20, 30, 40], dtype=float),
        np.array([50, 60, 70, 80], dtype=float),
        0.1,
        120.0,
        calibration_state,
        common=common,
    )

    assert (
        result["conformalized"]["width_median_months"]
        == result["posterior_predictive"]["width_median_months"]
    )
    assert (
        result["paired_conformal_minus_posterior_predictive"]["differences"]["width_median_months"][
            "estimate"
        ]
        == 0
    )


def _summary(alpha, horizon, n_cal, lower, upper, widths, ipcw):
    return {
        "alpha": alpha,
        "horizon_months": horizon,
        "n_test": 5,
        "n_cal": n_cal,
        "nominal_coverage": 1 - alpha,
        "observable_coverage_lower": lower,
        "observable_coverage_upper": upper,
        "width_q25_months": widths[0],
        "width_median_months": widths[1],
        "width_q75_months": widths[2],
        "ipcw_coverage": ipcw,
        "ipcw_coverage_ci": [ipcw - 0.05, ipcw + 0.05],
        "ipcw_status": "available",
        "bootstrap_replicates_requested": 1000,
        "confidence_level": 0.95,
        "minimum_bootstrap_success_fraction": 0.9,
        "bootstrap_sampling": "within_primary_event_strata",
    }


def comparison_report():
    alphas, horizons = (0.2, 0.1, 0.05), (300.0, 120.0)
    settings = {}
    for alpha in alphas:
        for horizon in horizons:
            arms = {}
            for feature in ("clinical", "clinical_molecular"):
                native = _summary(alpha, horizon, 0, 0.5, 0.8, (20, 40, 60), 0.75)
                conformal = _summary(alpha, horizon, 10, 0.6, 0.9, (30, 50, 70), 0.8)
                differences = {
                    "observable_coverage_lower": {"estimate": 0.1, "ci": [0.0, 0.2]},
                    "observable_coverage_upper": {"estimate": 0.1, "ci": [0.0, 0.2]},
                    "width_median_months": {"estimate": 10.0, "ci": [5.0, 15.0]},
                    "ipcw_coverage": {"estimate": 0.05, "ci": [0.0, 0.1]},
                }
                arms[feature] = {
                    "posterior_predictive": native,
                    "conformalized": conformal,
                    "paired_conformal_minus_posterior_predictive": {
                        "direction": (
                            "conformalized_posterior_predictive_minus_posterior_predictive"
                        ),
                        "n_test": 5,
                        "same_patient_resamples": True,
                        "n_cal_clinical": 0,
                        "n_cal_molecular": 10,
                        "bootstrap_replicates_requested": 1000,
                        "confidence_level": 0.95,
                        "minimum_bootstrap_success_fraction": 0.9,
                        "bootstrap_sampling": "within_primary_event_strata",
                        "differences": differences,
                    },
                    "calibration": {
                        "n_cal": 10,
                        "quantile_months": 5.0,
                        "quantile_is_infinite": False,
                    },
                }
            settings[f"alpha{alpha:g}__horizon{horizon:g}"] = {
                "alpha": alpha,
                "nominal_coverage": 1 - alpha,
                "horizon_months": horizon,
                "feature_sets": arms,
            }
    report = {
        "status": "post_hoc_exploratory_test_reuse",
        "n_test": 5,
        "main_comparison": {"alpha": 0.1, "horizon_months": 120.0},
        "settings": settings,
    }
    protocol = {
        "status": report["status"],
        "alphas": alphas,
        "horizons_months": horizons,
        "feature_sets": ["clinical", "clinical_molecular"],
        "main_comparison": report["main_comparison"],
        "bootstrap_replicates": 1000,
        "confidence_level": 0.95,
        "minimum_bootstrap_success_fraction": 0.9,
    }
    return report, protocol


def test_aggregate_report_validator_accepts_complete_aligned_comparison():
    report, protocol = comparison_report()

    _validate_comparison_report(report, protocol)


def test_aggregate_report_validator_rejects_incomplete_or_narrowed_intervals():
    report, protocol = comparison_report()
    del report["settings"]["alpha0.2__horizon300"]
    with pytest.raises(ValueError, match="every registered"):
        _validate_comparison_report(report, protocol)

    report, protocol = comparison_report()
    pair = report["settings"]["alpha0.2__horizon300"]["feature_sets"]["clinical"]
    pair["conformalized"]["width_median_months"] = 30
    with pytest.raises(ValueError, match="do not preserve the native set"):
        _validate_comparison_report(report, protocol)
