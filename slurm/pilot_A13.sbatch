#!/bin/bash
# Amendment A13 second pilot (engagement/satiety, amplitude signature, multi-unit activity) on PACE ICE.
# Prerequisites: repo synced to $SLURM_SUBMIT_DIR with data/interim (incl. data/interim/a13 and data/external/engage from
# scripts/12_fetch_A13.py, run locally), data/meta, results/{subspaces,stats}. The job builds a pinned
# venv at ~/scratch/venvs/pns on first use (login-node builds get killed when the SSH session ends).
# Submit from the repo root:  sbatch slurm/pilot_A13.sbatch
#SBATCH --job-name=pns-a13
#SBATCH --partition=coc-cpu
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=02:00:00
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

# Build the multi-unit and amplitude-stable copies, refit the unchanged pipeline (04-06) on each
python scripts/13_build_A13.py --mua-out data_mua --amp-out data_ampstable
for v in mua ampstable; do
  PNS_DATA=data_$v PNS_RESULTS=results_$v python scripts/04_fit_subspaces.py --subset all --d 5 --n-jobs 8 --force
  PNS_DATA=data_$v PNS_RESULTS=results_$v python scripts/05_decode.py --subset all --d 5 --n-jobs 8 --force
  PNS_DATA=data_$v PNS_RESULTS=results_$v python scripts/06_stats.py --subset all --d 5
done

# Engagement / satiety, amplitude signature, multi-unit comparisons, and the pre-registered reading
python scripts/14_pilot_A13.py --d 5 --mua-data data_mua --mua-results results_mua --amp-results results_ampstable
echo "done $(date -Is)"
