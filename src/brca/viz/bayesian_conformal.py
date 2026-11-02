"""Compact LaTeX exports for the Bayesian/post-conformal comparison."""

# Output is Macedonian with standard Latin method acronyms (Bayesian, IPCW, PAM50).
# ruff: noqa: RUF001

from __future__ import annotations

from pathlib import Path
from typing import Any

FEATURE_LABELS = {
    "clinical": "Клинички",
    "clinical_molecular": "Клинички + PAM50",
}


def _percent_bound(summary: dict[str, Any], name: str) -> str:
    value = summary[name]
    return r"\multicolumn{1}{c}{--}" if value is None else f"{100 * value:.1f}"


def _percent_bounds(summary: dict[str, Any]) -> str:
    lower, upper = summary["observable_coverage_lower"], summary["observable_coverage_upper"]
    if lower is None or upper is None:
        return "--"
    return f"{100 * lower:.1f}\\%--{100 * upper:.1f}\\%"


def _ipcw(summary: dict[str, Any]) -> str:
    value, ci = summary["ipcw_coverage"], summary["ipcw_coverage_ci"]
    if value is None or ci is None or any(bound is None for bound in ci):
        return "недостапно"
    return f"{value:.3f} ({ci[0]:.3f}; {ci[1]:.3f})"


def _width_iqr(summary: dict[str, Any]) -> str:
    lower, upper = summary["width_q25_months"], summary["width_q75_months"]
    if lower is None or upper is None:
        return "--"
    return f"{lower:.1f}--{upper:.1f}"


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def export_bayesian_conformal_tables(report: dict[str, Any], output_root: Path) -> list[Path]:
    """Export primary and supplementary tables from the frozen aggregate report."""
    alpha = report["main_comparison"]["alpha"]
    horizon = report["main_comparison"]["horizon_months"]
    main_key = f"alpha{alpha:g}__horizon{horizon:g}"
    primary = report["settings"][main_key]["feature_sets"]
    table_dir = output_root / "tables"

    metric_rows = []
    for feature in FEATURE_LABELS:
        pair = primary[feature]
        metric_rows.append(
            f"{FEATURE_LABELS[feature]} & Баесовски предиктивен"
            f" ($n_{{cal}}={pair['posterior_predictive']['n_cal']}$)"
            f" & {_percent_bound(pair['posterior_predictive'], 'observable_coverage_lower')}"
            f" & {_percent_bound(pair['posterior_predictive'], 'observable_coverage_upper')}"
            f" & {_ipcw(pair['posterior_predictive'])}"
            f" & {pair['posterior_predictive']['width_median_months']:.1f}"
            f" & {_width_iqr(pair['posterior_predictive'])} \\\\"
        )
        metric_rows.append(
            f" & конформализиран"
            f" ($n_{{cal}}={pair['conformalized']['n_cal']}$)"
            f" & {_percent_bound(pair['conformalized'], 'observable_coverage_lower')}"
            f" & {_percent_bound(pair['conformalized'], 'observable_coverage_upper')}"
            f" & {_ipcw(pair['conformalized'])}"
            f" & {pair['conformalized']['width_median_months']:.1f}"
            f" & {_width_iqr(pair['conformalized'])} \\\\"
        )
    primary_metrics = "\n".join(metric_rows)
    metrics_path = _write(
        table_dir / "bayesian_conformal_primary_metrics.tex",
        r"""% Generated from the frozen Bayesian/conformal comparison results.
% Requires booktabs and siunitx.
\begin{table}[htbp]
\centering
\small
\setlength{\tabcolsep}{4pt}
\caption{Байесови индивидуални предиктивни интервали пред и по конформална
калибрација при 90\% номинална покриеност и хоризонт од 120 месеци.
Границите се компатибилни со цензурирањето; IPCW претпоставува независно
цензурирање. Бројот на тест-пациенти е
"""
        + str(report["n_test"])
        + r""". Ширината е медијана и IQR во месеци.}
\label{tab:bayesian-conformal-primary-metrics}
\begin{tabular}{@{}ll S[table-format=2.1] S[table-format=2.1] l S[table-format=3.1] l@{}}
\toprule
Предиктори & Интервал & {Долна граница, \%} & {Горна граница, \%} & IPCW [95\% CI]
& {Медијана, месеци} & IQR \\
\midrule
"""
        + primary_metrics
        + r"""
\bottomrule
\end{tabular}
\end{table}
""",
    )

    difference_rows = []
    for feature in FEATURE_LABELS:
        paired = primary[feature]["paired_conformal_minus_posterior_predictive"]
        for name, label, percent in (
            ("observable_coverage_lower", "Долна граница покриеност, п.п.", True),
            ("observable_coverage_upper", "Горна граница покриеност, п.п.", True),
            ("ipcw_coverage", "IPCW покриеност, п.п.", True),
            ("width_median_months", "Медијана ширина, месеци", False),
        ):
            difference = paired["differences"][name]
            factor = 100 if percent else 1
            values = [difference["estimate"], *(difference["ci"] or [None, None])]
            formatted = [
                r"\multicolumn{1}{c}{--}" if value is None else f"{factor * value:+.1f}"
                for value in values
            ]
            difference_rows.append(
                f"{FEATURE_LABELS[feature]} & {label} & " + " & ".join(formatted) + r" \\"
            )
    difference_path = _write(
        table_dir / "bayesian_conformal_primary_differences.tex",
        r"""% Generated from paired test-patient bootstrap differences.
% Requires booktabs and siunitx.
\begin{table}[htbp]
\centering
\small
\setlength{\tabcolsep}{3pt}
\caption{Конформализирани минус оригинални Баесови интервали. Прикажани се
спарените разлики и 95\% bootstrap интервали за примарната споредба.}
\label{tab:bayesian-conformal-primary-differences}
\begin{tabular}{@{}ll S[table-format=+3.1] S[table-format=+3.1] S[table-format=+3.1]@{}}
\toprule
Предиктори & Мерка & {Разлика} & {95\% CI долна} & {95\% CI горна} \\
\midrule
"""
        + "\n".join(difference_rows)
        + r"""
\bottomrule
\end{tabular}
\end{table}
""",
    )

    supplement_rows = []
    for _, setting in sorted(report["settings"].items()):
        for feature in FEATURE_LABELS:
            pair = setting["feature_sets"][feature]
            delta = pair["paired_conformal_minus_posterior_predictive"]["differences"][
                "width_median_months"
            ]
            ci = delta["ci"]
            delta_text = (
                "--"
                if delta["estimate"] is None or ci is None or any(x is None for x in ci)
                else f"{delta['estimate']:+.1f} [{ci[0]:+.1f}; {ci[1]:+.1f}]"
            )
            supplement_rows.append(
                f"{1 - setting['alpha']:.0%} & {setting['horizon_months']:.0f}"
                f" & {FEATURE_LABELS[feature]}"
                f" & {_percent_bounds(pair['posterior_predictive'])}; "
                f"{_percent_bounds(pair['conformalized'])}"
                f" & {pair['posterior_predictive']['width_median_months']:.1f}; "
                f"{pair['conformalized']['width_median_months']:.1f}"
                f" & {delta_text} \\\\"
            )
    supplement_path = _write(
        table_dir / "bayesian_conformal_supplement.tex",
        r"""% Generated from all registered alpha and horizon settings.
% Requires booktabs.
\begin{table}[htbp]
\centering
\small
\setlength{\tabcolsep}{3pt}
\caption{Дополнителни Баесови и конформализирани резултати за сите регистрирани
нивоа и хоризонти. Границите на покриеност и разликите се спарени по
тест-пациент; IPCW е прикажан во агрегатниот JSON и е изоставен тука за
компактност. При 300 месеци поддршката за IPCW е недоволна.}
\label{tab:bayesian-conformal-supplement}
\begin{tabular}{@{}cc lcc c@{}}
\toprule
Номинална & Хоризонт & Предиктори & Граници: оригинални; конформализирани
& Медијана на ширина: оригинална; конформализирана & Δ ширина [95\% CI] \\
\midrule
"""
        + "\n".join(supplement_rows)
        + r"""
\bottomrule
\end{tabular}
\end{table}
""",
    )
    return [metrics_path, difference_path, supplement_path]
