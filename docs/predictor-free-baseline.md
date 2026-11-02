# Predictor-free Kaplan-Meier baseline

This post hoc comparison addresses whether patient-specific prediction intervals
are materially narrower than an interval method that uses no patient features.
It reuses the already-opened METABRIC test set and is exploratory, not an
independent validation.

## Procedure

For each miscoverage level $\\alpha$ and horizon $\\tau$, fit the disease-specific
Kaplan-Meier distribution on the training outcomes alone. Its equal-tailed
$\\alpha/2$ and $1-\\alpha/2$ quantiles define one restricted-time interval for
every patient. The target is $Z=\\min(T,\\tau)$, so any estimated probability
remaining beyond $\\tau$ is assigned to $Z=\\tau$. Estimating this marginal
Kaplan-Meier distribution assumes non-informative censoring for the disease-specific
endpoint. It represents net disease-specific survival under that assumption, not
the cumulative incidence of cancer death in the presence of competing risks.

Calibrate that common initial interval on the existing calibration split using the
same conservative score envelope, alpha, horizon and primary DSS event strata as
the individual-model analysis. The conformal calibration score can correct a
poorly centered initial interval under exchangeability; it does not make the
Kaplan-Meier distribution itself an individualized model.

Compare it on the frozen test set with all six existing conservative DSS model
arms (Cox, Bayesian Weibull and random survival forest, each with clinical and
clinical-plus-PAM50 features). Also report the trivial $[0,\\tau]$ interval.
Coverage bounds treat censored outcomes as sets of compatible target values.
IPCW estimates are shown only when training-based censoring support is adequate
and depend on the independent-censoring assumption. These quantities are not
interchangeable.

The primary comparison is 90% nominal coverage at 120 months. Other registered
coverage levels and the 300-month horizon are supplementary. Report median width,
interquartile range, fraction with full support $[0,\\tau]$, and fraction whose
width is at least 90% of the horizon. Paired bootstrap differences use identical
test-patient resamples and are conditional on the fitted models, calibration
states and training censoring estimate.

## Run and outputs

The test set is read only by stage 05, after a separate hash-bound exploratory
plan has been written. Run with:

    sbatch scripts/slurm/run_stage.sh 05 config/default.yaml \\
      --allow-dirty --predictor-free-baseline \\
      --baseline-config config/predictor_free_baseline.yaml

The dirty-tree override is recorded in the stage manifest and a source archive
is created. The analysis writes aggregate results and compact thesis exports under
outputs/predictor_free_baseline/; it does not write patient-level output.
