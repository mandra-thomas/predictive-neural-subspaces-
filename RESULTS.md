# Results summary: prediction horizon and the content of MOs population subspaces

Status as of 2026-11-16. All numbers are from commit `c6893b1` or later, after amendment D10 (see "What changed after
the first run"). Primary analysis at d = 5. Tables live in `results/stats/d5/`. Results with trial-locked responses
removed are in `results_residual/stats/d5/`. Robustness checks are in `results*/robustness/`. Figures are in
`figures/` and `figures/residual/`.

## One-paragraph summary

The proposal hypothesized that predicting further ahead would pull out different population dimensions:

- long horizons (30 s) would isolate a slow subspace carrying the Bayes-optimal block prior;
- short horizons (0.5 s) would isolate a fast subspace carrying sensorimotor variables.

In secondary motor cortex (MOs: 16 sessions, 13 mice), the second half holds only in a weaker form, and the first
half does not hold. Long-lag and short-lag subspaces do differ, and the long-lag subspaces carry less current-stimulus
information. But the 30 s subspaces do not carry the block prior, at any lag. Instead they track time in the session
(held-out R-squared 0.84), and they are no more reproducible across session halves than random subspaces matched to
the data covariance. The most predictable direction at every horizon is the same slow, drift-like mode. That mode
sits almost entirely inside the 0.5 s subspace too.

The block prior *is* present in the full population (it replicates Findling et al.). It lives in directions that are
neither high-variance nor predictable from the population's own past.

## Data and design

| Item | Value |
|---|---|
| Region | MOs (Beryl). Chosen by the frozen census rule: the region with the largest Findling prior effect among those with at least 15 eligible sessions from at least 8 mice. MOp had 14 eligible sessions. |
| Sessions / mice | 16 / 13 (sessions averaged within each mouse before every test) |
| Units per session | 22 to 128 (median 48.5), good units only, at least 0.1 Hz |
| Trials per session | 413 to 700 (median 534), all passing the BWM trial mask |
| Median trial duration | 3.9 s |
| Lags | 0.5, 2, 8 and 30 s, on 0.5 s bins of sqrt spike counts |
| Subspace | lagged reduced-rank ridge regression, d = 5 (3 and 10 as sensitivity), one cross-validated ridge penalty per session |
| Null | 200 pseudo-sessions with re-drawn block structure, shared across lags so that lag contrasts get a paired null |
| Tests | one-sided Wilcoxon across mice, Holm over the three pre-registered primary tests |

**Prior gate (Findling replication on the full population).**

| Gate statistic | Value |
|---|---|
| Median null-corrected prior R-squared | 0.064 |
| Sessions individually significant | 5 of 16 |
| Fisher-combined p | 1.2e-5 |

The prior is decodable from MOs, so the GO criterion was met.

## Primary results (pre-registered)

| Test | Holm p (raw) | Holm p (trial-locked residuals) | Mice in predicted direction |
|---|---|---|---|
| P1 geometry: cross-lag angle exceeds both same-lag floors | 0.0026 | 0.013 | 11 of 13 (10 of 13) |
| P2 prior: corrected prior decoding rises from 0.5 s to 30 s | 0.89 | 0.996 | 4 of 13 (3 of 13) |
| P3 current side: corrected decoding falls from 0.5 s to 30 s | 0.0061 | 0.0051 | 10 of 13 (11 of 13) |

### P1: geometry

The mean principal angle between subspaces fit on opposite session halves was:

| Comparison | Mean angle | First (smallest) angle |
|---|---|---|
| 0.5 s vs 0.5 s (same lag) | 59.7° | 32.8° |
| 30 s vs 30 s (same lag) | 69.1° | 50.0° |
| 0.5 s vs 30 s (cross lag) | 71.9° | 52.6° |
| Covariance-matched random chance | 67.8° | 46.7° |

The cross-lag angle exceeds the 0.5 s floor by 12.7° (95% CI 10.2 to 15.1) and the 30 s floor by 3.6° (2.2 to 4.9).
Most of the test's strength comes from the short-lag side. The 30 s split-half floor is itself at chance, so "cross
exceeds the 30 s floor" compares against a noise-level baseline. The result also depends on which basis is compared.
It holds for the readout basis (the space whose activity predicts the future) but not for the loading basis (the space
of predicted activity), where p = 0.96.

### P2: prior

The paired, null-corrected change in prior R-squared from 0.5 s to 30 s was −0.099 (95% CI −0.218 to +0.002). After
removing trial-locked responses it was −0.093 (−0.154 to −0.038), which runs significantly the *wrong* way.

Per subspace, the null-corrected prior R-squared was:

| Subspace | Raw | Residual |
|---|---|---|
| RRR 0.5 s | 0.054 | 0.053 |
| RRR 2 s | −0.027 | −0.017 |
| RRR 8 s | −0.057 | −0.034 |
| RRR 30 s | −0.046 | −0.038 |
| PCA | 0.013 | 0.041 |
| Random (covariance-matched) | −0.030 | 0.004 |

None of the per-lag Fisher-combined session p-values reaches 0.05 in the raw data. The best is 0.12, at 30 s. The
part of the 30 s subspace orthogonal to the 0.5 s subspace carries a prior R-squared of 0.005.

### P3: current stimulus side

On nonzero-contrast trials, the null-corrected AUC drops by 0.061 (0.028 to 0.095) from 0.5 s to 30 s. The drop is
0.063 (0.032 to 0.097) after residualization. This holds at d = 10 but not at d = 3 (Holm p = 0.11).

Important nuance: the 0.5 s subspace is not *specialized* for the stimulus. Its corrected AUC (0.218) equals that of
a covariance-matched random subspace (0.218) and is below PCA (0.240). The effect is that long-lag subspaces lose
stimulus information (0.144 to 0.161), not that short-lag subspaces gain it.

## Secondary results

**Nesting.** The 0.5 s subspace contains 92% (90 to 94%) of the 30 s subspace's leading direction. The reverse
figure is 76%. The slow mode is shared rather than split off.

**The slow mode tracks session time.**

| Subspace | Elapsed-time R-squared (raw) | Elapsed-time R-squared (residual) |
|---|---|---|
| RRR 30 s | 0.84 | 0.73 |
| RRR 0.5 s | 0.82 | 0.72 |
| PCA | 0.80 | 0.70 |
| Random (covariance-matched) | 0.64 | 0.56 |

The proposal's drift flag fires in 14 of 16 sessions (12 of 16 after residualization). The directions unique to the
30 s subspace carry almost none of it: R-squared 0.12 raw, 0.03 residual.

**Unit turnover.** In 14 of 16 sessions, at least one unit is effectively silent for an entire fifth of the session
(118 of 842 units overall). This is the classic signature of probe drift or sorting instability. It is also what
exposed the bug fixed in D10.

**Estimator check.** These are held-out R-squared values for predicting future activity.

| Method | 0.5 s lag | 30 s lag |
|---|---|---|
| Full-rank ridge | 0.371 | 0.178 |
| Lagged RRR, d = 5 | 0.246 | 0.176 |
| PCA, d = 5 | 0.232 | 0.152 |
| Random, d = 5 | 0.163 | 0.121 |

RRR beats PCA at every lag (by 0.011 at 0.5 s up to 0.022 at 30 s; all p at most 0.005). At 30 s, five dimensions
recover 96% of full-rank predictability, so long-horizon predictable structure is very low-dimensional. After
removing trial-locked responses, RRR's margin over PCA shrinks to 0.005 to 0.008, and its CIs include 0. Much of
what makes the predictive objective better than plain variance at 0.5 to 30 s is task structure that recurs every
trial.

## Robustness (post hoc, not pre-registered)

| Check | P1 | P2 | P3 |
|---|---|---|---|
| Leave-one-mouse-out, worst Holm p (raw) | 0.005 | 0.95 | 0.012 |
| Leave-one-mouse-out, worst Holm p (residual) | 0.027 | 0.998 | 0.010 |
| Drop DY_014 (raw) | 0.005 | 0.87 | 0.005 |
| d = 3 (Holm) | 0.032 | 0.21 | 0.11 |
| d = 10, 10 mice (Holm) | 0.003 | 0.88 | 0.006 |

**DY_014** is the low outlier in Fig 1b. Its readouts are dominated by one cluster firing at 141 Hz with a lag-1
autocorrelation of 0.95 (the session median is 0.39). That cluster loses about 40% of its rate in the last quarter of
the session, along with several other units. This looks like a multi-unit or noise cluster plus a drift event. The
cluster makes all its subspaces unusually reproducible. The animal's effects point the same way as everyone else's,
and dropping it changes nothing material.

## What changed after the first run (amendment D10)

While diagnosing two sessions with held-out R-squared ≈ 0 for every method, I found a bug.

- **Cause.** The z-score SD floor (1e-3) let a unit that was silent across a training fold but active in its test
  fold reach a held-out z-variance of about 10⁵. That one unit made up more than 99% of the pooled test variance.
- **What it corrupted.** The cross-validated R-squared and, through it, the session ridge penalty.
- **Fix.** The floor is now the SD of a unit firing exactly at the 0.1 Hz inclusion threshold (0.218).
- **Scope.** The fix changes no unit's whole-session z-score (0 of 842 units are floored). It changed the chosen ridge
  penalty in 2 sessions in the raw run and 4 in the residual run.
- **Effect on results.**
  - Raw primary p-values are unchanged.
  - The residual P1 moved from 0.048 to 0.013.
  - The estimator-check numbers changed. The earlier "RRR beats full-rank ridge at 30 s" (ratio 1.13) was an artifact
    of the bug.
- **Records.** Pre-fix outputs are kept in `results*/prefix_D10/`. The change is logged in `AMENDMENTS.md` and
  `ANALYSIS_LOG.md`.

## How strong is this, and is it interesting?

**Strongest result: the negative one.** "The block prior does not move into long-horizon subspaces" survives every
check: residualization, all three values of d, and every leave-one-mouse-out refit. Its upper confidence bound
(+0.002) is about 3% of the full-population prior effect, so a meaningful rise is ruled out, not just undetected. The
power caveat is that the prior is weak in MOs to begin with (R-squared about 0.06). The study could detect a lag
effect of that size, but not a subtle redistribution.

**Moderately strong: P3.** It is robust to residualization and leave-one-out, but sensitive to d (fails at d = 3), and
its interpretation is weaker than the hypothesis: long lags *lose* the stimulus; short lags are not specialized for it.
That is close to what you would expect from evoked responses lasting under a second, so on its own it is not
surprising.

**Weakest of the three: P1.** It is statistically significant but scientifically thin. Most of it is "short-lag
subspaces are reproducible and long-lag ones are not". It depends on the basis (fails for the loading basis), and the
long-lag side of the contrast is only 2 to 4°.

**What is interesting.**

1. **Predictable structure on 2 to 30 s horizons in MOs is about one-dimensional, shared across horizons, and indexes
   time in session rather than the latent variable the mouse must track.** The block prior is decodable from the
   population, yet it is not part of the population's predictable dynamics. One reading is that the prior is carried
   as a small, static modulation rather than as a slow dynamical mode. Methods that rank dimensions by variance or by
   predictability (PCA, lagged RRR, slow-feature or dynamical-components analysis) would then systematically miss it.
2. **The long-horizon readout is not stable across the session.** The 30 s subspaces from the two halves are only as
   aligned as random covariance-matched subspaces, and the cross-lag angle is no smaller. A stable slow cognitive
   variable (for example the engagement or impulsivity "slow drift" of Cowley et al. 2020) would be expected to have a
   reproducible readout. A drift whose direction depends on which units are turning over would not. Together with the
   unit turnover in 14 of 16 sessions, this favours probe or sorting drift over a stable internal state, though it does
   not prove it.
3. **A methodological lesson for predictive-subspace methods on chronic recordings.** Long-horizon objectives
   preferentially recover nonstationarity. Elapsed-time decoding, pseudo-session nulls, split-half reliability against
   a covariance-matched chance level, and care with fold-wise normalization (the D10 bug) are all needed to avoid
   reading drift as cognition.

**Overall.** This is a carefully controlled negative result with a clear mechanism, which suits a course project and
gives a clean story. It is not, on its own, a publishable discovery. It is one region and 13 mice, and the main
positive findings are either expected (P3) or modest (P1). The most interesting open question is item 2: is the slow
mode an artifact or a behavioural state? A small follow-up could answer that (see the next steps below).

## Limitations to state in the talk and report

- One region (MOs), 13 mice. The smallest attainable one-sided Wilcoxon p with 13 mice is 1.2e-4.
- Splitting sessions into halves confounds reproducibility with nonstationarity. A drifting signal looks unreliable
  partly because the halves differ in time.
- The drift flag cannot separate electrode drift from slow internal-state change.
- The 30 s lag on sessions of about 60 minutes leaves only about 120 non-overlapping windows, so long-lag fits are noisy
  by construction.
- One analysis decision (D10) was made after results were seen. It is a bug fix and is reported transparently.

## Pilot: is the slow mode recording drift or brain state? (amendment A12, run on PACE ICE)

The slow mode is the leading direction of the 30 s subspace, followed through the session in 30 s windows. Three
tests were written down before any probe-motion or pupil data was downloaded, along with the rule for reading them.

**Test 1: remove drifting units.** I kept only units firing at least 0.1 Hz in every fifth of the session. That left
13 of 16 sessions from 12 mice; three sessions fell below 20 stable units. Refitting from scratch, the 30 s subspace
still decodes elapsed time with an R-squared of 0.77 (originally 0.84; PCA 0.72, random 0.50). The drift flag still
fires in 12 of 13 sessions, and the 0.5 s subspace still contains 91% of the slow direction. The primary results are
unchanged:

| Primary test | Holm p, stable units | Holm p, original |
|---|---|---|
| Geometry | 0.002 | 0.003 |
| Prior | 0.97 | 0.89 |
| Current side | 0.027 | 0.006 |

Units entering and leaving the recording do not create the slow mode. By the pre-registered rule, it "survives".

**Test 2: probe motion.** IBL's spike-sorting motion estimate for these insertions is small: the median range across
a session is 7.9 micrometres, from 1 to 19 at the extremes. The slow mode correlates strongly with each session's own
motion trace (mean absolute correlation 0.74). But it correlates just as strongly with *other* sessions' motion
traces, so the session-permutation correction is −0.006 (p = 0.39). After removing linear trends from both, the
correction is +0.062 (p = 0.14). The slow mode follows probe motion no more than any slowly trending signal would.

**Test 3: pupil.** 15 sessions had usable pupil traces. The real correlation (mean absolute 0.35) is again no larger
than with other sessions' pupil traces: correction −0.001 (p = 0.42), and −0.004 (p = 0.55) after detrending.

**Reading.** The pre-registered overall reading is "mixed or undetermined". The mode survives removal of drifting
units, but neither probe motion nor pupil explains its session-specific shape. There is an important limitation,
visible only now. In most sessions the slow mode is close to a straight ramp: its correlation with elapsed time has
a median of 0.96. Any two slowly trending signals correlate about equally well with a ramp, so a session-permutation
test has little power to tell candidate causes apart unless they produce different *shapes*. What the pilot does rule
out is the simplest artifact story, units dropping out. Recording-side causes that the motion estimate misses remain
possible, as do slow state changes that pupil doesn't capture, such as satiety or task engagement. Telling these
apart needs signals that sometimes reverse within a session, for example engagement states, or sessions where the
mode is not a ramp. The literature review (`reports/Slow neural modes literature review.md`) lays out those analyses.

## Possible next steps

1. **Stationarity control.** Done (amendment A12, above). The slow mode survives.
2. **Engagement and satiety as competing explanations.** IBL publishes a per-trial engagement probability
   (`int-brain-lab/engage`). Sessions where engagement rises and falls rather than declining steadily are the only
   ones that can separate state from a generic ramp. Cumulative reward is a proxy for satiety.
3. **Artifact checks the motion estimate cannot make.** Per-unit spike amplitude over time, and the slow mode
   recomputed from sorting-free multi-unit activity per depth bin.
4. **Second region.** Relax the census rule to 14 sessions to admit MOp. This would be an amendment.

## Suggested slide outline (Nov 30)

1. Question: does prediction horizon select what a neural subspace encodes?
2. Data and design: IBL BWM, MOs, lagged RRR at four horizons, pseudo-session nulls, pre-registration.
3. Sanity check: the prior is in MOs (Findling replication gate).
4. Estimator check (Fig 3): RRR beats PCA; long horizons are low-rank.
5. Geometry (Fig 1): short-lag subspaces are reproducible; 30 s subspaces are at chance; modest cross-lag difference.
6. Content (Fig 2): stimulus fades with lag; the prior never rises; elapsed time dominates.
7. Nesting and orthogonal complements (Fig S1): one shared slow mode.
8. Controls: trial-locked residuals, d sensitivity, leave-one-mouse-out.
9. Interpretation: predictable dynamics reflect drift, not latent task state; the prior is a small static code.
10. Limitations and next steps.
