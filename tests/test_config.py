from pns.config import load_config


def test_config_keys_used_by_scripts_resolve():
    """Every config value the scripts read must exist (guards against YAML keywords like `null:` as keys)."""
    cfg = load_config()
    assert None not in cfg
    assert cfg["pseudo_null"]["n_pseudo"] > 0
    assert cfg["gate"]["n_pseudo"] > 0 and cfg["gate"]["n_folds"] > 1
    assert cfg["model"]["d"] < cfg["inclusion"]["min_units"]
    assert len(cfg["model"]["alphas"]) == cfg["model"]["alpha_log10"][2]
    for spec in cfg["windows"].values():
        assert spec["win"][1] - spec["win"][0] == cfg["binning"]["bin_s"]
    assert cfg["lags_bins"] == sorted(cfg["lags_bins"])


def test_sd_floor_matches_inclusion_threshold():
    """Amendment D10: z-score SD floor = SD of sqrt(Poisson counts) at the inclusion rate."""
    import numpy as np
    from pns.transform import SD_FLOOR, ZScore, poisson_sqrt_sd
    cfg = load_config()
    assert np.isclose(SD_FLOOR, poisson_sqrt_sd(cfg["binning"]["min_rate_hz"], cfg["binning"]["bin_s"]))
    rng = np.random.default_rng(0)
    x = np.sqrt(rng.poisson(0.1 * 0.5, 200000))
    assert abs(x.std() - SD_FLOOR) < 0.005
    # a unit silent in the fitting bins cannot explode on held-out bins
    tr = np.c_[np.zeros(100), rng.normal(size=100)]
    zs = ZScore.fit(tr)
    assert np.all(np.abs(zs.transform(np.array([[3.0, 0.0]]))) < 15)
