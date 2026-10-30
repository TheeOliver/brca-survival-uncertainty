# Reproducibility rerun — 2026-10-30

This package records a fresh real-data rerun of the thesis analysis. Model fitting,
calibration, test evaluation, and all bootstrap experiments ran on SLURM, not the login
node. The fresh primary pipeline ran from clean commit
`a5073403952c8bf3fd22f2f374a17c0fc4f10e52` with `git_dirty: false`; its stage manifests
record `reportable: true` for stage 05 and 495 test patients.

The recorded commit is not currently part of this repository's Git history. Its exact
tracked source snapshot is included as
`manifests/source_82cb2becc700bd850ca1b15bfa3c2c20d020a38baaf517d995c3a37ec7dd35fa.tar.gz`
(SHA-256 verified against the filename and manifests). To rerun the primary pipeline, use
that archive in a fresh, isolated directory, then follow the commands below. The archive
contains source/configuration files, not patient data or generated model artifacts. The
post hoc shift extension has its own source snapshot in the adjacent archive beginning
`source_91ff1357`.

For public release, machine-specific absolute run paths in logs and manifests are normalized
to the placeholder `<RUN_ROOT>`; timestamps, SLURM job IDs, source/configuration hashes,
artifact hashes, and results are retained. The original run root can be used to map those
relative artifact paths to the archived run.

## Outcome

The raw METABRIC snapshot passed all four SHA-256 checks. The rerun prepared 1,979 patients
and recreated the same 989/495/495 split. Partition fingerprints were identical to the
saved split (fingerprints are hashes, not patient identifiers).

Aggregate comparisons against the saved results found exact key, categorical, and numeric
agreement for the primary cohort, performance, paired feature-set, conformal, and research
answer files. The comparison covered 188,067 numeric values across those files, including
the cohort summary. All keys matched.

The separate Qin and uncertainty-reliability reruns also matched their saved aggregate
files exactly: 21,450 Qin numeric values and 96,216 reliability numeric values. The
independent reliability audit passed 2,530/2,530 checks and confirmed 72 lower-bound cells,
24 ridge-Qin cells, and 1,000/1,000 successful refits in each of its four ridge settings.

The thesis' METABRIC case-mix stress test was replayed from its exact archived source
snapshot (`source_sha256` beginning `91ff1357`), using the fresh core fits and reliability
artifacts. Its saved and rerun aggregate files matched across all 31,254 numeric values.
The rerun passed `make check` (228 passed, 4 deselected), then exported both shift figures.
The source archive is included because the extension is not part of the clean commit.

The only non-identical scientific summaries were from the separately refitted alternate-prior
Weibull sensitivity MCMC chains (including their diagnostic values). Both diagnostic gates
passed with zero divergences; the horizon-wise mean absolute survival differences changed by
at most 0.0015, and the maximum individual-difference summary changed by at most 0.0105. The
lognormal sensitivity summaries agreed to within 5e-9. This is consistent with Monte Carlo
variation in the sensitivity-chain draws; it does not affect the exactly matching primary
aggregate results. Its overall sensitivity conclusion is unchanged, but the rerun is not
bitwise identical.

The primary stage-06 exporter generated 378 artifacts. Comparing these with the saved export,
355 were byte-identical; the 23 differences were confined to Bayesian-sensitivity-derived
figures, tables, and the thesis-results summary, consistent with the sensitivity-chain
variation above. The central primary metric JSON files remain exactly identical.

TCGA-BRCA results are not included in this reproduction package or treated as thesis
validation results. The current thesis describes TCGA as unsuitable for validating the
original full-predictor models and leaves it for future work, consistent with the
supervisor's condition.

## Run records

| Work | SLURM job | Result |
| --- | ---: | --- |
| Full primary pipeline, stages 01–06 | 1856 | completed in 10m20s; 228 tests passed |
| Qin exploratory comparator | 1857 | completed in 4m23s; aggregates match |
| Reliability extension | 1858 | completed in 5m50s; aggregates match |
| Reliability audit and export | 1859 | completed; 2,530/2,530 audit checks passed |
| Core artifact/source integrity audit | 1860 | completed; 825 checks, `integrity_checks_passed` |
| METABRIC distribution-shift stress test | 1861 | completed in 1m16s; aggregates match; 228 tests passed |
| Distribution-shift figure export | 1862 | completed; 2 figure artifacts exported |

See `logs/` for the SLURM stdout logs, `config/` for the exact YAML and lockfile inputs,
and `manifests/` for stage provenance, source archives, and audit reports. The core audit
checks artifact/source integrity, not numerical reproduction; it accordingly leaves its
`clean_commit_reproduction` field false. The fresh clean-commit run and the direct aggregate
comparisons above provide the numerical reproduction evidence.

Configuration SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `default.yaml` | `53b7d51a54e8f0e7f5b87982c2f98f4018ee0c9d5ba3316f8e8c56cb9608ba9e` |
| `qin_exploratory.yaml` | `cbf1cdf3f19047f56789602c34935be389f61777ff50ae6b9300dd04e7fcea0b` |
| `uncertainty_reliability.yaml` | `c69793af12b73aef9bcf3b213cab51568be15308de849955197258d18f50038b` |
| `distribution_shift.yaml` | `0b148e024129d4a23bfab847370f246e01ef11288b869f146b0d43277c5de03a` |
| `uv.lock` | `b6fb5aad8598be46bb0ed025e06e3ad3e56574bef2e533e915dcd3fcfa783be8` |

## Reproduction commands

The METABRIC clinical tables are not redistributed here. Download them with the stage-00
script, then verify their bytes against `metabric-checksums.sha256` (run the checksum command
from the `data/raw/` directory). The checksum file records the exact four-file snapshot used.
If any downloaded file fails its checksum, that download is not the recorded snapshot and
cannot support an exact rerun.

From a clean temporary directory (replace the first path with the local clone containing
this package):

```bash
REPRO_PACKAGE=/path/to/brca-survival-uncertainty/docs/reproducibility/2026-10-30
mkdir -p /tmp/brca-reproduction
tar -xzf "$REPRO_PACKAGE/manifests/source_82cb2becc700bd850ca1b15bfa3c2c20d020a38baaf517d995c3a37ec7dd35fa.tar.gz" -C /tmp/brca-reproduction
cd /tmp/brca-reproduction
uv sync --frozen
uv run python scripts/00_download_data.py
(cd data/raw && sha256sum -c "$REPRO_PACKAGE/metabric-checksums.sha256")
sbatch scripts/slurm/run_pipeline.sh config/default.yaml
sbatch scripts/slurm/run_stage.sh 05 config/default.yaml --qin-exploratory
sbatch scripts/slurm/run_stage.sh 05 config/default.yaml --reliability-exploratory
```

For the distribution-shift extension, first complete the clean primary pipeline and the
reliability extension, then apply the archived source snapshot to the isolated checkout:

```bash
tar -xzf "$REPRO_PACKAGE/manifests/source_91ff1357055b398bdd46b85d2ea0ec5d299934541c6b7ea6954b7d374b251710.tar.gz" -C .
sbatch scripts/slurm/run_distribution_shift.sh --config config/default.yaml --shift-config config/distribution_shift.yaml
sbatch scripts/slurm/run_distribution_shift_export.sh --config config/default.yaml
```

Run the core integrity audit after stage 06:

```bash
sbatch --partition=openlab-queue --cpus-per-task=2 --mem=4G --time=00:15:00 \
  --output=logs/audit-%j.out \
  --wrap='uv run --frozen python scripts/audit_results.py --require-exports'
```

Keep the two exploratory jobs separate from the primary pipeline outputs when reproducing
in a fresh checkout, and retain their post-hoc interpretation in the thesis.
