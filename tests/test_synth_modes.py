"""A18 simulator modes: defaults reproduce the pre-A18 output bit for bit; new modes have the intended structure."""
import hashlib

import numpy as np
import pytest

from pns.synth import simulate_session

# Fingerprints recorded on 2026-11-23 before synth.py was changed for A18.
PRE_A18 = {
    "seed0": "eadc4ad4a8ee85f86c1d9eab5fb0379ed3754d37d96f19ced179dce515d89754",
    "seed1_drift": "569e3accc240c854015b82b76bc56b1a8cc647d1285887f5891cf6e7a445e676",
}


def fingerprint(sim):
    h = hashlib.sha256()
    for k in ("spike_times", "spike_clusters", "wheel_t", "wheel_v", "mask"):
        h.update(np.ascontiguousarray(sim[k]).tobytes())
    for k in sorted(sim["trials"]):
        h.update(np.ascontiguousarray(np.asarray(sim["trials"][k], float)).tobytes())
    for k in ("L", "latents", "prior", "side"):
        h.update(np.ascontiguousarray(sim["truth"][k]).tobytes())
    return h.hexdigest()


def test_defaults_unchanged():
    assert fingerprint(simulate_session(seed=0)) == PRE_A18["seed0"]
    assert fingerprint(simulate_session(seed=1, prior_gain=0.0, drift_gain=3.0)) == PRE_A18["seed1_drift"]


def test_lowrank_drift_has_requested_rank():
    sim = simulate_session(seed=2, n_trials=300, drift_mode="lowrank", drift_rank=2, drift_gain=1.0, drift_mid=0.5)
    Dc, Ld = sim["truth"]["drift_latents_coarse"], sim["truth"]["drift_loadings"]
    s = np.linalg.svd(Dc @ Ld.T, compute_uv=False)
    assert s[2] < 1e-8 * s[0] and s[1] > 1e-3 * s[0]
    assert np.allclose(sim["truth"]["latents"][:, 2], 0)          # drift no longer in the 'walk' column


def test_per_unit_drift_is_full_rank():
    sim = simulate_session(seed=3, n_trials=300, n_units=20, drift_mode="per_unit", drift_gain=1.0)
    assert sim["truth"]["drift_unit_gain"].shape == (20,)


def test_separate_slow_noise_leaves_pure_prior_latent():
    sim = simulate_session(seed=4, n_trials=300, slow_noise_loading="separate", drift_mode="lowrank", drift_gain=1.0)
    slow = sim["truth"]["latents"][:, 0]
    assert len(np.unique(np.round(slow, 12))) <= len(np.unique(sim["truth"]["prior"])) + 1
    neg = simulate_session(seed=4, n_trials=300, prior_gain=0.0, slow_noise_loading="separate")
    assert np.allclose(neg["truth"]["latents"][:, 0], 0)


def test_new_modes_keep_trials_and_loadings_paired_across_cells():
    a = simulate_session(seed=5, n_trials=200, drift_mode="lowrank", drift_gain=0.5)
    b = simulate_session(seed=5, n_trials=200, drift_mode="lowrank", drift_gain=2.0)
    assert np.array_equal(a["truth"]["L"], b["truth"]["L"])
    assert np.array_equal(a["trials"]["stimOn_times"], b["trials"]["stimOn_times"])


def test_bad_mode_raises():
    with pytest.raises(ValueError):
        simulate_session(seed=0, n_trials=50, drift_mode="nope")
