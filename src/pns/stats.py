"""Null summaries, animal-level paired tests, multiplicity control and bootstrap intervals."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats as sps


def null_summary(real: float, null: np.ndarray) -> dict:
    """Real score against its pseudo-session null. p is one-sided (real larger than null)."""
    null = np.asarray(null, dtype=float)
    null = null[~np.isnan(null)]
    if len(null) == 0 or np.isnan(real):
        return {"corrected": np.nan, "percentile": np.nan, "z": np.nan, "p": np.nan}
    sd = null.std(ddof=1)
    return {"corrected": float(real - np.median(null)),
            "percentile": float(np.mean(null < real)),
            "z": float((real - null.mean()) / sd) if sd > 0 else np.nan,
            "p": float((1 + np.sum(null >= real)) / (1 + len(null)))}


def animal_mean(df: pd.DataFrame, value: str, keys: list[str], subject_col: str = "subject") -> pd.DataFrame:
    """Average sessions within each animal (per condition keys) before testing across animals."""
    return df.groupby([subject_col] + keys, as_index=False)[value].mean()


def wilcoxon_greater(diff: np.ndarray) -> dict:
    """One-sided paired Wilcoxon signed-rank test of median(diff) > 0 (exact for small n, no ties)."""
    diff = np.asarray(diff, dtype=float)
    diff = diff[~np.isnan(diff)]
    n = len(diff)
    if n < 2 or np.all(diff == 0):
        return {"n": n, "stat": np.nan, "p": np.nan, "median": float(np.median(diff)) if n else np.nan}
    res = sps.wilcoxon(diff, alternative="greater")
    return {"n": n, "stat": float(res.statistic), "p": float(res.pvalue), "median": float(np.median(diff))}


def min_attainable_p(n: int) -> float:
    """Smallest exact one-sided Wilcoxon p-value with n pairs."""
    return 1.0 / 2 ** n


def holm(pvals: dict[str, float]) -> dict[str, float]:
    """Holm-adjusted p-values (step-down, monotone)."""
    keys = [k for k in pvals if not np.isnan(pvals[k])]
    order = sorted(keys, key=lambda k: pvals[k])
    m = len(order)
    adj, running = {}, 0.0
    for r, k in enumerate(order):
        running = max(running, min(1.0, (m - r) * pvals[k]))
        adj[k] = running
    for k in pvals:
        adj.setdefault(k, np.nan)
    return adj


def fisher_combine(pvals: np.ndarray) -> float:
    pvals = np.asarray(pvals, dtype=float)
    pvals = pvals[~np.isnan(pvals)]
    return float(sps.combine_pvalues(pvals, method="fisher").pvalue) if len(pvals) else np.nan


def bootstrap_ci(x: np.ndarray, rng: np.random.Generator, n_boot: int = 10000, level: float = 0.95) -> tuple:
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) < 2:
        return (np.nan, np.nan)
    means = rng.choice(x, size=(n_boot, len(x)), replace=True).mean(1)
    a = (1 - level) / 2
    return (float(np.quantile(means, a)), float(np.quantile(means, 1 - a)))


def spearman_trend(values: np.ndarray, lags: np.ndarray) -> float:
    ok = ~np.isnan(values)
    if ok.sum() < 3:
        return np.nan
    return float(sps.spearmanr(lags[ok], values[ok]).statistic)
