"""Spike binning: continuous bins over the task epoch and event-aligned trial windows."""
from __future__ import annotations

import numpy as np


def bin_edges(t0: float, t1: float, bin_s: float) -> np.ndarray:
    n = int(np.floor((t1 - t0) / bin_s + 1e-9))
    return t0 + bin_s * np.arange(n + 1)


def bin_spikes(times: np.ndarray, clusters: np.ndarray, n_units: int, edges: np.ndarray) -> np.ndarray:
    """Spike counts, shape (n_bins, n_units). Bins are [edge_k, edge_k+1)."""
    times = np.asarray(times)
    clusters = np.asarray(clusters, dtype=np.int64)
    n_bins = len(edges) - 1
    b = np.searchsorted(edges, times, side="right") - 1
    keep = (b >= 0) & (b < n_bins) & (clusters >= 0) & (clusters < n_units)
    flat = b[keep] * n_units + clusters[keep]
    return np.bincount(flat, minlength=n_bins * n_units).reshape(n_bins, n_units).astype(np.int32)


def window_counts(times: np.ndarray, clusters: np.ndarray, n_units: int, events: np.ndarray,
                  win: tuple[float, float]) -> np.ndarray:
    """Counts in [event + win[0], event + win[1]) per trial and unit, shape (n_trials, n_units).
    Trials whose event is NaN get a NaN row."""
    times = np.asarray(times)
    clusters = np.asarray(clusters, dtype=np.int64)
    events = np.asarray(events, dtype=float)
    out = np.full((len(events), n_units), np.nan)
    ok = ~np.isnan(events)
    lo, hi = events[ok] + win[0], events[ok] + win[1]
    order = np.lexsort((times, clusters))
    t_sorted, c_sorted = times[order], clusters[order]
    starts = np.searchsorted(c_sorted, np.arange(n_units), side="left")
    stops = np.searchsorted(c_sorted, np.arange(n_units), side="right")
    for u in range(n_units):
        tu = t_sorted[starts[u]:stops[u]]
        out[ok, u] = np.searchsorted(tu, hi, side="left") - np.searchsorted(tu, lo, side="left")
    return out


def bin_mean(t: np.ndarray, v: np.ndarray, edges: np.ndarray) -> np.ndarray:
    """Mean of v within each bin (NaN for empty bins)."""
    n_bins = len(edges) - 1
    b = np.searchsorted(edges, t, side="right") - 1
    keep = (b >= 0) & (b < n_bins) & ~np.isnan(v)
    s = np.bincount(b[keep], weights=v[keep], minlength=n_bins)
    c = np.bincount(b[keep], minlength=n_bins)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(c > 0, s / np.maximum(c, 1), np.nan)


def invalid_from_intervals(edges: np.ndarray, intervals: np.ndarray | None) -> np.ndarray:
    """Boolean (n_bins,) True where a bin overlaps any [start, stop) interval."""
    n_bins = len(edges) - 1
    bad = np.zeros(n_bins, bool)
    if intervals is None or len(intervals) == 0:
        return bad
    for a, b in np.asarray(intervals, dtype=float):
        if np.isnan(a) or np.isnan(b):
            continue
        bad |= (edges[:-1] < b) & (edges[1:] > a)
    return bad
