import numpy as np
import pytest

from pns.geometry import (complement_basis, cov_matched_random, nesting_index, orth, principal_angles,
                          random_floor)


def test_identical_and_rotated_subspaces():
    rng = np.random.default_rng(0)
    A = rng.standard_normal((30, 5))
    R = np.linalg.qr(rng.standard_normal((5, 5)))[0]
    np.testing.assert_allclose(principal_angles(A, A @ R), 0, atol=1e-6)


def test_orthogonal_subspaces():
    I = np.eye(10)
    np.testing.assert_allclose(principal_angles(I[:, :3], I[:, 3:6]), np.pi / 2, atol=1e-12)


def test_known_angles():
    deg = np.array([10, 30, 50])
    I = np.eye(8)
    A = I[:, :3]
    B = np.cos(np.radians(deg)) * I[:, :3] + np.sin(np.radians(deg)) * I[:, 3:6]
    np.testing.assert_allclose(np.degrees(principal_angles(A, B)), deg, atol=1e-8)


def test_isotropic_random_mean_cos2_is_d_over_p():
    rng = np.random.default_rng(1)
    p, d = 20, 5
    vals = [np.mean(np.cos(principal_angles(rng.standard_normal((p, d)), rng.standard_normal((p, d)))) ** 2)
            for _ in range(3000)]
    assert np.mean(vals) == pytest.approx(d / p, abs=0.01)


def test_cov_matched_random_concentrates_on_high_variance():
    rng = np.random.default_rng(2)
    C = np.diag(np.r_[100.0, 100.0, np.ones(18)])
    caps = [nesting_index(np.eye(20)[:, :2], cov_matched_random(C, 2, rng), k=2) for _ in range(300)]
    assert np.mean(caps) > 0.5          # isotropic random subspaces would give d/p = 0.1
    floor = random_floor(C, 2, rng, n=100)
    assert floor["mean_deg_mean"] < 60


def test_nesting_is_asymmetric():
    I = np.eye(10)
    big = I[:, :4]
    small = I[:, [0]] + 0.0
    assert nesting_index(big, small, k=1) == pytest.approx(1.0)
    assert nesting_index(small, big, k=2) == pytest.approx(0.5)


def test_complement_basis():
    I = np.eye(10)
    A = I[:, :3]
    B = I[:, [0]]
    Cb = complement_basis(A, B)
    assert Cb.shape[1] == 2
    np.testing.assert_allclose(Cb.T @ B, 0, atol=1e-12)
    np.testing.assert_allclose(principal_angles(Cb, I[:, 1:3]), 0, atol=1e-6)
    assert orth(A).shape == (10, 3)
