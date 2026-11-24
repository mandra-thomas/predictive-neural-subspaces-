# Office hours, 24 November 2026: notes

Bring `figures/slide_timescales.pdf`. The report version is `report/figures/rfig_timescales.pdf`. Both are built from
`results/a17/` by script 23 (amendment A17 part 0, post hoc). They use task data only: trial times, block
probabilities and the Bayes-optimal prior.

## What the figure shows

Panel a puts every timescale on one clock. The median stimulus interval is 3.9 s. The lags I tested ran from 0.5 to
30 s. The prior's integrated timescale is about 67 s (IQR 55–75 s across sessions). Counted directly in trials it is
about 12 trials, with the autocorrelation reaching zero by 27 trials. Blocks last a median of 46 trials, which is 3.6 min
(IQR 2.4–5.2 min, 215 completed blocks). A session lasts a median of 66.5 min.

Panel b shows how much of the prior's variance is still predictable Δ ahead (ρ²). It is 0.59 at 30 s, 0.27 at 60 s and
0.02 at 2 min. A linear session ramp has ρ² = 1 at every lag.

## Answers to the questions from the talk

- **Trials vs blocks.** One block is about 46 trials, or about 3.6 min. The longest lag, 30 s, is about 8 trials.
- **"Why not minutes?"** I measured it. The prior's own autocorrelation is 0.77 at 30 s, 0.52 at 60 s, 0.10 at 2 min
  and −0.19 at 4 min, where it turns negative because blocks alternate. So the prior is mostly unpredictable beyond
  about 2 min, while the session drift stays almost perfectly predictable. A variance-ranked predictive objective has
  no horizon at which it favours the prior over the drift; longer lags make the prior less predictable, not more. That
  is the design flaw, stated correctly.
- **Retraction.** In the talk I said a 30 s lag leaves only about 130 independent windows. That was wrong. RRR uses
  every overlapping pair of bins: a 66-min session has about 7,900 bins, and a 240 s lag gives up only 480 of them.
  The real limit on any slow signal is the number of blocks per session (about 13), and that is the same at every lag.
- **"Was there a loss on the prior?"** No. The objective is unsupervised prediction of future activity, by design. The
  prior enters only at evaluation, so it is found only if it is among the largest predictable directions, and it is
  not.
- **Separate representations?** No. The 0.5 s subspace contains 92% of the 30 s subspace's leading direction.
- **Is RRR the only model?** Yes. It is the only representation model; everything else is decoders, the trial-locked
  GLM and nulls.

## Results so far (A17, post hoc; run 23 November)

- **Variance shares** (16 sessions; median share of z-scored activity):

  | Component | Median share |
  |---|---|
  | Slow component, periods of 20 min or more | 22.6% |
  | Trial-locked responses | 8.6% |
  | Block prior, pre-stimulus windows (pseudo-session corrected) | 0.20% |

  The two shares are measured differently (all bins vs pre-stimulus windows), so the honest statement is "about two
  orders of magnitude larger, under the respective measurements", not an exact ratio. A rough scale comparison (the
  prior's corrected explained variance times ρ²) is well below the 5th RRR eigenvalue in most sessions. This is
  descriptive only. It is **not** a proof that the prior could not enter a 5-D subspace: components mix within
  directions, ρ² is not a true upper limit on predictability, and the eigenvalues describe the output side while I
  decode from the input side. I withdrew that claim (AMENDMENTS, A17 review note).
- **Lag sweep to 4 min on the two detrended copies.** No lag selects the prior (60 s vs 0.5 s: p = 0.29 and 0.55;
  60 s vs PCA: p = 0.12 and 0.53). The prior I decode from these subspaces stays about the same from 0.5 s to 4 min.
  Cosine copy: 0.03–0.05, similar to PCA (0.03) and to random subspaces (0.02). Quadratic copy: about 0 at every lag.
  I had predicted a decline that follows the prior's own ρ². It did not appear. The small prior signal in these
  subspaces is what any 5-D projection carries; it is not selected through the prior's predictability.

## What I am doing now (all labelled post hoc, amendment A17/A18)

1. **Variance shares.** How much activity is low-frequency drift versus prior versus trial-locked.
2. **Lag sweep to 4 min on the detrended data.** A check of the prediction from panel b.
3. **A calibrated simulation.** The prior and the drift compete inside the same population, with a negative control
   that has no prior.
4. **A latent state-space model.** It has an explicit drift term and a learned timescale for each latent (an
   OU-kernel GPFA analogue). It is fitted trial by trial, and the prior is read from each trial's own activity, so the
   model's filter cannot integrate past stimuli into a fake prior.
5. **A descriptive block-switch alignment.**

## Questions for the instructor

1. By "a loss on the prior", did you mean a supervised term in the objective, or a prior over the latent dynamics (as
   in GPFA's GP prior)?
2. Should the latent model be indexed by trial (one pre-stimulus vector per trial) or by 0.5 s bin?
3. Is a linear-Gaussian state-space model with per-latent AR(1) timescales an acceptable stand-in for GPFA, or would
   you expect GPFA itself?
