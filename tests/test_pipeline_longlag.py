"""A17 part 2: adding long lags with model.alpha_lags must leave everything computed for the original lags unchanged,
and a lag that is too long for the CV folds must raise instead of failing silently."""
import copy

import numpy as np
import pytest

pytest.importorskip("sklearn")

from pns.config import load_config  # noqa: E402
from pns.pipeline import fit_session, preprocess_session  # noqa: E402
from pns.synth import simulate_session  # noqa: E402

BASE = [1, 4, 16, 60]


@pytest.fixture(scope="module")
def pre_cfg():
    cfg = load_config()
    cfg["model"]["alphas"] = np.logspace(-3, 1, 5)
    sim = simulate_session(seed=3)
    pre = preprocess_session(sim["spike_times"], sim["spike_clusters"], sim["n_units"], sim["trials"],
                             sim["mask"], sim["wheel_t"], sim["wheel_v"], cfg)
    return pre, cfg


def _fit(pre, cfg, lags, alpha_lags=None):
    c = copy.deepcopy(cfg)
    c["lags_bins"] = lags
    if alpha_lags is not None:
        c["model"]["alpha_lags"] = alpha_lags
    return fit_session(pre, c, d=5, rng=np.random.default_rng(7))


def test_alpha_lags_reproduce_original_fit(pre_cfg):
    pre, cfg = pre_cfg
    f0, e0, _, m0 = _fit(pre, cfg, BASE)
    f1, e1, _, m1 = _fit(pre, cfg, BASE + [120], alpha_lags=BASE)
    assert f1["alpha"] == f0["alpha"]
    for lag in BASE:
        assert np.array_equal(f1[f"Vin_full_{lag}"], f0[f"Vin_full_{lag}"])
    assert np.array_equal(f1["V_random"], f0["V_random"])
    assert np.array_equal(f1["V_pca"], f0["V_pca"])
    assert {k: v for k, v in m1.items() if k.startswith("floor_")} == {k: v for k, v in m0.items() if k.startswith("floor_")}
    e0i = e0.set_index(["lag", "method"])
    e1i = e1[e1.lag.isin(BASE)].set_index(["lag", "method"])
    assert np.array_equal(e1i.loc[e0i.index, "r2_session_alpha"].to_numpy(), e0i["r2_session_alpha"].to_numpy())
    assert m1["alpha_lags"] == BASE and 120 in m1["min_test_pairs_per_fold"]
    assert "alpha_lags" not in m0                     # default runs write the same meta keys as before


def test_alpha_lags_must_be_subset(pre_cfg):
    pre, cfg = pre_cfg
    with pytest.raises(ValueError, match="subset"):
        _fit(pre, cfg, BASE, alpha_lags=[1, 99])


def test_too_long_lag_raises(pre_cfg):
    pre, cfg = pre_cfg
    T = len(pre["valid"])
    with pytest.raises(ValueError, match="too long|no lagged pairs|without pairs"):
        _fit(pre, cfg, BASE + [T // 5 + 10], alpha_lags=BASE)
