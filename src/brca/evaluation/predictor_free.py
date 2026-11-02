"""Exploratory predictor-free KM baseline evaluated on the frozen test set."""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np
import yaml

from brca.conformal.baseline import restricted_km_interval
from brca.conformal.survival import (
    ConformalCalibration,
    PredictionIntervals,
    calibrate_intervals,
    coverage_summary,
    paired_interval_comparison,
)
from brca.data.eda import outcome_labels
from brca.data.partitions import load_partition
from brca.manifest import sha256_file, write_json_exclusive
from brca.pipeline import StageRun, named_rng, write_json


def _freeze_plan(run: StageRun, index: dict, calibration: dict, baseline_config_path: Path):
    original_path = run.outputs / "evaluation/plan.json"
    original = json.loads(original_path.read_text())
    fit_index_path = run.outputs / "models/fit_index.json"
    calibration_path = run.outputs / "models/conformal_calibration.json"
    test_cache_path = run.outputs / "evaluation/test_cache.pkl"
    if (
        original.get("status") != "cached"
        or original["config_sha256"] != run.metadata["config_sha256"]
        or original["split_sha256"] != index["split_sha256"]
        or original["fit_index_sha256"] != sha256_file(fit_index_path)
        or original["calibration_sha256"] != sha256_file(calibration_path)
        or calibration["fit_index_sha256"] != sha256_file(fit_index_path)
        or calibration["calibration_partition_sha256"]
        != sha256_file(run.processed / "partitions/calibration.csv")
        or not test_cache_path.is_file()
        or original["test_cache_sha256"] != sha256_file(test_cache_path)
    ):
        raise ValueError("Frozen model, calibration or test-cache provenance does not match.")

    settings = yaml.safe_load(baseline_config_path.read_text())
    alpha, horizon = (
        settings["main_comparison"]["alpha"],
        settings["main_comparison"]["horizon_months"],
    )
    if (
        alpha not in run.config.conformal.alphas
        or horizon not in run.config.conformal.horizons_months
    ):
        raise ValueError("The requested main comparison must use a frozen alpha and horizon.")
    protocol = {
        "method": "predictor_free_kaplan_meier_conservative_conformal",
        "status": "post_hoc_exploratory_test_reuse",
        "target": "min(DSS_time, horizon)",
        "base_interval": "equal_tailed_restricted_Kaplan_Meier_train_only",
        "calibration": "existing_conservative_score_envelope_on_calibration_split",
        "calibration_strata": "primary_DSS_event_with_maximum_stratum_quantile",
        "trivial_reference": "[0,horizon]",
        "config_sha256": run.metadata["config_sha256"],
        "baseline_config_sha256": sha256_file(baseline_config_path),
        "split_sha256": index["split_sha256"],
        "training_partition_sha256": sha256_file(run.processed / "partitions/train.csv"),
        "calibration_partition_sha256": sha256_file(run.processed / "partitions/calibration.csv"),
        "fit_index_sha256": sha256_file(fit_index_path),
        "calibration_sha256": sha256_file(calibration_path),
        "original_evaluation_plan_sha256": sha256_file(original_path),
        "original_test_cache_sha256": sha256_file(test_cache_path),
        "test_partition_sha256": original["test_partition_sha256"],
        "alphas": run.config.conformal.alphas,
        "horizons_months": run.config.conformal.horizons_months,
        "main_comparison": {"alpha": alpha, "horizon_months": horizon},
        "near_full_width_fraction": settings["near_full_width_fraction"],
        "bootstrap_replicates": run.config.evaluation.bootstrap_replicates,
        "seed": run.config.seed,
        "analysis_source_sha256": {
            "scripts/05_evaluate.py": sha256_file(
                Path(__file__).parents[3] / "scripts/05_evaluate.py"
            ),
            "src/brca/conformal/baseline.py": sha256_file(
                Path(__file__).parents[1] / "conformal/baseline.py"
            ),
            "src/brca/conformal/survival.py": sha256_file(
                Path(__file__).parents[1] / "conformal/survival.py"
            ),
            "src/brca/evaluation/predictor_free.py": sha256_file(Path(__file__)),
            "src/brca/viz/predictor_free.py": sha256_file(
                Path(__file__).parents[1] / "viz/predictor_free.py"
            ),
        },
    }
    path = run.outputs / "predictor_free_baseline/plan.json"
    if path.exists():
        if json.loads(path.read_text()) != protocol:
            raise ValueError("Predictor-free baseline plan changed after test opening.")
    else:
        write_json_exclusive(path, protocol)
    return settings, protocol, path, original, test_cache_path


def run_predictor_free_baseline(
    run: StageRun, index: dict, calibration: dict, baseline_config_path: Path
) -> list[Path]:
    """Calibrate KM intervals without predictors; compare on the frozen test cache."""
    settings, protocol, plan_path, original, test_cache_path = _freeze_plan(
        run, index, calibration, baseline_config_path
    )
    if sha256_file(test_cache_path) != protocol["original_test_cache_sha256"]:
        raise ValueError("The frozen test cache changed after the baseline plan was written.")

    # Stage 05 is the only permitted reader of test outcomes; the protocol above
    # is frozen before this point, and this test set is reused post hoc.
    test = pickle.loads(test_cache_path.read_bytes())
    train = load_partition(run.config, "train")
    cal = load_partition(run.config, "calibration")
    y_train = outcome_labels(train, run.config.outcome.primary_endpoint)
    y_cal = outcome_labels(cal, run.config.outcome.primary_endpoint)
    y_test = outcome_labels(test, run.config.outcome.primary_endpoint)
    directory = run.outputs / "predictor_free_baseline"
    directory.mkdir(parents=True, exist_ok=True)
    report: dict = {
        "status": protocol["status"],
        "interpretation": (
            "Exploratory post hoc comparison on a previously opened test set; "
            "not an independent validation. Coverage bounds and IPCW answer different questions."
        ),
        "method_notes": [
            (
                "The predictor-free Kaplan-Meier distribution estimates disease-specific net "
                "survival under a non-informative censoring assumption; it is not a competing-"
                "risk cumulative incidence."
            ),
            (
                "Conformal calibration uses the existing conservative score envelope and "
                "calibration split; the KM interval remains common to all patients."
            ),
            (
                "Coverage bounds are test-set empirical bounds compatible with censoring and "
                "are not a direct observation of latent coverage."
            ),
            (
                "IPCW estimates require independent censoring and adequate support; bootstrap "
                "intervals condition on fitted models and calibration states."
            ),
        ],
        "primary_endpoint": run.config.outcome.primary_endpoint,
        "main_comparison": protocol["main_comparison"],
        "near_full_width_fraction": protocol["near_full_width_fraction"],
        "n_test": len(test),
        "settings": {},
    }

    fitted_models = {
        key: record
        for key, record in index["models"].items()
        if record["endpoint"] == run.config.outcome.primary_endpoint
        and record["feature_set"] in {"clinical", "clinical_molecular"}
    }
    expected_models = {
        f"{run.config.outcome.primary_endpoint}__{model}__{features}"
        for model in ("cox", "weibull", "rsf")
        for features in ("clinical", "clinical_molecular")
    }
    if set(fitted_models) != expected_models:
        raise ValueError("The frozen fit index does not contain all six registered model arms.")

    original_plan_sha = sha256_file(run.outputs / "evaluation/plan.json")
    model_intervals: dict[tuple[float, float, str], PredictionIntervals] = {}
    state_map = calibration["states"]
    for model_key, record in fitted_models.items():
        cache_path = run.outputs / "evaluation" / f"predictions__{model_key}.pkl"
        binding_path = cache_path.with_suffix(".json")
        expected_binding = {
            "plan_sha256": original_plan_sha,
            "model_artifacts_sha256": record["artifacts_sha256"],
            "test_cache_sha256": original["test_cache_sha256"],
        }
        if not cache_path.is_file() or not binding_path.is_file():
            raise ValueError(f"Missing frozen prediction cache for {model_key}.")
        binding_record = json.loads(binding_path.read_text())
        if binding_record.get("binding") != expected_binding or binding_record.get(
            "sha256"
        ) != sha256_file(cache_path):
            raise ValueError(f"Prediction cache provenance mismatch for {model_key}.")
        cached = pickle.loads(cache_path.read_bytes())
        for alpha in run.config.conformal.alphas:
            base = np.asarray(cached["quantiles"][alpha], dtype=float)
            if base.shape != (len(test), 2):
                raise ValueError(f"Prediction cache is misaligned for {model_key}.")
            for horizon in run.config.conformal.horizons_months:
                key = f"{model_key}__alpha{alpha:g}__horizon{horizon:g}__conservative"
                if key not in state_map:
                    raise ValueError(f"Missing frozen conformal state {key}.")
                state = state_map[key]
                lower, upper = np.minimum(base, horizon).T
                model_intervals[(alpha, horizon, model_key)] = ConformalCalibration.from_dict(
                    state["calibration"]
                ).predict(lower, upper)

    for alpha in run.config.conformal.alphas:
        for horizon in run.config.conformal.horizons_months:
            km_lower, km_upper = restricted_km_interval(y_train, alpha, horizon)
            cal_lower = np.full(len(y_cal), km_lower)
            cal_upper = np.full(len(y_cal), km_upper)
            calibration_state = calibrate_intervals(
                y_cal,
                cal_lower,
                cal_upper,
                alpha,
                horizon=horizon,
                strata=cal["event"].to_numpy(bool),
                expected_strata=(False, True),
            )
            km_intervals = calibration_state.predict(
                np.full(len(test), km_lower), np.full(len(test), km_upper)
            )
            trivial = PredictionIntervals(
                np.zeros(len(test)),
                np.full(len(test), horizon),
                alpha,
                0,
                horizon,
                "trivial_full_horizon",
            )
            seed = int(
                named_rng(
                    run.config.seed,
                    "predictor_free_baseline_bootstrap",
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
                "near_full_width_fraction": settings["near_full_width_fraction"],
            }
            arms = {
                "predictor_free_km_conformal": km_intervals,
                "trivial_full_horizon": trivial,
            }
            arms.update(
                {key: model_intervals[(alpha, horizon, key)] for key in sorted(fitted_models)}
            )
            summaries = {
                name: coverage_summary(y_test, intervals, y_train, **common)
                for name, intervals in arms.items()
            }
            paired = {
                key: paired_interval_comparison(
                    y_test,
                    km_intervals,
                    model_intervals[(alpha, horizon, key)],
                    y_train,
                    reference_label="predictor_free_km",
                    comparison_label=key,
                    **common,
                )
                for key in sorted(fitted_models)
            }
            setting_key = f"alpha{alpha:g}__horizon{horizon:g}"
            report["settings"][setting_key] = {
                "alpha": alpha,
                "nominal_coverage": 1 - alpha,
                "horizon_months": horizon,
                "km_initial_interval_months": [km_lower, km_upper],
                "km_conformal_quantile_months": (
                    None
                    if not np.isfinite(calibration_state.quantile)
                    else calibration_state.quantile
                ),
                "km_conformal_quantile_is_infinite": bool(
                    not np.isfinite(calibration_state.quantile)
                ),
                "km_calibration_n": calibration_state.n_cal,
                "km_calibration_stratum_counts": calibration_state.stratum_counts,
                "km_calibration_stratum_quantiles": calibration_state.to_dict()[
                    "stratum_quantiles"
                ],
                "marginal": summaries,
                "paired_model_minus_predictor_free_km": paired,
            }
    result_path = directory / "results.json"
    write_json(result_path, report)
    from brca.viz.predictor_free import export_predictor_free_baseline

    exports = export_predictor_free_baseline(report, run.outputs, run.config)
    return [plan_path, result_path, *exports]
