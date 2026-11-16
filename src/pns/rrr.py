"""Lagged reduced-rank ridge regression (Mukherjee & Zhu 2011) and the estimator check.

For centred X (activity at t) and Y (activity at t + lag), with the SVD X = U S W^T,
    ridge:          B_R(lam) = W diag(s / (s^2 + lam)) U^T Y          (one SVD serves every lam)
    reduced rank:   V_d = top-d right singular vectors of [X B_R ; sqrt(lam) B_R]
                    B_RRR = B_R V_d V_d^T
    subspaces:      V_in = orth(B_R V_d)  (input / readout side; the proposal's V_Delta)
                    V_out = V_d           (output side)
The top-d right singular vectors of the stacked matrix are the top eigenvectors of
B_R^T X^T X B_R + lam B_R^T B_R, which is what is computed (p x p, independent of n).
lam = alpha * tr(X^T X) / p.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .geometry import cov_matched_random, orth
from .lagged import lagged_pairs, purged_folds
from .transform import ZScore


@dataclass
class RRRFit:
    B: np.ndarray
    Vin: np.ndarray
    Vout: np.ndarray
    xm: np.ndarray
    ym: np.ndarray
    lam: float

    def predict(self, X: np.ndarray) -> np.ndarray:
        return (X - self.xm) @ self.B + self.ym


class RidgePath:
    """Centred ridge regression for many penalties from a single SVD."""

    def __init__(self, X: np.ndarray, Y: np.ndarray):
        self.xm, self.ym = X.mean(0), Y.mean(0)
        Xc, Yc = X - self.xm, Y - self.ym
        U, s, Wt = np.linalg.svd(Xc, full_matrices=False)
        self.s, self.Wt, self.UtY = s, Wt, U.T @ Yc
        self.p = X.shape[1]
        self.trace = float(np.sum(s ** 2))

    def lam(self, alpha: float) -> float:
        return alpha * self.trace / self.p

    def coef(self, lam: float) -> np.ndarray:
        return self.Wt.T @ ((self.s / (self.s ** 2 + lam))[:, None] * self.UtY)

    def predict(self, X: np.ndarray, lam: float) -> np.ndarray:
        return (X - self.xm) @ self.coef(lam) + self.ym

    def rrr(self, lam: float, d: int) -> RRRFit:
        BR = self.coef(lam)
        XB = self.s[:, None] * (self.Wt @ BR)            # rows span X B_R; XB^T XB = B_R^T X^T X B_R
        G = XB.T @ XB + lam * (BR.T @ BR)
        evals, evecs = np.linalg.eigh(G)
        Vd = evecs[:, np.argsort(evals)[::-1][:d]]
        return RRRFit(B=BR @ Vd @ Vd.T, Vin=orth(BR @ Vd), Vout=Vd, xm=self.xm, ym=self.ym, lam=lam)


def r2_pooled(Y: np.ndarray, Yhat: np.ndarray, ref_mean: np.ndarray) -> float:
    return 1.0 - np.sum((Y - Yhat) ** 2) / np.sum((Y - ref_mean) ** 2)


def pca_basis(X: np.ndarray, d: int) -> np.ndarray:
    Xc = X - X.mean(0)
    _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
    return Vt[:d].T


def subspace_ridge_predict(V: np.ndarray, Xtr, Ytr, Xte, alpha: float) -> np.ndarray:
    """Ridge from d subspace scores to full future activity (PCA / random / any fixed subspace)."""
    xm = Xtr.mean(0)
    path = RidgePath((Xtr - xm) @ V, Ytr)
    return path.predict((Xte - xm) @ V, path.lam(alpha))


def fit_rrr(S: np.ndarray, lag: int, d: int, alpha: float, valid=None, segment=None,
            zscore: ZScore | None = None) -> tuple[RRRFit, ZScore]:
    """Fit lagged RRR on sqrt counts S (T, p). z-score parameters are fit on the bins used unless given."""
    i, j = lagged_pairs(len(S), lag, valid, segment)
    if zscore is None:
        zscore = ZScore.fit(S[np.unique(np.r_[i, j])])
    Z = zscore.transform(S)
    path = RidgePath(Z[i], Z[j])
    return path.rrr(path.lam(alpha), d), zscore


METHODS = ("rrr", "ridge", "pca", "random")


def cv_lagged(S: np.ndarray, lag: int, d: int, alphas: np.ndarray, n_folds: int, embargo: int,
              valid=None, segment=None, methods=METHODS, rng: np.random.Generator | None = None) -> dict:
    """Held-out pooled R^2 of predicting Z[t + lag] from Z[t], per method and alpha, with purged
    contiguous folds and z-scoring fit on each fold's training bins.

    Returns {method: array (n_alphas,)}. For 'pca' and 'random' the subspace is fixed per fold and
    alpha is the ridge penalty of the score-to-activity regression.
    """
    rng = rng or np.random.default_rng(0)
    i, j = lagged_pairs(len(S), lag, valid, segment)
    folds = purged_folds(i, j, n_folds, embargo)
    sse = {m: np.zeros(len(alphas)) for m in methods}
    sst = 0.0
    for train, test in folds:
        if len(test) == 0 or len(train) < 10:
            continue
        zs = ZScore.fit(S[np.unique(np.r_[i[train], j[train]])])
        Z = zs.transform(S)
        Xtr, Ytr, Xte, Yte = Z[i[train]], Z[j[train]], Z[i[test]], Z[j[test]]
        sst += np.sum((Yte - Ytr.mean(0)) ** 2)
        path = RidgePath(Xtr, Ytr)
        Vp = pca_basis(Xtr, d) if "pca" in methods else None
        Vr = cov_matched_random(np.cov(Xtr.T), d, rng) if "random" in methods else None
        for a_idx, a in enumerate(alphas):
            lam = path.lam(a)
            if "rrr" in methods:
                sse["rrr"][a_idx] += np.sum((Yte - path.rrr(lam, d).predict(Xte)) ** 2)
            if "ridge" in methods:
                sse["ridge"][a_idx] += np.sum((Yte - path.predict(Xte, lam)) ** 2)
            if "pca" in methods:
                sse["pca"][a_idx] += np.sum((Yte - subspace_ridge_predict(Vp, Xtr, Ytr, Xte, a)) ** 2)
            if "random" in methods:
                sse["random"][a_idx] += np.sum((Yte - subspace_ridge_predict(Vr, Xtr, Ytr, Xte, a)) ** 2)
    return {m: 1.0 - sse[m] / sst for m in methods}


def select_session_alpha(S: np.ndarray, lags: list[int], d: int, alphas: np.ndarray, n_folds: int,
                         embargo: int, valid=None, segment=None) -> dict:
    """One alpha per session: maximise the mean (over lags) held-out rank-d R^2.
    Also returns the per-lag curves and per-lag best alphas (sensitivity analysis)."""
    curves = np.stack([cv_lagged(S, lag, d, alphas, n_folds, embargo, valid, segment, methods=("rrr",))["rrr"]
                       for lag in lags])                                   # (n_lags, n_alphas)
    best = int(np.argmax(curves.mean(0)))
    return {"alpha": float(alphas[best]), "curves": curves,
            "per_lag_alpha": alphas[np.argmax(curves, axis=1)],
            "weak_lag": np.all(curves <= 0, axis=1)}
