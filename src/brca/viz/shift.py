"""Print-sized coverage-and-width figure from stored shift summaries."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from brca.viz.coverage import REFERENCE, _number, _save

METHODS = {
    "conservative_score_envelope": ("Envelope", "#2a78d6", "o"),
    "conservative_lower_bound": ("Lower bound", "#eb6834", "s"),
    "qin_bootstrap_ridge_cox": ("Qin ridge", "#1baf7a", "^"),
}


def _whisker(ax, x, statistic, color, marker):
    estimate, ci = statistic["estimate"], statistic.get("ci")
    if ci is not None and all(_number(value) for value in ci):
        ax.vlines(x, *ci, color=color, linewidth=1.5)
    ax.plot(
        x,
        estimate,
        marker=marker,
        color=color,
        markersize=8,
        linestyle="none",
        markeredgecolor="white",
        markeredgewidth=0.8,
    )


def render_shift_figure(report, settings, figure_settings, directory: Path):
    """Plot frozen DSS Cox+PAM50 intervals under the declared scenarios."""
    alpha = settings["report_alpha"]
    horizon = settings["report_horizon_months"]
    rows = {
        row["method"]: row
        for row in report["results"].values()
        if row["endpoint"] == "disease_specific"
        and row["model"] == "cox"
        and row["feature_set"] == "clinical_molecular"
        and row["alpha"] == alpha
        and row["horizon_months"] == horizon
    }
    if set(rows) != set(METHODS):
        raise ValueError("The declared figure requires all three Cox+PAM50 methods")
    scenarios = list(settings["scenarios"])
    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(figure_settings.width_inches, 5.8))
    fig.subplots_adjust(left=0.15, right=0.98, bottom=0.15, top=0.81, hspace=0.15)
    legends = []
    for j, (method, (label, color, marker)) in enumerate(METHODS.items()):
        legends.append(
            Line2D([], [], color=color, marker=marker, linestyle="none", label=label, markersize=8)
        )
        for i, scenario in enumerate(scenarios):
            values = rows[method]["scenarios"][scenario]["estimates"]
            x = i + (j - (len(METHODS) - 1) / 2) * 0.22
            low = values["coverage_lower_bound"]
            high = values["coverage_upper_bound"]
            axes[0].vlines(
                x, low["estimate"], high["estimate"], color=color, linewidth=5, alpha=0.3
            )
            for statistic in (low, high):
                _whisker(axes[0], x, statistic, color, marker)
            _whisker(axes[1], x, values["median_width"], color, marker)
    axes[0].axhline(1 - alpha, color=REFERENCE, linewidth=1)
    axes[0].set(ylabel="Coverage bounds", ylim=(-0.02, 1.05))
    axes[1].set(ylabel="Median width (months)", ylim=(0, horizon * 1.05))
    axes[1].set_xticks(
        range(len(scenarios)), [name.replace("_", " ").capitalize() for name in scenarios]
    )
    fig.legend(handles=legends, loc="upper center", ncol=3, frameon=False)
    fig.text(
        0.15,
        0.86,
        "Coverage: thick range = observable bounds; whiskers = separate bound CIs.\n"
        "Width: symbol = weighted median; whisker = median CI.",
        fontsize=8,
    )
    for ax in axes:
        ax.grid(axis="y", linewidth=0.5, color="#dddddd")
        ax.set_axisbelow(True)
    directory.mkdir(parents=True, exist_ok=True)
    return _save(fig, directory, "shift_dss_coverage_width", figure_settings)
