#!/bin/bash
# Amendment A14 third pilot (amplitude-rate coupling, amplitude-corrected refits, early concentration) on PACE ICE.
# Prerequisites: repo synced to $SLURM_SUBMIT_DIR with data/interim (incl. data/interim/a13 from
# scripts/12_fetch_A13.py, run locally), data/meta, results/{subspaces,stats}. The job builds a pinned
# venv at ~/scratch/venvs/pns on first use (login-node builds get killed when the SSH session ends).
# Submit from the repo root:  sbatch slurm/pilot_A14.sbatch
#SBATCH --job-name=pns-a14
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

# Coupling estimates and the amplitude-corrected copies; refit the unchanged pipeline (04-06) on each copy
python scripts/15_build_A14.py --low-out data_ampcorr_low --high-out data_ampcorr_high --slow-out data_ampcorr_slow
for v in ampcorr_low ampcorr_high ampcorr_slow; do
  PNS_DATA=data_$v PNS_RESULTS=results_$v python scripts/04_fit_subspaces.py --subset all --d 5 --n-jobs 8 --force
  PNS_DATA=data_$v PNS_RESULTS=results_$v python scripts/05_decode.py --subset all --d 5 --n-jobs 8 --force
  PNS_DATA=data_$v PNS_RESULTS=results_$v python scripts/06_stats.py --subset all --d 5
done

# Coupling tests, bracketing readings, early concentration, and the pre-registered overall reading
python scripts/16_pilot_A14.py --d 5
echo "done $(date -Is)"
