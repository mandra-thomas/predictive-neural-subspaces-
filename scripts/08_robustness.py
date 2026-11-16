"""POST HOC robustness of the three primary tests (not pre-registered; reported as such).

For each primary test (P1 geometry IUT, P2 prior, P3 current side), recompute the one-sided animal-level
Wilcoxon p-value
  * leave-one-animal-out (min / median / max p over the 13 refits, and the animal whose removal hurts most);
  * with flagged sessions removed: DY_014 (readout dominated by one 141 Hz, AC1 = 0.95 cluster with a
    late-session rate drop) and sessions with near-zero held-out RRR R^2 at every lag (< 0.01).
Also reports the sign-consistency of each effect across animals.

Writes results/robustness/d{d}.csv. Uses the per-session tables already produced by 04/05; refits nothing.
"""
import json

import numpy as np
import pandas as pd

from pns.analysis import geometry_session_table, paired_null_diff
from pns.config import load_frozen
from pns.runner import log_run, out_dir, setup
from pns.stats import holm, wilcoxon_greater


def extra(p):
    p.add_argument("--d", type=int, default=None)
    p.add_argument("--flag-subjects", nargs="*", default=["DY_014"])
    p.add_argument("--min-r2", type=float, default=0.01)


def _read(dirp, eids, d):
    return pd.concat([pd.read_parquet(dirp / f"{e}_d{d}.pqt") for e in eids], ignore_index=True)


def main():
    args, cfg, _ = setup(__doc__, extra)
    d = args.d or cfg["model"]["d"]
    lags = list(cfg["lags_bins"])
    short, long_ = lags[0], lags[-1]
    subjects = {s["eid"]: s["subject"] for s in load_frozen(cfg)["sessions"]}
    eids = pd.read_csv(out_dir(cfg, "stats", f"d{d}") / "geometry_sessions.csv")["eid"].tolist()
    geo = _read(out_dir(cfg, "geometry"), eids, d)
    real = _read(out_dir(cfg, "decoding"), eids, d)
    null = _read(out_dir(cfg, "null"), eids, d)
    est = _read(out_dir(cfg, "estimator"), eids, d)

    gt = geometry_session_table(geo, short, long_)
    pr = paired_null_diff(real, null, "prior", f"rrr_{long_}", f"rrr_{short}")
    cs = paired_null_diff(real, null, "cur_side", f"rrr_{short}", f"rrr_{long_}")
    tab = (gt[["eid", "diff_short", "diff_long"]]
           .merge(pr[["eid", "corrected"]].rename(columns={"corrected": "prior"}), on="eid")
           .merge(cs[["eid", "corrected"]].rename(columns={"corrected": "cur_side"}), on="eid"))
    tab["subject"] = tab["eid"].map(subjects)
    r2 = est[est.method == "rrr"].groupby("eid")["r2_session_alpha"].max()
    tab["max_rrr_r2"] = tab["eid"].map(r2)

    def primary(t):
        a = t.groupby("subject")[["diff_short", "diff_long", "prior", "cur_side"]].mean()
        p1 = max(wilcoxon_greater(a.diff_short.to_numpy())["p"], wilcoxon_greater(a.diff_long.to_numpy())["p"])
        p = {"P1": p1, "P2": wilcoxon_greater(a.prior.to_numpy())["p"],
             "P3": wilcoxon_greater(a.cur_side.to_numpy())["p"]}
        return p, holm(p), a

    rows = []
    p_all, h_all, a_all = primary(tab)
    sign = {"P1": ((a_all.diff_short > 0) & (a_all.diff_long > 0)).sum(), "P2": (a_all.prior > 0).sum(),
            "P3": (a_all.cur_side > 0).sum()}
    for k in p_all:
        rows.append({"variant": "all", "test": k, "n_animals": len(a_all), "p": p_all[k], "p_holm": h_all[k],
                     "n_animals_in_direction": int(sign[k])})
    loo = {k: [] for k in p_all}
    for s in sorted(tab.subject.unique()):
        p, h, _ = primary(tab[tab.subject != s])
        for k in p:
            loo[k].append((h[k], s))
    for k, v in loo.items():
        hs = np.array([x for x, _ in v])
        worst = max(v)[1]
        rows.append({"variant": "leave-one-animal-out", "test": k, "n_animals": len(a_all) - 1,
                     "p_holm_min": hs.min(), "p_holm_median": float(np.median(hs)), "p_holm_max": hs.max(),
                     "worst_drop": worst})
    drops = {f"drop {'+'.join(args.flag_subjects)}": tab[~tab.subject.isin(args.flag_subjects)],
             f"drop sessions max RRR R2 < {args.min_r2}": tab[tab.max_rrr_r2 >= args.min_r2]}
    drops["drop both"] = tab[~tab.subject.isin(args.flag_subjects) & (tab.max_rrr_r2 >= args.min_r2)]
    for name, t in drops.items():
        p, h, a = primary(t)
        for k in p:
            rows.append({"variant": name, "test": k, "n_animals": len(a), "n_sessions": len(t), "p": p[k],
                         "p_holm": h[k]})
    out = pd.DataFrame(rows)
    od = out_dir(cfg, "robustness")
    out.to_csv(od / f"d{d}.csv", index=False)
    tab.to_csv(od / f"d{d}_session_effects.csv", index=False)
    pd.set_option("display.width", 200)
    print(out.round(4).to_string(index=False))
    print("low-R2 sessions:", tab.loc[tab.max_rrr_r2 < args.min_r2, ["subject", "max_rrr_r2"]].to_dict("records"))
    log_run(cfg, "08_robustness", f"POST HOC d={d}; LOAO max p_holm "
            + ", ".join(f"{k}={max(x for x, _ in v):.3g}" for k, v in loo.items()))


if __name__ == "__main__":
    main()
