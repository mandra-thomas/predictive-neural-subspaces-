# Project briefing: where everything stands

*Working document prepared by Claude (an AI assistant) for the author; not part of the course report. Updated 25 Nov
2026 after a round of AI-agent reviews; see "What the 25 November review changed" (section 10b).*

*First written 24 November 2026, to read in one sitting. It starts from the original question and ends with what to
do before the 7 December deadline. Section 9 says what is established and what is not; section 10b lists what the
25 November reviews changed; section 11 covers the latent-model test and section 12 lists the decisions that are
yours.*

## 1. The short version

The project asked whether predicting further ahead pulls out the slowly changing "block prior" that a mouse uses in
the IBL task. In MOs it did not. The pre-registered test of that idea (P2) was not supported: the mean change was
−0.099 with an interval of −0.218 to +0.002, which is wide, so a modest rise is not excluded. Every low-dimensional
summary of the recordings turned out to be dominated by a slow drift over the session.

Since the talk, the work has measured why it might have failed and what that means, with a partial (not
conclusive) answer:

- **The prior is short-lived.** It forgets itself within about 12 trials (one to two minutes), far less than a
  block. Longer prediction lags make it less predictable, not more, so longer lags were never likely to tip the
  balance toward it against a drift that stays predictable all session (a heuristic argument, not a proof).
- **The prior is small.** Its share of activity is about two orders of magnitude below the slow component.
- **Lags up to 4 minutes, on drift-removed data, still select no prior.** A prediction I made in advance (that the
  prior content would fall with lag) failed: it is flat.
- **A calibrated simulation gives a partial explanation, not proof.** With the recorded task, units and firing
  rates, a prior of the recorded strength *is* picked up by the 30 s subspace when there is no drift (longer lags
  then help: change +0.050). Drift of the recorded strength removes the 30 s subspace's prior score while the full
  population keeps it. But at that drift the 30 s minus 0.5 s change is near zero (median +0.015, positive in 9 of 16
  tasks), not negative as in the recordings, so the pre-set verdict is "intermediate". Drift is not established as
  the cause.
- **A known measurement issue applies here.** The ideal observer's prior is a function of past stimuli, so neurons
  that only remember recent stimuli also correlate with it, and the pseudo-session correction does not remove that.
  This is a known feature of the literature (subjective priors are commonly modelled as weighted sums over past
  events), not a discovery of this project. In the simulation, memory at the strength the recordings imply produced
  no false prior score (−0.012); only a deliberately strong memory did (+0.078). Removing stimulus memory also
  removes about 80% of the prior's variance, so the data cannot separate a belief from memory of recent stimuli.
- **The latent model did not help, so it stops.** Tested on the simulated sessions with a gate fixed in advance, this
  specification of a latent model with an explicit drift term kept none of the prior under realistic drift (and only
  about 15% without drift). By the stopping rule it was not run on the recordings.
- **One recorded session distorts some post hoc means.** The corrected score is not bounded by 1, and one session
  (SWC_038, 128 units) scores an implausible 1.59 on the post hoc ridge reference. A documented sensitivity check
  (A19) shows the registered P2 result does not depend on it, but the post hoc reference mean (0.159) drops to 0.101
  without it; session medians are now the primary descriptive summary.

What this is: a well-characterised negative result, a simulation that explains part (not all) of the recorded
pattern, and a measurement caveat about the prior. What it is not: a rescue of the original hypothesis, proof that
drift hid the prior in the real brain, or a new methodological discovery.

## 2. The original question and how it was tested

The project asked whether the *prediction horizon* of an objective decides what a low-dimensional population subspace
contains. The idea was that if you ask "which directions of current activity best predict activity a long time from
now?", you should pick out slowly changing internal variables, and if you ask about the next half second, you should
pick out fast sensorimotor ones.

The data are IBL Brain-Wide Map recordings from mouse secondary motor cortex (MOs): 16 sessions from 13 mice, 22 to
128 units per session (median 48.5), about 66 minutes and 534 usable trials per session. The task is IBL's biased
visual decision task. A grating appears on the left or right; in blocks of trials the stimulus is on one side 80% of
the time, and the blocks switch without warning every 20 to 100 trials (median 46 completed trials, about 3.6
minutes). The slow internal variable of interest is the **Bayes-optimal block prior**: the ideal observer's running
probability that the next stimulus will be on the left, given every stimulus so far. Earlier work (Findling et al.)
showed this prior can be decoded from many brain areas, including MOs, before the stimulus appears.

The method was **lagged reduced-rank ridge regression (RRR)**. Activity is binned into 0.5 s bins, square-rooted and
z-scored per unit. For a lag $\Delta$, RRR finds the best rank-5 linear map from the population vector now to the
population vector $\Delta$ later:

$$
\hat B_\Delta = \arg\min_{\operatorname{rank}(B)\le 5} \lVert Y - XB \rVert_F^2 + \lambda \lVert B \rVert_F^2 .
$$

Its *readout basis* is the five-dimensional space of current activity the fit uses to predict; its *loading basis*
is the space of predicted activity. The lags were 0.5, 2, 8 and 30 s. For each lag, the prior (and the stimulus side,
choice, feedback, wheel speed and elapsed time) was decoded from activity projected onto the readout basis, and
compared with PCA and with random subspaces of matched covariance.

Scores for experimenter-controlled variables are **pseudo-session corrected**: the same decoder is run on 200 fake
block sequences drawn from the task's own generator, and the corrected score is the real score minus the median fake
score. This guards against slow signals that would correlate with any block-like sequence by chance.

Three tests were pre-registered (written down and committed before the data were analysed):

- **P1, geometry:** the 0.5 s and 30 s subspaces differ more than each differs from itself across session halves.
- **P2, prior:** the corrected prior score rises from the 0.5 s to the 30 s subspace.
- **P3, stimulus:** the corrected current-stimulus score falls from 0.5 s to 30 s.

P2 was the heart of the project.

## 3. What the original analysis found

The prior gate passed first: the prior is decodable from the whole MOs population (Findling-style decoder, median
corrected $R^2$ 0.064, Fisher p = 1.2e-5), so there was something to look for.

| Test | Result (mouse mean) | Holm p | Verdict |
|---|---|---|---|
| P1 geometry | cross-lag angle exceeds the 0.5 s floor by 12.7° and the 30 s floor by 3.6° | 0.0026 | passed, thinly |
| P2 prior rises with lag | change −0.099 [−0.218, +0.002] | 0.89 | **not supported** (interval wide; modest rises not excluded) |
| P3 stimulus falls with lag | change +0.061 [0.028, 0.094] | 0.0061 | passed, but not as hoped |

The qualifications matter. P1's margin at 30 s is a few degrees against a floor that is itself at chance, and it
holds only in the readout basis. P3 holds because long-lag subspaces *lose* the stimulus; the 0.5 s subspace is no
better for the stimulus than a random subspace, so there is no "fast stimulus subspace". P2 is flat: no variant
(either decoder, residualised data, any dimension, any left-out mouse, either detrend) shows a rise. It is also
underpowered: with 13 mice and a per-mouse spread of about 0.21, a rise of the size the simulation produces without
drift (+0.05) would be detected only about one time in five. So "not supported" is the right wording, not "refuted".

What dominated every subspace instead was a slow **session-time mode**: a population direction whose activity
changes steadily over the session. Elapsed time is decodable with $R^2$ 0.84 from the 30 s subspace, but also 0.82
from the 0.5 s subspace, 0.80 from PCA and 0.64 even from random subspaces. Every low-dimensional summary of MOs
activity is mostly session time.

## 4. What the slow mode is not (pilots A12 to A16)

Five rounds of follow-up asked whether the slow mode is a recording artifact. Each had its design and reading rule
committed before its data were analysed.

- **A12 (pre-registered):** keeping only units that fire steadily all session leaves the mode (elapsed-time $R^2$
  0.77); it does not track IBL's probe-motion estimate or pupil size beyond what any ramp would.
- **A13:** multi-unit activity that ignores spike sorting reproduces the mode almost exactly (correlation 0.96); no
  sign of a rigid probe shift; spike amplitudes do change over the session, slightly in step with the mode.
- **A14:** amplitude loss cannot account for it: the moment-to-moment amplitude–rate coupling has the wrong sign for
  spike-detection loss, and correcting every unit for its own amplitude leaves 93 to 95% of the mode.
- **A15:** the same pattern appears in neighbouring areas on the same probes; their slow fluctuations are not shared
  with MOs beyond the trend; the mode does not track reaction time, accuracy, engagement or reward.
- **A16 (post hoc):** removing the trend (by a quadratic or by slow cosines) and refitting does not make the prior
  rise with lag; the two detrends disagree about whether any prior survives in the subspaces; the leading 30 s
  direction is carried by different units in the two session halves; the one abrupt step is artifact-consistent.

The open question that remained was the strictest unit filter: in the 5 sessions with enough units stable in both
rate and amplitude, the mode weakens (0.73 to 0.49), but so does PCA, so it is unclear whether that is the mode or
just fewer units.

## 5. The talk, the feedback, and the design flaw

The talk was on 23 November. The instructor's questions were: are lags in trials or blocks? was there a loss on the
prior? why not lags of minutes? are there separate representations? is RRR the only model? Outside reviews you
pasted converged on the same point: the design assumed a longer horizon would favour the prior, but nothing in the
objective knows about the prior.

The flaw, stated precisely: RRR is **unsupervised and variance-ranked**. It keeps the five directions that predict
the most future variance. A direction's predictable variance at lag $\Delta$ is roughly its variance times the
fraction of it still predictable that far ahead, times how well current activity reads it out. The prior enters only
at evaluation. It is found only if it happens to be among the largest predictable directions, and a large, slow,
highly predictable drift tends to win those dimensions first. The talk's answer that "the horizon wasn't the
limit" was untested; and one answer in the talk was wrong (the "only 130 independent windows at 30 s" argument; RRR
uses every overlapping pair of bins, and the real limit on any slow signal is the number of blocks, about 13 per
session, at every lag).

## 6. The pilot branch and A17: measuring the timescale argument

Everything after the talk lives on the git branch `pilot-timescale-fix` and is labelled **post hoc** (designed after
the earlier results were known). The original analyses, their results and the pre-registered readings are untouched.
Each new amendment's design and reading rules were committed before the data they govern were analysed, with one
documented exception: the A17 part 1 addendum (descriptive quantities only, no reading rule) says it was written
before the other 15 sessions ran, but it was committed after they ran, so its ordering is self-reported. A17 parts
1 and 2 also ran on code that was committed unchanged shortly afterwards.

**Part 0: how long the prior remembers itself (task data only).** The prior's autocorrelation $\rho_\pi(\Delta)$ is
the correlation between the prior now and $\Delta$ later; its square is the fraction of the prior's variance still
predictable $\Delta$ ahead.

| Lag | Fraction of the prior still predictable |
|---|---|
| 0.5 s | 0.99 |
| 8 s | 0.88 |
| 30 s | 0.59 |
| 60 s | 0.27 |
| 2 min | 0.01 |

Counted per trial, its timescale is about 12 trials (the autocorrelation reaches zero by 27 trials); counted per
0.5 s bin it is about 67 s. A block lasts about 46 trials and a session about 66 minutes. So the prior forgets itself
within one to two minutes, while a session-long ramp stays predictable at every lag. Longer lags make the prior
*less* predictable, not more. That is the answer to "why not minutes?" (as a heuristic: it treats the prior and the
drift as separate components, which RRR does not have to do).

**Part 1: how big each source of activity is.** Session medians, population level:

| Component | Share |
|---|---|
| Slow component (periods of 20 min or more) | 22.6% |
| Trial-locked responses | 8.6% |
| Block prior (pre-stimulus windows, pseudo-session corrected) | 0.20% |

The prior is present (positive in 14 of 16 sessions) but about two orders of magnitude smaller than the slow
component. The shares are measured on different data (all bins against pre-stimulus windows), so the ratio is a
scale, not an exact budget.

**Part 2: a lag sweep to 4 minutes on drift-removed data.** Scripts 04 and 05 were refit with lags up to 4 minutes on
both detrended copies from A16, after a reproduction check matched the earlier runs to $10^{-14}$. No lag selects the
prior: the 60 s subspace beat neither the 0.5 s subspace (p = 0.29 and 0.55) nor PCA (p = 0.12 and 0.53). The prior
content is flat across lags (0.03 to 0.05 on the cosine copy, about 0 on the quadratic), about what PCA carries. The
prediction committed in A17 (that it would decline as the prior becomes unpredictable) **failed**; the most plausible
reading is that the small prior signal is incidental, not selected.

**Corrections after a review you pasted (24 November).** You pasted a review of the GitHub repo. It was right on four
points, and the record was corrected in a dated note:

- I had called "the prior's corrected variance × $\rho_\pi^2$" an *upper bound* and claimed that, because it falls
  below the 5th RRR eigenvalue, the prior *could not* have entered a rank-5 subspace. That is not a bound and the
  claim was withdrawn: $\rho_\pi^2$ is not a ceiling on predictability from past activity, fitted directions mix
  components, the eigenvalues describe the output side while the prior is decoded from the input side, and the
  corrected sum of squares is a noisy estimate. It stays only as a descriptive scale comparison.
- The "100 times larger" ratio compares differently measured shares; it is now "about two orders of magnitude,
  under the respective measurements".
- Test-pair counts are not independent observations (they never were used as such).
- No A17 result implies the original prior decoder was misaligned; it uses event-aligned windows and a prior built
  from earlier trials only.

The review also asked for the per-trial timescale (now added: about 12 trials).

## 7. The calibrated simulation: design

**The question.** A17 shows the prior is small and short-lived, but correlation is not cause. The simulation asks it
directly, in a setting where the truth is known: if a prior and a drift of the measured sizes share one population,
does rank-5 lagged RRR lose the prior the way it did in the recordings? And is the drift needed, or is the prior just
too weak?

**How the simulated sessions are built.** Each simulated session copies one recorded session's task exactly: every
trial time, stimulus side and contrast, choice, outcome, block probability and the trial mask, so the prior and its
timescale are the real ones. It also copies the number of units and each unit's average firing rate. Neural activity
is then generated: each unit's log firing rate is a weighted sum of a few hidden signals, and spikes are drawn as
Poisson events. The hidden signals are:

- the block prior (switching to trial $t$'s value after the previous trial's feedback, so the whole pre-stimulus
  window carries it);
- a slow drift, either shared by all units through three slow processes ("low-rank") or independent in every unit
  ("per-unit");
- a stimulus-history trace (mostly the previous trial's stimulus);
- responses at stimulus, movement and feedback onset, plus a signed stimulus response;
- slower and faster noise.

**Calibration.** Six strengths were tuned so that the simulated sessions match six statistics of the recordings
(session medians): the full-population prior decoding score (0.108), the slow share (22.6%), the 5–20 min share
(4.7%), the trial-locked share (8.6%), how well the previous stimulus can be decoded (AUC 0.563) and how well the
current stimulus can be decoded (AUC 0.869). All six were matched within 10%. That match is less informative than
it sounds: six strengths were fitted to six targets, so a close match happens by construction and does not test
whether the model is right. What was *not* calibrated and is an assumption, never varied: how many independent drift
processes there are (three) and how their power falls with frequency, the slow noise's timescale (about 50 s, close
to the prior's own), the length of the stimulus memory (essentially one trial), the Gaussian random weights, and
Poisson spiking. The simulator also varies less across sessions than the recordings do on the history-controlled score: its interquartile range is −0.04 to 0.06 at realistic drift, against −0.135 to 0.125 in the recordings (−0.126 to 0.137 without SWC_038). So seed-level intervals understate real heterogeneity.

**Conditions.** Eleven conditions, each with the same 32 seeds. Seeds share the task, the latent noise, most weights,
the fake block sequences and the fitting seed across conditions, so comparisons are paired. (Spike-level noise is not
shared, and seeds s and s + 16 reuse the same recorded task, so there are 16 independent tasks, not 32.)

| Condition | What it is |
|---|---|
| Strong prior, no drift | Positive control: prior three times stronger |
| Calibrated prior, no drift | Does the realistic prior reach the 30 s subspace if nothing competes? |
| Low-rank drift at 1/3, 1 and 3 times the calibrated strength | Drift sweep, shared drift |
| Per-unit drift at 1/3, 1 and 3 times | Drift sweep, independent drift |
| No prior, no history | Null check |
| No prior, history at calibrated strength | Negative control as first specified |
| No prior, history alone strong enough to match the recordings | Added after calibration (see below) |

Each simulated session goes through the *registered* pipeline unchanged: the same binning, z-scoring, lags, rank-5
RRR, PCA and random subspaces, folds, decoder and 200 pseudo sessions. The rules for reading the results were
committed before any simulated result existed (commit `3a81ba1`).

**One change after calibration, before the main run.** Calibration put the stimulus-history strength near zero,
because the prior alone already makes the previous stimulus as decodable as in the recordings. That made the planned
negative control almost identical to the null, unable to test whether stimulus memory alone could fake a prior. A
dated addendum (`2f7611d`) added one condition, history alone tuned to the recordings, before the sweep ran.

## 8. The calibrated simulation: results

The figure is `results/a18/a18_simulation.pdf`. Scores are corrected prior $R^2$, averaged over 32 seeds.

| Condition | Full population | 30 s subspace | 0.5 s subspace |
|---|---|---|---|
| Strong prior, no drift | 0.63 | 0.54 | 0.45 |
| Calibrated prior, no drift | 0.17 | 0.07 | 0.02 |
| Low-rank drift x 1/3 | 0.17 | 0.05 | 0.02 |
| Low-rank drift x 1 (recorded strength) | 0.17 | −0.01 | −0.03 |
| Per-unit drift x 1 | 0.06 | −0.09 | −0.04 |
| Per-unit drift x 3 | 0.08 | 0.14 | 0.03 |
| No prior, no history | −0.04 | −0.04 | −0.05 |
| No prior, history alone matching the recordings | 0.08 | −0.01 | −0.02 |
| Recordings (mouse means, post hoc ridge reference) | 0.16 (0.10 without SWC_038) | −0.05 | 0.05 |
| Recordings (session medians) | 0.108 (0.087 without SWC_038) | 0.007 | 0.067 |

The recordings' full-population mouse mean (0.16) is inflated by one session (see section 10b), so compare the
simulation against the session medians. Read down the 30 s column first.

**The positive control works.** A strong prior is found in every seed, and the 30 s subspace keeps 85% of what the
full population decodes.

**Without drift, the original idea works in simulation.** With the prior at its recorded strength and no drift, the
30 s subspace carries about 40% of the full population's prior score and beats the 0.5 s subspace. A slow signal is
preferred by long-lag prediction when nothing slower competes. That is worth saying in the report: the hypothesis was
not silly. Whether drift is what defeated it in the recordings is not established.

**Drift at the recorded strength removes the 30 s prior score, but not the long-lag advantage.** With shared drift
tuned to the recorded slow share, the 30 s subspace's prior falls to about zero (so do the 0.5 s, PCA and random
scores), while the full population still decodes the prior about as well as before (mean 0.167 against 0.170). The
drop is consistent across tasks: the 30 s prior score is positive in 14 of 16 tasks without drift and 8 of 16 at the recorded drift. An earlier p = 0.002 treated the 32 seeds as independent and is no longer quoted. A third of the
drift cuts the 30 s score by about a third. But at the recorded drift the 30 s minus 0.5 s change is near zero
(mean +0.027, median +0.015, positive in 9 of 16 tasks, which is chance level), whereas in the recordings it was
clearly negative (−0.10). The reading rule written in advance therefore gives **"intermediate"**: the simulation
reproduces the *loss* at 30 s, not the recordings' advantage for the 0.5 s subspace. For independent per-unit drift
the rule gives "drift sufficient", but that verdict is fragile: that kind of drift also wrecks the full-population
decoder, fits the recordings poorly, and at three times the drift the 30 s advantage comes back.

**The profile comparison does not show that a prior is needed.** At the recorded drift, 6 of 8 pre-chosen features
fall inside the recordings' 95% intervals, most strikingly elapsed-time decoding (30 s subspace 0.79 against 0.84; PCA
0.75 against 0.80; random subspaces 0.65 against 0.64). But conditions with no prior at all match about as well (6 of
8 with stimulus memory alone, 5 of 8 with neither prior nor memory; `results/a19/profile_all_cells.json`), and every condition misses the two features that
would discriminate: the recordings' positive prior score in the 0.5 s subspace and their negative 30 s minus 0.5 s
change. Most of the match is the elapsed-time pattern, which any drift produces. (Recomputed without SWC_038 in A19,
the low-rank count is 7 of 8; the count moves with interval edges, so it is descriptive only.)

**Stimulus memory can produce a positive score, but only when it is strong.** The baseline first: with no prior and
no memory, the corrected full-population score averages −0.043 (positive in 13 of 32 seeds), not zero. Out-of-fold
$R^2$ values are strongly negative here, and subtracting the median of a skewed fake-session distribution leaves a
negative offset. With memory at the strength the recordings imply (the previous stimulus as decodable as in the
recordings, no prior), the score is −0.012, positive in 16 of 32 seeds: no false prior. Only in the deliberately
strong case, with memory given *all* of the recorded previous-stimulus decodability by a one-trial trace, is the
score positive: 0.078 (24 of 32 seeds; 12 of 16 tasks, a borderline p = 0.038, from one post hoc condition among
more than ten uncorrected readings). That is 72% of the recordings' session-median reference (49% of the inflated
mouse mean). The mechanism: the pseudo-session correction compares against *fake* block sequences, and neurons that
remember the *real* recent stimuli correlate with the real prior (which is built from those stimuli) but not with
the fake ones. So memory pushes the score upward, and if strong enough it can make it positive with no prior. This is
a known issue rather than a new one: the ideal-observer prior is by construction a function of past stimuli, and
subjective priors are commonly modelled as weighted sums over past events, so "belief versus memory" is largely a
question of the shape of that weighting. Check the Methods of Findling et al. (2025) for a previous-trial control
before saying anything about how their analysis handles it.

**The control for stimulus memory is blunt, and the recordings' controlled score is indistinguishable from zero.**
Regressing each target on its own last five stimuli before decoding removes the memory signal (strong memory alone:
about zero). But the ideal prior is itself largely predictable from its own past: across sessions the last stimulus
explains 41% of the prior's variance, the last five 81% and the last ten 86%, and the prior correlates 0.64 with the
previous stimulus (`results/a19/prior_history.json`). So the control also removes most of a genuine prior's score
(about 85% in the simulation without drift); it still detects a real prior without drift (23 of 32 seeds), but at the
recorded drift only in 18 of 32, and at that drift it cannot tell a prior from no prior. In the recordings this
controlled score is −0.061 (session median; 6 of 16 sessions positive; one-sided Wilcoxon p = 0.70; −0.050 without
SWC_038). That is consistent with zero. Medians of 16 simulated sessions rarely fall that low at realistic drift
(per-unit drift is an exception: probability 0.12, or 0.015 drawing one seed per task), but that mainly reflects how
little the simulator varies from session to session, not a property of the recordings. No conclusion about a belief
beyond memory of recent stimuli is possible from these data.

**After detrending, part of the 30 s prior comes back** (0.02 to 0.05), at about the size seen in the recordings'
cosine-detrended copy. That fits the A16/A17 picture.

**A metric I withdrew.** I had planned a "ground-truth capture" of the true prior direction. In the no-prior condition
it reported 0.53 (chance 0.11), because drift correlates with the prior by chance within a session and contaminates
the estimate. It is withdrawn and not used.

## 9. What is established, what is not, and what failed

**Established (with the evidence):**

- The prior's memory is about 12 trials (task data, all 16 sessions).
- Its share of activity is about two orders of magnitude below the slow component (descriptive).
- No lag up to 4 minutes selects it on drift-removed data (four pre-set tests, none significant).
- In a simulation matched to the recordings (under assumptions that were not varied), drift of the recorded strength
  removes a realistic prior from the 30 s subspace while the full population keeps it. It does not reproduce the
  recordings' advantage for the 0.5 s subspace (pre-set verdict: "intermediate"), and conditions without any prior
  match the recorded profile about as well.
- In simulation, strong stimulus memory with no prior can produce a positive pseudo-session-corrected prior score;
  memory at the strength the recordings imply did not.
- The registered P2 result does not depend on the one outlying session (A19).

**Not established:**

- That drift *is* what hid the prior in the real brain. The simulation explains part of the pattern under
  assumptions; it does not establish cause.
- That the recordings contain a block prior beyond memory of recent stimuli. The control that could tell removes
  most of a genuine prior too, and the recordings' controlled score is indistinguishable from zero.
- Anything about where the prior lives in MOs.

**Failed or withdrawn:**

- P2 (pre-registered): the predicted rise of the prior with lag was not supported (underpowered; not refuted).
- The A17 prediction that prior content would fall with lag: it is flat.
- The claim that the prior "could not have entered" a rank-5 subspace: withdrawn (it was not a real bound).
- The ground-truth capture metric: withdrawn.
- The latent state-space model, in the specification tested: failed its pre-set gate on simulated data (keeps no
  prior under realistic drift); not run on the recordings.
- A17 part 6 (aligning the decoded prior to block switches): never run; formally dropped in a dated note on 25
  November.
- The talk's "130 independent windows" argument: wrong, corrected.

**Labels.** Everything after the talk (A17, A18, A19) is post hoc: designed after the original results were known.
Each part's design was committed before its own data were analysed (with the one self-reported exception in section
6), and every change after seeing something is a dated note. The original pre-registered results are unchanged.

## 10. The first AI-agent audit (24 November)

After the A18 part A results were committed, two AI-agent reviewers (Claude subagents, not human reviewers) that had
not seen my conclusions audited everything: one the code, one the methods, numbers and wording. AI-agent reviews
catch many mistakes but are not independent human verification. Their findings, and what changed:

- **No leak.** The current trial's stimulus never reaches the pre-stimulus window in the simulation, the prior is
  built only from earlier trials, and there is no decoder or target leakage. Every number in the write-up
  reproduced from the result files, except those listed next.
- **My wording overstated three things,** then corrected: I had written that drift "is sufficient to reproduce the
  loss" (the pre-set verdict is "intermediate"); that stimulus memory "produces most" of the recorded prior score
  (in an extreme case it is 72% of the session-median reference); and, left over from A17, that a variance-ranked
  objective has "no horizon" that favours the prior (a heuristic, not a fact). One arithmetic slip ("a third of the
  drift halves it"; it cuts it by a third) and a missing table row were fixed.
- **The seeds are not 32 independent draws.** Pairs of seeds reuse the same recorded task, so there are 16
  independent tasks. Re-counted over tasks, every pre-set verdict stands; the "history alone mimics the prior"
  verdict becomes borderline (12 of 16 tasks, p = 0.038). Task-resampled intervals for the full-population score in
  conditions with a prior are 19 to 39% wider than the seed-level ones (some others are narrower). These task-level
  checks are computed by the committed script (`results/a18/audit_checks.json`).
- **Pairing across conditions is partial.** Spike-level noise differs, and the null condition got different
  event-response weights. The correlation between the two seeds of a task ranges from −0.34 to 0.92 across
  conditions, so pairing helps in some conditions and not others.
- **One comparison was made at the wrong level.** I had compared the recordings' history-controlled median with
  single simulated sessions; against medians of 16 sessions it is lower than the simulator usually produces. The 25
  November review then showed that this mostly reflects the simulator's narrow spread, and that the recordings' value
  is itself indistinguishable from zero (section 10b).
- **A small bias in the history control** (it slightly penalises the real target) was found by a reviewer check. Its
  size was not committed to any result file, so no number is quoted for it.

All of this is recorded in a dated "A18 audit note" in `AMENDMENTS.md`.

## 10b. What the 25 November review changed

On 25 November six further AI-agent reviewers (Claude subagents, again not human review) each attacked the project
from one direction: code and reproducibility, statistics and methods, every number against its result file, the
mathematical walkthrough, the course report as a grader would read it, and the repository and documentation. The
machinery held up: the tests pass, no leakage was found, the latent-model code matches exact Gaussian conditioning,
the committed results reproduce from the committed code, and several hundred numbers matched their files. What
changed was interpretation, in six places.

*One session distorts post hoc means.* The corrected score is the real out-of-fold $R^2$ minus the median over 200
fake sessions. Out-of-fold $R^2$ can be far below zero when a decoder extrapolates badly, and when both terms are
strongly negative their difference can be large either way; it is not bounded by 1. Session 4d8c7767 (SWC_038, 128
units) scores 1.59 on the post hoc ridge reference (real $R^2$ −0.94 against a fake-session median near −2.5) and
−6.30 history-controlled. The A19 sensitivity analysis, specified and committed before it ran, found:

- the registered P2 result does not depend on it (p 0.892 with it, 0.793 without; 4 then 5 of 13 mice positive; the
  session's own P2 value, −0.27, is the 4th lowest of 16, not extreme), and the registered Lasso prior gate never
  used this decoder;
- the post hoc full-population reference does depend on it: mouse mean 0.159 with it and 0.101 without; session
  median 0.108 with it and 0.087 without;
- ratios to that reference change a lot with the summary. On session medians the 0.5 s subspace keeps 0.62 of the
  full-population score (0.72 without the session), the 30 s subspace 0.06 (0.17) and PCA 0.18 (0.25). The earlier
  "about a third" for the 0.5 s subspace was a ratio of mouse means and is no longer quoted;
- the calibration target (session median 0.108) would move to 0.087 without the session, a 19% shift; the other five
  targets move by about 10% or less. The simulation was not re-run.

Session medians are now the primary descriptive summary for these post hoc quantities, a choice fixed in the A19
entry before its numbers existed.

*The stimulus-memory caution was overstated.* I had written that the corrected score is positive for any population
that encodes recent stimuli, and that memory could fake "half to 70%" of the recorded score. The simulation itself
says otherwise: with no prior and no memory the score averages −0.043; with memory at the recorded strength it is
−0.012 (no leak); only deliberately strong memory gives +0.078. The correct statement is that memory pushes the score
upward and, if strong enough, can make it positive without a prior. It is also a known issue, not a discovery.

*The recordings' history-controlled score is not evidence of anything.* I had called −0.061 an "unexplained feature"
and suggested asking the instructor about it. It is positive in 6 of 16 sessions (one-sided Wilcoxon p = 0.70),
indistinguishable from zero; it looked unusual only against the simulator's narrow spread. That question is dropped.

*The framing claimed more than the simulation supports.* The pre-set reading was "intermediate", and the outcome
table committed in A17 had no row for that case, so leading the report with "drift defeats variance ranking" would be
a post hoc choice. The profile match does not show a prior is needed (no-prior conditions match 6 and 5 of 8
features). The report now says the simulation explains part of the pattern.

*My explanation for the latent model's failure was wrong.* I had suggested that subtracting its previous-stimulus
input removed the prior. An AI-agent diagnostic (scratch only, not committed) re-ran the readout on four simulated
sessions subtracting only the slow time basis; the prior score barely changed (for example 0.017 to 0.050 against a
full-population 0.25). So that is not the reason, and no reason is now offered. The failure is scoped to the
specification tested; it keeps only about 15% of the prior even without drift; no positive control was run; and the
gate's 50% threshold is above what lagged RRR itself keeps without drift (41%).

*Smaller corrections.* P2 is "not supported" rather than "failed". The calibration fits six strengths to six targets,
so its match is by construction. Some numbers were corrected: seed-pair correlations −0.34 to 0.92 (not 0.52 to
0.92); task-level intervals 19 to 39% wider for conditions with a prior (not 10 to 25%); the achieved slow share in
calibration was 22.5% (the recordings' target is 22.6%). The prior-history statistics (0.64; 41, 81 and 86%) now have
a committed source, `results/a19/prior_history.json`, and the unsourced −0.058 is dropped. All reviews are labelled as
AI-agent reviews. A17 part 6 is formally dropped.

## 11. The latent model: tested, failed its gate, stopped

After this briefing was first written, a review you pasted recommended one bounded test of the latent model on the
simulated sessions, with a stopping rule, and nothing more. That test (A18 part B) was specified and committed before
any result, then run.

The model is fitted trial by trial to the pre-stimulus windows: 8 latents, each with its own timescale, with the slow
cosine drift basis and the previous trial's stimulus, choice and reward as known inputs. The prior is decoded from each
trial's own latent estimate, so the model cannot build a prior by accumulating past stimuli. It had to pass two
checks, judged over 16 tasks. First, with realistic drift it must keep at least half of what the full population
decodes (B1). Second, with stimulus memory alone it must not report a comparable prior (B2).

| Condition | Latent model | Tasks positive | Full population |
|---|---|---|---|
| Calibrated prior, no drift | 0.026 | 13 of 16 | 0.170 |
| Calibrated prior, realistic drift | −0.003 | 8 of 16 | 0.167 |
| Memory alone | −0.020 | 6 of 16 | 0.078 |
| No prior, no memory | −0.025 | 6 of 16 | −0.043 |

B1 failed, so the work stops: the model is not run on the recordings and no variant is tried. It isn't fooled by
memory, but it doesn't keep a genuine prior either, and even without drift it keeps only about 15% of what the full
population decodes. The conclusion is limited to this specification (these inputs, 8 latents, a single-trial
readout), not to latent models in general. Three things limit what the failure says. No positive control was run for
the latent model. Because it keeps so little even without drift, its failure under drift says little about drift in
particular. And the gate's 50% threshold is above what lagged RRR itself keeps without drift (41%).

I had suggested that subtracting the previous-stimulus input removed the prior. An AI-agent diagnostic on 25 November
(run in a scratch folder, not committed) re-ran the readout on four simulated sessions subtracting only the slow time
basis; the prior score barely changed (for example 0.017 to 0.050, against a full-population 0.25). So that is not
the explanation, and no explanation is offered.

**What this means for the plan.** The analysis is finished apart from the A19 sensitivity check, which is done and
committed (`9cd4a62` specification, `97b272b` results). All remaining time goes to the report:

| Dates | Work |
|---|---|
| 25 Nov – 3 Dec | Rewrite the report around the registered hypothesis and its failure, the observed timescales, the partial simulation and the limitations; 9-page main text |
| 4–5 Dec | Check every number against its file; finish docs |
| 6–7 Dec | Your AI-use statement; submit |

## 12. Decisions that are yours

1. **How to frame the report.** The outcome table committed in A17 has no row for the simulation's "intermediate"
   verdict, so any framing is a post hoc choice and should be labelled as one. My suggestion: lead with the registered
   hypothesis and its non-support, then the measured timescales, then "in a calibrated simulation, drift of the
   recorded strength removes a realistic prior from the 30 s subspace; this explains part of the recorded pattern,
   not all of it, and does not establish drift as the cause", then the limitations, including the known
   stimulus-memory issue. P1–P3 stay first in the abstract either way.
2. **Whether to raise the stimulus-memory issue with the instructor or TA.** It is a known limitation of decoding the
   ideal-observer prior, not a new finding, so the useful question is whether acknowledging it as a limitation is
   enough or a previous-trial control is expected. (The earlier idea of asking about the recordings' −0.061 is
   dropped: that value is indistinguishable from zero.)
3. **The AI-use statement.** It is yours to write, after checking the course's disclosure requirements. It should
   say that Claude designed, coded, ran and analysed A17, A18 and A19, and that the reviews were AI-agent reviews,
   which catch mistakes but are not independent human verification, so it should also say which parts you inspected
   and checked yourself. A factual inventory of the AI-performed tasks is provided separately.
4. **The default branch, or a merge.** GitHub currently shows `master` (the frozen study) by default. Options: merge
   `pilot-timescale-fix`, make it the default branch, or keep `master` with a pointer to the branch. Branches are not
   merged without the author's approval.
5. **Whether this briefing stays public.** It is addressed to you and is not part of the academic report; it can stay
   in the repository with its header note, be rewritten in your voice, or be untracked.

## 13. Where everything is

- **GitHub:** `mandra-thomas/predictive-neural-subspaces-`. Branch `master` is the project at the talk plus one
  commit that adds the results folders (the talk state itself is tag `freeze-2026-11-23-post-talk`); branch
  `pilot-timescale-fix` has everything since.
- **The record of every decision:** `AMENDMENTS.md` (A17, its review note, A18 parts A and B with their addendum and
  notes, the dated note dropping A17 part 6, and A19, all at the end).
- **Every number, with its source file:** `RESULTS.md`, sections "Timescale follow-ups (A17)", "Calibrated
  simulation (A18 part A)", the latent-model gate (A18 part B) and the A19 sensitivity analysis.
- **Every run:** `ANALYSIS_LOG.md`.
- **Results:** `results/a17/`, `results/a18/` (the simulation figure is `results/a18/a18_simulation.pdf`) and
  `results/a19/` (sensitivity analysis and prior-history statistics).
- **Office-hours notes:** `slides/office_hours_2026-11-24.md`; timescale figure `figures/slide_timescales.pdf`.
- **Code:** `src/pns/timescales.py`, `src/pns/sim_a18.py`, `src/pns/synth.py`, `src/pns/lds.py` (run on simulated
  sessions only, never on recordings); scripts 23 to 28.
- **Key commits on the pilot branch:** `0dbca28` (A17 written), `8486770` (A17 parts 1–2), `2b27bb6` (review
  corrections), `3a81ba1` (A18 written, before any simulation), `2f7611d` (addendum), `a42056b` (simulation results),
  `91d431d` (audit corrections), `1a233eb` (latent-model gate written, before any result), `371a43c` (gate result:
  failed, stop), `9cd4a62` (A19 written, before any A19 number), `97b272b` (A19 results).
- **The mathematical walkthrough:** `reports/math_walkthrough/math_walkthrough.pdf` (every analysis as the exact
  quantity computed, and every result in those terms).

## Glossary

- **Block prior:** the ideal observer's probability that the next stimulus is on the left, given all stimuli so far.
- **Lagged RRR:** finds the few directions of current activity that best predict activity a fixed time later.
- **Readout / loading basis:** the directions RRR reads from now / the directions it predicts later.
- **Pseudo-session correction:** subtract the score obtained with fake block sequences from the task's own generator.
- **Corrected $R^2$:** real decoding $R^2$ minus the median fake one; 0 means "no better than fake". It is not
  bounded by 1, because out-of-fold $R^2$ can be far below zero.
- **Drift / slow component / session-time mode:** activity that changes steadily over the session.
- **Low-rank vs per-unit drift:** drift shared by all units through a few processes, vs independent in each unit.
- **History-controlled score:** the prior score after removing what the last five stimuli explain, in the real and
  in every fake target.
- **Pre-registered / post hoc:** committed before the data were analysed / designed after the results were known.
- **AI-agent review:** a review run by Claude subagents, not by an independent human.
- **Capture:** the fraction of the full population's prior score that a subspace keeps.
