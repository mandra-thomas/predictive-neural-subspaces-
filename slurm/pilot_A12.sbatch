#!/bin/bash
# Amendment A12 pilot (drift vs brain state) on PACE ICE.
# Prerequisites: repo synced to $SLURM_SUBMIT_DIR with data/interim (incl. data/interim/state from
# scripts/09_fetch_state_signals.py, run locally), data/meta, results/{subspaces,stats}. The job builds a pinned
# venv at ~/scratch/venvs/pns on first use (login-node builds get killed when the SSH session ends).
# Submit from the repo root:  sbatch slurm/pilot_A12.sbatch
#SBATCH --job-name=pns-a12
#SBATCH --partition=coc-cpu
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=slurm/logs/%x-%j.out

set -euo pipefail
module load python/3.12.5
VENV="$HOME/scratch/venvs/pns"
if [ ! -x "$VENV/bin/python" ]; then
  python -m venv "$VENV"
  "$VENV/bin/pip" install -q --upgrade pip
  "$VENV/bin/pip" install -q numpy==2.5.5 scipy==1.18.1 scikit-learn==1.9.1 pandas==2.3.3 pyarrow==26.0.1 \
      matplotlib==3.11.2 joblib==1.6.0 pyyaml==6.0.3 pytest
fi
source "$VENV/bin/activate"
python -m pytest -q tests 2>&1 | tail -2
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
