"""Amendment A14 (runs on ICE): per-unit amplitude-rate coupling and the two amplitude-corrected data copies.

results/a14/units_{eid}.csv  per unit: fluctuation coupling (quadratic and degree-5 time nuisance), total coupling,
                             amplitude trend (A13 definition), early-concentration index of the amplitude change.
data_ampcorr_low/            counts x exp(-beta_session * smoothed relative amplitude), beta_session = median
                             fluctuation coupling (conservative correction).
data_ampcorr_high/           counts x exp(-beta_unit_total * smoothed relative amplitude) (maximal correction).
data_ampcorr_slow/           post hoc: unit coupling fitted and applied on an 11-window smoothed amplitude trajectory.
Post hoc 1b: fluctuation coupling with amplitudes from isolated spikes (preceding same-unit ISI >= 50 ms).
Each copy keeps all original sessions and units, with interim/ and meta/frozen.json so scripts 04-06 run unchanged.
"""
import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from pns.ampcorr import (coupling, early_index, isolated_mask, factor_at_times, factors, relative_amplitude, smooth_fill,
                         window_amplitudes, window_counts_exposure)
from pns.config import load_config, load_frozen
from pns.slowmode import bin_centres, spearman, window_edges

AMP_TREND_MIN = 0.5
ISO_MIN_ISI = 0.05
SLOW_SMOOTH = 11


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--low-out", default="data_ampcorr_low")
    ap.add_argument("--high-out", default="data_ampcorr_high")
    ap.add_argument("--slow-out", default="data_ampcorr_slow")
    args = ap.parse_args()
    cfg = load_config()
    src = Path(cfg["paths"]["data"])
    res_dir = Path(cfg["paths"]["results"]) / "a14"
    res_dir.mkdir(parents=True, exist_ok=True)
    frozen = load_frozen(cfg)
    bin_s = cfg["binning"]["bin_s"]
    roots = {"low": Path(args.low_out), "high": Path(args.high_out), "slow": Path(args.slow_out)}
    for r in roots.values():
        if r.resolve() == src.resolve():
            raise SystemExit("output folders must differ from the real data folder")
        (r / "interim").mkdir(parents=True, exist_ok=True)
    sess_rows = []
    for s in frozen["sessions"]:
        eid = s["eid"]
        pre = dict(np.load(src / "interim" / f"{eid}.npz", allow_pickle=False))
        a = dict(np.load(src / "interim" / "a13" / f"{eid}.npz", allow_pickle=False))
        counts, valid = pre["counts"], pre["valid"].astype(bool)
        p = counts.shape[1]
        ew = window_edges(pre)
        tb = bin_centres(pre)
        n_win, expo = window_counts_exposure(counts, valid, tb, ew, bin_s)
        med = window_amplitudes(a["unit_t"], a["unit_idx"].astype(np.int64), a["unit_amp"], p, ew)
        x = relative_amplitude(med)
        xs = np.column_stack([smooth_fill(x[:, u]) for u in range(p)])
        b2 = coupling(n_win, expo, x, degree=2)
        b5 = coupling(n_win, expo, x, degree=5)
        b0 = coupling(n_win, expo, x, degree=0)
        ut, ui, ua = a["unit_t"], a["unit_idx"].astype(np.int64), a["unit_amp"]
        iso = isolated_mask(ut, ui, ISO_MIN_ISI)
        x_iso = relative_amplitude(window_amplitudes(ut[iso], ui[iso], ua[iso], p, ew))
        b2_iso = coupling(n_win, expo, x_iso, degree=2)
        xh = np.column_stack([smooth_fill(x[:, u], SLOW_SMOOTH) for u in range(p)])
        xh[:, ~np.isfinite(x).any(0)] = np.nan
        b_slow = coupling(n_win, expo, np.where(np.isfinite(x), xh, np.nan), degree=0)
        tw = np.arange(len(ew) - 1, dtype=float)
        trend = np.array([spearman(med[:, u], tw) for u in range(p)])
        early = np.array([early_index(x[:, u], np.sign(trend[u])) if abs(trend[u]) >= AMP_TREND_MIN else np.nan
                          for u in range(p)])
        beta_low = float(np.nanmedian(b2)) if np.isfinite(b2).any() else 0.0
        f_all = {"low": factors(xs, beta_low), "high": factors(xs, b0), "slow": factors(xh, b_slow)}
        pd.DataFrame({"unit": np.arange(p), "beta_fluct_q2": b2, "beta_fluct_q5": b5, "beta_total": b0,
                      "beta_fluct_q2_isolated": b2_iso, "beta_slow": b_slow, "frac_isolated_spikes": float(iso.mean()),
                      "amp_trend": trend, "early_index": early,
                      "factor_low_min": f_all["low"].min(0), "factor_low_max": f_all["low"].max(0),
                      "factor_high_min": f_all["high"].min(0), "factor_high_max": f_all["high"].max(0),
                      "factor_slow_min": f_all["slow"].min(0), "factor_slow_max": f_all["slow"].max(0)}
                     ).to_csv(res_dir / f"units_{eid}.csv", index=False)
        bw = np.clip(np.searchsorted(ew, tb, side="right") - 1, 0, len(ew) - 2)
        for k, f in f_all.items():
            q = dict(pre)
            q["counts"] = counts * f[bw]
            for name, spec in cfg["windows"].items():
                key = f"win_{name}"
                q[key] = pre[key] * factor_at_times(f, np.asarray(pre[spec["event"]], float), ew)
            np.savez(roots[k] / "interim" / f"{eid}.npz", **q)
        row = {"eid": eid, "subject": s["subject"], "n_units": p, "n_units_coupling": int(np.isfinite(b2).sum()),
               "beta_low": beta_low, "median_beta_total": float(np.nanmedian(b0)),
               "frac_units_factor_changed_low": float(np.mean(np.any(np.abs(f_all["low"] - 1) > 0.05, 0))),
               "frac_units_factor_changed_high": float(np.mean(np.any(np.abs(f_all["high"] - 1) > 0.05, 0)))}
        sess_rows.append(row)
        print(f"{s['subject']:12s} units {p:3d} coupling-estimable {row['n_units_coupling']:3d} "
              f"beta_low {beta_low:+.2f}  median beta_total {row['median_beta_total']:+.2f}")
    for k, r in roots.items():
        (r / "meta").mkdir(parents=True, exist_ok=True)
        fz = dict(frozen)
        fz["note"] = f"A14 amplitude-corrected copy ({k} correction)"
        (r / "meta" / "frozen.json").write_text(json.dumps(fz, indent=1))
    pd.DataFrame(sess_rows).to_csv(res_dir / "sessions_build.csv", index=False)


if __name__ == "__main__":
    main()
