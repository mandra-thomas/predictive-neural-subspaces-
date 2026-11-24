"""Amendment A18 (post hoc): calibrated simulation of the block prior competing with slow drift. See AMENDMENTS.md, A18.

Stages (run in order; each reads the previous stage's output from results/a18/):
  targets    real data: calibration statistics per session (pns.sim_a18.calibration_stats, with script 05's pseudo
             draws) -> real_targets.csv, real_targets.json (also the real raw-data profile, from existing results)
  calibrate  simulated sessions on calibration seeds 900-915 (session k's task and unit rates): damped multiplicative
             fixed-point iteration of six gains onto six real targets; then the per-unit drift regime's two drift
             parameters onto the same two drift targets -> calibration.json, calibration_trace.csv
  sweep      ten cells x seeds 1000-1031 (task and rates of session (seed - 1000) mod 16), raw pipeline for every
             cell and the in-memory cosine detrend for four -> sim_seeds.csv
  summary    pre-specified readings, calibration diagnostics, profile comparison -> sim_summary.json, sim_cells.csv,
             a18_simulation.pdf

Only the targets stage reads neural data. Nothing here fits a latent state-space model.
"""
import json
import time

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from pns.config import ROOT, load_frozen, session_seed
from pns.pipeline import preprocess_session
from pns.runner import interim_path, load_npz, log_run, setup, write_json
from pns.sim_a18 import analyse_session, calibration_stats, pseudo_priors
from pns.synth import simulate_session, task_from_pre
from pns.timescales import detrend_pre

OUT = ROOT / "results" / "a18"
CAL_SEEDS = list(range(900, 916))
SWEEP_SEEDS = list(range(1000, 1032))
FIXED = dict(slow_noise=0.3, slow_noise_loading="separate", loading_scale=0.6, drift_rank=3, drift_decay=0.3,
             history_tau=1.0, history_k=10)
START = dict(prior_gain=1.0, drift_gain=1.0, drift_mid=0.5, history_gain=0.3, evoked_gain=0.5, stim_gain=1.5)
# gain -> (target statistic, exponent: how the statistic scales with the gain, AUC statistics measured as AUC - 0.5)
MAP = {"prior_gain": ("full_prior_corr", 0.5), "drift_gain": ("lowfreq_cos", 0.5), "drift_mid": ("midband", 0.5),
       "history_gain": ("full_prev_side_auc", 1.0), "evoked_gain": ("triallocked", 0.5),
       "stim_gain": ("full_cur_side_auc", 1.0)}
DAMP, MAX_ITER, STOP_TOL, ACCEPT_TOL = 0.7, 12, 0.10, 0.25
SCALES = (1 / 3, 1.0, 3.0)
DETREND_CELLS = ("nodrift", "lowrank_x1", "perunit_x1", "neg_history")
SETS = ["rrr_1", "rrr_4", "rrr_16", "rrr_60", "pca", "random"]


def extra(p):
    p.add_argument("--stage", required=True, choices=["targets", "calibrate", "sweep", "summary"])


def real_pres(cfg):
    frozen = load_frozen(cfg)
    return [(s["eid"], s["subject"]) for s in frozen["sessions"]]


def stat_value(st, key):
    v = st[key]
    return v - 0.5 if key.endswith("_auc") else v


# ----------------------------------------------------------------------------- targets (real data)
def target_row(eid, subject, cfg):
    pre = load_npz(interim_path(cfg, eid))
    sn, pn = pseudo_priors(len(pre["side"]), np.random.default_rng(session_seed(eid, cfg["seed"], "null")))
    return {"eid": eid, "subject": subject, **calibration_stats(pre, cfg, sn, pn)}


def real_profile():
    m = pd.read_csv(ROOT / "results" / "stats" / "d5" / "matrix.csv")
    prof = {}
    for var in ("prior", "elapsed_time"):
        for fs in SETS:
            r = m[(m.feature_set == fs) & (m.variable == var)].iloc[0]
            prof[f"{var}_{fs}"] = {"mean": float(r["mean"]), "ci": [float(r.ci_lo), float(r.ci_hi)]}
    p2 = pd.read_csv(ROOT / "results" / "stats" / "d5" / "primary.csv")
    r = p2[p2.test.str.startswith("P2")].iloc[0]
    prof["p2_change"] = {"mean": float(r["mean"]), "ci": [float(r.ci_lo), float(r.ci_hi)]}
    a16 = json.loads((ROOT / "results" / "a16" / "summary_d5.json").read_text())["part2_same_scale"]
    prof["prior_full"] = {"mean": float(a16["ridge_full_corr"]["mouse_mean"]), "ci": [np.nan, np.nan]}
    return prof


def stage_targets(cfg, n_jobs):
    rows = Parallel(n_jobs=n_jobs)(delayed(target_row)(e, s, cfg) for e, s in real_pres(cfg))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "real_targets.csv", index=False)
    stats = [c for c in df.columns if c not in ("eid", "subject")]
    summ = {"n_sessions": len(df), "session_median": {c: float(df[c].median()) for c in stats},
            "session_iqr": {c: [float(df[c].quantile(0.25)), float(df[c].quantile(0.75))] for c in stats},
            "mouse_mean": {c: float(df.groupby("subject")[c].mean().mean()) for c in stats},
            "real_profile": real_profile()}
    write_json(OUT / "real_targets.json", summ)
    print(json.dumps(summ["session_median"], indent=1))
    log_run(cfg, "26_sim_A18 targets", f"A18 real calibration targets: {len(df)} sessions")


# ----------------------------------------------------------------------------- simulation helpers
_TASKS = {}


def task_of(k, cfg):
    if k not in _TASKS:
        eid = real_pres(cfg)[k][0]
        _TASKS[k] = (eid, *task_from_pre(load_npz(interim_path(cfg, eid))))
    return _TASKS[k]


def simulate(seed, k, params, mode, cfg):
    eid, task, rates = task_of(k, cfg)
    sim = simulate_session(seed=seed, task=task, unit_rates_hz=rates, drift_mode=mode, **FIXED, **params)
    pre = preprocess_session(sim["spike_times"], sim["spike_clusters"], sim["n_units"], sim["trials"], sim["mask"],
                             sim["wheel_t"], sim["wheel_v"], cfg)
    sn, pn = pseudo_priors(len(pre["side"]), np.random.default_rng([seed, 99]))
    return eid, sim, pre, sn, pn


def cal_job(seed, params, mode, cfg):
    _, _, pre, sn, pn = simulate(seed, seed - CAL_SEEDS[0], params, mode, cfg)
    return calibration_stats(pre, cfg, sn, pn)


def evaluate(params, mode, cfg, n_jobs):
    rows = Parallel(n_jobs=n_jobs)(delayed(cal_job)(s, params, mode, cfg) for s in CAL_SEEDS)
    return {k: float(np.median([stat_value(r, k) for r in rows])) for k in rows[0] if k not in ("n_units", "T")}


def iterate(params, keys, target, mode, cfg, n_jobs, trace, label):
    params = dict(params)
    for it in range(MAX_ITER + 1):
        cur = evaluate(params, mode, cfg, n_jobs)
        ratios = {k: cur[MAP[k][0]] / target[MAP[k][0]] for k in keys}
        trace.append({"stage": label, "iter": it, **params, **{f"cur_{k}": v for k, v in cur.items()},
                      **{f"ratio_{k}": v for k, v in ratios.items()}})
        print(label, it, {k: round(v, 3) for k, v in ratios.items()}, flush=True)
        if all(abs(r - 1) <= STOP_TOL for r in ratios.values()) or it == MAX_ITER:
            return params, cur, ratios
        for k in keys:
            stat, expo = MAP[k]
            c, t = cur[stat], target[stat]
            f = 2.0 if c <= 0 else (t / c) ** (expo * DAMP)
            params[k] = float(params[k] * np.clip(f, 0.5, 2.0))


def stage_calibrate(cfg, n_jobs):
    real = json.loads((OUT / "real_targets.json").read_text())["session_median"]
    target = {k: (v - 0.5 if k.endswith("_auc") else v) for k, v in real.items()}
    trace = []
    lr, cur_lr, rat_lr = iterate(START, list(MAP), target, "lowrank", cfg, n_jobs, trace, "lowrank")
    pu_keys = ["drift_gain", "drift_mid"]
    pu, cur_pu, rat_pu = iterate(lr, pu_keys, target, "per_unit", cfg, n_jobs, trace, "per_unit")
    pd.DataFrame(trace).to_csv(OUT / "calibration_trace.csv", index=False)
    out = {"lowrank": {"params": lr, "achieved": cur_lr, "ratio": rat_lr,
                       "accepted": {k: bool(abs(r - 1) <= ACCEPT_TOL) for k, r in rat_lr.items()}},
           "per_unit": {"params": pu, "achieved": cur_pu, "ratio": rat_pu,
                        "accepted": {k: bool(abs(r - 1) <= ACCEPT_TOL) for k, r in rat_pu.items()}},
           "target": target, "fixed": FIXED, "seeds": CAL_SEEDS, "note": "AUC statistics are AUC - 0.5"}
    write_json(OUT / "calibration.json", out)
    log_run(cfg, "26_sim_A18 calibrate", f"A18 calibration: lowrank accepted {out['lowrank']['accepted']}; "
                                         f"per_unit accepted {out['per_unit']['accepted']}")


# ----------------------------------------------------------------------------- sweep
def cells(cal):
    lr, pu = cal["lowrank"]["params"], cal["per_unit"]["params"]
    c = {"favourable": ("lowrank", {**lr, "drift_gain": 0.0, "prior_gain": 3 * lr["prior_gain"]}),
         "nodrift": ("lowrank", {**lr, "drift_gain": 0.0})}
    for s, tag in zip(SCALES, ("x0.33", "x1", "x3")):
        c[f"lowrank_{tag}"] = ("lowrank", {**lr, "drift_gain": s * lr["drift_gain"]})
        c[f"perunit_{tag}"] = ("per_unit", {**pu, "drift_gain": s * pu["drift_gain"]})
    c["neg_history"] = ("lowrank", {**lr, "prior_gain": 0.0})
    c["neg_pure"] = ("lowrank", {**lr, "prior_gain": 0.0, "history_gain": 0.0})
    return c


def sweep_job(cell, mode, params, seed, cfg):
    t0 = time.time()
    eid, sim, pre, sn, pn = simulate(seed, (seed - SWEEP_SEEDS[0]) % 16, params, mode, cfg)
    base = {"cell": cell, "seed": seed, "task_eid": eid}
    rows = [{**base, "pipeline": "raw", **calibration_stats(pre, cfg, sn, pn),
             **analyse_session(pre, cfg, sn, pn, np.random.default_rng([seed, 98]), sim["truth"])}]
    if cell in DETREND_CELLS:
        pc = detrend_pre(pre, cfg, "cos")
        rows.append({**base, "pipeline": "cos", **analyse_session(pc, cfg, sn, pn, np.random.default_rng([seed, 98]),
                                                                  sim["truth"])})
    for r in rows:
        r["seconds"] = time.time() - t0
    return rows


def stage_sweep(cfg, n_jobs):
    cal = json.loads((OUT / "calibration.json").read_text())
    jobs = [(c, m, p, s) for c, (m, p) in cells(cal).items() for s in SWEEP_SEEDS]
    res = Parallel(n_jobs=n_jobs, verbose=5)(delayed(sweep_job)(c, m, p, s, cfg) for c, m, p, s in jobs)
    df = pd.DataFrame([r for rows in res for r in rows])
    df.to_csv(OUT / "sim_seeds.csv", index=False)
    log_run(cfg, "26_sim_A18 sweep", f"A18 sweep: {df.cell.nunique()} cells x {len(SWEEP_SEEDS)} seeds, "
                                     f"{len(df)} rows")


# ----------------------------------------------------------------------------- summary and readings
def boot_ratio(num, den, rng, n=2000):
    idx = rng.integers(0, len(num), (n, len(num)))
    b = num[idx].mean(1) / den[idx].mean(1)
    return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def boot_mean(x, rng, n=2000):
    b = x[rng.integers(0, len(x), (n, len(x)))].mean(1)
    return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def n_pos_needed(n):
    """Smallest k with one-sided binomial P(X >= k | n, 0.5) < 0.05."""
    from scipy.stats import binom
    return int(next(k for k in range(n + 1) if binom.sf(k - 1, n, 0.5) < 0.05))


def summarise(df, real):
    rng = np.random.default_rng(0)
    out, rows = {}, []
    raw = df[df.pipeline == "raw"]
    for (cell, pipe), g in df.groupby(["cell", "pipeline"]):
        g = g.sort_values("seed")
        full = g["prior_full"].to_numpy()
        row = {"cell": cell, "pipeline": pipe, "n": len(g),
               "prior_full_mean": float(full.mean()), "prior_full_ci": boot_mean(full, rng),
               "prior_full_npos": int((full > 0).sum()),
               "priorhist_full_mean": float(g["priorhist_full"].mean()),
               "priorhist_full_npos": int((g["priorhist_full"] > 0).sum()),
               "p2_change_median": float(g["p2_change"].median()), "p2_change_mean": float(g["p2_change"].mean()),
               "p2_change_ci": boot_mean(g["p2_change"].to_numpy(), rng)}
        for fs in SETS:
            x = g[f"prior_{fs}"].to_numpy()
            row[f"prior_{fs}_mean"] = float(x.mean())
            row[f"prior_{fs}_ci"] = boot_mean(x, rng)
            row[f"prior_{fs}_npos"] = int((x > 0).sum())
            row[f"capture_{fs}"] = float(x.mean() / full.mean()) if full.mean() > 0 else np.nan
            row[f"capture_{fs}_ci"] = boot_ratio(x, full, rng) if full.mean() > 0 else [np.nan, np.nan]
            row[f"priorhist_{fs}_mean"] = float(g[f"priorhist_{fs}"].mean())
            row[f"elapsed_{fs}_mean"] = float(g[f"elapsed_{fs}"].mean())
            row[f"cur_side_{fs}_mean"] = float(g[f"cur_side_{fs}"].mean())
            if f"capture_in_{fs}" in g:
                row[f"capture_in_{fs}_mean"] = float(g[f"capture_in_{fs}"].mean())
        for lag in (1, 60):
            row[f"capture_out_rrr_{lag}_mean"] = float(g[f"capture_out_rrr_{lag}"].mean())
        row["chance_capture_mean"] = float(g["chance_capture"].mean())
        if pipe == "raw":
            for k in ("lowfreq_cos", "midband", "triallocked", "full_prev_side_auc", "full_cur_side_auc",
                      "pc1_frac", "pc5_frac", "prior_trial_share_corr", "full_prior_corr"):
                row[f"diag_{k}_median"] = float(g[k].median())
        rows.append(row)
    cdf = pd.DataFrame(rows)
    R = {(r.cell, r.pipeline): r for r in cdf.itertuples()}
    need = n_pos_needed(len(SWEEP_SEEDS))
    out["n_positive_needed"] = need

    # Gate G1: positive control
    fav = R[("favourable", "raw")]
    g1 = fav.prior_full_npos >= need and fav.prior_rrr_60_npos >= need
    out["G1_positive_control"] = {"passed": bool(g1), "full_npos": fav.prior_full_npos,
                                  "rrr_60_npos": fav.prior_rrr_60_npos}
    # Reading A: is drift needed / sufficient? (primary: low-rank; secondary: per-unit)
    k0 = R[("nodrift", "raw")].capture_rrr_60
    readA = {}
    for regime in ("lowrank", "perunit"):
        r1 = R[(f"{regime}_x1", "raw")]
        if not g1:
            rd = "uninformative (positive control failed)"
        elif not np.isfinite(k0) or k0 < 0.25:
            rd = "weak prior sufficient (not captured at 30 s even without drift)"
        elif r1.capture_rrr_60 < 0.5 * k0 and r1.p2_change_median <= 0:
            rd = "drift sufficient"
        elif r1.capture_rrr_60 >= 0.5 * k0 and r1.p2_change_median > 0:
            rd = "drift not sufficient"
        else:
            rd = "intermediate"
        readA[regime] = {"reading": rd, "capture_rrr_60_nodrift": k0, "capture_rrr_60_real": r1.capture_rrr_60,
                         "p2_change_median_real": r1.p2_change_median}
    out["A_drift"] = readA
    # Reading B: history leakage and the history-controlled score
    nh, npure, nd = R[("neg_history", "raw")], R[("neg_pure", "raw")], R[("nodrift", "raw")]
    out["B_history"] = {
        "null_calibrated": bool(npure.prior_full_npos < need),
        "leakage_present": bool(nh.prior_full_npos >= need),
        "leakage_full_mean": nh.prior_full_mean,
        "leakage_fraction_of_real_target": float(nh.prior_full_mean / real["session_median"]["full_prior_corr"]),
        "hist_control_valid": bool(nh.priorhist_full_npos < need and nd.priorhist_full_npos >= need),
        "neg_history_hist_npos": nh.priorhist_full_npos, "nodrift_hist_npos": nd.priorhist_full_npos,
        "neg_pure_full_npos": npure.prior_full_npos, "neg_history_full_npos": nh.prior_full_npos}
    # Reading C: profile comparison (descriptive)
    prof = real["real_profile"]
    feats = [f"prior_{fs}" for fs in ("rrr_1", "rrr_60", "pca", "random")] + \
            [f"elapsed_time_{fs}" for fs in ("rrr_60", "pca", "random")] + ["p2_change"]
    readC = {}
    for regime in ("lowrank_x1", "perunit_x1"):
        r1 = R[(regime, "raw")]._asdict()
        within = {}
        for f in feats:
            sim_key = f.replace("elapsed_time_", "elapsed_") + "_mean" if f != "p2_change" else "p2_change_mean"
            lo, hi = prof[f]["ci"]
            within[f] = {"sim": r1[sim_key], "real": prof[f]["mean"], "real_ci": [lo, hi],
                         "within": bool(lo <= r1[sim_key] <= hi)}
        readC[regime] = {"n_within": int(sum(v["within"] for v in within.values())), "n_features": len(feats),
                         "features": within}
    out["C_profile"] = readC
    # Recommendation rule for the latent model (A18 part B)
    lr1 = R[("lowrank_x1", "raw")]
    out["recommend_lds"] = {
        "positive_control": bool(g1), "hist_control_valid": out["B_history"]["hist_control_valid"],
        "prior_reliable_at_real_drift": bool(lr1.prior_full_npos >= need),
        "proceed": bool(g1 and out["B_history"]["hist_control_valid"] and lr1.prior_full_npos >= need)}
    return out, cdf


def figure(cdf, real, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from pns.plotting import INK_2, SERIES
    R = {(r.cell, r.pipeline): r for r in cdf.itertuples()}
    fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.2), constrained_layout=True)
    xs = [0, 1 / 3, 1, 3]
    for i, fs in enumerate(("rrr_1", "rrr_60", "pca", "random")):
        for regime, ls in (("lowrank", "-"), ("perunit", "--")):
            cs = ["nodrift"] + [f"{regime}_{t}" for t in ("x0.33", "x1", "x3")]
            y = [getattr(R[(c, "raw")], f"capture_{fs}") for c in cs]
            ax[0].plot(range(4), y, ls, marker="o", ms=3, color=SERIES[i], label=fs if regime == "lowrank" else None)
    ax[0].axhline(0, color=INK_2, lw=0.6)
    ax[0].set_xticks(range(4), ["0", "1/3", "1", "3"])
    ax[0].set_xlabel("drift scale (x calibrated; dashed = per-unit)")
    ax[0].set_ylabel("prior captured / full population")
    ax[0].set_title("a  capture vs drift", loc="left", fontsize=9)
    ax[0].legend(fontsize=7, frameon=False)
    prof = real["real_profile"]
    sets = ["rrr_1", "rrr_4", "rrr_16", "rrr_60", "pca", "random"]
    for j, (var, title) in enumerate((("prior", "b  corrected prior R²"), ("elapsed", "c  elapsed-time R²"))):
        a = ax[j + 1]
        rk = "prior" if var == "prior" else "elapsed_time"
        rv = [prof[f"{rk}_{fs}"]["mean"] for fs in sets]
        ci = np.array([prof[f"{rk}_{fs}"]["ci"] for fs in sets])
        a.errorbar(range(6), rv, yerr=[np.array(rv) - ci[:, 0], ci[:, 1] - np.array(rv)], fmt="ko", ms=4,
                   label="real (mouse mean, 95% CI)")
        for i, (cell, lab) in enumerate((("lowrank_x1", "sim, low-rank drift"), ("perunit_x1", "sim, per-unit drift"),
                                         ("nodrift", "sim, no drift"))):
            v = [getattr(R[(cell, "raw")], f"{var}_{fs}_mean") for fs in sets]
            a.plot(np.arange(6) + 0.15 * (i + 1), v, "s", ms=3.5, color=SERIES[i], label=lab)
        a.set_xticks(range(6), ["0.5 s", "2 s", "8 s", "30 s", "PCA", "rand"], fontsize=7)
        a.axhline(0, color=INK_2, lw=0.6)
        a.set_title(title, loc="left", fontsize=9)
    ax[1].legend(fontsize=6.5, frameon=False)
    fig.savefig(path)


def stage_summary(cfg):
    real = json.loads((OUT / "real_targets.json").read_text())
    df = pd.read_csv(OUT / "sim_seeds.csv")
    out, cdf = summarise(df, real)
    cal = json.loads((OUT / "calibration.json").read_text())
    out["calibration"] = {m: {"params": cal[m]["params"], "ratio": cal[m]["ratio"], "accepted": cal[m]["accepted"]}
                          for m in ("lowrank", "per_unit")}
    cdf.to_csv(OUT / "sim_cells.csv", index=False)
    write_json(OUT / "sim_summary.json", out)
    figure(cdf, real, OUT / "a18_simulation.pdf")
    print(json.dumps({k: out[k] for k in ("G1_positive_control", "A_drift", "B_history", "recommend_lds")},
                     indent=1, default=str))
    log_run(cfg, "26_sim_A18 summary", f"A18 readings: G1 {out['G1_positive_control']['passed']}; "
                                       f"A lowrank '{out['A_drift']['lowrank']['reading']}', per-unit "
                                       f"'{out['A_drift']['perunit']['reading']}'; B leakage "
                                       f"{out['B_history']['leakage_present']}, hist control valid "
                                       f"{out['B_history']['hist_control_valid']}; proceed to LDS "
                                       f"{out['recommend_lds']['proceed']}")


def main():
    args, cfg, n_jobs = setup(__doc__, extra)
    OUT.mkdir(parents=True, exist_ok=True)
    {"targets": lambda: stage_targets(cfg, n_jobs), "calibrate": lambda: stage_calibrate(cfg, n_jobs),
     "sweep": lambda: stage_sweep(cfg, n_jobs), "summary": lambda: stage_summary(cfg)}[args.stage]()


if __name__ == "__main__":
    main()
