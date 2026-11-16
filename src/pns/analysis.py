"""Cross-session analysis: pre-registered primary tests, secondary measures and the variables x lags matrix.

Primary family (Holm over 3, one-sided Wilcoxon across animals after averaging sessions within animal):
  P1 geometry  : intersection-union test of cross-lag > same-lag angle at the shortest AND the longest lag
                 (p = max of the two one-sided p-values); metric = mean principal angle (deg), Vin basis,
                 session alpha.
  P2 prior     : null-corrected [R^2(rrr_long) - R^2(rrr_short)] > 0, null built on the paired difference.
  P3 cur_side  : null-corrected [AUC(rrr_short) - AUC(rrr_long)] > 0 on nonzero-contrast trials.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .stats import bootstrap_ci, fisher_combine, holm, min_attainable_p, null_summary, spearman_trend, \
    wilcoxon_greater

EXPERIMENTER = ("prior", "prev_side", "cur_side", "prev_side_gain", "cur_side_gain")


def _animal_test(df: pd.DataFrame, col: str, rng) -> dict:
    a = df.groupby("subject")[col].mean()
    t = wilcoxon_greater(a.to_numpy())
    lo, hi = bootstrap_ci(a.to_numpy(), rng)
    return {**t, "mean": float(a.mean()), "ci_lo": lo, "ci_hi": hi, "n_sessions": int(df[col].notna().sum())}


def geometry_session_table(geo: pd.DataFrame, short: int, long_: int, metric: str = "mean_deg",
                           alpha_mode: str = "session", basis: str = "Vin") -> pd.DataFrame:
    g = geo[(geo.alpha_mode == alpha_mode) & (geo.basis == basis)]

    def val(df, a, b):
        r = df[(df.lag_A == a) & (df.lag_B == b)][metric]
        return float(r.iloc[0]) if len(r) else np.nan
    rows = []
    for eid, df in g.groupby("eid"):
        cross = 0.5 * (val(df, short, long_) + val(df, long_, short))
        rows.append({"eid": eid, "cross": cross, "same_short": val(df, short, short),
                     "same_long": val(df, long_, long_)})
    t = pd.DataFrame(rows)
    t["diff_short"] = t["cross"] - t["same_short"]
    t["diff_long"] = t["cross"] - t["same_long"]
    t["diff_mean_floor"] = t["cross"] - 0.5 * (t["same_short"] + t["same_long"])
    return t


def paired_null_diff(real: pd.DataFrame, null: pd.DataFrame, variable: str, fs_a: str, fs_b: str) -> pd.DataFrame:
    """Per session: score(fs_a) - score(fs_b), corrected by the median of the same difference in the null."""
    rows = []
    for eid in real.eid.unique():
        r = real[(real.eid == eid) & (real.variable == variable)].set_index("feature_set")["score"]
        if fs_a not in r or fs_b not in r:
            continue
        diff = float(r[fs_a] - r[fs_b])
        n = null[(null.eid == eid) & (null.variable == variable)]
        if len(n):
            piv = n.pivot_table(index="pseudo_id", columns="feature_set", values="score")
            nd = (piv[fs_a] - piv[fs_b]).to_numpy()
            s = null_summary(diff, nd)
        else:
            s = {"corrected": np.nan, "p": np.nan, "z": np.nan, "percentile": np.nan}
        rows.append({"eid": eid, "raw_diff": diff, **{f"{k}": v for k, v in s.items()}})
    return pd.DataFrame(rows)


def corrected_scores(real: pd.DataFrame, null: pd.DataFrame) -> pd.DataFrame:
    """Per (session, feature set, variable): raw score and, where a null exists, real - null median, p, z."""
    out = real.copy()
    if len(null):
        g = null.groupby(["eid", "feature_set", "variable"])["score"]
        stats = g.apply(lambda s: s.to_numpy()).rename("null_scores").reset_index()
        out = out.merge(stats, on=["eid", "feature_set", "variable"], how="left")
        summ = out.apply(lambda r: null_summary(r["score"], r["null_scores"])
                         if isinstance(r["null_scores"], np.ndarray) else
                         {"corrected": np.nan, "p": np.nan, "z": np.nan, "percentile": np.nan}, axis=1)
        out = pd.concat([out.drop(columns="null_scores"), pd.DataFrame(list(summ), index=out.index)], axis=1)
    else:
        for k in ("corrected", "p", "z", "percentile"):
            out[k] = np.nan
    out["value"] = np.where(out["variable"].isin(EXPERIMENTER), out["corrected"], out["score"])
    return out


def run_analysis(subjects: dict, metas: dict, est: pd.DataFrame, geo: pd.DataFrame, real: pd.DataFrame,
                 null: pd.DataFrame, lags: list[int], min_animals: int, seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    short, long_ = lags[0], lags[-1]
    s_rrr, l_rrr = f"rrr_{short}", f"rrr_{long_}"
    weak = {e: m.get("weak_lag", {}) for e, m in metas.items()}

    def add_subj(df):
        return df.assign(subject=df["eid"].map(subjects))

    n_animals = len(set(subjects[e] for e in metas))
    warn = []
    if n_animals < min_animals:
        warn.append(f"only {n_animals} animals (< {min_animals}); min attainable one-sided p = "
                    f"{min_attainable_p(n_animals):.4f}")

    # ---- P1 geometry (sessions whose short or long lag is weak are excluded)
    gt = add_subj(geometry_session_table(geo, short, long_))
    ok = gt["eid"].map(lambda e: not (weak.get(e, {}).get(str(short)) or weak.get(e, {}).get(str(long_))
                                     or weak.get(e, {}).get(short) or weak.get(e, {}).get(long_)))
    gt_ok = gt[ok]
    t_s, t_l = _animal_test(gt_ok, "diff_short", rng), _animal_test(gt_ok, "diff_long", rng)
    p1 = {"test": "P1 geometry IUT (cross > same at both lags)", "p": max(t_s["p"], t_l["p"]),
          "n": t_s["n"], "mean_diff_short": t_s["mean"], "mean_diff_long": t_l["mean"],
          "ci_short": (t_s["ci_lo"], t_s["ci_hi"]), "ci_long": (t_l["ci_lo"], t_l["ci_hi"]),
          "n_sessions_excluded_weak": int((~ok).sum())}

    # ---- P2 prior, P3 current side (paired-difference nulls)
    pr = add_subj(paired_null_diff(real, null, "prior", l_rrr, s_rrr))
    cs = add_subj(paired_null_diff(real, null, "cur_side", s_rrr, l_rrr))
    t2, t3 = _animal_test(pr, "corrected", rng), _animal_test(cs, "corrected", rng)
    p2 = {"test": "P2 prior: corrected R2(long) - R2(short) > 0", **t2}
    p3 = {"test": "P3 cur_side: corrected AUC(short) - AUC(long) > 0", **t3}
    adj = holm({"P1": p1["p"], "P2": p2["p"], "P3": p3["p"]})
    for key, d in (("P1", p1), ("P2", p2), ("P3", p3)):
        d["p_holm"] = adj[key]
    primary = pd.DataFrame([p1, p2, p3])

    # ---- secondary
    cs_all = add_subj(corrected_scores(real, null))
    sec = []
    # S1 nesting index
    nest = pd.DataFrame([{"eid": e, **{k: v for k, v in m.items() if k.startswith("nest_")}} for e, m in metas.items()])
    nest = add_subj(nest)
    for col in [c for c in nest.columns if c.startswith("nest_")]:
        a = nest.groupby("subject")[col].mean()
        lo, hi = bootstrap_ci(a.to_numpy(), rng)
        sec.append({"test": f"S1 {col} (mean)", "mean": float(a.mean()), "ci_lo": lo, "ci_hi": hi, "n": len(a)})
    # S2 orthogonal-complement decoding (directional, one-sided)
    for var, a_fs, b_fs, label in (("prior", "orth_long_not_short", "orth_short_not_long", "prior long-only > short-only"),
                                   ("cur_side", "orth_short_not_long", "orth_long_not_short", "cur_side short-only > long-only")):
        dd = add_subj(paired_null_diff(real, null, var, a_fs, b_fs))
        sec.append({"test": f"S2 {label}", **_animal_test(dd, "corrected", rng)})
    # S3 trend across lags (Spearman per session on corrected / raw values)
    for var in ("prior", "cur_side", "prev_side", "choice", "feedback", "wheel_speed", "elapsed_time"):
        rows = []
        for eid, df in cs_all[(cs_all.variable == var) & cs_all.feature_set.str.startswith("rrr_")].groupby("eid"):
            df = df.sort_values("lag")
            rows.append({"eid": eid, "rho": spearman_trend(df["value"].to_numpy(), df["lag"].to_numpy())})
        if rows:
            tr = add_subj(pd.DataFrame(rows))
            sec.append({"test": f"S3 Spearman trend over lags: {var} (> 0)", **_animal_test(tr, "rho", rng)})
    # S4 Fisher-combined session p for prior at each lag
    for lag in lags:
        ps = cs_all[(cs_all.variable == "prior") & (cs_all.feature_set == f"rrr_{lag}")]["p"]
        sec.append({"test": f"S4 Fisher-combined prior p, rrr_{lag}", "p": fisher_combine(ps.to_numpy()),
                    "n": int(ps.notna().sum())})
    # S5 estimator check: RRR (session alpha) vs PCA (its best alpha) and fraction of full-rank R2
    e = add_subj(est)
    for lag in lags:
        piv = e[e.lag == lag].pivot_table(index=["eid", "subject"], columns="method",
                                          values=["r2_session_alpha", "r2_best"])
        dfl = pd.DataFrame({"diff": piv[("r2_session_alpha", "rrr")] - piv[("r2_best", "pca")],
                            "frac": piv[("r2_session_alpha", "rrr")] / piv[("r2_best", "ridge")]}).reset_index()
        sec.append({"test": f"S5 RRR - PCA R2 > 0, lag {lag}", **_animal_test(dfl, "diff", rng)})
        a = dfl.groupby("subject")["frac"].mean()
        sec.append({"test": f"S5 RRR / full-rank R2, lag {lag} (mean)", "mean": float(a.mean()), "n": len(a)})
    # S6 geometry sensitivities
    for alpha_mode, basis, metric in (("per_lag", "Vin", "mean_deg"), ("session", "Vout", "mean_deg"),
                                      ("session", "Vin", "sum_sin2"), ("session", "Vin", "first_deg")):
        g2 = add_subj(geometry_session_table(geo, short, long_, metric, alpha_mode, basis))
        g2 = g2[g2.eid.isin(gt_ok.eid)]
        a, b = _animal_test(g2, "diff_short", rng), _animal_test(g2, "diff_long", rng)
        sec.append({"test": f"S6 geometry IUT [{alpha_mode}, {basis}, {metric}]", "p": max(a["p"], b["p"]),
                    "n": a["n"], "mean_diff_short": a["mean"], "mean_diff_long": b["mean"]})
    secondary = pd.DataFrame(sec)

    # ---- drift flag per session (proposal rule)
    drift = []
    for eid in metas:
        sc = cs_all[(cs_all.eid == eid)]
        def get(fs, var, col="score"):
            r = sc[(sc.feature_set == fs) & (sc.variable == var)][col]
            return float(r.iloc[0]) if len(r) else np.nan
        el = get(l_rrr, "elapsed_time")
        drift.append({"eid": eid, "subject": subjects[eid], "elapsed_long": el,
                      "elapsed_pca": get("pca", "elapsed_time"), "elapsed_random": get("random", "elapsed_time"),
                      "prior_p_long": get(l_rrr, "prior", "p"),
                      "drift_flag": bool(el > max(get("pca", "elapsed_time"), get("random", "elapsed_time"))
                                         and not get(l_rrr, "prior", "p") < 0.05)})
    drift = pd.DataFrame(drift)

    # ---- variables x feature-set matrix (animal means of the per-session value)
    am = cs_all.groupby(["subject", "feature_set", "variable"], as_index=False)["value"].mean()
    rows = []
    for (fs, var), df in am.groupby(["feature_set", "variable"]):
        lo, hi = bootstrap_ci(df["value"].to_numpy(), rng)
        rows.append({"feature_set": fs, "variable": var, "mean": float(df["value"].mean()), "ci_lo": lo,
                     "ci_hi": hi, "n_animals": len(df)})
    matrix = pd.DataFrame(rows)
    return {"primary": primary, "secondary": secondary, "matrix": matrix, "geometry_sessions": gt,
            "drift": drift, "session_scores": cs_all, "warnings": warn, "n_animals": n_animals}
