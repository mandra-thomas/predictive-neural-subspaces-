"""Amendment A14 helpers: amplitude-rate coupling, amplitude-corrected counts, early-concentration index.

All quantities live on the A13 30 s windows (pns.slowmode.window_edges). See AMENDMENTS.md, section A14.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats as sps

MIN_SPIKES_PER_WINDOW = 5
MIN_AMP_WINDOWS = 20
MIN_VALID_BINS = 30
SMOOTH_WINDOWS = 5
FACTOR_CLIP = (0.5, 2.0)


def window_index(t: np.ndarray, edges_w: np.ndarray) -> np.ndarray:
    return np.searchsorted(edges_w, t, side="right") - 1


def window_counts_exposure(counts, valid, t_bins, edges_w, bin_s):
    """Spike counts (windows x units) over valid bins, exposure in s; windows with < MIN_VALID_BINS valid bins NaN."""
    w = window_index(t_bins, edges_w)
    n_w = len(edges_w) - 1
    n = np.full((n_w, counts.shape[1]), np.nan)
    expo = np.zeros(n_w)
    for k in range(n_w):
        g = (w == k) & valid
        if g.sum() >= MIN_VALID_BINS:
            n[k] = counts[g].sum(0)
            expo[k] = g.sum() * bin_s
    return n, expo


def isolated_mask(unit_t, unit_idx, min_isi: float) -> np.ndarray:
    """True for spikes whose preceding spike of the same unit is at least min_isi earlier (first spikes kept)."""
    order = np.lexsort((unit_t, unit_idx))
    t, u = unit_t[order], unit_idx[order]
    prev_ok = np.ones(len(t), bool)
    same = u[1:] == u[:-1]
    prev_ok[1:] = ~same | (np.diff(t) >= min_isi)
    out = np.empty(len(t), bool)
    out[order] = prev_ok
    return out


def window_amplitudes(unit_t, unit_idx, unit_amp, n_units, edges_w):
    """Median spike amplitude per window and unit (NaN with < MIN_SPIKES_PER_WINDOW spikes)."""
    w = window_index(unit_t, edges_w)
    n_w = len(edges_w) - 1
    med = np.full((n_w, n_units), np.nan)
    ok = (w >= 0) & (w < n_w)
    df = pd.DataFrame({"w": w[ok], "u": unit_idx[ok], "a": unit_amp[ok]})
    g = df.groupby(["w", "u"])["a"]
    agg = pd.DataFrame({"med": g.median(), "n": g.size()}).reset_index()
    agg = agg[agg.n >= MIN_SPIKES_PER_WINDOW]
    med[agg.w.to_numpy(), agg.u.to_numpy()] = agg.med.to_numpy()
    return med


def relative_amplitude(med: np.ndarray) -> np.ndarray:
    with np.errstate(all="ignore"):
        return med / np.nanmedian(med, axis=0, keepdims=True) - 1.0


def smooth_fill(x: np.ndarray, k: int = SMOOTH_WINDOWS) -> np.ndarray:
    """Fill NaNs by linear interpolation (nearest at ends), then centred running median over k windows."""
    x = np.asarray(x, float)
    ok = np.isfinite(x)
    if ok.sum() == 0:
        return np.full_like(x, np.nan)
    i = np.arange(len(x))
    f = np.interp(i, i[ok], x[ok])
    s = pd.Series(f).rolling(k, center=True, min_periods=1).median().to_numpy()
    return s


def poisson_glm(y, X, offset, n_iter: int = 100, tol: float = 1e-8):
    """Poisson GLM with log link and offset, by IRLS. X should include an intercept column. Returns coefficients."""
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    beta = np.zeros(X.shape[1])
    beta[0] = np.log(max(y.sum(), 1e-3) / np.exp(offset).sum())
    for _ in range(n_iter):
        eta = np.clip(X @ beta + offset, -30, 30)
        mu = np.exp(eta)
        z = eta - offset + (y - mu) / np.maximum(mu, 1e-10)
        W = np.maximum(mu, 1e-10)
        XtW = X.T * W
        new = np.linalg.lstsq(XtW @ X + 1e-9 * np.eye(X.shape[1]), XtW @ z, rcond=None)[0]
        if np.max(np.abs(new - beta)) < tol:
            beta = new
            break
        beta = new
    return beta


def time_design(n_w: int, degree: int) -> np.ndarray:
    tau = np.linspace(-1, 1, n_w)
    return np.column_stack([tau ** k for k in range(1, degree + 1)]) if degree else np.empty((n_w, 0))


def coupling(n_win, expo, x_rel, degree: int) -> np.ndarray:
    """Amplitude coefficient per unit (NaN if < MIN_AMP_WINDOWS usable windows); degree = time-polynomial nuisance."""
    n_w, p = n_win.shape
    T = time_design(n_w, degree)
    out = np.full(p, np.nan)
    for u in range(p):
        ok = np.isfinite(n_win[:, u]) & np.isfinite(x_rel[:, u]) & (expo > 0)
        if ok.sum() < MIN_AMP_WINDOWS or np.std(x_rel[ok, u]) == 0:
            continue
        X = np.column_stack([np.ones(ok.sum()), x_rel[ok, u], T[ok]])
        out[u] = poisson_glm(n_win[ok, u], X, np.log(expo[ok]))[1]
    return out


def factors(x_smooth: np.ndarray, beta) -> np.ndarray:
    """Per window and unit multiplicative correction exp(-beta * x), clipped; NaN beta or x gives 1."""
    b = np.broadcast_to(np.asarray(beta, float), (x_smooth.shape[1],))
    with np.errstate(all="ignore"):
        f = np.exp(-b[None, :] * x_smooth)
    f = np.where(np.isfinite(f), f, 1.0)
    return np.clip(f, *FACTOR_CLIP)


def factor_at_times(f: np.ndarray, t: np.ndarray, edges_w: np.ndarray) -> np.ndarray:
    """Rows of f for arbitrary times (nearest window at the ends; NaN times give factor 1)."""
    w = np.clip(window_index(np.nan_to_num(t, nan=edges_w[0]), edges_w), 0, len(edges_w) - 2)
    out = f[w]
    out[~np.isfinite(t)] = 1.0
    return out


def third_changes(y: np.ndarray, min_n: int = 5) -> tuple[float, float]:
    """Theil-Sen slope x length in the first and last third of a window series."""
    parts = np.array_split(np.arange(len(y)), 3)
    res = []
    for idx in (parts[0], parts[2]):
        v = y[idx]
        ok = np.isfinite(v)
        if ok.sum() < min_n:
            return np.nan, np.nan
        res.append(float(sps.theilslopes(v[ok], idx[ok].astype(float)).slope) * len(idx))
    return res[0], res[1]


def early_index(y: np.ndarray, direction: float) -> float:
    d1, d3 = third_changes(np.asarray(y, float))
    if not (np.isfinite(d1) and np.isfinite(d3)):
        return np.nan
    d1, d3 = direction * d1, direction * d3
    den = abs(d1) + abs(d3)
    return (d1 - d3) / den if den > 0 else np.nan
