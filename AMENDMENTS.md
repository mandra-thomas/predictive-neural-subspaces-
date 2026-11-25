# Amendments to the proposal (pre-registered)

## Index (added 2026-11-22; navigation only, no entry below was changed)

The table lists every entry in this file with the date and commit that first recorded it (from `git log`), its
status, the section of `RESULTS.md` that reports it, and the code that implements it. Times are US Eastern.

**Terminology.** *Pre-registered* means the entry was committed before the data it concerns were analysed; this
applies to D1 to D9, A1 to A11 (all in the first commit, before any real-data fit) and A12. *Prospectively documented
exploratory* applies to A13, A14 and A15. Their designs and reading rules were likewise committed before the relevant
data were analysed, and their headings below say "pre-registered", but they were written on 21 and 22 November, after
the 20 November analysis freeze in the proposal, so the report and `RESULTS.md` use the narrower label. *Post hoc*
means designed after the relevant results were seen: D10 (a bug fix), P1h, the two A14 post hoc additions, A16,
A17 (A17 executes extensions listed in the proposal, with post hoc specifics), A18 and A19. *AI-agent review*
means a review by Claude subagents, not by a person; no independent human review of the analysis has taken place.

| # | First recorded | Status | RESULTS.md section | Code |
|---|---|---|---|---|
| D1 | 2026-11-16 07:25 (`98a0033`) | pre-registered | Data and design | `02_preprocess.py`, `pns.pipeline` |
| D2 | 2026-11-16 07:25 (`98a0033`) | pre-registered | Data and design | `01_census.py`, `02_preprocess.py` |
| D3 | 2026-11-16 07:25 (`98a0033`) | pre-registered | Data and design | `pns.prior` |
| D4 | 2026-11-16 07:25 (`98a0033`) | pre-registered | Data and design; Secondary results (penalties) | `04_fit_subspaces.py`, `pns.rrr` |
| D5 | 2026-11-16 07:25 (`98a0033`) | pre-registered | Primary results, P3 | `05_decode.py`, `pns.pipeline` |
| D6 | 2026-11-16 07:25 (`98a0033`) | pre-registered | Primary results | `06_stats.py`, `pns.stats` |
| D7 | 2026-11-16 07:25 (`98a0033`) | pre-registered | Primary results, P1 | `06_stats.py`, `pns.analysis` |
| D8 | 2026-11-16 07:25 (`98a0033`) | pre-registered | Primary results, P1 | `04_fit_subspaces.py`, `pns.pipeline` |
| D9 | 2026-11-16 07:25 (`98a0033`) | pre-registered | Data and design | `02_preprocess.py`, `pns.pipeline` |
| A1 | 2026-11-16 07:25 (`98a0033`) | pre-registered | Data and design (prior gate) | `03_prior_gate.py` |
| A2 | 2026-11-16 07:25 (`98a0033`) | pre-registered | Primary results, P1; Secondary results (estimator check) | `04_fit_subspaces.py`, `pns.geometry` |
| A3 | 2026-11-16 07:25 (`98a0033`) | pre-registered | Primary results, P1; Secondary results (nesting) | `04_fit_subspaces.py`, `pns.geometry` |
| A4 | 2026-11-16 07:25 (`98a0033`) | pre-registered | Primary results, P2; Secondary results (other measures) | `05_decode.py`, `06_stats.py` |
| A5 | 2026-11-16 07:25 (`98a0033`) | pre-registered | Primary results, P3 | `05_decode.py`, `pns.analysis` |
| A6 | 2026-11-16 07:25 (`98a0033`) | pre-registered | How to read this file; Primary results | `05_decode.py`, `pns.analysis` |
| A7 | 2026-11-16 07:25 (`98a0033`) | pre-registered | Secondary results | `06_stats.py`, `pns.stats` |
| A8 | 2026-11-16 07:25 (`98a0033`) | pre-registered | Data and design | `pns.lagged` |
| A9 | 2026-11-16 07:25 (`98a0033`) | pre-registered | not reported separately (report appendix decoding table) | `05_decode.py`, `pns.pipeline` |
| A10 | 2026-11-16 07:25 (`98a0033`) | pre-registered | Secondary results (session-time mode) | `06_stats.py`, `pns.analysis` |
| A11 | 2026-11-16 07:25 (`98a0033`) | pre-registered (sensitivity) | Primary results; Secondary results; Robustness | `04_fit_subspaces.py` and `05_decode.py` with `--residual`, `pns.pipeline.residualize_session` |
| D10 | 2026-11-16 10:46 (`c6893b1`) | post hoc (bug fix) | What changed after the first run | `pns.transform` (`SD_FLOOR`) |
| P1h | 2026-11-16 10:46 (`c6893b1`) | post hoc | Robustness | `08_robustness.py` |
| A12 | 2026-11-17 03:02 (`e965b42`) | pre-registered, exploratory | Pilot (A12) | `09_fetch_state_signals.py`, `10_stable_units.py`, `11_pilot_state.py`, `slurm/pilot_A12.sbatch` |
| A13 | 2026-11-21 17:05 (`fd5f3d4`) | prospectively documented exploratory | Second pilot (A13) | `12_fetch_A13.py`, `13_build_A13.py`, `14_pilot_A13.py`, `slurm/pilot_A13.sbatch` |
| A14 | 2026-11-22 10:16 (`f3008e7`); post hoc additions 10:25 (`7d0172d`) | prospectively documented exploratory; two post hoc checks | Third pilot (A14) | `15_build_A14.py`, `16_pilot_A14.py`, `pns.ampcorr`, `slurm/pilot_A14.sbatch` |
| A15 | 2026-11-22 10:49 (`30d2c3f`) | prospectively documented exploratory | Fourth pilot (A15) | `17_build_region2.py`, `18_pilot_A15.py` |
| A16 | 2026-11-22 17:29 (`246fddb`); part 3 addendum 17:32 (`73ffa82`) | post hoc | Post hoc follow-ups (A16) | `21_build_detrend.py`, `22_pilot_A16.py` |
| A17 | 2026-11-23 (`0dbca28`); part 1 addendum later the same day; review note 2026-11-24 | post hoc | Timescale follow-ups (A17) | `pns.timescales`, `23_timescales_A17.py` to `25_longlag_A17.py` (part 6, `28_switch_A17.py`, never written; dropped 2026-11-25) |
| A18 part A | 2026-11-24 (`3a81ba1`), before any calibration or simulation outcome; addendum `2f7611d` after calibration, before the sweep; notes after the results | post hoc | Calibrated simulation (A18 part A) | `pns.sim_a18`, `pns.synth` task/rate/history/evoked options, `26_sim_A18.py` |
| A18 part B | 2026-11-24 (`1a233eb`), before any latent-model result; result note `371a43c` | post hoc | Calibrated simulation (A18 part B) | `pns.sim_a18.lds_readout`, `pns.lds`, `27_lds_sim_A18.py` |
| A19 | 2026-11-25 (`9cd4a62`), before any A19 number; results `97b272b` | post hoc (sensitivity, one session) | Sensitivity to one session (A19) | `28_sensitivity_A19.py` |
| Notes | 2026-11-25 | record-keeping and corrections after AI-agent reviews | (throughout) | none |

The figure scripts `19_talk_figures.py` and `20_slide_figures.py` read existing results only and implement no
amendment (the `timescales` option of script 20 plots A17 part 0 results). The entries below are the original dated record and are left exactly as written.

---

Committed on 2026-11-16, **before any real-data fit**. This file lists every departure from the proposal
("Prediction Horizon and the Content of Neural Population Subspaces", Oct 8 2026) and every addition, each
with its reason. Later changes are appended with a date and logged in `ANALYSIS_LOG.md`.

## Why amendments were needed

An adversarial review of the analysis plan (library source, literature, numerical checks) found:

1. **Nesting.** Slow modes are the most predictable signal at every lag (Pérez-Hernández et al. 2013), so
   the 0.5 s subspace is expected to contain the slow, prior-carrying mode. A simulation of the planned
   setup gave equal prior decoding at 0.5 s and 30 s. The primary test "prior rises with lag" can then be
   null even when the 30 s subspace is purely slow.
2. **λ confound.** The ridge penalty changes the readout subspace (CCA-like as it goes to 0, PLS-like as
   it grows). Choosing λ separately per lag would let λ alone make long-lag subspaces differ.
3. **Statistical power.** The exact two-sided Wilcoxon p-value cannot go below 2/2ⁿ. With fewer than
   8 animals, no contrast can survive Holm correction over 4 tests.
4. **Confounded side variables.** Current and previous stimulus side follow the block, so they carry
   prior information that the pseudo-session null does not remove.

## Deviations from the proposal

| # | Proposal | Implemented | Reason |
|---|---|---|---|
| D1 | Bins over the whole session | Bins over the task epoch (first trial start to last trial end) | Excludes passive and spontaneous periods |
| D2 | ≥ 400 trials | ≥ 400 trials **after** the BWM trial mask | Unambiguous; stricter |
| D3 | Bayes-optimal prior (Findling et al.) | Same model, numpy port, but no-go trials are **not** skipped | The prior then depends only on earlier stimuli, as the proposal states; no-go trials are rare after the mask |
| D4 | λ by cross-validation | **One CV-selected λ per session, shared by all lags**: λ = α·tr(XᵀX)/p, with α maximizing mean held-out rank-d R² across the four lags | Same procedure at every lag, without the λ confound; per-lag λ is kept as a sensitivity analysis |
| D5 | Current stimulus side decoded on all trials | On **nonzero-contrast** trials only | On zero-contrast trials the side carries only block information |
| D6 | Two-sided paired Wilcoxon | **One-sided**, in the predicted direction | The hypotheses are directional |
| D7 | Geometry: cross > same at both lags | An intersection–union test (p = max of the two); Holm over **3** primary tests | The proposal already requires both; IUT needs no extra correction |
| D8 | (unspecified) | Geometry halves use whole-session z-score parameters and the session α | Keeps both halves in the same coordinates; unsupervised, so it leaks nothing |
| D9 | (unspecified) | Units with < 0.1 Hz over the task epoch are dropped | Prevents near-zero variance blowing up z-scores |

## Additions

| # | Addition | Status |
|---|---|---|
| A1 | Findling-style full-population prior gate (Lasso, nested interleaved CV, pseudo-session null, Fisher-combined) as a go/no-go check before analyses 1–3 | gate |
| A2 | Covariance-matched random subspace baseline (Elsayed & Cunningham 2017) for the estimator check and the angle chance level | secondary |
| A3 | All d principal angles, plus an asymmetric **nesting index** (how much of one lag's leading direction lies in the other lag's subspace) | secondary (pre-registered) |
| A4 | Decoding from **orthogonal complements** (the 0.5 s subspace minus the 30 s subspace, and the reverse) and from single dimensions | secondary (pre-registered) |
| A5 | Side variables also scored as AUC gained over a prior-only model | secondary |
| A6 | Pseudo-session null shared across all lags and feature sets, so lag contrasts use a **paired-difference null**; summarized as real − null **median** (as Findling), plus percentile and z-score | primary method |
| A7 | Bootstrap CIs over animals; Fisher-combined session p-values; Spearman trend across lags | secondary |
| A8 | Purge plus a 10-bin embargo around test blocks; a 60-bin gap between halves | hygiene |
| A9 | Probe windows for choice ([−0.5, 0] s from first movement) and feedback ([0, 0.5] s from feedback) | unspecified in the proposal |
| A10 | Drift flag coded explicitly: elapsed time decoded above both the PCA and random baselines, while the prior is not significant | the proposal's rule, made explicit |
| A11 | Trial-locked residual rerun (event-locked GLM, then refit on the residuals): the **first add-on** after the 10-session checkpoint | sensitivity |

## Primary tests (frozen)

All are one-sided paired Wilcoxon tests across animals, with sessions averaged within each animal first, and Holm correction over the three:

- **P1 Geometry.** The mean principal angle across lags (0.5 s vs 30 s, fits on opposite halves) is larger than the same-lag angle at 0.5 s **and** at 30 s.
- **P2 Prior.** [R²(30 s) − R²(0.5 s)], corrected by the paired-difference null, is greater than 0.
- **P3 Current side.** [AUC(0.5 s) − AUC(30 s)], corrected by the paired-difference null on nonzero-contrast trials, is greater than 0.

**Expected-outcome note.** If there is one shared slow mode, the expected result is nesting, and P2 may be null. The secondary measures A3 and A4 distinguish "nested" from "no slow content".

## Post-registration amendments (after the first full run)

These were made after results were seen. Each is a bug fix or a clearly labelled post hoc check, and the
results from before the change are kept and reported alongside the corrected ones.

| # | When | Change | Why |
|---|---|---|---|
| D10 | 2026-11-16, after the d=3/5/10 and residual runs | z-score SD floor raised from 1e-3 to 0.218, the SD of sqrt(Poisson counts) for a unit at the 0.1 Hz inclusion rate in 0.5 s bins | **Bug.** Found while diagnosing two sessions (CSHL049, ZM_2245) with held-out R² ≈ 0 for *every* method, full-rank ridge included. A unit that is silent across a training fold but fires in the test fold got a 1e-3 SD, so its held-out z-variance reached ~10⁵ and made up > 99% of the pooled test variance. That corrupted the CV R² and, through it, the session α. Whole-session z-scoring (which defines the geometry and decoding subspaces) is unaffected, since every session's smallest whole-session SD is already ≥ 0.22. The fix changes fold-wise and half-wise z-scoring only. Pre-fix outputs are kept in `results/prefix_D10/` and `results_residual/prefix_D10/`. |
| P1h | 2026-11-16 | `scripts/08_robustness.py`: leave-one-animal-out refits of the three primary tests, and removal of flagged sessions | **Post hoc**, not pre-registered. Reported as a robustness check only. |

## A12: pilot "drift or brain state?" (pre-registered 2026-11-17, before any probe-motion or pupil data was downloaded)

**Question.** The longest-lag subspace's dominant direction (the "slow mode") tracks elapsed time in 14 of 16 sessions.
Is it driven by recording instability (units drifting in and out, probe motion) or by a slow brain state such as
arousal? This is exploratory. It informs the report discussion and a possible follow-up, and it does not alter the
primary tests above.

**Slow mode.** For each session, take the first basis column of the full-session 30 s-lag readout subspace (the
same "leading direction" used by the nesting index). Its time course is the z-scored sqrt-count activity projected
onto that direction, on valid bins, averaged in non-overlapping 30 s windows (windows with fewer than half their bins
valid are dropped). Its sign is fixed so that it correlates positively with elapsed time.

**Test 1: stable units only.**
- A unit is "stable" if its mean rate is at least 0.1 Hz in each of five equal fifths of the session's valid
  task-epoch bins.
- Stable-unit copies of the interim data are refit with scripts 04 to 06 at d = 5 (raw, not residualized), with no
  other change. Sessions left with fewer than 20 stable units are excluded, and the count is reported.
- Outcomes: the animal-mean elapsed-time R-squared of the 30 s subspace (originally 0.84), the number of
  drift-flagged sessions (originally 14 of 16), and the three primary tests.
- Reading:
  - "turnover-driven" if that R-squared falls below 0.42 (half the original) and the drift flag fires in at most
    25% of included sessions;
  - "survives" if the R-squared stays at or above 0.63 (three quarters of the original);
  - "intermediate" otherwise.
- Caveat stated in advance: the stability criterion also removes units that genuinely fall silent for a
  state-related reason, so it can only bias toward "turnover-driven".

**Test 2: probe motion.**
- Signal: IBL pykilosort drift registration (`drift.um`, `drift.times`; spike-sorting revision 2024-05-06, the one
  used for the spikes), averaged over depth points, giving one motion trace per probe.
- For two-probe sessions, the two traces are averaged with weights equal to each probe's number of good MOs units.
- The trace is averaged in the same 30 s windows. The statistic is the absolute Pearson correlation with the slow
  mode.
- Null: session permutation (Harris 2020). Session i's slow mode is correlated with every other session's motion
  trace, aligned from task start and truncated to the shorter length.
- Corrected score: the real absolute correlation minus the median of the cross-session absolute correlations.
- Test: one-sided Wilcoxon across animals (sessions averaged within animal) that the corrected score is above 0.
- Secondary: the same after removing a linear trend in time from both series.

**Test 3: pupil.**
- Signal: `pupilDiameter_smooth` from `_ibl_leftCamera.features.pqt` (latest revision, recorded at download),
  averaged in the same 30 s windows.
- Sessions with more than 50% missing pupil values in the task epoch are excluded.
- Statistic, null, test and secondary: identical to Test 2.

**Overall reading.**
- "Drift": Test 1 is turnover-driven, or Test 2 is significant (p < 0.05) while Test 3 is not.
- "Brain state": Test 1 survives, Test 3 is significant and Test 2 is not.
- "Mixed or undetermined": anything else.

No correction is applied across the three pilot tests; they are reported as exploratory. Probe motion and arousal
can co-vary (movement can shift the brain), and that limitation is stated in advance.

**Compute.** Runs as a Slurm job on PACE ICE. Data downloads that need the IBL login are done locally, and only the
derived arrays are copied to ICE.

## A13: second pilot, separating causes of the slow mode (pre-registered 2026-11-21, before the engagement table or the full spike files were downloaded)

**Why.** The first pilot (A12) showed the slow mode survives removal of drifting units, and is not specifically tied
to the session's probe-motion estimate or pupil. But it is close to a straight ramp in most sessions, so correlations
with other slowly trending signals cannot discriminate. This pilot uses three kinds of evidence that do not rely on
matching one ramp to another. Everything here is exploratory and does not touch the primary tests.

**Slow mode.** Defined exactly as in A12: the first basis column of the full-session 30 s-lag readout subspace from the
original fits, projected activity averaged in 30 s windows, sign fixed to increase with elapsed time.

**Part 1: engagement and satiety beyond the ramp.**
- Engagement: per-trial posterior probability of the engaged state, `p_state1`, from IBL's public GLM-HMM output
  (`int-brain-lab/engage`, file `merged_behavioral_and_states.pqt`; Schartner's adaptation of Ashwood et al. 2022).
  The window value is the mean over trials whose stimulus onset falls in the window.
- Alignment: rows are matched to our trial table by session and order. A session is used only if `contrastLeft`,
  `contrastRight` and reward agree on at least 99% of trials; otherwise it is excluded and reported.
- Satiety proxy: cumulative number of rewarded trials up to the end of each window.
- Statistic: regress the slow mode, engagement and cumulative reward each on a quadratic in window index (removing
  the ramp and simple curvature), then take the absolute correlation between residuals. This is done separately for
  engagement and for satiety.
- Null and test: session permutation, as in A12, with other sessions' residualized signal aligned from task start.
  Corrected score = real minus median cross-session value. One-sided Wilcoxon across animals.
- Secondary:
  - sign consistency of the signed residual correlation (two-sided Wilcoxon);
  - the same test restricted to sessions whose engagement varies beyond the trend (residual SD at least 0.1).

**Part 2: spike-amplitude signature of recording artifact.**
- For each analysed unit: median spike amplitude per 30 s window (windows with fewer than 5 spikes are NaN), using
  the cached `passingSpikes` table. Amplitude trend = Spearman correlation of window amplitude with time.
- 2a: within each session, Spearman correlation across units between the unit's slow-mode loading (same sign
  convention) and its amplitude trend. A recording artifact (units shrinking toward the detection threshold lose
  detected spikes) predicts a positive correlation. Test: Fisher z averaged within animal, one-sided Wilcoxon > 0.
- 2b: an amplitude-stable copy of the data keeps units that pass the A12 rate-stability rule and whose absolute
  amplitude trend is below 0.5. Scripts 04 to 06 are refit unchanged (at least 20 units per session). The reading
  rules are those of A12 test 1:
  - "survives" if the 30 s subspace still decodes elapsed time with at least 75% of the original R-squared (0.63);
  - "turnover-driven" if it falls below 50% (0.42) and the drift flag fires in at most 25% of sessions;
  - "intermediate" otherwise.

**Part 3: sorting-independent multi-unit activity.**
- Every detected spike (`spikes.times` and `spikes.depths`, spike-sorting revision 2024-05-06), whatever its cluster
  or quality label, at depths within the span of that probe's MOs channels.
- These spikes are binned into 50 µm depth bins, which act as "channels"; channels below 0.1 Hz are dropped, and
  sessions with fewer than 10 channels are excluded. The original session's bins and trial windows are reused, and
  scripts 04 to 06 run unchanged at d = 5.
- 3a, the multi-unit slow mode: the 30 s subspace's elapsed-time R-squared (animal mean), and "match", the absolute
  correlation between the multi-unit slow mode and the unit-based slow mode in the same windows (median over
  sessions).
- 3b, the probe-motion signature: within each session, Spearman correlation between the multi-unit slow-mode
  loadings and the depth derivative of the mean multi-unit rate profile. A physical shift of the probe moves the
  whole profile, which predicts loadings that follow the profile's slope. Null: loadings shuffled across channels
  2,000 times, giving a per-session p; sessions are combined with Fisher's method.

**Overall reading.**
- "Sorting artifact": the multi-unit elapsed-time R-squared is below 0.42, or the amplitude-stable reading is not
  "survives" while 2a is significant.
- "Probe motion": the multi-unit mode reproduces the unit mode (R-squared at least 0.63 and median match at least
  0.7) and the depth-gradient test is significant (combined p below 0.05).
- "Brain state": the multi-unit mode reproduces the unit mode, the depth-gradient test is not significant, 2a is not
  significant, the amplitude-stable copy survives, and the engagement or satiety test is significant (p below 0.05).
- "Mixed or undetermined": anything else.

There is no multiplicity correction (exploratory); all statistics are reported.

**Caveats stated in advance:**
- Amplitude can fall for biological reasons, such as adaptation at high rates.
- `spikes.depths` may be in drift-registered coordinates, which would weaken the depth-gradient test. That is checked
  from the IBL documentation and reported.
- Engagement is itself a slow behavioural variable, so residual correlations carry only the part not shared with a
  quadratic trend.

**Compute.** Downloads (engagement table from GitHub, full spike files about 12.8 GB) run locally, where the IBL
login is. Only compact derived arrays (MOs-depth spike times and depth bins, per-unit spike times and amplitudes) go
to PACE ICE, where all binning, fitting and testing runs.

## A14: third pilot, does amplitude loss account for the slow mode? (pre-registered 2026-11-22, before any amplitude-rate coupling or corrected refit was computed)

**Why.** A13 found that the slow mode reappears in sorting-free multi-unit activity, has no rigid-shift signature, and
is carried by units whose spike amplitudes shrink (2a, p = 0.029). That points to spikes being lost at the detection
threshold. A13 cannot say whether amplitude loss is *enough* to produce the mode. A naive correction (regress each
unit's rate on its amplitude trajectory) cannot answer this either. Both amplitude and rate are near-ramps, so such a
regression removes any ramp in any unit whose amplitude drifts, whatever the cause. This pilot therefore estimates the
amplitude-rate coupling only from fluctuations around the time trend, and brackets the answer between a conservative
and a maximal correction. Everything is exploratory and does not touch the primary tests. Inputs are the cached A13
per-unit spike times and amplitudes (`data/interim/a13`); no new downloads.

**Common definitions.**
- Windows: the A13 30 s windows. Per unit and window: spike count over valid bins, exposure (number of valid bins
  times 0.5 s; windows with fewer than 30 valid bins dropped), and median spike amplitude (NaN with fewer than 5
  spikes).
- Relative amplitude: window median amplitude divided by the unit's median over windows, minus 1.
- Smoothed amplitude trajectory: relative amplitude with NaN windows filled by linear interpolation (nearest value at
  the ends), then a centred running median over 5 windows.
- Coupling model: a Poisson GLM (log link, log exposure offset) of window spike count on relative amplitude, fit per
  unit by iteratively reweighted least squares. Units need at least 20 windows with a finite amplitude.
  - Fluctuation coupling: the amplitude coefficient with a quadratic in scaled window time as nuisance terms.
  - Total coupling: the amplitude coefficient with no time terms.
- Spike detection loss predicts a positive coefficient: a unit's detected rate falls when its spikes get smaller.
  Adaptation, where spikes shrink at high rates, predicts a negative one.

**Part 1: is there amplitude-rate coupling beyond the trend?**
- Session statistic: the median fluctuation coupling over units. Animal means. One-sided Wilcoxon greater than 0.
- Secondary: the same with a degree-5 polynomial time nuisance, which is more stringent about slow co-trends. Also the
  fraction of units with a positive coefficient.

**Part 2: amplitude-corrected refits (bracketing).**
Each unit's binned counts are multiplied, window by window, by the factor below, clipped to the range 0.5 to 2:

$$ f_u(t) = \exp\!\left(-\beta\,\tilde x_u(t)\right), $$

where $\tilde x_u(t)$ is the unit's smoothed amplitude trajectory and $\beta$ is a coupling coefficient. Trial-window
counts get the factor of the window containing their alignment event. Units without an estimate keep a factor of 1.
Scripts 04 to 06 are refit unchanged at d = 5 on each corrected copy.
- Conservative correction (`data_ampcorr_low`): $\beta$ is the session median of the fluctuation coupling, shared by
  all units. It under-corrects if detection loss is real, because measurement noise in window amplitudes attenuates
  the estimate and the time nuisance absorbs any amplitude-driven ramp.
- Maximal correction (`data_ampcorr_high`): $\beta$ is each unit's own total coupling. It removes every part of each
  unit's log-rate that is collinear with its amplitude trajectory, so it over-corrects when amplitude and rate
  co-trend for unrelated reasons.
- Reading of each copy, by the elapsed-time R-squared of the 30 s subspace relative to the original (0.84):
  - "survives" if at least 75%;
  - "removed" if below 50%;
  - "intermediate" otherwise.
- Secondary, with no refit: project the corrected data onto the *original* slow direction, using the original
  z-scoring. Report the ratio of the projection's linear slope over time to the uncorrected slope ("residual ramp
  fraction", session median).

**Part 3: is amplitude change concentrated early in the session?**
- Tissue settling after an acute insertion is a relaxation, so it should be fastest early. Satiety or disengagement
  build late.
- For units with absolute amplitude trend at least 0.5 (A13 definition), the session's windows are split into thirds.
  In each third, the change is the Theil-Sen slope of relative amplitude times the number of windows, signed in the
  direction of the unit's overall trend.
- Early-concentration index: first-third change minus last-third change, divided by the sum of their absolute values.
  It ranges from -1 to 1, with positive meaning early. Units need at least 5 finite windows in each third.
- Session median, animal means, one-sided Wilcoxon greater than 0.
- Secondary: the same index on the slow-mode window series itself.

**Overall reading (evaluated in this order).**
1. "Amplitude cannot account for the mode": the maximal correction reads "survives".
2. "Detection loss sufficient": Part 1 significant (p < 0.05) and the conservative correction reads "removed".
3. "Detection loss contributes": Part 1 significant and the conservative correction reads "intermediate".
4. "Coupling without sufficiency": Part 1 significant and the conservative correction reads "survives".
5. "Undetermined": anything else. This includes no fluctuation coupling with a maximal correction that removes the
   mode, which is the collinear case that cannot be separated.

Part 3 is reported alongside and does not enter the rule. There is no multiplicity correction; all statistics are
reported.

**Caveats stated in advance.**
- Kilosort amplitudes are template-scaling amplitudes, not raw voltages, and the detection threshold acts on whitened
  data. The coupling is therefore an empirical relation, not a calibrated detection curve.
- Positive coupling can also arise if a brain-state change raises rates and amplitudes together. No known mechanism
  makes this large; it is named as an alternative.
- The task starts some minutes after insertion, and that delay is not in the cached data. Settling that finished
  before the task began would not show as early concentration.

**Compute.** PACE ICE (coc-cpu), from the A13 arrays already there. A unit test checks that the GLM recovers a known
coupling in simulated detection loss before the job runs.

### A14 post hoc additions (written 2026-11-22 after a local smoke run of the build, before the ICE run)

The smoke run computed the A14 build on all 16 sessions. Two numbers in it exposed design weaknesses, so two checks
are added. They are labelled post hoc, do not enter the pre-registered overall reading, and are reported alongside it.
The two numbers were:
- The Part 1 fluctuation coupling came out negative in 15 of 16 sessions.
- Without any refit, the maximal correction removed only about 15% of the slow-mode ramp along the original
  direction.

- **Post hoc 1b, coupling from isolated spikes.** Spike amplitude is known to fall within bursts, so windows with more
  firing have smaller median amplitudes. This is an effect of rate on amplitude, and it can mask detection coupling.
  The check repeats the Part 1 fluctuation coupling (quadratic nuisance), with window amplitude computed only from
  spikes at least 50 ms after the same unit's previous spike. Same test: one-sided Wilcoxon greater than 0 across
  animals.
- **Post hoc slow-maximal correction (`data_ampcorr_slow`).** The pre-registered total coupling is fitted on raw window
  amplitudes, so measurement noise and the negative fast coupling bias it toward 0, and the "maximal" correction is
  not fully maximal. This variant fits each unit's coupling, with no time terms, on a heavily smoothed amplitude
  trajectory (filled as above, then a centred running median over 11 windows, about 5.5 min). It applies the factor
  with that same trajectory, clipped to the range 0.5 to 2, and refits scripts 04 to 06. It is read with the same
  survives / intermediate / removed rule, and its residual ramp fraction is also reported.

## A15: does it generalise beyond MOs, and does the slow mode relate to behaviour? (pre-registered 2026-11-22, before any non-MOs population was binned or fitted, and before any behavioural comparison)

**Why.** These tests ask whether scaling the project up is a sensible next step. A15 uses only data already cached
locally: the good-unit spike files for the 20 MOs probes in the 16 frozen sessions, which cover every region those
probes pass through, plus the cached trial tables. It runs locally. A census of the cached cluster tables (unit
counts per Beryl region only, no activity) found 15 sessions from 12 mice with at least one non-MOs region holding
20 or more good units.

**Second-region population.** In each session, the non-MOs Beryl region (excluding root, void and fiber tracts) with
the most good units over the session's MOs probes is chosen. Ties go alphabetically.
- Preprocessing is identical to the primary analysis (same bins, rate filter, trial mask and windows), written to
  `data_region2/`.
- The primary inclusion rules apply (at least 20 units after the rate filter, at least 400 masked trials). Sessions
  that fail are excluded and reported.
- The chosen region per session is recorded in `data_region2/meta/frozen.json`.

**Part 1: does the pattern replicate in another region?** Scripts 03 to 06 run unchanged on `data_region2/` at
d = 5. These criteria are fixed in advance:
- Prior in the population (gate): Fisher-combined p of the session-level pseudo-session tests is below 0.05.
- Core pattern replicates if all of the following hold:
  - P1 (geometry) Holm p < 0.05;
  - P3 (current side, short beats long) Holm p < 0.05;
  - P2 (prior, long beats short) is not significant (Holm p ≥ 0.05);
  - the 30 s subspace decodes elapsed time with R-squared at least 0.5.
- "Partial" if 2 or 3 of the four hold; "does not replicate" otherwise.
- Nesting, drift flags and the other secondary outputs are reported as produced by 06.

**Part 2: is the slow mode shared across regions beyond the trend?**
- The second region's slow mode is defined exactly as in A12 and A13, from its own 30 s fit. It is computed on the
  MOs 30 s windows so both series share time bins.
- Statistic: the signed correlation between the two slow modes after each is residualised on a quadratic in window
  index. Both are already sign-aligned to increase with time.
- Null: other sessions' residualised second-region series aligned from task start. Corrected score = real minus the
  median cross-session value. One-sided Wilcoxon greater than 0 across animals.
- Secondary: the raw (non-detrended) correlation, reported only to show how trivially two ramps correlate. Also
  whether the second region was recorded on the same probe as the MOs units (descriptive).
- Caveat: regions on the same probe share any probe-level recording factor, so shared fluctuations here are
  necessary but not sufficient for a brain-wide state.

**Part 3: does the MOs slow mode track behaviour beyond the trend?**
- Two window-level signals, each the mean over trials whose stimulus onset falls in the window:
  - log reaction time (first movement minus stimulus onset, trials with values between 0.05 and 30 s);
  - accuracy (rewarded or not, all trials).
- Method as A13 Part 1: residualise the slow mode and each signal on a quadratic, take the absolute residual
  correlation, and correct by the cross-session median. One-sided Wilcoxon across animals.
- Secondary: sign consistency (two-sided Wilcoxon on the signed residual correlation).

**Overall.** No multiplicity correction; exploratory; all statistics reported. Part 1 is the main evidence for
whether scaling is worthwhile. Parts 2 and 3 indicate whether the slow mode is a candidate brain-wide, behaviourally
relevant signal.

## A16: post hoc follow-ups prompted by external review (written 2026-11-22, before any of these analyses was run)

**Why.** Two external reviews of the report and slides raised four questions the project had not tested. All four
are post hoc: designed after all primary and pilot results were known. They are reported as exploratory, do not
change any earlier reading, and have no multiplicity correction. They use only cached data and run locally.

**Part 1: remove the drift and refit ("is the prior masked by the ramp?").**
- Each unit's sqrt-transformed binned activity is detrended:
  - primary: least-squares quadratic in time, fit on valid bins;
  - secondary: a cosine basis with periods of at least 20 min, about three times the mean block duration.
- Trial-window values get the trend evaluated at their alignment time.
- The pipeline's residual hook is used: `S_resid` and `Swin_resid_*`, the same mechanism as the trial-locked
  residual rerun. Copies are `data_detrend_q/` and `data_detrend_c/`.
- Scripts 04 to 06 are refit unchanged at d = 5. The pseudo-session null remains valid because only the neural data
  change, not the targets.
- Reported:
  - P2 (prior rises with lag) and the per-lag corrected prior R²;
  - P1 and P3;
  - elapsed-time R² of the 30 s subspace, for RRR, PCA and random.
- Reading: "masked" if P2 is significant (one-sided Holm p < 0.05 within the rerun) and the 30 s corrected prior is
  above zero with its 95% CI excluding zero. Otherwise "not masked by a smooth trend".

**Part 2: a same-scale reference for the prior.** The full-population gate used a different decoder (Lasso,
interleaved nested CV), so subspace prior scores had no reference on their own scale.
- (a) Decode the prior from the full z-scored population in the pre-stimulus window with the subspace decoder: ridge
  alpha 1, contiguous folds, the same pseudo-session draws as script 05 (`session_seed(eid, seed, "null")`, 200
  draws). This gives the corrected R² of the full population on the subspace scale. Report each subspace's corrected
  prior relative to it.
- (b) Sensitivity check: decode the prior from the 0.5 s and 30 s subspaces, and from PCA, with the gate's decoder
  (Lasso, interleaved nested CV) against 200 pseudo-sessions.
- Reported: session medians and mouse means, with no new hypothesis test.

**Part 3: spatial reproducibility of the leading slow direction.** For each session, compare the leading 30 s
direction fit on the two session halves (the saved half fits) in three representations:
- the readout (filter) weights;
- the loading weights;
- the activation pattern, the half's covariance times the filter (Haufe et al. 2014).

The statistic is the absolute cosine between halves. Chance is the median absolute cosine between pairs of random
directions drawn in proportion to the session covariance (1,000 pairs). Reported: mouse means and a one-sided
Wilcoxon of (cosine minus chance) > 0 for each representation.

**Part 4: the step sessions.**
- A step session is one whose sign-aligned 30 s-window slow mode has a single window-to-window jump of at least 30%
  of its total range. The step time is that jump.
- At each step time:
  - (i) the change in IBL motion estimate (median over 2 min after minus 2 min before), as a percentile of the same
    statistic at every other window;
  - (ii) how concentrated the jump is across units: the share of the projected jump contributed by the top 3 units;
  - (iii) for those top units, the abrupt change in median spike amplitude across the step, as a percentile of their
    own window-to-window changes.
- Reading per session: "artifact-consistent" if (i) or (iii) is at the 95th percentile or above, "no recording
  signature" otherwise. Descriptive only.
- **A16 part 3 addendum.** Written after the part 3 leading-direction cosines were seen; descriptive only. Leading
  directions can swap order between halves when singular values are close. So also report the fraction of each half's
  leading 30 s readout direction that lies inside the other half's full 5-D 30 s readout subspace (the squared norm of
  its projection, averaged over both directions), against the same quantity for covariance-matched random directions.

## A17: testing the timescale account (post hoc; written 2026-11-23, after the talk, before any A17 neural-data analysis)

**Why.** After the 23 November talk, external reviews and the instructor's questions converged on one design flaw. The
registered lags (0.5 to 30 s) were chosen as if a longer horizon would select the block prior, but a variance-ranked
predictive objective keeps whichever directions carry the most predictable variance, and the session-time drift is
both larger and more persistent than the prior at every lag. A17 measures the timescales and variance shares directly,
extends the lag sweep across the prior's own timescale, and adds a descriptive block-switch alignment. A18 (to be
written separately, before its data are analysed) will cover a calibrated simulation and a latent state-space model.

**Status and honesty notes.**
- Everything in A17 is post hoc: designed after all primary, pilot and A16 results were known. It is exploratory,
  changes no earlier reading, and has no multiplicity correction across parts.
- It executes extensions the proposal itself listed ("lags of 60 to 120 s; GPFA latents ordered by learned timescale;
  a latent linear dynamical system"); the specifics below are post hoc, and the sweep here goes beyond 120 s, to 4 min.
- The 20 November freeze allowed bug fixes only. The library changes made for A17/A18 are disclosed here:
  - `pns.pipeline.fit_session` lag guard: a bug fix. Today a lag at least as long as a CV block, or a session half
    with no lagged pairs, fails silently (empty folds are skipped, the NaN curve makes argmax pick the first alpha,
    and an empty half returns an arbitrary basis). The guard raises instead. No existing run is affected.
  - `pns.pipeline.fit_session` `model.alpha_lags` and a separate random stream for lags outside it: a new feature.
    With the default (all configured lags) behaviour is unchanged.
  - `pns.timescales` and `pns.plotting.timescale_panels`: new code. A18 will add `pns.lds` and new simulator modes.
- What was seen before writing this entry. Part 0 (below) uses task data only: trial times, block probabilities and
  the Bayes-optimal prior, no neural data. Its numbers were computed while planning and in a run of script 23 before
  this commit, and the Part 2 prediction is derived from them. The A16 detrended refits are also already known
  (cosine detrend: corrected prior 0.031 at 0.5 s, 0.051 at 30 s; quadratic: the prior vanishes at every lag). Because
  the two detrends disagree, and I chose between them before, Part 2 runs both and requires agreement.

**Part 0: timescales (task data only; script `23_timescales_A17.py`).** Per session:
- session duration;
- median stimulus interval;
- durations of completed biased blocks (runs of `probabilityLeft`, excluding the opening unbiased block and the
  final, truncated block), in trials and minutes;
- the autocorrelation rho_pi of the Bayes-optimal prior per 0.5 s bin at 0.5 s to 8 min, and its integrated
  timescale tau_pi (truncated at the first zero crossing), in seconds and trials;
- the fraction of the per-bin prior's variance that lies inside the >= 20 min cosine span (what the A16 cosine
  detrend removes from the prior's own time course).

The prior for trial t is the belief before stimulus t; it is assigned to bins with centres in
(stimOn[t-1], stimOn[t]]. Already computed:
- tau_pi: median 67 s (about 17 trials); first zero crossing, median 2.2 min.
- rho_pi (median): 0.77 at 30 s, 0.52 at 60 s, 0.10 at 2 min, -0.19 at 4 min.
- Completed blocks: 215 (median 46 trials, 3.6 min).
- Prior variance inside the cosine span: median 12% (range 4 to 45%).

**Part 1: variance shares (descriptive; no reading rule).** On whole-session z-scored square-root activity (D10
floor), at the population level (sums over units of explained and total variance), with pseudo-session corrections
at the sum level (sum of real minus the median of the summed null), never by summing per-unit corrections.
- **Low-frequency share:** in-sample variance explained by the >= 20 min cosine design, and by the quadratic. It is
  called a low-frequency share, not "drift".
- **Prior share, primary:** pre-stimulus window activity (`win_pre_stim`, BWM-masked trials with a finite window, as
  the prior decoder uses) regressed on the prior. Both activity and prior are first projected off the cosine design
  evaluated at the window times. Corrected with the exact 200 pseudo priors of script 05
  (`session_seed(eid, seed, "null")`, `pseudo_sides`, `bayes_optimal_prior`).
- **Prior share, secondary (per bin):** the per-bin prior after regressing out from activity and prior the cosine
  design plus raised-cosine event kernels: unsigned (the A11 design), stimulus kernels signed by side times
  sqrt(contrast), movement kernels signed by choice, and feedback kernels signed by outcome. This removes the
  stimulus-evoked route by which the current side, which matches the block 80% of the time, leaks into a per-bin
  prior share.
- **Trial-locked share:** in-sample variance explained by the A11 GLM.
- **Entry check (descriptive; cut first if short of time).** Within one fitted model and one data root (raw with
  raw, cosine-detrended with cosine-detrended), at lags 1 and 60 bins:
  - recompute the full-rank ridge solution B_R at the session's alpha and G = B_R' X'X B_R + lambda B_R' B_R
    (`pns.rrr`);
  - estimate the prior loading b (per-unit regression coefficients of the secondary per-bin analysis);
  - compare the Rayleigh quotient b'Gb / b'b with the 5th eigenvalue of G, and correct b by the median over the
    pseudo-prior loadings.
  - Reported as a ratio per session.
- Writes `results/a17/budget_sessions.csv` and `budget.json`; script `24_budget_A17.py`.

**Part 2: lag sweep across the prior's timescale (script `25_longlag_A17.py`).**
- Config `config_a17_longlag.yaml` is `config.yaml` with `lags_bins: [1, 4, 16, 60, 120, 240, 480]` (0.5 s to 4 min)
  and `model.alpha_lags: [1, 4, 16, 60]`, so each session's alpha is the A16 one.
- Scripts 04 and 05 are refit on `data_detrend_c` and `data_detrend_q` into `results_a17_longlag_c` and
  `results_a17_longlag_q`. Scripts 06 to 08 are not run on these roots: their short/long logic takes the first and
  last lag, which would silently redefine P1 to P3.
- **Reproduction check (must pass before reading).** In each new root, per-session alpha and the real and null scores
  of `rrr_1`, `rrr_4`, `rrr_16`, `rrr_60`, `pca` and `random` equal the A16 roots.
- **Reported, per lag:** the corrected prior, corrected current side and elapsed-time R² for `rrr_{lag}`, PCA and
  random (mouse means, bootstrap CIs); and test pairs per CV fold. Lags of 240 and 480 bins are flagged as thinly
  validated (fewer test pairs). `orth_*` and nesting outputs in these roots compare lag 1 with lag 480 and are not
  reported.
- **Prediction (from Part 0):** the corrected prior at each lag is no larger than at 0.5 s and falls roughly with
  rho_pi(lag)², reaching about zero by 2 min.
- **Reading:** "band selection" only if, in both roots, the 60 s corrected prior exceeds the 0.5 s value (paired-null
  difference, one-sided Wilcoxon across mice, p < 0.05) and exceeds PCA's (paired-null difference, one-sided Wilcoxon,
  p < 0.05). Otherwise "no band selection". Descriptive: Spearman correlation between the per-lag mean corrected prior
  and the median rho_pi(lag)².
- No raw-data root: on raw data the drift's dominance at every lag is already established.

**Part 6: block-switch alignment (descriptive; script `28_switch_A17.py`, run after A18's scripts 26 and 27).**
- Out-of-fold decoded prior per trial (ridge alpha 1, five contiguous folds, BWM-masked trials) from (a) the
  full-population pre-stimulus window, and (b) the A18 latent model's instantaneous band projection, if A18 runs.
- Decoded values and the Bayes-optimal prior are aligned to completed switches between 0.2 and 0.8 blocks (trials
  -20 to +40). The opening unbiased block is excluded.
- Chance band: the same decoder output aligned to the switches of the 200 pseudo-session block sequences.
- Reported: mouse-mean trajectories and the number of trials after a switch until the decoded prior is half-way.

**Outcome table (fixed now; chooses the report's title, abstract claim and discussion lead after the results).**
- Part 2 "no band selection", the A18 simulation reads "sufficient", and the latent model does not isolate the prior
  (or is uninformative): the report leads with "a variance-ranked predictive objective cannot favour a prior with a
  one-minute timescale over drift at any horizon", backed by the simulation.
- The A18 latent model isolates the prior, with its simulation gate passed: lead with the positive methods result (an
  explicit-drift latent model recovers the prior where RRR does not).
- The A18 simulation reads "not sufficient": variance ranking is demoted as the explanation, and the alternatives
  (weak or nonlinear prior coding, unit-level nonstationarity) lead.
- Part 2 "band selection" in both roots: reported as contradicting the account, and the account is revised.
- In every case P1 to P3 stay first in the abstract, and the current title is kept until the readings are in.

**Multiplicity.** A17 has four uncorrected tests, all in Part 2: 60 s vs 0.5 s and 60 s vs PCA, in each of two roots.
Parts 0, 1 and 6 are descriptive.

**Errata recorded now.**
- `RESULTS.md` (limitations) and the talk's Q&A said that a 30 s lag leaves only about 130 independent windows, so
  long-lag fits are noisy by construction. That was wrong: RRR uses every overlapping pair of bins (a 66 min session
  has about 7,900 bins; a 240 s lag gives up 480 of them). The real limit on any slow signal is the number of blocks
  per session (about 13), and it is the same at every lag.
- The talk's answer that "horizon length wasn't the limit" was untested; Parts 0 and 2 test it.

**A17 part 1 addendum (written 2026-11-23 after seeing the entry-check output for one session, before running the
other 15; descriptive).** As specified, the entry check's Rayleigh quotient measures the *total* predicted variance
along the estimated prior-loading direction. That includes drift and any other signal sharing the direction, so it
does not measure the prior's own contribution: in the first session it ranked the prior direction second at both
lags, raw and detrended. It is still reported, labelled as such. Two quantities are added:
- **Upper bound on the prior's predictable variance:** the pseudo-corrected prior-explained sum of squares (per-bin
  secondary analysis, summed over units, real minus null median) times rho_pi(lag)² from Part 0, compared with the
  5th eigenvalue of G. Because it ignores how well current activity can predict the prior's future component, it is
  an upper bound: if it is below the 5th eigenvalue, the prior cannot be among a rank-5 fit's directions at that lag
  however decodable it is.
- **Capture:** the squared norm of the unit prior-loading direction projected onto that root's fitted `Vout_full_{lag}`
  subspace, minus the median over the pseudo-prior loadings, against isotropic chance d/p.

**A17 review note (written 2026-11-24, after Parts 0 to 2 had run, in response to an outside review of the committed
code and results; post hoc).** Four corrections and one sensitivity check. No reading rule changes.
- **The "upper bound" is not a bound; it is renamed a scale comparison.** The part 1 addendum above claimed that if
  the corrected prior sum of squares times rho_pi² is below the 5th eigenvalue of G, the prior cannot be among a
  rank-5 fit's directions. No derivation supports that, and it fails for four reasons. First, rho_pi² is the
  predictability of the prior from its own current value; past activity can carry more information about the
  future prior than that (for example about how long the current block has run), so it is not an upper limit on
  the prior's predictability. Second, the fit's directions need not be pure components: a weak prior component that
  shares a direction with a strong predictable signal can tilt the subspace even when its own share is below the
  5th eigenvalue, and cross terms are ignored. Third, G's eigenvalues describe the output (loading) side, while the
  prior is decoded from the input-side readout basis. Fourth, the pseudo-corrected sum of squares is an estimate
  with sampling error, not a decomposition into independent sources. The quantity is still reported, as a
  descriptive indicator that the prior's estimated predictable variance is small next to the dominant modes (its
  ratio to the 5th eigenvalue has a median of 0.05 to 0.66 across roots and lags, and a maximum of 2.18). The
  claim that the prior "could not have entered" a rank-5 subspace is withdrawn. Relatedly, the uncorrected Rayleigh
  quotient along the prior-loading direction exceeds the 5th eigenvalue in 8 to 14 of 16 sessions (raw and
  detrended, 0.5 s and 30 s), and the pseudo-corrected one in 2 to 7; the direction the prior loads on is often
  strongly predictable, which is a further reason the comparison cannot settle entry.
- **The variance shares are measured differently and are not one budget.** The >= 20 min share is the in-sample R²
  of the cosine design on all 0.5 s bins of z-scored activity (not null-corrected). The primary prior share is
  measured on pre-stimulus trial windows after projecting the cosine span off both sides, and is pseudo-corrected.
  Their ratio (about 100) is not an exact competition between two additive sources. The per-bin secondary prior
  share is on the same bins as the low-frequency share; per session the ratio of the two has a median of 124. The
  report says "about two orders of magnitude larger, under the respective measurements".
- **Pair counts are not independent observations.** The per-fold test-pair counts stored by the lag guard check that
  each fold has data; consecutive pairs are strongly dependent, and inference is at the mouse level.
- **No claim of a misaligned prior in the original decoder.** `prior_per_bin` (Part 0, and the per-bin prior share)
  assigns trial t's prior to the 0.5 s bins before trial t's stimulus onset. The original decoder is unaffected by
  that convention: it uses spike counts in the event-aligned window [-0.6, -0.1) s before stimulus onset
  (`binning.window_counts`), and `bayes_optimal_prior` gives trial t's prior from the sides of trials before t. No A17
  result implies that the original prior decoding was misaligned.
- **Sensitivity of the prior timescale (Part 0).** Computed on the trial-indexed prior (one value per trial with a
  valid stimulus onset, lags in trials), so it does not depend on how the prior is spread over bins: median 12.2
  trials (IQR 10.9 to 13.8; bootstrap 95% interval of the median over sessions 11.0 to 13.6), first zero crossing
  at 27 trials, autocorrelation 0.67 at 8 trials and 0.37 at 15 trials. That is shorter than the bin-based 16.9
  trials (67 s divided by the median stimulus interval); the bin-based value is lengthened by long inter-trial gaps,
  during which the prior is constant. The bin-based median is 67 s (IQR 55 to 75 s; bootstrap 95% interval of the
  median 55 to 75 s). Both versions put the prior's memory well below a block (median 46 trials, 3.6 min). Added to
  `23_timescales_A17.py` (new columns `*_trialidx` in `results/a17/timescales.csv`; earlier columns unchanged).

## A18 part A: calibrated simulation of the prior competing with drift (post hoc; written 2026-11-24, before any calibration or simulation outcome was computed)

**Why.** A17 measured that the block prior is small and short-lived next to the slow component, and that no lag up
to 4 minutes selects it. It did not show that this competition causes the original failure, and the review note of
24 November withdrew the claim that the prior was provably excluded from the rank-5 subspaces. Part A asks the causal
question in a setting where the answer is known: when a prior and a drift of the measured sizes share one simulated
population, does rank-5 lagged RRR lose the prior the way it did in the recordings, and is the drift needed for that?
It also tests a weakness of the prior score itself: the pseudo-session null redraws the block sequence, so neurons
that merely remember the last few real stimuli correlate with the real prior and not with the pseudo priors, which
would give a positive corrected score without any encoded prior. Part B (the latent state-space model and its
simulation gate) is not specified here; it gets its own addendum, committed before any latent-model fit on simulated
or real data.

**Status and honesty notes.**
- Post hoc relative to the original study: designed after all primary, pilot, A16 and A17 results (including the
  review note) were known. Exploratory; changes no earlier reading, no frozen analysis and no A17 decision rule.
- What was seen before writing. The simulator's real-task path was checked for structure only (the simulated
  session has the real session's length, prior and trial mask; unit rates match; the pre-stimulus window carries
  trial t's task latents). Timing runs of `fit_session` and of one sweep job (cell "nodrift", seed 1000, at the
  starting gains, not the calibrated ones) were made with their outputs not printed or inspected, and the summary
  and figure code were run on random placeholder numbers. No calibration statistic of a simulated session, and no
  simulated decoding score, has been looked at.
- Code added for this entry (new features after the 20 November freeze): `pns.synth` options `task`,
  `unit_rates_hz`, `history_gain`/`history_tau`/`history_k` and `evoked_gain` (all off by default; the default
  output stays bit-identical, checked by the fingerprint test); `pns.sim_a18`; `scripts/26_sim_A18.py`;
  `tests/test_sim_a18.py`. The tests check that the simulation's prior and elapsed-time scores equal
  `pipeline.decode_session` to 1e-12 and that `calibration_stats` reproduces the published real values (A16
  full-population ridge prior, A17 low-frequency, trial-locked and pre-stimulus prior shares) to 1e-10.

**Audit of the generator against the recordings.**
- *Matched exactly, per simulated session (taken from one real session, task data and unit rates only):* trial
  timing (stimulus, movement and feedback times, including the long gaps), stimulus sides and contrasts, choices,
  outcomes, block probabilities, the BWM trial mask, session length (so the number of 0.5 s bins), number of units,
  and each unit's mean firing rate. The Bayes-optimal prior is computed from the real sides, so its timescale and
  block structure are the recorded ones.
- *Matched by calibration (six gains onto six real session medians):* full-population corrected prior R² (sets the
  prior's strength); the >= 20 min share (drift strength); the 5 to 20 min share (drift's mid-band weight);
  full-population previous-side AUC from the pre-stimulus window (strength of the stimulus-history trace); the
  trial-locked share (unsigned evoked responses); full-population current-side AUC from the post-stimulus window
  (signed stimulus response).
- *Assumptions, not matched (each could change the answer):*
  - Nuisance rank and spectrum. Low-rank drift (3 processes with variances decaying by 0.3 per component, fixed
    loadings) is the primary regime; per-unit independent drift (rank about p) is the second. Real drift may lie
    between them, and A16 found the units carrying the slow mode change between session halves, which fixed
    loadings do not reproduce.
  - Mixing geometry. Loadings are independent Gaussian across units (scale 0.6); the stimulus loading shares 0.3 of
    the prior loading; the prior, history, evoked, slow-noise and drift loadings are otherwise independent.
  - The prior is encoded linearly in log rate as one latent proportional to (prior - 0.5), switching at the previous
    trial's feedback + 0.5 s.
  - Stimulus history is one latent, sum over the last 10 sides with weights exp(-(j-1)/1 trial); real history
    memory may be longer or include choices and outcomes.
  - Evoked responses: exp(-t/0.3 s) kernels at stimulus, movement and feedback onsets.
  - Other variability: an AR(1) slow noise (autocorrelation 0.99 per 0.5 s, sd 0.3, own loading), the original
    fast noise and two shared fast noise factors. Observations are Poisson (no overdispersion or refractoriness).
  - Reported, not matched (diagnostics): the leading and five leading principal components' variance fractions, the
    A17 pre-stimulus prior share, and the full-population history-controlled prior score.

**New real-data computation (stage `targets`; descriptive).** `calibration_stats` on the 16 recorded sessions, with
script 05's exact pseudo-session draws: the six calibration targets, the diagnostics above, and one new descriptive
number, the full-population *history-controlled* prior score (the prior and every pseudo prior each regressed on
their own previous 5 sides before decoding). Writes `results/a18/real_targets.csv` and `real_targets.json`. No test
is made on these numbers.

**Calibration (stage `calibrate`).** Seeds 900 to 915, seed 900 + k using real session k's task and rates (disjoint
from the sweep seeds). Starting gains: prior 1.0, drift 1.0, mid-band weight 0.5, history 0.3, evoked 0.5,
stimulus 1.5. Each iteration simulates all 16 sessions, takes the median of each statistic, and multiplies each gain
by (target / current) raised to 0.7 times the statistic's scaling exponent (0.5 for shares and R², 1 for AUC - 0.5),
the factor clipped to [0.5, 2] (2 if the current value is not positive). Stop when all six are within 10% of
target, or after 12 iterations. A target is "accepted" if within 25%; unaccepted targets are reported, not hidden.
The per-unit regime then re-fits only its drift gain and mid-band weight onto the same two drift targets, other
gains fixed. Only calibration statistics are computed during calibration; no subspace is fitted.

**Cells (stage `sweep`).** Every cell uses the same 32 seeds (1000 to 1031; seed s uses real session (s - 1000) mod
16, so each task appears twice), so trial sequences, loadings and noise draws are paired across cells; within a
regime, cells differ only in the gains named.
- `favourable`: prior gain x 3, no drift (positive control).
- `nodrift`: calibrated, drift gain 0 (matched weak prior, no drift).
- `lowrank_x0.33`, `lowrank_x1`, `lowrank_x3`: low-rank drift at 1/3, 1 and 3 times the calibrated drift gain.
- `perunit_x0.33`, `perunit_x1`, `perunit_x3`: the same for per-unit drift.
- `neg_history`: prior gain 0, everything else as `lowrank_x1` (stimulus history, evoked responses, drift present).
- `neg_pure`: prior gain 0 and history gain 0, otherwise as `lowrank_x1` (null calibration check).

**Analysis per simulated session (`pns.sim_a18.analyse_session`).** The registered pipeline: `fit_session` with
`config.yaml` (lags 0.5, 2, 8 and 30 s; d = 5; the alpha grid and contiguous purged folds), PCA and the
covariance-matched random subspace; prior decoding from the pre-stimulus window by ridge with contiguous folds and
200 pseudo sessions (seed [s, 99]), for every subspace and the full population. Recorded: corrected prior per set;
the P2-style change (30 s minus 0.5 s, corrected by the median paired pseudo difference); the history-controlled
score per set; elapsed-time R² and current-side AUC per set; and the ground-truth capture of the true prior
direction (the share of its optimal linear readout inside each subspace, and of its loading inside the 0.5 s and
30 s loading bases, against chance d/p). The cells `nodrift`, `lowrank_x1`, `perunit_x1` and `neg_history` are also
run after the in-memory cosine detrend (`timescales.detrend_pre`, identical to the A16 copy), for comparison with
the A16/A17 cosine results. Output: `results/a18/sim_seeds.csv` (one row per cell, seed and pipeline).

**Fixed metrics.** For a cell, c(set) is the mean over the 32 seeds of the corrected prior, and the capture of a set
is c(set) / c(full population) (95% interval by resampling seeds). "Positive in enough seeds" means at least 22 of
32 (one-sided binomial p < 0.05).

**Readings (stage `summary`).**
- *G1, positive control.* Passes if in `favourable` the full-population and the 30 s scores are each positive in at
  least 22 of 32 seeds. If it fails, reading A is "uninformative".
- *A, is drift needed or sufficient (primary: low-rank; secondary: per-unit)?* Let k0 be the 30 s capture in
  `nodrift`. If k0 < 0.25: "weak prior sufficient" (the calibrated prior is not captured at 30 s even without
  drift, so drift is not needed to explain the failure). Otherwise, at the calibrated drift: "drift sufficient" if
  the 30 s capture is below k0 / 2 and the median P2-style change is at most 0; "drift not sufficient" if the
  capture is at least k0 / 2 and the median change is positive; "intermediate" otherwise.
- *B, history leakage.* `neg_pure` positive (full population) in 22 or more seeds: the null is miscalibrated, and
  every simulated prior score is suspect. `neg_history` positive in 22 or more: "leakage present" (a stimulus-history
  trace of the calibrated strength produces a positive pseudo-session-corrected prior score with no prior encoded);
  its size is reported as a fraction of the real full-population target. The history-controlled score is "valid" if
  it is positive in fewer than 22 seeds in `neg_history` and in 22 or more in `nodrift`.
- *C, profile comparison (descriptive).* For `lowrank_x1` and `perunit_x1`, eight features are compared with the
  real raw-data mouse means and their 95% intervals: corrected prior at 0.5 s, 30 s, PCA and random; elapsed-time R²
  at 30 s, PCA and random; and the P2 change. The count inside the real interval is reported. A match shows the
  simulated mechanism *can* produce the recorded pattern; it does not show that it *does* in the recordings.
- *Recommendation for Part B.* Proceed to the latent state-space model on real data only if G1 passes, the
  history-controlled score is valid (otherwise the model's readout cannot be told apart from stimulus memory and the
  design must change first), and the full-population prior is positive in 22 or more seeds of `lowrank_x1` (so
  there is something to find at realistic drift). Even then, Part B's own simulation gate comes first.

**Multiplicity.** The readings are about the simulator, not tests on neural data. The one new real-data number (the
history-controlled full-population prior) is descriptive.

**Not done here.** No latent-model fit, on simulated or real data. No frozen analysis, earlier result or A17 rule is
changed. No branch is merged.

**A18 part A addendum (written 2026-11-24 after the calibration output was seen, before the sweep ran; post hoc).**
Calibration put the stimulus-history gain at 0.036 (prior gain 0.29): the encoded prior alone already makes the
previous side as decodable as in the recordings, so the specified `neg_history` cell is almost the same as
`neg_pure` and cannot test whether stimulus memory alone could mimic the prior. Also seen at calibration: the
full-population history-controlled prior score is +0.041 in the calibrated simulation (median of 16 calibration
sessions) and -0.061 in the recordings. One cell and one reading are added; nothing specified above changes.
- **Cell `neg_history_strong`:** prior gain 0, low-rank drift at the calibrated gain, every other gain as calibrated,
  and the history gain re-calibrated with the prior removed (same seeds 900 to 915 and the same fixed-point rule) so
  that history alone reproduces the real full-population previous-side AUC. Stage `calibrate_neg`; stored in
  `calibration.json` under `neg_history_strong`.
- **Reading B2 (history alone):** "history alone can mimic the prior score" if in `neg_history_strong` the
  full-population corrected prior is positive in 22 or more of 32 seeds and its mean is at least half the real
  target (0.108 / 2). Reported descriptively alongside: its history-controlled score, and how the real
  history-controlled score (-0.061) compares with every cell's.

**A18 part A notes after the results (written 2026-11-24, after the sweep and summary; post hoc).**
- **The ground-truth "capture" metric is withdrawn as uninterpretable.** It estimates the prior's loading by
  regressing activity on the true per-bin prior. With only about 13 blocks per session, drift correlates with the
  prior by chance, so the estimate picks up drift: in `neg_pure`, which encodes no prior, the 30 s subspace
  "contains" 0.53 of the estimated prior readout (chance 0.11). The values stay in `sim_seeds.csv` but are not
  reported as results. No reading depended on them; the pre-specified capture is the decoding ratio.
- **The decoding-ratio capture is unstable where the full-population score is small** (per-unit cells, drift x 3),
  so `RESULTS.md` reports the corrected scores with their intervals alongside it.
- **The figure was redrawn** for legibility (panel a now shows corrected scores, not ratios; panel d added for the
  controls). Presentation only.
- **Provenance.** Targets ran at `3a81ba1`, calibration at `3a81ba1` with only result and log files modified, the
  history-only calibration and the sweep at `2f7611d` (likewise); the figure code was edited after the summary.

**A18 audit note (written 2026-11-24, after two independent reviews of the committed code, results and text; post
hoc).** No reading changes. Corrections:
- *Wording.* RESULTS.md had overstated three things, now corrected: (1) that drift "is sufficient to reproduce the
  loss"; the pre-set low-rank reading is "intermediate", because drift removes the 30 s prior score but not the 30 s
  advantage over 0.5 s (21 of 32 seeds); (2) that stimulus history "produces most" of the recorded prior score; it is
  about half to 70% depending on the summary, and only in the extreme case where history is given all of the
  recorded previous-side decodability; (3) a claim that a variance-ranked objective has "no horizon" favouring the
  prior, which rests on the same separable-components picture the A17 review note withdrew; now labelled a heuristic.
  Also corrected: "a third of the drift halves the 30 s score" (it cuts it by a third), a missing table row (per-unit
  drift x 3), principal-component fractions, and the comparison of the recordings' history-controlled score, which had
  been made against single simulated sessions rather than medians of 16.
- *Pairing.* Seeds s and s + 16 share a task, so there are 16 independent tasks, not 32. Spike-level Poisson noise is
  not shared across cells, and `neg_pure` draws different evoked-response loadings than the other cells (the history
  loading is drawn from the same generator only when history is on). The text said "same loadings and noise draws";
  corrected. Task-level counts and task-resampled intervals are added (stage `audit`, `results/a18/audit_checks.json`);
  every pre-set reading holds at the task level, the history-alone reading only borderline (12 of 16, p = 0.038).
- *History-controlled score.* The target is regressed on its own previous sides over the whole session before
  cross-validation, which gives the real target a small negative bias when neurons encode the real sides
  (-0.01 to -0.03 in a toy model). Refitting within training folds moves the recordings' median from -0.061 to
  -0.058, so it does not explain that value. Left as specified; noted.
- *Tests.* `test_negative_control_has_no_prior_latent` uses the synthetic task path, and the decode-equivalence test
  covers only the prior and elapsed-time scores of four subspaces. Their scope is narrower than their names suggest.
  The reviewer checked the real-task path directly (prior switch timing, transients and movement against the
  pre-stimulus window, on all 16 tasks) and found no leak; the first 0.05 s of the window carries the previous trial's
  value in 4 of 8,752 trials.

## A18 part B: the latent state-space model, on simulated sessions only (post hoc; written 2026-11-24, after the A18 part A results and audit, before any latent-model fit on simulated or real data was inspected)

**Why.** Part A showed that drift of the recorded strength erases a realistic prior from the 30 s RRR subspace while
the full population still decodes it, and that a stimulus memory with no prior can produce a pseudo-corrected prior
score of comparable size. A latent model with an explicit drift term is only worth running on the recordings if, on
simulated sessions where the truth is known, it (1) keeps the prior when drift is present and (2) does not report a
comparable "prior" when only stimulus memory is present. Part B is that one bounded test, with a stopping rule. It
follows an outside review of the briefing (24 November) that recommended exactly this test and nothing more. No real
neural data is used; whether to run the model on the recordings is a separate decision after the gate.

**What was seen before writing.** All part A results and the audit. One timing run of the readout on one simulated
session (cell `lowrank_x1`, seed 1000), with its output not printed. No latent-model result has been looked at.

**Model (pns.lds, tested on synthetic data in `tests/test_lds.py`).** Trial-indexed: one observation per trial, the
square-root pre-stimulus window counts of every trial with a valid window, z-scored per unit. Known inputs: the
>= 20 min cosine basis of the window time (explicit drift term) and the previous trial's side, choice and reward. 8
latents, each with its own AR(1) timescale (q = 1 - phi²); EM with 3 restarts, at most 300 iterations, tolerance
1e-6; restart seed [s, 97]. Fixed in advance: no choice of K, inputs or settings is made from results.

**Readout.** Each trial's instantaneous latent estimate (generalised least squares on that trial's window alone, inputs
subtracted), so the model cannot build a prior by accumulating past stimuli through its dynamics. The prior is
decoded from the 8 estimates on the decoder's trials with the subspace decoder (ridge, alpha 1, five contiguous
folds) and the same 200 pseudo sessions as part A; the corrected score is the primary readout ("all latents").
Secondary, descriptive: the same from the latents whose timescale lies within a factor of 3 of the session's
trial-indexed prior timescale ("band").

**Sessions.** Cells `nodrift` (reference), `lowrank_x1`, `neg_history_strong` and `neg_pure` of part A, seeds 1000 to
1031, regenerated deterministically (checked: the full-population prior score must equal part A's). Judged at the task
level: the two seeds of each task are averaged, giving 16 tasks; "positive in enough tasks" means at least 12 of 16
(one-sided binomial p = 0.038).

**Gate.**
- *B1, prior retained under drift:* in `lowrank_x1`, the all-latent score is positive in at least 12 of 16 tasks and
  its mean is at least half the full-population mean in the same sessions.
- *B2, stimulus memory not mimicked:* in `neg_history_strong`, the all-latent score is positive in fewer than 12 of 16
  tasks and its mean is at most a quarter of the `lowrank_x1` all-latent mean.
- *Null:* in `neg_pure`, positive in fewer than 12 of 16 tasks; otherwise the readout is miscalibrated and the work
  stops.

**Reading and stopping rule.** B1 and B2 pass: "gate passed"; running the model on the recordings may then be
considered, as a separate decision with its own specification. B1 passes and B2 fails: "recovers a correlated signal
but does not separate belief from stimulus memory"; stop. B1 fails: stop. In every case no further model variants,
inputs or settings are tried. Script `scripts/27_lds_sim_A18.py`; outputs `results/a18/lds_sim_seeds.csv` and
`lds_gate.json`.

**A18 part B result note (written 2026-11-24, after the gate ran; post hoc).** The gate read "does not retain the
prior under calibrated drift: stop". B1 failed (all-latent score in `lowrank_x1`: mean -0.003, positive in 8 of 16
tasks, against a full-population mean of 0.167); B2 and the null passed. Descriptive: without drift the readout
scored 0.026 (13 of 16 tasks) against 0.170 for the full population, so the model retains little of the prior even
when nothing competes; the fitted timescales with drift were dominated by slow latents (medians 43, 31, 21 and 9
trials) and without drift by fast ones. One plausible contributor, not tested (the stopping rule forbids variants):
the inputs include the previous stimulus, which correlates 0.64 with the prior, so subtracting the input term removes
part of the prior-related activity. The regenerated sessions matched part A exactly (largest difference 1e-16); 124
of 128 fits converged within 300 iterations. Per the stopping rule, no latent model is run on real data and no
variant is tried.

## A19 (post hoc): sensitivity of reported comparisons to one session (written 2026-11-25, before any A19 number was computed)

**Why.** An AI-agent audit of the repository on 2026-11-25 (not human review) found that session `4d8c7767`
(mouse SWC_038, 128 units, 562 decoded trials) has an implausible corrected full-population prior score in the A16
same-scale reference: 1.59 (raw out-of-fold R² −0.94 against a pseudo-session median near −2.5; `results/a16/sessions_d5.csv`)
and a history-controlled score of −6.30 (`results/a18/real_targets.csv`). The corrected score (real R² minus the
median R² of 200 pseudo sessions) is not bounded above by 1 when both terms are strongly negative, so one session can
move a mean. The session was identified *because* its value is extreme, so this analysis is data-driven and post hoc.

**What is fixed now, before computing anything.**
1. *Registered P2 is not changed.* The registered result (one-sided Wilcoxon over 13 mice of the paired-null
   corrected difference R²(30 s) − R²(0.5 s), mouse means, Holm over P1–P3) stands as registered whatever this
   analysis shows. A19 only reports how much it depends on this session.
2. *Quantities, each computed with and without session `4d8c7767` (SWC_038 is then represented by its other session,
   `1e45d992`), and each under three aggregations (mouse mean, as registered; median across mice; median across
   sessions), with sign counts:*
   - **S1, registered P2** from `results/decoding` and `results/null` with `pns.analysis.paired_null_diff`; the
     with-session mouse-mean version must reproduce `results/stats/d5/primary.csv` (p = 0.892, mean −0.099) exactly,
     otherwise the script stops. Wilcoxon p, bootstrap interval (same `bootstrap_ci`, seed 0), and the Holm-adjusted
     P2 with P1 and P3 unchanged.
   - **S2, the A16 same-scale reference** (`results/a16/sessions_d5.csv`): full population, 0.5 s subspace, 30 s
     subspace and PCA, ridge and Lasso decoders, and the ratios subspace / full population.
   - **S3, the registered profile used by the A18 comparison** (`results/stats/d5/session_scores.csv`, prior and
     elapsed time for the reported feature sets) and the A18 reading C count of profile features within the
     recordings' interval, recomputed against the profile without the session (intervals for both versions
     recomputed by the same bootstrap, seed 0, so they are comparable).
   - **S4, simulation comparisons quoted in the text:** history-alone full-population mean as a fraction of the
     recordings' reference (mouse mean and session median); the recordings' session medians of the six calibration
     statistics and of the history-controlled score over 15 versus 16 sessions; and the A18 audit's median-of-16
     probability recomputed with the 15-session threshold. No simulation is re-run and the calibration is not redone;
     the shift of each target is reported instead.
   - **S5, transparency listing:** every session and quantity in `results/a16/sessions_d5.csv` and
     `results/a18/real_targets.csv` whose corrected score exceeds 1 in absolute value. Listed, not excluded; only
     `4d8c7767` is analysed.
3. *Choice of summary fixed in advance, not by significance.* From now on the documents report, for every post hoc
   descriptive quantity built on the corrected R² (the A16 reference and ratios derived from it), the session median
   alongside the mouse mean, with the session median as the primary descriptive summary (the A18 calibration
   already used session medians). For the registered P2 the registered statistic remains primary; the variants are
   reported beside it whatever their p-values.
4. *No other analysis.* No new neural-data, simulation or latent-model fit. Script `scripts/28_sensitivity_A19.py`
   (stage `sensitivity`) reads committed result files only; outputs `results/a19/sensitivity.json` and
   `results/a19/sensitivity_tables.csv`.

**Also recorded in this entry: sources for numbers previously quoted without a committed file.** Stage `sources` of
the same script computes, from task data only (no neural data), the statistics of the ideal observer's prior quoted
in the A18 notes and the walkthrough: the correlation of the prior with the previous stimulus side and the in-sample
R² of the prior on the last 1, 5 and 10 sides, per session (median over the 16 sessions), on the full trial sequence
and on the decoded trials; output `results/a19/prior_history.csv` and `.json`.

**A19 result note (written 2026-11-25, after the run; post hoc).** The with-session registered P2 was reproduced
exactly (p = 0.892, mouse mean −0.099), so the script proceeded. All values are in `results/a19/sensitivity.json`.
- *S1, registered P2 (unchanged as the registered result).* The session's own paired-null value is −0.27, the fourth
  lowest of 16, so it is not an outlier on this quantity. Without it: mouse mean −0.079 (was −0.099), median across
  mice and across sessions about −0.04 either way, 5 of 13 mice positive (was 4), one-sided Wilcoxon p = 0.793 (was
  0.892), Holm-adjusted p the same. The registered conclusion does not depend on the session.
- *S2, the A16 same-scale ridge reference (post hoc).* Full population: mouse mean 0.159 with the session, 0.101
  without; session median 0.108 with, 0.087 without. Ratios to the full population, by session median (the primary
  descriptive summary fixed in A19 before the run): 0.5 s subspace 0.62 (0.72 without), 30 s subspace 0.06 (0.17),
  PCA 0.18 (0.25). By mouse mean: 0.34, −0.29 and 0.08 with the session. The earlier statements "the 0.5 s subspace
  captures about a third, the 30 s subspace none, PCA 8%" are mouse-mean ratios driven by one session; on the
  session-median scale the 0.5 s subspace captures most of the full-population score and the 30 s subspace little.
  The Lasso (Findling) decoder values barely move (for example 30 s subspace 0.038 to 0.036).
- *S3, the registered profile and A18 reading C.* Profile means move little except the prior at 0.5 s (0.054 to
  0.036) and PCA (0.013 to 0.027). With intervals recomputed by the same bootstrap, the low-rank regime matches 6 of
  8 features with the session (as committed) and 7 of 8 without; the per-unit regime 3 of 8 with (committed: 2; the
  difference is an interval-boundary effect of recomputing the bootstrap) and 2 of 8 without.
- *S4, simulation comparisons.* The strong history-alone condition's full-population score (0.078) is 49% of the
  mouse-mean reference and 72% of the session median with the session; 77% and 89% without. The memory condition
  at the recorded strength scores −0.012 (below zero) under every reference. Dropping the session would move the
  calibration target for the full-population prior score from 0.108 to 0.087 (−19%; outside the 10% stopping
  tolerance, inside the 25% acceptance band); the other five targets move by 10% or less. The simulation was not
  re-run. The recordings' history-controlled session median is −0.061 with the session (6 of 16 positive, one-sided
  Wilcoxon p = 0.70) and −0.050 without (6 of 15, p = 0.55): indistinguishable from zero either way. The A18 audit's
  median-of-16 probabilities change little (for example `lowrank_x1` 0.003 to 0.007 under random 16-of-32
  resampling, 0 under one seed per task; `perunit_x1` 0.12 to 0.17 and 0.017 to 0.038).
- *S5.* Only this session exceeds 1 in absolute value in the listed files (three quantities).
- *Sources stage.* Prior against previous sides, median over 16 sessions on the full trial sequence: correlation
  with the previous side 0.64; in-sample R² of the prior on the last 1, 5 and 10 sides 0.41, 0.81 and 0.86 (decoded
  trials: 0.63, 0.39, 0.80, 0.85). `results/a19/prior_history.json`. The earlier "0.42" for the last side is 0.41.

## Corrections and record-keeping notes (written 2026-11-25, after AI-agent reviews of the whole repository; post hoc)

Six AI-agent reviewers (Claude subagents briefed separately, without the main session's conclusions; not independent
human review) audited code, statistics, numbers, the mathematical walkthrough, the course report and the repository
on 2026-11-25. No registered result changes. Recorded here:

1. **Who reviewed.** Every review described in this file, `RESULTS.md`, `ANALYSIS_LOG.md` and the reports as
   "independent" (the A17 review note, the A18 audit note "after two independent reviews", and the 25 November
   round) was an AI-agent review, not human review. Reviews the author pasted into the working session are recorded
   as pasted reviews; their authorship is not recorded here. No part of this project has had independent human
   review of the code or analysis.
2. **A17 part 6 was not completed.** The block-switch alignment (Part 6, script `28_switch_A17.py`) was never
   written or run. It is dropped as of this date and will not be run before the report deadline; its variant (b)
   depended on the latent model, which failed its gate (A18 part B). The script number 28 is used instead by A19.
3. **Provenance.**
   - A17 part 0 (`23_timescales_A17`, task data only) ran at 18:34 on 2026-11-23 at commit `4dee202`, five minutes
     before the A17 entry was committed (`0dbca28`, 18:39). The log row is not marked dirty because the new files
     were untracked. Part 0 has no reading rule.
   - The A17 part 1 addendum states it was written after one session and "before running the other 15". The
     16-session run is logged at 18:44 and the addendum was first committed at 19:08 (`8486770`), so the ordering is
     the author's working-session record and cannot be verified from git. The addendum governs descriptive
     quantities only.
   - A17 parts 1 and 2 ran on uncommitted code (`0dbca28-dirty`), committed unchanged in `8486770` (already noted in
     `ANALYSIS_LOG.md`); their reading rules were committed beforehand in `0dbca28`.
   - A19 ran with its script untracked (log rows at `9cd4a62`); the script was committed unchanged in `97b272b`.
4. **Numbers with no committed source.** The A18 audit note's toy-model bias ("−0.01 to −0.03"), the refitted
   history-controlled median ("−0.058") and "4 of 8,752 trials" come from AI-agent checks run outside the repository.
   They are kept above as part of the dated record but are not cited elsewhere. The prior-history statistics now have
   a source (A19 sources stage).
5. **A18 part B result note.** Its "one plausible contributor" (the previous-stimulus input absorbing prior-related
   activity) was checked by an AI-agent diagnostic outside the repository: on four simulated sessions, subtracting
   only the cosine inputs changed the readout little (`lowrank_x1` seeds 1000 and 1001: 0.017 to 0.050 and −0.048 to
   −0.060, against full-population scores of 0.25 and 0.16). It is not supported as the explanation. The conclusion
   is limited to this specification (inputs and single-trial readout); the model retained about 15% of the prior even
   without drift, no positive control was run for it, and B1's threshold (half the full-population score) exceeds
   what lagged RRR itself captures at 30 s without drift (0.41).
6. **Interpretation, corrected wherever it appears.**
   - *Stimulus memory.* The derivation shows memory raises the corrected score relative to the null baseline; it
     does not guarantee a positive score. In simulation, memory at the strength the recordings imply scored −0.012
     (16 of 32 seeds positive); only a deliberately strong memory scored +0.078 (24 of 32; 12 of 16 tasks, p =
     0.038). The no-prior, no-memory baseline is −0.043, because raw out-of-fold R² is strongly negative and the
     pseudo-session distribution is skewed. Prior decodability that could come from memory of recent stimuli is a
     known concern (the ideal observer's prior is itself a function of past stimuli, and subjective priors are often
     modelled as kernels over past events); it is not presented as a new finding.
   - *The recordings' history-controlled score* (−0.061) is indistinguishable from zero (above); its low position
     against medians of 16 simulated sessions mainly reflects that the simulator varies less across sessions than the
     recordings on this quantity (interquartile range of the history-controlled score: −0.135 to 0.125 in the recordings,
     −0.126 to 0.137 without session `4d8c7767`, against −0.04 to 0.06 in `lowrank_x1`). For the full-population
     score the difference is small once that session is excluded (SD 0.24 recorded against 0.19 simulated; 0.43 with
     it).
   - *Framing.* The A17 outcome table had no row for an "intermediate" simulation reading, which is what A18 gave.
     Any framing of the report around variance ranking and drift is therefore a post hoc choice. Drift is not
     established as the cause: without drift, longer horizons help (+0.050); at the recorded drift the 30 s
     subspace's prior score is removed while the full population keeps it, and the horizon change is near zero
     (median +0.015, positive in 9 of 16 tasks).
   - *Calibration.* Six gains fitted to six targets leave no degrees of freedom, so the match is by construction; the
     fixed settings (slow-noise timescale about 50 s, drift rank 3, decay 0.3, one-trial memory length) were not
     varied.
   - *Counts.* The drift drop "p = 0.002" was computed over 32 seeds that share 16 tasks; at the task level the 30 s
     prior score is positive in 14 of 16 tasks without drift and 8 of 16 at the recorded drift
     (`results/a18/audit_checks.json`). The two seeds of a task correlate between −0.34 and 0.92 depending on the
     condition (not 0.52 to 0.92); task-resampled intervals are 19 to 39% wider than seed-resampled ones for the
     full-population score in conditions with a prior, and narrower in some others (not "10 to 25% wider").
   - *P2.* "Not supported" rather than "failed": the interval for the mean change (−0.218 to 0.002) is wider than the
     prior reference itself, so modest rises are not excluded.
7. **Derived check added to A19's script.** Stage `derived` of `28_sensitivity_A19.py` applies A18 reading C (profile
   features inside the recordings' intervals) to every simulated condition, reading committed files only
   (`results/a19/profile_all_cells.json`; it reproduces the committed counts for the two drift regimes). The
   no-prior conditions match 6 of 8 (strong history alone) and 5 of 8 (calibrated history; no prior and no history),
   against 6 of 8 for calibrated low-rank drift.
8. **Prior timescale units.** The integrated timescale of the prior is 67 s when computed on 0.5 s bins (16.9 trials
   at the median trial interval) and 12.2 trials when computed on the trial sequence (`results/a17/timescales.json`).
   Text that wrote "67 s, about 12 trials" mixed the two; both are now given with their basis.
9. **Correction to note 6 (same day).** Note 6 calls the history conditions "memory at the strength the
   recordings imply" (−0.012) and "a deliberately strong memory" (+0.078). That labelling is wrong. The −0.012
   condition (`neg_history`) is the history gain fitted jointly with the prior (0.036), with the prior then removed.
   The +0.078 condition (`neg_history_strong`) is memory alone, at the gain (0.061) that reproduces the recorded
   previous-side decodability without any prior: it is what the recordings would require if MOs carried no prior,
   not an arbitrary extreme. So, if there is no prior, the memory the recordings require yields a corrected prior
   score of 72% of the recorded session median; the recorded score cannot by itself separate a block prior from
   memory of recent stimuli. The rest of note 6 stands.
10. **After an outside review of the rewritten report (same day, later).** The author pasted a review of the report
    and the TA deck (its authorship is not recorded here). Its factual claims were checked against the code and the
    committed results. Recorded changes; no registered result and no pre-set reading changes:
    - *P2 wording.* The report, deck, `RESULTS.md`, briefing and walkthrough said the interval for the mean change
      (−0.218 to 0.002) was too wide to exclude modest rises. That read the interval backwards: it lies almost
      entirely below zero, so there is no evidence of a rise and rises larger than a few hundredths are unlikely. The
      qualifications are that a bootstrap over 13 mice under-covers and that the upper end depends on session
      `4d8c7767` (−0.205 to 0.032 without it; `results/a19/sensitivity.json`). The residual-data interval (−0.154 to
      −0.038) lies below zero; the test was one-sided for a rise, so this is reported, not tested. No equivalence test
      was added, since any margin chosen now would be chosen after seeing the data.
    - *Note 5 corrected.* The AI-agent diagnostic changed only what the readout subtracts; the latent model's
      loadings were fitted with the previous-side input present, so that input had already absorbed the
      prior-related activity it predicts (41% of the prior's variance) before any latent was fitted. The diagnostic
      cannot detect this, so the explanation is **untested**, not "not supported". The readout also discards the
      per-latent dynamics, by design (smoothing could integrate stimulus memory into an apparent prior), so the test is
      close to factor analysis with regressors. Refitting without that input was not done (constraint: no further
      latent-model experiments).
    - *Drift wording.* "The simulation does not reproduce the recordings' horizon pattern" is replaced by "consistent
      with the recordings, not established": the recordings' horizon change is −0.099 as a mouse mean, −0.041 as a
      median and +0.001 under the Lasso decoder (A16), a range that includes the simulated median (+0.015), and the
      no-prior conditions match the recorded profile about as well (note 7). The pre-set reading stays
      "intermediate".
    - *Simulation intervals.* The report's simulation figure and table, and the `RESULTS.md` table, now use 95%
      intervals that resample the 16 tasks rather than the 32 seeds (seeds come in correlated pairs). New stage
      `task_intervals` of `scripts/26_sim_A18.py` writes `results/a18/task_intervals.csv` from `sim_seeds.csv` only
      (no simulation was run). Quoted intervals that changed: capture without drift 41% [31, 50] (was [33, 48]);
      memory alone 0.078 [0.012, 0.154] (was [0.019, 0.132]).
    - *Report Figure 2a.* Its dotted full-population line was the mouse mean (0.159), which one session inflates. It
      now shows the session median (0.108), the summary A19 fixed in advance for post hoc reference values. The median
      over mice (0.176) was also computed and not used: choosing it after seeing it would be choosing by value.
    - *Report structure.* Retitled "Long Prediction Horizons Do Not Isolate the Block Prior in Mouse Secondary Motor
      Cortex"; "pre-specified" replaces "pre-registered" in the report (the repository keeps its terms); three status
      labels (pre-specified, exploratory, post hoc); amendment codes kept to the appendix; abstract shortened; the
      sensitivity analysis and the latent model moved to the appendix with one main-text sentence each; one
      sentence relating the 20 November freeze to the 23 November tag; a band-pass objective mentioned as future work
      only (not run).
