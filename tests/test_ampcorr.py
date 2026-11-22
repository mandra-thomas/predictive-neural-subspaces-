import numpy as np

from pns.ampcorr import coupling, early_index, factors, poisson_glm, smooth_fill


def test_poisson_glm_recovers_coefficients():
    rng = np.random.default_rng(0)
    n = 4000
    x = rng.normal(size=n)
    off = np.log(rng.uniform(5, 15, size=n))
    y = rng.poisson(np.exp(0.3 + 0.8 * x + off))
    b = poisson_glm(y, np.column_stack([np.ones(n), x]), off)
    assert abs(b[1] - 0.8) < 0.05 and abs(b[0] - 0.3) < 0.05


def _detection_sim(rng, n_w=120, p=30, beta_true=3.0, trend=-0.2, jitter=0.05):
    """Constant true rates; detected rate = rate * exp(beta * relative amplitude); amplitude ramps down + jitter."""
    tau = np.linspace(0, 1, n_w)
    x = trend * tau[:, None] + jitter * rng.normal(size=(n_w, p))
    x = x - np.median(x, 0)
    rate = rng.uniform(2, 10, size=p)
    expo = np.full(n_w, 30.0)
    n = rng.poisson(rate[None, :] * expo[:, None] * np.exp(beta_true * x))
    return n.astype(float), expo, x


def test_fluctuation_coupling_detects_detection_loss_and_ignores_cotrend():
    rng = np.random.default_rng(1)
    n, expo, x = _detection_sim(rng)
    b = coupling(n, expo, x, degree=2)
    assert np.median(b) > 2.0            # fluctuations identify the coupling despite the quadratic nuisance
    # amplitude ramps but rate ramps for an unrelated reason: total coupling is spuriously large, fluctuation ~ 0
    n_w, p = x.shape
    tau = np.linspace(0, 1, n_w)
    n2 = rng.poisson(5 * 30 * np.exp(-0.6 * tau)[:, None] * np.ones((1, p))).astype(float)
    assert np.median(coupling(n2, expo, x, degree=0)) > 1.0
    assert abs(np.median(coupling(n2, expo, x, degree=2))) < 0.5


def test_correction_flattens_detection_ramp():
    rng = np.random.default_rng(2)
    n, expo, x = _detection_sim(rng, jitter=0.0, trend=-0.3)
    corr = n * factors(smooth_fill_cols(x), 3.0)
    tau = np.arange(len(n))
    raw_slope = np.polyfit(tau, n.sum(1), 1)[0]
    cor_slope = np.polyfit(tau, corr.sum(1), 1)[0]
    assert raw_slope < 0 and abs(cor_slope) < 0.1 * abs(raw_slope)


def smooth_fill_cols(x):
    return np.column_stack([smooth_fill(x[:, j]) for j in range(x.shape[1])])


def test_early_index_sign():
    t = np.arange(90.0)
    assert early_index(1 - np.exp(-t / 10), 1.0) > 0.8    # relaxation: early
    assert early_index(np.exp(t / 20), 1.0) < -0.5        # accelerating: late
    assert abs(early_index(t, 1.0)) < 1e-9                # linear: neither


def test_isolated_mask():
    from pns.ampcorr import isolated_mask
    t = np.array([0.0, 0.01, 0.2, 0.0, 0.3, 0.31])
    u = np.array([0, 0, 0, 1, 1, 1])
    assert isolated_mask(t, u, 0.05).tolist() == [True, False, True, True, True, False]
