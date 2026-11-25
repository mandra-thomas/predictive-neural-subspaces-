# Results summary: prediction horizon and the content of MOs population subspaces

**Status as of 2026-11-25.** The main analysis was completed on 16 November (commit `c6893b1`, after the D10 bug fix)
and has not changed since. The exploratory pilots ran on 17 November (A12) and 21 to 22 November (A13 to A15), and
the post hoc checks (A16) on 22 November (commit `439e7dc`). On the `pilot-timescale-fix` branch: the post hoc
timescale follow-ups (A17 parts 0 to 2) ran on 23 November; the calibrated simulation (A18 part A) and the latent-model
gate on simulated sessions (A18 part B, which failed and stopped that line) on 24 November; a post hoc sensitivity
analysis for one session (A19) on 25 November. A17 part 6 was not done and is dropped. On 25 November six AI-agent
reviews (Claude subagents; not independent human review) audited the repository; the corrections they led to are
recorded at the end of `AMENDMENTS.md` and applied below. The report (`report/main.tex`) is being rewritten to
include A17 to A19; until then it is authoritative only for the registered analysis and A12 to A16. Numbers for the
registered analysis were re-checked against the result files on 2026-11-22; numbers from A17 to A19 were re-checked
by an AI-agent number audit on 2026-11-25.

Primary tables live in `results/stats/d5/` (d = 3 and d = 10 in `results/stats/d3/` and `d10/`). Results with
trial-locked responses removed are in `results_residual/stats/d5/`. Robustness checks are in `results*/robustness/`.
Pilot and post hoc summaries are in `results/pilot/`, `results/a13/` to `results/a16/`, with the refits on modified
data copies in the matching `results_*/` folders (see `README.md` for where each comes from). Figures are
generated into `figures/` and `report/figures/` (both gitignored; rebuilt by the figure scripts).

## How to read this file

**Averaging.** The primary tests average sessions within each mouse first and then compare the 13 mouse values; the
report and slides use these **mouse means** throughout, and so does `matrix.csv`. Some earlier versions of this file
quoted **session means** (a plain mean over the 16 sessions), which differ slightly because three mice contribute two
sessions each. Every table below says which it uses; where both appear they are labelled. Intervals are 95%
percentile bootstraps over mice. With 13 mice these under-cover, so they are descriptive.

**Corrected scores.** For variables the experimenter generated (the block prior, previous and current stimulus side),
each decoding score is compared with the same decoder applied to 200 pseudo-sessions, which are block sequences
redrawn from the task's own generative process. The corrected score is the real score minus the median pseudo-session
score. A corrected prior $R^2$ of 0.054 therefore means the real score exceeds the null median by 0.054 on that
decoder's scale; it is not 5.4% of variance explained. Raw subspace prior $R^2$ is negative with contiguous folds
(session means from $-0.126$ at 0.5 s to $-0.287$ at 30 s; PCA $-0.108$), which is why only corrected scores are
interpreted.

**Elapsed-time decoding.** Elapsed time is decoded from each subspace's projected activity, with 20 contiguous chunks
of the session assigned round-robin to five folds. Because the subspaces are fit on the whole session and every test
chunk lies between training chunks, elapsed-time $R^2$ measures how much of a fitted representation's activity varies
smoothly with session time, interpolated within the session. It is not end-to-end held-out prediction.

**Inference tiers.** *Pre-registered* means written in a timestamped commit (in the author's repository, not a public
registry) before the relevant data were analysed. That covers the three primary tests, the deviations D1 to D9, the
additions A1 to A11 and the first pilot A12. A13 to A15 are *prospectively documented exploratory follow-ups*: each
design and reading rule was committed before its data were analysed, but after the 20 November analysis freeze. D10
(a bug fix), P1h (robustness), the two A14 post hoc checks, A16, A17, A18 and A19 are *post hoc*: designed after the relevant results
were seen. *AI-agent review* means a review by Claude subagents; no independent human review has taken place. Nothing outside the three primary tests is corrected for multiplicity. `AMENDMENTS.md` has an index of
every entry.

## Summary

The proposal hypothesized that predicting further ahead would pull out different population dimensions: long horizons
(30 s) would isolate a slow subspace carrying the Bayes-optimal block prior, the ideal observer's running estimate of
which block the task is in, and short horizons (0.5 s) would isolate a fast subspace carrying sensorimotor variables.

In secondary motor cortex (MOs: 16 sessions, 13 mice) the prior half of the hypothesis was not supported and the rest
held only in qualified form. The prior is decodable from the full population with the registered decoder, as in
Findling et al. (whether that reflects a belief about the block or memory of recent stimuli is not separable here;
see the A18 section), but its decoding shows **no detectable rise with horizon**: not under the registered decoder, and not in post hoc checks with
a second decoder or after removing the session trend. Subspace-level prior estimates sit at the noise floor and their
ordering depends on the decoder. Long-lag subspaces carry less current-stimulus information, but because they lose it,
not because short-lag subspaces specialize in it. The long- and short-lag subspaces differ geometrically, but only in
one of the two bases tested.

What dominates every five-dimensional summary is a slow **session-time mode**: a population direction whose activity
changes steadily over the session. It is present in the 30 s subspace (elapsed-time $R^2$ 0.84), and nearly as much in
the 0.5 s subspace (0.82), in PCA (0.80) and even in covariance-matched random subspaces (0.64). Its time course is
consistent across sessions, but which units carry it appears to change between session halves (post hoc). Of the
recording causes tested, none accounts for most of it; the strictest unit filter is the main unresolved challenge.
One candidate explanation for why the hypothesis failed, tested only partly (A18), is variance ranking: lagged RRR keeps the
directions that predict the most variance, and a large slow signal wins those dimensions before a small one like the
prior. The registered P2 test was also weak: the interval for the mean change (−0.218 to 0.002) is wider than the prior's
own full-population reference, so modest rises are not excluded.

The post hoc timescale follow-ups (A17) sharpen this. The prior's own memory is short: its autocorrelation timescale
is about 12 trials counted per trial (67 s, or about 17 trials, counted per 0.5 s bin), and only about 1% of its variance is still predictable 2 minutes ahead (median $\rho_\pi^2$), whereas
a session-long ramp stays predictable at every lag tested. Under a simple two-component picture (each component's
predictable variance is its variance times its squared autocorrelation), the prior's share relative to such a drift
only falls with lag; that is a heuristic, not a property of the RRR objective. Extending the lags to 4 minutes on
drift-removed data selects no prior, and the small prior signal in the subspaces is flat across lags and about what
PCA carries. A calibrated simulation (A18 part A) then showed that a prior of the recorded strength *is* picked up by
the 30 s subspace when there is no drift, and that drift of the recorded strength removes the 30 s subspace's prior
score (and the 0.5 s, PCA and random ones) while the full population still decodes it. It does not reproduce the
recorded fall from 0.5 s to 30 s: at the recorded drift the horizon change is near zero (median +0.015, positive in 9
of 16 tasks), so the pre-set reading is "intermediate". Drift is a sufficient explanation for the loss at 30 s in this
model, not an established cause in the recordings, and the A17 outcome table had no row for an intermediate reading,
so framing the project around drift is a post hoc choice. Stimulus memory: if there were no block prior and the population only remembered the last stimulus as strongly as the recordings require (the recorded previous-stimulus decodability, one-trial memory), the corrected prior score would be +0.078 (12 of 16 tasks, p = 0.038), 72% of the recordings' session median. A
small memory trace of the size fitted alongside the prior adds nothing on its own (−0.012). So the recorded prior
score cannot by itself separate a block prior from memory of recent stimuli, a known concern rather than a new
finding. One session
(SWC_038, `4d8c7767`) has an implausible corrected score (1.59); A19 shows it does not drive the registered P2 result
but does drive the earlier mouse-mean reference of 0.159 (0.101 without it).

## Data and design

The table lists the fixed design. Session and trial counts come from `results/gate/*.json`; the median task epoch and
trial duration from `results/subspaces/*_d5.json`; the census from `data/meta/region_counts.csv`.

| Item | Value |
|---|---|
| Region | MOs (Beryl parcellation). The frozen census rule picks, among candidate regions with at least 15 sessions from at least 8 mice meeting inclusion, the one with the largest published prior effect. MOs was the only eligible region (MOp had 14 sessions from 12 mice, VISp 10 from 8, ACAd 4 from 4) |
| Sessions and mice | 16 sessions from 13 mice; sessions are averaged within each mouse before every test |
| Units per session | 22 to 128 (median 48.5; 842 in total), IBL good units firing at least 0.1 Hz over the task epoch |
| Trials per session | 413 to 700 (median 534), all passing the BWM trial mask |
| Task epoch and trial duration | median about 66 minutes; median trial duration 3.9 s |
| Lags | 0.5, 2, 8 and 30 s, on 0.5 s bins of square-root spike counts, z-scored per unit |
| Subspace | lagged reduced-rank ridge regression with 5 dimensions (3 and 10 as pre-registered sensitivity analyses), one cross-validated ridge penalty per session shared by all lags |
| Null | 200 pseudo-sessions, shared across lags so that lag contrasts get a paired null |
| Tests | one-sided Wilcoxon signed-rank across mice, Holm-corrected over the three primary tests |

Lagged reduced-rank ridge regression (RRR) finds the rank-$d$ linear map from activity now to activity $\Delta$
later. For z-scored population vectors $x_t$, with $X$ and $Y$ holding $x_t$ and $x_{t+\Delta}$,

$$
\hat B_\Delta = \arg\min_{\operatorname{rank}(B)\le d} \lVert Y - XB \rVert_F^2 + \lambda \lVert B \rVert_F^2 .
$$

The *readout basis* is the $d$-dimensional space of current activity that the fit uses to predict the future, and the
*loading basis* is the space of predicted activity. Because the loading basis holds the directions along which the fit
predicts the most variance, the subspace is ranked by predicted variance.

**Prior gate (full population, Findling et al.'s decoder).** Before any subspace analysis, the prior was decoded from
the full MOs population with the Findling decoder (Lasso, nested interleaved cross-validation) against the
pseudo-session null. The table gives the gate statistics from `results/gate/summary.json`.

| Gate statistic | Value |
|---|---|
| Median null-corrected prior R-squared (session median) | 0.064 |
| Mouse mean of the same | 0.070 |
| Sessions individually significant | 5 of 16 |
| Fisher-combined p | 1.2e-5 |

The prior is decodable from MOs, so the pre-registered GO criterion was met.

## Primary results (pre-registered)

The three primary tests are: P1, the mean principal angle between the 0.5 s and 30 s subspaces (fit on opposite
session halves) exceeds the same-lag split-half angle at both lags; P2, corrected prior $R^2$ rises from 0.5 s to
30 s; P3, corrected current-side AUC falls from 0.5 s to 30 s. The table gives effects as mouse means with bootstrap
intervals, Holm-corrected p-values, and the number of mice whose effect has the predicted sign, for the raw data and
for the trial-locked residual rerun (A11). Sources: `results/stats/d5/primary.csv`, `results_residual/stats/d5/primary.csv`,
and `results*/robustness/d5.csv` for the mouse counts.

| Test | Data | Effect (mouse mean) [95% CI] | Holm p | Mice in predicted direction |
|---|---|---|---|---|
| P1 geometry | raw | +12.7° [10.2, 15.1] over the 0.5 s floor and +3.6° [2.2, 4.9] over the 30 s floor | 0.0026 | 11 of 13 |
| P1 geometry | residual | +11.4° [8.9, 13.9] and +2.1° [0.7, 3.3] | 0.013 | 10 of 13 |
| P2 prior rises | raw | −0.099 [−0.218, +0.002] | 0.89 | 4 of 13 |
| P2 prior rises | residual | −0.093 [−0.154, −0.038] | 0.996 | 3 of 13 |
| P3 current side falls | raw | +0.061 [0.028, 0.094] | 0.0061 | 10 of 13 |
| P3 current side falls | residual | +0.063 [0.032, 0.097] | 0.0051 | 11 of 13 |

### P1: geometry

The principal angles between two subspaces measure how far apart they are, from 0° (shared direction) to 90°
(orthogonal); the summary is the mean over the five angles. The table gives the angle between fits on opposite
session halves in the readout basis, both as mouse means (the test's and the report's convention) and as session means.
"First" is the smallest angle, the closest pair of directions. Chance is the mean angle between independent
covariance-matched random subspaces. Sources: `results/stats/d5/geometry_sessions.csv`, `results/geometry/*_d5.pqt`
and the chance levels in `results/subspaces/*_d5.json`.

| Comparison | Mean angle, mouse mean | First angle, mouse mean | Mean angle, session mean | First angle, session mean |
|---|---|---|---|---|
| 0.5 s vs 0.5 s (same lag) | 58.9° | 31.9° | 59.7° | 32.8° |
| 30 s vs 30 s (same lag) | 68.0° | 48.2° | 69.1° | 50.0° |
| 0.5 s vs 30 s (cross lag) | 71.6° | 52.3° | 72.1° | 53.3° |
| Covariance-matched chance | 67.9° | 47.0° | 67.8° | 46.7° |

The cross-lag angle averages the two pairings (0.5 s on the first half with 30 s on the second, and the reverse), as
the test does. After residualization the mouse means are 58.1°, 67.5°, 69.5° and 68.8° (first angles 31.0°, 43.7°,
46.8° and 48.6°).

The test passes, with three qualifications. First, most of the effect is the short-lag side: the 30 s split-half floor
is itself at chance, so "cross exceeds the 30 s floor" compares against a noise-level baseline, and that margin is only
3.6°. Second, the result holds for the readout basis but not the loading basis, where the cross-lag angle is 1.0°
*below* the 30 s floor (p = 0.96). Third, chance is not a neutral null here: with the small penalties selected, the
readout basis is pushed toward low-variance input directions, while covariance-matched random subspaces favour
high-variance ones. The 30 s floor sitting at chance is consistent with the post hoc A16 finding that the leading 30 s
direction is not spatially reproducible across halves.

### P2: prior

The paired, null-corrected change in prior $R^2$ from 0.5 s to 30 s was $-0.099$ (mouse mean; 95% CI $-0.218$ to
$+0.002$; median over mice $-0.041$). The predicted rise was not supported. That conclusion does not rest on the
bootstrap upper bound alone. Under the Findling decoder (post hoc, A16) the 30 s minus 0.5 s difference was positive
in 7 of 13 mice (median 0.001, two-sided p = 0.34), against 4 of 13 under the registered ridge decoder (median
$-0.042$, p = 0.22), so neither decoder shows a detectable rise. After residualization the change was $-0.093$ ($-0.154$
to $-0.038$), an interval that excludes zero on the negative side; but no test in that direction was registered, the
apparent fall is decoder-dependent, and no fall is claimed.

Per subspace, the null-corrected prior $R^2$ (mouse means, `matrix.csv`) was as follows.

| Subspace | Raw | Residual |
|---|---|---|
| RRR 0.5 s | 0.054 | 0.053 |
| RRR 2 s | −0.027 | −0.017 |
| RRR 8 s | −0.057 | −0.034 |
| RRR 30 s | −0.046 | −0.038 |
| PCA | 0.013 | 0.041 |
| Random (covariance-matched) | −0.030 | 0.004 |

These estimates sit at the noise floor. None of the per-lag Fisher-combined session p-values reaches 0.05 in the raw
data (0.5 s: 0.15; the smallest is 0.12, at 30 s). The part of the 30 s subspace orthogonal to the 0.5 s subspace
carries a corrected prior $R^2$ of 0.005. Across decoders and detrending choices (A16) the subspace-level values move
by about ±0.05, and the ordering above (0.5 s highest) does not survive the second decoder or either detrend. Only "no
detectable rise with horizon" holds in every variant.

### P3: current stimulus side

On nonzero-contrast trials, the null-corrected current-side AUC drops by 0.061 (0.028 to 0.094) from 0.5 s to 30 s,
and by 0.063 (0.032 to 0.097) after residualization. The test holds at d = 10 but not at d = 3 (Holm p = 0.11), and
fails after the post hoc quadratic detrend (0.22).

The 0.5 s subspace is not *specialized* for the stimulus. Its corrected AUC (0.218, mouse mean) equals that of a
covariance-matched random subspace (0.218) and is below PCA (0.240). The effect is that long-lag subspaces *lose*
stimulus information (0.144 to 0.161 at 2 to 30 s), as evoked responses lasting under a second would predict, not that
short-lag subspaces gain it. The drop persists after controlling for block information: the AUC gained over a
prior-only model is 0.074 at 0.5 s and 0.028 to 0.044 at longer lags.

## Secondary results

All values in this section are mouse means from `results/stats/d5/matrix.csv` and `secondary.csv` unless stated.

**Nesting.** The nesting index is the fraction of one subspace's leading direction that lies inside another subspace
(1 means fully inside). The 0.5 s subspace contains 92% (90 to 94%) of the 30 s subspace's leading direction; the
reverse figure is 76%. After residualization the two figures are 94% and 89%. The slow signal is shared rather than
split off.

**The session-time mode.** Elapsed time is strongly decodable from every five-dimensional summary, as the table shows
(mouse means, raw and residual reruns).

| Subspace | Elapsed-time R-squared, raw | Elapsed-time R-squared, residual |
|---|---|---|
| RRR 30 s | 0.84 | 0.73 |
| RRR 0.5 s | 0.82 | 0.72 |
| PCA | 0.80 | 0.70 |
| Random (covariance-matched) | 0.64 | 0.56 |

Long lags add only a little over PCA, though the increase with lag is consistent (per-session Spearman correlation of
elapsed-time $R^2$ with lag, mouse mean 0.88). The proposal's drift flag (the 30 s subspace decodes elapsed time
better than both PCA and the random subspace while its prior decoding is not significant) fires in 14 of 16 sessions,
12 of 16 after residualization. That is a lenient criterion, since the 0.5 s subspace also beats PCA on elapsed time.
The directions unique to the 30 s subspace carry little of the signal (elapsed-time $R^2$ 0.12 raw, 0.03 residual).

I call the leading direction of the full-session 30 s readout subspace the *session-time mode* (earlier sections and
the pilots call it the "slow mode"; they are the same thing). The name describes its association with time and does
not imply a neural or cognitive origin. Averaged in 30 s windows it is close to a straight line in most sessions: its
correlation with elapsed time has a session median of 0.96 and is at least 0.9 in 12 of 16 sessions
(`results/pilot/sessions_d5.csv`).

**Unit turnover.** Recomputed from `data/interim/` with explicit definitions (fifths are five equal parts of each
session's valid task-epoch bins): 257 of 842 units fall below 0.1 Hz in some fifth of the session (in 15 of 16
sessions), and 68 units are completely silent for a fifth (in 13 sessions). An earlier figure of "118 units, 14 of 16
sessions" used an unrecorded definition and is superseded. Turnover like this is a classic signature of probe drift or
sorting instability, and it is what exposed the bug fixed in D10.

**Estimator check.** This asks how well each method predicts future population activity, as held-out $R^2$ with
contiguous folds. The table gives mouse means as in the report, where RRR uses the session's shared penalty and the
other methods their best penalty (source: `results/estimator/*_d5.pqt`).

| Method | 0.5 s lag | 2 s | 8 s | 30 s lag |
|---|---|---|---|---|
| Full-rank ridge | 0.373 | 0.223 | 0.200 | 0.176 |
| Lagged RRR, 5 dimensions | 0.246 | 0.192 | 0.183 | 0.172 |
| PCA + ridge, 5 dimensions | 0.235 | 0.171 | 0.161 | 0.150 |
| Random, 5 dimensions | 0.162 | 0.133 | 0.121 | 0.118 |

As session means of each method's score at the session's shared penalty, the 0.5 s and 30 s values are 0.371 and
0.178 (ridge), 0.246 and 0.176 (RRR), 0.232 and 0.152 (PCA), and 0.163 and 0.121 (random); the conclusions are the same.
RRR beats PCA at every lag, by 0.011 at 0.5 s up to 0.022 at 30 s (all p at most 0.005). At 30 s five dimensions
recover 96% of full-rank predictability, so what is predictable 30 s ahead is very low-dimensional. After removing
trial-locked responses, RRR's margin over PCA shrinks to 0.005 to 0.008, with intervals including zero at every lag: much
of what makes the predictive objective better than plain variance is task structure that recurs every trial.

**Other secondary measures.** Corrected previous-side AUC is roughly flat across lags (0.037 to 0.050). Current-side
decoding from the part of the 0.5 s subspace orthogonal to the 30 s subspace exceeds that from the reverse complement
(0.259 against 0.220; p = 0.016, uncorrected); prior decoding from the two complements does not differ (p = 0.39). The
chosen penalty multiplier was 0.1 in 9 sessions, 0.32 in 3, 0.032 in 2, 0.01 in 1 and 0.001 (the grid edge) in 1.

## Robustness

The d = 3 and d = 10 runs and the residual rerun were pre-registered sensitivity analyses; leave-one-mouse-out and
dropping DY_014 are post hoc (P1h). The table gives Holm-corrected p-values (sources: `results*/robustness/d5.csv` and
`results/stats/d{3,10}/primary.csv`).

| Variant | P1 geometry | P2 prior | P3 current side |
|---|---|---|---|
| Primary (5 dimensions, raw) | 0.0026 | 0.89 | 0.0061 |
| Trial-locked residuals | 0.013 | 0.996 | 0.0051 |
| 3 dimensions | 0.032 | 0.21 | 0.11 |
| 10 dimensions (12 sessions, 10 mice) | 0.0029 | 0.88 | 0.0059 |
| Leave one mouse out, worst case (raw) | 0.0051 | 0.95 | 0.012 |
| Leave one mouse out, worst case (residual) | 0.027 | 0.998 | 0.010 |
| Drop DY_014 (raw) | 0.0051 | 0.87 | 0.0051 |

The prior test is never significant in any variant, the current-side test fails only at d = 3, and the geometry test
survives every variant.

**DY_014** is the low outlier in the geometry figure. Its readouts are dominated by one cluster firing at about 141 Hz,
likely multi-unit, with a lag-1 autocorrelation of 0.95 in square-root counts (the session median is 0.39). In the last
quarter of the session that cluster's spike rate falls from about 164 Hz to 71 Hz (a 57% drop, or 40% on the
square-root scale the analysis uses), along with several other units. The cluster makes all of DY_014's subspaces
unusually reproducible. The mouse's effects point the same way as everyone else's, and dropping it changes nothing
material. The post hoc A16 step analysis (below) found that DY_014's session-time mode has one abrupt step at 43
minutes, coinciding with an amplitude event in a contributing unit.

## What changed after the first run (amendment D10)

While diagnosing two sessions with held-out $R^2$ near zero for every method, I found a bug. The z-score standard
deviation floor ($10^{-3}$) let a unit that was silent across a training fold but active in its test fold reach a
held-out z-variance of about $10^5$, so that one unit made up more than 99% of the pooled test variance. That corrupted
the cross-validated $R^2$ and, through it, the session ridge penalty. The floor is now the standard deviation of the
square-root count of a unit firing exactly at the 0.1 Hz inclusion threshold, 0.218 (every session's smallest
whole-session standard deviation is already 0.22 or more, so no unit's whole-session z-score is affected). The fix
changed the chosen penalty in 2 sessions in the raw run and 4 in the residual run.

Raw d = 5 primary p-values and raw leave-one-mouse-out p-values did not move. These Holm p-values did: residual P1
0.048 to 0.013 and P3 0.012 to 0.0051; residual worst leave-one-mouse-out P1 0.092 to 0.027 and P3 0.024 to 0.010;
d = 3 P1 0.049 to 0.032. P2 changed slightly (residual 0.999 to 0.996, d = 3 0.23 to 0.21, d = 10 0.81 to 0.88) and
stayed far from significance. An earlier estimator result, "RRR beats full-rank ridge at 30 s" (ratio 1.13), was an
artifact of the bug. Pre-fix outputs are kept in `results/prefix_D10/` and `results_residual/prefix_D10/`.

## How strong is this, and what does it mean?

**The prior: no detectable rise.** The predicted rise of the prior with horizon does not appear in any variant: raw or
residual, any d, any left-out mouse, either decoder, or either detrend. The claim is limited to that. A modest rise
remains possible: the raw bootstrap upper bound is +0.002, the cosine-detrend rerun gives +0.020 [−0.025, 0.068], and
the prior is a small signal in MOs to begin with. Subspace-level prior estimates sit at the noise floor and are
decoder-dependent, so nothing is claimed about where in the population the prior lives, and no decrease with horizon is
claimed either. Comparisons of subspace scores with the full-population gate are only meaningful on a common decoder
scale; A16 provides one.

**P3: moderately strong, qualified.** It is robust to residualization and leave-one-out, but sensitive to d (fails at
d = 3) and to detrending (fails after the quadratic detrend), and its interpretation is weaker than the hypothesis:
long lags lose the stimulus; short lags are not specialized for it. That is close to what evoked responses lasting
under a second would produce.

**P1: significant but thin.** Most of it is "short-lag subspaces are reproducible across halves and long-lag ones are
not". It holds in the readout basis only, and the long-lag side of the contrast is a few degrees against a floor at
chance.

**What is interesting.**

1. At every horizon, the predictable structure in MOs is dominated by one direction associated with session time,
   which PCA, 0.5 s RRR and random subspaces also carry, rather than by the latent variable the mouse must track. The
   most plausible account is variance ranking: RRR keeps the directions that predict the most variance, the
   session-time mode is large and slow, and the prior is small, so with five dimensions the slow signal is selected first; if
   many units drift independently, slow variance can fill the other dimensions too. This account is a mechanistic
   interpretation of the selection pattern, not an experimentally identified cause, and the detrending check fits it
   only in part (see A16). A17 measures the sizes and timescales involved but does not establish the cause either.
   An earlier "static code" reading is superseded by the next point.
2. The design could not have distinguished a dynamical from a static code for the prior. A 30 s lag spans about six to
   eight trials (median stimulus-to-stimulus interval 3.9 s), while blocks last tens of trials (median 46 completed
   trials, from the interim trial tables). Any persistent representation of the prior is therefore predictable 30 s
   ahead whether or not it evolves; predictability at these horizons tests persistence and size, not dynamics.
3. A methodological lesson, specific to these acute recordings. Every low-dimensional summary (30 s RRR 0.84, 0.5 s
   RRR 0.82, PCA 0.80, random 0.64) is dominated by session-scale variation, long horizons only slightly more.
   Elapsed-time decoding next to PCA and covariance-matched baselines, pseudo-session nulls, split-half reliability
   against a covariance-matched chance level, and care with fold-wise normalization (the D10 bug) are all needed
   before reading such subspaces as cognition.

**Overall.** This is a carefully controlled negative result with a plausible but untested mechanism, which suits a
course project. It is not, on its own, a publishable discovery: it is one region in 13 mice, and the positive primary
findings are either expected (P3) or modest (P1). The open question is what the session-time mode is; the pilots below
address it.

## Limitations

The study has one dataset of acute recordings in 13 mice; the smallest attainable one-sided Wilcoxon p with 13 mice is
$2^{-13} \approx 1.2\times10^{-4}$. The neighbouring areas used in A15 share probes, sessions and mice with MOs. The
remaining limitations are these:

- Splitting sessions into halves confounds reproducibility with nonstationarity: a drifting signal looks unreliable
  partly because the halves differ in time.
- Ramp-shaped signals inflate correlations with anything that trends, and elapsed-time decoding interpolates on
  representations fit to the whole session.
- The drift flag cannot separate electrode drift from slow internal-state change.
- With a median task epoch of about 66 minutes, the 30 s lag leaves only about 130 non-overlapping windows per session
  (median 133), so long-lag fits are noisy by construction.
  **Erratum (2026-11-23, A17):** this is wrong. RRR uses every overlapping pair of 0.5 s bins (about 7,900 per session;
  a 240 s lag gives up 480 of them). The real limit on any slow signal is the number of blocks per session (about 13),
  the same at every lag.
- Decoders are linear, and the prior is read from one pre-stimulus window.
- Bootstrap intervals over 13 mice under-cover; the pilots and post hoc checks are exploratory and uncorrected; the
  detrended tests have limited power.
- One analysis decision (D10) was made after results were seen. It is a bug fix and is reported in full above.

## Pilot: is the slow mode recording drift or brain state? (amendment A12, pre-registered, run on PACE ICE)

The slow mode is the leading direction of the 30 s subspace, followed through the session in 30 s windows and
sign-aligned to increase with time. Three tests were written down on 17 November, before any probe-motion or pupil data
was downloaded, along with the rule for reading them. All values are mouse means from `results/pilot/summary_d5.json`
unless stated.

**Test 1: remove drifting units.** I kept only units firing at least 0.1 Hz in every fifth of the session. That left 13
of 16 sessions from 12 mice; three sessions fell below 20 stable units. Refitting from scratch, the 30 s subspace still
decodes elapsed time with $R^2$ 0.77, against 0.83 for the original fits in the same 13 sessions (0.84 over all 16;
PCA 0.72, random 0.50 in the refit). The drift flag still fires in 12 of 13 sessions, and the 0.5 s subspace still
contains 91% of the slow direction. The primary results are unchanged, as the table shows (Holm p).

| Primary test | Stable units | Original |
|---|---|---|
| Geometry | 0.002 | 0.003 |
| Prior | 0.97 | 0.89 |
| Current side | 0.027 | 0.006 |

Units entering and leaving the recording do not create the slow mode; by the pre-registered rule it "survives".

**Test 2: probe motion.** IBL's spike-sorting motion estimate for these insertions is small: the median range across a
session is 7.9 µm (1 to 19 µm at the extremes). The slow mode correlates strongly with each session's own motion trace
(mean absolute correlation 0.74), but just as strongly with *other* sessions' motion traces, so the session-permutation
correction is $-0.006$ (p = 0.39). After removing linear trends from both, the correction is +0.062 (p = 0.14). The
slow mode follows probe motion no more than any slowly trending signal would.

**Test 3: pupil.** 15 sessions had usable pupil traces. The real correlation (mean absolute 0.35) is again no larger
than with other sessions' pupil traces: correction $-0.001$ (p = 0.42), and $-0.004$ (p = 0.55) after detrending.

**Reading.** The pre-registered overall reading is "mixed or undetermined". The mode survives removal of drifting
units, but neither probe motion nor pupil explains its session-specific shape. The limitation that matters most became
visible only here: the slow mode is close to a straight ramp in most sessions, and any two slowly trending signals
correlate about equally well with a ramp, so a session-permutation test has little power to tell candidate causes
apart unless they produce different shapes. The pilot does make the simplest artifact story, units dropping out,
unlikely as the main cause. The literature review (`reports/Slow neural modes literature review.md`) motivated the
ramp-independent tests that followed.

## Second pilot: what produces the slow mode? (amendment A13, prospectively documented exploratory, run on PACE ICE)

This pilot used three lines of evidence that do not depend on matching one ramp to another. The tests and the rule for
reading them were committed on 21 November, before the engagement table or the full spike files were downloaded.
Values are from `results/a13/summary_d5.json` and the refits in `results_mua/` and `results_ampstable/`.

**Multi-unit activity, independent of spike sorting.** Every detected spike in the MOs depth span, whatever cluster or
quality label it was given, was binned into 50 µm depth channels, and the unchanged pipeline was refit with those
channels in place of units (15 sessions, 12 mice; one session had too few channels). The slow mode reappears almost
exactly: the median correlation between the multi-unit slow mode and the unit-based one, over 30 s windows, is 0.96.
The 30 s subspace decodes elapsed time with $R^2$ 0.74, against 0.88 for the unit-based fits in the same 15 sessions,
and the drift flag fires in all 15. So I found no evidence that cluster assignment produces the mode. In this
representation the stimulus-side effect disappears (Holm p = 1.0), which is expected when each channel mixes neurons
with opposite preferences; the geometry effect remains (p = 0.010).

**No signature of a rigid probe shift.** If the probe moved as a whole, the multi-unit loadings should follow the slope
of the depth profile. They do not detectably: the mean absolute rank correlation is 0.19, and the Fisher-combined p over
15 sessions is 0.25. That is absence of evidence for a rigid shift, in line with IBL's small motion estimates.

**Spike amplitudes change, in step with the mode.** Spike amplitudes are far from stable over a session. Of the 840
units with an amplitude estimate, 59% have a consistent amplitude trend (absolute rank correlation with time of at least
0.5). The median unit's amplitude changes by 15.6% in absolute value between the first and last fifth of the session (a
descriptive measure, not pre-registered), more often downward (median trend $-0.26$; a quarter of units lose 21% or
more). The documented test asked whether units whose amplitude shrinks are the units whose rate falls along the slow
mode. They tend slightly to be: across units within a session, the loading and the amplitude trend are positively
correlated (mean Fisher z 0.15, one-sided p = 0.029 across 13 mice).

**The strictest filter.** Only 5 sessions (5 mice) kept 20 or more units that are stable in both rate and amplitude. In
those, elapsed-time $R^2$ falls to 0.49, against 0.73 for the original fits in the same 5 sessions, and the drift flag
fires in 3 of 5; the rule reads this as "intermediate". PCA falls too (0.68 to 0.43), so part of the drop reflects
having fewer units, but part may reflect the mode living in unstable units. This is the main unresolved challenge to the
recording-cause analysis (see "Where the session-time mode stands").

**Engagement and satiety beyond the trend.** After removing a quadratic trend in time from each signal, the slow mode is
not tied to IBL's per-trial engagement probability (session-permutation p = 0.19) or to cumulative rewards (p = 0.12).
Two secondary hints are weak: in the 11 sessions (9 mice) where engagement genuinely fluctuates p = 0.049, uncorrected,
but the sign of the relationship is not consistent across mice (p = 0.95), and the satiety relationship leans positive
(sign-consistency p = 0.068).

**Documented reading, and its later correction.** The rule outputs "sorting artifact". It reaches that label through
its second branch: the amplitude-stable refit is not "survives", and the amplitude-loading test is significant. The
label is a misnomer, because the most direct sorting test, the multi-unit refit, reproduced the mode; the rule had not
anticipated amplitude loss acting through spike *detection* rather than cluster assignment. At the time I read the
evidence as a slow change at the electrode–tissue interface costing spikes at the detection threshold. **That reading
is superseded by A14**, which tested detection loss directly: the moment-to-moment amplitude-rate coupling has the
opposite sign to detection loss, correcting every unit for its own amplitude change leaves the mode largely intact, and
amplitude change is not concentrated early. The A13 amplitude-loading correlation is real but small.

## Third pilot: does amplitude loss account for the slow mode? (amendment A14, prospectively documented exploratory, run on PACE ICE)

**Question and design.** A13 left open whether shrinking spike amplitudes are enough to produce the slow mode. The
obvious correction, regressing each unit's rate on its amplitude over time and removing the fit, cannot fail: both
quantities are near-ramps, so it removes any ramp in any unit whose amplitude drifts, whatever the cause. The
documented design (`f3008e7`, committed before any of it was computed) instead estimates the coupling only from
co-fluctuations around the time trend, brackets the answer between a conservative and a maximal correction, and tests
whether amplitude change is concentrated early in the session. A local smoke run exposed two weaknesses, so two post hoc
checks were added and recorded before the ICE run (job 7241313; all 16 sessions and 13 mice). Values are from
`results/a14/summary_d5.json` (mouse means unless stated).

**Part 1: coupling beyond the trend.** Each unit gets a Poisson regression of its spike count in each 30 s window on its
relative spike amplitude in that window, with a quadratic in time as nuisance terms. Spike-detection loss predicts a
positive coefficient: smaller spikes, fewer detected. The coefficient is negative instead: the mean across mice is
$-1.54$ (median $-1.43$), only 27% of units are positive (session median), and the one-sided p for a positive coupling
is 0.99. With a degree-5 time polynomial it is $-1.92$ (p = 0.995). A coefficient of $-1.5$ means that in a window
where a unit's spikes are 10% smaller than usual, it fires about 16% more, since $e^{0.15} \approx 1.16$.

The known cause of this sign is burst attenuation: spikes shrink during bursts and fast firing, an effect of rate on
amplitude. The post hoc check therefore used only isolated spikes, each at least 50 ms after the same unit's previous
spike (a median 46.5% of each unit's spikes). The coupling is still negative (mean $-1.32$, median $-0.97$, p = 0.98),
so burst attenuation does not hide a positive detection coupling.

**Part 2: amplitude-corrected refits.** Each unit's counts were multiplied, window by window, by the factor

$$
f_u(t) = \exp\!\left(-\beta\, \tilde a_u(t)\right),
$$

where $\tilde a_u(t)$ is the unit's smoothed relative amplitude and $\beta$ a coupling coefficient, clipped to between
0.5 and 2, and the full pipeline was refit. The main measure is how well the 30 s subspace decodes elapsed time
relative to the original $R^2$ of 0.84 (all 16 sessions are kept, so this is also the same-session original). The
"residual ramp" column needs no refit: it projects the corrected data onto the original slow direction and gives the
session-median fraction of the original slope that remains.

| Correction | Coupling used | Elapsed-time R-squared (fraction of original) | Residual ramp | Drift flags | Reading |
|---|---|---|---|---|---|
| Conservative (prospectively specified) | session median of the fluctuation coupling | 0.85 (101%) | 1.00 | 13 of 16 | survives |
| Maximal (prospectively specified) | each unit's coupling with no time terms | 0.80 (95%) | 0.86 | 14 of 16 | survives |
| Slow-maximal (post hoc) | each unit's coupling on a 5.5 min smoothed amplitude | 0.78 (93%) | 0.85 | 14 of 16 | survives |

The conservative correction is not a test of detection loss: its coefficient is the session-median coupling, which is
negative, so it corrects in the wrong direction. The informative rows are the maximal ones. Removing from every unit
everything that moves with its own amplitude takes away about a seventh of the ramp, and the 30 s subspace still
decodes elapsed time at 93 to 95% of its original level. The primary tests are unchanged in every corrected copy
(geometry Holm p 0.0004 to 0.004; prior 0.63 to 0.73; current side 0.006 to 0.013).

**Part 3: timing.** For units with a consistent amplitude trend, an index compares the change in the first third of the
session with the change in the last third, from $-1$ (all late) to $+1$ (all early). Settling after insertion predicts
early change. The observed index is $-0.12$ (p = 0.75 for "early"): if anything, the change is later. The slow mode
itself is almost exactly linear (index $-0.02$).

**Reading.** The documented rule outputs "amplitude cannot account for the mode", because even the maximal correction
"survives". All three parts agree: the coupling has the wrong sign, even with isolated spikes; correction removes at
most about 15% of the ramp; and the timing does not match settling. The A13 link between amplitude trend and slow-mode
loading is real but small, and is not the mechanism.

**Caveats.** Correction factors were clipped to between 0.5 and 2; about a third of units hit the clip in at least one
window in the maximal copies, so a unit that lost more than half its detected spikes to amplitude would be
under-corrected. Kilosort amplitudes are template scalings, not calibrated voltages, and the detection threshold acts
on whitened data. The task starts some minutes after insertion, so settling that ended before the task is invisible
here.

## Fourth pilot: other areas on the same probes, cross-area sharing and behaviour (amendment A15, prospectively documented exploratory, run locally)

**What was done.** Every frozen session's probes also pass through other brain areas, and their spikes were already
cached. For each session, the non-MOs area with the most good units was taken, and the unchanged pipeline (prior gate,
fits, decoding, statistics) was rerun on it. That gave 15 sessions from 12 mice (ZM_2245 had no other area with 20 or
more units) and nine areas: frontal cortex in 10 sessions (ACAd 1, ILA 2, PL 1, ORBl 1, ORBvl 3, AIv 1, MOp 1) and
lateral septum (LSr, 3) or striatum (CP, 2) in 5. All 15 were recorded on the same probes as the MOs units. The
criteria, the cross-area test and the behaviour tests were committed (`30d2c3f`) before any of this data was binned.
Values are from `results/a15/summary_d5.json` and `results_region2/stats/d5/`.

**Part 1: the core pattern is corroborated.** All four criteria written in advance hold (P1 and P3 significant, P2 not
significant, 30 s elapsed-time $R^2$ at least 0.5), as the table shows. The rule's label for this outcome is
"replicates", but because two criteria are lenient ("P2 not significant" is a null, and the elapsed-time threshold is
passed even by random subspaces, 0.56) and the areas share probes, sessions and mice with MOs, it is corroboration, not
replication.

| Measure | MOs (16 sessions, 13 mice) | Neighbouring areas (15 sessions, 12 mice) |
|---|---|---|
| Prior gate: median corrected R-squared (Fisher p) | 0.064 (1.2e-5) | 0.001 (0.002) |
| P1 geometry, Holm p | 0.0026 | 0.0037 |
| P1 cross-lag minus floor, 0.5 s and 30 s | 12.7° and 3.6° | 15.0° and 3.7° |
| P2 prior rises with lag, Holm p | 0.89 | 0.52 |
| P3 current side falls with lag, Holm p | 0.0061 | 0.012 |
| Elapsed-time R-squared: 30 s, 0.5 s, PCA, random (mouse means) | 0.84, 0.82, 0.80, 0.64 | 0.82, 0.78, 0.71, 0.56 |
| Drift flags | 14 of 16 | 14 of 15 |
| Nesting of the 30 s leading direction in the 0.5 s subspace | 0.92 | 0.92 |

The prior is barely present in these populations: the Fisher-combined gate p is 0.002, with 40% of sessions significant
on their own, but the median corrected $R^2$ is 0.001 against 0.064 in MOs. So these areas speak to "no detectable rise
with horizon" but not to where the prior lives.

**Part 2: the slow modes ramp together but do not share fluctuations.** Before detrending, the MOs and neighbouring-area
slow modes correlate strongly (median 0.94); two ramps always do. After a quadratic trend is removed from each, the
remaining fluctuations are not shared beyond the cross-session null: the corrected score averages 0.006 (one-sided
p = 0.48 across 12 mice) and the median detrended correlation is 0.07. Because the areas share a probe with MOs, a shared
fluctuation would not have shown a brain-wide state; its absence argues against a probe-level artifact about as much as
against a shared state, though these detrended tests have limited power.

**Part 3: no behavioural link beyond the trend.** Beyond a quadratic trend, the MOs slow mode does not track log reaction
time (p = 0.12) or accuracy (p = 0.34), and the signs are not consistent across mice (p = 0.50 and 0.38).

**Reading.** The project's main findings are not specific to MOs: in other areas on the same probes in the same mice,
long- and short-lag subspaces differ, the long-lag subspace is no better for the prior and worse for the current
stimulus, and a slow session-time mode dominates, nested inside the short-lag subspace. The pipeline also runs on
other areas without changes. Because the probes are shared, finding the mode again does not count against a
probe-level artifact, and this is not an independent replication.

## Post hoc follow-ups (amendment A16, run locally)

Four questions were added after all primary and pilot results were known. Each was written into `AMENDMENTS.md`
(`246fddb`) before it ran; all four are post hoc and exploratory. Values are mouse means from
`results/a16/summary_d5.json`, `results/a16/sessions_d5.csv`, `results/a16/steps_d5.csv` and the refits in
`results_detrend_q/` and `results_detrend_c/`.

**1. Remove the trend and refit: was the prior masked by the ramp?** Each unit's square-root activity was detrended,
either by a least-squares quadratic in time (removing a median 21% of binned variance) or by a cosine basis with periods
of at least 20 minutes (removing 26%), and the whole pipeline was refit unchanged. The trend is gone afterwards:
elapsed-time $R^2$ is negative for every subspace and no session is drift-flagged. The table gives the corrected prior
$R^2$ per subspace and the primary tests in each rerun.

| Subspace or test | Quadratic detrend | Cosine detrend |
|---|---|---|
| RRR 0.5 s | −0.002 | 0.031 |
| RRR 2 s | −0.054 | 0.043 |
| RRR 8 s | −0.003 | 0.037 |
| RRR 30 s | −0.015 | 0.051 [−0.000, 0.101] |
| PCA | 0.006 | 0.028 [0.004, 0.053] |
| Random | 0.006 | 0.020 |
| P2 change, 0.5 s to 30 s [95% CI] | −0.015 [−0.090, 0.047] | +0.020 [−0.025, 0.068] |
| Holm p for P1, P2, P3 | 0.0026, 0.58, 0.22 | 0.0007, 0.29, 0.0061 |
| Elapsed-time R-squared, 30 s and 0.5 s | −0.30 and −0.12 | −0.22 and −0.10 |

The reading rule written before running gave **not masked** for both: removing the trend does not make the prior rise
detectably with horizon. The two detrends disagree, however. With the cosine basis a small prior appears about equally
in every summary and P3 holds; with the quadratic the prior vanishes even at 0.5 s and P3 fails. So a modest rise is not
excluded by the cosine rerun, subspace-level prior estimates are fragile (moving by about ±0.05 across decoders and
detrends), and only "no detectable rise" holds in every variant. The cosine result fits the variance-ranking account
(once the ramp is gone, the prior is a small signal spread across directions); the quadratic result does not.

**2. A same-scale reference for the prior.** The full-population gate used a different decoder (Lasso, interleaved
nested cross-validation) from the subspace analysis, so subspace prior scores had no reference on their own scale. With
the subspace decoder (ridge, contiguous folds, the identical pseudo-sessions), the full population gives a corrected
prior $R^2$ of 0.159 (mouse mean; session median 0.108). On that scale the 0.5 s subspace scores 0.054, PCA 0.013 and
the 30 s subspace $-0.046$ (mouse means). *Corrected by A19 (25 November):* the mouse mean 0.159 is driven by one
session (`4d8c7767`, SWC_038, corrected score 1.59; without it 0.101), so the ratios first quoted here ("about a third",
"8%", "none") are not robust. By session medians, the summary A19 fixed in advance, the full population scores 0.108
(0.087 without that session) and the 0.5 s subspace, 30 s subspace and PCA capture 0.62, 0.06 and 0.18 of it (0.72,
0.17 and 0.25 without). See the A19 section. With the Findling decoder the full population scores 0.070
(mouse mean) and the subspaces 0.026 (0.5 s), 0.038 (30 s, about half) and 0.019 (PCA). The 30 s minus 0.5 s difference
is positive in 7 of 13 mice under the Findling decoder (median 0.001, two-sided p = 0.34) and in 4 of 13 under the ridge
decoder (median $-0.042$, p = 0.22). So "no detectable rise" holds under both decoders, while the fraction captured and
the ordering of subspaces depend on the decoder.

**3. Is the leading 30 s direction spatially reproducible?** For each session, the leading 30 s direction fit on each
half was compared across halves by absolute cosine, against chance from covariance-proportional random directions. The
table gives mouse means and one-sided Wilcoxon p-values for cosine above chance.

| Representation | Mean absolute cosine | Chance | p (above chance) |
|---|---|---|---|
| Readout (filter) weights | 0.21 | 0.15 | 0.32 |
| Loading weights | 0.19 | 0.15 | 0.37 |
| Activation pattern (Haufe et al. 2014) | 0.19 | 0.27 | 0.97 |
| Capture by the other half's 5-D subspace (descriptive addendum) | 0.21 | 0.15 | 0.21 |

None exceeds chance. (The activation-pattern baseline is covariance-proportional and itself biased toward high-variance
directions; the capture row, added after the cosines were seen, guards against leading directions swapping order between
halves.) The time course is a consistent ramp, but which units carry it appears to change within a session. That
points to unit-level nonstationarity rather than one coherent population state, and is consistent with the 30 s
split-half floor sitting at chance.

**4. The step sessions.** By the rule written in advance (a single 30 s window-to-window jump of at least 30% of the
mode's range), only DY_014 is a step session (a jump of 80% at 43 minutes); CSHL049's largest jump is 20%. At DY_014's
step, IBL's motion estimate barely changes (0.13 µm, 65th percentile of that session's changes), the three units
contributing most carry 48% of the jump, and one of them shows its largest window-to-window amplitude change of the
session at exactly that time (100th percentile). Reading: **artifact-consistent**. The step coincides with an abrupt
spike-amplitude change in a contributing unit, not with probe motion.

## Timescale follow-ups (amendment A17, post hoc, run locally)

After the talk, the instructor's questions ("trials or blocks?", "why not minutes?") and outside reviews pointed at
the timescale logic of the design. A17 was written into `AMENDMENTS.md` (`0dbca28`) before any of its neural-data
analyses ran; it is post hoc and exploratory, and its four tests are uncorrected. A dated review note (24 November,
`2b27bb6`) corrects two claims made on 23 November; the corrected versions are given here. Values are session medians
from `results/a17/timescales.json` and `results/a17/budget.json`, and mouse means from `results/a17/longlag_c.csv`,
`longlag_q.csv` and `longlag.json`, unless stated.

**Part 0: how long the prior stays predictable (task data only).** The question is how long the Bayes-optimal prior
remembers itself, compared with the lags tested and the block length. Its autocorrelation $\rho_\pi(\Delta)$ is the
correlation between the prior now and $\Delta$ later, and $\rho_\pi(\Delta)^2$ is the fraction of its variance that
could be predicted that far ahead. Per 0.5 s bin (the prior of trial $t$ assigned to the bins before stimulus $t$),
the fraction still predictable is 0.99 at 0.5 s, 0.88 at 8 s, 0.59 at 30 s, 0.27 at 60 s, 0.01 at 2 min and 0.04 at
4 min (where the correlation is slightly negative, because blocks alternate). The integrated timescale is 67 s (IQR
55 to 75 s across sessions). Counted per trial instead (one value per trial, added after the review so the result
does not depend on how the prior is spread over bins), it is 12.2 trials (IQR 10.9 to 13.8), and the
autocorrelation reaches zero after 27 trials. The per-bin version is longer in trials (16.9) because the prior is
constant through long inter-trial gaps. For comparison, the median stimulus interval is 3.9 s, completed blocks last
a median of 46 trials (3.6 min; 215 blocks), and sessions last 66.5 min. The ≥ 20 min cosine detrend of A16 removes
a median 12% (range 4 to 45%) of the prior's own variance.

**Reading.** The prior forgets itself within one to two minutes, far less than a block, while a session-long ramp
stays predictable at every lag tested. Under a simple two-component picture (predictable variance as variance times
squared autocorrelation), the prior's predictable share relative to such a drift only falls with lag, so longer lags
should not help. This is a heuristic, not a property of the RRR objective; the calibrated simulation (A18 part A)
shows long lags can still favour the prior over short ones when moderate drift is present. The earlier claim
that blocks outlast the longest horizon still holds (a 30 s lag is about 8 trials), but the relevant timescale for
prediction is the prior's own, about 12 trials.

**Part 1: how large each source of activity is (descriptive).** On whole-session z-scored square-root activity, at
the population level (sums over units):

| Component | Session median [IQR] | How it is measured |
|---|---|---|
| ≥ 20 min component (cosine basis) | 22.6% [12.2, 28.3] | In-sample fit on all bins; not null-corrected |
| Same, quadratic trend | 17.2% [10.4, 22.5] | In-sample fit on all bins |
| Trial-locked responses (A11 GLM) | 8.6% [6.0, 10.3] | In-sample fit on all bins |
| Block prior, pre-stimulus windows (primary) | 0.20% [0.06, 0.34] | Cosine span removed; real minus pseudo-session median; positive in 14 of 16 |
| Block prior, per bin (secondary) | 0.09% [0.06, 0.17] | Cosine span and signed event kernels removed; pseudo-corrected; positive in 14 of 16 |

The prior is genuinely present but tiny. The shares are measured differently (all bins against pre-stimulus windows;
uncorrected against null-corrected), so they are not one additive budget. On the same bins, the per-session ratio of
the slow share to the per-bin prior share has a median of 124 (two sessions with a negative corrected prior share give
negative ratios); the honest summary is "about two orders of magnitude larger, under the
respective measurements".

A descriptive entry check compared the prior's predictable variance, estimated as its corrected per-bin sum of
squares times $\rho_\pi(\Delta)^2$, with the 5th eigenvalue of the ridge-RRR matrix in the same fit. The ratio has a
median of 0.05 (raw, 0.5 s), 0.14 (raw, 30 s), 0.13 (cosine-detrended, 0.5 s) and 0.66 (cosine-detrended, 30 s); it
is below 1 in 16, 16, 16 and 12 of 16 sessions. This was first described as an upper bound showing that the prior
"could not have entered" a rank-5 subspace. That claim is withdrawn (review note): $\rho_\pi^2$ is not an upper limit
on the prior's predictability from past activity, fitted directions mix components, the eigenvalues describe the
output side while the prior is decoded from the input side, and the corrected sum of squares is a noisy estimate. The
comparison only says the prior's predictable variance is small next to the dominant modes. The direction the prior
loads on is itself often strongly predictable: its total predicted variance exceeds the 5th eigenvalue in 8 to 14 of
16 sessions before correction, and in 2 to 7 after.

**Part 2: does any lag select the prior once the drift is removed?** Scripts 04 and 05 were refit with lags of 0.5 s
to 4 min on both A16 detrended copies, with each session's ridge penalty fixed to its A16 value. A reproduction check
passed first: per-session penalties, and real and null scores at the original lags, equal the A16 roots (largest
difference $2 \times 10^{-14}$). The table gives the corrected prior $R^2$ by lag (mouse means [95% bootstrap CI]).

| Lag | Prior still predictable (median) | Cosine-detrended copy | Quadratic-detrended copy | Fewest test pairs per fold |
|---|---|---|---|---|
| 0.5 s | 0.99 | 0.031 [−0.009, 0.073] | −0.002 [−0.035, 0.033] | 1291 |
| 2 s | 0.97 | 0.043 [0.002, 0.085] | −0.054 [−0.156, 0.027] | 1288 |
| 8 s | 0.88 | 0.037 [−0.004, 0.076] | −0.003 [−0.085, 0.059] | 1276 |
| 30 s | 0.59 | 0.051 [−0.000, 0.100] | −0.015 [−0.101, 0.053] | 1232 |
| 60 s | 0.27 | 0.049 [0.008, 0.091] | −0.018 [−0.128, 0.064] | 1172 |
| 2 min | 0.01 | 0.032 [−0.007, 0.072] | −0.010 [−0.061, 0.035] | 1052 |
| 4 min | 0.04 | 0.038 [0.002, 0.074] | 0.008 [−0.080, 0.074] | 812 |
| PCA | | 0.028 [0.004, 0.054] | 0.006 [−0.030, 0.042] | |
| Random | | 0.020 [−0.002, 0.042] | 0.006 [−0.016, 0.029] | |

Test-pair counts only confirm that every fold has data; consecutive pairs are strongly dependent, and inference is
over mice. Elapsed-time $R^2$ is negative for every subspace at every lag in both copies, so the trend stays removed.

The rule written in advance reads "band selection" only if, in both copies, the 60 s subspace beats both the 0.5 s
subspace and PCA (paired-null differences, one-sided Wilcoxon over 13 mice, p < 0.05). None of the four tests passes:

- cosine copy, 60 s over 0.5 s: 6 of 13 mice, p = 0.29;
- cosine copy, 60 s over PCA: 9 of 13 mice, p = 0.12;
- quadratic copy, 60 s over 0.5 s: 5 of 13 mice, p = 0.55;
- quadratic copy, 60 s over PCA: 6 of 13 mice, p = 0.53.

The reading is **no band selection**.

**A failed prediction.** A17 predicted that the corrected prior would fall with lag, roughly following the fraction
still predictable, and reach about zero by 2 minutes. It did not. In the cosine copy it is flat at 0.03 to 0.05 from
0.5 s to 4 min (rank correlation with the predictable fraction −0.14, p = 0.76; quadratic copy −0.11), including at
lags where almost none of the prior is predictable, and close to PCA and random subspaces. The most plausible reading
is that the small prior signal in these subspaces is incidental, carried by any reasonable five-dimensional summary,
rather than selected through its predictability. The intervals (about ±0.05) cannot tell a flat line from a small
decline, and the two detrends still disagree about whether any prior survives at all.

**What A17 does and does not show.** It shows that the prior's memory is short (about 12 trials, or 67 s per bin), that its variance
is about two orders of magnitude smaller than the slow component under these measurements, and that lags up to
4 minutes on drift-removed data do not select it. It does not show that variance competition is the cause of the
original failure, or that the prior was mathematically excluded from the subspaces. The simulation and latent
model that followed are A18 (next section). The block-switch alignment (part 6) was not done and is dropped
(`AMENDMENTS.md`, notes of 25 November).

## Calibrated simulation: prior against drift (amendment A18 part A, post hoc, run locally)

A17 showed the prior is small and short-lived next to the slow component, but not that this causes the failure. A18
part A asks the causal question where the answer is known. Simulated sessions reuse each recorded session's task
(trial timing, stimulus sides, choices, outcomes, block probabilities, trial mask), its number of units and each
unit's firing rate, and encode a block prior, a slow drift, stimulus history, evoked and stimulus responses and noise
in Poisson spiking. The registered pipeline (rank-5 lagged RRR at 0.5 to 30 s, PCA, random subspaces, the same
z-scoring, folds, decoder and 200 pseudo sessions) is then run unchanged. The design, calibration rule and readings
were committed (`3a81ba1`) before any calibration or simulation outcome was computed; one control was added
(`2f7611d`) after calibration and before the sweep. Values are from `results/a18/` (`real_targets.json`,
`calibration.json`, `sim_seeds.csv`, `sim_cells.csv`, `sim_summary.json`); the figure is
`results/a18/a18_simulation.pdf`. Each condition has 32 seeds; seeds s and s + 16 reuse the same recorded task,
so there are 16 distinct tasks, and the two seeds of a task are correlated (for the full-population prior score, the
correlation ranges from −0.34 to 0.92 depending on the condition). Across conditions a seed shares its task, latent noise, most loadings,
pseudo sessions and fit seed; spike-level Poisson noise is not shared, and the no-history null condition draws
different evoked-response loadings. Task-level checks (averaging the two seeds of each task) are in
`results/a18/audit_checks.json` (stage `audit`, added after the AI-agent audit of 24 November).

**Calibration.** Six gains were tuned so that the medians of 16 simulated sessions (one per recorded task) match six
recorded session medians. All six were matched within 10%. Six gains fitted to six targets leave no degrees of
freedom, so the match holds by construction and does not test the model; the fixed settings (a slow noise with a
timescale of about 50 s, drift rank 3, drift spectrum decay 0.3, a one-trial stimulus memory) were not varied.

| Target (session median) | Recordings | Simulation |
|---|---|---|
| Full-population corrected prior R² | 0.108 | 0.111 |
| ≥ 20 min share | 22.6% | 22.5% |
| 5 to 20 min share | 4.7% | 4.7% |
| Trial-locked share | 8.6% | 8.6% |
| Previous-side AUC, full population | 0.563 | 0.558 |
| Current-side AUC, full population | 0.869 | 0.866 |

The per-unit drift regime matched its two drift targets within 10% as well. Not matched, reported: the leading
principal component carries 21% of variance in simulation (calibrated low-rank drift) and 16% in the recordings
(five components: 44% and 43%).
The calibrated history trace is tiny (gain 0.036 against 0.29 for the prior), because the prior alone already makes
the previous stimulus as decodable as in the recordings.

**Results.** Corrected prior $R^2$, mean over 32 seeds [95% interval], raw pipeline.

| Condition | Full population | 30 s subspace | 0.5 s subspace | 30 s minus 0.5 s (P2-style) |
|---|---|---|---|---|
| Strong prior (x3), no drift | 0.632 [0.555, 0.708] | 0.537 [0.479, 0.594] | 0.449 | +0.089 [0.057, 0.127] |
| Calibrated prior, no drift | 0.170 [0.134, 0.209] | 0.069 [0.048, 0.092] | 0.019 | +0.050 [0.033, 0.067] |
| Low-rank drift x 1/3 | 0.174 [0.136, 0.214] | 0.047 [0.028, 0.066] | 0.019 | +0.027 [0.011, 0.045] |
| Low-rank drift x 1 (calibrated) | 0.167 [0.105, 0.235] | −0.006 [−0.055, 0.041] | −0.033 | +0.027 [−0.009, 0.067] |
| Low-rank drift x 3 | 0.268 [−0.243, 0.999] | −0.205 [−0.542, 0.071] | −0.172 | −0.036 [−0.107, 0.028] |
| Per-unit drift x 1/3 | 0.154 [0.105, 0.208] | 0.046 [0.020, 0.072] | 0.011 | +0.036 [0.015, 0.061] |
| Per-unit drift x 1 | 0.063 [−0.056, 0.170] | −0.088 [−0.221, 0.030] | −0.038 | −0.052 [−0.144, 0.029] |
| Per-unit drift x 3 | 0.084 [−0.381, 0.466] | 0.136 [−0.126, 0.381] | 0.028 | +0.097 [0.018, 0.183] |
| No prior, no history (null) | −0.043 [−0.112, 0.023] | −0.036 | −0.053 | +0.017 |
| No prior, history at calibrated strength | −0.012 [−0.063, 0.038] | −0.044 | −0.056 | +0.015 |
| No prior, history alone matching the recordings | 0.078 [0.019, 0.132] | −0.010 | −0.023 | +0.016 |
| Recordings (mouse means; full population from the post hoc A16 reference) | 0.159 (session median 0.108; 0.101 and 0.087 without `4d8c7767`) | −0.046 | 0.054 | −0.099 [−0.218, 0.002] |

**What it shows.**

1. *The positive control passes.* A strong prior is found by the full population and the 30 s subspace in all 32
   seeds, and the 30 s subspace keeps 85% of it.
2. *Without drift, the original hypothesis works in simulation.* At the recorded prior strength and no drift, the 30
   s subspace carries about 40% of the full-population prior score (capture 0.41 [0.33, 0.48]) and beats the 0.5 s
   subspace (+0.050). A slow prior is preferred by long-lag prediction when nothing slower competes.
3. *Drift at the recorded strength removes the 30 s subspace's prior score, but not the long-lag advantage.* With
   low-rank drift calibrated to the recorded slow share, the 30 s subspace's prior falls to about zero (−0.006
   [−0.055, 0.041]), and so do the 0.5 s, PCA and random scores, while the full population still decodes the prior
   (0.167, positive in 27 of 32). Post hoc, not a pre-set reading: the paired drop from no drift is positive in 23 of
   32 seeds; at the task level the 30 s score is positive in 14 of 16 tasks without drift and 8 of 16 at the
   recorded drift (`audit_checks.json`). (A Wilcoxon p = 0.002 quoted earlier treated the 32 seeds as independent.) A third of the drift cuts the 30 s
   score by about a third (0.069 to 0.047). But the 30 s subspace still beats the 0.5 s subspace in 21 of 32 seeds
   (9 of 16 tasks, chance level; P2-style change median +0.015, mean +0.027 [−0.009, 0.067], about the same as at a third of the drift), whereas
   in the recordings the change was −0.099. The pre-specified reading for the low-rank regime is therefore
   **"intermediate"**: the capture criterion is met, the change criterion is not. The A17 outcome table had no row
   for this reading, so any framing of the report around drift is a post hoc choice, and drift is not established
   as the cause of the recorded result. For the per-unit regime the reading
   is **"drift sufficient"**, but it is fragile: the capture ratio's interval is [−17.7, 23.8] because the
   full-population score itself becomes unreliable (positive in only 19 of 32), the median change is −0.003 (16 of 32
   positive), the regime fits the recordings' profile poorly (point 5), and at three times the drift the 30 s
   advantage returns (+0.097 [0.018, 0.183]).
4. *Stimulus memory alone can mimic the prior score.* The pre-set reading B came out negative: at the history
   strength fitted jointly with the prior (gain 0.036), memory with the prior removed gives no leak (−0.012, positive in 16 of 32), and
   the null is calibrated (no prior, no history: −0.043, positive in 13 of 32; the baseline is below zero because raw
   out-of-fold R² is strongly negative and the pseudo-session distribution is skewed). The added reading B2 (written
   after calibration, before the sweep) asks the no-prior case: no prior at all, and a one-trial stimulus memory strong enough to give
   *all* of the recordings' previous-side decodability on its own (gain 0.061; in the calibrated model with a prior,
   the prior accounts for most of it). This is the case the recordings would be in if MOs carried no prior. That
   gives a corrected full-population prior score of 0.078 [0.019, 0.132], positive in 24 of 32 seeds (12 of 16
   tasks, p = 0.038, borderline; one post hoc condition among many uncorrected readings). Against the recordings'
   session median (0.108) that is 72%; against the mouse mean it was quoted as 49% of 0.159, a reference A19 shows is
   inflated by one session. Reading B2: **history alone can mimic the prior score**. The
   pseudo-session null redraws the block sequence, so it does not protect against neurons that remember the real
   stimuli; memory raises the corrected score relative to the null baseline, and makes it positive only when strong
   enough. This is a known concern for prior decoding (the ideal observer's prior is itself a function of past
   stimuli, and subjective priors are commonly modelled as kernels over past events), not a new finding. It depends on
   the memory kernel: the one-trial memory assumed here lies inside the control's five-trial window, and a longer real
   memory would both mimic the prior more and escape the control.
5. *The profile comparison does not show that a prior is needed.* At calibrated low-rank drift, 6 of 8 pre-set
   features fall inside the recordings' 95% intervals (7 of 8 without session `4d8c7767`, A19), including
   elapsed-time decoding (30 s 0.79 against 0.84; PCA 0.75 against 0.80; random 0.65 against 0.64) and the near-zero
   30 s, PCA and random prior scores. But conditions with no prior match about as well (strong history alone 6 of 8;
   calibrated history 5 of 8; no prior and no history 5 of 8; `results/a19/profile_all_cells.json`), and every condition misses the two features that discriminate: the recordings'
   positive 0.5 s prior score (0.054) and their negative P2 change. Per-unit drift matches 2 of 8 (its elapsed-time
   decoding is too high, 0.92). A match shows the mechanism *can* produce much of the recorded pattern, not that it
   *does*.
6. *The history-controlled score removes stimulus memory, but also most of a genuine prior.* Regressing each target
   on its own previous 5 sides removes the history leak (calibrated history: positive in 13 of 32, the cell the
   pre-set validity rule uses; history alone: −0.017, positive in 17 of 32), and by the pre-set rule the score is
   valid (23 of 32 positive with the prior and no drift). It has little power because the ideal observer's prior is
   largely a linear function of the last 5 sides (in-sample R² 0.81, median over sessions; `results/a19/prior_history.json`):
   with a genuine prior and no drift the controlled score is 0.026 against 0.170 uncontrolled (about 85% removed), and
   at recorded drift it is positive in only 18 of 32. In the recordings it is −0.061 (session median; 6 of 16
   sessions positive, one-sided Wilcoxon p = 0.70; −0.050 without `4d8c7767`), **indistinguishable from zero**.
   Medians of 16 simulated sessions rarely fall that low at the calibrated drift (`audit_checks.json`: probability
   0.002 to 0.01 when drawing 16 of the 32 seeds at random, and below 0.001 when drawing one seed per task, except
   per-unit drift, 0.12 and 0.017), but this mainly reflects that the simulator varies less across sessions than the
   recordings on this score (interquartile range −0.135 to 0.125 recorded, −0.04 to 0.06 simulated at calibrated
   low-rank drift), so it is not evidence of anything the recordings do. (An AI-agent check outside the repository
   found a small negative bias in the control from fitting the history regression on the whole session; it was not
   committed and is not quantified here.)
7. *Detrending partly restores the 30 s prior* (cosine detrend, calibrated low-rank drift: 0.021 [−0.015, 0.059];
   per-unit 0.045), at magnitudes like the recordings' cosine copy in A16/A17 (0.03 to 0.05).

**Recommendation for the latent model.** The pre-set rule says proceed (positive control passed, history control
valid with 23 of 32, and the full population decodes the prior in 27 of 32 seeds at recorded drift, so there is
something for a model to find). The results qualify that. A stimulus memory alone, in the no-prior case, produces a
prior score of comparable size to the recorded one; the only control that removes it also removes most of a genuine
prior; and the recordings' controlled score is indistinguishable from zero. A real-data latent-model result
would therefore be hard to read either way. A18 already requires part B's own simulation gate first; in addition
(post hoc, proposed here), the model should go to the recordings only if its readout separates "prior with drift"
from "history alone" in simulation. That gate was then run (below) and failed, so the latent model stops here.

**Latent state-space model on the simulated sessions (A18 part B).** One bounded test, specified and committed
before any result (`1a233eb`), with a stopping rule: a trial-indexed linear-Gaussian latent model (8 latents with
their own timescales; known inputs: the slow cosine drift basis and the previous trial's stimulus, choice and reward)
was fitted to the pre-stimulus windows, and the prior was decoded from each trial's own latent estimate with the same
decoder and pseudo sessions. Gate, at the task level (16 tasks): B1, with calibrated drift the score must be positive
in at least 12 tasks and at least half the full-population score; B2, with stimulus memory alone it must not be. Values
from `results/a18/lds_gate.json` and `lds_sim_seeds.csv`.

| Condition | Latent-model score (mean) | Tasks positive | Full population |
|---|---|---|---|
| Calibrated prior, no drift | 0.026 | 13 of 16 | 0.170 |
| Low-rank drift x 1 | −0.003 | 8 of 16 | 0.167 |
| No prior, memory alone matching the recordings | −0.020 | 6 of 16 | 0.078 |
| No prior, no memory | −0.025 | 6 of 16 | −0.043 |

B1 fails, so the reading is **"does not retain the prior under calibrated drift: stop"**. The model is not fooled by
stimulus memory, but it also keeps little of a genuine prior even without drift (0.026 against 0.170, about 15%), so
its failure under drift says little about drift specifically. No positive control was run for this model, and B1's
threshold (half the full-population score) is above what lagged RRR itself captures at 30 s without drift (0.41). The
conclusion is limited to this specification (these inputs and the single-trial readout). An explanation offered in the
result note (the previous-stimulus input absorbing prior-related activity) was checked by an AI-agent diagnostic
outside the repository and is not supported. No latent model is run on the recordings and no variant is tried. See
`AMENDMENTS.md` (A18 part B result note and the notes of 25 November).

**AI-agent audit (24 November).** Two AI-agent reviewers (Claude subagents, briefed without the main session's
conclusions; not human review) audited the part A code and claims.
They found no leak of the current trial's stimulus into the pre-stimulus window and no decoder or target leakage, and
they reproduced every number except those corrected above. Counting at the task level (16 tasks, one-sided binomial)
the pre-set readings stand: positive control 16 of 16 tasks; full-population prior at calibrated drift 16 of 16;
history control with a prior and no drift 13 of 16 (p = 0.011), with calibrated history and no prior 7 of 16; history
alone mimicking the prior 12 of 16 (p = 0.038, borderline). Task-resampled intervals for the full-population score are 19 to 39% wider than the seed-resampled ones in the
table in conditions with a prior, and narrower in some others (for history alone, 0.008 to 0.152). Wording that overstated the drift result, the
history result and the pairing was corrected after the audit (`AMENDMENTS.md`, A18 audit note).

**Withdrawn metric.** The ground-truth "capture" of the true prior direction is uninterpretable (it reports 0.53 in
the no-prior condition; see the A18 notes in `AMENDMENTS.md`) and is not used.

## Sensitivity to one session (amendment A19, post hoc, run locally)

Session `4d8c7767` (SWC_038, 128 units) has corrected scores outside any plausible range: 1.59 for the
full-population prior in the post hoc ridge reference and −6.30 for the history-controlled score. The corrected score
(real R² minus the median R² of 200 pseudo sessions) has no upper bound of 1 when both terms are strongly negative,
which happens when a weakly regularised decoder extrapolates across contiguous folds. A19 was specified and committed
(`9cd4a62`) before any number was computed; it fixed in advance that the registered P2 result is not changed, that
every variant is reported, and that session medians become the primary summary for post hoc descriptive quantities
built on the corrected score. Values are from `results/a19/sensitivity.json`.

| Quantity | With the session | Without it |
|---|---|---|
| Registered P2, mouse-mean change (30 s minus 0.5 s) | −0.099 | −0.079 |
| Registered P2, one-sided Wilcoxon p over mice (Holm-adjusted the same) | 0.892 | 0.793 |
| Registered P2, mice with a positive change | 4 of 13 | 5 of 13 |
| Post hoc ridge reference, full population, mouse mean | 0.159 | 0.101 |
| Post hoc ridge reference, full population, session median | 0.108 | 0.087 |
| 0.5 s subspace as a fraction of the full population (session medians) | 0.62 | 0.72 |
| 30 s subspace as a fraction (session medians) | 0.06 | 0.17 |
| PCA as a fraction (session medians) | 0.18 | 0.25 |
| Strong history-alone score as a fraction of the session-median reference | 72% | 89% |
| Recordings' history-controlled session median | −0.061 | −0.050 |
| Low-rank profile features within the recordings' intervals | 6 of 8 | 7 of 8 |

The registered conclusion does not depend on the session (its own P2 value, −0.27, is the fourth lowest of 16, not
extreme). The post hoc reference and the ratios built on its mouse mean do. On session medians the 0.5 s subspace
carries most of the full-population score and the 30 s subspace little. Dropping the session would move the
simulation's calibration target for the full-population prior score from 0.108 to 0.087 (−19%; the other five
targets move by 10% or less); the simulation was not re-run. Only this session exceeds 1 in absolute value in the
files checked.

## Where the session-time mode stands

Taking A12 to A16 together:

- **Recording causes.** No single recording cause tested accounts for most of the mode: unit turnover (A12),
  cluster assignment and rigid probe motion (A13), spike-amplitude change and detection loss (A14). Each explains little
  of it.
- **The main unresolved challenge.** In the 5 sessions that keep 20 or more units stable in both rate and amplitude,
  elapsed-time decoding falls from 0.73 to 0.49 in the same sessions, while PCA falls from 0.68 to 0.43. Separating "fewer
  units" from "the mode lives in unstable units" needs matched-unit-count, stability-stratified resampling, which has not
  been done.
- **Spatial carrier.** The time course is consistent, but the spatial carrier appears to change across session halves
  (post hoc, A16).
- **Steps.** The one abrupt step (DY_014) is artifact-consistent (post hoc, A16).
- **State and behaviour.** Beyond a quadratic trend, the mode's fluctuations do not track pupil, engagement, cumulative
  reward, reaction time or accuracy, and are not shared with neighbouring areas on the same probes.
- **Other areas.** The pattern is corroborated in other areas on the same probes, which is corroboration, not
  replication.

The mode is a consistent association between population activity and session time. It is not established as neural or
cognitive, and it is not explained by any single recording artifact tested.

## Possible next steps

1. **Matched-unit-count, stability-stratified resampling** of the amplitude-stable subset, to resolve the main open
   challenge above.
2. **Spontaneous-activity epochs** (not registered). IBL sessions include spontaneous periods outside the task. Does
   the mode continue through them (not tied to doing the task) or reset or flatten (task-linked)?
3. **Independent sessions and regions**, which need new downloads. MOp has 14 sessions from 12 mice under the census
   rule.
4. **Testing the variance-ranking account directly**: comparisons with Dynamical Components Analysis and slow feature
   analysis, a ground-truth simulation with known drift and a known prior, and a drift-robust objective. The
   simulation is done (A18 part A). The explicit-drift latent state-space model was tested on the simulated sessions
   (A18 part B) and failed its gate: it does not retain the prior under calibrated drift, so it was not run on the
   recordings.
5. **A block-transition-aligned analysis**, asking how the population prior signal changes trial by trial after a
   switch. Specified as A17 part 6 but not done; dropped on 25 November and left as future work.

Done already: the stationarity control (A12), the engagement, satiety, amplitude and multi-unit checks (A13), the
amplitude-corrected refits (A14), the same-session second-area run (A15), the detrended refits (A16), and the
timescale measurements and long-lag sweep (A17 parts 0 to 2), the calibrated simulation and latent-model gate (A18),
and the one-session sensitivity analysis (A19).

The presented talk is `slides/slides.tex`; the earlier suggested slide outline in this file was superseded by it and
has been removed.
