"""Amendment A12 pilot: is the slow mode recording drift or brain state?

Test 2 (probe motion) and test 3 (pupil): the slow mode = projection of z-scored sqrt counts onto the first basis
column of the full-session 30 s-lag readout subspace, averaged in non-overlapping 30 s windows, sign fixed to
correlate positively with elapsed time. Statistic: |Pearson r| with the state signal in the same windows.
Null: session permutation (session i's slow mode vs every other session's signal, aligned from task start).
Corrected = |r_real| - median |r_cross|; one-sided Wilcoxon across animals. Secondary: same after removing a
linear time trend from both series.

Test 1 (stable units) is summarised from the stable-units rerun of scripts 04-06 (--stable-results).
Writes results/pilot/{sessions,summary}.{csv,json}.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from pns.config import load_frozen
from pns.pipeline import session_S
from pns.runner import interim_path, load_npz, log_run, out_dir, setup
from pns.stats import animal_mean, wilcoxon_greater

WIN_BINS = 60            # 30 s windows of 0.5 s bins


def extra(p):
    p.add_argument("--d", type=int, default=None)
    p.add_argument("--stable-results", default="results_stable")


def window_means(t_bins, x_bins, ok_bins, edges_w):
    """Mean of x over bins in each window; NaN if fewer than half the window's bins are usable."""
    idx = np.searchsorted(edges_w, t_bins, side="right") - 1
    n_w = len(edges_w) - 1
    out = np.full(n_w, np.nan)
    for w in range(n_w):
        sel = (idx == w)
        good = sel & ok_bins
        if sel.sum() and good.sum() >= 0.5 * WIN_BINS:
            out[w] = x_bins[good].mean()
    return out


def signal_windows(t_sig, x_sig, edges_w, min_frac=0.5):
    """Mean of an irregularly sampled signal per window; NaN if < min_frac of samples finite or out of range."""
    out = np.full(len(edges_w) - 1, np.nan)
    if t_sig is None or len(t_sig) == 0:
        return out
    idx = np.searchsorted(edges_w, t_sig, side="right") - 1
    for w in range(len(out)):
        sel = idx == w
        if sel.sum() == 0:
            continue
        v = x_sig[sel]
        fin = np.isfinite(v)
        if fin.mean() >= min_frac:
            out[w] = v[fin].mean()
    return out


def _detrend(y, t):
    ok = np.isfinite(y)
    if ok.sum() < 3:
        return y
    b = np.polyfit(t[ok], y[ok], 1)
    return y - np.polyval(b, t)


def abs_r(a, b, detrend=False):
    n = min(len(a), len(b))
    a, b = a[:n].copy(), b[:n].copy()
    t = np.arange(n, dtype=float)
    if detrend:
        a, b = _detrend(a, t), _detrend(b, t)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 10 or np.std(a[ok]) == 0 or np.std(b[ok]) == 0:
        return np.nan
    return float(abs(np.corrcoef(a[ok], b[ok])[0, 1]))


def main():
    args, cfg, _ = setup(__doc__, extra)
    d = args.d or cfg["model"]["d"]
    long_ = max(cfg["lags_bins"])
    frozen = load_frozen(cfg)
    subjects = {s["eid"]: s["subject"] for s in frozen["sessions"]}
    state_dir = interim_path(cfg, "x").parent / "state"
    sess = {}
    for e in subjects:
        pre = load_npz(interim_path(cfg, e))
        fits = load_npz(out_dir(cfg, "subspaces") / f"{e}_d{d}.npz")
        st = load_npz(state_dir / f"{e}.npz")
        S = session_S(pre)
        valid = np.asarray(pre["valid"], bool)
        Z = (S - fits["z_mu"]) / fits["z_sd"]
        v = fits[f"Vin_full_{long_}"][:, 0]
        s = Z @ (v / np.linalg.norm(v))
        edges = pre["edges"]
        tc = 0.5 * (edges[:-1] + edges[1:])
        t0 = tc[valid][0]
        edges_w = t0 + np.arange(0, (tc[valid][-1] - t0) + 30.0 + 1e-9, 30.0)
        sw = window_means(tc, s, valid, edges_w)
        tw = np.arange(len(sw), dtype=float)
        ok = np.isfinite(sw)
        if np.corrcoef(sw[ok], tw[ok])[0, 1] < 0:
            sw = -sw
        mot = signal_windows(st["motion_t"], st["motion_um"], edges_w)
        pup = signal_windows(st.get("pupil_t"), st.get("pupil"), edges_w) if "pupil" in st else np.full(len(sw), np.nan)
        # pupil exclusion: > 50% missing samples within the task epoch
        if "pupil" in st:
            in_ep = (st["pupil_t"] >= edges_w[0]) & (st["pupil_t"] <= edges_w[-1])
            pup_missing = float(1 - np.isfinite(st["pupil"][in_ep]).mean()) if in_ep.any() else 1.0
        else:
            pup_missing = 1.0
        sess[e] = {"slow": sw, "motion": mot, "pupil": pup, "pupil_missing": pup_missing,
                   "elapsed_r": float(np.corrcoef(sw[ok], tw[ok])[0, 1] * np.sign(np.corrcoef(sw[ok], tw[ok])[0, 1])),
                   "motion_range_um": float(np.nanmax(mot) - np.nanmin(mot)) if np.isfinite(mot).any() else np.nan}

    rows = []
    eids = list(sess)
    for e in eids:
        r = {"eid": e, "subject": subjects[e], "n_windows": int(np.isfinite(sess[e]["slow"]).sum()),
             "slow_vs_time_r": sess[e]["elapsed_r"], "motion_range_um": sess[e]["motion_range_um"],
             "pupil_missing": sess[e]["pupil_missing"]}
        for sig in ("motion", "pupil"):
            usable = [j for j in eids if not (sig == "pupil" and sess[j]["pupil_missing"] > 0.5)]
            if e not in usable:
                for dt in ("", "_detrended"):
                    r.update({f"{sig}{dt}_r": np.nan, f"{sig}{dt}_corrected": np.nan, f"{sig}{dt}_p": np.nan})
                continue
            for dt, flag in (("", False), ("_detrended", True)):
                real = abs_r(sess[e]["slow"], sess[e][sig], flag)
                cross = np.array([abs_r(sess[e]["slow"], sess[j][sig], flag) for j in usable if j != e])
                cross = cross[np.isfinite(cross)]
                r[f"{sig}{dt}_r"] = real
                r[f"{sig}{dt}_corrected"] = real - np.median(cross) if len(cross) else np.nan
                r[f"{sig}{dt}_p"] = float((1 + np.sum(cross >= real)) / (1 + len(cross))) if len(cross) else np.nan
        rows.append(r)
    df = pd.DataFrame(rows)

    summary = {}
    for col in ("motion_corrected", "motion_detrended_corrected", "pupil_corrected", "pupil_detrended_corrected"):
        sub = df.dropna(subset=[col])
        a = animal_mean(sub, col, [])[col].to_numpy()
        t = wilcoxon_greater(a)
        summary[col] = {"n_animals": int(len(a)), "n_sessions": int(len(sub)), "mean": float(np.mean(a)) if len(a) else None,
                        "mean_abs_r_real": float(sub[col.replace("_corrected", "_r")].mean()) if len(sub) else None,
                        "p": t["p"]}

    # ---- test 1: stable-units rerun
    st_root = Path(args.stable_results)
    t1 = {"available": (st_root / "stats" / f"d{d}" / "matrix.csv").exists()}
    if t1["available"]:
        def elapsed(root):
            m = pd.read_csv(Path(root) / "stats" / f"d{d}" / "matrix.csv")
            return float(m[(m.feature_set == f"rrr_{long_}") & (m.variable == "elapsed_time")]["mean"].iloc[0])
        def drift(root):
            dd = pd.read_csv(Path(root) / "stats" / f"d{d}" / "drift.csv")
            return int(dd.drift_flag.sum()), int(len(dd))
        def prim(root):
            p = pd.read_csv(Path(root) / "stats" / f"d{d}" / "primary.csv")
            return dict(zip(p.test.str.split(" ").str[0], p.p_holm))
        orig_root = cfg["paths"]["results"]
        e0, e1 = elapsed(orig_root), elapsed(st_root)
        f1, n1 = drift(st_root)
        t1.update({"elapsed_r2_original": e0, "elapsed_r2_stable": e1, "drift_flags_stable": f1,
                   "n_sessions_stable": n1, "drift_flags_original": list(drift(orig_root)),
                   "primary_holm_original": prim(orig_root), "primary_holm_stable": prim(st_root)})
        if e1 < 0.5 * e0 and f1 <= 0.25 * n1:
            t1["reading"] = "turnover-driven"
        elif e1 >= 0.75 * e0:
            t1["reading"] = "survives"
        else:
            t1["reading"] = "intermediate"
    summary["test1_stable_units"] = t1
    p2, p3 = summary["motion_corrected"]["p"], summary["pupil_corrected"]["p"]
    sig2, sig3 = (p2 is not None and p2 < 0.05), (p3 is not None and p3 < 0.05)
    r1 = t1.get("reading")
    if r1 == "turnover-driven" or (sig2 and not sig3):
        overall = "drift"
    elif r1 == "survives" and sig3 and not sig2:
        overall = "brain state"
    else:
        overall = "mixed or undetermined"
    summary["overall_reading"] = overall

    od = out_dir(cfg, "pilot")
    df.to_csv(od / f"sessions_d{d}.csv", index=False)
    (od / f"summary_d{d}.json").write_text(json.dumps(summary, indent=1, default=float))
    pd.set_option("display.width", 220)
    print(df.round(3).to_string(index=False))
    print(json.dumps(summary, indent=1, default=float))
    log_run(cfg, "11_pilot_state", f"A12 pilot d={d}: motion p={p2}, pupil p={p3}, test1={r1}, overall={overall}")


if __name__ == "__main__":
    main()
