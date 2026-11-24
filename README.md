# Predictive neural subspaces

Does the prediction horizon of an objective determine what a neural population subspace encodes?

This project (CSE 8803, Georgia Tech, Fall 2026) fits lagged reduced-rank ridge regression to IBL Brain-Wide Map
recordings from mouse secondary motor cortex (MOs; 16 sessions from 13 mice) at lags of 0.5, 2, 8 and 30 s. It then
compares the resulting subspaces' geometry and what can be decoded from each: the Bayes-optimal block prior, stimulus
side, choice, feedback, wheel speed and elapsed time. The short answer is that the block prior shows no detectable rise
with horizon, and every low-dimensional summary, long-horizon or not, is dominated by a slow "session-time mode".

## Where to find what

| File or folder | Contents |
|---|---|
| `RESULTS.md` | Every reported number, with its source file, the averaging used, and the interpretation |
| `AMENDMENTS.md` | The dated pre-registration record: deviations from the proposal (D1 to D10), additions (A1 to A16) and the post hoc robustness check (P1h). An index at the top gives each entry's date and status |
| `ANALYSIS_LOG.md` | Append-only log; every script run adds a row |
| `report/` | Final report (`main.tex`, `main.pdf`) |
| `slides/` | Final presentation (`slides.tex`, `slides.pdf`, `slides_notes.pdf`) |
| `reports/`, `research_notes/` | Literature review on slow neural modes |

Three labels are used throughout. **Pre-registered** means written in a timestamped commit before the relevant data
were analysed; it applies to the primary tests, the deviations, and additions A1 to A12. **Prospectively documented
exploratory** applies to A13 to A15: each design and reading rule was committed before its data were analysed, but
after the 20 November analysis freeze. **Post hoc** applies to D10 (a bug fix), P1h, the two A14 post hoc checks, A16
and A17, which were designed after the relevant results were seen.

## Setup

```bash
conda env create -f environment.yml && conda activate pns
git clone https://github.com/int-brain-lab/paper-brain-wide-map && pip install -e paper-brain-wide-map
pip install -e .
pytest -q                      # unit tests + synthetic end-to-end controls (about 2 min)
```

One-time IBL login with your own account (https://openalyx.internationalbrainlab.org/signup). Run this in your own
terminal; the password is typed at a prompt and only a token is cached in `~/.one`:

```bash
python -c "import one.params as p; p.setup('https://openalyx.internationalbrainlab.org', silent=True, username='YOUR_USERNAME')"
python -c "from one.api import ONE; ONE(base_url='https://openalyx.internationalbrainlab.org', silent=False)"
```

Scripts 01, 02, 09 and 12 download from the IBL servers. Script 17 goes through ONE but reads only files already in
the local ONE cache. Everything else reads the project's own cached files.

## Pipeline

All scripts run from the repository root. The numbered pipeline scripts (01 to 08, plus 09, 11, 12, 14, 16, 18 and
22) share a command line from `src/pns/runner.py`: `--eids` (explicit sessions), `--subset checkpoint|all`, `--force`
(recompute cached per-session outputs), `--n-jobs`, `--config`, and `--residual` (the A11 trial-locked residual
analysis, which must write to a separate results root). Scripts that fit or decode also take `--d` (the subspace
dimension; default 5 from `config.yaml`). Paths come from `config.yaml` and can be overridden with the environment
variables `PNS_DATA`, `PNS_RESULTS`, `PNS_FIGURES` and `PNS_ONE_CACHE`; this is how every derived data copy below is
refit with the unchanged pipeline.

### Main analysis (pre-registered)

| Script | What it does | Writes |
|---|---|---|
| `01_census.py` | Applies the frozen region rule and freezes the session list and 10-session checkpoint subset. Run once only | `data/meta/frozen.json`, `census.csv`, `region_counts.csv` |
| `02_preprocess.py` | Downloads and bins each session (0.5 s bins over the task epoch), computes trial windows, wheel speed and the Bayes-optimal prior | `data/interim/` |
| `03_prior_gate.py` | Go/no-go gate: Findling-style prior decoding (Lasso, nested interleaved CV) from the full population against 200 pseudo-sessions | `results/gate/` |
| `04_fit_subspaces.py` | Lagged RRR subspaces (full session and halves), the estimator check and the geometry tables | `results/{subspaces,estimator,geometry}/` |
| `05_decode.py` | Decodes every variable from every subspace, with the shared pseudo-session null | `results/{decoding,null}/` |
| `06_stats.py` | Primary tests P1 to P3 and the secondary analyses | `results/stats/d{d}/` |
| `07_figures.py` | The proposal's three figures plus the nesting figure | `figures/` |
| `08_robustness.py` | Post hoc (P1h): leave-one-mouse-out and flagged-session checks of the primary tests | `results/robustness/d{d}.csv` |

The pre-registered sensitivity runs are `--d 3` and `--d 10` for scripts 04 to 08, and the trial-locked residual
rerun (A11):

```bash
PNS_RESULTS=results_residual PNS_FIGURES=figures/residual python scripts/04_fit_subspaces.py --residual
PNS_RESULTS=results_residual PNS_FIGURES=figures/residual python scripts/05_decode.py --residual
PNS_RESULTS=results_residual PNS_FIGURES=figures/residual python scripts/06_stats.py
PNS_RESULTS=results_residual PNS_FIGURES=figures/residual python scripts/07_figures.py
PNS_RESULTS=results_residual python scripts/08_robustness.py
```

Pre-fix outputs from before the D10 bug fix are kept in `results/prefix_D10/` and `results_residual/prefix_D10/`.

### What is the slow mode? Exploratory follow-ups (scripts 09 to 18) and post hoc checks (21, 22)

Each follow-up builds a modified copy of the data, refits scripts 04 to 06 on it unchanged, and then runs an analysis
script that applies the reading rule written in `AMENDMENTS.md`.

| Script | Amendment and status | What it does |
|---|---|---|
| `09_fetch_state_signals.py` | A12, pre-registered | Local (needs the IBL login): downloads IBL probe-motion estimates and pupil diameter to `data/interim/state/` |
| `10_stable_units.py` | A12, pre-registered | Builds `data_stable/`: only units at or above 0.1 Hz in every fifth of the session |
| `11_pilot_state.py` | A12, pre-registered | Slow mode against probe motion and pupil (session-permutation null), plus the stable-unit reading. Writes `results/pilot/` |
| `12_fetch_A13.py` | A13, prospectively documented exploratory | Local: extracts all detected spikes in the MOs depth span and per-unit spike amplitudes to `data/interim/a13/`, and downloads the IBL engagement table to `data/external/engage/` |
| `13_build_A13.py` | A13, prospectively documented exploratory | Builds `data_mua/` (sorting-free multi-unit activity in 50 µm depth channels) and `data_ampstable/` (units stable in rate and amplitude); writes per-unit amplitude trends to `results/a13/` |
| `14_pilot_A13.py` | A13, prospectively documented exploratory | Engagement and satiety beyond a quadratic trend, amplitude-loading test, rigid-shift test, multi-unit comparison. Writes `results/a13/` |
| `15_build_A14.py` | A14, prospectively documented exploratory (one copy post hoc) | Per-unit amplitude-rate coupling and three amplitude-corrected copies: `data_ampcorr_low/` (conservative), `data_ampcorr_high/` (maximal), `data_ampcorr_slow/` (post hoc slow-maximal) |
| `16_pilot_A14.py` | A14, prospectively documented exploratory | Coupling tests (including the post hoc isolated-spike check), corrected-refit readings, early-concentration test. Writes `results/a14/` |
| `17_build_region2.py` | A15, prospectively documented exploratory | Builds `data_region2/`: per session, the non-MOs area with the most good units on the same probes, from cached spikes |
| `18_pilot_A15.py` | A15, prospectively documented exploratory | Applies the A15 criteria to the second-area refit; cross-area slow-mode sharing and behaviour tests. Writes `results/a15/` |
| `21_build_detrend.py` | A16, post hoc | Builds `data_detrend_q/` (quadratic detrend) and `data_detrend_c/` (cosine detrend, periods of at least 20 min) |
| `22_pilot_A16.py` | A16, post hoc | Detrend-and-refit reading, same-scale prior reference, split-half reproducibility of the leading 30 s direction, step sessions. Writes `results/a16/` |

### Figures (scripts 19 and 20)

| Script | What it does |
|---|---|
| `19_talk_figures.py` | `figures/fig4_slowmode_controls` (elapsed-time decoding under each recording control) and `figures/fig5_slowmode_examples` (slow-mode time courses in six sessions chosen by a fixed rule). Reads results only |
| `20_slide_figures.py` | Slide-sized `figures/slide_fig5.pdf` (all 16 sessions) and `figures/slide_figS1.pdf` (nesting and complements). Reads results only |
| `make_synthetic_dataset.py` | Writes a synthetic frozen dataset so scripts 03 to 07 can be smoke-tested without IBL data |

## Derived data and results folders

The `data_*` folders are gitignored and are regenerated by the scripts shown. The `results*` folders are committed (all files are small) and can also be regenerated. Each `data_*` folder has the same layout as
`data/` (`interim/` and `meta/frozen.json`), so scripts 04 to 06 run on it unchanged with `PNS_DATA=data_X
PNS_RESULTS=results_X`. Region 2 also runs script 03.

| Data folder | Built by | Results folder | Read by |
|---|---|---|---|
| `data/interim/`, `data/meta/` | 01, 02 | `results/` | all |
| (same data, `--residual`) | 04 and 05 with `--residual` | `results_residual/` | report, RESULTS |
| `data_stable/` | 10 (A12) | `results_stable/` | 11 |
| `data_mua/` | 13 (A13) | `results_mua/` | 14 |
| `data_ampstable/` | 13 (A13) | `results_ampstable/` | 14 |
| `data_ampcorr_low/`, `data_ampcorr_high/`, `data_ampcorr_slow/` | 15 (A14) | `results_ampcorr_low/`, `results_ampcorr_high/`, `results_ampcorr_slow/` | 16 |
| `data_region2/` | 17 (A15) | `results_region2/` | 18 |
| `data_detrend_q/`, `data_detrend_c/` | 21 (A16) | `results_detrend_q/`, `results_detrend_c/` | 22 |

Pilot summaries are written into the main results root: `results/pilot/` (A12), `results/a13/`, `results/a14/`,
`results/a15/` and `results/a16/`. Runs on a copied data folder log into `results_X/ANALYSIS_LOG.md` (marked
`[results: results_X]`), and those rows were merged into the root log afterwards.

## Running on PACE ICE

`slurm/` holds the Slurm batch files used on the Georgia Tech PACE ICE cluster (partition `coc-cpu`). The pilot jobs
build a pinned Python virtual environment in `~/scratch/venvs/pns` on first use, run the tests, then run the whole
pilot. Downloads that need the IBL login (scripts 09 and 12) run locally first, and only derived arrays are synced.

| File | What it runs |
|---|---|
| `slurm/run_array.sbatch` | Any per-session step as a job array, one session per task: `sbatch --array=0-15 slurm/run_array.sbatch scripts/05_decode.py` with `eids.txt` holding one session id per line |
| `slurm/pilot_A12.sbatch` | Script 10, then 04 to 06 on `data_stable/`, then 11 |
| `slurm/pilot_A13.sbatch` | Script 13, then 04 to 06 on `data_mua/` and `data_ampstable/`, then 14 |
| `slurm/pilot_A14.sbatch` | Script 15, then 04 to 06 on the three `data_ampcorr_*` copies, then 16 |

A15 and A16 ran locally. For example, A16 is:

```bash
python scripts/21_build_detrend.py
for v in detrend_q detrend_c; do
  PNS_DATA=data_$v PNS_RESULTS=results_$v python scripts/04_fit_subspaces.py --d 5
  PNS_DATA=data_$v PNS_RESULTS=results_$v python scripts/05_decode.py --d 5
  PNS_DATA=data_$v PNS_RESULTS=results_$v python scripts/06_stats.py --d 5
done
python scripts/22_pilot_A16.py --d 5
```

## Rebuilding the report and slides

The report (`report/main.tex`) uses print-sized figures built from the result files, plus the slow-mode example
figure from script 19:

```bash
python scripts/19_talk_figures.py            # figures/fig5_slowmode_examples.pdf (and fig4)
(cd report && make figs)                      # copies figures/*.pdf used by the report into report/figures/
python report/scripts/make_figures.py         # report/figures/rfig_{geometry,content,controls,estimator,nesting}.pdf
(cd report && make)                           # latexmk -> report/main.pdf
```

The slides read their two image figures from `figures/` (gitignored), so build those first:

```bash
python scripts/20_slide_figures.py           # figures/slide_fig5.pdf, figures/slide_figS1.pdf
(cd slides && make)                           # slides.pdf, slides_notes.pdf, presentation_andra-thomas.pdf
```

## Smoke test without IBL data

```bash
export PNS_DATA=/tmp/pns_syn/data PNS_RESULTS=/tmp/pns_syn/results PNS_FIGURES=/tmp/pns_syn/fig
python scripts/make_synthetic_dataset.py --n-sessions 8
python scripts/03_prior_gate.py --n-pseudo 20 && python scripts/04_fit_subspaces.py
python scripts/05_decode.py --n-pseudo 50 && python scripts/06_stats.py && python scripts/07_figures.py
```

On a laptop this takes about 3 minutes.

## Layout

| Path | Contents |
|---|---|
| `src/pns/` | Library modules: `prior`, `binning`, `transform`, `lagged`, `rrr`, `geometry`, `decode`, `stats`, `pipeline`, `analysis`, `slowmode` (slow-mode definition used by A12 to A16), `ampcorr` (A14 amplitude helpers), `synth`, `plotting`, `io_ibl` (the only IBL-importing module), `runner`, `config` |
| `scripts/` | Numbered pipeline, pilot and figure scripts (above) |
| `config.yaml` | Frozen constants. Change them only through a logged amendment |
| `tests/` | Unit tests and synthetic positive and negative controls. `tests/reference/` holds the original `optimal_Bayesian` (MIT licence, IBL) for comparison |
| `slurm/` | PACE ICE batch files |
| `report/`, `slides/` | Final report and presentation |
