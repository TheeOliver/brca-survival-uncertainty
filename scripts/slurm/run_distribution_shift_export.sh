#!/bin/bash
# Render the distribution-shift figure from the completed aggregate run.
#SBATCH --job-name=brca-shift-export
#SBATCH --partition=openlab-queue
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --output=logs/slurm-%j.out

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$PWD}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
uv run python scripts/export_distribution_shift.py --allow-dirty "$@"
