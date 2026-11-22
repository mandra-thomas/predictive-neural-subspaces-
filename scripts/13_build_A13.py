"""Amendment A13 (runs on ICE): build the two derived datasets for the second pilot.

data_mua/        every detected spike in the MOs depth span, binned into 50 um depth "channels" that replace the
                 units; the original session's bins, validity mask, trial events and windows are reused. Channels
                 below binning.min_rate_hz are dropped; sessions with < 10 channels are excluded.
data_ampstable/  the original units restricted to those passing the A12 rate-stability rule and with
                 |Spearman(30 s window median amplitude, time)| < 0.5; sessions with < inclusion.min_units excluded.
Also writes results/a13/units_{eid}.csv (per-unit amplitude and rate trends) for test 2a.
Each folder gets interim/ and meta/frozen.json so scripts 04-06 run unchanged with PNS_DATA=<folder>.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from pns.binning import bin_spikes, window_counts
from pns.config import load_config, load_frozen
from pns.slowmode import bin_centres, spearman, window_edges, window_means

MIN_MUA_CHANNELS = 10
AMP_TREND_MAX = 0.5
MIN_SPIKES_PER_WINDOW = 5


def rate_stable(counts, valid, bin_s, min_rate, n_parts=5):
    parts = np.array_split(np.flatnonzero(valid), n_parts)
    return np.all(np.stack([counts[p].mean(0) / bin_s for p in parts]) >= min_rate, axis=0)


def amp_trends(unit_t, unit_idx, unit_amp, n_units, edges_w):
    w = np.searchsorted(edges_w, unit_t, side="right") - 1
    n_w = len(edges_w) - 1
    med = np.full((n_w, n_units), np.nan)
    ok = (w >= 0) & (w < n_w)
    df = pd.DataFrame({"w": w[ok], "u": unit_idx[ok], "a": unit_amp[ok]})
    g = df.groupby(["w", "u"])["a"]
    agg = pd.DataFrame({"med": g.median(), "n": g.size()}).reset_index()
    agg = agg[agg.n >= MIN_SPIKES_PER_WINDOW]
    med[agg.w.to_numpy(), agg.u.to_numpy()] = agg.med.to_numpy()
    tw = np.arange(n_w, dtype=float)
    return np.array([spearman(med[:, u], tw) for u in range(n_units)]), med


def write_folder(root: Path, frozen: dict, sessions: list, note: str, rows: list):
    (root / "meta").mkdir(parents=True, exist_ok=True)
    fz = dict(frozen)
    fz["sessions"] = sessions
    keep = {s["eid"] for s in sessions}
    fz["checkpoint"] = [e for e in frozen.get("checkpoint", []) if e in keep]
    fz["note"] = note
    (root / "meta" / "frozen.json").write_text(json.dumps(fz, indent=1))
    (root / "meta" / "a13_sessions.json").write_text(json.dumps(rows, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mua-out", default="data_mua")
    ap.add_argument("--amp-out", default="data_ampstable")
    args = ap.parse_args()
    cfg = load_config()
    src = Path(cfg["paths"]["data"])
    res_dir = Path(cfg["paths"]["results"]) / "a13"
    res_dir.mkdir(parents=True, exist_ok=True)
    frozen = load_frozen(cfg)
    bin_s, min_rate = cfg["binning"]["bin_s"], cfg["binning"]["min_rate_hz"]
    mua_root, amp_root = Path(args.mua_out), Path(args.amp_out)
    for r in (mua_root, amp_root):
        if r.resolve() == src.resolve():
            raise SystemExit("output folders must differ from the real data folder")
        (r / "interim").mkdir(parents=True, exist_ok=True)
    mua_keep, amp_keep, mua_rows, amp_rows = [], [], [], []
    for s in frozen["sessions"]:
        eid = s["eid"]
        pre = dict(np.load(src / "interim" / f"{eid}.npz", allow_pickle=False))
        a = dict(np.load(src / "interim" / "a13" / f"{eid}.npz", allow_pickle=False))
        edges, valid = pre["edges"], pre["valid"].astype(bool)

        # ---- multi-unit activity copy
        n_ch = len(a["mua_ch_depth"])
        mrow = {"eid": eid, "subject": s["subject"], "n_channels_total": int(n_ch)}
        if n_ch:
            counts = bin_spikes(a["mua_t"], a["mua_ch"].astype(np.int64), n_ch, edges)
            rate = counts.sum(0) / (edges[-1] - edges[0])
            keep = rate >= min_rate
            mrow["n_channels"] = int(keep.sum())
            if keep.sum() >= MIN_MUA_CHANNELS:
                m = dict(pre)
                m["counts"] = counts[:, keep]
                m["unit_keep"] = keep
                for name, spec in cfg["windows"].items():
                    m[f"win_{name}"] = window_counts(a["mua_t"], a["mua_ch"].astype(np.int64), n_ch,
                                                     np.asarray(pre[spec["event"]], float), spec["win"])[:, keep]
                m["mua_ch_depth"] = a["mua_ch_depth"][keep]
                m["mua_ch_probe"] = a["mua_ch_probe"][keep]
                np.savez(mua_root / "interim" / f"{eid}.npz", **m)
                mua_keep.append(s)
        else:
            mrow["n_channels"] = 0
        mrow["included"] = s in mua_keep
        mua_rows.append(mrow)

        # ---- amplitude-stable copy and per-unit trends
        p = pre["counts"].shape[1]
        ew = window_edges(pre)
        at, _ = amp_trends(a["unit_t"], a["unit_idx"].astype(np.int64), a["unit_amp"], p, ew)
        rw = window_means(bin_centres(pre), pre["counts"] / bin_s, valid, ew)
        tw = np.arange(len(ew) - 1, dtype=float)
        rt = np.array([spearman(rw[:, u], tw) for u in range(p)])
        stable = rate_stable(pre["counts"], valid, bin_s, min_rate)
        amp_ok = np.isfinite(at) & (np.abs(at) < AMP_TREND_MAX)
        sel = stable & amp_ok
        pd.DataFrame({"unit": np.arange(p), "amp_trend": at, "rate_trend": rt, "rate_stable": stable,
                      "amp_stable": amp_ok}).to_csv(res_dir / f"units_{eid}.csv", index=False)
        arow = {"eid": eid, "subject": s["subject"], "n_units": int(p), "n_rate_stable": int(stable.sum()),
                "n_amp_and_rate_stable": int(sel.sum()), "included": bool(sel.sum() >= cfg["inclusion"]["min_units"])}
        amp_rows.append(arow)
        if arow["included"]:
            q = dict(pre)
            q["counts"] = pre["counts"][:, sel]
            for k in [k for k in q if k.startswith("win_")]:
                q[k] = q[k][..., sel]
            uk = q["unit_keep"].copy()
            uk[np.flatnonzero(uk)[~sel]] = False
            q["unit_keep"] = uk
            np.savez(amp_root / "interim" / f"{eid}.npz", **q)
            amp_keep.append(s)
        print(f"{s['subject']:12s} mua channels {mrow.get('n_channels', 0):3d}/{n_ch:3d} "
              f"{'in ' if mrow['included'] else 'OUT'} | amp+rate-stable units {arow['n_amp_and_rate_stable']:3d}/{p:3d} "
              f"{'in' if arow['included'] else 'OUT'}")
    write_folder(mua_root, frozen, mua_keep, "A13 multi-unit (50 um depth channels) copy", mua_rows)
    write_folder(amp_root, frozen, amp_keep, "A13 amplitude- and rate-stable units copy", amp_rows)
    for name, keep in (("multi-unit", mua_keep), ("amplitude-stable", amp_keep)):
        print(f"{name}: {len(keep)}/{len(frozen['sessions'])} sessions, {len({s['subject'] for s in keep})} animals")


if __name__ == "__main__":
    main()
