# Q4: Predictive / slow subspace methods for neural population data, their sensitivity to nonstationarity, and controls

**Search protocol (systematic-review record).** Search date: 2026-11-17. Tools: a general web search engine (standard and "extended" modes; US index), direct full-text retrieval from arXiv/ar5iv, bioRxiv, and author-repository PDFs (text extracted locally with macOS PDFKit when the fetcher could not parse a PDF). Google Scholar "cited by" could not be queried directly (no Scholar API access), so citing-literature coverage of Clark 2019 and Harris 2020 is incomplete and partly based on background knowledge.

Exact queries run (15 web searches/fetches in total):

1. `Clark Livezey Bouchard dynamical components analysis predictive information NeurIPS 2019`
2. `compressed predictive information coding CPIC neural dynamics arXiv`
3. `Harris "Nonsense correlations in neuroscience" bioRxiv linear shift test`
4. `dimensionality reduction neural population slow drift nonstationarity confound latent factors detrending` (extended)
5. `Shinn "Phantom oscillations in principal component analysis" PNAS 2023`
6. `Cowley 2020 Neuron "slow drift" impulsivity macaque V4 prefrontal method PCA binned`
7. `Box Tiao 1977 canonical analysis multiple time series most predictable components nonstationary`
8. `Hyvärinen Morioka time-contrastive learning nonstationarity nonlinear ICA 2016`
9. `Findling IBL "Brain-wide representations of prior information" pseudo-session null Nature 2025`
10. `Galgali Sahani Mante residual dynamics slow drift across trials removed Nature Neuroscience 2023`
11. `latent variable model neural population within-session nonstationarity slow drift LFADS GPFA CEBRA confound time in session` (extended)
12. `Lebedev 2019 pitfalls rotational dynamics jPCA Scientific Reports`
13. `neural population activity encodes elapsed time within session slow drift representational drift time-on-task mouse`
14. `Schmutz Brea Gerstner "horseshoe effect" neuroscience PCA random walk drift` (the author guess was wrong; the search returned Antognini & Sohl-Dickstein 2018 instead, which turned out to be highly relevant)
15. Full-text fetches: DCA (ar5iv HTML of arXiv:1905.09944) and Harris "Nonsense correlations" (bioRxiv v3 PDF, posted 19 June 2021, read in full via local text extraction).

Inclusion criteria: (a) methods that extract low-dimensional latents/subspaces from multivariate time series using a temporal, predictive, slowness, or dynamical objective, applied to or proposed for neural population data; (b) papers on spurious structure produced by temporal smoothness, drift, or nonstationarity in neural analyses (decoding or dimensionality reduction); (c) statistical controls for slow confounds; (d) classic time-series/ML precedents that directly bear on "predictability objectives recover nonstationary components." Prioritized 2017–2026, preprints included. Exclusion: across-day representational-drift papers unless they bear on within-session analysis; pure spike-sorting papers (mentioned only as a source of drift); fMRI-only decoding papers (not searched systematically, a known gap).

Rough counts: about 140 search-result entries screened (about 10 per query); about 45 works noted; about 30 included below. **Evidence tags used in this file:** **[V]** = verified this session from primary full text; **[A]** = verified this session from abstract, publisher/repository landing page, or search-snippet level only; **[K]** = from background knowledge of the literature, NOT re-verified this session (citation details believed correct but the report writer should treat specific claims as secondary and spot-check before final use).

---

## Key question 1: What do predictive / slowness / dynamical latent methods optimize, and do their authors discuss sensitivity to slow drift, nonstationarity, or time-on-task?

### Takeaway
Every predictive or slowness objective (DCA, CPIC, SFA, lagged CCA/RRR, Box–Tiao, TICA, Koopman/DMD, CPC/forecasting, CEBRA-time) explicitly or implicitly assumes stationarity and rewards components whose autocorrelation persists across the chosen horizon. The DCA authors state stationarity is "a fundamental conceptual assumption" and quietly high-pass filtered their M1 data with a 30-s sliding mean. However, no method paper found demonstrates or warns that long-horizon objectives will preferentially lock onto within-session drift in neural data.

### Cited Findings

**Dynamical Components Analysis (DCA).** Clark, Livezey & Bouchard, NeurIPS 2019 (arXiv:1905.09944).
- **[V]** DCA finds a linear projection maximizing "predictive information, defined as the mutual information between the past and future" windows of length T, under a Gaussian approximation; the authors state "we assume that X is a stationary (discrete-time) Gaussian process" — [ar5iv full text](https://ar5iv.labs.arxiv.org/html/1905.09944); [NeurIPS page](https://papers.nips.cc/paper/2019/hash/704cddc91e28d1a5517518b2f12bc321-Abstract.html)
- **[V]** The authors write that "stationarity is a fundamental conceptual assumption of our method" and that "extending DCA for non-stationary data is a key direction for future work." They suggest segmenting the data into approximately stationary windows. — [ar5iv](https://ar5iv.labs.arxiv.org/html/1905.09944)
- **[V]** Neural preprocessing: for the M1 data they "square-root transformed the data and mean-centered the data using a sliding window 30 s in width." In effect this removes components slower than about 30 s before DCA sees them, an implicit drift control that is not discussed as such. Hippocampal data were binned (50 ms) and square-root transformed. M1 used 100 ms or 50 ms bins. The predictive horizons were short: a window of T up to about 20 bins, i.e. on the order of 1 s. — [ar5iv](https://ar5iv.labs.arxiv.org/html/1905.09944)
- **[V]** The paper relates DCA to SFA: the two coincide for one dimension and for time-reversible processes, and differ for time-irreversible or non-Markovian data. CCA solves a relaxed version with separate past and future projections. ForeCA and Complexity Pursuit are cited as related. GPFA and Kalman filters are compared in an appendix. Box–Tiao and TICA are not cited. Detrending, slow drift, and trends are not discussed. — [ar5iv](https://ar5iv.labs.arxiv.org/html/1905.09944)
- **[A]** NeurIPS reviewers noted that DCA provides no generative dynamical model and that CCA can capture more past–future MI because DCA constrains predictive and predictable subspaces to be identical. — [NeurIPS reviews](https://papers.nips.cc/paper_files/paper/2019/file/704cddc91e28d1a5517518b2f12bc321-Reviews.html)

The DCA objective, as verified in the full text, is the Gaussian past–future mutual information of the projected series:

$$I_T(V) = \log\det \Sigma_T\!\left(V^\top X\right) - \tfrac{1}{2}\log\det \Sigma_{2T}\!\left(V^\top X\right)$$

Here $\Sigma_T$ is the covariance of $T$ consecutive projected samples. Any component whose autocovariance stays close to its variance across $2T$ lags (for example a trend or random walk within a finite session) makes the second term small relative to the first and therefore scores highly.

**Compressed Predictive Information Coding (CPIC).** Meng, Luo & Bouchard, arXiv:2203.02051 (March 2022). The task brief's "Bai et al. 2020" appears to be a misattribution; the CPIC authors are Rui Meng, Tianyi Luo, and Kristofer Bouchard.
- **[A]** CPIC learns a stochastic encoder that minimizes compression complexity while maximizing predictive information in latent space, using variational mutual-information bounds. The means are encoded linearly and the variances nonlinearly. It is claimed to recover latents of noisy dynamical systems at low SNR and to extract features predictive of exogenous variables in neuroscience data. No drift discussion was found at abstract level. — [arXiv abstract](https://arxiv.org/abs/2203.02051)
- **[K]** Publication status: we believe it was later published in a peer-reviewed venue, but this was not confirmed this session; treat it as a preprint.

**Classic predictability-maximizing decompositions (time-series statistics precedent).**
- **[A]** Box & Tiao (1977, Biometrika 64:355–365), "A canonical analysis of multiple time series," orders linear combinations from least to most predictable. Velu, Wichern & Reinsel (1987) note that Box and Tiao established a correspondence between nonstationary roots and canonical correlations of a VAR(1). In the cointegration literature, the most predictable components of nonstationary vector series are the nonstationary (unit-root) directions, and the least predictable ones reveal stationary cointegrating relations. — [RePEc note, Velu et al. 1987](https://ideas.repec.org/a/bla/jtsera/v8y1987i4p479-487.html); [Galeano & Peña review](https://halweb.uc3m.es/esp/personal/personas/dpena/publications/ingles/2000RESENHAS_galeano.pdf)
- **[K]** Forecastable Component Analysis (ForeCA; Goerg, ICML 2013) and Slow Feature Analysis (Wiskott & Sejnowski 2002, Neural Computation) maximize forecastability and slowness respectively. Time-lagged ICA (TICA; Pérez-Hernández et al. 2013, J Chem Phys) and VAMP (Wu & Noé 2020) in molecular dynamics are lagged-covariance generalized eigenproblems that by construction return the slowest processes. That literature is aware that the slowest processes can be uninteresting (for example rare transitions or non-equilibrium relaxation). These are not neural papers.

**Time-contrastive learning (CEBRA-time ancestor).**
- **[A]** Hyvärinen & Morioka (NeurIPS 2016, arXiv:1605.06336) train a classifier to tell time segments apart. Identifiability of the sources relies *on the sources being nonstationary*: TCL plus linear ICA recovers sources "with temporal nonstationarity." In other words, a time-contrastive objective is provably a nonstationarity detector. — [arXiv](https://arxiv.org/abs/1605.06336)
- **[K]** CEBRA (Schneider, Lee & Mathis, Nature 2023, 617:360–368). CEBRA-Time samples positive pairs from temporally nearby samples, with an offset hyperparameter. The paper validates embeddings with label-shuffle controls and consistency across animals. We do not recall any analysis of within-session drift or a pseudo-session control for CEBRA-Time. Not re-verified this session.

**Cross-area and lagged reduced-rank methods.**
- **[K]** Semedo et al. 2019 (Neuron 102:249–259), "communication subspaces," use reduced-rank regression between V1 and V2 at zero lag, on trial-wise residuals after subtracting condition means. This residualization incidentally removes stimulus-locked structure but not slow drift. DLAG (Gokcen et al. 2022, Nature Computational Science) and multi-region GP models with lags (MRM-GP, Gokcen et al. 2023) model short (millisecond-scale) inter-areal delays with GP latents; the GP timescales are learned, so a very long timescale latent could absorb drift. No drift discussion was found. Not re-verified this session.
- **[A]** Residual dynamics (Galgali, Sahani & Mante, Nature Neuroscience 2023, 26:326–338) fits dynamics to trial-by-trial residuals around condition-mean trajectories. In their model the recurrent term "induces variability over slow time-scales (i.e. long temporal autocorrelation)" while fast variability is uncorrelated. Slow autocorrelated variance is therefore treated as signal attributable to recurrence. Whether across-trial slow drift was removed was not confirmed. — [UCL accepted manuscript](https://discovery.ucl.ac.uk/10164395/2/Galgalietal2023_Main_NNaccepted.pdf)

**Koopman / DMD.**
- **[K]** Brunton, Johnson, Ojemann & Kutz (2016, J Neurosci Methods 258:1–15) applied DMD to ECoG. Chen, Tu & Rowley (2012, J Nonlinear Sci) showed that mean-subtracted DMD reduces to a temporal discrete Fourier transform. DMD eigenvalues near 1 (unit circle, zero frequency) correspond to slow or trend modes, and the leading DMD/Koopman modes on drifting data tend to be near-unit-root trend modes. Not re-verified.

**Latent-dynamics and foundation models (LFADS, NDT, POYO, NLB).**
- **[A]** A 2022 domain-adaptation paper (Jude et al., ICML 2022) reports that vanilla LFADS fails to capture session-to-session variability, and uses gradient reversal on session identity to obtain session-invariant latents. The nonstationarity problem in this line of work is framed *across sessions*, not within a session. — [PMLR](https://proceedings.mlr.press/v162/jude22a/jude22a.pdf)
- **[A]** The Neural Latents Benchmark '21 (Pei et al., arXiv:2109.04463) evaluates co-smoothing and forward prediction on short trial-aligned windows, so long-horizon drift is outside its scope. — [arXiv](https://arxiv.org/pdf/2109.04463)
- **[K]** LFADS (Pandarinath et al. 2018, Nature Methods) handles multi-day nonstationarity with per-session read-in/read-out ("stitching"). NDT/NDT2 (Ye & Pandarinath 2021; Ye et al. 2023) and POYO (Azabou et al. NeurIPS 2023) use session or context tokens. ZAPBench (Lueckmann et al., ICLR 2025) is a whole-brain zebrafish activity-forecasting benchmark. None of these that we know of tests whether learned latents encode elapsed session time. Not re-verified.

**Tensor methods that explicitly model slow across-trial structure.**
- **[A]** sliceTCA (Pellegrino, Stein & Cayco-Gajic, Nature Neuroscience 2024) separates within-trial from between-trial covariability and notes that slowly evolving latent subspaces could reflect learning or drift. — [Nature Neuroscience](https://www.nature.com/articles/s41593-024-01626-2)
- **[K]** TCA (Williams et al. 2018, Neuron 98:1099–1115) gives each component a trial-factor that captures slow across-trial changes (learning, and changes across days). This is the main existing method that *demixes* slow across-trial modulation from within-trial dynamics rather than letting it contaminate them.

### Inferences
- The predictive objectives listed above share a structural property: as the horizon grows, only components whose autocorrelation time is at least comparable to the horizon retain predictable variance. In a finite session, trends, random walks, and slow arousal or engagement drifts have near-unit autocorrelation at every lag up to a sizable fraction of the session. At 0.5–30 s horizons with roughly 1-hour IBL sessions, these components should therefore dominate. This follows from the objectives' math (Box–Tiao/TICA logic). It was not demonstrated for neural data in any paper found.

For lagged reduced-rank ridge regression, the objective is

$$\min_{B:\ \mathrm{rank}(B)\le d}\ \sum_t \left\lVert x_{t+\Delta} - B\,x_t \right\rVert_2^2 + \lambda \lVert B \rVert_F^2 .$$

For a latent mode with exponential autocorrelation time $\tau$, the predictable fraction of its variance at lag $\Delta$ scales roughly as $e^{-2\Delta/\tau}$. At $\Delta = 30$ s, only modes with $\tau$ on the order of tens of seconds or longer contribute. Within a session, those are almost always drift, arousal, or engagement modes, or block-scale variables.

- The DCA authors' 30-s sliding-window mean-centering in M1 suggests they encountered, or anticipated, slow components; the paper does not discuss it as a drift control. Any re-application of DCA or CPIC to long-horizon IBL data that omits this step is not comparable to the original paper.
- TCL's identifiability theorem formally states that time-contrastive objectives extract nonstationary sources. This is a strong citable precedent that CEBRA-Time-like objectives will encode session time unless controlled.

### Gaps
- Could not read the full CPIC text or its peer-reviewed status. Could not check whether CPIC's neural applications used detrending.
- Did not verify any CEBRA, LFADS, NDT, or POYO text for within-session drift discussion. Statements are [K].
- No Google Scholar "cited by" crawl of DCA was possible. Follow-up Bouchard-lab or other DCA applications on long-horizon data may exist and were not found.
- Did not find any neural application of SFA proper (as opposed to slowness priors in GPFA) that discusses drift.

---

## Key question 2: Does any paper show that such methods pick up slow drift or session-time trends, or recommend detrending or time controls?

### Takeaway
Yes, in two adjacent senses. (i) Several papers show that *unsupervised* dimensionality reduction (PCA, jPCA, and population-trajectory analyses) produces spurious low-dimensional structure from temporal smoothness or random-walk drift: Antognini & Sohl-Dickstein 2018, Shinn 2023 PNAS, the 2022 horseshoe preprint, and Lebedev et al. 2019. (ii) Several papers show that within-session slow drift is a real, dominant, behaviorally meaningful population mode: Cowley et al. 2020, plus hippocampal "time-stamp" work. No paper found shows this specifically for *predictive/lagged-subspace* objectives (DCA, CPIC, lagged RRR, CEBRA-time) or offers a control battery for them.

### Cited Findings
- **[A]** Antognini & Sohl-Dickstein (NeurIPS 2018), "PCA of high dimensional random walks with comparison to neural network training": in the long-trajectory, high-dimensional limit, most variance of a random walk lies in the first few PCs. Projected trajectories have a characteristic random-walk signature. — [NeurIPS](https://proceedings.neurips.cc/paper/2018/hash/7a576629fef88f3e636afd33b09e8289-Abstract.html); [arXiv](https://arxiv.org/pdf/1806.08805.pdf)
- **[K]** In that paper the k-th PC projection of a high-dimensional random walk approaches a cosine of frequency proportional to k over the trajectory length. The first PC is a half-cosine, i.e. *monotonic in elapsed time*, and successive pairs form Lissajous curves. Treat this as secondary until checked in the PDF. It predicts exactly the "1-D slow mode tracking elapsed time" that the student found.
- **[A]** Shinn (PNAS 2023, 120(48):e2311420120), "Phantom oscillations in principal component analysis": PCA produces oscillatory components from non-oscillatory data that vary along a continuum such as time. The cause is smoothness and shifts in time or space, properties of "nearly all neuroscience data." **Traditional cross-validation does not detect phantom oscillations**; the paper proposes alternative procedures. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2023.06.20.545619.full.pdf); [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10691246/)
- **[A]** Dyer & Kording (PNAS 2023 commentary, "Why the simplest explanation isn't always the best") cite Shinn as an example of PCA hallucinating structure. — [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10756184/)
- **[A]** "Misinterpreting the horseshoe effect in neuroscience" (bioRxiv 2022.03.04.482986; authors not verified this session): oscillatory or horseshoe low-dimensional trajectories can arise from DR applied to data with particular temporal covariance structure and should not automatically be read as latent dynamics. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2022.03.04.482986.full.pdf)
- **[A]** Lebedev et al. (Scientific Reports 2019, 9:18978), "Analysis of neuronal ensemble activity reveals the pitfalls and shortcomings of rotation dynamics": jPCA rotations can arise from the temporal ordering of single-neuron PETH peaks. A 2024 Sci Rep follow-up (Kuzmina, Kriukov & Lebedev) notes that rotations may be jPCA artifacts. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6908571); [Sci Rep 2024](https://www.nature.com/articles/s41598-024-53907-2)
- **[K]** Elsayed & Cunningham (Nature Neuroscience 2017, 20:1310–1318), "Structure in neural population recordings: an expected byproduct of simpler phenomena?": tensor maximum-entropy (TME) surrogates preserve the time, neuron, and condition covariances and test whether population structure exceeds what those marginals imply. TME is designed for trial-averaged tensors and does not target slow within-session drift.
- **[A]** Cowley, Snyder, Acar, Williamson, Yu & Smith (Neuron 2020, 108:551–567): a slow fluctuation ("slow drift") in V4 population activity over tens of minutes covaried with slow changes in the animal's hit and false-alarm behavior. PFC showed a highly correlated slow drift. The drift "acted as an impulsivity signal" rather than altering stimulus encoding. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7822647); [CSHL repository](https://repository.cshl.edu/41559/)
- **[K]** Cowley et al. extracted slow drift by PCA on spike counts averaged in long (about 20–30 min) sliding windows, after removing stimulus-evoked responses. The exact window was not confirmed this session; check the Methods.
- **[A]** Hippocampal CA1 shows consistent population dynamics over many minutes within a session, tested against the alternative of stochastic drift (Liu et al., bioRxiv 2021 / Hippocampus 2022). Time-cell ensembles carry temporal information from seconds to days. Some work argues drift tracks accumulated experience rather than clock time. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2021.02.07.430172.full.pdf); [Weizmann repository](https://weizmann.elsevierpure.com/ws/files/89900466/yz_Hippocampus_ConsistentPopulationActivity_AM2022.pdf)
- **[K]** Related evidence that slow modes are real neural or behavioral state: Rubin et al. 2015 (eLife; hippocampal ensembles "timestamp" events), Rabinowitz et al. 2015 (eLife; slow shared gain modulators in V4), Hennig et al. 2021 (Nature Neuroscience; abrupt changes in a "neural engagement" axis shape BCI learning), Stringer et al. 2019 (Science; spontaneous behaviors dominate brain-wide activity), and Ashwood et al. 2022 (Nature Neuroscience; GLM-HMM engagement states in IBL mice that change within a session).
- **[A]** A 2026 bioRxiv preprint on M1 reports that drift in the *encoding* map, rather than the latent map, is the main nonstationarity. It estimates drift rates by regressing supervised latents on time. — [bioRxiv](https://www.biorxiv.org/content/10.64898/2026.01.30.702162v1.full)
- **[A]** The representational-drift review by Rule, O'Leary & Harvey (2019, Curr Opin Neurobiol) argues that drift can live largely in the null space of task coding when population dimensionality greatly exceeds task dimensionality. — [Harvey lab PDF](https://harveylab.hms.harvard.edu/pdf/rule2019.pdf)
- **[K]** Electrode drift is a well-documented recording-level source of within-session nonstationarity in Neuropixels data: Steinmetz et al. 2021 (Science; Neuropixels 2.0 motion correction), Kilosort 2.5+ drift correction, and DREDge (Boussard et al.). Residual motion changes unit amplitudes and firing rates over the session. This is directly relevant to IBL data.

### Inferences
- The student's result (a 1-D slow mode monotonic in elapsed time dominating long-horizon predictive subspaces) is what the random-walk PCA theory (Antognini & Sohl-Dickstein) predicts for *any* covariance-based method once drift variance is non-negligible. Predictive objectives should amplify it, because they reweight variance by autocorrelation at the chosen lag. A methods paper should cite this as the null model.
- The literature leaves an interpretive fork the paper must handle: the slow mode may be (a) recording artifact (probe motion, unit loss), (b) genuine neural state (arousal, engagement, satiety, impulsivity à la Cowley 2020), or (c) a genuine elapsed-time code (hippocampal timestamping). The claim "predictive objectives preferentially recover nonstationarity" is robust to this fork. The claim that the mode is "not task-relevant" is not, because IBL engagement and bias drift within sessions (GLM-HMM states).
- Shinn's finding that standard cross-validation fails to detect phantom oscillations parallels Harris's finding (KQ3) that cross-validated decoding fails against nonsense correlations. Together they justify why split-half and held-out-R² checks alone are insufficient controls for the student's analysis.

### Gaps
- No paper found that applies DCA, CPIC, lagged RRR, CEBRA-time, or LFADS to long horizons and reports that the leading component tracks session time. This is the core novelty gap.
- Cowley 2020's exact slow-drift extraction window and whether they recommend removing it before other analyses: not verified.
- Authorship and venue of the horseshoe preprint not verified.
- The fMRI literature on drift and temporal-autocorrelation confounds in MVPA, likely substantial, was not searched.

---

## Key question 3: What statistical controls exist for slow confounds in neural decoding, and has anyone applied them to unsupervised subspace methods?

### Takeaway
Harris (bioRxiv 2020, v3 2021) is the key reference. Pseudo-session and session-permutation tests are valid. The linear-shift test is valid only if one series is stationary. Cross-validation, circular shift, phase or wavelet randomization, and auto-decorrelation or detrending can yield up to 100% false positives. IBL's Findling et al. (Nature 2025) operationalized pseudo-sessions for block-prior decoding. All of these target *supervised association* between neural data and a variable. No paper was found that adapts them to validate an *unsupervised* subspace, for example asking whether a predictive subspace aligns with the block prior more than in pseudo-sessions, or whether its leading mode is explained by elapsed time.

### Cited Findings
- **[V]** Harris, "Nonsense correlations in neuroscience," bioRxiv 10.1101/2020.11.29.402719, v3 posted 19 June 2021, CC-BY, not peer-reviewed at that version. Abstract: "Methods based on cross-validation, circular shifting, phase randomization, or detrending gave up to 100% false positive rates in our simulations. We conclude that analysis of neural timeseries is best performed when stationarity and randomization is built into the experimental design." — [bioRxiv PDF](https://www.biorxiv.org/content/10.1101/2020.11.29.402719.full.pdf)
- **[V]** Harris evaluates ten approaches on simulated, slowly drifting signals. Pseudosession and session permutation do not produce nonsense correlations. The conservative linear shift method does not if one series is stationary. Naive correlation, circular shift, phase and wavelet randomization, cross-validation, and auto-decorrelation can all produce nonsense correlations. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2020.11.29.402719.full.pdf)
- **[V]** Pseudosession method: it requires a user-specified scalar association statistic computed on a session. A good choice is the error of a classifier predicting one series from the other, cross-validated or not. "Any choice of V gives a valid test; poor choices can only result in false-negative errors." It is the only method described that can show causality, and it requires that the behavioral variable (for example a block structure) be generated randomly by the experimenter, independent of the subject's choices. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2020.11.29.402719.full.pdf)
- **[V]** Session permutation requires multiple sessions under the same conditions. With different neurons per session it supports only population-level, not single-neuron, conclusions. Without randomized design it cannot establish causality, because sequential sessions can share trends. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2020.11.29.402719.full.pdf)
- **[V]** Linear shift: assumes stationarity of one series and compares the association of central segments against linearly shifted segments. An earlier version's "initial segment" variant is explicitly *not* recommended because it is not conservative. Details are in Harris (2020), "A Shift Test for Independence in Generic Time Series." — [bioRxiv](https://www.biorxiv.org/content/10.1101/2020.11.29.402719.full.pdf)
- **[V]** On detrending and auto-decorrelation (AR residualization, differencing, subtracting a best-fit line): it "comes with a major caveat: the auto-decorrelation algorithm must be extremely accurate. This cannot be guaranteed," because AR models exactly whiten only linear (filtered white-noise) series. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2020.11.29.402719.full.pdf)
- **[V]** Harris situates the problem in econometrics (Yule 1926; Granger & Newbold 1974 "spurious regressions"; Phillips 1986) and cites a mouse-brain versus cryptocurrency-price nonsense correlation (Meijer 2021). He states that the problem "has seen little discussion in this field (but see Elber-Dorozko and Loewenstein, 2018)." — [bioRxiv](https://www.biorxiv.org/content/10.1101/2020.11.29.402719.full.pdf); [PCI Neuroscience "Can a mouse understand the crypto market?"](https://neuro.peercommunityin.org/articles/rec?id=69)
- **[A]** Harris's paper does not address dimensionality reduction or latent-variable discovery. A keyword search of the full text for "dimensionality," "latent," and "PCA" returned no methodological discussion. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2020.11.29.402719.full.pdf) (our own text search of v3)
- **[K]** Elber-Dorozko & Loewenstein (eLife 2018, 7:e34248), "Striatal action-value neurons reconsidered": standard regression-based identification of action-value neurons yields many false positives when firing rates drift slowly, including for neurons recorded in unrelated tasks. They propose permutation tests that use behavior from other sessions (a session-permutation precursor).
- **[A]** Findling et al., IBL (Nature 2025, 645:192–200, doi:10.1038/s41586-025-09226-1): the subjective block prior is decodable in at least 20–30% of 242 brain regions. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12408363); [CSHL repository](https://repository.cshl.edu/id/eprint/41954/)
- **[K]** Its null is a pseudo-session distribution: block sequences are regenerated from the task's generative process, the prior is re-estimated with the behavioral model, and decoding is re-run. This applies Harris's method to the student's exact target variable. The specific Methods detail was not re-verified this session.
- **[K]** Other relevant controls: Elsayed & Cunningham 2017 TME surrogates (structure versus marginal covariances); Shinn 2023's proposed phantom-oscillation diagnostics; Stringer et al. 2019's shared-variance component analysis (SVCA) for reliable dimensions, using neuron-split and time-split halves. The split-half test is weak against drift if both halves of neurons share the same drift.

### Inferences
- There is a clean, unexploited bridge: Harris's pseudosession theorem says *any* association statistic gives a valid test. The student can therefore define the statistic as "alignment between the learned predictive subspace and the block-prior coding axis," or "decodability of the block prior from the projection onto the rank-d subspace," and get a valid test. This applies even though the subspace was learned without labels, as long as the IBL block sequence is randomized by the experimenter, which it is (geometric block lengths). As far as we found, nobody has written this down for unsupervised subspaces.
- Harris shows detrending is not a guaranteed fix. A methods paper should not recommend "just detrend" as the remedy. It should treat detrending or residualization as a sensitivity analysis, with pseudo-session validity as the inferential backbone.
- Elapsed-time decoding from the subspace is a useful *diagnostic* but not a valid *test*. Time is not randomized, so its significance cannot be assessed with a pseudosession. A linear-shift or session-permutation logic, or comparison against random covariance-matched subspaces, is needed to calibrate how much elapsed-time variance is "expected."

### Gaps
- No paper found that applies pseudo-session, session permutation, or linear-shift tests to unsupervised dimensionality reduction or latent models. This is a genuine gap, with the caveat that the "cited by" crawl was not possible.
- Peer-reviewed status of Harris's "Nonsense correlations" after 2021 was not confirmed. A researchhub copy indicates activity in 2025, and a PCI Neuroscience recommendation exists for a related crypto-mouse study.
- Findling 2025 pseudo-session implementation details (number of pseudo-sessions, how the prior is re-estimated) were not verified from Methods.

---

## Key question 4: Are there methodological notes on normalization inside cross-validation with nonstationary units (z-scoring floors, silent units)?

### Takeaway
No neural-specific methodological paper on this was found. The relevant guidance is scattered: general ML leakage literature, Harris's point that cross-validation does not protect against slow confounds, and spike-sorting drift literature explaining why units go silent or appear mid-session. This is an open niche the student's control battery could document.

### Cited Findings
- **[V]** Harris: cross-validation does not protect against nonsense correlations when signals drift, because training and test folds share the same slow trend. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2020.11.29.402719.full.pdf)
- **[A]** Shinn 2023: traditional cross-validation fails to detect phantom (smoothness-induced) PCA components. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10691246/)
- **[K]** Kapoor & Narayanan (Patterns 2023), "Leakage and the reproducibility crisis in ML-based science," provide a general taxonomy that includes preprocessing fitted on train and test together, and temporal leakage. Not neural-specific; not re-verified.
- **[K]** Neuropixels probe motion and spike-sorting drift correction (Steinmetz et al. 2021; Kilosort drift correction) cause units to fade in or out within a session. A unit that is silent in a training fold has near-zero standard deviation, so z-scoring with train-fold statistics either divides by about zero or needs a variance floor. This inflates that unit's test-fold values and can create a spurious time-locked "mode." This is our inference, not documented in a found paper.

### Inferences
- With contiguous (blocked) time folds, which are required to avoid temporal leakage, nonstationary units guarantee train/test distribution shift in per-unit mean and variance. Any normalization fit on train folds then makes the test-fold residual partly a function of elapsed time. This can create or amplify a slow mode, which is a potential confound *in* the student's own pipeline. It should be reported alongside the floor value and the fraction of units affected.
- Recommended disclosure items for a methods note: fold structure (contiguous versus interleaved); normalization fitted per fold versus globally; variance floor; unit inclusion criteria (firing-rate threshold in *every* fold, IBL unit-quality labels); and sensitivity of the leading mode to excluding units with a significant firing-rate trend.

### Gaps
- No primary neural-methods source found on z-scoring floors or silent-unit handling in cross-validated dimensionality reduction. This was searched only indirectly; a dedicated search (for example "variance floor z-score spike counts cross-validation") was not run because of the tool-call budget.

---

## Key question 5 (objective synthesis): Is a methods paper arguing "long-horizon predictive/slowness objectives preferentially recover nonstationarity," with a control battery, novel?

### Takeaway
Probably novel as a *neuroscience methods contribution*, but not as a *mathematical observation*. The mechanism is classical in time-series statistics (Box–Tiao, cointegration, TICA slowest processes) and ML (TCL identifiability via nonstationarity). PCA-specific versions are published in neuroscience (Shinn 2023; Antognini & Sohl-Dickstein 2018; jPCA critiques). Nobody we found has (a) shown it empirically for neural predictive-subspace methods across horizons, (b) connected it to Harris-style inference, or (c) proposed a control battery for unsupervised predictive subspaces.

### Cited Findings
- **[V]** The DCA paper itself states the stationarity assumption, flags nonstationary extensions as future work, and used 30-s sliding-mean centering on M1. A long-horizon application without such preprocessing is outside its stated assumptions. — [ar5iv](https://ar5iv.labs.arxiv.org/html/1905.09944)
- **[V]** Harris provides valid inference tools but covers only supervised association, and explicitly says CV and detrending fail. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2020.11.29.402719.full.pdf)
- **[A]** PCA-artifact precedents: Shinn 2023 PNAS ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10691246/)); Antognini & Sohl-Dickstein 2018 ([NeurIPS](https://proceedings.neurips.cc/paper/2018/hash/7a576629fef88f3e636afd33b09e8289-Abstract.html)); the horseshoe preprint ([bioRxiv](https://www.biorxiv.org/content/10.1101/2022.03.04.482986.full.pdf)); Lebedev et al. 2019 ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6908571)).
- **[A]** Time-series and ML precedents: Box & Tiao 1977 and the nonstationary-root link ([RePEc](https://ideas.repec.org/a/bla/jtsera/v8y1987i4p479-487.html)); TCL ([arXiv](https://arxiv.org/abs/1605.06336)).
- **[A]** Slow drift as genuine neural or behavioral signal: Cowley 2020 ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7822647)).

### Inferences
- **Positioning advice for the candidate paper.**
  1. Present the mechanism as an expected consequence of the objective, citing Box–Tiao, TICA, and Antognini & Sohl-Dickstein. Do not present it as a surprising discovery.
  2. Make the novelty empirical: on IBL Neuropixels data, the leading predictive subspace rotates from task-aligned to elapsed-time-aligned as the horizon increases.
  3. Make the novelty inferential: adapt the pseudosession test to unsupervised subspaces.
  4. Make the novelty practical: provide the control battery.
- **Suggested control battery, each item justified by the literature above.**
  1. Pseudo-session null on subspace–prior alignment or decodability (Harris; Findling).
  2. Elapsed-time decodability of each subspace dimension, as a diagnostic.
  3. Covariance-matched random-subspace baselines for reliability and alignment (Elsayed & Cunningham 2017 style).
  4. Random-walk or drift surrogate data matched to unit autocorrelations, to show the method recovers a half-cosine "time" mode from pure drift (Antognini & Sohl-Dickstein).
  5. Trial-locked residualization, in the spirit of Semedo 2019 and Galgali 2023.
  6. High-pass or sliding-mean sensitivity analysis (DCA's own 30-s preprocessing), reported as sensitivity analysis rather than a cure (Harris).
  7. Fold-wise normalization audit (KQ4).
  8. A probe-motion or unit-stability covariate check (Neuropixels drift).
  9. Sweep the horizon and report the crossover horizon at which the subspace becomes drift-dominated.
- **Risk to novelty and framing.** Reviewers may judge the core claim "obvious" given the Box–Tiao and TICA theory, and may object that the slow mode is real neural state (engagement or arousal). Cowley 2020 and the IBL GLM-HMM work show such states exist, and these states are partly task-relevant because engagement modulates prior use. The safer thesis is: "long-horizon predictive objectives are dominated by the slowest variance in the session, which in standard datasets is session-time-confounded, and claims that they recover task latents require pseudo-session-valid tests." Avoid claiming the mode is artifact.
- **What remains open (explicit list).**
  1. A formal or simulation result for how the horizon trades off task-latent versus drift recovery in RRR, DCA, or CPIC.
  2. A valid nonparametric test for unsupervised subspaces under nonstationarity.
  3. Benchmarks such as NLB or ZAPBench that include drift-only surrogates.
  4. Whether nonlinear contrastive models (CEBRA-time, POYO, NDT) encode session time in their latents.
  5. Normalization and fold-design guidance for drifting Neuropixels units.

### Gaps
- Citing-literature crawls (Google Scholar "cited by" for DCA, roughly hundreds of citations, and for Harris 2020) were not possible. A targeted manual check of those citation lists is the single most important remaining step before claiming novelty.
- Not searched: Bouchard-lab follow-ups applying DCA at long lags; IBL-internal methods notes on drift in brain-wide-map decoding; fMRI MVPA drift literature; econometrics reviews of predictability-based dimension reduction under unit roots, beyond the Box–Tiao abstracts.
- Many method-level statements (CEBRA, LFADS, NDT, POYO, DLAG, Semedo, Williams TCA, Elsayed & Cunningham, Elber-Dorozko & Loewenstein, Chen–Tu–Rowley DMD) are tagged [K] and should be spot-checked against primary sources before inclusion in a final report.
