# Project briefing: where everything stands

*Written 24 November 2026 for Gunnar, to read in one sitting. It starts from the original question and ends with what
to do before the 7 December deadline. Section 9 says what is established and what is not; section 11 gives my
recommendation and section 12 lists the decisions that are yours.*

## 1. The short version

The project asked whether predicting further ahead pulls out the slowly changing "block prior" that a mouse uses in
the IBL task. It does not, in MOs. The pre-registered test of that idea (P2) failed, and every low-dimensional summary
of the recordings turned out to be dominated by a slow drift over the session.

Since the talk, the work has moved from "it failed" to "here is why, and here is what that means":

- **The prior is short-lived.** It forgets itself within about 12 trials (one to two minutes), far less than a
  block. Longer prediction lags make it less predictable, not more, so longer lags were never likely to tip the
  balance toward it against a drift that stays predictable all session (a heuristic argument, not a proof).
- **The prior is small.** Its share of activity is about two orders of magnitude below the slow component.
- **Lags up to 4 minutes, on drift-removed data, still select no prior.** A prediction I made in advance (that the
  prior content would fall with lag) failed: it is flat.
- **A calibrated simulation shows drift is enough to erase the prior from the 30 s subspace, though not every
  feature of the failure.** With the recorded task, units and firing rates, a prior of the recorded strength *is*
  picked up by the 30 s subspace when there is no drift, and drift of the recorded strength erases it while the full
  population still decodes it. But the 30 s subspace still slightly beats the 0.5 s one, which the recordings do not
  show, so the pre-set verdict is "intermediate", not "drift sufficient".
- **A new problem surfaced.** In the same simulation, neurons that only remember the last stimulus, with no block
  prior at all, produce a "prior" decoding score about half to 70% the size of the recorded one (in the extreme case
  where memory explains all of the recorded previous-stimulus decoding). The standard pseudo-session correction does
  not catch this. The control that removes stimulus memory also removes most of a genuine prior, and on the
  recordings it comes out lower than the simulator can produce at realistic settings, which nothing here explains.

What this is: a well-characterised negative result, a mechanism shown in simulation to reproduce most (not all) of
the recorded pattern, and a methodological caution about how the prior is measured. What it is not: a rescue of the original hypothesis, or proof of what
happens in the real brain.

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
| P2 prior rises with lag | change −0.099 [−0.218, +0.002] | 0.89 | **not supported** |
| P3 stimulus falls with lag | change +0.061 [0.028, 0.094] | 0.0061 | passed, but not as hoped |

The qualifications matter. P1's margin at 30 s is a few degrees against a floor that is itself at chance, and it
holds only in the readout basis. P3 holds because long-lag subspaces *lose* the stimulus; the 0.5 s subspace is no
better for the stimulus than a random subspace, so there is no "fast stimulus subspace". P2 is flat: no variant
(either decoder, residualised data, any dimension, any left-out mouse, either detrend) shows a rise.

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
Each new amendment was committed before the data it governs were analysed.

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

**Corrections after an outside review (24 November).** You pasted a review of the GitHub repo. It was right on four
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
current stimulus can be decoded (AUC 0.869). All six were matched within 10%. What was *not* calibrated and is an
assumption: how many independent drift processes there are and how units load on them, the shape of the stimulus
memory, the Gaussian random weights, and Poisson spiking.

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
| Recordings (mouse means) | 0.16 | −0.05 | 0.05 |

Read down the 30 s column first.

**The positive control works.** A strong prior is found in every seed, and the 30 s subspace keeps 85% of what the
full population decodes.

**Without drift, the original idea works in simulation.** With the prior at its recorded strength and no drift, the
30 s subspace carries about 40% of the full population's prior score and beats the 0.5 s subspace. A slow signal is
preferred by long-lag prediction when nothing slower competes. That is worth saying in the report: the hypothesis was
not silly; it is defeated by the drift.

**Drift at the recorded strength erases the 30 s prior score, but not the long-lag advantage.** With shared drift
tuned to the recorded slow share, the 30 s subspace's prior falls to about zero (so do the 0.5 s, PCA and random
scores), while the full population still decodes the prior as well as before. The drop is consistent across seeds
(a paired test I added after the fact: p = 0.002). A third of the drift cuts the 30 s score by about a third. But
the 30 s subspace still beats the 0.5 s one in 21 of 32 seeds (difference +0.03, interval −0.01 to +0.07), whereas in
the recordings it was clearly worse (−0.10). The reading rule written in advance therefore gives **"intermediate"**:
the simulation reproduces the *loss* at 30 s, not the recordings' advantage for the 0.5 s subspace. For independent
per-unit drift the rule gives "drift sufficient", but that verdict is fragile: that kind of drift also wrecks the
full-population decoder, fits the recordings poorly, and at three times the drift the 30 s advantage comes back.

**The simulation reproduces most of the recorded pattern.** At the recorded drift, 6 of 8 pre-chosen features fall
inside the recordings' 95% intervals, most strikingly elapsed-time decoding (30 s subspace 0.79 against 0.84; PCA 0.75
against 0.80; random subspaces 0.65 against 0.64). The two misses are the recordings' positive prior score in the 0.5 s
subspace and their negative 30 s minus 0.5 s change. A match shows the mechanism *can* produce the recorded pattern,
not that it *does*.

**Stimulus memory alone can fake much of the prior score.** The negative control as first specified showed no
leak, but calibration had made its memory trace tiny. In the added extreme case, with no prior encoded and a trace of
the last stimulus given *all* of the recorded previous-stimulus decodability, the corrected full-population "prior"
score is 0.078 (positive in 24 of 32 seeds; 12 of 16 tasks, a borderline p = 0.038): about half to 70% of the
recorded score, depending on which summary you divide by. The reason is simple: the pseudo-session correction
compares against *fake* block sequences, and neurons that remember the *real* recent stimuli correlate with the real
prior (which is built from those stimuli) but not with the fake ones. The null itself is fine (no prior, no history:
positive in only 13 of 32). This affects the original prior gate too. A memory longer than one trial would both mimic
the prior more and escape the control below.

**The control for stimulus memory works, but it is blunt, and the recordings fail it in an unexplained way.**
Regressing each target on its own last five stimuli before decoding removes the fake signal (history alone: about
zero). But the ideal prior is itself largely predictable from the last five stimuli, so the control also removes
about 85% of a genuine prior's score; it still detects a real prior without drift (23 of 32 seeds), but at the
recorded drift only in 18 of 32. In the recordings this controlled score is −0.061 (session median; 6 of 16 sessions
positive). Compared properly, against medians of 16 simulated sessions, a value that low almost never occurs in any
simulated condition at realistic drift, with or without a prior. So the recordings do something the simulator does
not: their stimulus memory may be longer or richer than assumed, their slow structure may differ, or something else.
This is an open question, not a conclusion.

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
- In a simulation matched to the recordings, drift of the recorded strength erases a realistic prior from the 30 s
  subspace, and the same simulation reproduces 6 of 8 features of the recorded pattern. It does not reproduce the
  recordings' advantage for the 0.5 s subspace (pre-set verdict: "intermediate").
- The pseudo-session-corrected prior score can be produced in large part by stimulus memory alone (in simulation,
  in an extreme but possible case).

**Not established:**

- That drift *is* what hid the prior in the real brain. The simulation shows sufficiency under assumptions, not
  cause.
- That the recordings contain a block prior beyond memory of recent stimuli. The control that could tell is blunt,
  and the recordings' controlled score is lower than the simulator explains.
- Anything about where the prior lives in MOs.

**Failed or withdrawn:**

- P2 (pre-registered): no rise of the prior with lag.
- The A17 prediction that prior content would fall with lag: it is flat.
- The claim that the prior "could not have entered" a rank-5 subspace: withdrawn (it was not a real bound).
- The ground-truth capture metric: withdrawn.
- The talk's "130 independent windows" argument: wrong, corrected.

**Labels.** Everything after the talk (A17, A18) is post hoc: designed after the original results were known. Each
part was committed before its own data were analysed, and every change after seeing something is a dated note. The
original pre-registered results are unchanged.

## 10. The independent audit

After the results were committed, two reviewers that had not seen my conclusions audited everything: one the code,
one the methods, numbers and wording. Their findings, and what changed:

- **No leak.** The current trial's stimulus never reaches the pre-stimulus window in the simulation, the prior is
  built only from earlier trials, and there is no decoder or target leakage. Every number in the write-up
  reproduced from the result files, except those listed next.
- **My wording overstated three things,** now corrected: I had written that drift "is sufficient to reproduce the
  loss" (the pre-set verdict is "intermediate"); that stimulus memory "produces most" of the recorded prior score (it
  is half to 70%, in an extreme case); and, left over from A17, that a variance-ranked objective has "no horizon" that
  favours the prior (a heuristic, not a fact). One arithmetic slip ("a third of the drift halves it"; it cuts it by
  a third) and a missing table row were fixed.
- **The seeds are not 32 independent draws.** Pairs of seeds reuse the same recorded task, so there are 16
  independent tasks. Re-counted over tasks, every pre-set verdict stands; the "history alone mimics the prior"
  verdict becomes borderline (12 of 16 tasks, p = 0.038), and intervals widen by 10 to 25%. These task-level checks
  are now computed by the committed script (`results/a18/audit_checks.json`).
- **Pairing across conditions is partial.** Spike-level noise differs, and the null condition got different
  event-response weights. Comparisons are still paired, just noisier than I had said.
- **One comparison was made at the wrong level.** I had compared the recordings' history-controlled median with
  single simulated sessions and called it unremarkable; against medians of 16 sessions it is clearly lower than the
  simulator produces at realistic settings. That reversed one of my statements (now in section 8).
- **A small bias in the history control** (it slightly penalises the real target) was found and measured; it moves
  the recordings' value only from −0.061 to −0.058.

All of this is recorded in a dated "A18 audit note" in `AMENDMENTS.md`.

## 11. Recommendation: should the latent model go ahead?

The rule written in advance says yes: the positive control passed, the history control is valid by its definition,
and at the recorded drift the full population still decodes the prior in 27 of 32 simulated sessions, so a model
that separates drift could in principle find it. Drift is what erases the prior from the 30 s subspace in
simulation, which is the situation an explicit-drift latent model is built for.

My recommendation is **yes, but only on simulated data first.** Two results make a real-data latent-model result
hard to read in either direction. First, stimulus memory alone can produce a prior score of comparable size, so a
"prior-like" latent in the recordings could be stimulus memory. Second, the control that removes stimulus memory
also removes most of a genuine prior, and the recordings fail it in a way the simulator does not explain, so a null
result would not mean much either. So the next step is part B, specified and
committed first. It would run the latent model on these same simulated conditions, including "history alone", and
go to the recordings only if the model's readout cleanly separates "prior with drift" from "history alone" in
simulation. If it cannot, stop there and write the report around the simulation. That is a perfectly good ending.

**Time budget (deadline 7 December):**

| Dates | Work |
|---|---|
| 25–26 Nov | Part B specification committed; latent model on the simulated conditions (code exists and is tested) |
| 27 Nov | Decide: real data or stop. Hard stop for the latent model |
| 28–29 Nov | Real-data latent model only if the gate passed; otherwise start the report |
| 30 Nov – 3 Dec | Rewrite the report: timescales section, simulation section, history caution, honest P1–P3 framing, 9-page main text |
| 4–5 Dec | Check every number against its file; finish docs |
| 6–7 Dec | Your AI-use statement; submit |

The report can be written from what exists now. The latent model is optional extra, not a requirement.

## 12. Decisions that are yours

1. **Go ahead with part B (the latent model on simulated data first), or stop the analysis here** and put all
   remaining time into the report.
2. **How to frame the report.** The outcome table committed in A17 points to: "a variance-ranked predictive objective
   cannot favour a one-minute prior over drift at any horizon", backed by the simulation. Given the "intermediate"
   verdict and the audit, I would soften that to: "drift of the recorded strength erases the prior from long-lag
   subspaces in a calibrated simulation, reproducing most of the recorded pattern", plus the stimulus-memory
   caution. P1–P3 stay first in the abstract either way.
3. **Whether to tell the instructor about the stimulus-memory issue** before the report. It bears on the prior gate
   that the whole project rests on.
4. **The AI-use statement.** It must say that Claude designed and ran A17 and A18, with agent review.
5. **Whether to merge** `pilot-timescale-fix` into `master` on GitHub (I never merge without you).

## 13. Where everything is

- **GitHub:** `mandra-thomas/predictive-neural-subspaces-`. Branch `master` is the project at the talk (tag
  `freeze-2026-11-23-post-talk`); branch `pilot-timescale-fix` has everything since.
- **The record of every decision:** `AMENDMENTS.md` (A17, its review note, A18 part A, its addendum and the
  post-result notes, all at the end).
- **Every number, with its source file:** `RESULTS.md`, sections "Timescale follow-ups (A17)" and "Calibrated
  simulation (A18 part A)".
- **Every run:** `ANALYSIS_LOG.md`.
- **Results:** `results/a17/` and `results/a18/` (the simulation figure is `results/a18/a18_simulation.pdf`).
- **Office-hours notes:** `slides/office_hours_2026-11-24.md`; timescale figure `figures/slide_timescales.pdf`.
- **Code:** `src/pns/timescales.py`, `src/pns/sim_a18.py`, `src/pns/synth.py`, `src/pns/lds.py` (not yet used on any
  data except tests); scripts 23 to 26.
- **Key commits on the pilot branch:** `0dbca28` (A17 written), `8486770` (A17 parts 1–2), `2b27bb6` (review
  corrections), `3a81ba1` (A18 written, before any simulation), `2f7611d` (addendum), `a42056b` (simulation results),
  `91d431d` (audit corrections).

## Glossary

- **Block prior:** the ideal observer's probability that the next stimulus is on the left, given all stimuli so far.
- **Lagged RRR:** finds the few directions of current activity that best predict activity a fixed time later.
- **Readout / loading basis:** the directions RRR reads from now / the directions it predicts later.
- **Pseudo-session correction:** subtract the score obtained with fake block sequences from the task's own generator.
- **Corrected $R^2$:** real decoding $R^2$ minus the median fake one; 0 means "no better than fake".
- **Drift / slow component / session-time mode:** activity that changes steadily over the session.
- **Low-rank vs per-unit drift:** drift shared by all units through a few processes, vs independent in each unit.
- **History-controlled score:** the prior score after removing what the last five stimuli explain, in the real and
  in every fake target.
- **Pre-registered / post hoc:** committed before the data were analysed / designed after the results were known.
- **Capture:** the fraction of the full population's prior score that a subspace keeps.
