"""Session-level pipeline, independent of IBL I/O so it runs identically on synthetic and real data.

preprocess_session -> fit_session (subspaces, estimator check, geometry) -> decode_session (content +
pseudo-session null) ; gate_session (full-population, Findling-style prior decoding).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .binning import bin_edges, bin_mean, bin_spikes, invalid_from_intervals, window_counts
from .decode import auc_cv, lasso_nested_r2, r2_cv
from .geometry import (angle_summary, complement_basis, cov_matched_random, nesting_index, principal_angles,
                       random_floor)
from .lagged import chunk_folds, contiguous_folds, session_halves
from .prior import bayes_optimal_prior, pseudo_sides, side_from_contrasts
from .rrr import METHODS, cv_lagged, fit_rrr, pca_basis
from .stats import null_summary
from .transform import ZScore, sqrt_counts

TRIAL_KEYS = ("intervals", "stimOn_times", "firstMovement_times", "feedback_times", "contrastLeft",
              "contrastRight", "probabilityLeft", "choice", "feedbackType")


# --------------------------------------------------------------------------- preprocessing
def preprocess_session(spike_times, spike_clusters, n_units: int, trials: dict, mask, wheel_t, wheel_v,
                       cfg: dict, bad_intervals=None) -> dict:
    """Bin the task epoch, compute trial windows, wheel speed and the Bayes-optimal prior.

    trials: dict of per-trial arrays over the FULL (unmasked) trial sequence, keys TRIAL_KEYS,
            'intervals' shaped (n_trials, 2). mask: BWM trial mask (bool, n_trials).
    """
    bin_s = cfg["binning"]["bin_s"]
    iv = np.asarray(trials["intervals"], dtype=float)
    t0, t1 = float(iv[0, 0]), float(np.nanmax(iv[:, 1]))
    edges = bin_edges(t0, t1, bin_s)
    counts = bin_spikes(spike_times, spike_clusters, n_units, edges)
    rate = counts.sum(0) / (edges[-1] - edges[0])
    keep = rate >= cfg["binning"]["min_rate_hz"]
    out = {"counts": counts[:, keep], "edges": edges, "unit_keep": keep,
           "valid": ~invalid_from_intervals(edges, bad_intervals)}
    for name, spec in cfg["windows"].items():
        out[f"win_{name}"] = window_counts(spike_times, spike_clusters, n_units,
                                           np.asarray(trials[spec["event"]], dtype=float), spec["win"])[:, keep]
    if wheel_t is not None:
        out["wheel_speed"] = bin_mean(np.asarray(wheel_t), np.abs(np.asarray(wheel_v)), edges)
    else:
        out["wheel_speed"] = np.full(len(edges) - 1, np.nan)
    cl = np.asarray(trials["contrastLeft"], dtype=float)
    cr = np.asarray(trials["contrastRight"], dtype=float)
    side = side_from_contrasts(cl, cr)
    prior = bayes_optimal_prior(side)
    pl = np.asarray(trials["probabilityLeft"], dtype=float)
    ok = ~np.isnan(pl)
    out.update(side=side, prior=prior, contrast=np.where(side > 0, cl, cr),
               mask=np.asarray(mask, dtype=bool), choice=np.asarray(trials["choice"], dtype=float),
               feedbackType=np.asarray(trials["feedbackType"], dtype=float), probabilityLeft=pl,
               stimOn_times=np.asarray(trials["stimOn_times"], dtype=float),
               prior_pleft_corr=float(np.corrcoef(prior[ok], pl[ok])[0, 1]) if ok.sum() > 2 else np.nan,
               median_trial_s=float(np.nanmedian(np.diff(iv[:, 0]))))
    return out


# --------------------------------------------------------------------------- subspaces
def fit_session(pre: dict, cfg: dict, d: int, rng: np.random.Generator) -> tuple[dict, pd.DataFrame, pd.DataFrame, dict]:
    """Fit lagged RRR subspaces (full session and halves), the estimator check and geometry tables."""
    S = sqrt_counts(pre["counts"])
    valid = np.asarray(pre["valid"], dtype=bool)
    T, p = S.shape
    if d >= p:
        raise ValueError(f"d={d} must be < number of units p={p}")
    lags = list(cfg["lags_bins"])
    alphas = cfg["model"]["alphas"]
    nf, emb = cfg["cv"]["n_folds"], cfg["cv"]["embargo_bins"]

    # estimator check + alpha selection (one CV pass per lag, all methods)
    cv = {lag: cv_lagged(S, lag, d, alphas, nf, emb, valid, rng=rng, methods=METHODS) for lag in lags}
    curves = np.stack([cv[lag]["rrr"] for lag in lags])
    a_idx = int(np.argmax(curves.mean(0)))
    alpha = float(alphas[a_idx])
    per_lag_alpha = {lag: float(alphas[int(np.argmax(curves[k]))]) for k, lag in enumerate(lags)}
    weak = {lag: bool(np.all(curves[k] <= 0)) for k, lag in enumerate(lags)}
    est_rows = []
    for lag in lags:
        for m in METHODS:
            est_rows.append({"lag": lag, "method": m, "r2_session_alpha": float(cv[lag][m][a_idx]),
                             "r2_best": float(np.max(cv[lag][m])),
                             "alpha_best": float(alphas[int(np.argmax(cv[lag][m]))])})
    estimator = pd.DataFrame(est_rows)

    # full-session fits in one shared z-scored coordinate system
    zs = ZScore.fit(S[valid])
    Z = zs.transform(S)
    fits = {"z_mu": zs.mu, "z_sd": zs.sd, "alpha": alpha, "lags": np.array(lags), "d": d}
    for lag in lags:
        f, _ = fit_rrr(S, lag, d, alpha, valid, zscore=zs)
        fits[f"Vin_full_{lag}"], fits[f"Vout_full_{lag}"] = f.Vin, f.Vout
    C = np.cov(Z[valid].T)
    fits["V_pca"] = pca_basis(Z[valid], d)
    fits["V_random"] = cov_matched_random(C, d, rng)

    # split-half fits (whole-session z-scoring; same alpha rule) for geometry
    seg = session_halves(T, cfg["cv"]["half_gap_bins"])
    geo_rows = []
    for alpha_mode, a_of in (("session", {lag: alpha for lag in lags}), ("per_lag", per_lag_alpha)):
        halves = {}
        for h in (0, 1):
            segment = np.where(seg == h, 0, -1)
            for lag in lags:
                f, _ = fit_rrr(S, lag, d, a_of[lag], valid, segment, zscore=zs)
                halves[(h, lag)] = f
                if alpha_mode == "session":
                    fits[f"Vin_half{h}_{lag}"], fits[f"Vout_half{h}_{lag}"] = f.Vin, f.Vout
        for basis in ("Vin", "Vout"):
            for la in lags:
                for lb in lags:
                    theta = principal_angles(getattr(halves[(0, la)], basis), getattr(halves[(1, lb)], basis))
                    row = {"alpha_mode": alpha_mode, "basis": basis, "lag_A": la, "lag_B": lb, **angle_summary(theta)}
                    row.update({f"angle{k + 1}_deg": float(np.degrees(t)) for k, t in enumerate(theta)})
                    geo_rows.append(row)
    geometry = pd.DataFrame(geo_rows)

    short, long_ = lags[0], lags[-1]
    meta = {"T": T, "p": p, "d": d, "alpha": alpha, "per_lag_alpha": per_lag_alpha, "weak_lag": weak,
            "n_trials_masked": int(np.sum(pre["mask"])), "prior_pleft_corr": float(pre["prior_pleft_corr"]),
            "median_trial_s": float(pre["median_trial_s"])}
    for k in (1, 2):
        meta[f"nest_short_contains_long_k{k}"] = nesting_index(fits[f"Vin_full_{short}"], fits[f"Vin_full_{long_}"], k)
        meta[f"nest_long_contains_short_k{k}"] = nesting_index(fits[f"Vin_full_{long_}"], fits[f"Vin_full_{short}"], k)
    meta.update({f"floor_{k}": v for k, v in random_floor(C, d, rng, n=300).items()})
    return fits, estimator, geometry, meta


# --------------------------------------------------------------------------- decoding
def feature_sets(fits: dict) -> tuple[dict, dict]:
    """(null_sets, real_only_sets): name -> (basis p x k, lag or nan)."""
    lags = [int(x) for x in fits["lags"]]
    short, long_ = lags[0], lags[-1]
    Vin = {lag: fits[f"Vin_full_{lag}"] for lag in lags}
    main = {f"rrr_{lag}": (Vin[lag], lag) for lag in lags}
    main["pca"] = (fits["V_pca"], np.nan)
    main["random"] = (fits["V_random"], np.nan)
    main["orth_short_not_long"] = (complement_basis(Vin[short], Vin[long_]), short)
    main["orth_long_not_short"] = (complement_basis(Vin[long_], Vin[short]), long_)
    dims = {f"dim{k + 1}_{lag}": (Vin[lag][:, [k]], lag) for lag in lags for k in range(Vin[lag].shape[1])}
    return main, dims


def _trial_targets(pre: dict, cfg: dict) -> dict:
    """name -> (window, trial index array, kind, null?)"""
    mask = np.asarray(pre["mask"], bool)
    n = len(mask)
    idx = np.arange(n)
    finite = {w: ~np.any(np.isnan(pre[f"win_{w}"]), axis=1) for w in cfg["windows"]}
    contrast = np.nan_to_num(pre["contrast"], nan=0.0)
    choice = pre["choice"]
    return {
        "prior": ("pre_stim", idx[mask & finite["pre_stim"]], "r2"),
        "prev_side": ("pre_stim", idx[mask & finite["pre_stim"] & (idx > 0)], "auc"),
        "cur_side": ("post_stim", idx[mask & finite["post_stim"] & (contrast > 0)], "auc"),
        "choice": ("choice", idx[mask & finite["choice"] & np.isin(choice, (-1, 1))], "auc"),
        "feedback": ("feedback", idx[mask & finite["feedback"] & np.isin(pre["feedbackType"], (-1, 1))], "auc"),
    }


def _target_values(name: str, side: np.ndarray, prior: np.ndarray, pre: dict, tr: np.ndarray) -> np.ndarray:
    if name == "prior":
        return prior[..., tr]
    if name == "prev_side":
        return side[..., tr - 1]
    if name == "cur_side":
        return side[..., tr]
    if name == "choice":
        return pre["choice"][tr]
    if name == "feedback":
        return pre["feedbackType"][tr]
    raise KeyError(name)


def _gain(F, y, cov, folds, C):
    return auc_cv(np.column_stack([cov, F]), y, folds, C) - auc_cv(cov[:, None], y, folds, C)


def decode_session(pre: dict, fits: dict, cfg: dict, rng: np.random.Generator, n_pseudo: int):
    """Decode every target from every feature set; pseudo-session null for experimenter-generated targets.
    The SAME pseudo sequences are used for every feature set and lag. Returns (real_df, null_df)."""
    zs = ZScore(fits["z_mu"], fits["z_sd"])
    C, ridge_a = cfg["decode"]["C"], cfg["decode"]["ridge_alpha"]
    nf = cfg["cv"]["n_folds"]
    main, dims = feature_sets(fits)
    targets = _trial_targets(pre, cfg)
    side, prior = pre["side"], pre["prior"]
    Zw = {w: zs.transform(sqrt_counts(pre[f"win_{w}"])) for w in cfg["windows"]}

    sides_null = np.stack([pseudo_sides(len(side), rng)[1] for _ in range(n_pseudo)]) if n_pseudo else None
    prior_null = bayes_optimal_prior(sides_null) if n_pseudo else None

    real, null = [], []
    for name, (win, tr, kind) in targets.items():
        folds = contiguous_folds(len(tr), nf)
        y = _target_values(name, side, prior, pre, tr)
        experimenter = name in ("prior", "prev_side", "cur_side")
        for fs_name, (V, lag) in {**main, **dims}.items():
            F = Zw[win][tr] @ V
            score = r2_cv(F, y, folds, ridge_a) if kind == "r2" else auc_cv(F, y, folds, C)
            real.append({"feature_set": fs_name, "lag": lag, "variable": name, "metric": kind, "score": score})
            do_null = experimenter and n_pseudo and fs_name in main
            if do_null:
                yn = _target_values(name, sides_null, prior_null, pre, tr)          # (n_pseudo, n_sel)
                if kind == "r2":
                    sc = r2_cv(F, yn.T, folds, ridge_a)
                else:
                    sc = np.array([auc_cv(F, yn[b], folds, C) for b in range(n_pseudo)])
                null += [{"feature_set": fs_name, "lag": lag, "variable": name, "metric": kind,
                          "pseudo_id": b, "score": float(s)} for b, s in enumerate(sc)]
            # AUC gain over a prior-only model (secondary), for side variables on the main sets
            if name in ("cur_side", "prev_side") and fs_name in main:
                cov = prior[tr]
                real.append({"feature_set": fs_name, "lag": lag, "variable": f"{name}_gain", "metric": "auc_gain",
                             "score": _gain(F, y, cov, folds, C)})
                if n_pseudo and fs_name.startswith("rrr_"):
                    yn = _target_values(name, sides_null, prior_null, pre, tr)
                    pn = prior_null[:, tr]
                    null += [{"feature_set": fs_name, "lag": lag, "variable": f"{name}_gain", "metric": "auc_gain",
                              "pseudo_id": b, "score": float(_gain(F, yn[b], pn[b], folds, C))}
                             for b in range(n_pseudo)]

    # continuous-bin targets: wheel speed and elapsed time (no null; descriptive / drift probe)
    S = sqrt_counts(pre["counts"])
    Z = zs.transform(S)
    edges = pre["edges"]
    elapsed = 0.5 * (edges[:-1] + edges[1:]) - edges[0]
    cont = {"wheel_speed": pre["wheel_speed"], "elapsed_time": elapsed}
    for name, yv in cont.items():
        ok = np.asarray(pre["valid"], bool) & ~np.isnan(yv)
        if ok.sum() < 100:
            continue
        sel = np.flatnonzero(ok)
        folds = chunk_folds(len(sel), cfg["cv"]["n_chunks_continuous"], nf, cfg["cv"]["embargo_bins"])
        for fs_name, (V, lag) in main.items():
            real.append({"feature_set": fs_name, "lag": lag, "variable": name, "metric": "r2",
                         "score": r2_cv(Z[sel] @ V, yv[sel], folds, ridge_a)})
    return pd.DataFrame(real), pd.DataFrame(null)


# --------------------------------------------------------------------------- gate
def gate_session(pre: dict, cfg: dict, rng: np.random.Generator, n_pseudo: int) -> dict:
    """Full-population prior decoding (Lasso, nested interleaved CV) against the pseudo-session null."""
    mask = np.asarray(pre["mask"], bool)
    W = sqrt_counts(pre["win_pre_stim"])
    tr = np.flatnonzero(mask & ~np.any(np.isnan(W), axis=1))
    F = W[tr]
    y = pre["prior"][tr]
    Y = y[:, None]
    if n_pseudo:
        sides = np.stack([pseudo_sides(len(pre["side"]), rng)[1] for _ in range(n_pseudo)])
        Y = np.column_stack([y, bayes_optimal_prior(sides)[:, tr].T])
    r2 = lasso_nested_r2(F, Y, cfg["gate"]["n_folds"], rng)
    return {"r2": float(r2[0]), "null": r2[1:], **null_summary(float(r2[0]), r2[1:]), "n_trials": len(tr),
            "n_units": F.shape[1]}
