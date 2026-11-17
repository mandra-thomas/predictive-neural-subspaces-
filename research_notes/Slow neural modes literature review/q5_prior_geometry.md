# Q5: Neural population geometry of prior / expectation signals (block priors, base rates, history biases): high- vs low-variance, static vs dynamical dimensions, relation to slow dynamics

Compiled 2026-11-17. This is part of a systematic literature review on slow neural modes and predictive subspaces in IBL Brain-Wide Map data.

**Search methodology (systematic-review record)**

Sources searched:
- Web search, standard and extended modes. This mostly surfaced Google-Scholar-style results from nature.com, biorxiv.org, PMC, eLife, publisher repositories and lab pages.
- Direct full-text fetches from bioRxiv and PMC.
- The local IBL `paper-brain-wide-map` code repository in this project (`paper-brain-wide-map/brainwidemap/decoding/…`), used to check the decoding settings.
- The Nature full text (paywall redirect) and the Zador-lab PDF (more than 10 MB) could not be fetched, so the 2023 bioRxiv v3 full text was used as the primary source for Findling et al.
- Two fetches of bioRxiv 10.64898/2025.12.15.694430 failed with HTTP 429.

Exact queries, in order:
1. "Findling 2025 Nature brain-wide representations of prior information mouse"
2. "prior encoded low-variance dimensions neural population block prior subspace" (extended)
3. "Posani "rarely categorical, always high-dimensional" mouse cortex"
4. "Sohn Narain Meirhaeghe Jazayeri 2019 Neuron Bayesian computation through cortical latent dynamics prior curvature"
5. "block prior IBL neural dynamics subspace slow drift "block" prior mouse cortex population geometry 2024 2025 preprint" (extended)
6. "trial history coding cortex population Hattori Komiyama 2023 history information distributed; Akrami 2018 posterior parietal history"
7. "Kobak 2016 eLife demixed principal component analysis explained variance condition-independent stimulus decision small fraction"
8. "Langdon Engel 2025 Nature Neuroscience latent circuit inference context-dependent decision making prefrontal"
9. "Aoi Mante Pillow 2020 Nature Neuroscience prefrontal cortex multidimensional dynamic encoding context low-dimensional"
10. "Remington Narain Hosseini Jazayeri 2018 Neuron flexible sensorimotor computations rapid reconfiguration cortical dynamics tonic input initial condition"
11. "Darlington Beck Lisberger 2018 Nature Neuroscience neural implementation Bayesian inference prior FEF gain"
12. "Cowley Snyder Smith 2020 Neuron slow drift neural activity impulsivity axis V4 PFC"
13. "prior expectation encoded orthogonal subspace choice preparatory activity mouse frontal cortex trial history 2024" (extended)
14. "Meirhaeghe Sohn Jazayeri 2021 Neuron precise adaptive neural mechanism predictive temporal processing frontal cortex"

Full-text fetches:
- Findling et al. bioRxiv 2023.07.04.547684v3 (first ~100k of 230k characters, which covers the Results and most of the Methods).
- Posani et al. PMC11601379 (first ~100k of 159k characters).

Local code inspected: `settings_template.py`, `settings_for_BWM_figure/settings_block.py`, and `meta/fig_motor_correlates_prior.py`.

Inclusion criteria: the paper or preprint (2013–2026, with 2019–2026 prioritized; older works only as necessary anchors) reports neural population data or models that say something about at least one of the following:
- how a prior, expectation, context or trial-history variable is represented: dimensionality, subspace, variance share, orthogonality to other variables, temporal stability or dynamics;
- methods that determine whether such signals are visible to variance-based or predictability-based dimensionality reduction;
- confounds (slow drift, arousal, movement) for slowly varying latent variables.

Exclusion criteria:
- Purely behavioral studies of history bias with no neural geometry (e.g., GLM-HMM behavioral papers), except as context.
- Single-neuron-only studies with no population analysis, unless they establish a mechanism such as gain.
- Studies of non-prior variables with no transferable methodological point.

Rough counts:
- About 14 search queries returned about 140 distinct result items. About 45 were screened at title/abstract level and 2 full texts were read in part.
- About 30 works are included below: 12 verified from abstract/metadata or full text this session, and the remainder flagged as background.

Verification tags used below:
- **[V-full]** means the content was verified this session from full text or code.
- **[V-abs]** means it was verified from the abstract, metadata or search-result snippet only.
- **[BG]** means background knowledge from the established literature that was not re-fetched this session. The URL points to the DOI. Treat specific details as needing a check before citation in a manuscript.

---

## Key Question 1: Findling et al. (IBL prior paper; bioRxiv 2023 → Nature 2025). How was the prior decoded, how much variance or how many neurons carry it, and is there any analysis of dimensionality, subspace, dynamics, or "prior as integrator / slow dynamics"?

### Takeaway
Findling et al. treat the prior purely as a decoding target. They use L1-regularized linear regression (Lasso) on spike counts in a single pre-stimulus window, with pseudosession nulls to control for slow drift. They report how many regions carry the prior (roughly 20–30%) and the effect sizes as corrected R². They do not analyse dimensionality, variance share, subspace orientation, orthogonality to choice or stimulus, or within-session neural dynamics of the prior. The only "dynamical" content is behavioral and timescale-level. The favored action-kernel model is an exponential (leaky-integrator) average of past choices, and timescales fitted to neural activity correlate with behavioral timescales. The claim that the loopy network is Bayesian is an untested interpretation. The question of whether the prior lives in a static low-variance direction or a slow dynamical mode is therefore open, and it is the niche the student project could fill.

### Cited Findings
- Publication status: Findling, Hubert, International Brain Laboratory et al., "Brain-wide representations of prior information in mouse decision-making," *Nature* 645:192–200 (published online 2025-09-03), doi 10.1038/s41586-025-09226-1. [V-abs] — [Nature](https://www.nature.com/articles/s41586-025-09226-1); [UNIGE record](https://archive-ouverte.unige.ch/unige:188000); [Princeton record](https://collaborate.princeton.edu/en/publications/brain-wide-representations-of-prior-information-in-mouse-decision/). The preprint is bioRxiv 2023.07.04.547684 (v3 read) — [bioRxiv v3](https://www.biorxiv.org/content/10.1101/2023.07.04.547684v3.full).
- Task: the stimulus appeared left or right with prior probability alternating between 0.2 and 0.8 in blocks of variable length. Mice estimate this prior and use it to improve accuracy. The abstract claims the subjective prior is encoded in "at least 20% to 30% of brain regions" spanning all processing levels, including LGd and VISp. [V-abs] — [UNIGE abstract](https://archive-ouverte.unige.ch/unige:188000).
- Decoder (electrophysiology): L1-regularized linear regression (scikit-learn `Lasso`, single α). The authors chose L1 "because it is more robust to outliers from single-cell drift." The input is binned spike counts per unit, about 72 units per session on average. [V-full] — [bioRxiv v3](https://www.biorxiv.org/content/10.1101/2023.07.04.547684v3.full).
- Decoder (widefield imaging, WFI): Ridge (L2) on ΔF/F pixels per region, chosen because pixel features are collinear. [V-full] — [bioRxiv v3](https://www.biorxiv.org/content/10.1101/2023.07.04.547684v3.full).
- Decoding window: the intertrial interval (ITI) window in the prior paper is −600 to −100 ms relative to stimulus onset for ephys and frame −2 (about −132 to −66 ms) for WFI. The post-stimulus window is 0 to +100 ms. [V-full] — [bioRxiv v3](https://www.biorxiv.org/content/10.1101/2023.07.04.547684v3.full).
  - The companion IBL Brain-Wide Map decoding code uses a different window for block prior ("pLeft"): −400 to −100 ms relative to `stimOn_times`, one 300-ms bin, Lasso estimator, 200 pseudosessions, and the initial unbiased block excluded. [V-full, local code] — `paper-brain-wide-map/brainwidemap/decoding/settings_for_BWM_figure/settings_block.py` and `settings_template.py` in this project; the BWM paper is [IBL Brain-Wide Map bioRxiv](https://www.biorxiv.org/content/10.1101/2023.07.04.547681v2.full.pdf). **The student should state which window they replicated.**
- Hyperparameters were chosen by nested 5-fold cross-validation averaged over 10 seeds. [V-full] — [bioRxiv v3](https://www.biorxiv.org/content/10.1101/2023.07.04.547684v3.full).
- Target: the Bayes-optimal prior estimate rather than the true block identity, because mice are not cued. Log-odds and an action-kernel prior are also decoded. [V-full] — [bioRxiv v3](https://www.biorxiv.org/content/10.1101/2023.07.04.547684v3.full). The Nature version also says the Bayes-optimal prior is the appropriate target and warns that slow drift partially aligned with the block structure can produce spurious decoding. [V-abs via search snippet] — [Nature](https://www.nature.com/articles/s41586-025-09226-1).
- Null and drift control: pseudosessions (citing Harris 2020) are counterfactual block and stimulus sequences drawn from the task's generative process. The real R² must exceed the 95th percentile of the pseudosession null. Effect sizes are reported as "corrected R²" (real R² minus the null median), because slow drift alone produces nonzero R². Regions are combined with Benjamini–Hochberg at 1% FDR. A separate analysis (Fig. S7) shows the decoded prior predicts choices after controlling for drift. [V-full] — [bioRxiv v3](https://www.biorxiv.org/content/10.1101/2023.07.04.547684v3.full).
- Region counts and effect sizes. [V-full] — [bioRxiv v3](https://www.biorxiv.org/content/10.1101/2023.07.04.547684v3.full)
  - Ephys, ITI: 29.5% of regions (47/159) significant before correction.
  - Ephys and WFI merged at 1% FDR: 21.3% (57/267).
  - Ephys, post-stimulus: 20.7% (33/159).
  - WFI: all 32 dorsal-cortex regions significant in the ITI.
  - Example region ORBvl: 107 neurons, corrected R² = 0.16, p = 0.005.
  - Ephys and WFI corrected R² correlate across regions (Spearman R = 0.57, N = 31).
  - Regions that encode the prior in the ITI tend to encode it post-stimulus (Spearman R = 0.25 for ephys, 0.65 for WFI).
- Single neurons: the prior is visible in single-neuron PSTHs (Fig. S3), but the excerpt read here did not quantify a fraction of neurons. [V-full] — [bioRxiv v3](https://www.biorxiv.org/content/10.1101/2023.07.04.547684v3.full).
- Neurometric analysis: a signed-contrast decoder is applied post-stimulus, and its curves are split by whether the prior is above or below 0.5. The vertical shift at zero contrast indexes the prior. This measure is less sensitive than direct decoding (10.6% vs 29.5% of ephys regions). [V-full] — [bioRxiv v3](https://www.biorxiv.org/content/10.1101/2023.07.04.547684v3.full).
- Embodiment and eye confounds. [V-full] — [bioRxiv v3](https://www.biorxiv.org/content/10.1101/2023.07.04.547684v3.full)
  - DeepLabCut body features (paws, whisking, licking) decode the prior in 40.5% (43/106) of sessions.
  - Neural decoding of the prior residual, after regressing out video features, survives, and its R² correlates with the full R² (Spearman R = 0.79, N = 242).
  - Eye position decodes the prior in a way that correlates with VISp/LGd decoding (R = 0.48), but the residual analysis is again robust (R = 0.85).
  - Pupil was not covered in the excerpt read.
  - The local repo contains `meta/fig_motor_correlates_prior.py`, which computes 7 ITI behaviors at −0.6 and −0.4 s lags against pseudo-blocks. [V-full, local code]
- Action-kernel vs Bayes-optimal, and timescales. [V-full] — [bioRxiv v3](https://www.biorxiv.org/content/10.1101/2023.07.04.547684v3.full)
  - Behaviorally, the action-kernel model (exponential smoothing of previous actions; median decay constant 5.6 trials) beats the Bayes-optimal and stimulus-kernel models.
  - The action-kernel prior gives higher uncorrected ITI decoding R² than the Bayes-optimal prior (N = 341 sessions).
  - Inverse decay constants fitted to neural activity correlate with behavioral ones (ephys R = 0.31, N = 71; WFI R = 0.42, N = 49), but not for stimulus kernels (Fig. S14).
  - The authors say the action-kernel prior cannot be tested for regional significance with pseudosessions, because no null exists without the exact behavioral generative model.
- Dynamics and network modeling: there is no integrator, RNN, or dynamical-systems fit of the neural prior signal. The Discussion interprets the brain-wide distribution as consistent with a "loopy" multidirectional Bayesian network. It calls building such a neural model "a pressing, remaining task" and notes compatibility with linear probabilistic population codes. [V-full] — [bioRxiv v3](https://www.biorxiv.org/content/10.1101/2023.07.04.547684v3.full).
- A December 2025 bioRxiv preprint (10.64898/2025.12.15.694430) reportedly fits a simple circuit model to brain-wide IBL responses with prior-driven bias and gain modulation, and checks it against the true block prior. Full text could not be retrieved (HTTP 429). Title, authors and claims are **unverified**. [search snippet only] — [bioRxiv](https://www.biorxiv.org/content/10.64898/2025.12.15.694430v1.full.pdf).

The action-kernel prior that best explains behavior is itself a first-order linear dynamical system driven by actions. In the local repo it is implemented as `expSmoothing_prevAction`. With $a_t \in \{0,1\}$ the previous choice and learning rate $\alpha$ (decay of about 5.6 trials, so $\alpha \approx 1/5.6$), the update is

$$\hat{\pi}_{t+1} = (1-\alpha)\,\hat{\pi}_t + \alpha\, a_t .$$

This is a leaky integrator in trial time, updated at discrete events. It is not a continuous-time autonomous slow mode.

### Inferences
- Findling et al. establish that the prior is linearly decodable and widespread. They are silent on where the decoding weights sit relative to the population's dominant covariance. Lasso yields sparse weight vectors, so a successful Lasso decode is compatible with the signal living in a few neurons or in a direction of small population variance. The student's result (decodable from the full population but absent from the top 5 PCs) fits this and does not contradict the paper.
- Corrected R² values are modest (e.g., 0.16 in a strong example region), and decoding needs pseudosession correction. Both point to a small-amplitude signal relative to trial-to-trial variability, which is what a "small static modulation" account predicts.
- The neural-vs-behavioral timescale correlation (R ≈ 0.3–0.4) is the only Findling result that touches "prior as dynamics." It operates in trial-index time, not in seconds-scale autonomous dynamics, and it is consistent with an event-driven, input-updated state that is held roughly constant between updates.
- Neither paper version tests whether the prior signal is stationary within a trial (e.g., the same decoder axis across ITI, stimulus and movement epochs). The fact that ITI-encoding regions also encode post-stimulus shifts weakly suggests persistence across the trial, but no cross-temporal generalization matrix is reported in the excerpt read.

### Gaps
- The Nature 2025 Methods and Extended Data could not be read (paywall, and the PDF exceeded 10 MB). It is unknown whether the published version added any subspace, cross-temporal or dimensionality analysis absent from preprint v3. **Check the Nature Extended Data before claiming novelty.**
- Whether MOs (M2) was among the significant regions, and its corrected R², was not extracted.
- Whether pupil was used as a confound control was not covered in the excerpt read.
- The content of the December 2025 IBL circuit-model preprint (bias vs gain, static vs dynamic prior) is unverified.

---

## Key Question 2: What other work characterizes the geometry or dynamics of prior / expectation / history / context signals (Jazayeri lab, Lisberger, history coding, context subspaces, latent circuits)?

### Takeaway
In primate timing tasks (Jazayeri lab), priors and contexts are explicitly geometric and dynamical. Priors warp (compress or curve) low-dimensional task manifolds. Context acts as a tonic input or initial-condition offset that sets the speed of dynamics, rather than as a separately evolving slow mode. In smooth pursuit (Lisberger), the prior acts through preparatory activity that sets a gain. In context-dependent decisions (Mante, Aoi, Langdon/Engel), context is a low-dimensional input axis that reconfigures dynamics or suppresses irrelevant inputs. History and value signals in rodents are distributed and can be stable across trial epochs. Across this literature, the dominant model is a static or tonic offset or input that shapes dynamics. None of these studies quantified the variance share of the prior axis.

### Cited Findings
- **Sohn, Narain, Meirhaeghe & Jazayeri 2019, *Neuron* 103:934–947** (doi 10.1016/j.neuron.2019.06.012) [V-abs]. In a time-interval reproduction task in monkey frontal cortex (DMFC), prior statistics "warp neural representations." RNNs indicate this relies on a low-dimensional curved manifold, framed as the "curved manifold hypothesis": the curvature of trajectories is the substrate for Bayesian estimation, so priors shape behavior by sculpting latent dynamics. — [PMC6805134](https://pmc.ncbi.nlm.nih.gov/articles/PMC6805134); [MIT DSpace](https://dspace.mit.edu/handle/1721.1/130521)
- **Meirhaeghe, Sohn & Jazayeri 2021, *Neuron* 109:2995–3011** (doi 10.1016/j.neuron.2021.08.025) [V-abs]. DMFC dynamics speed up or slow down with the expected timing of a stimulus, so the population encodes deviation from expectation rather than raw elapsed time. When timing statistics changed without cues, responses shifted predictably toward the new mean, so the expectation is a learned, adaptive setting of dynamics. — [PMC9737059](https://pmc.ncbi.nlm.nih.gov/articles/PMC9737059)
- **Remington, Narain, Hosseini & Jazayeri 2018, *Neuron* 98:1005–1019** (doi 10.1016/j.neuron.2018.05.020) [V-abs]. In DMFC, the measured interval sets the initial condition and the sensorimotor context sets an input. Together they control the speed of the subsequent trajectory, and RNNs support these control principles. This is the canonical "context as tonic input / static offset that reconfigures dynamics" result. — [PMC6009852](https://pmc.ncbi.nlm.nih.gov/articles/PMC6009852)
- **Wang, Narain, Hosseini & Jazayeri 2018, *Nature Neuroscience* 21:102–110** ("Flexible timing by temporal scaling of cortical responses") [BG]. Medial frontal responses temporally scale with the produced interval, and in RNNs the scaling is controlled by a tonic input level. — [doi](https://doi.org/10.1038/s41593-017-0028-6)
- **Darlington, Beck & Lisberger 2018, *Nature Neuroscience* 21:1442–1451** (doi 10.1038/s41593-018-0233-y) [V-abs]. Before target motion, FEF_SEM preparatory activity encodes the speed prior and adapts in parallel with behavior. At pursuit initiation, output reflects a reliability-weighted MAP combination. The proposed mechanism is that FEF_SEM sets the gain of visual-motor transmission, and the prior can be updated locally (the latter point comes from a third-party summary). — [PMC6312195](https://pmc.ncbi.nlm.nih.gov/articles/PMC6312195)
- **Mante, Sussillo, Shenoy & Newsome 2013, *Nature* 503:78–84** [BG]. In macaque FEF/PFC, context (color vs motion) is represented along its own axis. Both relevant and irrelevant inputs are present, and selection is implemented by context-dependent recurrent dynamics (a line attractor plus context-dependent selection vectors) rather than input gating. — [doi](https://doi.org/10.1038/nature12742)
- **Aoi, Mante & Pillow 2020, *Nature Neuroscience* 23:1410–1420** [V-abs]. Model-based targeted dimensionality reduction (mTDR) shows that PFC carries a multidimensional, dynamic code for context, decision, and relevant and irrelevant inputs. There is early linear accumulation followed by rotational dynamics. The distinct dimensions come from one broadly tuned population, not separate neuron classes. mTDR recovers encoding subspaces "despite additional components of neural activity," i.e., task subspaces need not align with dominant variance. — [PMC7610668](https://pmc.ncbi.nlm.nih.gov/articles/PMC7610668)
- **Langdon & Engel 2025, *Nature Neuroscience* 28:665–675** (doi 10.1038/s41593-025-01869-7) [V-abs]. The latent circuit model fits heterogeneous responses with a small set of task variables coupled by low-dimensional recurrent connectivity. In RNNs and monkey PFC, context representations suppress irrelevant sensory responses. Patterned connectivity perturbations predicted behavioral effects. The authors argue that including causal interactions among task variables is needed to identify behaviorally relevant computations. — [PMC11893458](https://pmc.ncbi.nlm.nih.gov/articles/PMC11893458); [Engel lab](https://engel-lab.princeton.edu/news/2025/new-paper-chris-published-nature-neuroscience)
- **Akrami, Kopec, Diamond & Brody 2018, *Nature* 554:368–372** [V-abs]. In a rat auditory parametric working-memory task, PPC represents sensory-stimulus history and mediates its behavioral effect (contraction bias); optogenetic PPC inactivation reduced history effects. — [Nature](https://www.nature.com/articles/nature25510); [PMC5944836](https://pmc.ncbi.nlm.nih.gov/articles/PMC5944836)
- **Morcos & Harvey 2016, *Nature Neuroscience* 19:1672–1681** ("History-dependent variability in population dynamics during evidence accumulation in cortex") [BG; title confirmed via search]. Mouse PPC population trajectories carry previous-trial information, which contributes to trial-to-trial variability in evidence-accumulation dynamics. — [doi](https://doi.org/10.1038/nn.4403); [HMS listing](https://instrumentation.hms.harvard.edu/publications/history-dependent-variability-population-dynamics-during-evidence)
- **Hattori, Danskin, … Komiyama 2019, *Cell* 177:1858** [BG] and **Hattori & Komiyama 2022, *Neuron*** ("Context-dependent persistency as a coding mechanism for robust and widely distributed value coding") [V-abs]. Action-history and value coding are distributed across six cortical areas. Coding persistency (stability of the code across trial epochs) varies by area, learning phase and context, and is highest in retrosplenial cortex of expert mice. — [Komiyama lab PDF](https://komiyamalab.biosci.ucsd.edu/wp-content/uploads/2021/12/1-s2.0-S0896627321008916-main.pdf); [Cell 2019 doi](https://doi.org/10.1016/j.cell.2019.04.027)
- **Danskin et al. 2023, *Science Advances*** [V-abs, snippet]. Inactivating RSC, but not PPC or posterior premotor cortex (pM2), impairs the use of history information. This is relevant because the student's area (MOs/M2) may carry history without being causally required. — via search results ([Komiyama-lab related listing](https://par.nsf.gov/biblio/10612361); exact URL for Danskin not isolated, so verify)
- **Bari et al. 2019, *Neuron*** ("Stable representations of decision variables for flexible behavior") [BG]. In mouse frontal cortex, relative-value/decision variables are encoded persistently and stably across trial epochs, including the ITI. This is the closest rodent precedent for a slowly varying belief carried as a stable (static-across-epochs) representation. — [doi (verify)](https://doi.org/10.1016/j.neuron.2019.06.001)
- **Siniscalchi, Phoumthipphavong, Ali, Lozano & Kwan 2016, *Nature Neuroscience* 19:1234** [BG]. M2 ensembles show both fast and slow transitions in rule/context representation during switching. M2 is the student's region. — [doi](https://doi.org/10.1038/nn.4342)
- **"Localized and global representation of prior value, sensory evidence, and choice in male mouse cerebral cortex," *Nature Communications* 2024** [V-abs, snippet]. Prior value is represented both locally and globally across mouse cortex, with medial prefrontal neurons combining reward expectation with sensory input. — [Nat Commun](https://www.nature.com/articles/s41467-024-48338-6)
- **"Abstract deliberation by visuomotor neurons in prefrontal cortex," *Nature Neuroscience* 2024** [V-abs, snippet]. Prior stimulus expectations shape formation of the categorical choice but not the action plan, and categorical and motor signals evolve in orthogonal subspaces (primate PFC). — [Nat Neurosci](https://www.nature.com/articles/s41593-024-01635-1)
- **"Prior expectation enhances sensorimotor behavior by modulating population tuning and subspace activity in the sensory cortex," bioRxiv 2022.12.04.516847** [V-abs, snippet; publication status unverified]. In primate MT, targeted dimensionality reduction shows the prior modulating population tuning and subspace activity. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2022.12.04.516847.full.pdf)
- **Berkes, Orbán, Lengyel & Fiser 2011, *Science* 331:83–87** [BG]. In ferret V1, spontaneous activity statistics converge with development toward stimulus-evoked activity averaged over natural scenes, which is interpreted as a learned prior (an internal model) expressed in spontaneous activity. This is a contrasting notion of "prior": a distributional prior in the structure of ongoing variability, not a scalar block prior. — [doi](https://doi.org/10.1126/science.1195870)

### Inferences
- The primate literature mostly frames priors and contexts as inputs or initial conditions that set the trajectory of fast within-trial dynamics. The prior variable itself is static within a trial and its effect is expressed through dynamics. This aligns with the student's "small static modulation" hypothesis more than with a "slow autonomous mode" hypothesis.
- No study in this set reports what fraction of population variance the prior or context axis captures, or tests whether the prior axis is predictable from the population's own past, which is what lagged RRR tests. These metrics are absent from this literature rather than contradicted.
- Two mechanisms coexist in the literature: additive offset (preparatory or baseline shift; Findling, Darlington preparatory activity) and multiplicative gain (Darlington; possibly the 2025 IBL circuit preprint). A gain-type prior would be invisible to methods that look for an additive direction in baseline activity, but it should appear as a stimulus × prior interaction.

### Gaps
- The items "Gupta 2024 prior in mouse," "Le Merre," "Noel," "Rossi-Pool," "Rajalingham" and "Bondanelli" from the brief were not located or verified in a prior-geometry context within the search budget.
  - Gupta et al. 2024 is likely the Brody-lab paper on trial-history biases producing apparent lapses, which is behavioral and model-based.
  - Rossi-Pool et al. (PNAS 2019/2021) reported large condition-independent temporal components with smaller coding components in premotor cortex, but this was not re-verified.
- Pinto/Brody on accumulated history geometry was not found.

---

## Key Question 3: Is there work explicitly showing priors or context are carried in low-variance dimensions, and how do variance-share and high-dimensionality results (dPCA, Stringer 2019, Posani 2024/2026, Manley 2024) bear on this?

### Takeaway
No paper was found that explicitly reports a block prior or base-rate expectation as residing in low-variance population dimensions, or that measures its variance share. Indirect support is strong:
- dPCA and related work show that task-coding components carry a minority of variance compared with condition-independent and movement-related components.
- Stringer 2019 and Musall 2019 show that the top variance dimensions in mouse cortex are dominated by spontaneous behavior and arousal.
- Posani et al. (IBL data, block prior included) show near-maximal shattering dimensionality, so task variables are linearly separable without dominating variance.
- Manley 2024 shows that dimensionality keeps growing with neuron count.

An explicit demonstration on IBL data that the block prior is low-variance and non-autonomous would be novel.

### Cited Findings
- **Kobak et al. 2016, *eLife* 5:e10989** (dPCA) [V-abs]. dPCA decomposes activity into components tied to stimulus, decision, time and their interactions, applied to four datasets. Per-variable variance shares were not extracted this session. [BG] In the paper's figures, condition-independent (time) components typically capture the largest share of variance and stimulus or decision components smaller shares, so this needs checking before quoting numbers. — [eLife](https://elifesciences.org/articles/10989); [PMC4887222](https://pmc.ncbi.nlm.nih.gov/articles/PMC4887222)
- **Stringer, Pachitariu, Steinmetz, Reddy, Carandini & Harris 2019, *Science* 364:eaav7893** [BG]. Spontaneous facial behaviors predict a large share of mouse cortical activity across many dimensions. Stimulus-related activity overlaps only partly with the behavior-related subspace. This implies that top PCs in awake mice are dominated by movement and arousal, not task variables. — [doi](https://doi.org/10.1126/science.aav7893)
- **Musall, Kaufman, Juavinett, Gluf & Churchland 2019, *Nature Neuroscience* 22:1677** [BG]. Uninstructed movements explain more single-trial cortical variance than task variables. This directly predicts that a block prior will not be found in top PCs of dorsal-cortex or M2 activity. — [doi](https://doi.org/10.1038/s41593-019-0502-4)
- **Posani, Wang, Muscinelli, Paninski & Fusi, bioRxiv 2024.11.15.623878** ("Rarely categorical, always high-dimensional…"), IBL Brain-Wide Map data, about 43 cortical regions [V-full, partial]. [V-abs] A later *Nature* (2026) version is reportedly titled "Rarely categorical, highly separable representations along the cortical hierarchy" (doi 10.1038/s41586-026-10668-4, dated 15 July 2026 per a press piece), but the final title and date are unverified. — [PMC11601379](https://pmc.ncbi.nlm.nih.gov/articles/PMC11601379/); [SciTechDaily](https://scitechdaily.com/a-massive-study-reveals-the-brain-is-far-more-flexible-than-we-thought/)
  - The encoding model includes the **block prior** (p(left) = 0.8 vs 0.2) alongside contrast, side, choice, reward, wheel, whisking and lick.
  - The conditions-space analysis uses stimulus side, whisking, **block** and contrast.
  - Shattering dimensionality is near maximal in all regions (mean SD = 0.92 ± 0.06).
  - Block helped drive VISp selectivity clusters.
  - **No variance share is reported for block or any other variable.**
  - The paper notes that representations "can have the generalization properties of low dimensional disentangled representations and still possess the maximal shattering dimensionality."
- **Manley et al. 2024, *Neuron*** ("Simultaneous, cortex-wide dynamics of up to 1 million neurons reveal unbounded scaling of dimensionality with neuron number") [BG]. Dimensionality increases without saturation as more neurons are recorded. Behavior-related dimensions account for a limited part of the variance, and many reliable dimensions are unrelated to measured behavior. — [doi (verify)](https://doi.org/10.1016/j.neuron.2024.02.011)
- **Aoi et al. 2020** [V-abs]. mTDR recovers task-encoding subspaces "despite additional components of neural activity," which is methodologically aligned with targeting low-variance, task-defined axes rather than PCs. — [PMC7610668](https://pmc.ncbi.nlm.nih.gov/articles/PMC7610668)
- **Kaufman, Churchland, Ryu & Shenoy 2014, *Nature Neuroscience* 17:440** (output-null) [BG] and **Semedo et al. 2019, *Neuron*** (communication subspaces via reduced-rank regression; the predictive subspace is low-dimensional and not aligned with the source's dominant dimensions) [BG]. These are precedents for task-relevant or communicated signals living outside the top-variance dimensions. — [Kaufman doi](https://doi.org/10.1038/nn.3643); [Semedo doi](https://doi.org/10.1016/j.neuron.2019.01.026)
- **Clark, Livezey & Bouchard 2019, NeurIPS** (Dynamical Components Analysis, DCA) [BG]. DCA finds projections maximizing predictive information (past → future), independent of variance. PCA and variance-weighted predictive methods can miss low-variance but highly predictable (slow) signals. — [arXiv 1905.09944](https://arxiv.org/abs/1905.09944)

Why a decodable prior can be absent from the top PCs: suppose the prior $\pi_t$ adds a small offset $\delta\,\pi_t\,u$ along a unit direction $u$ on top of noise with covariance $\Sigma$. Its contribution to variance along $u$ is $\delta^2 \operatorname{Var}(\pi)$, and it enters the top-$k$ PCs only if that is comparable to the $k$-th eigenvalue $\lambda_k$. Linear decodability instead scales with the signal-to-noise quantity

$$\delta^2\, u^\top \Sigma^{-1} u ,$$

which can be large when $u$ points into low-noise directions, even though $\delta^2 \operatorname{Var}(\pi) \ll \lambda_5$.

### Inferences
- Combining Musall/Stringer (movement and arousal dominate top variance) with Posani (block linearly separable in a high-dimensional code) and Findling (modest corrected R²), one expects a priori that the block prior lies outside the top 5 PCs of M2. The student's PCA null result is therefore expected rather than surprising. It becomes informative only if quantified, for example as the fraction of decoder-weight norm or decodable R² captured by the top-k PCs versus the rest, using a variance-matched random-subspace null.
- Lagged reduced-rank regression ranks dimensions by **predicted variance**. A persistent but low-amplitude prior offset can be perfectly predictable yet carry too little variance to enter low-rank RRR subspaces, the same logic as the PCA argument. Absence from RRR subspaces therefore does not by itself show that the prior is non-dynamical. A variance-normalized predictability test (DCA, CCA between past and future, slow feature analysis, or simply the autocorrelation of the projection onto the prior-decoder axis) is needed before claiming "not a slow dynamical mode."

### Gaps
- No published variance-explained figure for the IBL block prior was found in any brain region.
- No study found tests the predictability (autonomous dynamics) of the prior axis as distinct from its decodability.
- Specific dPCA variance-share numbers were not extracted.
- Manley 2024 and Stringer 2019 details are background, not re-verified.

---

## Key Question 4: How have block-prior or other slowly varying latent signals been related to slow drift, arousal and engagement confounds, and how were they controlled?

### Takeaway
Slow drift is the central confound for any block-prior analysis, because blocks are themselves slow, autocorrelated latent processes. The IBL standard is pseudosession nulls plus corrected R², plus video, eye and DLC residual controls. The primate literature shows that a shared slow-drift axis exists, co-varies with arousal and impulsivity, and is not the same as a task-coding axis. No study found explicitly tests whether the block-prior axis is orthogonal to the session's slow-drift or arousal axis.

### Cited Findings
- **Findling et al.** [V-full]: [bioRxiv v3](https://www.biorxiv.org/content/10.1101/2023.07.04.547684v3.full)
  - Pseudosession nulls with corrected R² (real minus null median).
  - A separate drift-controlled behavioral-prediction analysis (Fig. S7).
  - L1 chosen partly for robustness to single-cell drift.
  - Video (DLC) and eye-position residualization.
  - The Nature version warns that slow drift partially aligned with block structure produces spurious decoding ([Nature](https://www.nature.com/articles/s41586-025-09226-1), [V-abs via snippet]).
- **IBL Brain-Wide Map preprint** [V-abs, snippet]. It notes that slow drift creates temporal correlations across trials when assessing block effects on single cells. The BWM code generates pseudo-blocks for motor-correlate nulls (`generate_pseudo_blocks` in `meta/fig_motor_correlates_prior.py`, [V-full, local code]). — [bioRxiv](https://www.biorxiv.org/content/10.1101/2023.07.04.547681v2.full.pdf)
- **Harris 2020, "Nonsense correlations in neuroscience," bioRxiv** [BG; cited by Findling, V-full]. Autocorrelated variables (like blocks) correlate spuriously with drifting neural signals. The proposed remedy is a null generated from the variable's own generative process, i.e., pseudosessions. — [doi](https://doi.org/10.1101/2020.11.29.402719)
- **Cowley, Snyder, Acar, Williamson, Yu & Smith 2020, *Neuron* 108:551–567** [V-abs]. A slow drift (tens of minutes) shared by V4 and PFC populations co-varies with the animal's slowly fluctuating tendency to report changes (impulsivity) and does not change stimulus encoding. A follow-up associates slow drift with arousal. — [PMC7822647](https://pmc.ncbi.nlm.nih.gov/articles/PMC7822647); [CSHL PDF](https://repository.cshl.edu/41559/1/Slow%20Drift%20of%20Neural%20Activity%20as%20a%20Signature%20of%20Impulsivity%20in%20Macaque%20Visual%20and%20Prefrontal%20Cortex.pdf)
- **Hennig et al. 2021, *Nature Neuroscience* 24:727** ("Learning is shaped by abrupt changes in neural engagement") [BG]. A high-variance "neural engagement" axis in motor cortex fluctuates with behavioral state. This is an example of a slow, state-like signal dominating top variance. — [doi](https://doi.org/10.1038/s41593-021-00822-8)
- **Ashwood et al. 2022, *Nature Neuroscience*** (GLM-HMM on IBL behavior) [BG]. Mice switch between engaged and biased or disengaged strategy states lasting many trials. This is a behavioral slow latent state that can partially co-vary with block structure, so a candidate confound or covariate. — [doi](https://doi.org/10.1038/s41593-021-01007-z)

### Inferences
- A plausible and testable picture is that the top PCs and top lagged-RRR modes in M2 capture slow drift, arousal and engagement plus movement, which are high-variance and autonomous (predictable from the past). The block prior is a small, event-updated offset in a different direction. Showing this requires:
  - the angle between the prior-decoder axis and the top PCs and top RRR modes, against a random-direction null;
  - the variance captured along the prior axis;
  - the autocorrelation and predictability of the prior-axis projection within blocks versus across block switches;
  - whether the prior-axis projection jumps at action or feedback events (input-driven) rather than drifting smoothly (autonomous).
- Because blocks average about 50 trials and switch unannounced, the 0.5–30 s horizons in the student's RRR span roughly 0.1–10 trials. A prior that is constant within blocks should be highly predictable over these horizons if it is held in activity. If it is not predictable, that favors either very low SNR on the prior axis or maintenance in non-spiking (e.g., synaptic) state that is re-expressed each trial. Distinguishing these requires the variance-normalized tests above.

### Gaps
- No paper found tests the alignment between the IBL block-prior axis and the slow-drift or arousal axis (e.g., pupil-predicted axis). Whether Findling Nature 2025 included pupil regressors is unverified.
- No paper reports within-ITI or within-block stationarity of the prior axis in IBL data.

---

## Key Question 5: Overall assessment. What is known vs open, and does the "prior as small static modulation, not slow dynamical mode" route complement Findling et al. 2025?

### Takeaway
What is known:
- Brain-wide linear decodability of the prior, controlled against drift and movement (Findling).
- Behavioral-level leaky-integrator (action-kernel) dynamics, with matched neural timescales (Findling).
- Priors and contexts acting as inputs or initial conditions that shape fast within-trial dynamics (Jazayeri lab, Remington, Mante).
- Gain-based prior effects (Lisberger).
- High-dimensional, linearly separable coding of block in IBL cortex (Posani).

What is open, and unaddressed by Findling:
- the variance share and subspace orientation of the prior;
- whether the prior axis is autonomous or predictable versus event-updated;
- whether the prior is orthogonal to slow drift, arousal and movement dimensions;
- whether the prior axis is stable across trial epochs and sessions.

A carefully controlled brain-wide geometry analysis would therefore be a genuine complement to Findling et al. 2025, as long as it avoids conflating "low-variance" with "non-predictable."

### Cited Findings
- Findling et al. leave building a neural model of loopy inference as "a pressing, remaining task," and fit no dynamical model to the neural prior signal. [V-full] — [bioRxiv v3](https://www.biorxiv.org/content/10.1101/2023.07.04.547684v3.full)
- The action-kernel (exponential smoothing of past actions) model wins behaviorally, and neural and behavioral timescales correlate (R ≈ 0.31–0.42). [V-full] — [bioRxiv v3](https://www.biorxiv.org/content/10.1101/2023.07.04.547684v3.full)
- Posani et al. include block in IBL dimensionality analyses but report no variance share. [V-full] — [PMC11601379](https://pmc.ncbi.nlm.nih.gov/articles/PMC11601379/)
- The Jazayeri-lab framework treats context and priors as initial-condition, input and curvature controls of low-dimensional dynamics. [V-abs] — [Remington 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6009852); [Sohn 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6805134)

### Inferences
- Recommended framing: "The prior is carried as a low-variance, event-updated offset that is largely orthogonal to the high-variance, autonomously predictable (slow-drift, movement, arousal) subspace." This is distinct from, and complementary to, Findling's "where" result. It connects to the Jazayeri "prior as input or initial condition" literature, and it contrasts with any "prior as persistent slow attractor mode" hypothesis.
- The main threat to validity is that variance-ranked methods (PCA, low-rank RRR) are structurally blind to low-variance signals. The claim "not a slow dynamical mode" therefore needs a variance-agnostic predictability test (DCA, past–future CCA, or the autocorrelation of the decoder-axis projection), not only RRR at rank k.
- A second threat is window choice: the prior paper uses −600 to −100 ms and the BWM code uses −400 to −100 ms. The student should report which window they used and show robustness.
- A third check is mechanism: a gain-type prior (stimulus × prior interaction) would be missed by baseline-offset analyses. The neurometric-shift analysis in Findling and the 2025 IBL circuit preprint (unverified) suggest both additive and gain components are worth testing.

### Gaps
- Unverified: whether Findling Nature 2025 Extended Data added any geometry analysis.
- Unverified: whether the December 2025 IBL circuit-model preprint addresses static vs dynamic prior representation.
- Unverified: whether Posani's Nature 2026 version adds per-variable variance analyses.
- These three items are the highest-priority checks before asserting novelty.
