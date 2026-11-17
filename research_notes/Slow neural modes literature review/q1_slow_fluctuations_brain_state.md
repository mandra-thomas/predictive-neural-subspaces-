# Slow fluctuations ("slow drift", infraslow activity, time-on-task) in neural population activity and their links to internal/behavioral state

**Search methodology (systematic-review record)**

Search engines and sources: web search (general engine, "standard" and "extended" modes), which surfaced records from PubMed Central, bioRxiv, eLife, Nature, Cell Press (Neuron, Current Biology), eNeuro, J Neurosci, arXiv, Research Square, author and institutional repositories, and press releases. Full text was fetched directly from PMC, eNeuro and an institutional PDF where possible. Google Scholar forward-citation lists could not be queried directly with these tools. Instead, forward trails were followed through the reference lists and citing text of the 2022 and 2026 Smith-lab papers (which cite Cowley 2020).

Exact queries run (13 web searches):
1. `slow drift neural activity impulsivity Cowley 2020 Neuron`
2. `slow drift population activity macaque 2023 2024 Smith Yu pupil arousal`
3. `infraslow pupil fluctuations neuronal firing mouse eNeuro 2022`
4. `brain-wide within-session time-on-task slow neural dynamics mouse Neuropixels satiety engagement 2024 2025`
5. `Sadeh Clopath 2022 eLife contribution of behavioural variability to representational drift`
6. `Hennig 2021 Nature Neuroscience learning shaped by abrupt changes in neural engagement`
7. `brain-wide slow fluctuations task engagement mouse decision-making Neuropixels arousal disengagement 2023 2024 2025 bioRxiv`
8. `representational drift confounded by behavioral state running pupil arousal visual cortex 2023 2024`
9. `internal state latent variable slowly varying across session multiple brain regions mice "brain-wide" pupil engagement GLM-HMM neural 2024 2025 Nature Neuroscience`
10. `Stringer 2019 Science spontaneous behaviors drive multidimensional brainwide activity facial motion variance explained`
11. `"slow drift" mouse neuropixels population activity arousal brain-wide 2025`
12. `"Internal state is at least two dimensional" Amjad Hiratani` (no useful hits)
13. (Plus full-text fetches of 4 papers; 3 further fetches failed: Nature paywall redirect for Steinmetz 2019, and binary PDFs for Allen 2019 and the Amjad/Hiratani preprint that could not be converted to text locally.)

Inclusion criteria: primary empirical or analysis papers (2014–2026, priority 2019–2026) that (a) characterize slow (tens of seconds to hours) shared fluctuations in neural population activity, or (b) link such fluctuations or within-session changes to arousal, engagement, impulsivity, satiety/motivation, fatigue or time-on-task, or (c) address whether "representational drift" is confounded by behavioral state. Species: macaque, mouse (plus one zebrafish and one human paper as context). Exclusion: pure fMRI/EEG resting-state papers without single-unit population data (except where they bridge to spiking); sleep-only studies; press releases and aggregator summaries (used only to locate primaries); papers on electrode-drift engineering except where they bear directly on the artifact-vs-state question.

Rough counts: about 130 search results screened (about 10 per query); about 40 distinct candidate papers identified; 30 included below. Of those, 6 were checked against full text or the publisher abstract page in this session, about 9 against search-result abstracts or snippets, and the rest from prior knowledge of the literature (marked).

Verification tags used below:
- **[FT]** means verified this session against full text (PMC, eNeuro or a repository).
- **[ABS]** means verified this session against the abstract, publisher page or search-engine abstract snippet only.
- **[MEM]** means not re-verified this session. Bibliographic details and findings are from prior knowledge of the literature. The report writer should treat these as needing a citation check before final use. DOIs marked [MEM] are given as best-known and should be confirmed.

---

## Q1. What characterizes slow drift / slow shared fluctuations in monkey population activity, and what are they linked to?

### Takeaway
In macaques, a single dominant "slow drift" axis (timescale of roughly 10–45 min) is shared across V4, PFC, SC and motor cortex. It explains most of the variance of slowly varying population activity, co-varies with pupil size, false-alarm/hit rate and reaction time, and is interpreted as an arousal- or impulsivity-like internal state, not a change in sensory encoding. Faster shared gain fluctuations (Goris, Ecker, Rabinowitz) and attention-linked cortical state changes (Engel) are a related but distinct, trial-to-second-scale literature.

### Cited Findings

**Cowley, Snyder, Acar, Williamson, Yu & Smith (2020), Neuron 108(3):551–567, DOI 10.1016/j.neuron.2020.07.021, "Slow drift of neural activity as a signature of impulsivity in macaque visual and prefrontal cortex" [FT]**
- Two rhesus macaques with Utah arrays in V4 and dorsolateral PFC (area 8Ar), orientation-change detection task with spatial cueing. Sessions averaged 2.3 h and 3.0 h; 24 and 19 sessions analysed. Median 32 V4 and 60 PFC units. (The STAR Methods mention three animals and 96 electrodes, while the Results say two animals and 100 electrodes, an internal inconsistency in the paper.) — [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC7822647)
- Method: stimulus-evoked residual spike counts (400 ms bins, mean response per orientation subtracted), 20-min running average in 6-min steps, then PCA. The first PC is the "slow drift axis" and explains about 70% of slow variance (69% and 77% in the two monkeys). Single-trial residuals were projected and smoothed with a 9-min Gaussian. Drift timescale was about 33 min (monkey 1) and 44 min (monkey 2). — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7822647)
- Behavior: hit rate and false-alarm rate drifted together over about 13–16 min timescales with no change in task conditions. The drift correlated with a behavioral pattern (higher hit rate, false-alarm rate and pupil diameter, shorter RT and trial duration) that explained 60% of behavioral variance. Example per-session correlations were rho = 0.72 and 0.64 (hit rate) and 0.27 and 0.67 (false-alarm rate). — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7822647)
- V4 and PFC drifts were nearly identical within session (median absolute rho = 0.96 and 0.93) versus 0.68 for a random-walk null and 0.81 for a 1-h control. Drift magnitude correlated across areas across sessions (rho about 0.6). Drift variance exceeded the spatial-attention effect by a factor of 1.8 and 6.6. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7822647)
- Interpretation: subtracting drift from V4 improved decoding of false alarms, which supports an "impulsivity" model (drift biases the decision and overrides sensory evidence) over a "sensory bias" model. Downstream areas are proposed to remove the drift from the sensory readout. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7822647); [bioRxiv preprint](https://www.biorxiv.org/content/10.1101/2020.01.10.902403.full.pdf)
- Artifact controls: units kept only if spike waveforms were stable across 10 session bins. Drift persisted without visual stimuli and during very still fixation, which argues against an eye-movement or microsaccade explanation. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7822647)
- Note the two-step logic relevant to the student project: the slow drift axis is defined per session by PCA on slow averages, and the sign is aligned across sessions using stimulus-orientation responses. Reproducibility of the axis direction within session (for example, split halves) is not, as far as the fetched text shows, a reported test. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7822647)

**Johnston, Snyder, Khanna, Issar & Smith (2022), Cerebral Cortex, DOI 10.1093/cercor/bhab418, "The eyes reflect an internal cognitive state hidden in the population activity of cortical neurons" [ABS]**
- Follow-up in two monkeys: the slow drift in V4/PFC was associated with evoked pupil size and microsaccade rate, which ties the drift to an arousal-like state readable from the eyes. — [DOI](https://doi.org/10.1093/cercor/bhab418); [bioRxiv](https://www.biorxiv.org/content/10.1101/2020.06.29.178251.full.pdf)

**Johnston, Snyder, Schibler & Smith (2022), eNeuro 9(3), ENEURO.0012-22.2022, DOI 10.1523/ENEURO.0012-22.2022, "EEG signals index a global signature of arousal embedded in neuronal population recordings" [FT]**
- Two macaques, 100-channel Utah array in V4 plus 8 scalp EEG electrodes and eye tracking, orientation-change detection. — [eNeuro](https://www.eneuro.org/content/9/3/ENEURO.0012-22.2022)
- Slow-drift timescale was 32.3 min (SD 14.4) versus 9.3 min (SD 5.9) for prestimulus alpha power. The timescales correlated across sessions (r = 0.40). — [eNeuro](https://www.eneuro.org/content/9/3/ENEURO.0012-22.2022)
- Prestimulus alpha (8–12 Hz only; theta, beta and gamma were not significant) correlated negatively with slow drift (median r = −0.34), with pupil size (median r = −0.35) and with false-alarm rate (median r = −0.28). — [eNeuro](https://www.eneuro.org/content/9/3/ENEURO.0012-22.2022)
- The paper motivates its work with the mouse literature (Stringer 2019 PC1 tracking whisking, pupil and running; Musall 2019) but contains no mouse analysis of its own. — [eNeuro](https://www.eneuro.org/content/9/3/ENEURO.0012-22.2022)

**Johnston & Smith, "Brain-wide arousal signals are segregated from movement planning in the superior colliculus", eLife RP99278, DOI 10.7554/eLife.99278 [FT of the PMC version]**
- Status: an eLife reviewed preprint (v1 and v2 exist) with a Version of Record listed on PMC as 2026. The PMC page also references a bioRxiv posting dated June 2025, while search results describe a 2024 reviewed preprint. The exact dates should be checked. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13246003/); [eLife reviews](https://elifesciences.org/reviewed-preprints/99278v2/reviews)
- Two macaques (25 and 26 sessions), 16-channel linear array in SC plus Utah array in PFC (8Ar), memory-guided saccade task. Slow drift axis defined as PC1 of delay-period residuals averaged in 15-min windows stepped every 3 min (the same approach as Cowley 2020, including waveform-stability and abrupt-change exclusions). — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13246003/)
- SC slow drift shared variance with PFC slow drift: median 0.26. Pupil size explained a median 0.06 of SC drift variance (p < 0.001 vs shuffle); microsaccade rate only 0.003. Neurons with higher motor (saccade) index loaded much less on the drift axis (mean squared loading 0.01 vs about 0.15–0.17). The pupil axis aligned with the drift axis better than the saccade-tuning axis did. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13246003/)
- Interpretation: a brain-wide arousal signal is present in SC but is routed largely to non-motor neurons, i.e. orthogonalized from movement planning. The paper cites Joshi & Gold 2022 and Collins et al. 2023 (LC–cortex recordings) and Setzer et al. 2022 (brain-wide fluctuations) as related; these were not verified here. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13246003/)

**Hennig, Oby, Golub, Bahureksa, Sadtler, Quick, Ryu, Tyler-Kabara, Batista, Chase & Yu (2021), Nature Neuroscience 24(5):727–736, DOI 10.1038/s41593-021-00822-8, "Learning is shaped by abrupt changes in neural engagement" [ABS]**
- Monkeys, motor cortex (Utah arrays) during BCI learning. Large, abrupt fluctuations of population activity along a "neural engagement" axis occurred when the task changed (e.g., pauses or BCI-mapping perturbations), accompanied by pupil dilation. Engagement then decayed over the course of learning. The engagement changes shaped how quickly different targets were learned, even when they were not helpful for performance. — [author PDF](https://homes.cs.washington.edu/~mgolub/publications/2021-Hennig-NN.pdf); [CMU press release, secondary](https://www.cmu.edu/news/stories/archives/2021/april/engagement-learning.html)
- The 2026 Johnston & Smith paper cites Hennig 2021 as showing a signal similar to slow drift in several cortical areas. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13246003/)

**Behavioral slow drifts in decision criterion (method debate) [ABS]**
- An arXiv paper, "Limitations of a proposed correction for slow drifts in decision criterion" (2022), shows that slow drifts in choice criterion are hard to correct statistically, and cites Cowley 2020 as neural evidence for slow criterion drift. Authors were not verified in this session. — [arXiv 2205.10912](https://arxiv.org/pdf/2205.10912)

**Shared gain / modulator literature (faster timescales; context) [MEM]**
- Goris, Movshon & Simoncelli (2014), Nature Neuroscience 17:858, "Partitioning neuronal variability": much of the super-Poisson variability in macaque V1/V2/MT is explained by a slowly fluctuating multiplicative gain. — [DOI 10.1038/nn.3711](https://doi.org/10.1038/nn.3711)
- Ecker, Berens, Cotton, ... Tolias (2014), Neuron, "State dependence of noise correlations in macaque primary visual cortex": noise correlations in V1 are largely due to a shared global state fluctuation (higher under anesthesia). — [DOI 10.1016/j.neuron.2014.02.006](https://doi.org/10.1016/j.neuron.2014.02.006)
- Ecker, Denfield, Bethge & Tolias (2016), J Neurosci, "On the structure of neuronal population activity under fluctuations in attentional state": fluctuations in attentional state, as a shared gain, produce low-rank correlation structure. Cited from memory; DOI not checked.
- Rabinowitz, Goris, Cohen & Simoncelli (2015), eLife 4:e08998, "Attention stabilizes the shared gain of V4 populations": V4 activity is explained by a few latent modulators, and attention reduces the variance of a shared gain modulator. — [DOI 10.7554/eLife.08998](https://doi.org/10.7554/eLife.08998)
- Engel, Steinmetz, Gieselmann, Thiele, Moore & Boahen (2016), Science 354:1140, "Selective modulation of cortical state during spatial attention": V4 columns show spontaneous on/off (synchronous) state transitions on a sub-second to seconds scale. Attention increases on-state duration, and on-states predict better behavior. — [DOI 10.1126/science.aag1420](https://doi.org/10.1126/science.aag1420)
- Okun, Steinmetz, ... Harris (2015), Nature 521:511, "Diverse coupling of neurons to populations in sensory cortex": "population coupling" (mouse and monkey), i.e. neurons differ in how strongly they follow the population rate. — [DOI 10.1038/nature14273](https://doi.org/10.1038/nature14273)

### Inferences
- The monkey slow drift is consistently roughly one-dimensional (PC1 explains about 70% of slow variance) and shared across areas. That is qualitatively the same signature as the student's "1-D slow mode tracking elapsed time". However, Cowley et al. emphasize non-monotonic drift on a 30–45 min timescale that co-varies with behavior, whereas a monotonic time-in-session ramp is a weaker test of a genuine state, because many artifacts (electrode drift, cell loss) are also monotonic.
- The Smith lab defines the slow drift axis per session from 15–20-min averages. With sessions of 1–3 h, this gives only a handful of independent samples per session. That argues for caution about "direction reproducibility" claims in either direction, and the student's split-half non-reproducibility might partly reflect few effective degrees of freedom rather than absence of a state.
- The monkey slow drift has external anchors (pupil, alpha EEG, false-alarm rate, RT). These are the validation criteria a brain-wide mouse study would need to meet in order to call a slow mode a "state" rather than an artifact.

### Gaps
- No verified paper (2021–2026) tested within-session reproducibility of the slow-drift axis direction (e.g., split halves), which is the specific failure mode the student observed.
- Could not access full text of Hennig 2021 to extract effect sizes (variance along the engagement axis, pupil correlation).
- Could not verify Joshi & Gold 2022, Collins et al. 2023 or Setzer et al. 2022 (cited in Johnston & Smith) in this session.
- Did not find a 2023–2025 Smith/Yu paper specifically extending slow drift to more areas beyond SC (V4, PFC, SC, M1 covered). This absence is from search results only, not exhaustive citation tracking.

---

## Q2. What links slow/infraslow population activity to arousal, movement, engagement and satiety in mice?

### Takeaway
In mice, the dominant spontaneous population fluctuations are tied to arousal and movement (pupil, running, whisking, facial motion), are brain-wide and are high-dimensional at fast timescales. Infraslow (below 0.1 Hz) population rate is strongly coherent with pupil. Within-session state changes (thirst/satiety, engagement) have been shown to reorganize brain-wide activity (Allen 2019, Steinmetz 2019). However, these studies used state labels (satiety, engagement, pupil) as regressors, rather than discovering and validating an unsupervised slow mode and testing its stability.

### Cited Findings

**Okun, Steinmetz, Lak, Dervinis & Harris (2019), Cerebral Cortex 29(5):2196–2210, DOI 10.1093/cercor/bhz023, "Distinct structure of cortical population activity on fast and infraslow timescales" [FT]**
- Mouse medial PFC (mostly prelimbic) with chronic silicon probes and Neuropixels. 26 recordings, 775 neurons. Head-fixed sessions of 1.5–3 h with pupil tracking; freely moving sessions of 4–8 h. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6458908)
- Population-rate power below 1 Hz was several-fold higher than the sum of single-neuron power, i.e. strongly correlated slow fluctuations. Coherence of single neurons with the population at 0.01–0.1 Hz was typically 0.2–0.4. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6458908)
- At 0.1 Hz and below, the population rate was highly coherent with pupil area. 65% of neurons (350/541) were significantly coherent with pupil at 0.03 Hz, with a bimodal phase (two groups about pi apart, i.e. positively and negatively arousal-coupled cells). Spiking led pupil. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6458908)
- At 0.3 Hz and below, 28% or more of cells were anti-phase with the population (versus about 5% at 10 Hz and above). A neuron's slow coupling was unrelated to its fast coupling, and pupil coherence was unrelated to fast population coupling (P = 0.85). Spike-train spectra followed a power law over 0.01–1 Hz with exponent about 0.39. The authors conclude that fast and infraslow population structures are distinct processes with distinct mechanisms. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6458908)
- Search for the user-suggested "eNeuro 2022 infraslow pupil–firing coupling" mouse paper did not find it. The eNeuro 2022 paper found is the macaque Johnston et al. EEG paper (Q1). A 2024 PLoS Biology paper on dLGN tonic and burst spikes coupled to pupil across timescales was surfaced but not verified. — [search hit, PLoS Biol PDF](https://oa-fund.ub.uni-muenchen.de/1290/2/journal.pbio.3002614.pdf)

**Stringer, Pachitariu, Steinmetz, Reddy, Carandini & Harris (2019), Science 364:eaav7893, DOI 10.1126/science.aav7893, "Spontaneous behaviors drive multidimensional, brainwide activity" [ABS]**
- Two-photon imaging of about 10,000 V1 neurons plus 8-probe Neuropixels recordings across forebrain regions. Spontaneous activity is high-dimensional; 128 shared variance components captured 86% of reliable variance. A 16-dimensional summary of orofacial movements predicted about 45% of explainable variance (preprint figure; press reports "about one-third", so the published number should be checked). Similar behavior encoding was found across forebrain regions. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7029483); [bioRxiv](https://www.biorxiv.org/content/10.1101/306019v2.full.pdf)
- The first PC of the population tracked arousal variables (running, pupil, whisking), as summarized in Johnston et al. 2022. — [eNeuro](https://www.eneuro.org/content/9/3/ENEURO.0012-22.2022)

**Steinmetz, Zatka-Haas, Carandini & Harris (2019), Nature 576:266–273, DOI 10.1038/s41586-019-1787-x, "Distributed coding of choice, action and engagement across the mouse brain" [ABS; Nature full text blocked]**
- About 30,000 neurons in 42 regions (Neuropixels), visual discrimination task. Brain-wide pre-stimulus activity predicted engagement on individual trials and across the task. Engagement was associated with enhanced subcortical and suppressed neocortical activity. — [ResearchGate record](https://www.researchgate.net/publication/337579254_Distributed_coding_of_choice_action_and_engagement_across_the_mouse_brain)
- [MEM] Late-session disengagement (as mice become sated) was part of how engaged and disengaged epochs were defined. Not re-verified.

**Allen, Chen, Pichamoorthy, Tien, Pachitariu, Luo & Deisseroth (2019), Science 364:eaav3932, DOI 10.1126/science.aav3932, "Thirst regulates motivated behavior through modulation of brainwide neural population dynamics" [ABS]**
- About 24,000 neurons in 34 brain regions (Neuropixels) recorded as thirsty mice drank to satiety over a session. Brainwide activity persisted throughout each trial and correlated with the behaviorally measured satiety state. Every brain area contained neurons with diverse task responses. — [Science PDF via Luo lab](https://luolab.stanford.edu/sites/g/files/sbiybj20556/files/media/file/allen_et_al_science_2019_0.pdf); [Science author PDF](https://www.science.org/cms/asset/02018fb1-c912-4a68-9dee-f94a720a1855/pap.pdf)
- Optogenetic stimulation of thirst-sensing (hypothalamic lamina terminalis/MnPO) neurons in sated mice reinstated drinking and restored the brainwide "thirsty" population state. — [Luo lab PDF](https://luolab.stanford.edu/sites/g/files/sbiybj20556/files/media/file/allen_et_al_science_2019_0.pdf)
- This is the closest existing precedent for a satiety-linked, brain-wide, within-session slow change in mouse population activity, and it uses a causal manipulation to argue it is a genuine state rather than drift. It was a Go/No-Go odor task, not the IBL task.

**Jacobs, Steinmetz, Peters, Carandini & Harris (2020), Current Biology, "Cortical state fluctuations during sensory decision making" [ABS]**
- Widefield calcium imaging across dorsal cortex during a visual task. Low-frequency (about 3–6 Hz) global fluctuations were related to engagement, not accuracy: mice were less likely to respond at all during increased slow oscillations, but no more likely to respond incorrectly. Variations in low-frequency fluctuations were predominantly global and related to task engagement. — [Current Biology](https://www.cell.com/current-biology/fulltext/S0960-9822(20)31437-8); [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7758730/)

**Fast-local and slow-global neural ensembles in the mouse brain (2023), Network Neuroscience 7(2):731 [ABS]**
- Using brain-wide (Stringer/Steinmetz 8-probe) Neuropixels data: below 1 s, ensembles were localized within single regions; above 1 s, ensembles spanned multiple brain regions. This directly supports the idea that slower timescales are dominated by brain-wide shared modes. Authors not verified this session (believed Delaney & O'Donnell). — [MIT Press](https://direct.mit.edu/netn/article/7/2/731/114967/Fast-local-and-slow-global-neural-ensembles-in-the); [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10312261/)

**Arousal/movement–cortex foundational papers [MEM]**
- Musall, Kaufman, Juavinett, Gluf & Churchland (2019), Nature Neuroscience 22:1677, "Single-trial neural dynamics are dominated by richly varied movements": in widefield and 2-photon data, uninstructed movements explain far more single-trial cortical variance than task variables. — [DOI 10.1038/s41593-019-0502-4](https://doi.org/10.1038/s41593-019-0502-4)
- Reimer, Froudarakis, Cadwell, Yatsenko, Denfield & Tolias (2014), Neuron 84:355, "Pupil fluctuations track fast switching of cortical states during quiet wakefulness". — [DOI 10.1016/j.neuron.2014.09.033](https://doi.org/10.1016/j.neuron.2014.09.033)
- Reimer, McGinley, ... McCormick & Tolias (2016), Nature Communications 7:13289, "Pupil fluctuations track rapid changes in adrenergic and cholinergic activity in cortex". — [DOI 10.1038/ncomms13289](https://doi.org/10.1038/ncomms13289)
- McGinley, David & McCormick (2015), Neuron 87:179, "Cortical membrane potential signature of optimal states for sensory signal detection": an inverted-U relation between pupil-indexed arousal and auditory detection performance. — [DOI 10.1016/j.neuron.2015.05.038](https://doi.org/10.1016/j.neuron.2015.05.038)
- Vinck, Batista-Brito, Knoblich & Cardin (2015), Neuron 86:740, "Arousal and locomotion make distinct contributions to cortical activity patterns and visual encoding". — [DOI 10.1016/j.neuron.2015.03.028](https://doi.org/10.1016/j.neuron.2015.03.028)
- Ashwood, Roy, Stone, IBL, Urai, Churchland, Pouget & Pillow (2022), Nature Neuroscience 25:201, "Mice alternate between discrete strategies during perceptual decision-making": GLM-HMM on IBL behavior reveals engaged and disengaged (biased) states lasting many trials. This is behavior only, but on exactly the IBL task. — [DOI 10.1038/s41593-021-01007-z](https://doi.org/10.1038/s41593-021-01007-z); [bioRxiv](https://www.biorxiv.org/content/10.1101/2020.10.19.346353v2.full.pdf)
- Marques, Li, Schaak, Robson & Li (2020), Nature 577:239, "Internal state dynamics shape brainwide activity and foraging behaviour" (larval zebrafish): whole-brain imaging reveals slowly alternating exploit/explore states lasting minutes, controlled by a serotonergic (dorsal raphe) state signal. This is a non-mouse precedent for brain-wide, unsupervised discovery of slow internal states. — [DOI 10.1038/s41586-019-1858-z](https://doi.org/10.1038/s41586-019-1858-z)

**Recent mouse arousal/engagement work (2024–2026) [ABS, snippet-level]**
- A 2026 bioRxiv preprint, "Baseline activity of V1 interneurons connects pupil-linked arousal to engaged behavioral state", reports an inverted-U (Yerkes-Dodson-like) relation between baseline pupil and probability of an engaged (GLM-HMM) state. — [bioRxiv](https://www.biorxiv.org/content/10.64898/2026.02.05.704022v2.full)
- A 2026 bioRxiv preprint, "Task engagement gates interareal communication geometry in the mouse thalamocortical–midbrain visual circuit", reports that engagement reduced network activity, participation and dimensionality across the hierarchy (engaged vs passive comparison, not slow drift). — [bioRxiv](https://www.biorxiv.org/content/10.64898/2026.09.15.751810v1)
- A 2024 (updated 2025) preprint with Neuropixels in mouse auditory cortex reports that sound discriminability peaks at intermediate pupil-indexed arousal. — [ResearchHub PDF of bioRxiv 2024.04.04.588209](https://storage.prod.researchhub.com/uploads/papers/2025/11/14/2024.04.04.588209v3.full.pdf)

### Inferences
- In mice, the expected "genuine" slow shared mode is pupil/arousal-coupled, brain-wide, and present in both positively and negatively coupled neuron groups (Okun 2019). A real state mode should therefore show (a) mixed-sign loadings, (b) coherence with pupil and movement at below 0.1 Hz, and (c) shared structure across simultaneously recorded regions. An electrode-drift artifact would instead tend to show depth-ordered, same-sign rate changes on neighbouring channels and no pupil coherence.
- Allen 2019 and Steinmetz 2019 establish that within-session motivational changes (thirst to satiety, engagement to disengagement) move brain-wide activity. In IBL sessions, mice also work toward satiety (water-restricted, about 1 h sessions), so a monotonic "time-in-session" mode in M2 is a priori plausible as satiety/engagement-related.

### Gaps
- Could not verify the specific "eNeuro 2022 infraslow pupil–firing coupling" mouse paper named in the assignment. It may be misremembered, or it may be the macaque Johnston et al. 2022 eNeuro paper.
- Could not extract full-text quantities from Allen 2019 (fraction of neurons tracking satiety, dimensionality of the state signal, number of trials to satiety) or Steinmetz 2019 (engagement-index definition); access failed in this session.
- Did not verify the McGinley/Reimer/Vinck/Musall/Ashwood/Marques details this session ([MEM]).

---

## Q3. Representational drift versus behavioral-state confounds

### Takeaway
Whether "representational drift" in mouse cortex reflects slow behavioral/arousal changes is contested on the same Allen Brain Observatory data. Deitch et al. 2021 and Marks & Goard 2021 argue arousal does not explain drift. Sadeh & Clopath 2022 argue behavioral variability (running, pupil) contributes substantially. Reviewers of Sadeh & Clopath pressed them to disentangle behavior from elapsed time, which is exactly the confound in the student's time-tracking slow mode.

### Cited Findings
- **Sadeh & Clopath (2022), eLife 11:e77907, DOI 10.7554/eLife.77907 [ABS + peer reviews].** Reanalysis of Allen Brain Observatory (2-photon and Neuropixels) data shows that behavioral variability (running speed, pupil) substantially contributes to apparent representational drift in V1, higher visual areas and hippocampus. Modeling is consistent with behavior modulating activity independently of stimulus over slow timescales. Preprint January 2022; published 30 August 2022. — [eLife](https://elifesciences.org/articles/77907v1); [PDF](https://elifesciences.org/articles/77907.pdf)
- The eLife peer review stated that behavioral contributions to response variability are well established and asked the authors to separate behavior from elapsed time, noting the title claim needs analysis that controls for time. The bioRxiv version stated that passage of time per se did not contribute strongly to drift. — [eLife peer reviews](https://elifesciences.org/articles/77907/peer-reviews); [bioRxiv v2](https://www.biorxiv.org/content/10.1101/2022.01.02.474731v2.full)
- **Deitch, Rubin & Ziv (2021), Current Biology 31(19):4327, "Representational drift in the mouse visual cortex" [ABS].** Allen Brain Observatory 2-photon and Neuropixels data. Drift accumulates over minutes to days. Running speed and pupil area dipped early in movie-repeat blocks, but the authors conclude that drift is not driven by systematic declines in firing rate, changes in behavioral state or adaptation. — [Current Biology](https://www.cell.com/current-biology/fulltext/S0960-9822(21)01052-6); [bioRxiv](https://www.biorxiv.org/content/10.1101/2020.10.05.327049v1.full)
- **Marks & Goard (2021), Nature Communications 12:5169, DOI 10.1038/s41467-021-25436-3, "Stimulus-dependent representational drift in primary visual cortex" [ABS].** Chronic 2-photon V1 imaging. Drift is stronger for naturalistic movies than gratings. Pupil fluctuations, tracked in a subset (n = 4 mice), were not sufficient to explain progressive drift. — [Nature Communications](https://www.nature.com/articles/s41467-021-25436-3)
- **arXiv 2305.11953 (2023), "Representational drift changes the encoding of fast and slow-varying natural scene features differently" [ABS].** Notes that variability in pupil size, running speed and other behavioral metrics is strongly correlated with drift in V1 responses. Framing source, not a decisive test. — [arXiv](https://arxiv.org/pdf/2305.11953)
- [MEM] Xia, Marks, Goard & Wessel (2021), Nature Communications, "Stable representation of a naturalistic movie emerges from episodic activity with gain variability": slow gain fluctuations contribute to apparent instability of V1 responses. DOI not checked.

### Inferences
- The drift debate supplies the exact methodological template the student needs: regress out (or condition on) pupil, running, wheel and face-motion energy, and explicitly compare against an elapsed-time regressor. The best-practice objection (from Sadeh & Clopath's reviewers) is that time, behavior and state are collinear within a session, so attribution requires either designs that decorrelate them or explicit time controls.
- Representational-drift papers concern stimulus tuning across days. The student's slow mode is a within-session shift in baseline population activity. The two are related, because gain and baseline shifts change tuning-based similarity metrics, but they are not the same phenomenon.

### Gaps
- No 2024–2026 paper was found that decisively resolves the drift-versus-behavior dispute on new data. The search was snippet-level only for 2023–2024.
- Did not verify whether newer work (e.g., Allen Institute Brain Observatory reanalyses, 2023–2025) adds electrode-drift or motion-correction controls specific to Neuropixels.

---

## Q4. 2023–2026 work on time-on-task / within-session slow modes across many brain regions simultaneously

### Takeaway
Searches turned up no published 2023–2026 study that characterizes an unsupervised within-session slow (time-on-task) mode across many simultaneously recorded brain regions in mice and validates it against arousal, satiety and artifact controls. Adjacent work exists: IBL internal-state analyses, brain-wide arousal axes in macaque, fast-local versus slow-global ensembles, and latent-model preprints noting unexplained slow session-level variation. This looks like a real gap, though a database-level forward-citation search (Google Scholar or Semantic Scholar) is needed to confirm.

### Cited Findings
- **Amjad & Hiratani (UCL), "Internal state is at least two dimensional", Research Square preprint (rs-7749081, about 2025–2026) [snippet only; full text unreadable in this session].** Uses the IBL dataset (145 sessions, 44 mice) to compare three candidate internal-state measures: the IBL/Steinmetz-style engagement index, the GLM-HMM stimulus coefficient and pupil diameter. It assumes the internal state changes slowly and notes that pupil also responds reflexively, so it is not a pure state readout. The title claims internal state is at least 2-D. Whether neural population data from the Brain-Wide Map are used, and how, could not be verified. — [Research Square PDF](https://assets-eu.researchsquare.com/files/rs-7749081/v1_covered_14b6566c-ed28-411c-a10a-d12a540353c2.pdf?c=1775216577)
- **"A latent space network model for dynamic neural latent embedding" (arXiv 2608.24452, 2026) [snippet only].** Applied to Neuropixels data, it reports that early- versus late-session latent structure at the same task phase differs modestly, suggesting "additional slow variation over the session" that "could reflect changes in engagement or fatigue". It explicitly does not identify the mechanism. — [arXiv](https://arxiv.org/pdf/2608.24452)
- **"Internal states emerge early during learning of a perceptual decision-making task" (bioRxiv 2024.11.30.626182; revised September 2025) [snippet only].** Dynamic GLM-HMM on mouse behavior during learning; a 3-state model beats 1-state early in training. Behavior only. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2024.11.30.626182v1.full.pdf)
- **Transformer-based VAE for cross-area interactions (arXiv 2506.02263, 2025) [snippet only].** On Allen Neuropixels visual-coding data, locomotion and pupil diameter organize the trial-wise latent across visual areas and are described as major sources of background dynamics across the brain. — [arXiv](https://arxiv.org/pdf/2506.02263)
- **Johnston & Smith (eLife 2026; see Q1)** is the closest 2024–2026 multi-area (SC plus PFC) slow-drift characterization, but it is in macaque and covers 2 areas. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13246003/)
- **Fast-local / slow-global ensembles (Network Neuroscience 2023; see Q2)** shows that above 1 s, ensembles are multi-regional, but it does not link them to elapsed time or state. — [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10312261/)
- A 2026 bioRxiv Neuropixels Quad-Base preprint notes mice performed "until satiety (typically about 1 h/day)". This illustrates that satiety-bounded sessions are standard, so time-on-task and satiety are confounded by design in most mouse datasets. — [bioRxiv](https://www.biorxiv.org/content/10.64898/2026.07.23.740388v1.full)
- [MEM] International Brain Laboratory (2023 bioRxiv, 10.1101/2023.07.04.547681; later published in Nature, 2025), "A brain-wide map of neural activity during complex behaviour": brain-wide encoding of stimulus, choice, feedback, movement and block prior. To my knowledge it does not characterize within-session slow drift modes. Status and content not re-verified this session. — [bioRxiv DOI](https://doi.org/10.1101/2023.07.04.547681)
- [MEM] Benisty, ... Higley (2024), Nature Neuroscience, "Rapid fluctuations in functional connectivity of cortical networks encode spontaneous behavior" (mesoscale imaging, dorsal cortex). Relevant to brain-wide state but at faster timescales. DOI not verified.
- [MEM] Hulsey, Zumwalt, Mazzucato, McCormick & Jaramillo (2024), Cell Reports, "Decision-making dynamics are predicted by arousal and uninstructed movements": pupil and movement predict mouse decision states. Behavior plus arousal, not brain-wide neural slow modes. DOI not verified.

### Inferences
- The literature has established, separately: (i) a 1-D slow drift shared across areas in macaque (2–3 areas at a time, tens-of-minutes timescale, pupil- and impulsivity-linked); (ii) arousal- and movement-dominated brain-wide spontaneous activity in mice; (iii) satiety- and engagement-dependent brain-wide state shifts in mice; (iv) behavioral latent states (GLM-HMM) on the IBL task. What appears missing is a unified, brain-wide (tens of regions, many animals) characterization of the within-session slow mode in mice, with (a) its dimensionality and cross-region alignment, (b) its relation to pupil, movement, satiety (licking/reward count), engagement (GLM-HMM) and time, and (c) explicit artifact controls (probe motion, unit stability).

### Gaps
- Could not run Google Scholar or Semantic Scholar forward-citation counts for Cowley 2020 and Stringer 2019. The claim that no brain-wide mouse time-on-task study exists rests on targeted searches, not exhaustive citation screening.
- Could not read the Amjad & Hiratani preprint's methods to determine whether it uses neural data from the IBL Brain-Wide Map. This is the most important paper to check for novelty overlap.

---

## Q5. Assessment: what remains open, and implications for judging the student's slow mode (genuine state vs artifact)

### Takeaway
A slow, roughly 1-D, cross-area mode is a well-documented genuine phenomenon in macaques (Cowley 2020 and follow-ups) and has mouse analogues (infraslow pupil coupling, satiety and engagement states). So the existence of such a mode in M2 is not novel by itself. What would be novel is a rigorous brain-wide mouse characterization that separates time-on-task, satiety, arousal and engagement from recording drift, and that tests within-session stability of the mode's direction. The student's finding of a monotonic time-tracking mode that is not direction-reproducible across halves is, on current evidence, as consistent with artifact as with state.

### Cited Findings
- Genuine slow-drift claims in macaque rest on waveform-stability unit selection, cross-area coherence (V4 vs PFC, |rho| about 0.93–0.96, above random-walk and time-control nulls) and behavioral/pupil co-variation, not on monotonic time trends alone. — [Cowley 2020, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7822647)
- Cross-area agreement for SC vs PFC is weaker (shared variance median about 0.26) and pupil explains only about 6% of SC drift variance. This shows that even genuine slow drift can have modest external correlates. — [Johnston & Smith, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13246003/)
- In mouse PFC, infraslow population fluctuations are strongly pupil-coherent, with both positively and negatively coupled neurons. This is a signature of a state mode that is hard to mimic with uniform electrode drift. — [Okun 2019, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6458908)
- Satiety-driven brain-wide state change in mice can be reversed by stimulating thirst neurons, which is causal evidence for a genuine motivational state. — [Allen 2019](https://luolab.stanford.edu/sites/g/files/sbiybj20556/files/media/file/allen_et_al_science_2019_0.pdf)
- The time-versus-behavior attribution problem is explicitly flagged in the drift literature. — [Sadeh & Clopath reviews](https://elifesciences.org/articles/77907/peer-reviews)

### Inferences
- Concrete tests suggested by the literature for the IBL M2 slow mode:
  - Coherence of the mode with pupil, wheel and face motion energy at below 0.1 Hz (Okun 2019 style).
  - Correlation with cumulative reward or water consumed (satiety, as in Allen 2019) and with GLM-HMM engaged-state probability (as in Ashwood 2022), each compared against a pure elapsed-time regressor.
  - Sign structure of loadings: mixed-sign loadings suggest state, while same-sign, depth-ordered loadings suggest probe drift.
  - Alignment with modes in other simultaneously recorded regions in the same IBL session (Cowley-style cross-area correlation, compared against random-walk nulls).
  - Relation to spike-sorting drift estimates (Kilosort or IBL motion registration) and unit-stability metrics.
- The split-half non-reproducibility of direction is ambiguous. A monotonic ramp has essentially one effective degree of freedom per half, so PCA directions estimated from each half may be poorly constrained. A genuine non-stationary state could also recruit different neurons early versus late. Neither the monkey nor the mouse literature verified here reports a split-half direction-stability test for slow drift, so this is an open methodological contribution.
- Novelty judgment: a brain-wide (many regions, many mice) characterization of within-session slow modes in the IBL Brain-Wide Map, with state and artifact dissociation, appears not to have been published as of late 2026. This rests on searches in this session, with one important unverified candidate overlap (Amjad & Hiratani, Research Square).

### Gaps
- Artifact-side literature (Neuropixels probe motion, e.g. Steinmetz et al. 2021 Science "Neuropixels 2.0", DOI 10.1126/science.abf4588 [MEM]; IBL spike-sorting and motion-registration papers) was out of scope here and is presumably covered by another review question. It is essential for the state-versus-artifact verdict.
- No effect sizes were found for how much variance a time-on-task mode explains brain-wide in mice. Allen 2019 likely contains relevant numbers but full text was not accessible.
- Fatigue as distinct from satiety and disengagement has essentially no dedicated mouse population-level literature in the results screened.
