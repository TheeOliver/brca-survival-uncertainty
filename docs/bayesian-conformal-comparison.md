# Bayesian posterior-predictive versus conformalized intervals

This post hoc exploratory analysis compares the original Bayesian Weibull
posterior-predictive intervals with those same intervals after conservative
split-conformal calibration. It reuses the fitted models, prediction caches,
calibration states and already-opened test partition. It does not refit models
or select a method using test results.

## Intervals and evaluation

The native endpoints are equal-tailed quantiles of the posterior mixture of
individual event times. They include posterior parameter uncertainty and future
event-time variation. They are not credible intervals for the survival curve.
The conformalized interval uses these exact endpoints and applies the existing
nonnegative conservative score-envelope quantile, so it can widen but cannot
narrow the native interval.

Both feature sets are included for the primary disease-specific survival
endpoint. The main row is 90% nominal coverage at 120 months. All registered
miscoverage levels and the 300-month horizon are included as supplementary
settings. For every pair, the test patients, restricted target, outcome labels
and bootstrap selections are aligned.

The report gives censoring-compatible empirical coverage bounds, IPCW coverage
where the existing support checks allow it, interval widths, and paired
conformal-minus-native differences with test-patient bootstrap intervals. The
coverage bounds are not confidence intervals for latent coverage. IPCW assumes
independent censoring and adequate support; bootstrap intervals condition on the
fitted models, calibration states and training censoring estimate. At 300
months, unsupported IPCW results remain unavailable rather than being replaced
with estimates.

All comparisons are exploratory because they reuse a test set already examined
in the primary analysis. They do not provide independent validation or an
unconditional guarantee that the calibrated intervals achieve their nominal
coverage.

## Run and exports

This stage only consumes existing model and prediction artifacts; it does not
run MCMC or refit a survival model. Submit it on SLURM:

```bash
sbatch scripts/slurm/run_stage.sh 05 config/default.yaml \
  --allow-dirty --bayesian-conformal-exploratory \
  --bayesian-conformal-config config/bayesian_conformal_comparison.yaml
```

The hash-bound plan and aggregate report are written to
`outputs/bayesian_conformal_comparison/`. Primary and supplementary LaTeX tables
are exported to `outputs/tables/bayesian_conformal_*.tex`.
