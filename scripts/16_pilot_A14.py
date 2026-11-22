"""Amendment A14 third pilot (runs on ICE after 15_build_A14 and the 04-06 refits on both corrected copies).

Part 1  fluctuation amplitude-rate coupling (session median over units, animal means, one-sided Wilcoxon > 0).
Part 2  readings of the conservative and maximal amplitude-corrected refits (elapsed-time R2 of the 30 s subspace
        relative to the original) and, without refitting, the residual ramp fraction along the original slow direction.
Part 3  early-concentration index of amplitude change (and, secondary, of the slow mode itself).
Writes results/a14/{sessions_d5.csv, summary_d5.json}.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from pns.ampcorr import early_index
from pns.config import load_frozen
from pns.pipeline import session_S
from pns.runner import interim_path, load_npz, log_run, out_dir, setup
from pns.slowmode import bin_centres, slow_direction, slow_mode, window_edges, window_means
from pns.stats import wilcoxon_greater


def extra(p):
    p.add_argument("--d", type=int, default=None)
    p.add_argument("--low", default="ampcorr_low")
    p.add_argument("--high", default="ampcorr_high")
    p.add_argument("--slow", default="ampcorr_slow")


def elapsed_r2(root, d, long_):
    m = pd.read_csv(Path(root) / "stats" / f"d{d}" / "matrix.csv")
    return float(m[(m.feature_set == f"rrr_{long_}") & (m.variable == "elapsed_time")]["mean"].iloc[0])


def reading(orig_root, root, d, long_):
    if not (Path(root) / "stats" / f"d{d}" / "matrix.csv").exists():
        return {"available": False}
    e0, e1 = elapsed_r2(orig_root, d, long_), elapsed_r2(root, d, long_)
    dd = pd.read_csv(Path(root) / "stats" / f"d{d}" / "drift.csv")
    pr = pd.read_csv(Path(root) / "stats" / f"d{d}" / "primary.csv")
    frac = e1 / e0
    return {"available": True, "elapsed_r2_original": e0, "elapsed_r2": e1, "fraction_of_original": frac,
            "drift_flags": int(dd.drift_flag.sum()), "n_sessions": int(len(dd)),
            "primary_holm": dict(zip(pr.test.str.split(" ").str[0], pr.p_holm)),
            "reading": "survives" if frac >= 0.75 else "removed" if frac < 0.5 else "intermediate"}


def window_slope(pre, s_bins):
    sw = window_means(bin_centres(pre), s_bins, np.asarray(pre["valid"], bool), window_edges(pre))
    t = np.arange(len(sw), dtype=float)
    ok = np.isfinite(sw)
    return float(np.polyfit(t[ok], sw[ok], 1)[0])


def animal_test(df, col, subjects):
    sub = df.dropna(subset=[col])
    a = sub.assign(subject=sub.eid.map(subjects)).groupby("subject")[col].mean().to_numpy()
    return {"n_animals": int(len(a)), "n_sessions": int(len(sub)), "mean": float(np.mean(a)) if len(a) else None,
            "median": float(np.median(a)) if len(a) else None, "p": wilcoxon_greater(a)["p"]}


def main():
    args, cfg, _ = setup(__doc__, extra)
    d = args.d or cfg["model"]["d"]
    long_ = max(cfg["lags_bins"])
    frozen = load_frozen(cfg)
    subjects = {s["eid"]: s["subject"] for s in frozen["sessions"]}
    od = out_dir(cfg, "a14")
    rows = []
    for e in subjects:
        pre = load_npz(interim_path(cfg, e))
        fits = load_npz(out_dir(cfg, "subspaces") / f"{e}_d{d}.npz")
        u = pd.read_csv(od / f"units_{e}.csv")
        sw, _, sign = slow_mode(pre, fits, session_S(pre), long_)
        v = sign * slow_direction(fits, long_)
        r = {"eid": e, "subject": subjects[e],
             "beta_fluct_q2": float(np.nanmedian(u.beta_fluct_q2)),
             "beta_fluct_q5": float(np.nanmedian(u.beta_fluct_q5)),
             "frac_pos_q2": float(np.mean(u.beta_fluct_q2.dropna() > 0)),
             "beta_total": float(np.nanmedian(u.beta_total)),
             "beta_fluct_q2_isolated": float(np.nanmedian(u.beta_fluct_q2_isolated)),
             "beta_slow": float(np.nanmedian(u.beta_slow)),
             "early_amp": float(np.nanmedian(u.early_index)) if u.early_index.notna().any() else np.nan,
             "n_units_early": int(u.early_index.notna().sum()),
             "early_slow": early_index(sw, 1.0)}
        s0 = window_slope(pre, ((session_S(pre) - fits["z_mu"]) / fits["z_sd"]) @ v)
        for k, name in (("low", args.low), ("high", args.high), ("slow", args.slow)):
            cp = load_npz(Path(f"data_{name}") / "interim" / f"{e}.npz")
            s1 = window_slope(cp, ((session_S(cp) - fits["z_mu"]) / fits["z_sd"]) @ v)
            r[f"ramp_fraction_{k}"] = s1 / s0 if s0 != 0 else np.nan
        rows.append(r)
    df = pd.DataFrame(rows)
    orig = cfg["paths"]["results"]
    summ = {
        "part1_fluct_coupling_q2": animal_test(df, "beta_fluct_q2", subjects),
        "part1_fluct_coupling_q5": animal_test(df, "beta_fluct_q5", subjects),
        "part1_frac_units_positive_median": float(df.frac_pos_q2.median()),
        "total_coupling_median": float(df.beta_total.median()),
        "part2_low": reading(orig, f"results_{args.low}", d, long_),
        "part2_high": reading(orig, f"results_{args.high}", d, long_),
        "part2_ramp_fraction_low_median": float(df.ramp_fraction_low.median()),
        "part2_ramp_fraction_high_median": float(df.ramp_fraction_high.median()),
        "posthoc_1b_isolated_coupling": animal_test(df, "beta_fluct_q2_isolated", subjects),
        "posthoc_slow_maximal": reading(orig, f"results_{args.slow}", d, long_),
        "posthoc_ramp_fraction_slow_median": float(df.ramp_fraction_slow.median()),
        "part3_early_amp": animal_test(df, "early_amp", subjects),
        "part3_early_slow": animal_test(df, "early_slow", subjects),
    }
    coup = summ["part1_fluct_coupling_q2"]["p"] < 0.05
    lo, hi = summ["part2_low"].get("reading"), summ["part2_high"].get("reading")
    if hi == "survives":
        overall = "amplitude cannot account for the mode"
    elif coup and lo == "removed":
        overall = "detection loss sufficient"
    elif coup and lo == "intermediate":
        overall = "detection loss contributes"
    elif coup and lo == "survives":
        overall = "coupling without sufficiency"
    else:
        overall = "undetermined"
    summ["overall_reading"] = overall
    df.to_csv(od / f"sessions_d{d}.csv", index=False)
    (od / f"summary_d{d}.json").write_text(json.dumps(summ, indent=1, default=float))
    pd.set_option("display.width", 250)
    print(df.round(3).to_string(index=False))
    print(json.dumps(summ, indent=1, default=float))
    log_run(cfg, "16_pilot_A14", f"A14 pilot d={d}: overall={overall}")


if __name__ == "__main__":
    main()
