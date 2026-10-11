# Experimental design

## The three-way split

I draw one DSS-event-stratified split using `config.seed` and freeze patient IDs in
`data/processed/splits.json`. `scripts/02_make_splits.py` reuses that split on compatible
reruns.

| Set | Fraction | Used for | Never used for |
| --- | --- | --- | --- |
| train | 0.50 | fitting all models, fitting all transforms | — |
| calibration | 0.25 | conformal quantiles only | any fitting or tuning |
| test | 0.25 | final evaluation, read once | anything that influences a choice |

**Why I reserve a calibration set.** Split conformal prediction needs scores from patients
the model has not seen during fitting. Training residuals can be optimistically small and
produce intervals that undercover. I use calibration only for conformal thresholds and do
not use it to select a model or revise the analysis. Any theoretical guarantee still
depends on the stated exchangeability and censoring assumptions.

### Running stage 02

The real-data preparation and split stages are implemented. Submit them through SLURM:

```bash
sbatch scripts/slurm/run_stage.sh 01
# After stage 01 completes successfully:
sbatch scripts/slurm/run_stage.sh 02
```

This writes `data/processed/splits.json` and
`outputs/manifests/02_make_splits_<UTC timestamp>.json`. For isolated development only,
`--synthetic` selects the test fixture; never replace the real-data split with a synthetic
split. Synthetic outputs are **development artefacts, never thesis results**.
`--allow-dirty` explicitly permits an uncommitted source tree; the manifest records
`git_dirty: true`, the baseline Git SHA and an immutable source/config archive.
Without that flag, a dirty tree or an unborn HEAD fails before writing anything.

`make split` expects `<paths.processed>/cohort.csv`. An explicit
`--input /path/to/cohort.csv` is also supported. Inputs always go through `load_cohort` and
schema validation. There is no automatic fallback to synthetic data. Relative paths in the
configuration are relative to the repository; relative `--input` paths are relative to the
working directory.

The split file's version-1 contract is a JSON object with `schema_version`, `seed`,
`fractions` (train/calibration/test), `stratify_by`, `cohort_sha256`, `input_kind`, and `splits`.
`splits` contains exactly `train`, `calibration` and `test`, each a sorted list of patient-ID
strings. Both feature sets read these same lists. IDs that look numeric retain leading zeros.

Partition sizes use largest-remainder rounding of the configured fractions; ties follow
train, calibration, test order. Event counts are allocated proportionally to those sizes,
subject to including both events and censored rows in each partition. Infeasible tiny cohorts
fail explicitly. Each event stratum is sorted by ID and shuffled with
`np.random.default_rng(config.seed)`, so assignments do not depend on input row order.

Compatible reruns validate and reuse the existing file **without resampling or rewriting**.
They write a fresh manifest, while the split bytes and modification time stay unchanged.
Changed seed, fractions, stratification, source kind, schema version or cohort bytes cause an
error, as does a malformed or overlapping partition. Other configuration changes retain the
split and receive a new config hash in the run manifest. The cohort checksum covers the entire
input file, so even reordering CSV rows makes an existing file incompatible; newly generated
assignments remain invariant to row order.

There is no overwrite flag. Before transitioning from the synthetic check to real data,
archive the synthetic split and its manifests, or select separate processed/output directories
in a configuration file. Changing a real split invalidates every downstream fit and calibration
and needs an explicit experiment decision.

Manifests contain the Git SHA and dirty flag, SHA256 of the config/input/split files, resolved
package versions, seed, UTC timestamp, SLURM job ID (or null), elapsed wall time, source kind,
partition sizes and whether the frozen split was reused. They contain no patient IDs.

## The experiment matrix

I fit each of three models with two predictor sets for both DSS and OS: six arms per
endpoint, 12 primary fits in total, all using the same frozen split.

| Model | Clinical | Clinical + PAM50 |
| --- | --- | --- |
| Cox PH | fit | fit |
| Bayesian Weibull AFT | fit | fit |
| Random Survival Forest | fit | fit |

I leave RSF untuned in this comparison and state that limitation when comparing it with
the other model families.

## Research questions and the artefact that answers each

| RQ | Question | Artefact |
| --- | --- | --- |
| 1 | How well do clinical characteristics predict survival? | `outputs/metrics/performance.json`, clinical arm |
| 2 | Does PAM50 improve predictive performance? | `outputs/metrics/rq2_feature_set_comparison.json` |
| 3 | How do classical / Bayesian / ML models differ? | performance table across all six cells |
| 4 | What uncertainty does the Bayesian model give? | `outputs/metrics/bayes_diagnostics_*.json`, posterior predictive intervals |
| 5 | Do conformal intervals achieve 80/90/95%? | `outputs/metrics/conformal_coverage.json` |
| 6 | Is the best-performing model also the best-calibrated? | joint table: C-index vs coverage vs width |

My central question is whether stronger discrimination also yields more useful and
trustworthy uncertainty. These properties need not coincide.

## Completed analysis (2026-09-29)

The subsequent [uncertainty reliability experiment](uncertainty-reliability.md) is a
post hoc extension on the same split: 72 conservative lower-bound settings and 24
fixed-ridge Qin settings. It has its own source-bound plan and does not redefine
the primary endpoint, horizon, models or conclusions by test-driven selection.

Realised partition counts and event rates are recorded in the stage-02 manifests.
The [published primary results](results/thesis_results.md) summarize all six research
questions, including uncertain comparisons and limitations. More detailed machine-readable
metrics remain local under `outputs/metrics/`.

## Implemented protocol

I selected DSS as primary and OS as sensitivity. The prepared cohort contains 1,979
patients; the frozen split is 989/495/495. Both endpoints and feature arms use the same
DSS-event-stratified assignments. Training and downstream stages load physically separate
partition tables, whose bytes and membership are checked before use.

See `analysis-decisions.md` for missing predictors, claudin-low, follow-up and competing-risk
interpretation. There are 12 primary fits (three models × two feature arms × two endpoints)
and four DSS Bayesian sensitivity fits (alternative prior and lognormal family × two arms).
The evaluation grid and conformal target horizons are selected before test access.

Stage 05 freezes code, configuration, model and calibration hashes before loading test once.
It writes an integrity-checked local cache for interruption recovery, and stages 03/04 then
refuse refitting or recalibration. Patient-level caches remain ignored. Bootstrap resampling
preserves the primary event-stratum counts and pairs the feature arms. Results and generated
RQ answers are written under `outputs/metrics/` and `outputs/reports/`; their final verified
conclusions are recorded in the generated thesis report. Execution instructions: `pipeline-runbook.md`.
