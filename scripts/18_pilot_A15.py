"""Amendment A15 (local): second-region replication reading, cross-region slow-mode sharing, behaviour beyond trend.

Part 1  reads results_region2/{gate/summary.json, stats/d5/primary.csv, stats/d5/matrix.csv} with the A15 criteria.
Part 2  signed correlation of quadratic-residualised MOs and second-region slow modes (MOs 30 s windows),
        cross-session null, one-sided Wilcoxon across animals.
Part 3  MOs slow mode vs log reaction time and accuracy beyond a quadratic trend, as in A13 part 1.
Writes results/a15/{sessions_d5.csv, summary_d5.json}.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sps

from pns.config import load_frozen
from pns.pipeline import session_S
from pns.runner import interim_path, load_npz, log_run, out_dir, setup
from pns.slowmode import (bin_centres, corr_aligned, event_windows, residualize_quadratic, slow_direction, slow_mode,
                          window_edges, window_means)
from pns.stats import wilcoxon_greater


def extra(p):
    p.add_argument("--d", type=int, default=None)
    p.add_argument("--r2-data", default="data_region2")
    p.add_argument("--r2-results", default="results_region2")


def animal_test(df, col, subjects, greater=True):
    sub = df.dropna(subset=[col])
    a = sub.assign(subject=sub.eid.map(subjects)).groupby("subject")[col].mean().to_numpy()
    if greater:
        p = wilcoxon_greater(a)["p"]
    else:
        p = float(sps.wilcoxon(a).pvalue) if len(a) > 1 else np.nan
    return {"n_animals": int(len(a)), "n_sessions": int(len(sub)), "mean": float(np.mean(a)) if len(a) else None,
            "median": float(np.median(a)) if len(a) else None, "p": p}


def main():
    args, cfg, _ = setup(__doc__, extra)
    d = args.d or cfg["model"]["d"]
    long_ = max(cfg["lags_bins"])
    frozen = load_frozen(cfg)
    subjects = {s["eid"]: s["subject"] for s in frozen["sessions"]}
    r2root, r2res = Path(args.r2_data), Path(args.r2_results)
    r2frozen = json.loads((r2root / "meta" / "frozen.json").read_text())
    r2meta = {r["eid"]: r for r in json.loads((r2root / "meta" / "a15_sessions.json").read_text())}
    r2eids = [s["eid"] for s in r2frozen["sessions"]]
    od = out_dir(cfg, "a15")

    S_, rows = {}, {}
    for e in subjects:
        pre = load_npz(interim_path(cfg, e))
        fits = load_npz(out_dir(cfg, "subspaces") / f"{e}_d{d}.npz")
        sw, _, _ = slow_mode(pre, fits, session_S(pre), long_)
        ew = window_edges(pre)
        stim = np.asarray(pre["stimOn_times"], float)
        rt = np.asarray(pre["firstMovement_times"], float) - stim
        lrt = np.where((rt > 0.05) & (rt < 30), np.log(np.where(rt > 0, rt, np.nan)), np.nan)
        acc = np.where(np.isfinite(stim), (np.asarray(pre["feedbackType"]) > 0).astype(float), np.nan)
        S_[e] = {"res_s": residualize_quadratic(sw),
                 "res_RT": residualize_quadratic(event_windows(stim, lrt, ew)),
                 "res_ACC": residualize_quadratic(event_windows(stim, acc, ew))}
        r = {"eid": e, "subject": subjects[e], "region2": r2meta.get(e, {}).get("region2"),
             "same_probe_as_mos": r2meta.get(e, {}).get("same_probe_as_mos")}
        f2 = r2res / "subspaces" / f"{e}_d{d}.npz"
        if e in r2eids and f2.exists():
            pre2 = load_npz(r2root / "interim" / f"{e}.npz")
            fits2 = load_npz(f2)
            s2 = ((session_S(pre2) - fits2["z_mu"]) / fits2["z_sd"]) @ slow_direction(fits2, long_)
            w2 = window_means(bin_centres(pre2), s2, np.asarray(pre2["valid"], bool), ew)
            t = np.arange(len(w2), dtype=float)
            ok = np.isfinite(w2)
            w2 = w2 * (1.0 if np.corrcoef(w2[ok], t[ok])[0, 1] >= 0 else -1.0)
            S_[e]["res_r2"] = residualize_quadratic(w2)
            r["raw_match"] = corr_aligned(sw, w2, absolute=False)
        rows[e] = r

    # part 2: shared fluctuations beyond the trend
    have = [e for e in subjects if "res_r2" in S_[e]]
    for e in subjects:
        if e not in have:
            rows[e].update({"share_r": np.nan, "share_corrected": np.nan})
            continue
        real = corr_aligned(S_[e]["res_s"], S_[e]["res_r2"], absolute=False)
        null = np.array([corr_aligned(S_[e]["res_s"], S_[j]["res_r2"], absolute=False) for j in have if j != e])
        null = null[np.isfinite(null)]
        rows[e].update({"share_r": real, "share_corrected": real - np.median(null) if len(null) else np.nan})

    # part 3: behaviour beyond the trend
    eids = list(subjects)
    for sig in ("RT", "ACC"):
        for e in eids:
            real = corr_aligned(S_[e]["res_s"], S_[e][f"res_{sig}"])
            cross = np.array([corr_aligned(S_[e]["res_s"], S_[j][f"res_{sig}"]) for j in eids if j != e])
            cross = cross[np.isfinite(cross)]
            rows[e].update({f"{sig}_r": real,
                            f"{sig}_signed_r": corr_aligned(S_[e]["res_s"], S_[e][f"res_{sig}"], absolute=False),
                            f"{sig}_corrected": real - np.median(cross) if len(cross) else np.nan})

    df = pd.DataFrame(list(rows.values()))

    # part 1: replication reading
    part1 = {"available": (r2res / "stats" / f"d{d}" / "primary.csv").exists()}
    if part1["available"]:
        pr = pd.read_csv(r2res / "stats" / f"d{d}" / "primary.csv")
        ph = dict(zip(pr.test.str.split(" ").str[0], pr.p_holm))
        m = pd.read_csv(r2res / "stats" / f"d{d}" / "matrix.csv")
        el = float(m[(m.feature_set == f"rrr_{long_}") & (m.variable == "elapsed_time")]["mean"].iloc[0])
        gate = json.loads((r2res / "gate" / "summary.json").read_text())
        crit = {"P1_sig": ph["P1"] < 0.05, "P3_sig": ph["P3"] < 0.05, "P2_not_sig": ph["P2"] >= 0.05,
                "elapsed_r2_ge_0.5": el >= 0.5}
        n_ok = sum(crit.values())
        part1.update({"primary_holm": ph, "elapsed_r2": el, "gate": gate, "prior_in_population": gate["fisher_p"] < 0.05,
                      "criteria": crit,
                      "reading": "replicates" if n_ok == 4 else "partial" if n_ok >= 2 else "does not replicate"})
    summ = {
        "part1_replication": part1,
        "part2_shared_slow_mode": animal_test(df, "share_corrected", subjects),
        "part2_raw_match_median": float(np.nanmedian(df.raw_match)) if "raw_match" in df else None,
        "part2_detrended_r_median": float(np.nanmedian(df.share_r)),
        "part2_n_same_probe": int(df.same_probe_as_mos.fillna(False).astype(bool).sum()),
        "part3_rt": animal_test(df, "RT_corrected", subjects),
        "part3_rt_sign": animal_test(df, "RT_signed_r", subjects, greater=False),
        "part3_accuracy": animal_test(df, "ACC_corrected", subjects),
        "part3_accuracy_sign": animal_test(df, "ACC_signed_r", subjects, greater=False),
    }
    df.to_csv(od / f"sessions_d{d}.csv", index=False)
    (od / f"summary_d{d}.json").write_text(json.dumps(summ, indent=1, default=float))
    pd.set_option("display.width", 250)
    print(df.round(3).to_string(index=False))
    print(json.dumps(summ, indent=1, default=float))
    log_run(cfg, "18_pilot_A15", f"A15 d={d}: replication={part1.get('reading')}; "
            f"shared p={summ['part2_shared_slow_mode']['p']:.3g}; RT p={summ['part3_rt']['p']:.3g}; "
            f"acc p={summ['part3_accuracy']['p']:.3g}")


if __name__ == "__main__":
    main()
