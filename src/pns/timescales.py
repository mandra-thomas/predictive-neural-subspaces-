"""Amendment A17 (post hoc): timescales of the task and of the block prior, and an importable detrend.

Part 0 uses task data only (trial times, block probabilities, the Bayes-optimal prior); no neural data.

prior_per_bin: prior[t] is P(left on trial t | sides before t), the belief *before* stimulus t. It is assigned to the
bins whose centres fall in (stimOn[t-1], stimOn[t]] (np.searchsorted(stimOn, centre, side="left")), so the
pre-stimulus bins of trial t carry prior[t], matching the decoder target. Trials with NaN stimOn are dropped.

detrend_pre reproduces scripts/21_build_detrend.py (A16) in memory, so A17/A18 code never has to run script 21
(which writes cwd-relative data folders).
"""
from __future__ import annotations

import numpy as np

from .transform import sqrt_counts

MIN_PERIOD_MIN = 20.0


# ----------------------------------------------------------------------------- task timescales
def bin_centres(pre: dict) -> np.ndarray:
    e = np.asarray(pre["edges"], float)
    return 0.5 * (e[:-1] + e[1:])


def block_runs(p_left: np.ndarray) -> list[tuple[int, int, float]]:
    """Runs of equal block probability as (start, stop_exclusive, value)."""
    p = np.asarray(p_left, float)
    runs, s = [], 0
    for i in range(1, len(p) + 1):
        if i == len(p) or p[i] != p[s]:
            runs.append((s, i, float(p[s])))
            s = i
    return runs


def completed_blocks(p_left: np.ndarray) -> list[tuple[int, int, float]]:
    """Biased blocks that are complete: drop the unbiased (0.5) opening block(s) and the final, truncated block."""
    runs = block_runs(p_left)
    if runs:
        runs = runs[:-1]                     # last block is cut off by the session end
    return [r for r in runs if r[2] != 0.5]


def session_timescales(pre: dict) -> dict:
    """Session duration, stimulus interval and completed-block durations (trials and minutes)."""
    e = np.asarray(pre["edges"], float)
    st = np.asarray(pre["stimOn_times"], float)
    pl = np.asarray(pre["probabilityLeft"], float)
    blocks = completed_blocks(pl)
    n_trials = np.array([b - a for a, b, _ in blocks], float)
    dur = []
    for a, b, _ in blocks:
        t0 = st[a]
        t1 = st[b] if b < len(st) else np.nan     # start of the next block
        dur.append((t1 - t0) / 60.0 if np.isfinite(t0) and np.isfinite(t1) else np.nan)
    return {
        "duration_min": float((e[-1] - e[0]) / 60.0),
        "stim_interval_s": float(np.nanmedian(np.diff(st))),
        "n_blocks": len(blocks),
        "block_trials": n_trials,
        "block_min": np.asarray(dur, float),
    }


def trial_index_per_bin(pre: dict) -> tuple[np.ndarray, np.ndarray]:
    """For each bin, the index (into the full trial arrays) of the next valid stimulus onset at or after the bin
    centre, i.e. the trial whose pre-stimulus belief the bin carries; and a mask of bins that have one."""
    c = bin_centres(pre)
    st = np.asarray(pre["stimOn_times"], float)
    ok_idx = np.flatnonzero(np.isfinite(st))
    st_ok = st[ok_idx]
    k = np.searchsorted(st_ok, c, side="left")
    inside = (k < len(st_ok)) & (c > st_ok[0])
    idx = np.zeros(len(c), int)
    idx[inside] = ok_idx[k[inside]]
    return idx, inside


def prior_per_bin(pre: dict, prior: np.ndarray | None = None) -> np.ndarray:
    """Bayes-optimal prior per 0.5 s bin (NaN before the first and after the last valid stimulus onset).
    `prior` may be (n_trials,) or (m, n_trials) (e.g. pseudo-session priors); default pre["prior"]."""
    pr = np.asarray(pre["prior"] if prior is None else prior, float)
    idx, inside = trial_index_per_bin(pre)
    out = np.full(pr.shape[:-1] + (len(inside),), np.nan)
    out[..., inside] = pr[..., idx[inside]]
    return out


def acf(x: np.ndarray, lags_bins) -> np.ndarray:
    """NaN-aware autocorrelation: Pearson correlation of (x_t, x_{t+lag}) over pairs where both are finite."""
    x = np.asarray(x, float)
    out = []
    for lag in lags_bins:
        lag = int(lag)
        if lag == 0:
            out.append(1.0)
            continue
        a, b = x[:-lag], x[lag:]
        m = np.isfinite(a) & np.isfinite(b)
        out.append(float(np.corrcoef(a[m], b[m])[0, 1]) if m.sum() > 2 else np.nan)
    return np.asarray(out)


def integrated_timescale(x: np.ndarray, bin_s: float, max_lag_bins: int) -> tuple[float, float]:
    """Integrated autocorrelation time, truncated at the first zero crossing (trapezoid from lag 0).
    Returns (tau_s, first_zero_crossing_s). For rho = exp(-t/tau) this returns approximately tau."""
    r = acf(x, range(0, max_lag_bins + 1))
    neg = np.where(r <= 0)[0]
    k0 = int(neg[0]) if len(neg) else len(r)
    tau = bin_s * (np.sum(r[:k0]) - 0.5 * r[0])
    return float(tau), float(k0 * bin_s)


# ----------------------------------------------------------------------------- detrend (copy of A16 script 21)
def cosine_design(t_min: np.ndarray, t0: float, length: float, min_period: float = MIN_PERIOD_MIN) -> np.ndarray:
    """Cosine basis on the task epoch with periods of at least `min_period` minutes (as scripts/21_build_detrend.py)."""
    u = (np.asarray(t_min, float) - t0) / length
    kmax = int(np.floor(2 * length / min_period))
    return np.column_stack([np.cos(np.pi * k * u) for k in range(1, kmax + 1)])


def quad_design(t_min: np.ndarray, t0: float, length: float) -> np.ndarray:
    u = (np.asarray(t_min, float) - t0) / length
    return np.column_stack([u, u ** 2])


def design(t_min, kind: str, t0: float, length: float) -> np.ndarray:
    return quad_design(t_min, t0, length) if kind == "q" else cosine_design(t_min, t0, length)


def epoch_minutes(pre: dict) -> tuple[np.ndarray, np.ndarray, float, float]:
    """Bin-centre times in minutes, the valid mask, and (t0, length) of the valid epoch, as in script 21."""
    tc = bin_centres(pre) / 60.0
    valid = np.asarray(pre["valid"], bool)
    t0, length = tc[valid][0], tc[valid][-1] - tc[valid][0]
    return tc, valid, float(t0), float(length)


def detrend_pre(pre: dict, cfg: dict, kind: str) -> dict:
    """Return a copy of `pre` with S_resid, Swin_resid_* and detrend_r2, identical to scripts/21_build_detrend.py."""
    pre = dict(pre)
    tc, valid, t0, length = epoch_minutes(pre)
    S = sqrt_counts(pre["counts"])
    D = design(tc, kind, t0, length)
    dm, sm = D[valid].mean(0), S[valid].mean(0)
    Dc, Sc = D[valid] - dm, S[valid] - sm
    beta = np.linalg.lstsq(Dc, Sc, rcond=None)[0]
    pre["S_resid"] = S - (D - dm) @ beta
    for name, spec in cfg["windows"].items():
        ev = (np.asarray(pre[spec["event"]], float) + 0.5 * (spec["win"][0] + spec["win"][1])) / 60.0
        W = sqrt_counts(pre[f"win_{name}"])
        ok = np.isfinite(ev)
        Dw = np.zeros((len(ev), D.shape[1]))
        Dw[ok] = design(ev[ok], kind, t0, length)
        pre[f"Swin_resid_{name}"] = W - (Dw - dm) @ beta
    pre["detrend_r2"] = float(1 - np.sum((Sc - Dc @ beta) ** 2) / np.sum(Sc ** 2))
    return pre


def span_fraction(y: np.ndarray, D: np.ndarray) -> float:
    """Fraction of the variance of y (finite entries) explained by the columns of D (both centred)."""
    m = np.isfinite(y) & np.all(np.isfinite(D), axis=1)
    yc = y[m] - y[m].mean()
    Dc = D[m] - D[m].mean(0)
    beta = np.linalg.lstsq(Dc, yc, rcond=None)[0]
    return float(1 - np.sum((yc - Dc @ beta) ** 2) / np.sum(yc ** 2))


def prior_cosine_fraction(pre: dict) -> float:
    """Fraction of the per-bin prior's variance that lies in the >= 20 min cosine span (removed by the A16 detrend)."""
    tc, valid, t0, length = epoch_minutes(pre)
    x = prior_per_bin(pre)
    x[~valid] = np.nan
    return span_fraction(x, cosine_design(tc, t0, length))


# ----------------------------------------------------------------------------- variance shares (A17 part 1)
def signed_event_design(times: np.ndarray, ev_times: np.ndarray, weights: np.ndarray,
                        span=(-1.0, 2.0), n_basis: int = 8) -> np.ndarray:
    """(len(times), n_basis): raised-cosine responses to each event, each scaled by its weight (e.g. side x
    sqrt(contrast)); same basis as the A11 trial-locked GLM (pipeline._raised_cosines)."""
    from .pipeline import _raised_cosines
    ev = np.asarray(ev_times, float)
    w = np.asarray(weights, float)
    ok = np.isfinite(ev) & np.isfinite(w)
    order = np.argsort(ev[ok])
    ev, w = ev[ok][order], w[ok][order]
    D = np.zeros((len(times), n_basis))
    lo = np.searchsorted(ev, times - span[1], side="left")
    hi = np.searchsorted(ev, times - span[0], side="right")
    for k in range(len(times)):
        if hi[k] > lo[k]:
            D[k] += (w[lo[k]:hi[k], None] * _raised_cosines(times[k] - ev[lo[k]:hi[k]], span, n_basis)).sum(0)
    return D


def event_design_full(pre: dict, times: np.ndarray) -> np.ndarray:
    """Unsigned A11 event kernels (stimOn, firstMovement, feedback) plus kernels signed by side x sqrt(contrast),
    choice and feedback outcome."""
    from .pipeline import EVENTS, _event_design
    events = {e: np.asarray(pre[e], float) for e in EVENTS}
    side = np.asarray(pre["side"], float)
    contrast = np.nan_to_num(np.asarray(pre["contrast"], float), nan=0.0)
    signed = [signed_event_design(times, pre["stimOn_times"], side * np.sqrt(contrast)),
              signed_event_design(times, pre["firstMovement_times"], np.asarray(pre["choice"], float)),
              signed_event_design(times, pre["feedback_times"], np.asarray(pre["feedbackType"], float))]
    return np.hstack([_event_design(times, events)] + signed)


def residualize(A: np.ndarray, D: np.ndarray | None) -> np.ndarray:
    """A minus its least-squares projection on [1, D] (columns of A treated separately)."""
    ones = np.ones((len(A), 1))
    X = ones if D is None else np.hstack([ones, D])
    return A - X @ np.linalg.lstsq(X, A, rcond=None)[0]


def population_share(W: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Share of the summed variance of the (already residualized) columns of W explained by each single regressor
    column of X (also residualized): sum_u (x'w_u)^2/(x'x) / sum_u w_u'w_u. Returns one value per column of X."""
    expl = ((X.T @ W) ** 2).sum(1) / np.sum(X ** 2, axis=0)
    return expl / np.sum(W ** 2)


def lowfreq_share(Z: np.ndarray, D: np.ndarray) -> float:
    """In-sample share of the summed variance of Z explained by the design D (plus intercept)."""
    Zc = Z - Z.mean(0)
    return float(1 - np.sum(residualize(Z, D) ** 2) / np.sum(Zc ** 2))
