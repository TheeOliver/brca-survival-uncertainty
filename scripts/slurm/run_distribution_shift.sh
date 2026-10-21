#!/bin/bash
# Evaluate fixed METABRIC models and intervals under hypothetical case-mix shifts.
#SBATCH --job-name=brca-shift
#SBATCH --partition=openlab-queue
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --output=logs/slurm-%j.out

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$PWD}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
make check
uv run python scripts/05_evaluate.py --shift-exploratory --allow-dirty "$@"
