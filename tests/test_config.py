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
