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
