"""Post hoc case-mix stress test of frozen METABRIC prediction intervals.

The stage-05 caller alone opens the previously frozen test cache. This module
never refits a model or recalibrates an interval under the hypothetical shifts.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import yaml

from brca.calibration import interval_key, load_calibration, model_quantiles
from brca.config import PROJECT_ROOT
from brca.conformal.lower import LowerBoundCalibration
from brca.conformal.qin import QinBootstrap, predict_qin_intervals
from brca.conformal.survival import ConformalCalibration
from brca.data.eda import outcome_labels
from brca.data.partitions import load_partition
from brca.data.preprocessing import TrainingPreprocessor
from brca.evaluation.shift import shift_weights, weighted_interval_report
from brca.fitting import load_fit
from brca.manifest import sha256_file, write_json_exclusive
from brca.models.cox import CoxPHModel
from brca.pipeline import named_rng, write_json


def shift_directory(run):
    return run.outputs / "distribution_shift"


def freeze_shift_plan(run, index, settings_path):
    """Bind source, settings and historical artifacts before test-cache access."""
    settings_path = Path(settings_path).resolve()
    settings = yaml.safe_load(settings_path.read_text())
    if set(settings) != {"distribution_shift"}:
        raise ValueError("Shift settings must contain only distribution_shift")
    cfg = settings["distribution_shift"]
    if (
        cfg["alphas"] != run.config.conformal.alphas
        or set(cfg["horizons_months"]) != set(run.config.conformal.horizons_months)
        or cfg["report_alpha"] not in cfg["alphas"]
        or cfg["report_horizon_months"] not in cfg["horizons_months"]
        or not isinstance(cfg["bootstrap_replicates"], int)
        or cfg["bootstrap_replicates"] < 2
        or not 0 < cfg["confidence_level"] < 1
        or not 0 < cfg["minimum_success_fraction"] <= 1
        or set(cfg["scenarios"]) != {"baseline", "younger", "older", "basal_enriched"}
        or cfg["scenarios"]["baseline"] != {"kind": "baseline"}
    ):
        raise ValueError("Unreviewed shift experiment settings")
    original_path = run.outputs / "evaluation/plan.json"
    original = json.loads(original_path.read_text())
    fit_index_path = run.outputs / "models/fit_index.json"
    cache_path = run.outputs / "evaluation/test_cache.pkl"
    calibration_path = run.outputs / "models/conformal_calibration.json"
    reliability_dir = run.outputs / "uncertainty_reliability"
    reliability_path = reliability_dir / "preparation.json"
    reliability = json.loads(reliability_path.read_text())
    reliability_binding = json.loads((reliability_dir / "preparation_binding.json").read_text())
    if (
        original["config_sha256"] != run.metadata["config_sha256"]
        or original["fit_index_sha256"] != sha256_file(fit_index_path)
        or original["test_cache_sha256"] != sha256_file(cache_path)
        or original["calibration_sha256"] != sha256_file(calibration_path)
        or index["training_sha256"] != sha256_file(run.processed / "partitions/train.csv")
        or reliability_binding["preparation_sha256"] != sha256_file(reliability_path)
        or reliability_binding["plan_sha256"] != sha256_file(reliability_dir / "plan.json")
    ):
        raise ValueError("Frozen source or reliability inputs changed")
    bindings = {
        str(path): sha256_file(path)
        for path in (
            original_path,
            fit_index_path,
            cache_path,
            calibration_path,
            reliability_path,
            reliability_dir / "preparation_binding.json",
            reliability_dir / "plan.json",
            run.outputs / "metrics/conformal_coverage.json",
            reliability_dir / "coverage.json",
        )
    }
    for record in index["models"].values():
        bindings.update(record["artifacts_sha256"])
    bindings.update(reliability["artifacts_sha256"])
    if any(sha256_file(path) != digest for path, digest in bindings.items()):
        raise ValueError("A frozen model or evaluation artifact changed")
    sources = sorted(
        [
            PROJECT_ROOT / "scripts/05_evaluate.py",
            *[
                path
                for path in (PROJECT_ROOT / "src/brca").rglob("*.py")
                if "viz" not in path.parts and path.name != "reporting.py"
            ],
        ]
    )
    protocol = {
        "schema_version": 1,
        "status": "post_hoc_internal_case_mix_shift",
        "settings": cfg,
        "settings_sha256": sha256_file(settings_path),
        "config_sha256": run.metadata["config_sha256"],
        "lock_sha256": sha256_file(PROJECT_ROOT / "uv.lock"),
        "analysis_source_sha256": {
            str(path.relative_to(PROJECT_ROOT)): sha256_file(path) for path in sources
        },
        "frozen_inputs_sha256": bindings,
        "coverage_guarantee_under_shift": False,
    }
    path = shift_directory(run) / "plan.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if json.loads(path.read_text()) != protocol:
            raise ValueError("Opened distribution-shift plan or source changed")
    else:
        write_json_exclusive(path, protocol)
    return cfg


def _intervals_for_model(model, X, key, states, alphas, horizons, ridge=None):
    quantiles = model_quantiles(model, X, alphas)
    low_quantiles = model.predict_quantiles(X, np.array(alphas))
    for a, alpha in enumerate(alphas):
        for horizon in horizons:
            k = interval_key(key, alpha, horizon, "conservative")
            yield (
                k,
                ConformalCalibration.from_dict(states[k]["calibration"]).predict(
                    *np.minimum(quantiles[alpha], horizon).T
                ),
            )
            k = interval_key(key, alpha, horizon, "conservative_lower_bound")
            if k in states:
                yield (
                    k,
                    LowerBoundCalibration.from_dict(states[k]["calibration"]).predict(
                        low_quantiles[:, a]
                    ),
                )
            if ridge is not None:
                ridge_model, bootstrap = ridge
                k = interval_key(key, alpha, horizon, "qin_bootstrap_ridge_cox")
                yield (
                    k,
                    replace(
                        predict_qin_intervals(
                            ridge_model, X, bootstrap, alpha=alpha, horizon=horizon
                        ),
                        method="qin_bootstrap_ridge_cox",
                    ),
                )


def run_shift_analysis(run, index, cfg, test):
    """Evaluate all original methods under fixed positive covariate weights."""
    directory = shift_directory(run)
    train = load_partition(run.config, "train")
    states = load_calibration(run, index)["states"]
    reliability = json.loads((run.outputs / "uncertainty_reliability/preparation.json").read_text())
    states = {**states, **reliability["lower_states"]}
    weights = {
        name: shift_weights(train, test, scenario) for name, scenario in cfg["scenarios"].items()
    }
    seed = int(named_rng(run.config.seed, "shift_bootstrap").integers(0, np.iinfo(np.uint32).max))
    results = {}
    for key, record in index["models"].items():
        model = load_fit(record)
        pre = TrainingPreprocessor.load(Path(index["preprocessors"][record["feature_set"]]))
        X = pre.transform(test)
        ridge = None
        if key in reliability["ridge"]:
            item = reliability["ridge"][key]
            ridge = (
                CoxPHModel.load(item["path"]),
                QinBootstrap(np.array(item["pivots"]), item["diagnostics"]),
            )
        for cell, intervals in _intervals_for_model(
            model, X, key, states, cfg["alphas"], cfg["horizons_months"], ridge
        ):
            results[cell] = {
                "endpoint": record["endpoint"],
                "model": record["model"],
                "feature_set": record["feature_set"],
                "method": intervals.method,
                "alpha": intervals.alpha,
                "horizon_months": intervals.horizon,
                "scenarios": {
                    name: weighted_interval_report(
                        outcome_labels(test, record["endpoint"]),
                        intervals,
                        w,
                        bootstrap_replicates=cfg["bootstrap_replicates"],
                        seed=seed,
                        confidence_level=cfg["confidence_level"],
                        minimum_success_fraction=cfg["minimum_success_fraction"],
                        bootstrap_strata=test["event"].to_numpy(bool),
                    )
                    for name, w in weights.items()
                },
            }
        print(f"Frozen-model shift evaluated: {key}", flush=True)
    output = {
        "status": "post_hoc_test_reuse",
        "n_original_test": len(test),
        "scenarios": cfg["scenarios"],
        "coverage_guarantee_under_shift": False,
        "interpretation": (
            "Weighted target-population summaries; no new independent patients or recalibration"
        ),
        "results": results,
    }
    path = directory / "distribution_shift.json"
    write_json(path, output)
    return path
