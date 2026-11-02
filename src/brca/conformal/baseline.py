"""Predictor-free survival distribution used as an exploratory benchmark."""

from __future__ import annotations

import numpy as np
from sksurv.nonparametric import kaplan_meier_estimator

from brca.conformal.survival import _labels


def restricted_km_interval(
    y_train: np.ndarray, alpha: float, horizon: float
) -> tuple[float, float]:
    """Return an equal-tailed KM interval for ``min(T, horizon)``.

    The same endpoints apply to every patient. The Kaplan-Meier distribution is
    estimated from training outcomes only; probability mass remaining at the
    horizon is assigned to the restricted target value ``horizon``.
    """
    _event, time = _labels(y_train)
    if not len(time):
        raise ValueError("Training outcomes are required for the predictor-free KM baseline.")
    if not np.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha is miscoverage and must be between zero and one.")
    if not np.isfinite(horizon) or horizon <= 0:
        raise ValueError("The restricted KM interval requires a finite positive horizon.")

    event_times, survival = kaplan_meier_estimator(y_train["event"], time)
    cdf = 1.0 - survival

    def quantile(probability: float) -> float:
        reached = np.flatnonzero((event_times <= horizon) & (cdf >= probability))
        return float(event_times[reached[0]]) if reached.size else float(horizon)

    lower = quantile(alpha / 2)
    upper = quantile(1 - alpha / 2)
    return lower, max(lower, upper)
