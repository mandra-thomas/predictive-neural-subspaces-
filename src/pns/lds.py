"""Amendment A18 (post hoc): a linear-Gaussian state-space model with an explicit drift term and a learned timescale
per latent (an OU-kernel analogue of GPFA, fitted by EM with a Kalman filter and RTS smoother).

    y_n = C z_n + D u_n + d + eps_n,        eps_n ~ N(0, diag R)
    z_{n+1} = diag(phi) z_n + eta_n,        eta_n ~ N(0, diag(1 - phi^2)),   z_0 ~ N(0, I)

Each latent has unit stationary variance (the GPFA convention), so scale is identified and no rescaling is needed;
phi is kept in [0, PHI_MAX]. The timescale of latent k is tau_k = -dt / ln(phi_k). u_n holds known inputs: the
explicit drift term (slow cosines of session time) and any other regressors.

Observations may be missing per entry (mask False): the filter then uses only the observed entries of y_n. EM
parameter updates require whole rows to be either observed or missing.

Readouts:
  filtered means  E[z_n | y_1..n] (causal; secondary readout)
  instantaneous   (C'R^-1 C)^-1 C'R^-1 (y_n - D_sel u_n - d): each trial's own activity only, so no filter can
                  integrate past stimuli into a prior-like signal (primary readout in A18)
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np
from scipy.optimize import minimize_scalar

PHI_MAX = 1.0 - 1e-4
LOG2PI = np.log(2 * np.pi)


@dataclass
class LDSParams:
    C: np.ndarray        # (p, K)
    D: np.ndarray        # (p, m)
    d: np.ndarray        # (p,)
    R: np.ndarray        # (p,)
    phi: np.ndarray      # (K,)

    def tau(self, dt: float = 1.0) -> np.ndarray:
        return -dt / np.log(np.clip(self.phi, 1e-12, PHI_MAX))


@dataclass
class LDSFit:
    params: LDSParams
    ll_trace: list = field(default_factory=list)
    converged: bool = False
    restart_lls: list = field(default_factory=list)


# ----------------------------------------------------------------------------- inference
def _logdet(A: np.ndarray) -> float:
    return float(np.linalg.slogdet(A)[1])


def kalman_filter(Y: np.ndarray, U: np.ndarray, params: LDSParams, mask: np.ndarray | None = None) -> dict:
    """Filtered and one-step predicted moments and the log-likelihood of the observed entries.
    While rows are fully observed the covariance recursion converges to a steady state, which is then reused
    (exactly: the recursion does not depend on the data)."""
    N, p = Y.shape
    C, phi = params.C, params.phi
    K = len(phi)
    Qd = np.diag(1.0 - phi ** 2)
    mask = np.ones((N, p), bool) if mask is None else np.asarray(mask, bool)
    Yt = Y - U @ params.D.T - params.d
    rinv = 1.0 / params.R
    CtRinv = (C * rinv[:, None]).T                       # (K, p)
    J_full = CtRinv @ C
    sum_log_r_full = -float(np.sum(np.log(rinv)))
    full = mask.all(1)
    m_f, P_f = np.zeros((N, K)), np.zeros((N, K, K))
    m_p, P_p = np.zeros((N, K)), np.zeros((N, K, K))
    ll = 0.0
    steady = None                                        # (Pp, Ppost, logdet_S) once converged on full rows
    for n in range(N):
        if n == 0:
            mp, Pp = np.zeros(K), np.eye(K)
        else:
            mp = phi * m_f[n - 1]
            Pp = steady[0] if steady is not None else phi[:, None] * P_f[n - 1] * phi[None, :] + Qd
        m_p[n], P_p[n] = mp, Pp
        obs = mask[n]
        if not obs.any():
            m_f[n], P_f[n] = mp, Pp
            steady = None
            continue
        if full[n]:
            e = Yt[n]
            if steady is not None:
                Ppost, logdet_S = steady[1], steady[2]
            else:
                Ppost = np.linalg.inv(np.linalg.inv(Pp) + J_full)
                Ppost = 0.5 * (Ppost + Ppost.T)
                logdet_S = sum_log_r_full + _logdet(Pp) - _logdet(Ppost)
                if n > 0 and full[n - 1] and np.max(np.abs(Pp - P_p[n - 1])) < 1e-12:
                    steady = (Pp, Ppost, logdet_S)
            innov = e - C @ mp
            g = CtRinv @ innov
            quad = float(innov @ (rinv * innov) - g @ Ppost @ g)
            n_obs = p
        else:
            steady = None
            Cs, ri, e = C[obs], rinv[obs], Yt[n, obs]
            J = Cs.T @ (Cs * ri[:, None])
            Ppost = np.linalg.inv(np.linalg.inv(Pp) + J)
            Ppost = 0.5 * (Ppost + Ppost.T)
            logdet_S = -float(np.sum(np.log(ri))) + _logdet(Pp) - _logdet(Ppost)
            innov = e - Cs @ mp
            g = Cs.T @ (ri * innov)
            quad = float(innov @ (ri * innov) - g @ Ppost @ g)
            n_obs = int(obs.sum())
        m_f[n] = mp + Ppost @ g
        P_f[n] = Ppost
        ll += -0.5 * (n_obs * LOG2PI + logdet_S + quad)
    return {"m_f": m_f, "P_f": P_f, "m_p": m_p, "P_p": P_p, "ll": ll}


def rts_smoother(kf: dict, phi: np.ndarray) -> dict:
    """Smoothed means, covariances and lag-one cross-covariances Cov(z_{n+1}, z_n | y)."""
    m_f, P_f, m_p, P_p = kf["m_f"], kf["P_f"], kf["m_p"], kf["P_p"]
    N, K = m_f.shape
    m_s, P_s = m_f.copy(), P_f.copy()
    P_cross = np.zeros((max(N - 1, 0), K, K))
    cache = None                                         # (P_f[n], P_p[n+1], J) reused while both repeat exactly
    for n in range(N - 2, -1, -1):
        if cache is not None and np.array_equal(P_f[n], cache[0]) and np.array_equal(P_p[n + 1], cache[1]):
            Jn = cache[2]
        else:
            Jn = (P_f[n] * phi[None, :]) @ np.linalg.inv(P_p[n + 1])
            cache = (P_f[n], P_p[n + 1], Jn)
        m_s[n] = m_f[n] + Jn @ (m_s[n + 1] - m_p[n + 1])
        P_s[n] = P_f[n] + Jn @ (P_s[n + 1] - P_p[n + 1]) @ Jn.T
        P_cross[n] = P_s[n + 1] @ Jn.T
    return {"m_s": m_s, "P_s": P_s, "P_cross": P_cross}


def instantaneous_scores(Y: np.ndarray, U: np.ndarray, params: LDSParams, subtract_cols=None) -> np.ndarray:
    """Generalized least-squares latent estimate from each observation alone (no dynamics):
    (C'R^-1 C)^-1 C'R^-1 (y_n - D[:, cols] u_n[cols] - d). `subtract_cols` selects the inputs removed (default all)."""
    C, rinv = params.C, 1.0 / params.R
    cols = np.arange(U.shape[1]) if subtract_cols is None else np.asarray(subtract_cols, int)
    Yt = Y - U[:, cols] @ params.D[:, cols].T - params.d
    A = C.T @ (C * rinv[:, None])
    return np.linalg.solve(A, (C * rinv[:, None]).T @ Yt.T).T


# ----------------------------------------------------------------------------- EM
def _phi_update(A: float, B: float, Cc: float, n_trans: int) -> float:
    """Maximize the expected AR(1) log-likelihood with q = 1 - phi^2 over phi in [0, PHI_MAX].
    A = sum E[z_{n+1}^2], B = sum E[z_{n+1} z_n], Cc = sum E[z_n^2] over the n_trans transitions."""
    def negf(ph):
        q = 1.0 - ph ** 2
        return 0.5 * n_trans * np.log(q) + (A - 2 * ph * B + ph ** 2 * Cc) / (2 * q)
    res = minimize_scalar(negf, bounds=(0.0, PHI_MAX), method="bounded", options={"xatol": 1e-7})
    return float(res.x)


def _m_step(Y, U, rows, sm, fix_phi):
    m_s, P_s, P_cross = sm["m_s"], sm["P_s"], sm["P_cross"]
    N, K = m_s.shape
    Yo, Uo, Mo = Y[rows], U[rows], m_s[rows]
    n_obs = len(Yo)
    X = np.hstack([Mo, Uo, np.ones((n_obs, 1))])
    Sxx = X.T @ X
    Sxx[:K, :K] += P_s[rows].sum(0)
    Syx = Yo.T @ X
    W = np.linalg.solve(Sxx + 1e-9 * np.eye(len(Sxx)), Syx.T).T
    C, D, d = W[:, :K], W[:, K:-1], W[:, -1]
    R = (np.sum(Yo ** 2, 0) - np.sum(W * Syx, 1)) / n_obs
    R = np.maximum(R, 1e-4)
    if fix_phi is not None:
        phi = np.full(K, float(fix_phi))
    else:
        Ezz = P_s + np.einsum("nk,nl->nkl", m_s, m_s)
        Ecross = P_cross + np.einsum("nk,nl->nkl", m_s[1:], m_s[:-1])
        A = np.einsum("nkk->k", Ezz[1:])
        Cc = np.einsum("nkk->k", Ezz[:-1])
        B = np.einsum("nkk->k", Ecross)
        phi = np.array([_phi_update(A[k], B[k], Cc[k], N - 1) for k in range(K)])
    return LDSParams(C=C, D=D, d=d, R=R, phi=phi)


def init_params(Y, U, K, rows, rng=None, jitter=False) -> LDSParams:
    """Regress out inputs, factor analysis on the residuals, AR(1) coefficient of each factor's scores."""
    from sklearn.decomposition import FactorAnalysis
    Yo, Uo = Y[rows], U[rows]
    X = np.hstack([Uo, np.ones((len(Yo), 1))])
    beta = np.linalg.lstsq(X, Yo, rcond=None)[0]
    res = Yo - X @ beta
    fa = FactorAnalysis(n_components=K, random_state=0).fit(res)
    C = fa.components_.T.copy()
    R = np.maximum(fa.noise_variance_, 1e-3)
    sc = fa.transform(res)
    # AR(1) plus observation noise: acf(k) = c phi^k for k >= 1, so acf(2)/acf(1) estimates phi without the
    # downward bias that noise in the factor scores gives acf(1)
    def ar_init(x):
        r1 = np.corrcoef(x[:-1], x[1:])[0, 1]
        r2 = np.corrcoef(x[:-2], x[2:])[0, 1]
        return r2 / r1 if r1 > 0.05 and r2 > 0 else max(r1, 0.0)
    phi = np.clip([ar_init(sc[:, k]) for k in range(K)], 0.05, 0.995)
    if jitter:
        rng = rng or np.random.default_rng(0)
        C = C + 0.2 * np.std(C) * rng.standard_normal(C.shape)
        phi = rng.uniform(0.1, 0.98, K)
    return LDSParams(C=C, D=beta[:-1].T, d=beta[-1], R=R, phi=phi)


def _em(Y, U, params, rows, mask, max_iter, tol, fix_phi):
    trace = []
    converged = False
    for _ in range(max_iter):
        kf = kalman_filter(Y, U, params, mask)
        trace.append(kf["ll"])
        if len(trace) > 1 and abs(trace[-1] - trace[-2]) < tol * abs(trace[-2]):
            converged = True
            break
        sm = rts_smoother(kf, params.phi)
        params = _m_step(Y, U, rows, sm, fix_phi)
    return params, trace, converged


def fit_lds(Y: np.ndarray, U: np.ndarray | None, K: int, row_mask: np.ndarray | None = None, max_iter: int = 300,
            tol: float = 1e-6, n_restarts: int = 5, rng: np.random.Generator | None = None,
            fix_phi: float | None = None) -> LDSFit:
    """EM fit with restarts (FA initialization, then jittered copies); keeps the highest log-likelihood.
    row_mask: rows (time points) used for fitting; other rows are treated as missing. Latents are returned sorted by
    timescale (slowest first), with signs set so each loading column sums to a non-negative value."""
    N, p = Y.shape
    U = np.zeros((N, 0)) if U is None else np.asarray(U, float)
    rows = np.ones(N, bool) if row_mask is None else np.asarray(row_mask, bool)
    mask = np.repeat(rows[:, None], p, axis=1)
    rng = rng or np.random.default_rng(0)
    best, lls = None, []
    for r in range(max(n_restarts, 1)):
        p0 = init_params(Y, U, K, rows, rng, jitter=r > 0)
        if fix_phi is not None:
            p0 = replace(p0, phi=np.full(K, float(fix_phi)))
        params, trace, conv = _em(Y, U, p0, rows, mask, max_iter, tol, fix_phi)
        lls.append(trace[-1])
        if best is None or trace[-1] > best[1][-1]:
            best = (params, trace, conv)
    params, trace, conv = best
    order = np.argsort(params.phi)[::-1]
    sign = np.where(params.C[:, order].sum(0) < 0, -1.0, 1.0)
    params = LDSParams(C=params.C[:, order] * sign, D=params.D, d=params.d, R=params.R, phi=params.phi[order])
    return LDSFit(params=params, ll_trace=trace, converged=conv, restart_lls=lls)


# ----------------------------------------------------------------------------- model comparison
def cosmooth_r2(Y: np.ndarray, U: np.ndarray | None, K: int, n_trial_folds: int = 5, n_neuron_folds: int = 5,
                rng: np.random.Generator | None = None, fix_phi: float | None = None, max_iter: int = 200) -> float:
    """Leave-neuron-out co-smoothing R^2 (Yu et al. 2009 style), with contiguous held-out trial blocks:
    fit on the training trials; on the test trials, infer the latents from the held-in neurons only (held-out
    neurons are unobserved everywhere during inference) and predict the held-out neurons."""
    N, p = Y.shape
    U = np.zeros((N, 0)) if U is None else np.asarray(U, float)
    rng = rng or np.random.default_rng(0)
    bounds = np.linspace(0, N, n_trial_folds + 1).round().astype(int)
    groups = np.array_split(rng.permutation(p), n_neuron_folds)
    sse = sst = 0.0
    for f in range(n_trial_folds):
        test = np.zeros(N, bool)
        test[bounds[f]:bounds[f + 1]] = True
        fit = fit_lds(Y, U, K, row_mask=~test, max_iter=max_iter, n_restarts=1, rng=rng, fix_phi=fix_phi)
        P = fit.params
        mean_train = Y[~test].mean(0)
        for g in groups:
            mask = np.ones((N, p), bool)
            mask[:, g] = False                           # held-out neurons unobserved on every trial
            kf = kalman_filter(Y, U, P, mask)
            ms = rts_smoother(kf, P.phi)["m_s"]
            pred = ms[test] @ P.C[g].T + U[test] @ P.D[g].T + P.d[g]
            sse += float(np.sum((Y[test][:, g] - pred) ** 2))
            sst += float(np.sum((Y[test][:, g] - mean_train[g]) ** 2))
    return 1.0 - sse / sst
