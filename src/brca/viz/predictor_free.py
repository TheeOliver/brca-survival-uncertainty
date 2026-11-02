"""Compact publication exports for the predictor-free baseline comparison."""

# Output is Macedonian with standard Latin method acronyms (Cox, IPCW, PAM50).
# ruff: noqa: RUF001

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ARM_LABELS = {
    "predictor_free_km_conformal": "KM конформал",
    "trivial_full_horizon": "Тривијален хоризонт",
    "disease_specific__cox__clinical": "Cox клинички",
    "disease_specific__cox__clinical_molecular": "Cox клин. + PAM50",
    "disease_specific__weibull__clinical": "Weibull клинички",
    "disease_specific__weibull__clinical_molecular": "Weibull клин. + PAM50",
    "disease_specific__rsf__clinical": "RSF клинички",
    "disease_specific__rsf__clinical_molecular": "RSF клин. + PAM50",
}
COLORS = {
    "predictor_free_km_conformal": "#2a78d6",
    "trivial_full_horizon": "#767676",
    "disease_specific__cox__clinical": "#1baf7a",
    "disease_specific__cox__clinical_molecular": "#1baf7a",
    "disease_specific__weibull__clinical": "#eb6834",
    "disease_specific__weibull__clinical_molecular": "#eb6834",
    "disease_specific__rsf__clinical": "#6b4c9a",
    "disease_specific__rsf__clinical_molecular": "#6b4c9a",
}
MARKERS = {
    "predictor_free_km_conformal": "o",
    "trivial_full_horizon": "s",
    "disease_specific__cox__clinical": "o",
    "disease_specific__cox__clinical_molecular": "D",
    "disease_specific__weibull__clinical": "o",
    "disease_specific__weibull__clinical_molecular": "D",
    "disease_specific__rsf__clinical": "o",
    "disease_specific__rsf__clinical_molecular": "D",
}
ARM_ORDER = tuple(ARM_LABELS)


def _format_percent(value):
    return "--" if value is None else f"{100 * value:.1f}".replace(".", ",") + r"\%"


def _format_width(summary):
    median = summary["width_median_months"]
    if median is None:
        return r"$\infty$"
    return (
        f"{median:.1f} ({summary['width_q25_months']:.1f}--{summary['width_q75_months']:.1f})"
    ).replace(".", ",")


def _format_ipcw(summary):
    estimate = summary["ipcw_coverage"]
    ci = summary["ipcw_coverage_ci"]
    if estimate is None or ci is None:
        return "--"
    return f"{estimate:.3f} ({ci[0]:.3f}; {ci[1]:.3f})".replace(".", ",")


def export_predictor_free_baseline(report: dict, directory: Path, config) -> list[Path]:
    """Export the prespecified main comparison from the stored aggregate report only."""
    table_directory = directory / "tables"
    figure_directory = directory / "figures"
    table_directory.mkdir(parents=True, exist_ok=True)
    figure_directory.mkdir(parents=True, exist_ok=True)
    alpha = report["main_comparison"]["alpha"]
    horizon = report["main_comparison"]["horizon_months"]
    setting_key = f"alpha{alpha:g}__horizon{horizon:g}"
    setting = report["settings"][setting_key]
    summaries = setting["marginal"]

    table = table_directory / "predictor_free_baseline_main.tex"
    rows = []
    for arm in ARM_ORDER:
        summary = summaries[arm]
        rows.append(
            " & ".join(
                (
                    ARM_LABELS[arm],
                    f"{_format_percent(summary['observable_coverage_lower'])}--"
                    f"{_format_percent(summary['observable_coverage_upper'])}",
                    _format_ipcw(summary),
                    _format_width(summary),
                    _format_percent(summary["full_support_fraction"]),
                    _format_percent(summary["near_full_horizon_fraction"]),
                )
            )
            + r" \\"
        )
    table.write_text(
        "% Generated from predictor-free baseline aggregate results. Do not edit values by hand.\n"
        "\\begin{table}[htbp]\n\\centering\n\\small\n"
        "\\setlength{\\tabcolsep}{3pt}\n"
        f"\\caption{{Референтен модел без предиктори при {100 * (1 - alpha):.0f}\\% "
        f"номинална покриеност и хоризонт од {horizon:g} месеци. Границите се "
        "компатибилни со цензурирањето; IPCW бара независно цензурирање и доволна "
        "поддршка. Ширината е медијана (интерквартилен распон) во месеци. "
        "Пост-хок споредбата на тест-множеството е експлораторна.}\n"
        "\\label{tab:predictor-free-baseline}\n"
        "\\begin{tabular}{@{}lccccc@{}}\n\\toprule\n"
        + r"Метод & Coverage граници & IPCW [95\% CI] & Ширина [медијана (IQR)] "
        + r"& Целосен & Речиси цел \\"
        + "\n"
        + "\\midrule\n"
        + "\n".join(rows)
        + "\n\\bottomrule\n\\end{tabular}\n"
        "\\begin{minipage}{0.98\\linewidth}\\footnotesize\n"
        "Целосен опсег значи интервал $[0,\\tau]$; речиси цел интервал има ширина најмалку "
        f"{100 * report['near_full_width_fraction']:.0f}\\% од $\\tau$. Тривијалниот "
        "интервал има 100\\% покриеност по конструкција, но не носи индивидуална "
        "информација. Недостапните IPCW процени укажуваат на недоволна цензурирачка "
        "поддршка.\n\\end{minipage}\n\\end{table}\n"
    )

    figure = figure_directory / "predictor_free_baseline_main.pdf"
    preview = figure_directory / "predictor_free_baseline_main.png"
    fig, (coverage_ax, width_ax) = plt.subplots(
        2,
        1,
        sharey=True,
        figsize=(config.figures.width_inches, max(config.figures.height_inches, 5.4)),
    )
    positions = list(range(len(ARM_ORDER)))
    labels = [ARM_LABELS[arm] for arm in ARM_ORDER]
    for position, arm in zip(positions, ARM_ORDER, strict=True):
        summary = summaries[arm]
        color, marker = COLORS[arm], MARKERS[arm]
        coverage_ax.hlines(
            position,
            summary["observable_coverage_lower"],
            summary["observable_coverage_upper"],
            color=color,
            linewidth=3,
        )
        estimate, ci = summary["ipcw_coverage"], summary["ipcw_coverage_ci"]
        if estimate is not None:
            if ci is not None:
                coverage_ax.hlines(position, *ci, color=color, linewidth=1.3)
            coverage_ax.plot(
                estimate,
                position,
                marker=marker,
                color=color,
                markersize=7,
                markeredgecolor="white",
                markeredgewidth=0.6,
                linestyle="none",
            )
        median = summary["width_median_months"]
        if median is not None:
            width_ax.hlines(
                position,
                summary["width_q25_months"],
                summary["width_q75_months"],
                color=color,
                linewidth=3,
            )
            width_ax.plot(
                median,
                position,
                marker=marker,
                color=color,
                markersize=7,
                markeredgecolor="white",
                markeredgewidth=0.6,
                linestyle="none",
            )
    coverage_ax.axvline(1 - alpha, color="#767676", linewidth=1, linestyle=":")
    coverage_ax.set_xlim(0, 1.03)
    coverage_ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    coverage_ax.set_ylabel("Постапка")
    coverage_ax.set_xlabel("Емпириска покриеност")
    coverage_ax.set_yticks(positions, labels)
    coverage_ax.invert_yaxis()
    coverage_ax.grid(axis="x", color="#dddddd", linewidth=0.6)
    width_ax.set_xlim(0, horizon * 1.03)
    width_ax.set_xlabel("Ширина на интервалот (месеци)")
    width_ax.grid(axis="x", color="#dddddd", linewidth=0.6)
    width_ax.set_yticks(positions, labels)
    width_ax.invert_yaxis()
    coverage_ax.tick_params(axis="both", labelsize=8)
    width_ax.tick_params(axis="both", labelsize=8)
    coverage_ax.xaxis.label.set_size(9)
    width_ax.xaxis.label.set_size(9)
    coverage_ax.yaxis.label.set_size(9)
    fig.legend(
        handles=[
            Line2D([], [], color="#333333", linewidth=3, label="Coverage граници"),
            Line2D([], [], color="#333333", marker="o", linestyle="none", label="IPCW процена"),
            Line2D(
                [], [], color="#767676", linestyle=":", label=f"Номинално {100 * (1 - alpha):g}%"
            ),
        ],
        loc="upper center",
        bbox_to_anchor=(0.62, 0.995),
        ncol=3,
        fontsize=8,
        frameon=False,
    )
    fig.subplots_adjust(left=0.34, right=0.98, bottom=0.1, top=0.91, hspace=0.22)
    fig.savefig(figure, metadata={"CreationDate": None, "ModDate": None})
    fig.savefig(preview, dpi=config.figures.dpi)
    plt.close(fig)
    return [table, figure, preview]
