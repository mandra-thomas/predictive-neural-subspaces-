"""Slow-mode helpers for the drift-versus-state pilots (amendments A12 and A13).

The slow mode is the first basis column of the full-session longest-lag readout subspace; its time course is the
z-scored sqrt-count activity projected on it, averaged in non-overlapping 30 s windows (60 bins of 0.5 s),
with the sign fixed so that it increases with elapsed time. These definitions mirror scripts/11_pilot_state.py.
"""
from __future__ import annotations

import numpy as np
from scipy import stats as sps

WIN_S = 30.0


def window_edges(pre: dict) -> np.ndarray:
    edges = pre["edges"]
    tc = 0.5 * (edges[:-1] + edges[1:])
    valid = np.asarray(pre["valid"], bool)
    t0 = tc[valid][0]
    return t0 + np.arange(0, (tc[valid][-1] - t0) + WIN_S + 1e-9, WIN_S)


def bin_centres(pre: dict) -> np.ndarray:
    e = pre["edges"]
    return 0.5 * (e[:-1] + e[1:])


def window_means(t_bins, x_bins, ok_bins, edges_w, min_bins: int = 30):
    """Mean over bins in each window (x may be 1-D or 2-D bins x features); NaN with fewer than min_bins usable."""
    x = np.asarray(x_bins, float)
    idx = np.searchsorted(edges_w, t_bins, side="right") - 1
    n_w = len(edges_w) - 1
    out = np.full((n_w,) + x.shape[1:], np.nan)
    for w in range(n_w):
        good = (idx == w) & ok_bins
        if good.sum() >= min_bins:
            out[w] = x[good].mean(0)
    return out


def slow_direction(fits: dict, long_lag: int) -> np.ndarray:
    v = np.asarray(fits[f"Vin_full_{long_lag}"])[:, 0]
    return v / np.linalg.norm(v)


def slow_mode(pre: dict, fits: dict, S: np.ndarray, long_lag: int) -> tuple[np.ndarray, np.ndarray, float]:
    """Window time course of the slow mode, the sign-aligned loading vector, and the sign used (+1 or -1)."""
    v = slow_direction(fits, long_lag)
    Z = (S - fits["z_mu"]) / fits["z_sd"]
    s = Z @ v
    ew = window_edges(pre)
    sw = window_means(bin_centres(pre), s, np.asarray(pre["valid"], bool), ew)
    tw = np.arange(len(sw), dtype=float)
    ok = np.isfinite(sw)
    sign = 1.0 if np.corrcoef(sw[ok], tw[ok])[0, 1] >= 0 else -1.0
    return sign * sw, sign * v, sign


def event_windows(times: np.ndarray, values: np.ndarray, edges_w: np.ndarray) -> np.ndarray:
    """Mean of per-event values whose event time falls in each window (NaN if none)."""
    idx = np.searchsorted(edges_w, times, side="right") - 1
    out = np.full(len(edges_w) - 1, np.nan)
    for w in range(len(out)):
        v = values[(idx == w) & np.isfinite(values)]
        if len(v):
            out[w] = v.mean()
    return out


def residualize_quadratic(y: np.ndarray) -> np.ndarray:
    """Residual of y after a least-squares quadratic in window index (NaNs kept)."""
    y = np.asarray(y, float)
    t = np.arange(len(y), dtype=float)
    ok = np.isfinite(y)
    out = np.full_like(y, np.nan)
    if ok.sum() >= 5:
        b = np.polyfit(t[ok], y[ok], 2)
        out[ok] = y[ok] - np.polyval(b, t[ok])
    return out


def corr_aligned(a: np.ndarray, b: np.ndarray, absolute: bool = True, min_n: int = 10) -> float:
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < min_n or np.std(a[ok]) == 0 or np.std(b[ok]) == 0:
        return np.nan
    r = float(np.corrcoef(a[ok], b[ok])[0, 1])
    return abs(r) if absolute else r


def spearman(a, b) -> float:
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 5:
        return np.nan
    return float(sps.spearmanr(np.asarray(a)[ok], np.asarray(b)[ok]).statistic)
