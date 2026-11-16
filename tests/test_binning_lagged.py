import numpy as np

from pns.binning import bin_edges, bin_mean, bin_spikes, invalid_from_intervals, window_counts
from pns.lagged import chunk_folds, lagged_pairs, purged_folds, session_halves


def _spikes(seed=0, n=5000, n_units=7, t1=100.0):
    rng = np.random.default_rng(seed)
    return np.sort(rng.uniform(0, t1, n)), rng.integers(0, n_units, n), n_units


def test_bin_spikes_matches_brute_force():
    t, c, nu = _spikes()
    edges = bin_edges(3.0, 97.3, 0.5)
    counts = bin_spikes(t, c, nu, edges)
    brute = np.array([[np.sum((t >= a) & (t < b) & (c == u)) for u in range(nu)]
                      for a, b in zip(edges[:-1], edges[1:])])
    np.testing.assert_array_equal(counts, brute)


def test_window_counts_matches_brute_force_and_nan_rows():
    t, c, nu = _spikes(1)
    events = np.array([5.0, np.nan, 50.2, 99.0])
    w = window_counts(t, c, nu, events, (-0.6, -0.1))
    for k, e in enumerate(events):
        if np.isnan(e):
            assert np.all(np.isnan(w[k]))
            continue
        for u in range(nu):
            assert w[k, u] == np.sum((t >= e - 0.6) & (t < e - 0.1) & (c == u))


def test_bin_mean_and_invalid():
    edges = bin_edges(0, 3, 1.0)
    np.testing.assert_allclose(bin_mean(np.array([0.1, 0.5, 2.2]), np.array([1.0, 3.0, 5.0]), edges),
                               [2.0, np.nan, 5.0])
    np.testing.assert_array_equal(invalid_from_intervals(edges, np.array([[1.5, 1.7]])), [False, True, False])


def test_pairs_respect_segments_and_validity():
    T, lag = 400, 60
    seg = session_halves(T, 60)
    valid = np.ones(T, bool)
    valid[[10, 300]] = False
    i, j = lagged_pairs(T, lag, valid, seg)
    assert np.all(j - i == lag)
    assert np.all(seg[i] == seg[j]) and np.all(seg[i] >= 0)
    assert not np.isin(i, [10, 300]).any() and not np.isin(j, [10, 300]).any()


def test_purged_folds_never_leak():
    T, lag, emb = 1000, 16, 10
    i, j = lagged_pairs(T, lag)
    folds = purged_folds(i, j, 5, emb)
    bounds = np.linspace(0, T, 6).round().astype(int)
    for k, (train, test) in enumerate(folds):
        s, e = bounds[k], bounds[k + 1]
        assert np.all((i[test] >= s) & (j[test] < e))
        for arr in (i[train], j[train]):
            assert not np.any((arr >= s - emb) & (arr < e + emb))
        assert len(np.intersect1d(train, test)) == 0


def test_chunk_folds_embargo():
    folds = chunk_folds(1000, 20, 5, 10)
    covered = np.concatenate([te for _, te in folds])
    assert np.array_equal(np.sort(covered), np.arange(1000))
    for train, test in folds:
        dist = np.min(np.abs(train[:, None] - test[None, :]), axis=1)
        assert dist.min() > 10
