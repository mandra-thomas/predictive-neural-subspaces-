"""Lagged sample pairs, session halves and purged contiguous cross-validation folds."""
from __future__ import annotations

import numpy as np


def session_halves(T: int, gap: int) -> np.ndarray:
    """Segment id per bin: 0 = first half, 1 = second half, -1 = the gap discarded between them."""
    seg = np.full(T, -1, dtype=int)
    mid = T // 2
    seg[: max(mid - gap // 2, 0)] = 0
    seg[min(mid + (gap - gap // 2), T):] = 1
    return seg


def lagged_pairs(T: int, lag: int, valid: np.ndarray | None = None,
                 segment: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Indices (i, j = i + lag) with both bins valid and inside the same (non-negative) segment."""
    i = np.arange(max(T - lag, 0))
    j = i + lag
    keep = np.ones(len(i), bool)
    if valid is not None:
        keep &= valid[i] & valid[j]
    if segment is not None:
        keep &= (segment[i] == segment[j]) & (segment[i] >= 0)
    return i[keep], j[keep]


def purged_folds(i: np.ndarray, j: np.ndarray, n_folds: int, embargo: int,
                 span: tuple[int, int] | None = None) -> list[tuple[np.ndarray, np.ndarray]]:
    """Contiguous-block CV over lagged pairs (i -> j).

    The time span [lo, hi) is split into n_folds contiguous blocks. For block k:
      test  = pairs with BOTH ends inside the block,
      train = pairs with NEITHER end inside [block_start - embargo, block_end + embargo).
    Returns a list of (train_idx, test_idx) indexing into the pair arrays.
    """
    lo, hi = span if span is not None else (int(i.min()), int(j.max()) + 1)
    bounds = np.linspace(lo, hi, n_folds + 1).round().astype(int)
    folds = []
    for k in range(n_folds):
        s, e = bounds[k], bounds[k + 1]
        test = (i >= s) & (i < e) & (j >= s) & (j < e)
        a, b = s - embargo, e + embargo
        touch = ((i >= a) & (i < b)) | ((j >= a) & (j < b))
        folds.append((np.flatnonzero(~touch), np.flatnonzero(test)))
    return folds


def chunk_folds(n: int, n_chunks: int, n_folds: int, embargo: int) -> list[tuple[np.ndarray, np.ndarray]]:
    """Samples split into n_chunks contiguous chunks, assigned round-robin to folds; training excludes
    samples within `embargo` of any test chunk. Used for continuous targets (elapsed time, wheel)."""
    bounds = np.linspace(0, n, n_chunks + 1).round().astype(int)
    idx = np.arange(n)
    folds = []
    for k in range(n_folds):
        test = np.zeros(n, bool)
        near = np.zeros(n, bool)
        for c in range(k, n_chunks, n_folds):
            s, e = bounds[c], bounds[c + 1]
            test[s:e] = True
            near[max(s - embargo, 0):min(e + embargo, n)] = True
        folds.append((idx[~near], idx[test]))
    return folds


def contiguous_folds(n: int, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    bounds = np.linspace(0, n, n_folds + 1).round().astype(int)
    idx = np.arange(n)
    return [(np.r_[idx[: bounds[k]], idx[bounds[k + 1]:]], idx[bounds[k]: bounds[k + 1]]) for k in range(n_folds)]


def interleaved_folds(n: int, n_folds: int, rng: np.random.Generator) -> list[tuple[np.ndarray, np.ndarray]]:
    perm = rng.permutation(n)
    parts = np.array_split(perm, n_folds)
    return [(np.sort(np.concatenate(parts[:k] + parts[k + 1:])), np.sort(parts[k])) for k in range(n_folds)]
