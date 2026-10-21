# Selected METABRIC results

These aggregate results come from the completed local METABRIC analysis: breast-cancer-specific survival was primary, overall survival was a sensitivity analysis, and one frozen split contained 989 training, 495 calibration, and 495 test patients. The numerical pipeline has not been rerun from this new repository's Git history. This is internal validation, not external validation.

[Read the detailed primary results](thesis_results.md). Patient-level data, individual predictions, model objects, and full generated outputs are not published here.

- [Training survival by PAM50 (PNG)](figures/training_disease_specific_pam50_subtype_km.png) · [PDF](figures/training_disease_specific_pam50_subtype_km.pdf): descriptive EDA; late curves have few patients at risk.
- [Model discrimination (PNG)](figures/rq1_rq2_rq3_disease_specific_uno_c.png) · [PDF](figures/rq1_rq2_rq3_disease_specific_uno_c.pdf): Uno C with uncertainty.
- [Added PAM50 comparison (PNG)](figures/rq1_rq2_rq3_disease_specific_paired_uno_c.png) · [PDF](figures/rq1_rq2_rq3_disease_specific_paired_uno_c.pdf): paired feature-set differences.
- [Bayesian uncertainty example (PNG)](figures/rq4_hypothetical_uncertainty_reference.png) · [PDF](figures/rq4_hypothetical_uncertainty_reference.pdf): a hypothetical profile, not an individual clinical forecast.
- [Coverage and width at 120 months (PNG)](figures/rq5_coverage_vs_nominal__disease_specific__clinical_molecular__conservative__horizon120.png) · [PDF](figures/rq5_coverage_vs_nominal__disease_specific__clinical_molecular__conservative__horizon120.pdf).
- [Coverage and width at 300 months (PNG)](figures/rq5_coverage_vs_nominal__disease_specific__clinical_molecular__conservative__horizon300.png) · [PDF](figures/rq5_coverage_vs_nominal__disease_specific__clinical_molecular__conservative__horizon300.pdf): censoring support is insufficient for DSS IPCW coverage at this horizon.
- [Coverage by PAM50 subgroup (PNG)](figures/rq5_subgroup_coverage_width__disease_specific__clinical_molecular__conservative__horizon120__pam50_subtype.png) · [PDF](figures/rq5_subgroup_coverage_width__disease_specific__clinical_molecular__conservative__horizon120__pam50_subtype.pdf): exploratory; marginal coverage gives no subgroup guarantee.

The [overall training survival curve (PNG)](figures/training_disease_specific_overall_km.png) and its [PDF](figures/training_disease_specific_overall_km.pdf) provide additional EDA context. The detailed report gives the numerical results and limitations.

## Exploratory reliability comparison

[Read the post hoc reliability comparison](reliability_comparison.md), including coverage and width figures for disease-specific and overall survival at 120 and 300 months. These analyses reuse the test set and do not validate a new primary method. The one-sided lower bound answers a different question from the two-sided intervals.

## Distribution-shift stress test

[Read the fixed-model case-mix stress test](distribution-shift.md), including coverage bounds,
interval width, and effective sample size under age and PAM50 reweighting. This uses
the original held-out patients and is not an external validation cohort.
