"""End-to-end positive and negative controls through the real pipeline functions."""
import numpy as np
import pytest

pytest.importorskip("sklearn")
pytest.importorskip("scipy")

from pns.config import load_config  # noqa: E402
from pns.geometry import principal_angles  # noqa: E402
from pns.pipeline import decode_session, fit_session, preprocess_session  # noqa: E402


def _run(seed=0, n_pseudo=30, **kw):
    from pns.synth import simulate_session
    cfg = load_config()
    cfg["model"]["alphas"] = np.logspace(-3, 1, 5)
    sim = simulate_session(seed=seed, **kw)
    pre = preprocess_session(sim["spike_times"], sim["spike_clusters"], sim["n_units"], sim["trials"],
                             sim["mask"], sim["wheel_t"], sim["wheel_v"], cfg)
    rng = np.random.default_rng(seed)
    fits, est, geo, meta = fit_session(pre, cfg, d=5, rng=rng)
    real, null = decode_session(pre, fits, cfg, rng, n_pseudo=n_pseudo)
    return cfg, sim, pre, fits, est, geo, meta, real, null


@pytest.fixture(scope="module")
def positive():
    return _run(seed=0)


def _score(real, fs, var):
    return float(real.query("feature_set == @fs and variable == @var")["score"].iloc[0])


def _corrected(real, null, fs, var):
    r = _score(real, fs, var)
    n = null.query("feature_set == @fs and variable == @var")["score"].to_numpy()
    return r - np.median(n)


def test_preprocessing_sane(positive):
    _, sim, pre, *_ = positive
    assert pre["prior_pleft_corr"] > 0.5
    assert not np.isnan(pre["counts"]).any()


def test_estimator_ordering(positive):
    *_, est, geo, meta, real, null = positive
    r = est.query("lag == 1").set_index("method")["r2_best"]
    assert r["ridge"] >= r["rrr"] - 0.02
    assert r["rrr"] > r["random"]
    assert r["rrr"] > 0


def test_long_lag_subspace_finds_slow_loading(positive):
    _, sim, pre, fits, *_ = positive
    zsd = fits["z_sd"]
    L_slow = (sim["truth"]["L"][:, 0])[pre["unit_keep"]]
    # the slow loading in z-scored coordinates is approximately L / sd; compare spans loosely
    v30 = fits["Vin_full_60"]
    theta = principal_angles(v30, (L_slow / zsd)[:, None])
    assert np.degrees(theta[0]) < 45


def test_nesting_short_lag_contains_slow_mode(positive):
    *_, meta, real, null = positive
    assert meta["nest_short_contains_long_k1"] > 0.5      # expected nesting under one shared slow mode


def test_prior_null_corrected_positive_at_long_lag(positive):
    *_, real, null = positive
    assert _corrected(real, null, "rrr_60", "prior") > 0
    assert _corrected(real, null, "rrr_60", "prior") >= _corrected(real, null, "rrr_1", "prior") - 0.05


def test_current_side_better_at_short_lag(positive):
    *_, real, null = positive
    assert _score(real, "rrr_1", "cur_side") > 0.6
    assert _score(real, "rrr_1", "cur_side") > _score(real, "rrr_60", "cur_side")


def test_negative_control_drift_without_prior():
    """No prior coding but strong slow drift: the prior must not be significant against its null,
    while elapsed time is decodable (the drift signature)."""
    from pns.stats import null_summary
    *_, real, null = _run(seed=1, prior_gain=0.0, drift_gain=3.0, n_pseudo=100)
    for fs in ("rrr_60", "pca"):
        r = _score(real, fs, "prior")
        n = null.query("feature_set == @fs and variable == 'prior'")["score"].to_numpy()
        assert null_summary(r, n)["p"] > 0.05
    # drift-flag rule: the slow subspace decodes elapsed time above both PCA and random baselines
    e = {fs: _score(real, fs, "elapsed_time") for fs in ("rrr_1", "rrr_60", "pca", "random")}
    assert e["rrr_60"] > max(e["pca"], e["random"]) + 0.05
    assert e["rrr_60"] > e["rrr_1"]
