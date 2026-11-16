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
