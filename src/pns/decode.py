"""Decoders for subspace content and the full-population (Findling-style) prior gate.

Binary targets: logistic regression, mean per-fold AUC. Continuous targets: ridge, pooled out-of-fold
R^2 (per-fold R^2 is biased under contiguous folds). Features are standardised inside each training fold.
Regularisation is fixed (C, alpha from config) and identical across lags, real data and the null.
"""
from __future__ import annotations

import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import Lasso
from sklearn.model_selection import KFold


def _standardize(Ftr: np.ndarray, Fte: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    m = Ftr.mean(0)
    s = Ftr.std(0)
    s[s < 1e-12] = 1.0
    return (Ftr - m) / s, (Fte - m) / s


def logistic_fit(X: np.ndarray, y01: np.ndarray, C: float = 1.0, max_iter: int = 50,
                 tol: float = 1e-10) -> tuple[np.ndarray, float]:
    """L2 logistic regression by Newton's method; same objective as sklearn
    LogisticRegression(C=C, penalty='l2'): 0.5 ||w||^2 + C * sum log-loss, intercept unpenalised.
    Much faster than sklearn for the small (d <= 10 feature) problems decoded thousands of times."""
    n, k = X.shape
    Xa = np.column_stack([X, np.ones(n)])
    beta = np.zeros(k + 1)
    reg = np.r_[np.ones(k), 0.0]
    for _ in range(max_iter):
        z = Xa @ beta
        p = 0.5 * (1 + np.tanh(0.5 * z))                 # numerically stable sigmoid
        g = C * Xa.T @ (p - y01) + reg * beta
        H = C * (Xa.T * (p * (1 - p))) @ Xa + np.diag(reg) + 1e-12 * np.eye(k + 1)
        step = np.linalg.solve(H, g)
        beta -= step
        if np.max(np.abs(step)) < tol:
            break
    return beta[:k], float(beta[k])


def auc_score(y01: np.ndarray, score: np.ndarray) -> float:
    """ROC AUC via the Mann-Whitney rank statistic (ties get average ranks)."""
    from scipy.stats import rankdata
    r = rankdata(score)
    n1 = int(y01.sum())
    n0 = len(y01) - n1
    return float((r[y01 == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def auc_cv(F: np.ndarray, y: np.ndarray, folds, C: float = 1.0) -> float:
    """Mean per-fold AUC of an L2 logistic decoder. y in {0, 1} (or +-1). Folds lacking a class are skipped."""
    y = (np.asarray(y) > 0).astype(float)
    aucs = []
    for tr, te in folds:
        ytr, yte = y[tr], y[te]
        if ytr.min() == ytr.max() or yte.min() == yte.max():
            continue
        Xtr, Xte = _standardize(F[tr], F[te])
        w, b = logistic_fit(Xtr, ytr, C)
        aucs.append(auc_score(yte, Xte @ w + b))
    return float(np.mean(aucs)) if aucs else np.nan


def r2_cv(F: np.ndarray, Y: np.ndarray, folds, alpha: float = 1.0) -> np.ndarray | float:
    """Pooled out-of-fold R^2 of ridge regression. Y may be (n,) or (n, m) for m targets at once
    (used to score all pseudo-session priors in one pass). SST is taken around each fold's training mean."""
    Y = np.asarray(Y, dtype=float)
    one = Y.ndim == 1
    Y2 = Y[:, None] if one else Y
    sse = np.zeros(Y2.shape[1])
    sst = np.zeros(Y2.shape[1])
    for tr, te in folds:
        Xtr, Xte = _standardize(F[tr], F[te])
        ym = Y2[tr].mean(0)
        k = Xtr.shape[1]
        W = np.linalg.solve(Xtr.T @ Xtr + alpha * np.eye(k), Xtr.T @ (Y2[tr] - ym))
        pred = Xte @ W + ym
        sse += np.sum((Y2[te] - pred) ** 2, axis=0)
        sst += np.sum((Y2[te] - ym) ** 2, axis=0)
    r2 = 1.0 - sse / sst
    return float(r2[0]) if one else r2


def lasso_nested_r2(F: np.ndarray, Y: np.ndarray, n_folds: int, rng: np.random.Generator,
                    alphas=(1e-4, 1e-3, 1e-2, 1e-1)) -> np.ndarray:
    """Findling-style decoder: Lasso with interleaved outer folds and an inner interleaved CV over alpha.
    Y (n,) or (n, m); returns pooled out-of-fold R^2 per target column."""
    Y = np.asarray(Y, dtype=float)
    Y2 = Y[:, None] if Y.ndim == 1 else Y
    n = len(F)
    outer = KFold(n_folds, shuffle=True, random_state=int(rng.integers(2**31)))
    sse = np.zeros(Y2.shape[1])
    sst = np.zeros(Y2.shape[1])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        for tr, te in outer.split(np.arange(n)):
            Xtr, Xte = _standardize(F[tr], F[te])
            inner = list(KFold(n_folds, shuffle=True, random_state=int(rng.integers(2**31))).split(tr))
            for col in range(Y2.shape[1]):
                y_tr = Y2[tr, col]
                scores = []
                for a in alphas:
                    err = 0.0
                    for itr, ite in inner:
                        m = Lasso(alpha=a, max_iter=5000).fit(Xtr[itr], y_tr[itr])
                        err += np.sum((y_tr[ite] - m.predict(Xtr[ite])) ** 2)
                    scores.append(err)
                best = alphas[int(np.argmin(scores))]
                m = Lasso(alpha=best, max_iter=5000).fit(Xtr, y_tr)
                sse[col] += np.sum((Y2[te, col] - m.predict(Xte)) ** 2)
                sst[col] += np.sum((Y2[te, col] - y_tr.mean()) ** 2)
    return 1.0 - sse / sst
