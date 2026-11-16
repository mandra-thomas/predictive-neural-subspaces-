import numpy as np
import pytest

sk = pytest.importorskip("sklearn")

from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402

from pns.decode import auc_cv, auc_score, logistic_fit, r2_cv  # noqa: E402
from pns.lagged import contiguous_folds  # noqa: E402
from pns.prior import bayes_optimal_prior, pseudo_sides  # noqa: E402
from pns.stats import holm, null_summary, wilcoxon_greater  # noqa: E402


def test_logistic_matches_sklearn():
    rng = np.random.default_rng(0)
    X = rng.standard_normal((400, 5))
    y = (X @ rng.standard_normal(5) + 0.5 + rng.standard_normal(400) > 0).astype(float)
    for C in (0.1, 1.0, 10.0):
        w, b = logistic_fit(X, y, C)
        ref = LogisticRegression(C=C, tol=1e-12, max_iter=10000).fit(X, y)
        np.testing.assert_allclose(w, ref.coef_[0], atol=1e-5)
        assert b == pytest.approx(ref.intercept_[0], abs=1e-5)


def test_auc_matches_sklearn_with_ties():
    rng = np.random.default_rng(1)
    y = rng.integers(0, 2, 300).astype(float)
    s = np.round(rng.standard_normal(300) + y, 1)
    assert auc_score(y, s) == pytest.approx(roc_auc_score(y, s))


def test_auc_noise_and_separable():
    rng = np.random.default_rng(2)
    n = 600
    y = rng.integers(0, 2, n)
    folds = contiguous_folds(n, 5)
    assert auc_cv(rng.standard_normal((n, 4)), y, folds) == pytest.approx(0.5, abs=0.06)
    F = np.column_stack([y + 0.05 * rng.standard_normal(n), rng.standard_normal(n)])
    assert auc_cv(F, y, folds) > 0.99


def test_r2_multi_target_matches_single():
    rng = np.random.default_rng(3)
    F = rng.standard_normal((300, 3))
    Y = F @ rng.standard_normal((3, 4)) + rng.standard_normal((300, 4))
    folds = contiguous_folds(300, 5)
    multi = r2_cv(F, Y, folds)
    np.testing.assert_allclose(multi, [r2_cv(F, Y[:, k], folds) for k in range(4)])


def test_pseudo_null_removes_drift_correlation():
    """A slowly drifting feature unrelated to the task inflates raw prior R^2 but not the null-corrected one."""
    rng = np.random.default_rng(4)
    n = 700
    _, side = pseudo_sides(n, rng)
    prior = bayes_optimal_prior(side)
    walk = np.cumsum(rng.standard_normal(n))
    F = np.column_stack([np.convolve(walk, np.ones(50) / 50, mode="same"), rng.standard_normal(n)])
    folds = contiguous_folds(n, 5)
    real = r2_cv(F, prior, folds)
    sides = np.stack([pseudo_sides(n, rng)[1] for _ in range(200)])
    null = r2_cv(F, bayes_optimal_prior(sides).T, folds)
    s = null_summary(real, null)
    assert s["p"] > 0.01                          # not significant
    assert null.std() > 0.005                     # the null is wide, as expected for slow features


def test_stats_helpers():
    assert wilcoxon_greater(np.arange(1, 11))["p"] == pytest.approx(1 / 2 ** 10)
    adj = holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adj["a"] == pytest.approx(0.03) and adj["c"] == pytest.approx(0.06) and adj["b"] == pytest.approx(0.06)
