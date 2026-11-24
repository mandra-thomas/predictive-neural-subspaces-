"""Amendment A17 Part 2 (post hoc): the lag sweep across the prior's own timescale, on both detrended copies.

Reads results_a17_longlag_{c,q} (scripts 04 and 05 with config_a17_longlag.yaml on data_detrend_{c,q}).
1. Reproduction check (must pass before reading): per-session alpha, and real and null scores of rrr_1/4/16/60, pca
   and random, equal the A16 roots results_detrend_{c,q}.
2. Per lag: corrected prior R^2, corrected current-side AUC and elapsed-time R^2 for rrr_{lag}, PCA and random (mouse
   means, 95% bootstrap CIs over mice); minimum test pairs per CV fold.
3. Tests (one-sided Wilcoxon across mice, paired-null differences): rrr_120 (60 s) > rrr_1 (0.5 s), and rrr_120 > PCA.
   Reading "band selection" only if all four tests (two per root) have p < 0.05; otherwise "no band selection".
4. Descriptive: Spearman correlation between the per-lag mean corrected prior and the median rho_pi(lag)^2 (Part 0).
Writes results/a17/longlag_{c,q}.csv and results/a17/longlag.json.
"""
import json

import numpy as np
import pandas as pd
from scipy import stats as sps

from pns.analysis import corrected_scores, paired_null_diff
from pns.config import ROOT, load_frozen
from pns.runner import log_run, out_dir, setup, write_json
from pns.stats import bootstrap_ci, wilcoxon_greater

D = 5
ORIG = [1, 4, 16, 60]
BAND = 120                                    # 60 s
RHO_COL = {1: "rho_0.5s", 4: "rho_2s", 16: "rho_8s", 60: "rho_30s", 120: "rho_60s", 240: "rho_120s", 480: "rho_240s"}


def read(root, kind, eids):
    return pd.concat([pd.read_parquet(root / kind / f"{e}_d{D}.pqt") for e in eids], ignore_index=True)


def reproduction(v, eids):
    new, old = ROOT / f"results_a17_longlag_{v}", ROOT / f"results_detrend_{v}"
    out = {"alpha_equal": all(json.loads((new / "subspaces" / f"{e}_d{D}.json").read_text())["alpha"] ==
                              json.loads((old / "subspaces" / f"{e}_d{D}.json").read_text())["alpha"] for e in eids)}
    sets = [f"rrr_{l}" for l in ORIG] + ["pca", "random"]
    for kind in ("decoding", "null"):
        a, b = read(new, kind, eids), read(old, kind, eids)
        keys = ["eid", "feature_set", "variable"] + (["pseudo_id"] if kind == "null" else [])
        a, b = a[a.feature_set.isin(sets)], b[b.feature_set.isin(sets)]
        m = a.merge(b, on=keys, suffixes=("_new", "_old"), how="outer", indicator=True)
        out[f"{kind}_rows_matched"] = bool((m["_merge"] == "both").all())
        out[f"{kind}_max_abs_diff"] = float(np.nanmax(np.abs(m.score_new - m.score_old)))
    out["passed"] = bool(out["alpha_equal"] and out["decoding_rows_matched"] and out["null_rows_matched"]
                         and out["decoding_max_abs_diff"] < 1e-9 and out["null_max_abs_diff"] < 1e-9)
    return out


def mouse_mean(df, col, subj):
    return df.assign(subject=df.eid.map(subj)).groupby("subject")[col].mean()


def analyse_root(v, eids, subj, lags, rho2, rng):
    root = ROOT / f"results_a17_longlag_{v}"
    real, null = read(root, "decoding", eids), read(root, "null", eids)
    cs = corrected_scores(real, null)
    pairs = [json.loads((root / "subspaces" / f"{e}_d{D}.json").read_text())["min_test_pairs_per_fold"] for e in eids]
    rows = []
    for fs, lag in [(f"rrr_{l}", l) for l in lags] + [("pca", None), ("random", None)]:
        row = {"feature_set": fs, "lag_bins": lag, "lag_s": lag * 0.5 if lag else np.nan,
               "rho_pi2_median": rho2.get(lag, np.nan),
               "min_test_pairs_per_fold": min(int(p[str(lag)]) for p in pairs) if lag else np.nan}
        for var in ("prior", "cur_side", "elapsed_time"):
            x = cs[(cs.feature_set == fs) & (cs.variable == var)]
            mm = mouse_mean(x, "value", subj)
            lo, hi = bootstrap_ci(mm.to_numpy(), rng)
            row.update({f"{var}_mean": float(mm.mean()), f"{var}_ci_lo": lo, f"{var}_ci_hi": hi})
        rows.append(row)
    tab = pd.DataFrame(rows)
    tests = {}
    for name, (a, b) in {"band_vs_short": (f"rrr_{BAND}", "rrr_1"), "band_vs_pca": (f"rrr_{BAND}", "pca")}.items():
        pdiff = paired_null_diff(real, null, "prior", a, b)
        mm = mouse_mean(pdiff, "corrected", subj)
        w = wilcoxon_greater(mm.to_numpy())
        tests[name] = {"mean": float(mm.mean()), "median": w["median"], "p": w["p"], "n_mice": w["n"],
                       "mice_positive": int((mm > 0).sum())}
    rr = tab[tab.lag_bins.notna()]
    rho_s = sps.spearmanr(rr.prior_mean, rr.rho_pi2_median)
    return tab, tests, {"spearman_prior_vs_rho2": float(rho_s.statistic), "spearman_p": float(rho_s.pvalue)}


def main():
    args, cfg, _ = setup(__doc__)
    frozen = load_frozen(cfg)
    subj = {s["eid"]: s["subject"] for s in frozen["sessions"]}
    eids = [s["eid"] for s in frozen["sessions"]]
    lags = [1, 4, 16, 60, 120, 240, 480]
    ts = pd.read_csv(out_dir(cfg, "a17") / "timescales.csv")
    rho2 = {l: float((ts[c] ** 2).median()) for l, c in RHO_COL.items()}
    rng = np.random.default_rng(cfg["seed"])
    out = {"lags_bins": lags, "rho_pi2_median": rho2}
    for v in ("c", "q"):
        rep = reproduction(v, eids)
        tab, tests, desc = analyse_root(v, eids, subj, lags, rho2, rng)
        tab.to_csv(out_dir(cfg, "a17") / f"longlag_{v}.csv", index=False)
        out[v] = {"reproduction": rep, "tests": tests, **desc}
        pd.set_option("display.width", 220)
        print(f"\n=== detrend {v}: reproduction {'PASSED' if rep['passed'] else 'FAILED'} {rep}")
        print(tab[["feature_set", "lag_s", "rho_pi2_median", "min_test_pairs_per_fold", "prior_mean", "prior_ci_lo",
                   "prior_ci_hi", "cur_side_mean", "elapsed_time_mean"]].round(4).to_string(index=False))
        print("tests:", json.dumps(tests), desc)
    passed = out["c"]["reproduction"]["passed"] and out["q"]["reproduction"]["passed"]
    band = all(out[v]["tests"][t]["p"] < 0.05 for v in ("c", "q") for t in ("band_vs_short", "band_vs_pca"))
    out["reading"] = ("reproduction check failed: not read" if not passed
                      else "band selection" if band else "no band selection")
    write_json(out_dir(cfg, "a17") / "longlag.json", out)
    print("\nreading:", out["reading"])
    log_run(cfg, "25_longlag_A17", f"A17 part 2: reading={out['reading']}; reproduction c={out['c']['reproduction']['passed']}, "
            f"q={out['q']['reproduction']['passed']}; 60 s vs 0.5 s p: c={out['c']['tests']['band_vs_short']['p']:.3g}, "
            f"q={out['q']['tests']['band_vs_short']['p']:.3g}")


if __name__ == "__main__":
    main()
