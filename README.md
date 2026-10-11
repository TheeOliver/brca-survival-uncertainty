# brca-survival-uncertainty

Trustworthy prognostic modelling for breast cancer using Bayesian survival analysis and
conformal prediction, on the METABRIC cohort.

Three models (Cox proportional hazards, Bayesian Weibull AFT, Random Survival Forest) are
compared across two feature sets (clinical, clinical + PAM50) on a fixed
train / calibration / test split, then wrapped in split conformal prediction to test whether
the declared 80% / 90% / 95% intervals achieve their stated coverage.

```bash
make setup    # uv sync
sbatch scripts/slurm/run_stage.sh check # lint + fast tests on a compute node
make help     # all targets
```

Start with the [experimental design](docs/experimental-design.md) and
[pipeline runbook](docs/pipeline-runbook.md) for the study design and execution steps.

The implemented analysis uses public cBioPortal clinical tables; controlled expression data
are not required. No patient data are redistributed in Git. See the
[registered decisions](docs/analysis-decisions.md). Generated results, figures and posterior
draws stay in the ignored `outputs/` directory, with source and artifact hashes in run manifests.

Selected aggregate reports and figures are available in [Results](docs/results/README.md).
