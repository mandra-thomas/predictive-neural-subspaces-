"""Amendment A17 Part 0 (post hoc): timescales of the task and of the Bayes-optimal block prior. Task data only.

Per session: duration, median stimulus interval, completed-block durations, the prior's autocorrelation rho_pi at
fixed lags, its integrated timescale tau_pi (seconds and trials; truncated at the first zero crossing), and the
fraction of the per-bin prior's variance inside the >= 20 min cosine span (what the A16 cosine detrend removes).
Sensitivity (added 2026-11-24 after an outside review): the same timescale computed on the trial-indexed prior (one
value per trial with a valid stimOn, lags in trials), so it does not depend on how the prior is spread over 0.5 s
bins; plus the session spread (IQR, and a bootstrap interval for the median over sessions).

Writes results/a17/timescales.csv (per session), results/a17/blocks.csv (every completed block),
results/a17/prior_acf.csv (dense log-spaced ACF per session, for the figure) and results/a17/timescales.json.
"""
import json

import numpy as np
import pandas as pd

from pns.config import load_frozen
from pns.runner import interim_path, load_npz, log_run, out_dir, setup, write_json
from pns.timescales import acf, integrated_timescale, prior_cosine_fraction, prior_per_bin, session_timescales

LAGS_S = [0.5, 2, 8, 30, 60, 120, 240, 480]
MAX_LAG_S = 20 * 60
LAGS_TRIALS = [8, 15, 30, 60]
MAX_LAG_TRIALS = 300


def boot_median(x, n=5000, seed=0):
    """Percentile bootstrap 95% interval of the median over sessions (sessions resampled; 13 mice, 16 sessions)."""
    rng = np.random.default_rng(seed)
    b = np.median(rng.choice(x, (n, len(x))), axis=1)
    return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def main():
    args, cfg, _ = setup(__doc__)
    bin_s = cfg["binning"]["bin_s"]
    frozen = load_frozen(cfg)
    od = out_dir(cfg, "a17")
    dense = np.unique(np.round(np.logspace(0, np.log10(MAX_LAG_S / bin_s), 70)).astype(int))
    rows, blocks, curves = [], [], []
    for s in frozen["sessions"]:
        eid, subj = s["eid"], s["subject"]
        pre = load_npz(interim_path(cfg, eid))
        ts = session_timescales(pre)
        x = prior_per_bin(pre)
        rho = acf(x, [int(round(l / bin_s)) for l in LAGS_S])
        tau_s, zero_s = integrated_timescale(x, bin_s, int(MAX_LAG_S / bin_s))
        row = {"eid": eid, "subject": subj, "duration_min": ts["duration_min"],
               "stim_interval_s": ts["stim_interval_s"], "n_blocks": ts["n_blocks"],
               "block_trials_median": float(np.median(ts["block_trials"])),
               "block_min_median": float(np.nanmedian(ts["block_min"])),
               "tau_pi_s": tau_s, "tau_pi_trials": tau_s / ts["stim_interval_s"], "first_zero_s": zero_s,
               "prior_cosine_fraction": prior_cosine_fraction(pre)}
        row.update({f"rho_{l:g}s": r for l, r in zip(LAGS_S, rho)})
        p_tr = np.asarray(pre["prior"], float)[np.isfinite(np.asarray(pre["stimOn_times"], float))]
        tau_tr, zero_tr = integrated_timescale(p_tr, 1.0, MAX_LAG_TRIALS)
        row.update({"tau_pi_trials_trialidx": tau_tr, "first_zero_trials_trialidx": zero_tr})
        row.update({f"rho_{l}tr_trialidx": r for l, r in zip(LAGS_TRIALS, acf(p_tr, LAGS_TRIALS))})
        rows.append(row)
        blocks += [{"eid": eid, "subject": subj, "trials": n, "minutes": m}
                   for n, m in zip(ts["block_trials"], ts["block_min"])]
        curves += [{"eid": eid, "lag_s": k * bin_s, "rho": r} for k, r in zip(dense, acf(x, dense))]
    df = pd.DataFrame(rows)
    bl = pd.DataFrame(blocks)
    df.to_csv(od / "timescales.csv", index=False)
    bl.to_csv(od / "blocks.csv", index=False)
    pd.DataFrame(curves).to_csv(od / "prior_acf.csv", index=False)
    summ = {
        "n_sessions": len(df), "n_blocks": int(len(bl)),
        "duration_min_median": float(df.duration_min.median()),
        "duration_min_range": [float(df.duration_min.min()), float(df.duration_min.max())],
        "stim_interval_s_median": float(df.stim_interval_s.median()),
        "block_trials_median": float(bl.trials.median()),
        "block_min_median": float(bl.minutes.median()),
        "block_min_iqr": [float(bl.minutes.quantile(0.25)), float(bl.minutes.quantile(0.75))],
        "tau_pi_s_median": float(df.tau_pi_s.median()), "tau_pi_trials_median": float(df.tau_pi_trials.median()),
        "first_zero_s_median": float(df.first_zero_s.median()),
        "tau_pi_s_iqr": [float(df.tau_pi_s.quantile(0.25)), float(df.tau_pi_s.quantile(0.75))],
        "tau_pi_s_median_boot95": boot_median(df.tau_pi_s.values),
        "trial_indexed": {
            "tau_trials_median": float(df.tau_pi_trials_trialidx.median()),
            "tau_trials_iqr": [float(df.tau_pi_trials_trialidx.quantile(0.25)),
                               float(df.tau_pi_trials_trialidx.quantile(0.75))],
            "tau_trials_median_boot95": boot_median(df.tau_pi_trials_trialidx.values),
            "first_zero_trials_median": float(df.first_zero_trials_trialidx.median()),
            "rho_median": {f"{l}tr": float(df[f"rho_{l}tr_trialidx"].median()) for l in LAGS_TRIALS},
        },
        "prior_cosine_fraction_median": float(df.prior_cosine_fraction.median()),
        "prior_cosine_fraction_range": [float(df.prior_cosine_fraction.min()), float(df.prior_cosine_fraction.max())],
        "rho_median": {f"{l:g}s": float(df[f"rho_{l:g}s"].median()) for l in LAGS_S},
        "rho_range": {f"{l:g}s": [float(df[f"rho_{l:g}s"].min()), float(df[f"rho_{l:g}s"].max())] for l in LAGS_S},
    }
    write_json(od / "timescales.json", summ)
    print(json.dumps(summ, indent=1))
    log_run(cfg, "23_timescales_A17",
            f"A17 part 0: {len(df)} sessions, {len(bl)} blocks; tau_pi median {summ['tau_pi_s_median']:.0f} s "
            f"({summ['tau_pi_trials_median']:.1f} trials); rho_pi 30 s {summ['rho_median']['30s']:.2f}, "
            f"120 s {summ['rho_median']['120s']:.2f}")


if __name__ == "__main__":
    main()
