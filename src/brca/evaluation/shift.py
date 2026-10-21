"""Covariate diagnostics and fixed-population stress tests of frozen intervals.

Weights define a hypothetical population q(x) proportional to w(x)p(x). They
are used only to evaluate existing prediction intervals. This is not weighted
conformal calibration and supplies no new coverage guarantee under shift.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
import pandas as pd

from brca.conformal.survival import (
    PredictionIntervals,
    _bootstrap_indices,
    _coverage_indicators,
    _draw_summary,
    _validate_bootstrap,
)


def _numeric(frame: pd.DataFrame, column: str) -> np.ndarray:
    if column not in frame:
        raise ValueError(f"Missing covariate column: {column}")
    values = pd.to_numeric(frame[column], errors="raise").to_numpy(dtype=float, na_value=np.nan)
    if np.isinf(values).any():
        raise ValueError(f"Infinite numeric covariates in {column}")
    return values


def _categories(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame:
        raise ValueError(f"Missing covariate column: {column}")
    # Preserve a real string '(missing)' distinctly from missing cells.
    return frame[column].map(
        lambda item: ("missing", "") if pd.isna(item) else ("value", str(item))
    )


def covariate_shift_report(
    source_train: pd.DataFrame,
    target: pd.DataFrame,
    numeric_columns: Sequence[str],
    categorical_columns: Sequence[str],
    minimum_group_size: int,
    *,
    source_quantiles: Sequence[float] = (0.05, 0.95),
) -> dict[str, Any]:
    """Describe feature and recording differences without inspecting outcomes.

    Numeric SMD divides target minus source mean by the square root of the
    average of the two sample variances. Overlap is the fraction of observed
    target values inside a prespecified central source range. Categorical total
    variation includes missing as a separate level. Small category counts and
    their proportions are suppressed; aggregate distances retain all levels.
    """
    if (
        not isinstance(minimum_group_size, int)
        or isinstance(minimum_group_size, bool)
        or minimum_group_size < 2
        or len(source_train) == 0
        or len(target) == 0
    ):
        raise ValueError("Nonempty populations and a minimum group size >= 2 are required")
    quantiles = np.asarray(source_quantiles, dtype=float)
    if (
        quantiles.shape != (2,)
        or not np.isfinite(quantiles).all()
        or not 0 <= quantiles[0] < quantiles[1] <= 1
    ):
        raise ValueError("Source quantiles must be two increasing probabilities")
    all_columns = [*numeric_columns, *categorical_columns]
    if len(set(all_columns)) != len(all_columns):
        raise ValueError("Covariate column lists must not overlap or contain duplicates")
    report: dict[str, Any] = {
        "n_source_train": len(source_train),
        "n_target": len(target),
        "source_quantiles": quantiles.tolist(),
        "minimum_group_size": minimum_group_size,
        "scope": "descriptive_covariates_only; does_not_identify_conditional_outcome_shift",
        "numeric": {},
        "categorical": {},
    }
    for column in numeric_columns:
        source_all, target_all = _numeric(source_train, column), _numeric(target, column)
        source = source_all[~np.isnan(source_all)]
        values = target_all[~np.isnan(target_all)]
        item: dict[str, Any] = {
            "source_missing_fraction": float(np.isnan(source_all).mean()),
            "target_missing_fraction": float(np.isnan(target_all).mean()),
            "n_source_observed": len(source),
            "n_target_observed": len(values),
            "standardized_mean_difference": None,
            "source_range": None,
            "target_fraction_inside_source_range": None,
        }
        if len(source) < minimum_group_size or len(values) < minimum_group_size:
            item["status"] = "insufficient_observed_values"
        else:
            bounds = np.quantile(source, quantiles)
            difference = float(values.mean() - source.mean())
            denominator = float(np.sqrt((source.var(ddof=1) + values.var(ddof=1)) / 2))
            item.update(
                {
                    "source_mean": float(source.mean()),
                    "target_mean": float(values.mean()),
                    "source_range": bounds.tolist(),
                    "target_fraction_inside_source_range": float(
                        ((values >= bounds[0]) & (values <= bounds[1])).mean()
                    ),
                    "standardized_mean_difference": (
                        difference / denominator
                        if denominator > 0
                        else 0.0
                        if difference == 0
                        else None
                    ),
                    "status": "ok"
                    if denominator > 0 or difference == 0
                    else "zero_pooled_variance",
                }
            )
        report["numeric"][column] = item
    for column in categorical_columns:
        source, values = _categories(source_train, column), _categories(target, column)
        source_counts, target_counts = source.value_counts(), values.value_counts()
        levels = sorted(set(source) | set(values))
        total_variation = 0.0
        categories = []
        for level in levels:
            n_source = int(source_counts.get(level, 0))
            n_target = int(target_counts.get(level, 0))
            p_source, p_target = n_source / len(source), n_target / len(values)
            total_variation += abs(p_target - p_source) / 2
            suppressed = any(0 < n < minimum_group_size for n in (n_source, n_target))
            categories.append(
                {
                    "level": "(missing)" if level[0] == "missing" else level[1],
                    "is_missing": level[0] == "missing",
                    "n_source": None if suppressed else n_source,
                    "n_target": None if suppressed else n_target,
                    "source_fraction": None if suppressed else p_source,
                    "target_fraction": None if suppressed else p_target,
                    "status": "suppressed_small_group" if suppressed else "ok",
                }
            )
        report["categorical"][column] = {
            "source_missing_fraction": float(source_train[column].isna().mean()),
            "target_missing_fraction": float(target[column].isna().mean()),
            "total_variation_distance": total_variation,
            "categories": categories,
            "status": "ok",
        }
    return report


def shift_weights(
    train: pd.DataFrame, test: pd.DataFrame, scenario: Mapping[str, Any]
) -> np.ndarray:
    """Return fixed covariate weights; numeric location/scale use train only.

    ``age_tilt`` accepts column, beta and z_clip. Missing test values use the
    observed training median before applying the tilt. ``categorical_multiplier``
    accepts column, value and a strictly positive factor. ``baseline`` uses ones.
    """
    kind = scenario.get("kind")
    if kind == "baseline":
        return np.ones(len(test), dtype=float)
    if kind == "age_tilt":
        column = scenario["column"]
        source, values = _numeric(train, column), _numeric(test, column)
        source = source[~np.isnan(source)]
        beta, z_clip = float(scenario["beta"]), float(scenario["z_clip"])
        if not len(source) or not np.isfinite([beta, z_clip]).all() or z_clip <= 0:
            raise ValueError("Age tilt needs finite parameters and observed training values")
        scale = float(source.std(ddof=0))
        if scale <= 0:
            raise ValueError("Age tilt needs positive training variance")
        values = np.where(np.isnan(values), np.median(source), values)
        z = np.clip((values - source.mean()) / scale, -z_clip, z_clip)
        with np.errstate(over="ignore", under="ignore", invalid="ignore"):
            weights = np.exp(beta * z)
    elif kind == "categorical_multiplier":
        column, value, factor = (
            scenario["column"],
            str(scenario["value"]),
            float(scenario["factor"]),
        )
        if column not in test or column not in train:
            raise ValueError(f"Missing covariate column: {column}")
        if not np.isfinite(factor) or factor <= 0:
            raise ValueError("Category multiplier must be finite and strictly positive")
        matches = test[column].astype("string").eq(value).fillna(False).to_numpy(bool)
        weights = np.where(matches, factor, 1.0)
    else:
        raise ValueError(f"Unknown shift scenario kind: {kind}")
    if not np.isfinite(weights).all() or np.any(weights <= 0):
        raise ValueError("Shift parameters produce nonfinite or zero weights")
    return weights


def _weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    order = np.argsort(values, kind="stable")
    cumulative = np.cumsum(weights[order])
    threshold = cumulative[-1] / 2
    # The inverted empirical CDF agrees with existing interval reports,
    # including the lower middle order statistic for even-sized samples.
    index = min(int(np.searchsorted(cumulative, threshold)), len(order) - 1)
    return float(values[order[index]])


def weighted_interval_report(
    y: np.ndarray,
    intervals: PredictionIntervals,
    weights: np.ndarray,
    *,
    bootstrap_replicates: int,
    seed: int,
    confidence_level: float,
    minimum_success_fraction: float,
    bootstrap_strata: np.ndarray | None = None,
) -> dict[str, Any]:
    """Self-normalized weighted observable coverage bounds and interval widths.

    Bootstrap the original patients, keeping fixed source split strata when
    supplied, then recompute each weighted statistic. Equal seed and strata
    give paired resampling across methods and scenarios. This is uncertainty
    conditional on the frozen model, calibration and weight function. The two
    coverage bounds describe uncertainty due to censoring; their bootstrap
    confidence intervals describe sampling uncertainty and are distinct.
    """
    weights = np.asarray(weights, dtype=float)
    n = len(y)
    if n == 0 or weights.shape != (n,) or not np.isfinite(weights).all() or np.any(weights <= 0):
        raise ValueError("Weights must be aligned, finite, strictly positive and nonempty")
    if not np.isfinite(intervals.horizon):
        raise ValueError("Shift interval reports require a finite restricted horizon")
    certain, possible, _ = _coverage_indicators(y, intervals)
    strata = _validate_bootstrap(
        bootstrap_replicates, confidence_level, minimum_success_fraction, bootstrap_strata, n
    )
    # Max-rescaling avoids overflow while preserving self-normalized estimates.
    weights = weights / weights.max()
    if np.any(weights == 0):
        raise ValueError("Weight range exceeds stable floating-point precision")
    mass = weights.sum()
    normalized = weights / mass
    width = intervals.width
    points = {
        "coverage_lower_bound": float(np.dot(normalized, certain)),
        "coverage_upper_bound": float(np.dot(normalized, possible)),
        "mean_width": float(np.dot(normalized, width)),
        "median_width": _weighted_median(width, weights),
        "full_support_fraction": float(
            np.dot(normalized, (intervals.lower == 0) & (intervals.upper == intervals.horizon))
        ),
    }
    draws = {key: np.empty(bootstrap_replicates) for key in points}
    selections = _bootstrap_indices(n, bootstrap_replicates, seed, strata)
    full_support = (intervals.lower == 0) & (intervals.upper == intervals.horizon)
    for b, indices in enumerate(selections):
        selected_weights = weights[indices]
        proportions = selected_weights / selected_weights.sum()
        draws["coverage_lower_bound"][b] = np.dot(proportions, certain[indices])
        draws["coverage_upper_bound"][b] = np.dot(proportions, possible[indices])
        draws["mean_width"][b] = np.dot(proportions, width[indices])
        draws["median_width"][b] = _weighted_median(width[indices], selected_weights)
        draws["full_support_fraction"][b] = np.dot(proportions, full_support[indices])
    estimates = {
        key: {
            "estimate": value,
            **_draw_summary(draws[key], confidence_level, minimum_success_fraction),
        }
        for key, value in points.items()
    }
    with np.errstate(over="ignore"):
        weight_ratio = float(weights.max() / weights.min())
    return {
        "n_test": n,
        "n_cal": intervals.n_cal,
        "alpha": intervals.alpha,
        "nominal_coverage": 1 - intervals.alpha,
        "horizon_months": intervals.horizon,
        "method": intervals.method,
        "effective_sample_size": float(1 / np.dot(normalized, normalized)),
        "maximum_normalized_weight": float(normalized.max()),
        "weight_ratio_max_to_min": weight_ratio if np.isfinite(weight_ratio) else None,
        "weight_ratio_is_infinite": not np.isfinite(weight_ratio),
        "estimates": estimates,
        "bootstrap_replicates": bootstrap_replicates,
        "bootstrap_seed": seed,
        "confidence_level": confidence_level,
        "bootstrap_stratified": strata is not None,
        "ci_scope": "source_patient_bootstrap_conditional_on_frozen_model_calibration_and_weights",
        "weighting_scope": "evaluation_of_fixed_intervals_not_weighted_conformal_calibration",
        "coverage_scope": "observable_bounds_for_restricted_event_time_no_censoring_model",
        "status": (
            "bootstrap_gate_failed"
            if any(item["status"] == "bootstrap_gate_failed" for item in estimates.values())
            else "ok"
        ),
    }
