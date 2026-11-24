"""Synthetic IBL-like sessions with known slow (prior) and fast (stimulus) latents, emitted as spike times.

Latents on a fine grid (dt = 0.05 s):
  slow  : prior_gain * (prior(t) - 0.5) + slow AR noise (autocorrelation 0.99 per 0.5 s)
  fast  : stim_gain * side * contrast-weighted exp(-(t - stimOn)/0.3 s) transient + fast AR noise (0.5 per 0.5 s)
  drift : drift_gain * smooth random walk independent of the task (negative control)
Neurons: log-rate = b + L @ latents + shared anisotropic noise factors; Poisson spikes.

A18 additions (defaults reproduce the original output bit for bit; every new random draw comes from a separate
generator np.random.default_rng([seed, 17]) so existing draws are unchanged):
  drift_mode "lowrank"  : drift_rank latent processes, each a unit-variance mix of a >= 20 min part (linear ramp plus
                          cosines, the span the A16 cosine detrend removes) and a 5-20 min part (weight drift_mid),
                          with variances decaying by drift_decay per component, on their own loadings
  drift_mode "per_unit" : the same kind of process drawn independently for every unit (rank about p)
  slow_noise_loading "separate" : the AR(0.99) slow noise gets its own loading instead of riding on the prior loading
"""
from __future__ import annotations

import numpy as np

from .prior import bayes_optimal_prior, pseudo_sides

DT = 0.05


def _ar(n: int, phi_per_half_s: float, sd: float, rng) -> np.ndarray:
    phi = phi_per_half_s ** (DT / 0.5)
    x = np.zeros(n)
    e = rng.standard_normal(n) * sd * np.sqrt(1 - phi ** 2)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + e[t]
    return x


def _slow_process(t: np.ndarray, rng, mid: float, min_period_min: float = 20.0, mid_period_min: float = 5.0):
    """Unit-variance drift on times t (s): linear ramp + cosines with periods >= min_period (decaying 1/k), plus
    `mid` x a unit-variance mix of cosines with periods between mid_period and min_period."""
    u = (t - t[0]) / (t[-1] - t[0])
    length = (t[-1] - t[0]) / 60.0
    k_lo = int(np.floor(2 * length / min_period_min))
    k_hi = int(np.floor(2 * length / mid_period_min))
    low = rng.choice([-1.0, 1.0]) * (u - 0.5) * np.sqrt(12)
    for k in range(1, k_lo + 1):
        low = low + rng.standard_normal() / k * np.cos(np.pi * k * u)
    low = (low - low.mean()) / low.std()
    x = low
    if mid > 0 and k_hi > k_lo:
        m = sum(rng.standard_normal() / np.sqrt(k) * np.cos(np.pi * k * u + rng.uniform(0, 2 * np.pi))
                for k in range(k_lo + 1, k_hi + 1))
        x = low + mid * (m - m.mean()) / m.std()
    return (x - x.mean()) / x.std()


def simulate_session(n_trials: int = 600, n_units: int = 40, seed: int = 0, prior_gain: float = 2.0,
                     stim_gain: float = 1.5, drift_gain: float = 0.0, slow_noise: float = 0.3,
                     base_rate_hz: float = 8.0, loading_scale: float = 0.6, drift_mode: str = "walk",
                     drift_rank: int = 3, drift_decay: float = 0.3, drift_mid: float = 0.0,
                     slow_noise_loading: str = "shared") -> dict:
    if drift_mode not in ("walk", "lowrank", "per_unit") or slow_noise_loading not in ("shared", "separate"):
        raise ValueError(f"unknown drift_mode {drift_mode!r} or slow_noise_loading {slow_noise_loading!r}")
    rng = np.random.default_rng(seed)
    rng2 = np.random.default_rng([seed, 17])          # A18: all new draws
    # --- trial structure
    dur = rng.uniform(3.0, 5.0, n_trials)
    starts = 1.0 + np.r_[0, np.cumsum(dur)[:-1]]
    stim_on = starts + rng.uniform(0.4, 0.7, n_trials)
    first_move = stim_on + rng.uniform(0.15, 0.45, n_trials)
    feedback = first_move + 0.05
    p_left, side = pseudo_sides(n_trials, rng)
    prior = bayes_optimal_prior(side)
    contrast = rng.choice([0.0, 0.0625, 0.125, 0.25, 1.0], n_trials)
    p_correct = 0.5 + 0.45 * np.minimum(contrast / 0.25, 1.0)
    correct = rng.random(n_trials) < p_correct
    choice = np.where(correct, side, -side)              # +1 = left-stimulus choice in this convention
    trials = {
        "intervals": np.column_stack([starts, starts + dur]),
        "stimOn_times": stim_on, "firstMovement_times": first_move, "feedback_times": feedback,
        "contrastLeft": np.where(side > 0, contrast, np.nan), "contrastRight": np.where(side < 0, contrast, np.nan),
        "probabilityLeft": p_left, "choice": choice.astype(float), "feedbackType": np.where(correct, 1.0, -1.0),
    }
    # --- latents on the fine grid
    t_end = starts[-1] + dur[-1] + 1.0
    t = np.arange(0, t_end, DT)
    n = len(t)
    trial_of_t = np.clip(np.searchsorted(starts, t, side="right") - 1, 0, n_trials - 1)
    slow_ar = _ar(n, 0.99, slow_noise, rng)
    slow = prior_gain * (prior[trial_of_t] - 0.5) + (slow_ar if slow_noise_loading == "shared" else 0.0)
    fast = _ar(n, 0.5, 0.3, rng)
    k_on = np.searchsorted(t, stim_on)
    kern = np.exp(-np.arange(0, int(1.5 / DT)) * DT / 0.3)
    drive = np.zeros(n)
    for k in range(n_trials):
        if contrast[k] > 0:
            seg = slice(k_on[k], min(k_on[k] + len(kern), n))
            drive[seg] += side[k] * np.sqrt(contrast[k]) * kern[: seg.stop - seg.start]
    fast = fast + stim_gain * drive
    drift = drift_gain * np.convolve(np.cumsum(rng.standard_normal(n)) * 0.02, np.ones(400) / 400, mode="same")
    if drift_mode != "walk":
        drift = np.zeros(n)                              # drift enters through the extra term below instead
    latents = np.column_stack([slow, fast, drift])
    # --- neurons: non-orthogonal loadings, anisotropic shared noise
    L = rng.standard_normal((n_units, 3)) * loading_scale
    L[:, 1] += 0.3 * L[:, 0]
    noise = np.column_stack([_ar(n, 0.3, 0.4, rng), _ar(n, 0.3, 0.2, rng)])
    Ln = rng.standard_normal((n_units, 2))
    log_rate = np.log(base_rate_hz) + latents @ L.T + noise @ Ln.T
    truth_extra = {}
    if slow_noise_loading == "separate":
        L_ar = rng2.standard_normal(n_units) * loading_scale
        log_rate = log_rate + np.outer(slow_ar, L_ar)
        truth_extra["L_slow_noise"] = L_ar
    if drift_mode != "walk":
        tc = np.arange(t[0], t[-1] + 0.5, 0.5)           # drift drawn on a 0.5 s grid, interpolated to the fine grid
        if drift_mode == "lowrank":
            Dc = np.column_stack([_slow_process(tc, rng2, drift_mid) * drift_decay ** (r / 2)
                                  for r in range(drift_rank)])
            Ld = rng2.standard_normal((n_units, drift_rank)) * loading_scale
            truth_extra.update({"drift_latents_coarse": Dc, "drift_loadings": Ld})
            Dunits_c = Dc @ Ld.T
        else:
            g = rng2.standard_normal(n_units) * loading_scale
            Dunits_c = np.column_stack([_slow_process(tc, rng2, drift_mid) for _ in range(n_units)]) * g
            truth_extra["drift_unit_gain"] = g
        Dunits = np.column_stack([np.interp(t, tc, Dunits_c[:, u]) for u in range(n_units)])
        log_rate = log_rate + drift_gain * Dunits
        truth_extra["drift_units_coarse_t"] = tc
    lam = np.exp(np.clip(log_rate, -10, 5)) * DT
    counts = rng.poisson(lam)
    tt, uu = np.nonzero(counts)
    reps = counts[tt, uu]
    spike_t = np.repeat(t[tt], reps) + rng.uniform(0, DT, reps.sum())
    spike_c = np.repeat(uu, reps)
    order = np.argsort(spike_t)
    # --- wheel: velocity bump after first movement, sign = choice
    wheel_v = np.zeros(n)
    k_mv = np.searchsorted(t, first_move)
    for k in range(n_trials):
        wheel_v[k_mv[k]: k_mv[k] + 6] += choice[k] * 3.0
    return {"spike_times": spike_t[order], "spike_clusters": spike_c[order], "n_units": n_units,
            "trials": trials, "mask": np.ones(n_trials, bool), "wheel_t": t, "wheel_v": wheel_v,
            "truth": {"L": L, "latents": latents, "prior": prior, "side": side, **truth_extra}}
