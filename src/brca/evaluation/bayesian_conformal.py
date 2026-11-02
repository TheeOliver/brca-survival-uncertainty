"""Exploratory paired comparison of native and conformalized Bayesian intervals."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from brca.conformal.survival import (
    ConformalCalibration,
    PredictionIntervals,
    coverage_summary,
    paired_interval_comparison,
)
from brca.data.eda import outcome_labels
from brca.data.partitions import load_partition
from brca.manifest import sha256_file, write_json_exclusive
from brca.pipeline import StageRun, named_rng, write_json


def _freeze_plan(
    run: StageRun, index: dict, calibration: dict, comparison_config_path: Path
) -> tuple[dict, Path, Path]:
    """Bind this post-hoc comparison to the existing frozen test and fitted artifacts."""
    outputs = run.outputs
    original_path = outputs / "evaluation/plan.json"
    calibration_path = outputs / "models/conformal_calibration.json"
    fit_index_path = outputs / "models/fit_index.json"
    test_cache_path = outputs / "evaluation/test_cache.pkl"
    partitions_dir = run.processed / "partitions"
    partition_checksums = json.loads((partitions_dir / "checksums.json").read_text())[
        "partitions_sha256"
    ]
    train_partition_sha256 = sha256_file(partitions_dir / "train.csv")
    calibration_partition_sha256 = sha256_file(partitions_dir / "calibration.csv")
    test_partition_sha256 = sha256_file(partitions_dir / "test.csv")
    original = json.loads(original_path.read_text())
    if (
        original.get("status") != "cached"
        or original["config_sha256"] != run.metadata["config_sha256"]
        or original["split_sha256"] != index["split_sha256"]
        or original["fit_index_sha256"] != sha256_file(fit_index_path)
        or original["calibration_sha256"] != sha256_file(calibration_path)
        or calibration["fit_index_sha256"] != sha256_file(fit_index_path)
        or calibration["calibration_partition_sha256"] != calibration_partition_sha256
        or partition_checksums["train"] != train_partition_sha256
        or partition_checksums["calibration"] != calibration_partition_sha256
        or partition_checksums["test"] != test_partition_sha256
        or original["test_partition_sha256"] != test_partition_sha256
        or not test_cache_path.is_file()
        or original["test_cache_sha256"] != sha256_file(test_cache_path)
    ):
        raise ValueError("Frozen fit, calibration or test-cache provenance does not match.")

    endpoint = run.config.outcome.primary_endpoint
    feature_sets = ("clinical", "clinical_molecular")
    model_keys = [f"{endpoint}__weibull__{features}" for features in feature_sets]
    if not set(model_keys).issubset(index["models"]):
        raise ValueError("Both registered primary-endpoint Weibull fits are required.")
    prediction_hashes = {}
    for model_key in model_keys:
        record = index["models"][model_key]
        cache_path = outputs / "evaluation" / f"predictions__{model_key}.pkl"
        binding_path = cache_path.with_suffix(".json")
        if not cache_path.is_file() or not binding_path.is_file():
            raise ValueError(f"Missing frozen prediction cache for {model_key}.")
        binding_record = json.loads(binding_path.read_text())
        expected_binding = {
            "plan_sha256": sha256_file(original_path),
            "model_artifacts_sha256": record["artifacts_sha256"],
            "test_cache_sha256": original["test_cache_sha256"],
        }
        if binding_record.get("binding") != expected_binding or binding_record.get(
            "sha256"
        ) != sha256_file(cache_path):
            raise ValueError(f"Prediction cache provenance mismatch for {model_key}.")
        prediction_hashes[model_key] = sha256_file(cache_path)

    comparison_config = yaml.safe_load(comparison_config_path.read_text())
    alpha = comparison_config["main_comparison"]["alpha"]
    horizon = comparison_config["main_comparison"]["horizon_months"]
    if (
        alpha not in run.config.conformal.alphas
        or horizon not in run.config.conformal.horizons_months
    ):
        raise ValueError("The declared primary comparison must use registered alpha and horizon.")
    protocol = {
        "method": "bayesian_posterior_predictive_vs_conformalized_posterior_predictive",
        "status": "post_hoc_exploratory_test_reuse",
        "endpoint": endpoint,
        "target": "min(T, horizon)",
        "native_interval": "equal_tailed_quantiles_of_posterior_mixture_event_time",
        "calibrated_interval": "same_native_interval_plus_existing_conservative_score_envelope",
        "calibration_partition_sha256": calibration["calibration_partition_sha256"],
        "training_partition_sha256": train_partition_sha256,
        "config_sha256": run.metadata["config_sha256"],
        "split_sha256": index["split_sha256"],
        "fit_index_sha256": sha256_file(fit_index_path),
        "calibration_sha256": sha256_file(calibration_path),
        "comparison_config_sha256": sha256_file(comparison_config_path),
        "original_evaluation_plan_sha256": sha256_file(original_path),
        "test_cache_sha256": original["test_cache_sha256"],
        "test_partition_sha256": original["test_partition_sha256"],
        "prediction_cache_sha256": prediction_hashes,
        "feature_sets": list(feature_sets),
        "alphas": run.config.conformal.alphas,
        "horizons_months": run.config.conformal.horizons_months,
        "main_comparison": {"alpha": alpha, "horizon_months": horizon},
        "bootstrap_replicates": run.config.evaluation.bootstrap_replicates,
        "minimum_bootstrap_success_fraction": (
            run.config.evaluation.minimum_bootstrap_success_fraction
        ),
        "confidence_level": run.config.evaluation.confidence_level,
        "seed": run.config.seed,
        "analysis_source_sha256": {
            str(path.relative_to(Path(__file__).parents[3])): sha256_file(path)
            for path in (
                Path(__file__).parents[3] / "scripts/05_evaluate.py",
                Path(__file__).parents[1] / "calibration.py",
                Path(__file__).parents[1] / "conformal/survival.py",
                Path(__file__).parents[1] / "data/eda.py",
                Path(__file__).parents[1] / "evaluation/bayesian_conformal.py",
                Path(__file__).parents[1] / "models/bayesian.py",
                Path(__file__).parents[1] / "viz/bayesian_conformal.py",
            )
        },
    }
    plan_path = outputs / "bayesian_conformal_comparison/plan.json"
    if plan_path.exists():
        if json.loads(plan_path.read_text()) != protocol:
            raise ValueError("Bayesian/conformal comparison plan changed after test opening.")
    else:
        write_json_exclusive(plan_path, protocol)
    return protocol, plan_path, test_cache_path


def _pair_summary(
    y_test: np.ndarray,
    y_train: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    alpha: float,
    horizon: float,
    calibration_state: dict,
    *,
    common: dict[str, Any],
) -> dict[str, Any]:
    native = PredictionIntervals(lower, upper, alpha, 0, horizon, "bayesian_posterior_predictive")
    calibrated = ConformalCalibration.from_dict(calibration_state).predict(lower, upper)
    if np.any(calibrated.lower > native.lower) or np.any(calibrated.upper < native.upper):
        raise ValueError("Conformalized intervals must contain the native intervals.")
    return {
        "posterior_predictive": coverage_summary(y_test, native, y_train, **common),
        "conformalized": coverage_summary(y_test, calibrated, y_train, **common),
        "paired_conformal_minus_posterior_predictive": paired_interval_comparison(
            y_test,
            native,
            calibrated,
            y_train,
            reference_label="posterior_predictive",
            comparison_label="conformalized_posterior_predictive",
            **common,
        ),
        "calibration": {
            "n_cal": calibration_state["n_cal"],
            "quantile_months": calibration_state["quantile"],
            "quantile_is_infinite": calibration_state["quantile_is_infinite"],
            "stratum_counts": calibration_state["stratum_counts"],
            "stratum_quantiles": calibration_state["stratum_quantiles"],
        },
    }


def _validate_comparison_report(report: dict[str, Any], protocol: dict[str, Any]) -> None:
    """Fail closed on missing, misaligned or non-finite aggregate comparisons."""
    expected = {
        f"alpha{alpha:g}__horizon{horizon:g}": (alpha, horizon)
        for alpha in protocol["alphas"]
        for horizon in protocol["horizons_months"]
    }
    if set(report.get("settings", {})) != set(expected):
        raise ValueError("Comparison report does not contain every registered alpha/horizon pair.")
    if report.get("n_test", 0) <= 0 or report.get("status") != protocol["status"]:
        raise ValueError("Comparison report has invalid test size or exploratory status.")
    if report.get("main_comparison") != protocol["main_comparison"]:
        raise ValueError("Comparison report changed the registered primary setting.")

    def finite(value: Any, label: str, lower: float, upper: float) -> float:
        if (
            not isinstance(value, (int, float, np.number))
            or isinstance(value, (bool, np.bool_))
            or not np.isfinite(value)
            or value < lower - 1e-10
            or value > upper + 1e-10
        ):
            raise ValueError(f"{label} is outside its finite domain.")
        return float(value)

    for key, (alpha, horizon) in expected.items():
        setting = report["settings"][key]
        if (
            setting.get("alpha") != alpha
            or setting.get("nominal_coverage") != 1 - alpha
            or setting.get("horizon_months") != horizon
            or set(setting.get("feature_sets", {})) != set(protocol["feature_sets"])
        ):
            raise ValueError(f"Setting metadata or feature arms mismatch for {key}.")
        for feature, pair in setting["feature_sets"].items():
            native = pair["posterior_predictive"]
            conformal = pair["conformalized"]
            calibration = pair["calibration"]
            if (
                native.get("alpha") != alpha
                or conformal.get("alpha") != alpha
                or native.get("nominal_coverage") != 1 - alpha
                or conformal.get("nominal_coverage") != 1 - alpha
                or native.get("horizon_months") != horizon
                or conformal.get("horizon_months") != horizon
                or native.get("n_test") != report["n_test"]
                or conformal.get("n_test") != report["n_test"]
                or native.get("n_cal") != 0
                or conformal.get("n_cal") != calibration.get("n_cal")
                or calibration.get("n_cal", 0) <= 0
            ):
                raise ValueError(f"Interval identity/sample-size mismatch for {key}/{feature}.")
            widths = {}
            for label, summary in (("native", native), ("conformal", conformal)):
                for bound in ("observable_coverage_lower", "observable_coverage_upper"):
                    finite(summary.get(bound), f"{key}/{feature}/{label}/{bound}", 0, 1)
                if summary["observable_coverage_lower"] > summary["observable_coverage_upper"]:
                    raise ValueError(f"Coverage bounds are reversed for {key}/{feature}/{label}.")
                widths[label] = [
                    finite(
                        summary.get(f"width_{name}_months"),
                        f"{key}/{feature}/{label}/{name}",
                        0,
                        horizon,
                    )
                    for name in ("q25", "median", "q75")
                ]
                if widths[label] != sorted(widths[label]):
                    raise ValueError(f"Width quartiles are unordered for {key}/{feature}/{label}.")
                if (
                    summary.get("bootstrap_replicates_requested")
                    != protocol["bootstrap_replicates"]
                    or summary.get("confidence_level") != protocol["confidence_level"]
                    or summary.get("minimum_bootstrap_success_fraction")
                    != protocol["minimum_bootstrap_success_fraction"]
                    or summary.get("bootstrap_sampling") != "within_primary_event_strata"
                ):
                    raise ValueError(f"Bootstrap protocol mismatch for {key}/{feature}/{label}.")
                value, ci = summary.get("ipcw_coverage"), summary.get("ipcw_coverage_ci")
                status = summary.get("ipcw_status")
                if status not in {
                    "available",
                    "unavailable_censoring_support",
                    "unavailable_no_observed_targets",
                }:
                    raise ValueError(
                        f"Unrecognized IPCW support status for {key}/{feature}/{label}."
                    )
                if (value is not None) != (status == "available"):
                    raise ValueError(
                        f"IPCW value and support status disagree for {key}/{feature}/{label}."
                    )
                if value is None:
                    if ci is not None:
                        raise ValueError(
                            f"Unsupported IPCW estimate has a CI for {key}/{feature}/{label}."
                        )
                else:
                    finite(value, f"{key}/{feature}/{label}/ipcw", 0, 1)
                    if not isinstance(ci, list) or len(ci) != 2:
                        raise ValueError(
                            f"IPCW estimate lacks a two-sided CI for {key}/{feature}/{label}."
                        )
                    limits = [finite(x, f"{key}/{feature}/{label}/ipcw_ci", 0, 1) for x in ci]
                    if limits[0] > limits[1]:
                        raise ValueError(f"IPCW CI is reversed for {key}/{feature}/{label}.")
            if (
                widths["conformal"][1] + 1e-10 < widths["native"][1]
                or conformal["observable_coverage_lower"] + 1e-10
                < native["observable_coverage_lower"]
                or conformal["observable_coverage_upper"] + 1e-10
                < native["observable_coverage_upper"]
            ):
                raise ValueError(
                    f"Conformalized intervals do not preserve the native set for {key}/{feature}."
                )
            q = calibration.get("quantile_months")
            if calibration.get("quantile_is_infinite"):
                if q is not None:
                    raise ValueError(
                        f"Infinite calibration quantile is encoded as finite for {key}/{feature}."
                    )
            elif finite(q, f"{key}/{feature}/calibration_quantile", 0, float("inf")) < 0:
                raise ValueError(f"Calibration quantile is negative for {key}/{feature}.")

            paired = pair["paired_conformal_minus_posterior_predictive"]
            if (
                paired.get("direction")
                != "conformalized_posterior_predictive_minus_posterior_predictive"
                or paired.get("n_test") != report["n_test"]
                or paired.get("same_patient_resamples") is not True
                or paired.get("n_cal_clinical") != 0
                or paired.get("n_cal_molecular") != calibration["n_cal"]
                or paired.get("bootstrap_replicates_requested") != protocol["bootstrap_replicates"]
                or paired.get("confidence_level") != protocol["confidence_level"]
                or paired.get("minimum_bootstrap_success_fraction")
                != protocol["minimum_bootstrap_success_fraction"]
                or paired.get("bootstrap_sampling") != "within_primary_event_strata"
            ):
                raise ValueError(f"Paired comparison is not aligned for {key}/{feature}.")
            point_differences = {
                "observable_coverage_lower": conformal["observable_coverage_lower"]
                - native["observable_coverage_lower"],
                "observable_coverage_upper": conformal["observable_coverage_upper"]
                - native["observable_coverage_upper"],
                "width_median_months": widths["conformal"][1] - widths["native"][1],
            }
            if native["ipcw_coverage"] is not None and conformal["ipcw_coverage"] is not None:
                point_differences["ipcw_coverage"] = (
                    conformal["ipcw_coverage"] - native["ipcw_coverage"]
                )
            for name, estimate in point_differences.items():
                observed = paired["differences"][name].get("estimate")
                if observed is None or not np.isclose(observed, estimate, atol=1e-10):
                    raise ValueError(
                        f"Paired point difference is inconsistent for {key}/{feature}/{name}."
                    )


def run_bayesian_conformal_comparison(
    run: StageRun, index: dict, calibration: dict, comparison_config_path: Path
) -> list[Path]:
    """Compare the fitted posterior predictive intervals before/after calibration."""
    protocol, plan_path, test_cache_path = _freeze_plan(
        run, index, calibration, comparison_config_path
    )
    if sha256_file(test_cache_path) != protocol["test_cache_sha256"]:
        raise ValueError("The frozen test cache changed after the comparison plan was written.")

    # This is a post-hoc reuse of the already-opened test partition; the plan above
    # fixes all methods, settings and source hashes before test outcomes are read.
    test = pickle.loads(test_cache_path.read_bytes())
    train = load_partition(run.config, "train")
    endpoint = run.config.outcome.primary_endpoint
    y_test = outcome_labels(test, endpoint)
    y_train = outcome_labels(train, endpoint)
    states = calibration["states"]
    report: dict[str, Any] = {
        "status": protocol["status"],
        "interpretation": (
            "Exploratory comparison on a previously opened test set; not independent validation. "
            "The posterior predictive interval is model-based uncertainty, while the conformal "
            "interval adds calibration from the existing calibration partition."
        ),
        "n_test": len(test),
        "main_comparison": protocol["main_comparison"],
        "method_notes": [
            (
                "Native intervals are equal-tailed quantiles of the posterior mixture of "
                "individual event times, including future-event variation; they are not "
                "survival-curve credible intervals."
            ),
            (
                "Conformalized intervals use the same native endpoints, widened by the "
                "frozen conservative score-envelope quantile."
            ),
            (
                "Coverage bounds are compatible with right-censored outcomes, not direct "
                "observations of latent coverage. IPCW assumes independent censoring and "
                "adequate support."
            ),
            (
                "Bootstrap confidence intervals condition on the fitted model, calibration "
                "state and training censoring estimate."
            ),
        ],
        "settings": {},
    }
    for features in protocol["feature_sets"]:
        model_key = f"{endpoint}__weibull__{features}"
        cache_path = run.outputs / "evaluation" / f"predictions__{model_key}.pkl"
        cache = pickle.loads(cache_path.read_bytes())
        if sha256_file(cache_path) != protocol["prediction_cache_sha256"][model_key]:
            raise ValueError(f"Prediction cache changed for {model_key}.")
        for alpha in run.config.conformal.alphas:
            base = np.asarray(cache["quantiles"][alpha], dtype=float)
            if base.shape != (len(test), 2) or np.any(~np.isfinite(base)):
                raise ValueError(f"Invalid posterior predictive quantiles for {model_key}.")
            for horizon in run.config.conformal.horizons_months:
                state_key = f"{model_key}__alpha{alpha:g}__horizon{horizon:g}__conservative"
                if state_key not in states:
                    raise ValueError(f"Missing frozen conservative calibration state {state_key}.")
                state = states[state_key]
                if (
                    state["model_key"] != model_key
                    or state["endpoint"] != endpoint
                    or state["feature_set"] != features
                    or state["registered_method"] != "conservative"
                ):
                    raise ValueError(f"Calibration metadata mismatch for {state_key}.")
                lower, upper = np.minimum(base, horizon).T
                seed = int(
                    named_rng(
                        run.config.seed,
                        "bayesian_conformal_comparison_bootstrap",
                        f"alpha{alpha:g}",
                        f"horizon{horizon:g}",
                    ).integers(0, np.iinfo(np.uint32).max)
                )
                common = {
                    "bootstrap_replicates": run.config.evaluation.bootstrap_replicates,
                    "seed": seed,
                    "confidence_level": run.config.evaluation.confidence_level,
                    "min_censoring_survival": run.config.conformal.min_censoring_survival,
                    "minimum_bootstrap_success_fraction": (
                        run.config.evaluation.minimum_bootstrap_success_fraction
                    ),
                    "bootstrap_strata": test["event"].to_numpy(bool),
                }
                setting = report["settings"].setdefault(
                    f"alpha{alpha:g}__horizon{horizon:g}",
                    {
                        "alpha": alpha,
                        "nominal_coverage": 1 - alpha,
                        "horizon_months": horizon,
                        "feature_sets": {},
                    },
                )
                setting["feature_sets"][features] = _pair_summary(
                    y_test,
                    y_train,
                    lower,
                    upper,
                    alpha,
                    horizon,
                    state["calibration"],
                    common=common,
                )
    _validate_comparison_report(report, protocol)
    result_path = run.outputs / "bayesian_conformal_comparison/results.json"
    write_json(result_path, report)
    from brca.viz.bayesian_conformal import export_bayesian_conformal_tables

    table_paths = export_bayesian_conformal_tables(report, run.outputs)
    return [plan_path, result_path, *table_paths]
