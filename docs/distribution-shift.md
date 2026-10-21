# Exploratory METABRIC case-mix stress test

This post hoc analysis asks how the **existing** survival prediction intervals
would behave if the original METABRIC test patients represented a different mix
of ages or PAM50 subtypes. It uses the same 495 test patients, 12 original model
fits, frozen calibration states, and later lower-bound/ridge comparators. No
model is refitted and no conformal threshold is recalibrated for the shifted
population.

The four scenarios are fixed in
[`config/distribution_shift.yaml`](../config/distribution_shift.yaml): uniform
baseline weights; younger and older age tilts using the training age mean and
standard deviation; and twice the weight for Basal subtype. Weights are
positive and normalized only when evaluating a statistic. Age tilts use a
clipped standardized age. The declared figure shows breast-cancer-specific
survival, Cox with clinical predictors and PAM50, 90% nominal coverage, and a
120-month restricted survival target. The machine-readable result contains both
outcomes, both predictor sets, three nominal levels, two horizons, and all
available interval methods.

For each scenario the output gives observable lower and upper bounds on coverage
under censoring, mean and median interval width, effective sample size, and
1,000 patient-bootstrap confidence intervals. The bootstrap resamples the same
frozen test-split strata across scenarios; uncertainty is conditional on the
original models, calibration and chosen weights. The bounds and their bootstrap
confidence intervals answer different questions. Weighted evaluation provides
no new conformal coverage guarantee, and these hypothetical populations do not
constitute external validation.

This analysis reuses the test set after the primary evaluation and must remain
exploratory. Its settings, source hashes and original artifact hashes are frozen
in `outputs/distribution_shift/plan.json` before stage 05 reopens the verified
test cache. Results and the rendered figure go to ignored `outputs/`; the
aggregate-only publication copy is in
[`docs/results/distribution_shift/`](results/distribution_shift/).

After reproducing the primary and reliability artifacts on a SLURM node, run:

```bash
mkdir -p logs
sbatch scripts/slurm/run_distribution_shift.sh
```

Once that job completes, export the figure from the aggregate JSON:

```bash
sbatch scripts/slurm/run_distribution_shift_export.sh
```

The new public repository has not yet completed an independent clean-commit
numerical reproduction of the historical METABRIC run. Exact numbers require
the recorded raw snapshot and matching frozen model/calibration artifacts.
