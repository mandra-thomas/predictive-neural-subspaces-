"""Square-root transform and per-unit z-scoring with explicit, reusable parameters.

Leakage rule: z-score parameters are fit on the bins that fit a model and stored with it; trial
windows are always transformed with those stored parameters, never re-z-scored.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

SD_FLOOR = 1e-3


def sqrt_counts(counts: np.ndarray) -> np.ndarray:
    return np.sqrt(np.asarray(counts, dtype=float))


@dataclass
class ZScore:
    mu: np.ndarray
    sd: np.ndarray

    @classmethod
    def fit(cls, X: np.ndarray) -> "ZScore":
        mu = np.nanmean(X, axis=0)
        sd = np.maximum(np.nanstd(X, axis=0), SD_FLOOR)
        return cls(mu, sd)

    def transform(self, X: np.ndarray) -> np.ndarray:
        return (X - self.mu) / self.sd
