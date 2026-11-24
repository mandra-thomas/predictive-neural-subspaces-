# Analysis log (append-only)

Scripts append a row automatically. Add manual notes for any config change, with the amendment number.

| date | git | config | step | note |
|---|---|---|---|---|
| 2026-11-16 | - | - | setup | Repo created; AMENDMENTS.md pre-registered before any real-data fit. Synthetic smoke test of scripts 03-07 passed (8 synthetic sessions). |
| 2026-11-16 08:16 | 1c3b991-dirty | fac6882b34 | 01_census | region=MOs; 16 sessions / 13 subjects; checkpoint 10 sessions / 10 subjects |
| 2026-11-16 08:55 | c1193f8-dirty | fa1a9a7190 | 02_preprocess | 10 sessions requested; 10 included |
| 2026-11-16 08:59 | c1193f8-dirty | fa1a9a7190 | 03_prior_gate | GO: {'n_sessions': 10, 'median_corrected_r2': 0.07666797688600324, 'frac_sessions_p05': 0.4, 'fisher_p': 7.384381253053937e-05, 'n_pseudo': 200, 'decision': 'GO'} |
| 2026-11-16 09:00 | c1193f8-dirty | fa1a9a7190 | 04_fit_subspaces | d=5; 10/10 ok |
| 2026-11-16 | - | - | config | Renamed config section `null:` -> `pseudo_null:` (YAML parsed the key as None, crashing 05_decode). No values changed; config hash changes for this reason only. |
| 2026-11-16 09:02 | c1193f8-dirty | fa1a9a7190 | 02_preprocess | 16 sessions requested; 16 included |
| 2026-11-16 09:04 | c1193f8-dirty | 3d83323a46 | 05_decode | d=5; n_pseudo=200; 10/10 ok |
| 2026-11-16 09:04 | c1193f8-dirty | 3d83323a46 | 06_stats | d=5; 10 sessions/10 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.00293; P2 prior p_holm=0.884; P3 cur_side p_holm=0.0488 |
| 2026-11-16 09:09 | 3d808e1 | 3d83323a46 | 03_prior_gate | GO: {'n_sessions': 16, 'median_corrected_r2': 0.06424744950058905, 'frac_sessions_p05': 0.3125, 'fisher_p': 1.2266414803038271e-05, 'n_pseudo': 200, 'decision': 'GO'} |
| 2026-11-16 09:10 | 3d808e1-dirty | 3d83323a46 | 04_fit_subspaces | d=5; 16/16 ok |
| 2026-11-16 09:12 | 3d808e1-dirty | 3d83323a46 | 05_decode | d=5; n_pseudo=200; 16/16 ok |
| 2026-11-16 09:12 | 3d808e1-dirty | 3d83323a46 | 06_stats | d=5; 16 sessions/13 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.00256; P2 prior p_holm=0.892; P3 cur_side p_holm=0.0061 |
| 2026-11-16 09:15 | e8a277f | 3d83323a46 | 02_preprocess | 16 sessions requested; 16 included |
| 2026-11-16 09:17 | e8a277f-dirty | 3d83323a46 | 04_fit_subspaces | d=5; 16/16 ok |
| 2026-11-16 09:25 | e8a277f-dirty | 3d83323a46 | 05_decode | d=5; n_pseudo=200; 16/16 ok |
| 2026-11-16 09:25 | e8a277f-dirty | 3d83323a46 | 06_stats | d=5; 16 sessions/13 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.0479; P2 prior p_holm=0.999; P3 cur_side p_holm=0.0121 |
| 2026-11-16 09:27 | e8a277f-dirty | 3d83323a46 | 04_fit_subspaces | d=3; 16/16 ok |
| 2026-11-16 09:31 | e8a277f-dirty | 3d83323a46 | 05_decode | d=3; n_pseudo=200; 16/16 ok |
| 2026-11-16 09:31 | e8a277f-dirty | 3d83323a46 | 06_stats | d=3; 16 sessions/13 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.0491; P2 prior p_holm=0.227; P3 cur_side p_holm=0.11 |
| 2026-11-16 09:33 | e8a277f-dirty | 3d83323a46 | 04_fit_subspaces | d=10; 16/16 ok |
| 2026-11-16 09:36 | e8a277f-dirty | 3d83323a46 | 05_decode | d=10; n_pseudo=200; 16/16 ok |
| 2026-11-16 09:36 | e8a277f-dirty | 3d83323a46 | 06_stats | d=10; 12 sessions/10 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.00293; P2 prior p_holm=0.812; P3 cur_side p_holm=0.00586 |
| 2026-11-16 | - | - | note | The 09:15 02_preprocess row regenerated interim files (adds movement/feedback times; counts unchanged). The 09:17 04_fit_subspaces and 09:25 05_decode/06_stats rows are the trial-locked residual add-on (A11), written to results_residual/. |
| 2026-11-16 10:44 | 7820535 | 3d83323a46 | 08_robustness | POST HOC d=5; LOAO max p_holm P1=0.00513, P2=0.954, P3=0.0122 |
| 2026-11-16 10:44 | 7820535-dirty | 3d83323a46 | 08_robustness | [results: results_residual] POST HOC d=5; LOAO max p_holm P1=0.0923, P2=1, P3=0.0242 |
| 2026-11-16 10:47 | c6893b1-dirty | 3d83323a46 | 04_fit_subspaces | d=5; 16/16 ok |
| 2026-11-16 10:51 | c6893b1-dirty | 3d83323a46 | 05_decode | d=5; n_pseudo=200; 16/16 ok |
| 2026-11-16 10:51 | c6893b1-dirty | 3d83323a46 | 06_stats | d=5; 16 sessions/13 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.00256; P2 prior p_holm=0.892; P3 cur_side p_holm=0.0061 |
| 2026-11-16 10:52 | c6893b1-dirty | 3d83323a46 | 04_fit_subspaces | d=3; 16/16 ok |
| 2026-11-16 10:56 | c6893b1-dirty | 3d83323a46 | 05_decode | d=3; n_pseudo=200; 16/16 ok |
| 2026-11-16 10:56 | c6893b1-dirty | 3d83323a46 | 06_stats | d=3; 16 sessions/13 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.0322; P2 prior p_holm=0.207; P3 cur_side p_holm=0.11 |
| 2026-11-16 10:58 | c6893b1-dirty | 3d83323a46 | 04_fit_subspaces | d=10; 16/16 ok |
| 2026-11-16 11:01 | c6893b1-dirty | 3d83323a46 | 05_decode | d=10; n_pseudo=200; 16/16 ok |
| 2026-11-16 11:02 | c6893b1-dirty | 3d83323a46 | 06_stats | d=10; 12 sessions/10 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.00293; P2 prior p_holm=0.884; P3 cur_side p_holm=0.00586 |
| 2026-11-16 11:02 | c6893b1-dirty | 3d83323a46 | 08_robustness | POST HOC d=5; LOAO max p_holm P1=0.00513, P2=0.954, P3=0.0122 |
| 2026-11-16 11:03 | c6893b1-dirty | 3d83323a46 | 04_fit_subspaces | [results: results_residual] d=5; 16/16 ok |
| 2026-11-16 11:07 | c6893b1-dirty | 3d83323a46 | 05_decode | [results: results_residual] d=5; n_pseudo=200; 16/16 ok |
| 2026-11-16 11:07 | c6893b1-dirty | 3d83323a46 | 06_stats | [results: results_residual] d=5; 16 sessions/13 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.0134; P2 prior p_holm=0.996; P3 cur_side p_holm=0.00513 |
| 2026-11-16 11:08 | c6893b1-dirty | 3d83323a46 | 08_robustness | [results: results_residual] POST HOC d=5; LOAO max p_holm P1=0.0269, P2=0.998, P3=0.0103 |
| 2026-11-16 | - | - | note | Rows from 10:47 to 11:08 are the full rerun after amendment D10 (z-score SD floor; commit c6893b1). The "-dirty" flag on those rows is only the in-progress Fig 1b label fix in scripts/07_figures.py; no analysis code was uncommitted. Raw d=5 primary p-values are unchanged. Residual P1 Holm p went from 0.048 to 0.013. d=3 P1 went from 0.049 to 0.032. Earlier 08_robustness rows (before 10:47) are pre-fix. Pre-fix outputs are in results*/prefix_D10/. |
| 2026-11-17 03:03 | e965b42-dirty | 3d83323a46 | 09_fetch_state_signals | A12 pilot inputs; 1/1 ok |
| 2026-11-17 03:06 | e965b42-dirty | 3d83323a46 | 09_fetch_state_signals | A12 pilot inputs; 16/16 ok |
| 2026-11-17 03:32 | 540be37 | 3d83323a46 | 04_fit_subspaces | [results: results_stable] d=5; 13/13 ok |
| 2026-11-17 03:33 | 540be37 | 3d83323a46 | 05_decode | [results: results_stable] d=5; n_pseudo=200; 13/13 ok |
| 2026-11-17 03:33 | 540be37 | 3d83323a46 | 06_stats | [results: results_stable] d=5; 13 sessions/12 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.0022; P2 prior p_holm=0.974; P3 cur_side p_holm=0.0269 |
| 2026-11-17 03:33 | 540be37 | 3d83323a46 | 11_pilot_state | A12 pilot d=5: motion p=0.3934326171875, pupil p=0.419677734375, test1=survives, overall=mixed or undetermined |
| 2026-11-17 | - | - | note | Rows above marked [results: results_stable] and the 11_pilot_state row ran on PACE ICE (Slurm job 7133088, coc-cpu, 3 min; 45 tests passed there first). Stable-units copy: 13/16 sessions, 12 animals (KS023 22-unit session, SWC_038 46-unit session, SWC_043 excluded with < 20 stable units). |
| 2026-11-21 17:07 | fd5f3d4 | 3d83323a46 | 12_fetch_A13 | A13 inputs; 1/1 ok |
| 2026-11-22 06:21 | 3bc25d1 | 3d83323a46 | 12_fetch_A13 | A13 inputs; 16/16 ok |
| 2026-11-22 07:27 | 3bc25d1-dirty | 3d83323a46 | 04_fit_subspaces | [results: results_mua] d=5; 15/15 ok |
| 2026-11-22 07:28 | 3bc25d1-dirty | 3d83323a46 | 05_decode | [results: results_mua] d=5; n_pseudo=200; 15/15 ok |
| 2026-11-22 07:28 | 3bc25d1-dirty | 3d83323a46 | 06_stats | [results: results_mua] d=5; 15 sessions/12 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.0103; P2 prior p_holm=1; P3 cur_side p_holm=1 |
| 2026-11-22 07:28 | 3bc25d1-dirty | 3d83323a46 | 04_fit_subspaces | [results: results_ampstable] d=5; 5/5 ok |
| 2026-11-22 07:29 | 3bc25d1-dirty | 3d83323a46 | 05_decode | [results: results_ampstable] d=5; n_pseudo=200; 5/5 ok |
| 2026-11-22 07:29 | 3bc25d1-dirty | 3d83323a46 | 06_stats | [results: results_ampstable] d=5; 5 sessions/5 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.188; P2 prior p_holm=1; P3 cur_side p_holm=1 |
| 2026-11-22 07:29 | 3bc25d1-dirty | 3d83323a46 | 14_pilot_A13 | A13 pilot d=5: overall=sorting artifact |
| 2026-11-22 | - | - | note | Rows above marked [results: results_mua] / [results: results_ampstable] and the 14_pilot_A13 row ran on PACE ICE (Slurm job 7240337, coc-cpu, 5.5 min; 45 tests passed first). Multi-unit copy: 15/16 sessions, 12 animals (DY_014 had 8 channels < 10). Amplitude-stable copy: 5/16 sessions, 5 animals (most units have |amplitude trend| >= 0.5). |
| 2026-11-22 | - | - | note | The "-dirty" flag on the ICE rows reflects only files not synced to ICE (literature-review notes) and the log itself; the ICE code tree matched commit 3bc25d1. |
| 2026-11-22 10:28 | 7d0172d-dirty | 3d83323a46 | 04_fit_subspaces | [results: results_ampcorr_low] d=5; 16/16 ok |
| 2026-11-22 10:29 | 7d0172d-dirty | 3d83323a46 | 05_decode | [results: results_ampcorr_low] d=5; n_pseudo=200; 16/16 ok |
| 2026-11-22 10:29 | 7d0172d-dirty | 3d83323a46 | 06_stats | [results: results_ampcorr_low] d=5; 16 sessions/13 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.000366; P2 prior p_holm=0.729; P3 cur_side p_holm=0.0061 |
| 2026-11-22 10:30 | 7d0172d-dirty | 3d83323a46 | 04_fit_subspaces | [results: results_ampcorr_high] d=5; 16/16 ok |
| 2026-11-22 10:31 | 7d0172d-dirty | 3d83323a46 | 05_decode | [results: results_ampcorr_high] d=5; n_pseudo=200; 16/16 ok |
| 2026-11-22 10:31 | 7d0172d-dirty | 3d83323a46 | 06_stats | [results: results_ampcorr_high] d=5; 16 sessions/13 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.00183; P2 prior p_holm=0.706; P3 cur_side p_holm=0.0134 |
| 2026-11-22 10:31 | 7d0172d-dirty | 3d83323a46 | 04_fit_subspaces | [results: results_ampcorr_slow] d=5; 16/16 ok |
| 2026-11-22 10:32 | 7d0172d-dirty | 3d83323a46 | 05_decode | [results: results_ampcorr_slow] d=5; n_pseudo=200; 16/16 ok |
| 2026-11-22 10:32 | 7d0172d-dirty | 3d83323a46 | 06_stats | [results: results_ampcorr_slow] d=5; 16 sessions/13 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.00366; P2 prior p_holm=0.632; P3 cur_side p_holm=0.0105 |
| 2026-11-22 10:32 | 7d0172d-dirty | 3d83323a46 | 16_pilot_A14 | A14 pilot d=5: overall=amplitude cannot account for the mode |
| 2026-11-22 | - | - | note | Rows above marked [results: results_ampcorr_*] and the 16_pilot_A14 row ran on PACE ICE (Slurm job 7241313, coc-cpu, 6 min; 50 tests passed first; code tree matched commit 7d0172d, "-dirty" reflects unsynced documents only). All 16 sessions / 13 animals in every corrected copy. A local smoke run of 15_build_A14 (all sessions, results in the scratchpad) preceded the ICE run and motivated the two post hoc checks recorded in AMENDMENTS (A14 post hoc additions). |
| 2026-11-22 11:25 | 0d4b1a0 | 3d83323a46 | 18_pilot_A15 | A15 d=5: replication=replicates; shared p=0.485; RT p=0.122; acc p=0.342 |
| 2026-11-22 10:57 | 30d2c3f-dirty | 3d83323a46 | 04_fit_subspaces | [results: results_region2] d=5; 15/15 ok |
| 2026-11-22 11:02 | 9385d5a | 3d83323a46 | 05_decode | [results: results_region2] d=5; n_pseudo=200; 15/15 ok |
| 2026-11-22 11:02 | 9385d5a | 3d83323a46 | 06_stats | [results: results_region2] d=5; 15 sessions/12 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.00366; P2 prior p_holm=0.515; P3 cur_side p_holm=0.0122 |
| 2026-11-22 11:25 | 0d4b1a0 | 3d83323a46 | 03_prior_gate | [results: results_region2] GO: {'n_sessions': 15, 'median_corrected_r2': 0.0010954173393297184, 'frac_sessions_p05': 0.4, 'fisher_p': 0.0019458608951450434, 'n_pseudo': 200, 'decision': 'GO'} |
| 2026-11-22 | - | - | note | Rows above marked [results: results_region2] and the 18_pilot_A15 row ran locally on cached data (A15). 17_build_region2 ran locally before them (15/16 sessions, 12 animals; ZM_2245 has no non-MOs region with >= 20 good units). The first 03_prior_gate call failed on an unsupported --d flag and was rerun without it. |
| 2026-11-22 18:03 | a1b2efc | 3d83323a46 | 22_pilot_A16 | A16 d=5: detrend q=not masked by a smooth trend, c=not masked by a smooth trend; step sessions=1 |
| 2026-11-22 17:30 | 2cc9386-dirty | 3d83323a46 | 04_fit_subspaces | [results: results_detrend_q] d=5; 16/16 ok |
| 2026-11-22 17:33 | 73ffa82-dirty | 3d83323a46 | 05_decode | [results: results_detrend_q] d=5; n_pseudo=200; 16/16 ok |
| 2026-11-22 17:33 | 73ffa82-dirty | 3d83323a46 | 06_stats | [results: results_detrend_q] d=5; 16 sessions/13 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.00256; P2 prior p_holm=0.58; P3 cur_side p_holm=0.216 |
| 2026-11-22 17:34 | 73ffa82-dirty | 3d83323a46 | 04_fit_subspaces | [results: results_detrend_c] d=5; 16/16 ok |
| 2026-11-22 17:43 | 73ffa82-dirty | 3d83323a46 | 05_decode | [results: results_detrend_c] d=5; n_pseudo=200; 16/16 ok |
| 2026-11-22 17:43 | 73ffa82-dirty | 3d83323a46 | 06_stats | [results: results_detrend_c] d=5; 16 sessions/13 animals; P1 geometry IUT (cross > same at both lags) p_holm=0.000732; P2 prior p_holm=0.294; P3 cur_side p_holm=0.0061 |
| 2026-11-22 | - | - | note | A16 (post hoc) ran locally: 21_build_detrend then 04-06 on data_detrend_q / data_detrend_c (rows marked [results: results_detrend_*]); 22_pilot_A16 above. A --skip-lasso smoke run preceded the full run (its log row was discarded). |
| 2026-11-22 | - | - | note | Row order: some rows above are out of time order because runs on copied data folders log into their own results_*/ANALYSIS_LOG.md (log_run rule), and those rows were merged into this file afterwards. The A15 rows (10:57–11:25) and the A16 rows (17:30–18:03) are examples. Timestamps and commit hashes in each row are as written at run time; no row was edited. |
| 2026-11-22 | - | - | note | Documentation pass, no analysis rerun. README.md rewritten for scripts 01-22, derived data/results folders, slurm/ files, and report/slide rebuilds. RESULTS.md made consistent with the final report (4928ad2) and slides (b3b60d2): averaging labelled (mouse vs session means), terminology (pre-registered / prospectively documented exploratory / post hoc), stale slide outline removed; every number re-checked against the result files. Corrected: session-mean cross-lag angle 71.9 -> 72.1 deg and first angle 52.6 -> 53.3 (both pairings averaged, as geometry_sessions.csv); A16 cosine-detrend P2 change +0.021 -> +0.020; A14 isolated-spike share 47% -> 46.5%; A13 multi-unit comparison now against the same-session original 0.88 (was the all-session 0.84); DY_014 rate loss restated (57% in spikes/s, 40% on the sqrt scale); 30 s windows per session about 120 -> about 130 (median 133). AMENDMENTS.md: index added at the top, no entry changed. Docstring-only fixes in scripts 11, 14, 16, 19, 22 and src/pns/slowmode.py. pytest: 50 passed, 1 skipped. |
| 2026-11-22 | - | - | note | Deviation found in the documentation audit: A15's pre-registration excludes 'root, void and fiber tracts', but scripts/17_build_region2.py excludes only MOs, root and void. None of the 15 chosen second-region areas is a fiber tract, so no result is affected. Also corrected: the report's unverifiable 'mean 5.1 s' stimulus interval was removed (median 3.9 s kept), and the slides' DY_014 rate loss now reads 164 to 71 Hz (57%; the earlier '40%' was on the sqrt scale). |
| 2026-11-23 18:34 | 4dee202 | 3d83323a46 | 23_timescales_A17 | A17 part 0: 16 sessions, 215 blocks; tau_pi median 67 s (16.9 trials); rho_pi 30 s 0.77, 120 s 0.10 |
| 2026-11-23 18:44 | 0dbca28-dirty | 3d83323a46 | 24_budget_A17 | A17 part 1: 16 sessions; median lowfreq_cos 0.226, prior_trial_corr 0.0020, prior_bin_corr 0.0009 |
| 2026-11-23 18:48 | 0dbca28-dirty | 3d83323a46 | 25_longlag_A17 | A17 part 2: reading=no band selection; reproduction c=True, q=True; 60 s vs 0.5 s p: c=0.294, q=0.554 |
| 2026-11-23 18:41 | 0dbca28-dirty | 249a048f17 | 04_fit_subspaces | [results: results_a17_longlag_c] d=5; 16/16 ok |
| 2026-11-23 18:44 | 0dbca28-dirty | 249a048f17 | 05_decode | [results: results_a17_longlag_c] d=5; n_pseudo=200; 16/16 ok |
| 2026-11-23 18:46 | 0dbca28-dirty | 249a048f17 | 04_fit_subspaces | [results: results_a17_longlag_q] d=5; 16/16 ok |
| 2026-11-23 18:48 | 0dbca28-dirty | 249a048f17 | 05_decode | [results: results_a17_longlag_q] d=5; n_pseudo=200; 16/16 ok |
| 2026-11-23 | - | - | note | Rows above marked [results: results_a17_longlag_c/q] ran locally (A17 part 2: scripts 04 and 05 with config_a17_longlag.yaml on data_detrend_c/q) and were merged here from those roots' own logs. Reproduction check in 25_longlag_A17 passed: alpha and rrr_1/4/16/60, pca, random scores equal results_detrend_c/q (max abs diff < 2e-14). |
| 2026-11-23 | - | - | note | The 24_budget_A17, 25_longlag_A17 and A17 part 2 04/05 rows above ran at 0dbca28-dirty; the code they used (pipeline alpha_lags/check_lags, scripts 24 and 25, config_a17_longlag.yaml) is committed unchanged in 8486770. A18 code in 8486770 has run on synthetic data only; no real-data A18 analysis has run. |
| 2026-11-24 05:00 | 1a32b05-dirty | 3d83323a46 | 23_timescales_A17 | A17 part 0: 16 sessions, 215 blocks; tau_pi median 67 s (16.9 trials); rho_pi 30 s 0.77, 120 s 0.10 |
| 2026-11-24 | - | - | note | Documentation pass (README, RESULTS A17 section): every A17 number re-read from results/a17/{timescales,budget,longlag}.json and longlag_{c,q}.csv; office-hours note corrected (prior still predictable at 2 min is 0.013, not 0.02). No analysis rerun. |
| 2026-11-24 18:18 | 3a81ba1 | 3d83323a46 | 26_sim_A18 targets | A18 real calibration targets: 16 sessions |
| 2026-11-24 18:38 | 3a81ba1-dirty | 3d83323a46 | 26_sim_A18 calibrate | A18 calibration: lowrank accepted {'prior_gain': True, 'drift_gain': True, 'drift_mid': True, 'history_gain': True, 'evoked_gain': True, 'stim_gain': True}; per_unit accepted {'drift_gain': True, 'drift_mid': True} |
