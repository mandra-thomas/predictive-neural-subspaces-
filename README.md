# Predictive neural subspaces

Does the prediction horizon of an objective determine what a neural population subspace encodes?

This project fits lagged reduced-rank ridge regression on IBL Brain-Wide Map recordings, at lags of 0.5, 2, 8 and 30 s. It then compares the resulting subspaces' geometry, and what can be decoded from each: the Bayes-optimal block prior, stimulus side, choice, feedback, wheel speed and elapsed time.

`AMENDMENTS.md` lists every pre-registered departure from the proposal. `ANALYSIS_LOG.md` records every run.

## Setup

```bash
conda env create -f environment.yml && conda activate pns
git clone https://github.com/int-brain-lab/paper-brain-wide-map && pip install -e paper-brain-wide-map
pip install -e .
pytest -q                      # unit tests + synthetic end-to-end controls (about 2 min)
```

## Pipeline

Each script caches its outputs per session and skips sessions that are already done. Pass `--force` to recompute.

| Step | What it does |
|---|---|
| `scripts/01_census.py` | Picks the region, freezes the session list and checkpoint subset into `data/meta/frozen.json`. Run once only. |
| `scripts/02_preprocess.py` | Downloads data; bins it; computes trial windows, wheel speed and the prior. Writes to `data/interim/`. |
| `scripts/03_prior_gate.py` | Full-population prior decoding against the pseudo-session null. Gives GO/NO-GO. |
| `scripts/04_fit_subspaces.py` | Subspaces, estimator check and geometry. Use `--d 3` / `--d 10` for sensitivity runs. |
| `scripts/05_decode.py` | Content decoding plus the paired pseudo-session null. |
| `scripts/06_stats.py` | Primary and secondary tests. Writes to `results/stats/d{d}/`. |
| `scripts/07_figures.py` | Builds the figures in `figures/`. |

To run on the 10-session checkpoint first, add `--subset checkpoint` to scripts 02–06. A single session can be run with `--eids <eid>`.

### Smoke test without IBL data

```bash
export PNS_DATA=/tmp/pns_syn/data PNS_RESULTS=/tmp/pns_syn/results PNS_FIGURES=/tmp/pns_syn/fig
python scripts/make_synthetic_dataset.py --n-sessions 8
python scripts/03_prior_gate.py --n-pseudo 20 && python scripts/04_fit_subspaces.py
python scripts/05_decode.py --n-pseudo 50 && python scripts/06_stats.py && python scripts/07_figures.py
```

On the laptop this takes about 3 minutes. A real run (15–20 sessions, 200 pseudo-sessions) is expected to take under an hour once the data is downloaded. `slurm/run_array.sbatch` runs any step as a PACE ICE job array.

## Layout

| Path | Contents |
|---|---|
| `src/pns/` | Library modules: `prior`, `binning`, `transform`, `lagged`, `rrr`, `geometry`, `decode`, `stats`, `pipeline`, `analysis`, `synth`, `plotting`, `io_ibl` (the only IBL-importing module), `runner`, `config` |
| `config.yaml` | Frozen constants. Change them only through a logged amendment. |
| `tests/` | Unit tests and synthetic positive and negative controls. `tests/reference/` holds the original `optimal_Bayesian` (MIT licence, IBL) for comparison. |
