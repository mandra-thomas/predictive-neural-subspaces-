"""Subspace geometry: principal angles, nesting, orthogonal complements, covariance-matched chance."""
from __future__ import annotations

import numpy as np


def orth(A: np.ndarray) -> np.ndarray:
    """Orthonormal basis preserving column order (span of the first k columns is kept)."""
    Q, _ = np.linalg.qr(A)
    return Q


def principal_angles(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Principal angles (radians, ascending) between span(A) and span(B)."""
    s = np.linalg.svd(orth(A).T @ orth(B), compute_uv=False)
    return np.arccos(np.clip(s, 0.0, 1.0))


def angle_summary(theta: np.ndarray) -> dict:
    return {"mean_deg": float(np.degrees(theta).mean()),
            "first_deg": float(np.degrees(theta[0])),
            "sum_sin2": float(np.sum(np.sin(theta) ** 2))}


def nesting_index(container: np.ndarray, target: np.ndarray, k: int = 1) -> float:
    """Mean squared projection of the leading k directions of `target` onto span(container).
    1 = the target's leading directions lie inside the container; 0 = orthogonal. Asymmetric."""
    Q = orth(container)
    v = orth(target)[:, :k]
    return float(np.mean(np.sum((Q.T @ v) ** 2, axis=0)))


def complement_basis(A: np.ndarray, B: np.ndarray, tol: float = 1e-6) -> np.ndarray:
    """Orthonormal basis of the part of span(A) orthogonal to span(B)."""
    Qa, Qb = orth(A), orth(B)
    M = Qa - Qb @ (Qb.T @ Qa)
    U, s, _ = np.linalg.svd(M, full_matrices=False)
    return U[:, s > tol]


def cov_matched_random(C: np.ndarray, d: int, rng: np.random.Generator) -> np.ndarray:
    """Random d-dim subspace drawn in proportion to the data covariance C (Elsayed, Lara, Kaufman, Churchland & Cunningham 2016, Nat Commun 7:13239)."""
    evals, evecs = np.linalg.eigh(C)
    evals = np.clip(evals, 0, None)
    G = rng.standard_normal((C.shape[0], d))
    return orth(evecs @ (np.sqrt(evals)[:, None] * G))


def random_floor(C: np.ndarray, d: int, rng: np.random.Generator, n: int = 500) -> dict:
    """Chance distribution of angle summaries between two independent covariance-matched subspaces."""
    rows = [angle_summary(principal_angles(cov_matched_random(C, d, rng), cov_matched_random(C, d, rng)))
            for _ in range(n)]
    out = {}
    for key in rows[0]:
        vals = np.array([r[key] for r in rows])
        out[f"{key}_mean"] = float(vals.mean())
        out[f"{key}_q05"] = float(np.quantile(vals, 0.05))
    return out
