"""Bayes-optimal block prior and pseudo-session generation.

`bayes_optimal_prior` is a numpy port of `optimal_Bayesian` in
int-brain-lab/prior-localization (prior_localization/functions/behavior_targets.py, MIT licence):
a forward filter over (block-length counter x block type {0.2, 0.5, 0.8}) with hazard
proportional to exp(-n / tau) on lb <= n <= ub. Sign convention follows the original:
side = +1 means a LEFT stimulus, -1 RIGHT, and the output is P(next stimulus is LEFT).

`pseudo_p_left` is a port of brainbox.task.closed_loop.generate_pseudo_blocks.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

LB, TAU, UB, GAMMA = 20, 60, 100, 0.8
N_BLOCKLENGTHS = 100
N_TYPES = 3
EPS = 1e-15


@lru_cache(maxsize=4)
def _transition(lb: int = LB, tau: float = TAU, ub: int = UB, n_bl: int = N_BLOCKLENGTHS) -> np.ndarray:
    """Transition matrix over flattened states (l * 3 + k), rows = previous, cols = next."""
    n = np.arange(1, n_bl + 1)
    ref = np.exp(-n / tau) * ((n >= lb) & (n <= ub))
    tail = np.cumsum(ref[::-1])[::-1]
    hazard = np.maximum.accumulate(ref / (tail + EPS))
    L = np.zeros((n_bl, n_bl))                     # L[l_prev, l_next]
    L[:, 0] = hazard                               # block switch: counter resets
    L[np.arange(n_bl - 1), np.arange(1, n_bl)] = 1.0 - hazard[:-1]
    b = np.zeros((n_bl, N_TYPES, N_TYPES))         # b[l_next, k_prev, k_next]
    b[1:, [0, 1, 2], [0, 1, 2]] = 1.0              # no switch: keep block type
    b[0, 0, 2] = 1.0                               # 0.2 -> 0.8
    b[0, 2, 0] = 1.0                               # 0.8 -> 0.2
    b[0, 1, 0] = b[0, 1, 2] = 0.5                  # unbiased -> either biased block
    T = L[:, :, None, None] * b[None]              # (l_prev, l_next, k_prev, k_next)
    T = T.transpose(0, 2, 1, 3).reshape(n_bl * N_TYPES, n_bl * N_TYPES)
    T = T + EPS
    T.setflags(write=False)
    return T


def bayes_optimal_prior(side: np.ndarray, act: np.ndarray | None = None, gamma: float = GAMMA) -> np.ndarray:
    """P(stimulus on trial t is LEFT | stimulus sides on trials < t).

    side : (n,) or (m, n) array of +1 (left) / -1 (right). Zeros are rejected because a zero side
           collapses the posterior onto the unbiased block in the original model.
    act  : optional (n,) or (m, n); trials with act == 0 contribute no evidence (Findling's no-go
           handling). Default None = every trial is used (this project's choice).
    Returns an array with the same shape as `side`.
    """
    side = np.asarray(side, dtype=float)
    squeeze = side.ndim == 1
    side = np.atleast_2d(side)
    if not np.all(np.isin(side, (-1.0, 1.0))):
        raise ValueError("side must contain only +1 (left) and -1 (right)")
    m, n = side.shape
    act = np.ones_like(side) if act is None else np.atleast_2d(np.asarray(act, dtype=float))
    T = _transition()
    n_states = T.shape[0]

    # likelihood of the observed side under each block type k = (0.2, 0.5, 0.8) of P(left)
    lk = np.stack([gamma * (side == -1) + (1 - gamma) * (side == 1),
                   np.full_like(side, 0.5),
                   gamma * (side == 1) + (1 - gamma) * (side == -1)], axis=-1)   # (m, n, 3)

    alpha = np.zeros((m, n_states))                     # predictive state for the current trial
    alpha[:, 1] = 1.0                                   # start: counter 0, unbiased block
    pred = np.zeros((m, n, N_TYPES))
    h = np.zeros((m, n_states))
    for t in range(n):
        if t > 0:
            upd = (act[:, t - 1] != 0)[:, None]
            alpha = np.where(upd, h @ T, alpha)
        pred[:, t] = alpha.reshape(m, N_BLOCKLENGTHS, N_TYPES).sum(axis=1)
        h = alpha * np.tile(lk[:, t], N_BLOCKLENGTHS)
        h /= h.sum(axis=1, keepdims=True)
    p_right = pred[..., 0] * gamma + pred[..., 1] * 0.5 + pred[..., 2] * (1 - gamma)
    out = 1.0 - p_right
    return out[0] if squeeze else out


def pseudo_p_left(n_trials: int, rng: np.random.Generator, factor: float = 60, min_: int = 20,
                  max_: int = 100, first5050: int = 90) -> np.ndarray:
    """Port of brainbox generate_pseudo_blocks: integer block lengths 20..99, first 90 trials 0.5."""
    blocks: list[float] = []
    while len(blocks) < n_trials:
        x = rng.exponential(factor)
        while x <= min_ or x >= max_:
            x = rng.exponential(factor)
        if not blocks:
            p = 0.2 if rng.integers(2) == 0 else 0.8
        else:
            p = 0.8 if blocks[-1] == 0.2 else 0.2
        blocks += [p] * int(x)
    return np.array([0.5] * first5050 + blocks[: max(n_trials - first5050, 0)])[:n_trials]


def pseudo_sides(n_trials: int, rng: np.random.Generator, **kw) -> tuple[np.ndarray, np.ndarray]:
    """Pseudo block structure and stimulus sides (+1 left with probability pLeft)."""
    p_left = pseudo_p_left(n_trials, rng, **kw)
    side = np.where(rng.random(n_trials) < p_left, 1.0, -1.0)
    return p_left, side


def side_from_contrasts(contrast_left: np.ndarray, contrast_right: np.ndarray) -> np.ndarray:
    """+1 if the stimulus was on the left (contrastLeft not NaN), else -1. Never 0."""
    cl = np.asarray(contrast_left, dtype=float)
    cr = np.asarray(contrast_right, dtype=float)
    if np.any(np.isnan(cl) & np.isnan(cr)):
        raise ValueError("trial with neither contrastLeft nor contrastRight")
    return np.where(~np.isnan(cl), 1.0, -1.0)


def targets_from_sides(side: np.ndarray, mask: np.ndarray, prior: np.ndarray | None = None) -> dict:
    """Prior, current side and previous side computed on the FULL trial sequence, then masked.

    side : (n,) or (m, n) full unmasked sequence. mask : (n,) boolean trial mask.
    Returns arrays indexed by the masked trials. prev_side for the first trial of the session is NaN.
    """
    side = np.asarray(side, dtype=float)
    if prior is None:
        prior = bayes_optimal_prior(side)
    prev = np.full_like(side, np.nan)
    prev[..., 1:] = side[..., :-1]
    mask = np.asarray(mask, dtype=bool)
    return {"prior": prior[..., mask], "cur_side": side[..., mask], "prev_side": prev[..., mask]}
