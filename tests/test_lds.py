"""A18 latent state-space model: exact inference on a tiny problem, EM behaviour, recovery, drift absorption,
causality of the filter, phi bounds and missing data."""
import numpy as np
import pytest
from scipy.stats import multivariate_normal

from pns.lds import (PHI_MAX, LDSParams, cosmooth_r2, fit_lds, instantaneous_scores, kalman_filter, rts_smoother)


def simulate_lds(N, p, phi, rng, R=0.5, U=None, D=None):
    K = len(phi)
    C = rng.standard_normal((p, K))
    z = np.zeros((N, K))
    z[0] = rng.standard_normal(K)
    for n in range(1, N):
        z[n] = phi * z[n - 1] + np.sqrt(1 - phi ** 2) * rng.standard_normal(K)
    Y = z @ C.T + np.sqrt(R) * rng.standard_normal((N, p))
    if U is not None:
        Y = Y + U @ D.T
    return Y, z, C


def joint_cov(params, N):
    """Covariance of the stacked latents and observations of the model (inputs zero, d zero)."""
    phi, C, R = params.phi, params.C, params.R
    K, p = len(phi), len(R)
    Szz = np.zeros((N * K, N * K))
    for a in range(N):
        for b in range(N):
            Szz[a * K:(a + 1) * K, b * K:(b + 1) * K] = np.diag(phi ** abs(a - b))
    Cbig = np.kron(np.eye(N), C)
    Syy = Cbig @ Szz @ Cbig.T + np.kron(np.eye(N), np.diag(R))
    Szy = Szz @ Cbig.T
    return Szz, Syy, Szy


def tiny():
    rng = np.random.default_rng(0)
    params = LDSParams(C=rng.standard_normal((3, 2)), D=np.zeros((3, 0)), d=np.zeros(3), R=np.array([0.3, 0.5, 0.8]),
                       phi=np.array([0.9, 0.4]))
    Y = rng.standard_normal((6, 3))
    return params, Y


def test_smoother_and_loglik_equal_dense_gaussian_conditioning():
    params, Y = tiny()
    N, K = 6, 2
    kf = kalman_filter(Y, np.zeros((N, 0)), params)
    sm = rts_smoother(kf, params.phi)
    Szz, Syy, Szy = joint_cov(params, N)
    y = Y.ravel()
    mean = Szy @ np.linalg.solve(Syy, y)
    cov = Szz - Szy @ np.linalg.solve(Syy, Szy.T)
    assert np.allclose(sm["m_s"].ravel(), mean, atol=1e-8)
    for n in range(N):
        assert np.allclose(sm["P_s"][n], cov[n * K:(n + 1) * K, n * K:(n + 1) * K], atol=1e-8)
    for n in range(N - 1):
        assert np.allclose(sm["P_cross"][n], cov[(n + 1) * K:(n + 2) * K, n * K:(n + 1) * K], atol=1e-8)
    assert kf["ll"] == pytest.approx(multivariate_normal(np.zeros(len(y)), Syy).logpdf(y), abs=1e-8)


def test_missing_entries_match_dense_conditioning():
    params, Y = tiny()
    N, K, p = 6, 2, 3
    mask = np.ones((N, p), bool)
    mask[1, 0] = False
    mask[3] = False
    kf = kalman_filter(Y, np.zeros((N, 0)), params, mask)
    sm = rts_smoother(kf, params.phi)
    Szz, Syy, Szy = joint_cov(params, N)
    obs = mask.ravel()
    mean = Szy[:, obs] @ np.linalg.solve(Syy[np.ix_(obs, obs)], Y.ravel()[obs])
    assert np.allclose(sm["m_s"].ravel(), mean, atol=1e-8)
    ll = multivariate_normal(np.zeros(obs.sum()), Syy[np.ix_(obs, obs)]).logpdf(Y.ravel()[obs])
    assert kf["ll"] == pytest.approx(ll, abs=1e-8)


def test_filter_is_causal():
    params, Y = tiny()
    U = np.zeros((6, 0))
    a = kalman_filter(Y, U, params)["m_f"]
    Y2 = Y.copy()
    Y2[3:] += 5.0
    b = kalman_filter(Y2, U, params)["m_f"]
    assert np.allclose(a[:3], b[:3]) and not np.allclose(a[3:], b[3:])


@pytest.fixture(scope="module")
def recovered():
    """Three sessions of real-session size (about 1,500 trials). The target is each simulation's realised timescale:
    the sampling error of a slow timescale from a finite noisy series is large, and EM finds the likelihood maximum
    (checked against a profile likelihood while developing A18)."""
    out = []
    for seed in (11, 12, 13):
        rng = np.random.default_rng(seed)
        Y, z, C = simulate_lds(1500, 30, np.array([0.9, 0.5]), rng)
        phi_emp = np.array([z[1:, k] @ z[:-1, k] / (z[:-1, k] @ z[:-1, k]) for k in range(2)])
        out.append((fit_lds(Y, None, 2, n_restarts=2, max_iter=500, rng=np.random.default_rng(seed)), phi_emp, C))
    return out


def test_em_loglik_non_decreasing(recovered):
    for fit, _, _ in recovered:
        d = np.diff(fit.ll_trace)
        assert np.all(d > -1e-6 * np.abs(np.asarray(fit.ll_trace[1:])))


def test_recovers_timescales_and_loadings(recovered):
    for fit, phi_emp, C in recovered:
        assert fit.converged
        assert np.allclose(fit.params.tau(), -1 / np.log(phi_emp), rtol=0.3)
        Qa, _ = np.linalg.qr(fit.params.C)
        Qb, _ = np.linalg.qr(C)
        angle = np.degrees(np.arccos(np.clip(np.linalg.svd(Qa.T @ Qb, compute_uv=False).min(), -1, 1)))
        assert angle < 15


def test_cosine_drift_is_absorbed_by_inputs():
    rng = np.random.default_rng(3)
    N = 2000
    u = np.linspace(0, 1, N)
    U = np.column_stack([np.cos(np.pi * k * u) for k in (1, 2, 3)])
    D = 2.0 * rng.standard_normal((20, 3))
    Y, _, _ = simulate_lds(N, 20, np.array([0.8]), rng, U=U, D=D)
    fit = fit_lds(Y, U, 1, n_restarts=1, max_iter=200)
    assert np.corrcoef(fit.params.D.ravel(), D.ravel())[0, 1] > 0.95
    assert fit.params.phi[0] < 0.95                   # the latent keeps its own timescale, not the drift's


def test_phi_stays_below_one_on_random_walk():
    rng = np.random.default_rng(4)
    w = np.cumsum(rng.standard_normal(1500))
    Y = np.outer(w / w.std(), rng.standard_normal(10)) + rng.standard_normal((1500, 10))
    fit = fit_lds(Y, None, 1, n_restarts=1, max_iter=100)
    assert 0.0 <= fit.params.phi[0] <= PHI_MAX


def test_instantaneous_scores_recover_latents_without_dynamics():
    rng = np.random.default_rng(5)
    params = LDSParams(C=rng.standard_normal((40, 2)), D=np.zeros((40, 0)), d=np.zeros(40), R=np.full(40, 0.01),
                       phi=np.array([0.9, 0.5]))
    z = rng.standard_normal((50, 2))
    Y = z @ params.C.T + 0.1 * rng.standard_normal((50, 40))
    assert np.allclose(instantaneous_scores(Y, np.zeros((50, 0)), params), z, atol=0.1)


def test_cosmoothing_prefers_dynamics_when_present():
    rng = np.random.default_rng(6)
    Y, _, _ = simulate_lds(1200, 15, np.array([0.97, 0.9]), rng, R=1.0)
    r_lds = cosmooth_r2(Y, None, 2, n_trial_folds=3, n_neuron_folds=3, rng=np.random.default_rng(7), max_iter=60)
    r_fa = cosmooth_r2(Y, None, 2, n_trial_folds=3, n_neuron_folds=3, rng=np.random.default_rng(7), fix_phi=0.0,
                       max_iter=60)
    assert r_lds > r_fa > 0
