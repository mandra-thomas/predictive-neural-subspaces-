import numpy as np
import pytest

from pns.prior import (bayes_optimal_prior, pseudo_p_left, pseudo_sides, side_from_contrasts,
                       targets_from_sides)


def _session(n=800, seed=0):
    rng = np.random.default_rng(seed)
    return pseudo_sides(n, rng)


def test_starts_at_half_and_is_probability():
    _, side = _session()
    p = bayes_optimal_prior(side)
    assert p[0] == pytest.approx(0.5)
    assert np.all((p > 0) & (p < 1))


def test_causal():
    _, side = _session()
    p = bayes_optimal_prior(side)
    for t in [1, 50, 200, 500]:
        s2 = side.copy()
        s2[t:] *= -1
        p2 = bayes_optimal_prior(s2)
        np.testing.assert_allclose(p2[: t + 1], p[: t + 1])   # prior at t uses sides < t only
        assert not np.allclose(p2[t + 1:], p[t + 1:])


def test_tracks_p_left_with_positive_sign():
    corrs, errs = [], []
    for seed in range(5):
        p_left, side = _session(900, seed)
        p = bayes_optimal_prior(side)
        biased = p_left != 0.5
        corrs.append(np.corrcoef(p[biased], p_left[biased])[0, 1])
        errs.append(np.mean(np.abs(p[biased] - p_left[biased])))
    assert np.mean(corrs) > 0.6
    assert np.mean(errs) < 0.2


def test_batch_matches_single():
    sides = np.stack([_session(300, s)[1] for s in range(3)])
    batch = bayes_optimal_prior(sides)
    for i in range(3):
        np.testing.assert_allclose(batch[i], bayes_optimal_prior(sides[i]))


def test_rejects_zero_side():
    with pytest.raises(ValueError):
        bayes_optimal_prior(np.array([1.0, 0.0, -1.0]))


def test_act_zero_skips_evidence():
    _, side = _session(200)
    act = np.ones_like(side)
    act[100] = 0
    p = bayes_optimal_prior(side, act)
    s2 = side.copy()
    s2[100] *= -1
    np.testing.assert_allclose(bayes_optimal_prior(s2, act), p)   # trial 100's side is ignored


def test_matches_reference_implementation():
    try:                                   # skip if torch is absent or broken (e.g. numpy-ABI mismatch)
        import torch  # noqa: F401
        from tests.reference.optimal_bayesian_ref import optimal_Bayesian
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"torch reference unavailable: {type(e).__name__}")
    for seed in range(3):
        _, side = _session(700, seed)
        act = np.ones(len(side))
        act[np.random.default_rng(seed).random(len(side)) < 0.05] = 0
        ref = optimal_Bayesian(act, side).numpy()
        np.testing.assert_allclose(bayes_optimal_prior(side, act), ref, atol=1e-5)
        ref1 = optimal_Bayesian(np.ones(len(side)), side).numpy()
        np.testing.assert_allclose(bayes_optimal_prior(side), ref1, atol=1e-5)


def test_pseudo_blocks_structure():
    rng = np.random.default_rng(1)
    lengths = []
    for _ in range(200):
        p = pseudo_p_left(1000, rng)
        assert len(p) == 1000
        assert np.all(p[:90] == 0.5)
        assert set(np.unique(p[90:])) <= {0.2, 0.8}
        change = np.flatnonzero(np.diff(p[90:]) != 0) + 1
        bounds = np.r_[0, change, len(p) - 90]
        lengths += list(np.diff(bounds)[:-1])            # last block is truncated
        assert np.all(np.diff(p[90:])[change - 1] != 0)
    lengths = np.array(lengths)
    assert lengths.min() >= 20 and lengths.max() <= 99
    # alternation: consecutive blocks differ (guaranteed by construction of change points)


def test_pseudo_side_frequencies():
    rng = np.random.default_rng(2)
    p, s = pseudo_sides(20000, rng)
    assert np.mean(s[p == 0.8] == 1) == pytest.approx(0.8, abs=0.02)
    assert np.mean(s[p == 0.2] == 1) == pytest.approx(0.2, abs=0.02)


def test_side_from_contrasts_and_targets():
    cl = np.array([0.25, np.nan, 0.0, np.nan])
    cr = np.array([np.nan, 1.0, np.nan, 0.0])
    side = side_from_contrasts(cl, cr)
    np.testing.assert_array_equal(side, [1, -1, 1, -1])
    tg = targets_from_sides(side, np.array([True, False, True, True]))
    np.testing.assert_array_equal(tg["cur_side"], [1, 1, -1])
    assert np.isnan(tg["prev_side"][0])
    np.testing.assert_array_equal(tg["prev_side"][1:], [-1, 1])
