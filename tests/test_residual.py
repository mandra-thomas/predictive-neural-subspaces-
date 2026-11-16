import numpy as np

from pns.config import load_config
from pns.pipeline import residualize_session, session_S, window_S
from pns.prior import bayes_optimal_prior, pseudo_sides


def _pre(seed=0, n_trials=400, p=6):
    """Bins with a strong stimOn-locked response (same every trial) plus a prior-driven slow signal."""
    rng = np.random.default_rng(seed)
    starts = np.cumsum(rng.uniform(3, 4.5, n_trials))
    stim = starts + 0.5
    move = stim + rng.uniform(0.2, 0.4, n_trials)
    fb = move + 0.05
    _, side = pseudo_sides(n_trials, rng)
    prior = bayes_optimal_prior(side)
    edges = np.arange(starts[0] - 1, starts[-1] + 5, 0.5)
    c = 0.5 * (edges[:-1] + edges[1:])
    trial = np.clip(np.searchsorted(starts, c) - 1, 0, n_trials - 1)
    evoked = np.zeros(len(c))
    for s in stim:
        dt = c - s
        evoked += np.where((dt >= 0) & (dt < 1.0), np.exp(-np.clip(dt, 0, None) / 0.3), 0)
    rate = 3 + 4 * evoked[:, None] + 3 * (prior[trial] - 0.5)[:, None] * np.linspace(-1, 1, p)
    counts = rng.poisson(np.clip(rate, 0.1, None) ** 2 * 0.5 / 4)            # sqrt(counts) ~ rate-ish
    win = rng.poisson(np.full((n_trials, p), 2.0))
    pre = {"counts": counts, "edges": edges, "valid": np.ones(len(c), bool), "stimOn_times": stim,
           "firstMovement_times": move, "feedback_times": fb, "prior": prior}
    for w in ("pre_stim", "post_stim", "choice", "feedback"):
        pre[f"win_{w}"] = win
    return pre, evoked, prior[trial]


def test_residual_removes_event_locked_and_keeps_prior():
    cfg = load_config()
    pre, evoked, prior_t = _pre()
    S0 = session_S(pre)
    res = residualize_session(pre, cfg)
    S1 = session_S(res)
    r_before = abs(np.corrcoef(S0[:, 0], evoked)[0, 1])
    r_after = abs(np.corrcoef(S1[:, 0], evoked)[0, 1])
    # most event-locked structure is removed (the generator's squared-rate nonlinearity leaves a little)
    assert r_before > 0.3 and r_after < 0.3 * r_before
    # the prior-coupled signal (opposite signs on the first and last unit) survives
    assert np.corrcoef(S1[:, -1] - S1[:, 0], prior_t)[0, 1] > 0.3
    assert window_S(res, "pre_stim").shape == pre["win_pre_stim"].shape
    assert 0 < res["resid_r2"] < 1
