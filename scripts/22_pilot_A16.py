"""Amendment A16 (post hoc, local): parts 1-4 of the post hoc follow-ups. See AMENDMENTS.md, A16.

Part 1  reads results_detrend_{q,c}/stats/d5 (refits of 04-06 on 21_build_detrend output) and applies the reading.
Part 2  same-scale prior reference: (a) ridge/contiguous decoder on the full population with script 05's pseudo
        draws; (b) Findling decoder (Lasso, interleaved nested CV) on the 0.5 s, 30 s and PCA subspaces.
Part 3  split-half reproducibility of the leading 30 s direction: filter, loading and activation-pattern weights.
Part 4  step sessions: motion, unit concentration and amplitude at the step.
Writes results/a16/{sessions_d5.csv, steps_d5.csv, summary_d5.json}.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from pns.ampcorr import window_amplitudes
from pns.config import load_frozen, session_seed
from pns.decode import lasso_nested_r2, r2_cv
from pns.lagged import contiguous_folds, session_halves
from pns.pipeline import _trial_targets, session_S, window_S
from pns.prior import bayes_optimal_prior, pseudo_sides
from pns.runner import interim_path, load_npz, log_run, out_dir, setup
from pns.slowmode import bin_centres, slow_mode, window_edges, window_means
from pns.stats import wilcoxon_greater
from pns.transform import ZScore

N_PSEUDO = 200
STEP_FRAC = 0.30


def extra(p):
    p.add_argument("--d", type=int, default=None)
    p.add_argument("--skip-lasso", action="store_true")


def corrected(scores):
    return float(scores[0] - np.median(scores[1:]))


def part2_session(e, cfg, d, long_, short, skip_lasso):
    pre = load_npz(interim_path(cfg, e))
    fits = load_npz(out_dir(cfg, "subspaces") / f"{e}_d{d}.npz")
    zs = ZScore(fits["z_mu"], fits["z_sd"])
    win, tr, _ = _trial_targets(pre, cfg)["prior"]
    Z = zs.transform(window_S(pre, win))[tr]
    rng = np.random.default_rng(session_seed(e, cfg["seed"], "null"))          # same draws as script 05
    sides_null = np.stack([pseudo_sides(len(pre["side"]), rng)[1] for _ in range(N_PSEUDO)])
    Y = np.column_stack([pre["prior"][tr], bayes_optimal_prior(sides_null)[:, tr].T])
    folds = contiguous_folds(len(tr), cfg["cv"]["n_folds"])
    sets = {"full": np.eye(Z.shape[1]), f"rrr_{short}": fits[f"Vin_full_{short}"],
            f"rrr_{long_}": fits[f"Vin_full_{long_}"], "pca": fits["V_pca"]}
    row = {"eid": e, "n_units": int(Z.shape[1]), "n_trials": int(len(tr))}
    for name, V in sets.items():
        sc = r2_cv(Z @ V, Y, folds, cfg["decode"]["ridge_alpha"])
        row[f"ridge_{name}_raw"] = float(sc[0])
        row[f"ridge_{name}_corr"] = corrected(sc)
    if not skip_lasso:
        lrng = np.random.default_rng(session_seed(e, cfg["seed"], "a16_lasso"))
        for name in (f"rrr_{short}", f"rrr_{long_}", "pca"):
            sc = lasso_nested_r2(Z @ sets[name], Y, cfg["gate"]["n_folds"], lrng)
            row[f"lasso_{name}_raw"] = float(sc[0])
            row[f"lasso_{name}_corr"] = corrected(sc)
    return row


def cos_abs(a, b):
    return float(abs(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def part3_session(e, cfg, d, long_, rng):
    pre = load_npz(interim_path(cfg, e))
    fits = load_npz(out_dir(cfg, "subspaces") / f"{e}_d{d}.npz")
    Z = (session_S(pre) - fits["z_mu"]) / fits["z_sd"]
    valid = np.asarray(pre["valid"], bool)
    seg = session_halves(len(Z), cfg["cv"]["half_gap_bins"])
    C = [np.cov(Z[(seg == h) & valid].T) for h in (0, 1)]
    Call = np.cov(Z[valid].T)
    w = [fits[f"Vin_half{h}_{long_}"][:, 0] for h in (0, 1)]
    v = [fits[f"Vout_half{h}_{long_}"][:, 0] for h in (0, 1)]
    out = {"eid": e, "cos_filter": cos_abs(*w), "cos_loading": cos_abs(*v),
           "cos_pattern": cos_abs(C[0] @ w[0], C[1] @ w[1])}
    ev, U = np.linalg.eigh(Call)
    Lh = U * np.sqrt(np.clip(ev, 0, None))
    g = Lh @ rng.standard_normal((Call.shape[0], 2000))
    g0, g1 = g[:, :1000], g[:, 1000:]
    out["chance_dir"] = float(np.median([cos_abs(g0[:, k], g1[:, k]) for k in range(1000)]))
    out["chance_pattern"] = float(np.median([cos_abs(C[0] @ g0[:, k], C[1] @ g1[:, k]) for k in range(1000)]))
    # addendum (descriptive): capture of each half's leading direction by the other half's 5-D subspace
    Q = [np.linalg.qr(fits[f"Vin_half{h}_{long_}"])[0] for h in (0, 1)]

    def capture(x, Qo):
        x = x / np.linalg.norm(x)
        return float(np.sum((Qo.T @ x) ** 2))
    out["capture_leading"] = 0.5 * (capture(w[0], Q[1]) + capture(w[1], Q[0]))
    out["capture_chance"] = float(np.median([0.5 * (capture(g0[:, k], Q[1]) + capture(g1[:, k], Q[0]))
                                             for k in range(1000)]))
    return out


def part4_session(e, cfg, d, long_):
    pre = load_npz(interim_path(cfg, e))
    fits = load_npz(out_dir(cfg, "subspaces") / f"{e}_d{d}.npz")
    S = session_S(pre)
    sw, v, _ = slow_mode(pre, fits, S, long_)
    ew = window_edges(pre)
    ok = np.flatnonzero(np.isfinite(sw))
    rng_ = np.nanmax(sw) - np.nanmin(sw)
    jumps = np.diff(sw[ok])
    k = int(np.argmax(np.abs(jumps)))
    row = {"eid": e, "max_jump_frac": float(abs(jumps[k]) / rng_)}
    row["step_session"] = row["max_jump_frac"] >= STEP_FRAC
    if not row["step_session"]:
        return row
    w0, w1 = ok[k], ok[k + 1]
    t_step = float(ew[w1])
    row["step_min"] = (t_step - ew[0]) / 60.0
    # (i) motion
    st = np.load(Path(cfg["paths"]["data"]) / "interim" / "state" / f"{e}.npz")
    mt, mu = st["motion_t"], st["motion_um"]

    def mstat(t):
        a, b = mu[(mt >= t - 120) & (mt < t)], mu[(mt > t) & (mt <= t + 120)]
        return abs(np.median(b) - np.median(a)) if len(a) and len(b) else np.nan
    allm = np.array([mstat(t) for t in ew[1:-1]])
    sm = mstat(t_step)
    row["motion_change_um"] = float(sm)
    row["motion_pct"] = float(np.mean(allm[np.isfinite(allm)] <= sm) * 100) if np.isfinite(sm) else np.nan
    # (ii) unit concentration of the projected jump
    Z = (S - fits["z_mu"]) / fits["z_sd"]
    wm = window_means(bin_centres(pre), Z, np.asarray(pre["valid"], bool), ew)
    contrib = (wm[w1] - wm[w0]) * v
    total = float(np.nansum(contrib))
    top = np.argsort(contrib)[::-1][:3]
    row["top3_share"] = float(np.sum(contrib[top]) / total) if total else np.nan
    row["top3_units"] = ",".join(map(str, top))
    # (iii) amplitude change of the top units at the step vs their own window-to-window changes
    a = load_npz(Path(cfg["paths"]["data"]) / "interim" / "a13" / f"{e}.npz")
    med = window_amplitudes(a["unit_t"], a["unit_idx"].astype(np.int64), a["unit_amp"], Z.shape[1], ew)
    pcts = []
    for u in top:
        dm = np.abs(np.diff(med[:, u]))
        x = abs(med[w1, u] - med[w0, u])
        if np.isfinite(x) and np.isfinite(dm).sum() > 10:
            pcts.append(float(np.mean(dm[np.isfinite(dm)] <= x) * 100))
    row["amp_pct_max_top3"] = max(pcts) if pcts else np.nan
    row["reading"] = ("artifact-consistent" if (row["motion_pct"] >= 95 or (pcts and max(pcts) >= 95))
                      else "no recording signature")
    return row


def detrend_summary(cfg, d, long_, short, kind):
    root = Path(f"results_detrend_{kind}") / "stats" / f"d{d}"
    if not (root / "primary.csv").exists():
        return {"available": False}
    pr = pd.read_csv(root / "primary.csv")
    m = pd.read_csv(root / "matrix.csv")
    ph = dict(zip(pr.test.str.split(" ").str[0], pr.p_holm))
    cell = lambda fs, var: m[(m.feature_set == fs) & (m.variable == var)].iloc[0]
    prior = {fs: {"mean": float(cell(fs, "prior")["mean"]), "ci": [float(cell(fs, "prior")["ci_lo"]),
                                                                  float(cell(fs, "prior")["ci_hi"])]}
             for fs in [f"rrr_{l}" for l in cfg["lags_bins"]] + ["pca", "random"]}
    el = {fs: float(cell(fs, "elapsed_time")["mean"]) for fs in (f"rrr_{long_}", f"rrr_{short}", "pca", "random")}
    p2 = pr[pr.test.str.startswith("P2")].iloc[0]
    lp = prior[f"rrr_{long_}"]
    masked = ph["P2"] < 0.05 and lp["ci"][0] > 0
    return {"available": True, "primary_holm": ph, "P2_mean_change": float(p2["mean"]),
            "P2_ci": [float(p2["ci_lo"]), float(p2["ci_hi"])], "prior_by_set": prior, "elapsed_r2": el,
            "reading": "masked" if masked else "not masked by a smooth trend"}


def animal_mean(df, col, subjects):
    sub = df.dropna(subset=[col])
    return sub.assign(subject=sub.eid.map(subjects)).groupby("subject")[col].mean()


def main():
    args, cfg, n_jobs = setup(__doc__, extra)
    d = args.d or cfg["model"]["d"]
    lags = list(cfg["lags_bins"])
    long_, short = max(lags), min(lags)
    frozen = load_frozen(cfg)
    subjects = {s["eid"]: s["subject"] for s in frozen["sessions"]}
    eids = list(subjects)
    od = out_dir(cfg, "a16")

    p2 = Parallel(n_jobs=n_jobs)(delayed(part2_session)(e, cfg, d, long_, short, args.skip_lasso) for e in eids)
    rng = np.random.default_rng(cfg["seed"] + 16)
    p3 = [part3_session(e, cfg, d, long_, rng) for e in eids]
    p4 = [part4_session(e, cfg, d, long_) for e in eids]
    df = pd.DataFrame(p2).merge(pd.DataFrame(p3), on="eid")
    df["subject"] = df.eid.map(subjects)
    steps = pd.DataFrame(p4)
    steps["subject"] = steps.eid.map(subjects)

    summ = {"part1_quadratic": detrend_summary(cfg, d, long_, short, "q"),
            "part1_cosine": detrend_summary(cfg, d, long_, short, "c")}
    p2s = {}
    for c in [c for c in df.columns if c.endswith("_corr") or c.endswith("_raw")]:
        am = animal_mean(df, c, subjects)
        p2s[c] = {"mouse_mean": float(am.mean()), "session_median": float(df[c].median())}
    full = animal_mean(df, "ridge_full_corr", subjects)
    for name in (f"rrr_{short}", f"rrr_{long_}", "pca"):
        p2s[f"ratio_{name}_to_full_mouse_means"] = float(animal_mean(df, f"ridge_{name}_corr", subjects).mean()
                                                         / full.mean()) if full.mean() else None
    summ["part2_same_scale"] = p2s
    p3s = {}
    for rep, ch in (("filter", "chance_dir"), ("loading", "chance_dir"), ("pattern", "chance_pattern")):
        diff = animal_mean(df.assign(x=df[f"cos_{rep}"] - df[ch]), "x", subjects)
        p3s[rep] = {"mouse_mean_cos": float(animal_mean(df, f"cos_{rep}", subjects).mean()),
                    "mouse_mean_chance": float(animal_mean(df, ch, subjects).mean()),
                    "p_above_chance": wilcoxon_greater(diff.to_numpy())["p"]}
    cap = animal_mean(df.assign(x=df.capture_leading - df.capture_chance), "x", subjects)
    p3s["addendum_capture"] = {"mouse_mean": float(animal_mean(df, "capture_leading", subjects).mean()),
                               "mouse_mean_chance": float(animal_mean(df, "capture_chance", subjects).mean()),
                               "p_above_chance": wilcoxon_greater(cap.to_numpy())["p"]}
    summ["part3_reproducibility"] = p3s
    summ["part4_steps"] = steps[steps.step_session].drop(columns=["step_session"]).to_dict(orient="records")
    summ["part4_n_step_sessions"] = int(steps.step_session.sum())

    df.to_csv(od / f"sessions_d{d}.csv", index=False)
    steps.to_csv(od / f"steps_d{d}.csv", index=False)
    (od / f"summary_d{d}.json").write_text(json.dumps(summ, indent=1, default=float))
    pd.set_option("display.width", 250)
    print(json.dumps(summ, indent=1, default=float))
    log_run(cfg, "22_pilot_A16", f"A16 d={d}: detrend q={summ['part1_quadratic'].get('reading')}, "
            f"c={summ['part1_cosine'].get('reading')}; step sessions={summ['part4_n_step_sessions']}")


if __name__ == "__main__":
    main()
