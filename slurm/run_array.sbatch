#!/bin/bash
# Optional: run one pipeline step on PACE ICE as a job array (one task per session).
# Usage:   sbatch --array=0-$(($(wc -l < eids.txt)-1)) slurm/run_array.sbatch scripts/05_decode.py
#   where eids.txt holds one session id per line (e.g. from data/meta/frozen.json).
# Set PNS_ONE_CACHE / PNS_DATA / PNS_RESULTS to scratch paths before submitting.
#SBATCH -J pns
#SBATCH -c 4
#SBATCH --mem=8G
#SBATCH -t 01:00:00
#SBATCH -o slurm/logs/%x_%A_%a.out

set -euo pipefail
module load anaconda3 2>/dev/null || true
conda activate pns
EID=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" eids.txt)
python "$1" --eids "$EID" --n-jobs 1 "${@:2}"
