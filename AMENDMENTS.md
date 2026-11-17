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
