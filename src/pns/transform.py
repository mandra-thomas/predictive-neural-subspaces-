"""Square-root transform and per-unit z-scoring with explicit, reusable parameters.

Leakage rule: z-score parameters are fit on the bins that fit a model and stored with it; trial
windows are always transformed with those stored parameters, never re-z-scored.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

def poisson_sqrt_sd(rate_hz: float, bin_s: float, kmax: int = 50) -> float:
    """SD of sqrt(count) for a Poisson unit firing at rate_hz in bins of bin_s seconds."""
    from scipy.stats import poisson
    k = np.arange(kmax)
    pk = poisson.pmf(k, rate_hz * bin_s)
    m1 = np.sum(np.sqrt(k) * pk)
    return float(np.sqrt(np.sum(k * pk) - m1 ** 2))


# Amendment D10: the SD floor equals the SD of a unit firing exactly at the inclusion threshold
# (binning.min_rate_hz = 0.1 Hz, bin_s = 0.5 s; tests/test_config.py checks they agree), so it binds only
# for units that are below inclusion within the fitting bins. The original 1e-3 floor let a unit that is
# silent across a training fold but active in its test fold reach z-variance ~1e5 and swamp pooled R^2.
SD_FLOOR = poisson_sqrt_sd(0.1, 0.5)


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
