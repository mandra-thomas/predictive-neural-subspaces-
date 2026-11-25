"""Amendment A18 (post hoc): calibrated simulation of a block prior competing with slow drift.

Shared by scripts/26_sim_A18.py and its tests. Two entry points:

  calibration_stats(pre, cfg, side_null, prior_null)
      Statistics that set and check the simulator's free gains. Computed identically on real and simulated sessions.
  analyse_session(pre, cfg, side_null, prior_null, fit_rng, truth=None)
      The real pipeline on one session: pns.pipeline.fit_session (registered lags, alpha grid, folds, z-scoring),
      then prior decoding exactly as decode_session does it for the prior target (pre-stimulus windows, ridge with
      contiguous folds, the same pseudo-session construction), for every rank-5 subspace, PCA, the covariance-matched
      random subspace and the full population. Adds a history-controlled prior score, elapsed-time and current-side
      decoding per subspace, and, when the ground truth is known, how much of the true prior direction each subspace
      contains.
"""
from __future__ import annotations

import numpy as np

from .decode import auc_cv, r2_cv
from .lagged import chunk_folds, contiguous_folds
from .pipeline import _trial_targets, fit_session, residualize_session, session_S, window_S
from .prior import bayes_optimal_prior, pseudo_sides
from .synth import DT
from .timescales import cosine_design, epoch_minutes, lowfreq_share, population_share, residualize
from .transform import ZScore

N_PSEUDO = 200
HIST_K = 5          # history-controlled score: the previous HIST_K stimulus sides are regressed out of the target
D = 5


def pseudo_priors(n_trials: int, rng: np.random.Generator, n_pseudo: int = N_PSEUDO):
    """Pseudo-session sides and priors, drawn exactly as scripts 05 and 22 draw them."""
    sides = np.stack([pseudo_sides(n_trials, rng)[1] for _ in range(n_pseudo)])
    return sides, bayes_optimal_prior(sides)


def history_design(side: np.ndarray, tr: np.ndarray, k: int = HIST_K) -> np.ndarray:
    """(len(tr), k): side of trials tr-1 ... tr-k (zero before the first trial)."""
    side = np.asarray(side, float)
    out = np.zeros((len(tr), k))
    for j in range(1, k + 1):
        ok = tr - j >= 0
        out[ok, j - 1] = side[tr[ok] - j]
    return out


def history_residual_targets(Y: np.ndarray, sides: np.ndarray, tr: np.ndarray) -> np.ndarray:
    """Columns of Y (real target first, then pseudo targets), each minus its least-squares fit on [1, its own
    previous HIST_K sides]. Uses the target's own sides only, never neural data."""
    out = np.empty_like(Y)
    for c in range(Y.shape[1]):
        out[:, c] = residualize(Y[:, [c]], history_design(sides[c], tr))[:, 0]
    return out


def corrected(sc: np.ndarray) -> float:
    return float(sc[0] - np.median(sc[1:]))


def _z(pre):
    S = session_S(pre)
    valid = np.asarray(pre["valid"], bool)
    zs = ZScore.fit(S[valid])
    return zs, zs.transform(S), valid


# ----------------------------------------------------------------------------- calibration statistics
def calibration_stats(pre: dict, cfg: dict, side_null: np.ndarray, prior_null: np.ndarray) -> dict:
    zs, Z, valid = _z(pre)
    tc, _, t0, length = epoch_minutes(pre)
    nf, ridge_a, C = cfg["cv"]["n_folds"], cfg["decode"]["ridge_alpha"], cfg["decode"]["C"]
    out = {"n_units": int(Z.shape[1]), "T": int(len(Z))}
    low = lowfreq_share(Z[valid], cosine_design(tc[valid], t0, length))
    out["lowfreq_cos"] = low
    out["midband"] = lowfreq_share(Z[valid], cosine_design(tc[valid], t0, length, min_period=5.0)) - low
    Zr = zs.transform(residualize_session(pre, cfg)["S_resid"])
    out["triallocked"] = float(1 - np.sum((Zr[valid] - Zr[valid].mean(0)) ** 2)
                               / np.sum((Z[valid] - Z[valid].mean(0)) ** 2))
    ev = np.sort(np.linalg.eigvalsh(np.cov(Z[valid].T)))[::-1]
    out["pc1_frac"], out["pc5_frac"] = float(ev[0] / ev.sum()), float(ev[:D].sum() / ev.sum())

    targets = _trial_targets(pre, cfg)
    side, prior = np.asarray(pre["side"], float), np.asarray(pre["prior"], float)
    win, tr, _ = targets["prior"]
    W = zs.transform(window_S(pre, win))[tr]
    folds = contiguous_folds(len(tr), nf)
    Y = np.column_stack([prior[tr], prior_null[:, tr].T])
    out["full_prior_corr"] = corrected(r2_cv(W, Y, folds, ridge_a))
    Yh = history_residual_targets(Y, np.vstack([side[None], side_null]), tr)
    out["full_prior_hist_corr"] = corrected(r2_cv(W, Yh, folds, ridge_a))
    # A17 part 1 primary prior share (pre-stimulus windows, cosine span removed), pseudo-corrected
    spec = cfg["windows"][win]
    tw = (np.asarray(pre[spec["event"]], float)[tr] + 0.5 * sum(spec["win"])) / 60.0
    Dw = cosine_design(tw, t0, length)
    sh = population_share(residualize(W, Dw), residualize(Y, Dw))
    out["prior_trial_share_corr"] = corrected(sh)

    win, tr2, _ = targets["prev_side"]
    W2 = zs.transform(window_S(pre, win))[tr2]
    out["full_prev_side_auc"] = auc_cv(W2, side[tr2 - 1], contiguous_folds(len(tr2), nf), C)
    win, tr3, _ = targets["cur_side"]
    W3 = zs.transform(window_S(pre, win))[tr3]
    out["full_cur_side_auc"] = auc_cv(W3, side[tr3], contiguous_folds(len(tr3), nf), C)
    return out


# ----------------------------------------------------------------------------- subspace analysis
def _orth(V):
    q, _ = np.linalg.qr(V)
    return q


def _capture(V, u):
    u = u / np.linalg.norm(u)
    return float(np.sum((_orth(V).T @ u) ** 2))


def true_prior_per_bin(pre: dict, truth: dict) -> np.ndarray:
    """The simulated prior at each 0.5 s bin centre (ground truth, from the simulator's own trial assignment)."""
    edges = np.asarray(pre["edges"], float)
    centres = 0.5 * (edges[:-1] + edges[1:])
    k = np.clip(np.round(centres / DT).astype(int), 0, len(truth["trial_of_t"]) - 1)
    return np.asarray(truth["prior"], float)[truth["trial_of_t"][k]]


def analyse_session(pre: dict, cfg: dict, side_null: np.ndarray, prior_null: np.ndarray,
                    fit_rng: np.random.Generator, truth: dict | None = None) -> dict:
    fits, _, _, meta = fit_session(pre, cfg, D, fit_rng)
    zs = ZScore(fits["z_mu"], fits["z_sd"])
    nf, ridge_a, C = cfg["cv"]["n_folds"], cfg["decode"]["ridge_alpha"], cfg["decode"]["C"]
    lags = [int(x) for x in fits["lags"]]
    p = len(fits["z_mu"])
    sets = {f"rrr_{lag}": fits[f"Vin_full_{lag}"] for lag in lags}
    sets.update(pca=fits["V_pca"], random=fits["V_random"], full=np.eye(p))
    out = {"alpha": float(meta["alpha"]), "p": p, "T": int(meta["T"])}

    targets = _trial_targets(pre, cfg)
    side, prior = np.asarray(pre["side"], float), np.asarray(pre["prior"], float)
    win, tr, _ = targets["prior"]
    Zw = zs.transform(window_S(pre, win))[tr]
    folds = contiguous_folds(len(tr), nf)
    Y = np.column_stack([prior[tr], prior_null[:, tr].T])
    Yh = history_residual_targets(Y, np.vstack([side[None], side_null]), tr)
    raw = {}
    for name, V in sets.items():
        F = Zw @ V
        sc, sch = r2_cv(F, Y, folds, ridge_a), r2_cv(F, Yh, folds, ridge_a)
        raw[name] = sc
        out[f"prior_{name}"] = corrected(sc)
        out[f"prior_{name}_raw"] = float(sc[0])
        out[f"priorhist_{name}"] = corrected(sch)
    short, long_ = f"rrr_{lags[0]}", f"rrr_{lags[-1]}"
    dn = raw[long_][1:] - raw[short][1:]
    out["p2_change"] = float((raw[long_][0] - raw[short][0]) - np.median(dn))      # paired-null, as P2

    win, tr3, _ = targets["cur_side"]
    Z3 = zs.transform(window_S(pre, win))[tr3]
    f3 = contiguous_folds(len(tr3), nf)
    S = session_S(pre)
    Z = zs.transform(S)
    edges = pre["edges"]
    elapsed = 0.5 * (edges[:-1] + edges[1:]) - edges[0]
    sel = np.flatnonzero(np.asarray(pre["valid"], bool))
    fe = chunk_folds(len(sel), cfg["cv"]["n_chunks_continuous"], nf, cfg["cv"]["embargo_bins"])
    for name, V in sets.items():
        if name == "full":
            continue
        out[f"cur_side_{name}"] = auc_cv(Z3 @ V, side[tr3], f3, C)
        out[f"elapsed_{name}"] = r2_cv(Z[sel] @ V, elapsed[sel], fe, ridge_a)

    if truth is not None:
        x = true_prior_per_bin(pre, truth)[sel]
        xc = x - x.mean()
        g = (Z[sel] - Z[sel].mean(0)).T @ xc / (xc @ xc)                # true prior loading, z-scored units
        Cz = np.cov(Z[sel].T)
        w = np.linalg.solve(Cz + 1e-6 * np.eye(p), g)                    # its optimal linear readout direction
        out["chance_capture"] = D / p
        for name, V in sets.items():
            if name == "full":
                continue
            out[f"capture_in_{name}"] = _capture(V, w)
        for lag in lags:
            out[f"capture_out_rrr_{lag}"] = _capture(fits[f"Vout_full_{lag}"], g)
    return out


# ----------------------------------------------------------------------------- A18 part B: latent model on simulations
def lds_inputs(pre: dict, cfg: dict, tr: np.ndarray) -> np.ndarray:
    """Known inputs per trial: the >= 20 min cosine basis of the pre-stimulus window time (explicit drift term) and the
    previous trial's side, choice and reward (0 for the first trial)."""
    tc, _, t0, length = epoch_minutes(pre)
    spec = cfg["windows"]["pre_stim"]
    tw = (np.asarray(pre[spec["event"]], float)[tr] + 0.5 * sum(spec["win"])) / 60.0
    prev = []
    for key in ("side", "choice", "feedbackType"):
        v = np.nan_to_num(np.asarray(pre[key], float), nan=0.0)
        prev.append(np.where(tr > 0, v[np.maximum(tr - 1, 0)], 0.0))
    return np.column_stack([cosine_design(tw, t0, length), *prev])


def lds_readout(pre: dict, cfg: dict, side_null: np.ndarray, prior_null: np.ndarray, rng: np.random.Generator,
                K: int = 8, n_restarts: int = 3, max_iter: int = 300) -> dict:
    """Fit the trial-indexed latent model to the pre-stimulus windows of every trial with a valid window, then decode
    the prior from each trial's instantaneous latent estimate (no filtering across trials), exactly as the subspace
    scores are decoded (ridge, contiguous folds, the same pseudo sessions)."""
    from .lds import fit_lds, instantaneous_scores
    from .timescales import integrated_timescale
    W = window_S(pre, "pre_stim")
    rows = np.flatnonzero(~np.any(np.isnan(W), axis=1))
    Y = W[rows]
    Y = (Y - Y.mean(0)) / np.where(Y.std(0) > 1e-9, Y.std(0), 1.0)
    U = lds_inputs(pre, cfg, rows)
    fit = fit_lds(Y, U, K, n_restarts=n_restarts, max_iter=max_iter, rng=rng)
    Zs = instantaneous_scores(Y, U, fit.params)
    tau = fit.params.tau()
    side, prior = np.asarray(pre["side"], float), np.asarray(pre["prior"], float)
    tau_pi = integrated_timescale(prior[rows], 1.0, 300)[0]
    band = (tau >= tau_pi / 3) & (tau <= 3 * tau_pi)
    _, tr, _ = _trial_targets(pre, cfg)["prior"]
    pos = np.searchsorted(rows, tr)
    folds = contiguous_folds(len(tr), cfg["cv"]["n_folds"])
    Ytar = np.column_stack([prior[tr], prior_null[:, tr].T])
    ra = cfg["decode"]["ridge_alpha"]
    out = {"lds_converged": bool(fit.converged), "lds_tau": [float(x) for x in tau], "tau_pi_trials": float(tau_pi),
           "lds_n_band": int(band.sum()), "lds_restart_ll_spread": float(np.ptp(fit.restart_lls)),
           "lds_all": corrected(r2_cv(Zs[pos], Ytar, folds, ra))}
    out["lds_band"] = corrected(r2_cv(Zs[pos][:, band], Ytar, folds, ra)) if band.any() else np.nan
    return out
