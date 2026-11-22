# Amendments to the proposal (pre-registered)

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
