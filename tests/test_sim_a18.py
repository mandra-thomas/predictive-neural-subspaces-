"""A18 simulation code: it must reproduce the real pipeline's numbers, and the simulator's real-task path must keep the
task exactly. Real-data checks are skipped when the cached data are absent."""
import numpy as np
import pandas as pd
import pytest

from pns.config import ROOT, load_config, session_seed
from pns.pipeline import decode_session, fit_session, preprocess_session
from pns.sim_a18 import (analyse_session, calibration_stats, history_design, history_residual_targets,
                         pseudo_priors)
from pns.synth import simulate_session, task_from_pre


def _pre(sim, cfg):
    return preprocess_session(sim["spike_times"], sim["spike_clusters"], sim["n_units"], sim["trials"], sim["mask"],
                              sim["wheel_t"], sim["wheel_v"], cfg)


@pytest.fixture(scope="module")
def small():
    cfg = load_config()
    sim = simulate_session(seed=21, n_trials=400)
    return cfg, sim, _pre(sim, cfg)


def test_prior_scores_equal_decode_session(small):
    cfg, _, pre = small
    n = len(pre["side"])
    sn, pn = pseudo_priors(n, np.random.default_rng(5), 30)
    ours = analyse_session(pre, cfg, sn, pn, np.random.default_rng(1))
    fits, *_ = fit_session(pre, cfg, 5, np.random.default_rng(1))
    real, null = decode_session(pre, fits, cfg, np.random.default_rng(5), n_pseudo=30)
    for fs in ("rrr_1", "rrr_60", "pca", "random"):
        r = real.query("feature_set == @fs and variable == 'prior'")["score"].iloc[0]
        nl = null.query("feature_set == @fs and variable == 'prior'")["score"].to_numpy()
        assert ours[f"prior_{fs}_raw"] == pytest.approx(r, abs=1e-12)
        assert ours[f"prior_{fs}"] == pytest.approx(r - np.median(nl), abs=1e-12)
        e = real.query("feature_set == @fs and variable == 'elapsed_time'")["score"].iloc[0]
        assert ours[f"elapsed_{fs}"] == pytest.approx(e, abs=1e-12)


def test_history_residual_removes_exact_history():
    rng = np.random.default_rng(0)
    side = rng.choice([-1.0, 1.0], 300)
    tr = np.arange(10, 300)
    H = history_design(side, tr)
    y = 0.3 + H @ np.array([0.5, 0.2, 0.1, 0.05, 0.01])
    out = history_residual_targets(np.column_stack([y, y]), np.vstack([side, side]), tr)
    assert np.allclose(out, 0, atol=1e-10)


def test_real_task_path_keeps_task_and_rates():
    cfg = load_config()
    path = ROOT / "data" / "interim"
    files = sorted(path.glob("*.npz")) if path.exists() else []
    if not files:
        pytest.skip("no cached real data")
    pre_real = dict(np.load(files[0], allow_pickle=True))
    task, rates = task_from_pre(pre_real)
    sim = simulate_session(seed=1, task=task, unit_rates_hz=rates, slow_noise_loading="separate",
                           drift_mode="lowrank", drift_gain=1.0, history_gain=0.5, evoked_gain=0.5)
    pre = _pre(sim, cfg)
    assert np.array_equal(pre["prior"], pre_real["prior"])
    assert np.array_equal(pre["mask"], pre_real["mask"])
    assert pre["counts"].shape == pre_real["counts"].shape
    r = pre["counts"].sum(0) / (pre["edges"][-1] - pre["edges"][0])
    assert np.median(r / rates) == pytest.approx(1.0, abs=0.05)
    # the pre-stimulus window of trial t carries trial t's value of every task latent
    st = np.asarray(task["stimOn_times"], float)
    ok = np.flatnonzero(np.isfinite(st))
    tot = sim["truth"]["trial_of_t"]
    for lo in (-0.6, -0.11):
        k = np.round((st[ok] + lo) / 0.05).astype(int)
        assert np.array_equal(tot[k], ok)


def test_negative_control_has_no_prior_latent():
    sim = simulate_session(seed=2, n_trials=200, prior_gain=0.0, slow_noise_loading="separate", history_gain=1.0)
    assert np.allclose(sim["truth"]["latents"][:, 0], 0)
    h = sim["truth"]["history"]
    side = sim["truth"]["side"]
    assert np.corrcoef(h[1:], side[:-1])[0, 1] > 0.8          # carries the previous stimulus


def test_calibration_stats_reproduce_published_real_values():
    cfg = load_config()
    a16 = ROOT / "results" / "a16" / "sessions_d5.csv"
    a17 = ROOT / "results" / "a17" / "budget_sessions.csv"
    path = ROOT / "data" / "interim"
    if not (a16.exists() and a17.exists() and path.exists()):
        pytest.skip("no cached real data or results")
    s16 = pd.read_csv(a16).set_index("eid")
    s17 = pd.read_csv(a17).set_index("eid")
    eid = s16.index[0]
    pre = dict(np.load(path / f"{eid}.npz", allow_pickle=True))
    sn, pn = pseudo_priors(len(pre["side"]), np.random.default_rng(session_seed(eid, cfg["seed"], "null")))
    st = calibration_stats(pre, cfg, sn, pn)
    assert st["full_prior_corr"] == pytest.approx(s16.loc[eid, "ridge_full_corr"], abs=1e-10)
    assert st["lowfreq_cos"] == pytest.approx(s17.loc[eid, "lowfreq_cos"], abs=1e-10)
    assert st["triallocked"] == pytest.approx(s17.loc[eid, "triallocked"], abs=1e-10)
    assert st["prior_trial_share_corr"] == pytest.approx(s17.loc[eid, "prior_trial_corr"], abs=1e-10)
