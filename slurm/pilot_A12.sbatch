#!/bin/bash
# Amendment A12 pilot (drift vs brain state) on PACE ICE.
# Prerequisites: repo synced to $SLURM_SUBMIT_DIR with data/interim (incl. data/interim/state from
# scripts/09_fetch_state_signals.py, run locally), data/meta, results/{subspaces,stats}; env at ~/scratch/conda-envs/pns.
# Submit from the repo root:  sbatch slurm/pilot_A12.sbatch
#SBATCH --job-name=pns-a12
#SBATCH --partition=coc-cpu
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=slurm/logs/%x-%j.out

set -euo pipefail
module load anaconda3 >/dev/null 2>&1 || true
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$HOME/scratch/conda-envs/pns"
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
export MPLBACKEND=Agg
echo "host $(hostname)  commit $(git rev-parse --short HEAD 2>/dev/null || echo none)  start $(date -Is)"

# Test 1: stable-units copy, then the unchanged pipeline (scripts 04-06) on it
python scripts/10_stable_units.py --out data_stable
PNS_DATA=data_stable PNS_RESULTS=results_stable python scripts/04_fit_subspaces.py --subset all --d 5 --n-jobs 8 --force
PNS_DATA=data_stable PNS_RESULTS=results_stable python scripts/05_decode.py --subset all --d 5 --n-jobs 8 --force
PNS_DATA=data_stable PNS_RESULTS=results_stable python scripts/06_stats.py --subset all --d 5

# Tests 2 and 3 plus the pre-registered reading
python scripts/11_pilot_state.py --d 5 --stable-results results_stable
echo "done $(date -Is)"
