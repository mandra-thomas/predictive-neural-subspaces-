"""Amendment A19 (post hoc): sensitivity of reported comparisons to session 4d8c7767, and committed sources for the
prior-history statistics. See AMENDMENTS.md, A19.

Stages
  sensitivity : reads committed result files only (no neural data, no refits). S1 registered P2 (must reproduce
                results/stats/d5/primary.csv), S2 A16 same-scale reference and ratios, S3 the registered profile used
                by A18 reading C, S4 simulation comparisons quoted in the text, S5 listing of |corrected| > 1.
                -> results/a19/sensitivity.json, results/a19/sensitivity_tables.csv
  sources     : task data only (prior and stimulus sides; no neural data): correlation of the prior with the previous
                side and in-sample R^2 of the prior on the last 1, 5 and 10 sides, per session.
                -> results/a19/prior_history.csv, results/a19/prior_history.json
"""
import json

import numpy as np
import pandas as pd

from pns.analysis import paired_null_diff
from pns.config import ROOT, load_frozen
from pns.runner import interim_path, load_npz, log_run, setup, write_json
from pns.stats import bootstrap_ci, holm, wilcoxon_greater

OUT = ROOT / "results" / "a19"
EID = "4d8c7767-981c-4347-8e5e-5d5fffe38534"
AGGS = ("mouse_mean", "mouse_median", "session_median")


def extra(p):
    p.add_argument("--stage", choices=("sensitivity", "sources"), required=True)


def aggregate(df, col):
    """The three fixed aggregations of a per-session column, with sign counts (mice and sessions)."""
    x = df[["subject", col]].dropna()
    m = x.groupby("subject")[col].mean()
    return {"mouse_mean": float(m.mean()), "mouse_median": float(m.median()),
            "session_median": float(x[col].median()), "n_mice": int(len(m)), "n_sessions": int(len(x)),
            "mice_pos": int((m > 0).sum()), "sessions_pos": int((x[col] > 0).sum())}


def both(df, col):
    return {"with": aggregate(df, col), "without": aggregate(df[df.eid != EID], col)}


def _read(sub, eids):
    return pd.concat([pd.read_parquet(ROOT / "results" / sub / f"{e}_d5.pqt") for e in eids], ignore_index=True)


def s1_p2(subjects):
    eids = list(subjects)
    real, null = _read("decoding", eids), _read("null", eids)
    pr = paired_null_diff(real, null, "prior", "rrr_60", "rrr_1")
    pr["subject"] = pr.eid.map(subjects)
    prim = pd.read_csv(ROOT / "results" / "stats" / "d5" / "primary.csv")
    reg = prim[prim.test.str.startswith("P2")].iloc[0]
    others = {k: float(prim[prim.test.str.startswith(k)].iloc[0]["p"]) for k in ("P1", "P3")}
    out = {"session_value": float(pr.loc[pr.eid == EID, "corrected"].iloc[0]),
           "session_rank_of_16": int(pr.corrected.rank().loc[pr.eid == EID].iloc[0])}
    for tag, d in (("with", pr), ("without", pr[pr.eid != EID])):
        m = d.groupby("subject")["corrected"].mean()
        w = wilcoxon_greater(m.to_numpy())
        lo, hi = bootstrap_ci(m.to_numpy(), np.random.default_rng(0))
        ws = wilcoxon_greater(d["corrected"].to_numpy())
        out[tag] = {**aggregate(d, "corrected"), "wilcoxon_mice_p": w["p"], "boot_ci_mouse_mean": [lo, hi],
                    "holm_p": holm({"P1": others["P1"], "P2": w["p"], "P3": others["P3"]})["P2"],
                    "wilcoxon_sessions_p_descriptive": ws["p"]}
    ok = abs(out["with"]["wilcoxon_mice_p"] - reg["p"]) < 1e-12 and abs(out["with"]["mouse_mean"] - reg["mean"]) < 1e-12
    out["reproduces_registered"] = bool(ok)
    if not ok:
        raise SystemExit(f"S1 does not reproduce the registered P2: {out['with']} vs p={reg['p']}, mean={reg['mean']}")
    return out, pr


def s2_a16():
    a = pd.read_csv(ROOT / "results" / "a16" / "sessions_d5.csv")
    cols = [c for c in a.columns if c.endswith("_corr")]
    out = {"session_values": {c: float(a.loc[a.eid == EID, c].iloc[0]) for c in cols}}
    out["values"] = {c: both(a, c) for c in cols}
    ratios = {}
    for dec in ("ridge", "lasso"):
        full = "ridge_full_corr"          # the only full-population score on this decoder scale (A16 part 2)
        for fs in ("rrr_1", "rrr_60", "pca"):
            c = f"{dec}_{fs}_corr"
            if dec == "lasso":
                continue
            ratios[c] = {tag: {agg: out["values"][c][tag][agg] / out["values"][full][tag][agg] for agg in AGGS}
                         for tag in ("with", "without")}
    out["ratios_to_full"] = ratios
    return out, a


def s3_profile(subjects):
    ss = pd.read_csv(ROOT / "results" / "stats" / "d5" / "session_scores.csv")
    feats = [("prior", fs) for fs in ("rrr_1", "rrr_60", "pca", "random")] + \
            [("elapsed_time", fs) for fs in ("rrr_60", "pca", "random")]
    prof = {}
    for tag, d in (("with", ss), ("without", ss[ss.eid != EID])):
        p = {}
        for var, fs in feats:
            x = d[(d.variable == var) & (d.feature_set == fs)]
            m = x.groupby("subject")["value"].mean().to_numpy()
            p[f"{var}_{fs}"] = {"mean": float(m.mean()), "ci": list(bootstrap_ci(m, np.random.default_rng(0))),
                                "session_median": float(x["value"].median())}
        prof[tag] = p
    # P2 change: the registered per-session paired-null values
    return prof


def s3_readc(prof, p2_sessions):
    """A18 reading C recomputed against each version of the profile (same simulated means)."""
    summ = json.loads((ROOT / "results" / "a18" / "sim_summary.json").read_text())
    out = {}
    for tag in ("with", "without"):
        d = p2_sessions if tag == "with" else p2_sessions[p2_sessions.eid != EID]
        m = d.groupby("subject")["corrected"].mean().to_numpy()
        p2 = {"mean": float(m.mean()), "ci": list(bootstrap_ci(m, np.random.default_rng(0)))}
        res = {}
        for regime in ("lowrank_x1", "perunit_x1"):
            feats = summ["C_profile"][regime]["features"]
            n = 0
            detail = {}
            for f, v in feats.items():
                ref = p2 if f == "p2_change" else prof[tag][f]
                lo, hi = ref["ci"]
                w = bool(lo <= v["sim"] <= hi)
                n += w
                detail[f] = {"sim": v["sim"], "real": ref["mean"], "real_ci": [lo, hi], "within": w}
            res[regime] = {"n_within": n, "n_features": len(feats), "features": detail,
                           "committed_n_within": summ["C_profile"][regime]["n_within"]}
        out[tag] = res
    return out


def s4_sim(a16):
    rt = pd.read_csv(ROOT / "results" / "a18" / "real_targets.csv")
    summ = json.loads((ROOT / "results" / "a18" / "sim_summary.json").read_text())
    cells = pd.read_csv(ROOT / "results" / "a18" / "sim_cells.csv")
    cells = cells[cells.pipeline == "raw"].set_index("cell")
    stats = [c for c in rt.columns if c not in ("eid", "subject", "n_units", "T")]
    targets = {c: {"with": float(rt[c].median()), "without": float(rt[rt.eid != EID][c].median())} for c in stats}
    for c in targets:
        w, wo = targets[c]["with"], targets[c]["without"]
        targets[c]["relative_shift"] = float((wo - w) / abs(w)) if w != 0 else np.nan
    hs = float(cells.loc["neg_history_strong", "prior_full_mean"])
    nh = float(cells.loc["neg_history", "prior_full_mean"])
    ref = {tag: {"ridge_full_mouse_mean": a16["values"]["ridge_full_corr"][tag]["mouse_mean"],
                 "ridge_full_session_median": a16["values"]["ridge_full_corr"][tag]["session_median"],
                 "targets_session_median_full_prior_corr": targets["full_prior_corr"][tag]}
           for tag in ("with", "without")}
    frac = {tag: {k: {"history_strong": hs / v, "history_calibrated": nh / v} for k, v in ref[tag].items()}
            for tag in ("with", "without")}
    # A18 audit median-of-16 probability with the 15-session threshold
    df = pd.read_csv(ROOT / "results" / "a18" / "sim_seeds.csv")
    df = df[df.pipeline == "raw"].copy()
    df["task"] = (df.seed - 1000) % 16
    med16 = {}
    for tag in ("with", "without"):
        thr = targets["full_prior_hist_corr"][tag]
        rng = np.random.default_rng(0)
        cell_p = {}
        for cell, g in df.groupby("cell"):
            h = g.priorhist_full.to_numpy()
            m1 = np.median(rng.choice(h, (20000, 16)), axis=1)
            piv = g.pivot_table(index="task", columns=g.seed >= 1016, values="priorhist_full")
            pick = rng.integers(0, 2, (20000, 16))
            m2 = np.median(np.where(pick == 0, piv[False].to_numpy()[None], piv[True].to_numpy()[None]), axis=1)
            cell_p[cell] = {"random_16_of_32": float(np.mean(m1 <= thr)), "one_seed_per_task": float(np.mean(m2 <= thr))}
        med16[tag] = {"threshold": thr, "cells": cell_p}
    b2 = summ.get("B2_history_alone", {})
    return {"calibration_targets": targets, "reference": ref, "history_alone_fraction": frac,
            "history_strong_full_mean": hs, "history_calibrated_full_mean": nh,
            "B2_rule_target_committed": b2.get("real_target"), "median16": med16,
            "hist_controlled_recordings": {
                tag: {"session_median": targets["full_prior_hist_corr"][tag],
                      "sessions_pos": int((rt if tag == "with" else rt[rt.eid != EID]).full_prior_hist_corr.gt(0).sum()),
                      "n_sessions": int(len(rt) - (tag == "without")),
                      "wilcoxon_sessions_p": wilcoxon_greater(
                          (rt if tag == "with" else rt[rt.eid != EID]).full_prior_hist_corr.to_numpy())["p"]}
                for tag in ("with", "without")}}


def s5_listing(a16, rt):
    rows = []
    for name, df in (("results/a16/sessions_d5.csv", a16), ("results/a18/real_targets.csv", rt)):
        for c in [c for c in df.columns if c.endswith("_corr")]:
            for r in df[df[c].abs() > 1].itertuples():
                rows.append({"file": name, "quantity": c, "eid": r.eid, "subject": r.subject, "value": float(getattr(r, c))})
    return rows


def stage_sensitivity(cfg):
    frozen = load_frozen(cfg)
    subjects = {s["eid"]: s["subject"] for s in frozen["sessions"]}
    s1, p2_sessions = s1_p2(subjects)
    s2, a16 = s2_a16()
    prof = s3_profile(subjects)
    s3 = {"profile": prof, "reading_C": s3_readc(prof, p2_sessions)}
    s4 = s4_sim(s2)
    rt = pd.read_csv(ROOT / "results" / "a18" / "real_targets.csv")
    s5 = s5_listing(a16, rt)
    out = {"note": "A19, post hoc; registered P2 unchanged; all variants reported", "session": EID,
           "S1_P2": s1, "S2_A16": s2, "S3_profile": s3, "S4_simulation": s4, "S5_abs_gt_1": s5}
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / "sensitivity.json", out)
    rows = []
    for tag in ("with", "without"):
        rows.append({"quantity": "P2 registered (paired-null 30 s - 0.5 s)", "version": tag,
                     **{k: s1[tag][k] for k in ("mouse_mean", "mouse_median", "session_median", "mice_pos",
                                                 "n_mice", "sessions_pos", "n_sessions", "wilcoxon_mice_p", "holm_p")}})
        for c, v in s2["values"].items():
            rows.append({"quantity": f"A16 {c}", "version": tag, **v[tag]})
    pd.DataFrame(rows).to_csv(OUT / "sensitivity_tables.csv", index=False)
    print(json.dumps({"S1": {t: {k: s1[t][k] for k in ("mouse_mean", "session_median", "wilcoxon_mice_p", "holm_p",
                                                       "mice_pos")} for t in ("with", "without")},
                      "session_P2": s1["session_value"], "session_rank": s1["session_rank_of_16"]}, indent=1))
    log_run(cfg, "28_sensitivity_A19 sensitivity",
            f"A19: P2 mouse-mean p with/without {EID[:8]} = {s1['with']['wilcoxon_mice_p']:.3f}/"
            f"{s1['without']['wilcoxon_mice_p']:.3f}; A16 full ridge mouse mean "
            f"{s2['values']['ridge_full_corr']['with']['mouse_mean']:.3f}/"
            f"{s2['values']['ridge_full_corr']['without']['mouse_mean']:.3f}")


def stage_sources(cfg):
    from pns.pipeline import _trial_targets
    frozen = load_frozen(cfg)
    rows = []
    for s in frozen["sessions"]:
        pre = load_npz(interim_path(cfg, s["eid"]))
        prior = np.asarray(pre["prior"], float)
        side = np.asarray(pre["side"], float)
        _, tr, _ = _trial_targets(pre, cfg)["prior"]
        row = {"eid": s["eid"], "subject": s["subject"], "n_trials": len(prior), "n_decoded": len(tr)}
        for name, idx in (("all", np.arange(1, len(prior))), ("decoded", tr[tr >= 1])):
            row[f"corr_prev_side_{name}"] = float(np.corrcoef(prior[idx], side[idx - 1])[0, 1])
            for k in (1, 5, 10):
                X = np.zeros((len(idx), k))
                for j in range(1, k + 1):
                    ok = idx - j >= 0
                    X[ok, j - 1] = side[idx[ok] - j]
                X = np.column_stack([np.ones(len(idx)), X])
                y = prior[idx]
                beta = np.linalg.lstsq(X, y, rcond=None)[0]
                row[f"r2_last{k}_{name}"] = float(1 - np.sum((y - X @ beta) ** 2) / np.sum((y - y.mean()) ** 2))
        rows.append(row)
    df = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "prior_history.csv", index=False)
    stats = [c for c in df.columns if c.startswith(("corr_", "r2_"))]
    summ = {"n_sessions": len(df), "session_median": {c: float(df[c].median()) for c in stats},
            "note": "task data only; side coded as in the preprocessed trials; in-sample least squares with intercept"}
    write_json(OUT / "prior_history.json", summ)
    print(json.dumps(summ, indent=1))
    log_run(cfg, "28_sensitivity_A19 sources",
            "A19 sources: prior vs previous sides, median corr {:.2f}, R2 last 1/5/10 = {:.2f}/{:.2f}/{:.2f}".format(
                summ["session_median"]["corr_prev_side_all"], summ["session_median"]["r2_last1_all"],
                summ["session_median"]["r2_last5_all"], summ["session_median"]["r2_last10_all"]))


def main():
    args, cfg, _ = setup(__doc__, extra)
    {"sensitivity": stage_sensitivity, "sources": stage_sources}[args.stage](cfg)


if __name__ == "__main__":
    main()
