# METABRIC thesis results

This report is generated from saved aggregate JSON; it does not recompute metrics.
Primary endpoint: disease_specific. OS is a sensitivity analysis. Training n=989; test n=495. The predictive metric grid spans 28.973 to 120 months; IBS integrates over that interval, not from zero.
DSS describes net cause-specific survival under censoring assumptions, not crude breast-cancer mortality. All analyses are prognostic.

## RQ1 — Clinical predictive performance

| Model | Uno C (95% CI) | IBS (95% CI) | Mean dynamic AUC (95% CI) |
| --- | --- | --- | --- |
| cox | 0.686 [0.641, 0.730] | 0.141 [0.129, 0.153] | 0.745 [0.694, 0.793] |
| rsf | 0.690 [0.645, 0.736] | 0.140 [0.129, 0.151] | 0.752 [0.699, 0.799] |
| weibull | 0.687 [0.642, 0.732] | 0.143 [0.130, 0.155] | 0.746 [0.696, 0.792] |

Evidence: `outputs/metrics/performance.json`.

## RQ2 — Added predictive value of PAM50

Differences are clinical + PAM50 minus clinical on identical patients.

| Model | Paired Δ Uno C (95% CI) | Paired Δ IBS (95% CI) |
| --- | --- | --- |
| cox | 0.010 [-0.005, 0.026] | 0.00095 [-0.00203, 0.00486] |
| rsf | 0.014 [0.003, 0.025] | -0.00180 [-0.00319, -0.00042] |
| weibull | 0.018 [0.003, 0.032] | -0.00149 [-0.00306, 0.00004] |

cox, primary Uno C: The interval includes zero; the direction of added predictive value is uncertain.

rsf, primary Uno C: The paired interval favors clinical + PAM50; comparisons are exploratory without multiplicity adjustment.

weibull, primary Uno C: The paired interval favors clinical + PAM50; comparisons are exploratory without multiplicity adjustment.

Width and coverage changes also have paired intervals in `outputs/metrics/rq2_feature_set_comparison.json`; predictive gains alone do not establish better uncertainty.

## RQ3 — Classical, Bayesian and forest models

| Model / features | Uno C (95% CI) | IBS (95% CI) |
| --- | --- | --- |
| weibull__clinical_molecular | 0.705 [0.662, 0.747] | 0.141 [0.128, 0.154] |
| rsf__clinical_molecular | 0.705 [0.661, 0.748] | 0.138 [0.128, 0.149] |
| cox__clinical_molecular | 0.696 [0.651, 0.739] | 0.142 [0.129, 0.154] |
| rsf__clinical | 0.690 [0.645, 0.736] | 0.140 [0.129, 0.151] |
| weibull__clinical | 0.687 [0.642, 0.732] | 0.143 [0.130, 0.155] |
| cox__clinical | 0.686 [0.641, 0.730] | 0.141 [0.129, 0.153] |

The largest primary Uno C point estimate belongs to weibull__clinical_molecular. This descriptive ordering is not a test of superiority between model families. RSF was deliberately untuned.

Cox proportional-hazards score checks (training only, unadjusted):
- disease_specific__cox__clinical: global p=1.1e-08; flagged=True.
- disease_specific__cox__clinical_molecular: global p=3.27e-08; flagged=True.
- overall__cox__clinical: global p=2.11e-15; flagged=True.
- overall__cox__clinical_molecular: global p=9.09e-15; flagged=True.

Global PH departures were detected in 4 of 4 Cox fits. They remain prognostic benchmarks, with this assumption limitation explicit. Continuous coefficients are per training standard deviation, not per raw measurement unit.

A flagged PH check limits the proportional-hazards interpretation. Weibull AFT also imposes proportional hazards; adding AFT terminology does not remove that restriction.

## RQ4 — Bayesian uncertainty

Survival credible bands describe posterior uncertainty in S(t|x). Individual event-time predictive intervals additionally include variation of event times under the fitted model. Neither is a conformal coverage guarantee. Hypothetical profiles are constructed from training summaries and are not patient records.
Holding modal receptors fixed while changing subtype can create rare joint predictor combinations. A subtype's training count alone does not establish support for that hypothetical combination; these illustrations are not validated individual forecasts.
Unrestricted predictive tails can extend beyond plausible human lifetimes, especially for net DSS. Those are consequences of parametric extrapolation with no cure fraction or competing-risk distribution; they must not be read as literal clinical forecasts.

| Fit | Max R-hat | Min bulk ESS | Min tail ESS | Divergences | Max training PPC discrepancy |
| --- | --- | --- | --- | --- | --- |
| disease_specific__weibull__clinical | 1.0025 | 2693 | 2419 | 0 | 0.056 |
| disease_specific__weibull__clinical_molecular | 1.0036 | 2764 | 2539 | 0 | 0.051 |
| overall__weibull__clinical | 1.0059 | 2202 | 2331 | 0 | 0.075 |
| overall__weibull__clinical_molecular | 1.0041 | 2313 | 2415 | 0 | 0.080 |
| disease_specific__weibull__clinical__lognormal__default | 1.0037 | 1780 | 2330 | 0 | 0.030 |
| disease_specific__weibull__clinical__weibull__sensitivity | 1.0045 | 2204 | 2471 | 0 | 0.050 |
| disease_specific__weibull__clinical_molecular__lognormal__default | 1.0025 | 3049 | 2745 | 0 | 0.028 |
| disease_specific__weibull__clinical_molecular__weibull__sensitivity | 1.0027 | 1714 | 1956 | 0 | 0.047 |

Sensitivity: maximum absolute differences in fitted survival across training profiles and registered times:
- disease_specific__weibull__clinical__lognormal__default: 0.209.
- disease_specific__weibull__clinical__weibull__sensitivity: 0.073.
- disease_specific__weibull__clinical_molecular__lognormal__default: 0.220.
- disease_specific__weibull__clinical_molecular__weibull__sensitivity: 0.161.

Inspect the saved training PPC overlays: a passing MCMC gate establishes sampling adequacy, not a correct survival family. The alternative lognormal family and wider prior were checked on training patients only. Evidence: `bayes_diagnostics_*.json`, `bayesian_sensitivity.json` and the hypothetical-profile report in `outputs/metrics/`.

## RQ5 — Coverage and efficiency under censoring

Latent event times for censored patients are unknown. The observable lower/upper bounds enclose realised test coverage; they are not confidence limits for an identified coverage probability. IPCW coverage is a separate estimate requiring marginal independent censoring and adequate censoring support. The IPCW-calibrated method is an approximate sensitivity analysis with no asserted finite-sample guarantee.

The table below shows primary DSS conservative intervals for min(T, horizon), at every registered nominal level. Coverage is always paired with width.

| Model / features | Horizon (months) | Nominal | n calibration | Observable coverage bounds | IPCW coverage | Median width [IQR], months |
| --- | --- | --- | --- | --- | --- | --- |
| cox / clinical | 120 | 95% | 495 | [0.956, 0.974] | 0.972 | 100.3 [96.8, 104.8] |
| cox / clinical | 300 | 95% | 495 | [0.956, 0.974] | unavailable | 280.3 [276.6, 284.8] |
| cox / clinical | 120 | 90% | 495 | [0.929, 0.954] | 0.950 | 94.5 [89.0, 99.0] |
| cox / clinical | 300 | 90% | 495 | [0.929, 0.954] | unavailable | 274.4 [268.4, 279.0] |
| cox / clinical | 120 | 80% | 495 | [0.838, 0.905] | 0.898 | 78.4 [68.1, 87.9] |
| cox / clinical | 300 | 80% | 495 | [0.834, 0.905] | unavailable | 257.5 [246.0, 266.1] |
| cox / clinical_molecular | 120 | 95% | 495 | [0.954, 0.972] | 0.969 | 100.3 [96.1, 104.8] |
| cox / clinical_molecular | 300 | 95% | 495 | [0.952, 0.972] | unavailable | 280.0 [275.9, 284.8] |
| cox / clinical_molecular | 120 | 90% | 495 | [0.929, 0.954] | 0.950 | 94.0 [87.6, 98.8] |
| cox / clinical_molecular | 300 | 90% | 495 | [0.925, 0.952] | unavailable | 273.1 [266.8, 278.0] |
| cox / clinical_molecular | 120 | 80% | 495 | [0.828, 0.907] | 0.900 | 77.3 [65.1, 88.1] |
| cox / clinical_molecular | 300 | 80% | 495 | [0.816, 0.905] | unavailable | 256.2 [242.1, 266.8] |
| rsf / clinical | 120 | 95% | 495 | [0.966, 0.984] | 0.983 | 100.3 [92.8, 106.5] |
| rsf / clinical | 300 | 95% | 495 | [0.966, 0.984] | unavailable | 280.3 [272.8, 286.5] |
| rsf / clinical | 120 | 90% | 495 | [0.921, 0.954] | 0.951 | 90.8 [82.2, 99.0] |
| rsf / clinical | 300 | 90% | 495 | [0.921, 0.954] | unavailable | 270.8 [262.2, 279.0] |
| rsf / clinical | 120 | 80% | 495 | [0.836, 0.911] | 0.904 | 77.7 [60.7, 92.8] |
| rsf / clinical | 300 | 80% | 495 | [0.836, 0.911] | unavailable | 257.7 [240.7, 272.8] |
| rsf / clinical_molecular | 120 | 95% | 495 | [0.962, 0.982] | 0.981 | 99.5 [92.5, 105.6] |
| rsf / clinical_molecular | 300 | 95% | 495 | [0.962, 0.982] | unavailable | 279.5 [272.5, 285.6] |
| rsf / clinical_molecular | 120 | 90% | 495 | [0.915, 0.956] | 0.953 | 91.4 [82.0, 99.0] |
| rsf / clinical_molecular | 300 | 90% | 495 | [0.915, 0.956] | unavailable | 271.4 [262.0, 279.0] |
| rsf / clinical_molecular | 120 | 80% | 495 | [0.824, 0.909] | 0.902 | 77.0 [51.8, 90.3] |
| rsf / clinical_molecular | 300 | 80% | 495 | [0.824, 0.909] | unavailable | 257.0 [231.8, 270.3] |
| weibull / clinical | 120 | 95% | 495 | [0.982, 0.994] | 0.993 | 106.5 [102.0, 110.1] |
| weibull / clinical | 300 | 95% | 495 | [0.982, 0.994] | unavailable | 286.5 [281.6, 290.0] |
| weibull / clinical | 120 | 90% | 495 | [0.935, 0.962] | 0.959 | 94.5 [85.9, 101.3] |
| weibull / clinical | 300 | 90% | 495 | [0.935, 0.962] | unavailable | 274.3 [265.1, 280.8] |
| weibull / clinical | 120 | 80% | 495 | [0.824, 0.901] | 0.893 | 74.4 [58.0, 87.4] |
| weibull / clinical | 300 | 80% | 495 | [0.820, 0.901] | unavailable | 253.7 [236.0, 266.0] |
| weibull / clinical_molecular | 120 | 95% | 495 | [0.978, 0.994] | 0.993 | 107.0 [101.8, 110.6] |
| weibull / clinical_molecular | 300 | 95% | 495 | [0.978, 0.994] | unavailable | 286.6 [281.4, 290.4] |
| weibull / clinical_molecular | 120 | 90% | 495 | [0.945, 0.968] | 0.965 | 95.1 [85.3, 102.0] |
| weibull / clinical_molecular | 300 | 90% | 495 | [0.945, 0.968] | unavailable | 274.3 [264.3, 281.5] |
| weibull / clinical_molecular | 120 | 80% | 495 | [0.822, 0.897] | 0.888 | 73.1 [54.1, 86.4] |
| weibull / clinical_molecular | 300 | 80% | 495 | [0.816, 0.897] | unavailable | 251.3 [231.8, 264.9] |

At 300 months, estimated training censoring survival is 0.01478, below the registered support threshold 0.05. IPCW coverage is unavailable there. The IPCW-calibration sensitivity falls back to the entire restricted support, which is uninformative; it is not evidence of a useful calibrated interval. The 120-month analysis was prespecified.

Uncertainty intervals for each coverage bound, IPCW estimate and width statistic, plus PAM50/ER subgroup estimates, are in `conformal_coverage.json` and the exported tables. Groups smaller than the configured minimum are suppressed. Small remaining groups can still have wide uncertainty intervals. No subgroup coverage guarantee is inferred from marginal calibration.

## RQ6 — Does the strongest discriminator give the most useful uncertainty?

Compare the largest Uno C point estimate (weibull__clinical_molecular) with all interval widths above. A width close to the whole restricted support represents weak individual information even when coverage bounds are favorable. When bounds span nominal coverage or IPCW is unavailable, the data do not identify a uniquely best-calibrated model. Discrimination rankings therefore cannot by themselves establish which model has the most trustworthy uncertainty.

## Overall-survival sensitivity

| Model / features | Uno C (95% CI) | IBS (95% CI) |
| --- | --- | --- |
| cox__clinical | 0.649 [0.612, 0.687] | 0.170 [0.155, 0.184] |
| cox__clinical_molecular | 0.652 [0.616, 0.689] | 0.171 [0.157, 0.185] |
| rsf__clinical | 0.668 [0.634, 0.700] | 0.162 [0.151, 0.175] |
| rsf__clinical_molecular | 0.678 [0.643, 0.709] | 0.160 [0.149, 0.173] |
| weibull__clinical | 0.649 [0.611, 0.686] | 0.170 [0.156, 0.184] |
| weibull__clinical_molecular | 0.653 [0.616, 0.690] | 0.170 [0.156, 0.184] |

## Limits of inference

One internal split, no external validation; historical treatment practice; missing-predictor imputation assumptions; possible dependent censoring and competing deaths; parametric family and PH misspecification; limited tail support; exploratory multiplicity. Test-patient bootstrap holds primary event-stratum counts fixed and conditions on fitted models, training censoring estimates and calibration. It omits model-fitting and split-selection variability. CIs with undefined replicates omitted are explicitly conditional and approximate; failed gates leave CIs unavailable. Full follow-up used for fitting must not be confused with restricted evaluation.

Source/config archives, exact hashes and SLURM jobs are recorded in `outputs/manifests/`.

## RQ6 joint comparison at the primary restricted horizon

| Model / features | Uno C (95% CI) | Nominal | Observable coverage bounds | Median width [95% CI], months | Full-support fraction |
| --- | --- | --- | --- | --- | --- |
| cox__clinical | 0.686 [0.641, 0.730] | 95% | [0.956, 0.974] | 280.3 [280.0, 280.6] | 0.0% |
| cox__clinical | 0.686 [0.641, 0.730] | 90% | [0.929, 0.954] | 274.4 [273.4, 274.9] | 0.0% |
| cox__clinical | 0.686 [0.641, 0.730] | 80% | [0.834, 0.905] | 257.5 [256.2, 259.1] | 0.0% |
| cox__clinical_molecular | 0.696 [0.651, 0.739] | 95% | [0.952, 0.972] | 280.0 [279.6, 280.3] | 0.0% |
| cox__clinical_molecular | 0.696 [0.651, 0.739] | 90% | [0.925, 0.952] | 273.1 [272.7, 274.0] | 0.0% |
| cox__clinical_molecular | 0.696 [0.651, 0.739] | 80% | [0.816, 0.905] | 256.2 [255.0, 257.4] | 0.0% |
| rsf__clinical | 0.690 [0.645, 0.736] | 95% | [0.966, 0.984] | 280.3 [277.9, 281.3] | 0.0% |
| rsf__clinical | 0.690 [0.645, 0.736] | 90% | [0.921, 0.954] | 270.8 [269.7, 272.1] | 0.0% |
| rsf__clinical | 0.690 [0.645, 0.736] | 80% | [0.836, 0.911] | 257.7 [255.4, 259.5] | 0.0% |
| rsf__clinical_molecular | 0.705 [0.661, 0.748] | 95% | [0.962, 0.982] | 279.5 [278.4, 280.6] | 0.0% |
| rsf__clinical_molecular | 0.705 [0.661, 0.748] | 90% | [0.915, 0.956] | 271.4 [270.3, 272.5] | 0.0% |
| rsf__clinical_molecular | 0.705 [0.661, 0.748] | 80% | [0.824, 0.909] | 257.0 [254.3, 261.2] | 0.0% |
| weibull__clinical | 0.687 [0.642, 0.732] | 95% | [0.982, 0.994] | 286.5 [285.7, 286.8] | 0.0% |
| weibull__clinical | 0.687 [0.642, 0.732] | 90% | [0.935, 0.962] | 274.3 [272.4, 274.6] | 0.0% |
| weibull__clinical | 0.687 [0.642, 0.732] | 80% | [0.820, 0.901] | 253.7 [250.0, 254.6] | 0.0% |
| weibull__clinical_molecular | 0.705 [0.662, 0.747] | 95% | [0.978, 0.994] | 286.6 [285.8, 287.1] | 0.0% |
| weibull__clinical_molecular | 0.705 [0.662, 0.747] | 90% | [0.945, 0.968] | 274.3 [272.7, 275.4] | 0.0% |
| weibull__clinical_molecular | 0.705 [0.662, 0.747] | 80% | [0.816, 0.897] | 251.3 [248.1, 253.5] | 0.0% |

## Subgroup signals requiring caution

Below are primary-horizon subgroup cells whose observable upper coverage bound is below nominal on this test sample. Their bootstrap intervals concern the observable upper bound; intervals including nominal do not establish population undercoverage. These exploratory comparisons are not multiplicity-adjusted.

| Model / features | Group | n | Nominal | Observable bounds | Upper-bound 95% CI | Median width, months |
| --- | --- | --- | --- | --- | --- | --- |
| cox / clinical | pam50_subtype: Basal | 59 | 95% | [0.932, 0.949] | [0.898, 1.000] | 284.8 |
| cox / clinical | pam50_subtype: Her2 | 54 | 95% | [0.907, 0.926] | [0.852, 0.981] | 284.8 |
| cox / clinical | pam50_subtype: Basal | 59 | 90% | [0.831, 0.847] | [0.763, 0.932] | 279.9 |
| cox / clinical | pam50_subtype: Basal | 59 | 80% | [0.780, 0.797] | [0.712, 0.881] | 267.9 |
| cox / clinical_molecular | pam50_subtype: Basal | 59 | 95% | [0.932, 0.949] | [0.898, 1.000] | 284.9 |
| cox / clinical_molecular | pam50_subtype: Her2 | 54 | 95% | [0.907, 0.926] | [0.852, 0.981] | 284.8 |
| cox / clinical_molecular | pam50_subtype: Basal | 59 | 90% | [0.831, 0.847] | [0.763, 0.932] | 280.3 |
| cox / clinical_molecular | pam50_subtype: Basal | 59 | 80% | [0.763, 0.797] | [0.712, 0.881] | 269.4 |
| rsf / clinical | pam50_subtype: Her2 | 54 | 95% | [0.907, 0.926] | [0.852, 0.981] | 284.7 |
| rsf / clinical | pam50_subtype: Basal | 59 | 90% | [0.847, 0.864] | [0.780, 0.932] | 283.3 |
| rsf / clinical_molecular | pam50_subtype: Her2 | 54 | 95% | [0.907, 0.926] | [0.852, 0.981] | 283.8 |
| weibull / clinical | pam50_subtype: Basal | 59 | 90% | [0.881, 0.898] | [0.831, 0.966] | 282.0 |
| weibull / clinical | pam50_subtype: Basal | 59 | 80% | [0.780, 0.797] | [0.712, 0.881] | 266.6 |
