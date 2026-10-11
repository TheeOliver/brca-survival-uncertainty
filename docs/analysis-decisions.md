# Primary analysis decisions — 2026-09-29

I chose breast-cancer-specific survival (DSS) as the primary endpoint and overall survival
(OS) as a sensitivity analysis. I fixed the primary cohort, split, predictors, models,
evaluation metrics, and conformal horizons before inspecting the held-out test results.
Both endpoints and predictor sets use the same DSS-event-stratified split: 989 training,
495 calibration, and 495 test patients.

## Cohort and predictors

I use the public cBioPortal clinical extract. Of 2,509 patients, 528 lack the required
survival follow-up and subtype information. I exclude one further patient without a
usable cause-of-death classification and one with nonpositive follow-up, leaving 1,979
eligible patients. These are sequential exclusions.

I retain patients with partially missing predictors. Numeric variables use training-fitted
median imputation and scaling, with missingness indicators; categorical variables have an
explicit unknown level. This keeps preprocessing independent of calibration and test data.
It is a prediction strategy, not an assumption that missingness is random or a substitute
for multiple-imputation inference about coefficients. See the
[prediction-time missingness study](https://pmc.ncbi.nlm.nih.gov/articles/PMC7586995/).

I retain the supplied claudin-low label as its own category and map NC or missing subtype
to unknown. I do not interpret claudin-low as a sixth intrinsic PAM50 subtype; its
relationship to those subtypes is discussed by
[Fougner et al.](https://www.nature.com/articles/s41467-020-15574-5).

## Follow-up and the prediction target

I retain full recorded follow-up for fitting. Thirteen eligible patients have follow-up
beyond 300 months, including two DSS events and five OS events, so blanket truncation
would discard information. Late recurrence in METABRIC is discussed by
[Rueda et al.](https://www.nature.com/articles/s41586-019-1007-8).

For predictive metrics, I use a training-derived interior time grid capped at 120 months;
this does not change the fitting labels. The primary conformal target is restricted event
time `min(T, 300 months)`, with a prespecified 120-month sensitivity analysis. Coverage
of restricted time is not coverage of unrestricted event time.

For DSS, I treat death from other causes as censoring. The resulting survival function
describes net cause-specific survival under censoring assumptions, not crude cumulative
breast-cancer mortality in the presence of competing deaths. Marginal reverse-Kaplan–Meier
IPCW estimates additionally require censoring to be independent of the event time and
relevant predictors. I report observable coverage bounds separately and suppress IPCW
estimates when training censoring support is insufficient.

## Models and comparisons

I compare Cox proportional hazards (PH), Bayesian Weibull accelerated failure time (AFT),
and an untuned Random Survival Forest across clinical and clinical-plus-PAM50 predictors.
This gives 12 primary fits across DSS and OS. Bayesian lognormal and wider-prior Weibull
fits are training-only sensitivity analyses; I did not choose a likelihood or prior using
calibration or test performance.

I use Uno's C for the primary discrimination comparison, with Brier score, integrated
Brier score, interval coverage, and width reported alongside it. Test-patient bootstrap
intervals condition on the fixed models and calibration; they do not include refitting
or split-selection uncertainty.

Training diagnostics found global PH departures in all four Cox fits. I retain them as
prognostic benchmarks and report the assumption limitation. Weibull AFT also implies PH;
its AFT name does not remove that restriction. Unrestricted net-DSS predictive tails can
extend beyond plausible lifetimes because of parametric extrapolation. I do not interpret
those tails as literal individual forecasts.

The later [Qin comparator](qin-exploratory.md) and
[uncertainty-reliability experiment](uncertainty-reliability.md) reuse the opened test set.
I report them as post hoc analyses, not as grounds for replacing the primary method.

## Reproducibility

Compute runs use SLURM. Early runs that explicitly allowed uncommitted sources recorded
content-addressed source and configuration archives, Git state, dependency versions,
input and artifact hashes, and job IDs. These records make the published analysis
traceable, but they do not establish a clean-commit numerical reproduction. That separate
sign-off remains pending.
