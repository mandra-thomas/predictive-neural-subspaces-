"""Amendment A17 Part 1 (post hoc, descriptive): variance shares and the rank-5 entry check.

On whole-session z-scored sqrt activity (D10 floor), population level (sums over units), pseudo-session corrections
at the sum level with the exact 200 pseudo priors of script 05:
  lowfreq_cos / lowfreq_quad : in-sample share explained by the >= 20 min cosine design / the quadratic
  prior_trial_*              : pre-stimulus windows of the prior decoder's trials, activity and prior both projected
                               off the cosine design at the window times; share explained by the prior
  prior_bin_*                : per 0.5 s bin, activity and per-bin prior both projected off the cosine design and the
                               unsigned + signed event kernels (side x sqrt(contrast), choice, feedback)
  triallocked                : in-sample share explained by the A11 trial-locked GLM
  entry_{root}_{lag}_*       : within the full-session RRR fit of that root (raw: results/; cosine-detrended:
                               results_detrend_c/), the predicted variance along the estimated prior loading
                               (Rayleigh quotient in G = B_R'X'XB_R + lam B_R'B_R) against G's eigenvalues;
                               corrected by the median over pseudo-prior loadings. Addendum: an upper bound on the
                               prior's predictable SS (corrected prior-explained SS x rho_pi(lag)^2) against the 5th
                               eigenvalue, and the pseudo-corrected capture of the prior-loading direction by Vout.
Writes results/a17/budget_sessions.csv and results/a17/budget.json.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from pns.config import ROOT, load_config, load_frozen, session_seed
from pns.lagged import lagged_pairs
from pns.pipeline import _trial_targets, residualize_session, session_S, window_S
from pns.prior import bayes_optimal_prior, pseudo_sides
from pns.rrr import RidgePath
from pns.runner import interim_path, load_npz, log_run, out_dir, run_sessions, setup, write_json
from pns.timescales import (cosine_design, epoch_minutes, event_design_full, lowfreq_share, population_share,
                            prior_per_bin, quad_design, residualize)
from pns.transform import ZScore

N_PSEUDO = 200
D = 5
ENTRY_LAGS = (1, 60)
ROOTS = {"raw": ("data", "results"), "detc": ("data_detrend_c", "results_detrend_c")}


def null_priors(pre, eid, cfg):
    rng = np.random.default_rng(session_seed(eid, cfg["seed"], "null"))          # same draws as script 05
    sides_null = np.stack([pseudo_sides(len(pre["side"]), rng)[1] for _ in range(N_PSEUDO)])
    return bayes_optimal_prior(sides_null)                                         # (N_PSEUDO, n_trials)


def corr(v):
    return float(v[0] - np.median(v[1:]))


def bin_prior_parts(pre, Z, cfg, priors):
    """Residualized per-bin activity and the matrix of residualized per-bin priors (real first, then null)."""
    tc, valid, t0, length = epoch_minutes(pre)
    X = prior_per_bin(pre, priors)                                                 # (1 + N, T)
    ok = valid & np.all(np.isfinite(X), axis=0)
    centres = tc[ok] * 60.0
    Dm = np.hstack([cosine_design(tc[ok], t0, length), event_design_full(pre, centres)])
    return residualize(Z[ok], Dm), residualize(X[:, ok].T, Dm)


def session(eid, cfg):
    pre = load_npz(interim_path(cfg, eid))
    S = session_S(pre)
    valid = np.asarray(pre["valid"], bool)
    zs = ZScore.fit(S[valid])
    Z = zs.transform(S)
    tc, _, t0, length = epoch_minutes(pre)
    row = {"eid": eid, "n_units": int(Z.shape[1])}
    row["lowfreq_cos"] = lowfreq_share(Z[valid], cosine_design(tc[valid], t0, length))
    row["lowfreq_quad"] = lowfreq_share(Z[valid], quad_design(tc[valid], t0, length))
    Zr = zs.transform(residualize_session(pre, cfg)["S_resid"])
    row["triallocked"] = float(1 - np.sum((Zr[valid] - Zr[valid].mean(0)) ** 2) / np.sum((Z[valid] - Z[valid].mean(0)) ** 2))

    priors = np.vstack([pre["prior"][None], null_priors(pre, eid, cfg)])          # (1 + N, n_trials)
    # primary: pre-stimulus windows of the decoder's trials
    win, tr, _ = _trial_targets(pre, cfg)["prior"]
    W = zs.transform(window_S(pre, win))[tr]
    spec = cfg["windows"][win]
    tw = (np.asarray(pre[spec["event"]], float)[tr] + 0.5 * sum(spec["win"])) / 60.0
    Dw = cosine_design(tw, t0, length)
    sh = population_share(residualize(W, Dw), residualize(priors[:, tr].T, Dw))
    row.update({"prior_trial_real": float(sh[0]), "prior_trial_nullmed": float(np.median(sh[1:])),
                "prior_trial_corr": corr(sh), "n_trials": int(len(tr))})
    # secondary: per bin, event kernels and cosine removed
    Wb, Xb = bin_prior_parts(pre, Z, cfg, priors)
    sb = population_share(Wb, Xb)
    row.update({"prior_bin_real": float(sb[0]), "prior_bin_nullmed": float(np.median(sb[1:])),
                "prior_bin_corr": corr(sb)})

    # entry check within each root's full-session fit; rho_pi per session from Part 0 (results/a17/timescales.csv)
    ts = pd.read_csv(Path(cfg["paths"]["results"]) / "a17" / "timescales.csv").set_index("eid")
    rho_pi = {1: float(ts.loc[eid, "rho_0.5s"]), 60: float(ts.loc[eid, "rho_30s"])}
    for root, (data_dir, res_dir) in ROOTS.items():
        pre_r = load_npz(ROOT / data_dir / "interim" / f"{eid}.npz")
        fits = load_npz(ROOT / res_dir / "subspaces" / f"{eid}_d{D}.npz")
        zr = ZScore(fits["z_mu"], fits["z_sd"])
        Zf = zr.transform(session_S(pre_r))
        Wr, Xr = bin_prior_parts(pre_r, Zf, cfg, priors)
        Bload = Wr.T @ Xr / np.sum(Xr ** 2, axis=0)                               # (p, 1 + N) prior loadings
        prior_ss = np.sum(Bload ** 2, axis=0) * np.sum(Xr ** 2, axis=0)           # prior-explained SS, summed over units
        bhat = Bload / np.linalg.norm(Bload, axis=0)
        for lag in ENTRY_LAGS:
            i, j = lagged_pairs(len(Zf), lag, np.asarray(pre_r["valid"], bool))
            path = RidgePath(Zf[i], Zf[j])
            lam = path.lam(float(fits["alpha"]))
            BR = path.coef(lam)
            XB = path.s[:, None] * (path.Wt @ BR)
            G = XB.T @ XB + lam * (BR.T @ BR)
            ev = np.sort(np.linalg.eigvalsh(G))[::-1]
            rq = np.einsum("pm,pq,qm->m", Bload, G, Bload) / np.sum(Bload ** 2, axis=0)
            k = f"entry_{root}_{lag}"
            row.update({f"{k}_lam1": float(ev[0]), f"{k}_lam5": float(ev[D - 1]), f"{k}_rq_real": float(rq[0]),
                        f"{k}_rq_nullmed": float(np.median(rq[1:])), f"{k}_rq_corr": corr(rq),
                        f"{k}_ratio_corr_to_lam5": corr(rq) / float(ev[D - 1]),
                        f"{k}_rank_real": int(np.sum(ev > rq[0]) + 1)})
            rho2 = rho_pi[lag] ** 2
            ub = corr(prior_ss) * rho2
            cap = np.sum((fits[f"Vout_full_{lag}"].T @ bhat) ** 2, axis=0)
            row.update({f"{k}_ub": float(ub), f"{k}_ub_to_lam5": float(ub / ev[D - 1]),
                        f"{k}_capture_real": float(cap[0]), f"{k}_capture_corr": corr(cap),
                        f"{k}_capture_chance": D / Zf.shape[1]})
    return row


def main():
    args, cfg, n_jobs = setup(__doc__)
    frozen = load_frozen(cfg)
    subj = {s["eid"]: s["subject"] for s in frozen["sessions"]}
    eids = [s["eid"] for s in frozen["sessions"]]
    res = run_sessions(lambda e: session(e, cfg), eids, n_jobs)
    bad = [r for r in res if not r["ok"]]
    for r in bad:
        print("FAILED", r["eid"], r["error"], r.get("tb", ""))
    df = pd.DataFrame([{k: v for k, v in r.items() if k not in ("ok",)} for r in res if r["ok"]])
    df["subject"] = df.eid.map(subj)
    od = out_dir(cfg, "a17")
    df.to_csv(od / "budget_sessions.csv", index=False)
    num = df.drop(columns=["eid", "subject"]).select_dtypes("number")
    mouse = df.groupby("subject")[num.columns].mean()
    summ = {"n_sessions": int(len(df)), "n_mice": int(mouse.shape[0]), "failed": [r["eid"] for r in bad],
            "session_median": {c: float(df[c].median()) for c in num.columns},
            "mouse_mean": {c: float(mouse[c].mean()) for c in num.columns},
            "n_sessions_prior_trial_corr_positive": int((df.prior_trial_corr > 0).sum()),
            "n_sessions_entry_below_lam5": {f"{r}_{l}": int((df[f"entry_{r}_{l}_rq_corr"] < df[f"entry_{r}_{l}_lam5"]).sum())
                                            for r in ROOTS for l in ENTRY_LAGS},
            "n_sessions_upper_bound_below_lam5": {f"{r}_{l}": int((df[f"entry_{r}_{l}_ub_to_lam5"] < 1).sum())
                                                  for r in ROOTS for l in ENTRY_LAGS}}
    write_json(od / "budget.json", summ)
    print(json.dumps({k: v for k, v in summ.items() if k != "mouse_mean"}, indent=1))
    log_run(cfg, "24_budget_A17",
            f"A17 part 1: {len(df)} sessions; median lowfreq_cos {summ['session_median']['lowfreq_cos']:.3f}, "
            f"prior_trial_corr {summ['session_median']['prior_trial_corr']:.4f}, "
            f"prior_bin_corr {summ['session_median']['prior_bin_corr']:.4f}")


if __name__ == "__main__":
    main()
