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
