"""A17 Part 0 helpers: block parsing, prior-per-bin mapping, autocorrelation, and the in-memory A16 detrend."""
import importlib.util

import numpy as np
import pytest

from pns.config import ROOT, load_config
from pns.timescales import (acf, completed_blocks, cosine_design, detrend_pre, integrated_timescale,
                            prior_per_bin, session_timescales)


def test_completed_blocks_drop_opening_and_last():
    p = np.array([0.5] * 5 + [0.8] * 3 + [0.2] * 4 + [0.8] * 2)
    assert completed_blocks(p) == [(5, 8, 0.8), (8, 12, 0.2)]


def test_session_timescales_block_minutes():
    st = np.arange(14) * 6.0                       # one trial every 6 s
    pre = {"edges": np.arange(0, 90.5, 0.5), "stimOn_times": st,
           "probabilityLeft": np.array([0.5] * 5 + [0.8] * 3 + [0.2] * 4 + [0.8] * 2)}
    ts = session_timescales(pre)
    assert ts["n_blocks"] == 2
    assert np.allclose(ts["block_trials"], [3, 4])
    assert np.allclose(ts["block_min"], [3 * 6 / 60, 4 * 6 / 60])
    assert ts["stim_interval_s"] == pytest.approx(6.0)


def test_prior_per_bin_assigns_belief_before_each_stimulus():
    edges = np.arange(0, 10.5, 0.5)                # centres 0.25 .. 9.75
    pre = {"edges": edges, "stimOn_times": np.array([2.0, 5.0, np.nan, 8.0]),
           "prior": np.array([0.5, 0.6, 0.9, 0.7])}
    x = prior_per_bin(pre)
    c = 0.5 * (edges[:-1] + edges[1:])
    assert np.all(np.isnan(x[c <= 2.0]))           # before the first stimulus: undefined
    assert np.all(x[(c > 2.0) & (c <= 5.0)] == 0.6)  # bins before stimulus 1 carry prior[1]
    assert np.all(x[(c > 5.0) & (c <= 8.0)] == 0.7)  # trial with NaN stimOn dropped
    assert np.all(np.isnan(x[c > 8.0]))


def test_acf_of_telegraph_matches_theory():
    rng = np.random.default_rng(0)
    p_switch = 0.01                                 # per bin
    flips = rng.random(400_000) < p_switch
    x = np.where(np.cumsum(flips) % 2 == 0, 1.0, -1.0)
    lags = [1, 10, 50, 100]
    r = acf(x, lags)
    assert np.allclose(r, (1 - 2 * p_switch) ** np.array(lags), atol=0.02)


def test_integrated_timescale_of_ar1():
    rng = np.random.default_rng(1)
    phi, n = 0.95, 400_000
    x = np.zeros(n)
    e = rng.standard_normal(n)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + e[t]
    tau, _ = integrated_timescale(x, bin_s=1.0, max_lag_bins=400)
    assert tau == pytest.approx(-1 / np.log(phi), rel=0.1)   # about 19.5 bins


def _script21():
    spec = importlib.util.spec_from_file_location("bd21", ROOT / "scripts" / "21_build_detrend.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_cosine_design_matches_script21():
    t = np.linspace(10, 80, 500)
    assert np.allclose(cosine_design(t, 10.0, 70.0), _script21().design(t, "c", 10.0, 70.0))


@pytest.mark.parametrize("kind", ["c", "q"])
def test_detrend_pre_reproduces_cached_copy(kind):
    cfg = load_config()
    import json
    frozen_p = ROOT / "data" / "meta" / "frozen.json"
    cached_dir = ROOT / f"data_detrend_{kind}" / "interim"
    if not frozen_p.exists() or not cached_dir.exists():
        pytest.skip("real data or A16 detrended copy not available")
    eid = json.loads(frozen_p.read_text())["sessions"][0]["eid"]
    pre = dict(np.load(ROOT / "data" / "interim" / f"{eid}.npz"))
    ref = np.load(cached_dir / f"{eid}.npz")
    out = detrend_pre(pre, cfg, kind)
    assert np.allclose(out["S_resid"], ref["S_resid"])
    assert np.allclose(out["Swin_resid_pre_stim"], ref["Swin_resid_pre_stim"], equal_nan=True)
    assert out["detrend_r2"] == pytest.approx(float(ref["detrend_r2"]))


def test_population_share_equals_r2_for_one_unit():
    from pns.timescales import population_share, residualize
    rng = np.random.default_rng(2)
    x = rng.standard_normal(500)
    w = 0.6 * x + rng.standard_normal(500)
    xr, wr = residualize(x[:, None], None), residualize(w[:, None], None)
    assert population_share(wr, xr)[0] == pytest.approx(np.corrcoef(x, w)[0, 1] ** 2)


def test_signed_event_design_scales_with_weight():
    from pns.pipeline import _raised_cosines
    from pns.timescales import signed_event_design
    t = np.arange(0, 20, 0.5)
    D = signed_event_design(t, np.array([5.0, 12.0, np.nan]), np.array([2.0, -1.0, 3.0]))
    ref = 2 * _raised_cosines(t - 5.0) - _raised_cosines(t - 12.0)
    assert np.allclose(D, ref)


def test_prior_per_bin_maps_pseudo_priors_like_real():
    edges = np.arange(0, 10.5, 0.5)
    pre = {"edges": edges, "stimOn_times": np.array([2.0, 5.0, np.nan, 8.0]),
           "prior": np.array([0.5, 0.6, 0.9, 0.7])}
    null = np.array([[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]])
    out = prior_per_bin(pre, null)
    assert out.shape == (2, 20)
    real = prior_per_bin(pre)
    ok = np.isfinite(real)
    assert np.all(np.isfinite(out[:, ok])) and np.all(np.isnan(out[:, ~ok]))
    assert np.allclose(out[0, ok], np.where(real[ok] == 0.6, 0.2, 0.4))
