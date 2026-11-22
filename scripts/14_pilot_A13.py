"""Amendment A13 second pilot (runs on ICE after 13_build_A13 and the 04-06 refits on data_mua / data_ampstable).

Part 1  engagement (IBL GLM-HMM p_state1) and satiety (cumulative rewards) versus the slow mode after removing a
        quadratic time trend from each; session-permutation null; one-sided Wilcoxon across animals.
Part 2a within-session Spearman(unit slow-mode loading, unit amplitude trend); Fisher z, animal means, Wilcoxon > 0.
Part 2b amplitude-stable refit, read with the A12 test-1 rules.
Part 3a multi-unit refit: elapsed-time R2 of the 30 s subspace, and |r| between multi-unit and unit slow modes.
Part 3b Spearman(multi-unit slow-mode loadings, depth derivative of the mean multi-unit rate profile); shuffle null;
        Fisher-combined across sessions.
Writes results/a13/{sessions.csv, summary.json}.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sps

from pns.config import load_frozen
from pns.pipeline import session_S
from pns.runner import interim_path, load_npz, log_run, out_dir, setup
from pns.slowmode import (bin_centres, corr_aligned, event_windows, residualize_quadratic, slow_mode, spearman,
                          window_edges)
from pns.stats import fisher_combine, wilcoxon_greater

N_SHUFFLE = 2000


def extra(p):
    p.add_argument("--d", type=int, default=None)
    p.add_argument("--mua-data", default="data_mua")
    p.add_argument("--mua-results", default="results_mua")
    p.add_argument("--amp-results", default="results_ampstable")


def reading_test1(orig_root, root, d, long_):
    """A12 test-1 rules applied to a refit results folder."""
    mfile = Path(root) / "stats" / f"d{d}" / "matrix.csv"
    if not mfile.exists():
        return {"available": False}

    def elapsed(r):
        m = pd.read_csv(Path(r) / "stats" / f"d{d}" / "matrix.csv")
        return float(m[(m.feature_set == f"rrr_{long_}") & (m.variable == "elapsed_time")]["mean"].iloc[0])
    dd = pd.read_csv(Path(root) / "stats" / f"d{d}" / "drift.csv")
    p = pd.read_csv(Path(root) / "stats" / f"d{d}" / "primary.csv")
    e0, e1 = elapsed(orig_root), elapsed(root)
    f1, n1 = int(dd.drift_flag.sum()), int(len(dd))
    out = {"available": True, "elapsed_r2_original": e0, "elapsed_r2": e1, "drift_flags": f1, "n_sessions": n1,
           "primary_holm": dict(zip(p.test.str.split(" ").str[0], p.p_holm))}
    out["reading"] = ("turnover-driven" if (e1 < 0.5 * e0 and f1 <= 0.25 * n1)
                      else "survives" if e1 >= 0.75 * e0 else "intermediate")
    return out


def animal_test(df, col, subjects, greater=True):
    sub = df.dropna(subset=[col])
    a = sub.assign(subject=sub.eid.map(subjects)).groupby("subject")[col].mean().to_numpy()
    if greater:
        t = wilcoxon_greater(a)
    else:
        a2 = a[np.isfinite(a)]
        t = {"n": len(a2), "p": float(sps.wilcoxon(a2).pvalue) if len(a2) > 1 else np.nan}
    return {"n_animals": int(len(a)), "n_sessions": int(len(sub)), "mean": float(np.mean(a)) if len(a) else None,
            "p": t["p"]}


def main():
    args, cfg, _ = setup(__doc__, extra)
    d = args.d or cfg["model"]["d"]
    long_ = max(cfg["lags_bins"])
    frozen = load_frozen(cfg)
    subjects = {s["eid"]: s["subject"] for s in frozen["sessions"]}
    eids = list(subjects)
    od = out_dir(cfg, "a13")
    rng = np.random.default_rng(cfg["seed"])

    # ---------------- slow modes (original fits) and per-session signals
    eng_all = pd.read_parquet(Path(cfg["paths"]["data"]) / "external" / "engage" / "merged_behavioral_and_states.pqt")
    S_, rows = {}, {}
    for e in eids:
        pre = load_npz(interim_path(cfg, e))
        fits = load_npz(out_dir(cfg, "subspaces") / f"{e}_d{d}.npz")
        sw, load, sign = slow_mode(pre, fits, session_S(pre), long_)
        ew = window_edges(pre)
        r = {"eid": e, "subject": subjects[e], "n_windows": int(np.isfinite(sw).sum())}
        # engagement alignment (match by session and order; >= 99% agreement required)
        side = np.asarray(pre["side"], float)
        con = np.asarray(pre["contrast"], float)
        cl = np.where(side > 0, con, np.nan)
        cr = np.where(side < 0, con, np.nan)
        rew = np.where(np.asarray(pre["feedbackType"]) > 0, 1, -1)
        g = eng_all[eng_all.eid == e].reset_index(drop=True)
        best = (0.0, None)
        if len(g) and len(g) <= len(cl):
            for off in range(0, len(cl) - len(g) + 1):
                sl = slice(off, off + len(g))
                agree = np.mean((np.isclose(g.contrastLeft, cl[sl], equal_nan=True))
                                & (np.isclose(g.contrastRight, cr[sl], equal_nan=True))
                                & (g.rewarded.to_numpy() == rew[sl]))
                if agree > best[0]:
                    best = (float(agree), off)
        r["engage_rows"], r["engage_agreement"] = int(len(g)), best[0]
        stim = np.asarray(pre["stimOn_times"], float)
        if best[1] is not None and best[0] >= 0.99:
            pst = np.full(len(cl), np.nan)
            pst[best[1]:best[1] + len(g)] = g.p_state1.to_numpy()
            E = event_windows(stim, pst, ew)
        else:
            E = np.full(len(sw), np.nan)
        fb = np.asarray(pre["feedback_times"], float)
        rewarded = (np.asarray(pre["feedbackType"]) > 0) & np.isfinite(fb)
        R = np.array([np.sum(fb[rewarded] <= t_end) for t_end in ew[1:]], float)
        S_[e] = {"slow": sw, "load": load, "E": E, "R": R, "res_s": residualize_quadratic(sw),
                 "res_E": residualize_quadratic(E), "res_R": residualize_quadratic(R)}
        r["engage_resid_sd"] = float(np.nanstd(S_[e]["res_E"])) if np.isfinite(E).any() else np.nan
        rows[e] = r

    # ---------------- part 1: engagement and satiety beyond the quadratic trend
    for sig in ("E", "R"):
        usable = [e for e in eids if np.isfinite(S_[e][f"res_{sig}"]).sum() >= 10]
        for e in eids:
            if e not in usable:
                rows[e].update({f"{sig}_r": np.nan, f"{sig}_signed_r": np.nan, f"{sig}_corrected": np.nan})
                continue
            real = corr_aligned(S_[e]["res_s"], S_[e][f"res_{sig}"])
            cross = np.array([corr_aligned(S_[e]["res_s"], S_[j][f"res_{sig}"]) for j in usable if j != e])
            cross = cross[np.isfinite(cross)]
            rows[e].update({f"{sig}_r": real,
                            f"{sig}_signed_r": corr_aligned(S_[e]["res_s"], S_[e][f"res_{sig}"], absolute=False),
                            f"{sig}_corrected": real - np.median(cross) if len(cross) else np.nan})

    # ---------------- part 2a: amplitude trend vs slow-mode loading
    for e in eids:
        u = pd.read_csv(od / f"units_{e}.csv")
        rho = spearman(S_[e]["load"], u["amp_trend"].to_numpy())
        rows[e].update({"amp_loading_rho": rho, "amp_loading_z": np.arctanh(np.clip(rho, -0.999, 0.999))
                        if np.isfinite(rho) else np.nan,
                        "frac_units_amp_unstable": float(np.mean(~u["amp_stable"]))})

    # ---------------- part 3: multi-unit slow mode and depth-gradient signature
    mua_sub = Path(args.mua_results) / "subspaces"
    for e in eids:
        f = mua_sub / f"{e}_d{d}.npz"
        mi = Path(args.mua_data) / "interim" / f"{e}.npz"
        if not (f.exists() and mi.exists()):
            rows[e].update({"mua_match": np.nan, "mua_grad_rho": np.nan, "mua_grad_p": np.nan})
            continue
        mpre = load_npz(mi)
        mfits = load_npz(f)
        msw, mload, _ = slow_mode(mpre, mfits, session_S(mpre), long_)
        rows[e]["mua_match"] = corr_aligned(msw, S_[e]["slow"])
        rate = mpre["counts"].mean(0)
        depth = np.asarray(mpre["mua_ch_depth"], float)
        probe = np.asarray(mpre["mua_ch_probe"])
        grad = np.full(len(rate), np.nan)
        for k in np.unique(probe):
            m = probe == k
            if m.sum() >= 3:
                o = np.argsort(depth[m])
                gk = np.gradient(rate[m][o], depth[m][o])
                tmp = np.empty(m.sum())
                tmp[o] = gk
                grad[m] = tmp
        rho = spearman(mload, grad)
        ok = np.isfinite(grad)
        null = np.array([spearman(rng.permutation(mload[ok]), grad[ok]) for _ in range(N_SHUFFLE)])
        rows[e].update({"mua_grad_rho": rho,
                        "mua_grad_p": float((1 + np.sum(np.abs(null) >= abs(rho))) / (1 + N_SHUFFLE))
                        if np.isfinite(rho) else np.nan})

    df = pd.DataFrame(list(rows.values()))
    summ = {
        "part1_engagement": animal_test(df, "E_corrected", subjects),
        "part1_satiety": animal_test(df, "R_corrected", subjects),
        "part1_engagement_sign": animal_test(df, "E_signed_r", subjects, greater=False),
        "part1_satiety_sign": animal_test(df, "R_signed_r", subjects, greater=False),
        "part1_engagement_fluctuating_subset": animal_test(df[df.engage_resid_sd >= 0.1], "E_corrected", subjects),
        "engagement_sessions_aligned": int(np.sum(df.engage_agreement >= 0.99)),
        "part2a_amp_vs_loading": animal_test(df, "amp_loading_z", subjects),
        "part2b_ampstable": reading_test1(cfg["paths"]["results"], args.amp_results, d, long_),
        "part3a_mua": reading_test1(cfg["paths"]["results"], args.mua_results, d, long_),
        "part3a_mua_match_median": float(np.nanmedian(df.mua_match)),
        "part3b_depth_gradient": {"mean_abs_rho": float(np.nanmean(np.abs(df.mua_grad_rho))),
                                  "fisher_p": fisher_combine(df.mua_grad_p.to_numpy()),
                                  "n_sessions": int(df.mua_grad_p.notna().sum())},
    }
    mua = summ["part3a_mua"]
    mua_r2 = mua.get("elapsed_r2", np.nan) if mua.get("available") else np.nan
    e0 = mua.get("elapsed_r2_original", np.nan)
    reproduces = mua.get("available") and mua_r2 >= 0.75 * e0 and summ["part3a_mua_match_median"] >= 0.7
    grad_sig = summ["part3b_depth_gradient"]["fisher_p"] < 0.05
    amp_sig = (summ["part2a_amp_vs_loading"]["p"] or 1) < 0.05
    amp_read = summ["part2b_ampstable"].get("reading")
    state_sig = min(summ["part1_engagement"]["p"] or 1, summ["part1_satiety"]["p"] or 1) < 0.05
    if (mua.get("available") and mua_r2 < 0.5 * e0) or (amp_read != "survives" and amp_sig):
        overall = "sorting artifact"
    elif reproduces and grad_sig:
        overall = "probe motion"
    elif reproduces and not grad_sig and not amp_sig and amp_read == "survives" and state_sig:
        overall = "brain state"
    else:
        overall = "mixed or undetermined"
    summ["overall_reading"] = overall

    df.to_csv(od / f"sessions_d{d}.csv", index=False)
    (od / f"summary_d{d}.json").write_text(json.dumps(summ, indent=1, default=float))
    pd.set_option("display.width", 250)
    print(df.round(3).to_string(index=False))
    print(json.dumps(summ, indent=1, default=float))
    log_run(cfg, "14_pilot_A13", f"A13 pilot d={d}: overall={overall}")


if __name__ == "__main__":
    main()
