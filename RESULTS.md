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

## Second pilot: what produces the slow mode? (amendment A13, run on PACE ICE)

This pilot used three lines of evidence that do not depend on matching one ramp to another. The tests and the rule for
reading them were committed before the engagement table or the full spike files were downloaded.

**Multi-unit activity, independent of spike sorting.** Every detected spike in the MOs depth span, whatever cluster or
quality label it was given, was binned into 50 µm depth channels. The unchanged pipeline was then refit with those
channels in place of units (15 sessions, 12 mice; one session had too few channels).
- The slow mode reappears almost exactly. The median correlation between the multi-unit slow mode and the unit-based
  one, over 30 s windows, is 0.96.
- The 30 s subspace decodes elapsed time with an R-squared of 0.74 (0.84 for units), and the drift flag fires in all
  15 sessions.
- So the mode is not created by how spikes were assigned to clusters.
- In this representation the stimulus-side effect disappears (Holm p = 1.0), which is expected when each channel mixes
  neurons with opposite preferences. The geometry effect remains (p = 0.010).

**No signature of a rigid probe shift.** If the probe moved as a whole, the multi-unit loadings should follow the
slope of the depth profile. They don't: the mean absolute rank correlation is 0.19, and the combined p over 15
sessions is 0.25. This agrees with IBL's small motion estimates (median about 8 µm).

**Spike amplitudes change, in step with the mode.** Spike amplitudes are far from stable over a session:
- 59% of units have a consistent amplitude trend (absolute rank correlation with time of at least 0.5);
- the median unit's amplitude changes by 15.6% in absolute value between the first and last fifth of the session
  (a descriptive measure, not pre-registered);
- the change is more often a decline (median trend −0.26; a quarter of units lose 21% or more).

The pre-registered test asked whether units whose amplitude shrinks are the units whose rate falls along the slow
mode. They are: across units within a session, the loading and the amplitude trend are positively correlated (mean
Fisher z 0.15, one-sided p = 0.029 across 13 mice). Adaptation at high rates would produce the opposite sign. This is
the signature of spikes dropping below the detection threshold as their amplitude falls.

Only 5 sessions (5 mice) kept 20 or more units that are stable in both rate and amplitude. In those, elapsed-time
R-squared falls to 0.49 and the drift flag fires in 3 of 5 sessions, which the rule reads as "intermediate". With 5
sessions this is suggestive at best.

**Engagement and satiety beyond the trend.** After removing a quadratic trend in time from each signal, the slow mode
is not tied to IBL's per-trial engagement probability (session-permutation p = 0.19) or to cumulative rewards
(p = 0.12). Two secondary hints are weak and inconsistent:
- In the 11 sessions where engagement genuinely fluctuates, p = 0.049 (uncorrected), but the sign of the relationship
  is not consistent across mice (p = 0.95).
- The satiety relationship leans positive (sign-consistency p = 0.068).

**Reading.** The pre-registered rule outputs "sorting artifact". It reaches that label through its second branch (the
amplitude-stable refit is not "survives", and the amplitude-loading test is significant). The label fits the evidence
poorly, though, because the most direct sorting test, multi-unit activity, says the mode is *not* a sorting
artifact. The rule did not anticipate that amplitude loss could act through spike *detection* rather than cluster
assignment.

What the three lines of evidence support together:
- the slow mode is a real, recording-level change in detected spiking;
- it is not a cluster-assignment error and not a rigid shift of the probe;
- it goes with gradually shrinking spike amplitudes in the units that carry it;
- the most consistent explanation is a slow change at the electrode–tissue interface, such as tissue settling after
  an acute insertion or local non-rigid movement, which costs spikes at the detection threshold;
- evidence for engagement or satiety is weak.

This is a recording-side explanation, but not the "spike-sorting artifact" the label suggests. It cannot fully
exclude a physiological contribution to amplitude change.

**Correction after the third pilot (A14, below).** The "detection loss at the electrode–tissue interface" reading above
did not hold up. A14 found three things:
- the moment-to-moment amplitude-rate coupling has the opposite sign to detection loss;
- correcting every unit for its own amplitude change, even maximally, leaves the mode almost intact;
- amplitude change is not concentrated early in the session.

The 2a correlation is real but small (a rank correlation of about 0.15 across units).


## Third pilot: does amplitude loss account for the slow mode? (amendment A14, run on PACE ICE)

**Question and why the obvious test fails.** A13 left open whether shrinking spike amplitudes are enough to produce
the slow mode. The obvious correction would regress each unit's rate on its amplitude over time and remove the fit.
That test cannot fail: both quantities are near-ramps, so it removes any ramp in any unit whose amplitude drifts,
whatever the cause. The registered design (`f3008e7`, committed before any of it was computed) has three parts:
- it estimates the coupling only from co-fluctuations around the time trend;
- it brackets the answer between a conservative and a maximal correction;
- it tests whether amplitude change is concentrated early in the session.

A local smoke run exposed two weaknesses in the design, so two post hoc checks were added and recorded before the ICE
run. ICE job 7241313 covered all 16 sessions and 13 mice.

**Part 1: coupling beyond the trend.** Each unit gets a Poisson regression of its spike count in each 30 s window on
its relative spike amplitude in that window, with a quadratic in time as nuisance terms. Spike-detection loss predicts
a positive coefficient: smaller spikes, fewer detected. The coefficient is negative instead:
- the mean across animals is −1.54 (median −1.43), and only 27% of units are positive;
- the one-sided p for a positive coupling is 0.99;
- with a degree-5 time polynomial it is −1.92 (p = 0.995).

A coefficient of −1.5 means that in a window where a unit's spikes are 10% smaller than usual, it fires about 16% more.

The known cause of this sign is that spikes shrink during bursts and fast firing, an effect of rate on amplitude. The
post hoc check therefore used only isolated spikes, each at least 50 ms after the same unit's previous spike (median
47% of spikes). The coupling is still negative (mean −1.32, median −0.97, p = 0.98). Burst attenuation does not hide a
positive detection coupling.

**Part 2: amplitude-corrected refits.** Each unit's counts were multiplied, window by window, by a factor undoing its
estimated amplitude effect, clipped to between half and double. The full pipeline was then refit. The main measure is
how well the 30 s subspace decodes elapsed time, relative to the original R-squared of 0.84. The "residual ramp"
column needs no refit: it projects the corrected data onto the original slow direction and gives the fraction of the
original slope that remains.

| Correction | What it uses | Elapsed-time R² (fraction of original) | Residual ramp | Reading |
|---|---|---|---|---|
| Conservative (registered) | session median of the fluctuation coupling | 0.85 (101%) | 1.00 | survives |
| Maximal (registered) | each unit's coupling with no time terms | 0.80 (95%) | 0.86 | survives |
| Slow-maximal (post hoc) | each unit's coupling on a 5.5 min smoothed amplitude | 0.78 (93%) | 0.85 | survives |

The conservative correction does nothing useful because its coefficient is negative. The informative rows are the
maximal ones. Removing from every unit everything that moves with its own amplitude takes away about a seventh of the
ramp. The 30 s subspace still decodes elapsed time at 93 to 95% of its original level, and the drift flag fires in
14 of 16 sessions. The primary tests are unchanged in every corrected copy:
- geometry, Holm p between 0.0004 and 0.004;
- prior, 0.63 to 0.73;
- current side, 0.006 to 0.013.

**Part 3: timing.** For units with a consistent amplitude trend, an index compares the change in the first third of
the session with the change in the last third. It runs from −1 (all late) to +1 (all early). Settling after insertion
predicts early change. The observed index is −0.12 (p = 0.75 for "early"): if anything, the change is later. The slow
mode itself is almost exactly linear (index −0.02).

**Reading.** The registered rule outputs "amplitude cannot account for the mode", because even the maximal correction
"survives". All three parts agree:
- the coupling has the wrong sign, even with isolated spikes;
- correction removes at most about 15% of the ramp;
- the timing does not match settling.

The A13 link between amplitude trend and slow-mode loading is real but small. It is not the mechanism.

**Caveats.**
- Correction factors were clipped to between 0.5 and 2. About a third of units hit the clip in at least one window,
  so a unit that lost more than half its detected spikes to amplitude would be under-corrected.
- Kilosort amplitudes are template scalings, not calibrated voltages, and the detection threshold acts on whitened
  data.
- The task starts some minutes after insertion, so settling that ended before the task is invisible here.

**Where this leaves the slow mode.** Each candidate tested so far explains little of it:
- unit turnover (A12);
- spike-sorting assignment and rigid probe motion (A13);
- spike-amplitude change and detection loss (A14);
- pupil, engagement and satiety beyond the shared trend (A12, A13).

What remains is a slow, close-to-linear change in MOs firing that tracks time in the session and survives every
recording control applied. That makes a neural origin more plausible than before, for example slow arousal or
neuromodulatory drift, fatigue, or elapsed-time coding. It is not established. Behavioural comparisons are limited by
the ramp shape, and unmeasured recording factors remain possible.

## Possible next steps

1. **Stationarity control.** Done (amendment A12, above). The slow mode survives.
2. **Engagement, satiety, amplitude and multi-unit checks.** Done (amendment A13, above).
3. **Amplitude-corrected slow mode and early concentration.** Done (amendment A14, above). Amplitude cannot account for
   the mode.
4. **Spontaneous-activity epochs** (not yet registered). IBL sessions include spontaneous periods outside the task,
   which the current analysis excludes. Ask whether the slow mode continues through the post-task spontaneous period
   (not tied to doing the task) or resets or flattens there (task-linked).
5. **Second region.** Relax the census rule to 14 sessions to admit MOp. This would be an amendment.

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
