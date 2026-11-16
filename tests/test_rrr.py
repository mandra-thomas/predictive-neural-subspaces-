import numpy as np
import pytest

from pns.geometry import principal_angles
from pns.rrr import RidgePath, cv_lagged, fit_rrr


def _objective(X, Y, B, lam):
    Xc, Yc = X - X.mean(0), Y - Y.mean(0)
    return np.sum((Yc - Xc @ B) ** 2) + lam * np.sum(B ** 2)


def _als(X, Y, lam, d, rng, iters=3000):
    """Brute-force rank-d ridge via alternating least squares on B = A C^T, C orthonormal."""
    Xc, Yc = X - X.mean(0), Y - Y.mean(0)
    p = X.shape[1]
    C, _ = np.linalg.qr(rng.standard_normal((Y.shape[1], d)))
    G = Xc.T @ Xc + lam * np.eye(p)
    for _ in range(iters):
        A = np.linalg.solve(G, Xc.T @ Yc @ C)                    # ridge onto Y C
        C = Yc.T @ Xc @ A @ np.linalg.inv(A.T @ G @ A)           # optimal C given A
        Q, R = np.linalg.qr(C)
        C, A = Q, A @ R.T
    return A @ C.T


@pytest.fixture
def data():
    rng = np.random.default_rng(0)
    n, p = 300, 12
    X = rng.standard_normal((n, p)) @ rng.standard_normal((p, p))
    Btrue = rng.standard_normal((p, 2)) @ rng.standard_normal((2, p))
    Y = X @ Btrue + 2.0 * rng.standard_normal((n, p))
    return X, Y, Btrue


def test_ridge_path_matches_direct_solve(data):
    X, Y, _ = data
    path = RidgePath(X, Y)
    Xc, Yc = X - X.mean(0), Y - Y.mean(0)
    for lam in [0.1, 10.0, 1000.0]:
        direct = np.linalg.solve(Xc.T @ Xc + lam * np.eye(X.shape[1]), Xc.T @ Yc)
        np.testing.assert_allclose(path.coef(lam), direct, atol=1e-10)


def test_closed_form_is_the_rank_d_optimum(data):
    X, Y, _ = data
    path = RidgePath(X, Y)
    rng = np.random.default_rng(1)
    for lam in [1.0, 100.0]:
        for d in [1, 3]:
            closed = _objective(X, Y, path.rrr(lam, d).B, lam)
            best_als = min(_objective(X, Y, _als(X, Y, lam, d, rng), lam) for _ in range(5))
            assert closed <= best_als * (1 + 1e-8)
            assert closed == pytest.approx(best_als, rel=1e-6)


def test_non_augmented_variant_is_worse(data):
    """The augmented stacking matters: projecting onto the top singular vectors of X B_R alone is suboptimal."""
    X, Y, _ = data
    lam, d = 3000.0, 2
    path = RidgePath(X, Y)
    BR = path.coef(lam)
    Xc = X - X.mean(0)
    _, _, Vt = np.linalg.svd(Xc @ BR, full_matrices=False)
    naive = BR @ Vt[:d].T @ Vt[:d]
    assert _objective(X, Y, path.rrr(lam, d).B, lam) < _objective(X, Y, naive, lam)


def test_full_rank_equals_ridge(data):
    X, Y, _ = data
    path = RidgePath(X, Y)
    np.testing.assert_allclose(path.rrr(5.0, X.shape[1]).B, path.coef(5.0), atol=1e-9)


def test_recovers_rank2_truth(data):
    X, Y, Btrue = data
    fit = RidgePath(X, Y).rrr(1e-3, 2)
    U, _, _ = np.linalg.svd(Btrue)                       # column space of Btrue (input side)
    theta = principal_angles(fit.Vin, U[:, :2])
    assert np.degrees(theta.max()) < 5


def test_lag_direction():
    """Unit 1 copies unit 0 one bin later: forward lag-1 B must map 0 -> 1, not 1 -> 0."""
    rng = np.random.default_rng(3)
    T, p = 4000, 6
    S = rng.standard_normal((T, p))
    S[1:, 1] = S[:-1, 0] + 0.1 * rng.standard_normal(T - 1)
    fit, _ = fit_rrr(S, lag=1, d=1, alpha=1e-3)
    assert abs(fit.B[0, 1]) > 0.8
    assert abs(fit.B[1, 0]) < 0.1


def test_cv_lagged_orders_methods():
    rng = np.random.default_rng(4)
    T, p, k = 3000, 20, 2
    lat = np.zeros((T, k))
    for t in range(1, T):
        lat[t] = 0.95 * lat[t - 1] + rng.standard_normal(k)
    S = lat @ rng.standard_normal((k, p)) + 3.0 * rng.standard_normal((T, p))
    alphas = np.logspace(-3, 1, 5)
    r2 = cv_lagged(S, lag=1, d=2, alphas=alphas, n_folds=5, embargo=10)
    assert r2["ridge"].max() >= r2["rrr"].max() - 0.02     # full rank is the ceiling (up to noise)
    assert r2["rrr"].max() > 0.05
    assert r2["rrr"].max() > r2["random"].max()
