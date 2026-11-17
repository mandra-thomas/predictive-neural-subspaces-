"""Amendment A12, test 1: build a stable-units copy of the interim data.

A unit is stable if its mean rate is >= binning.min_rate_hz in each of five equal fifths of the session's valid
task-epoch bins. Sessions with fewer than inclusion.min_units stable units are excluded. Writes
<out>/interim/{eid}.npz and <out>/meta/frozen.json (the frozen session list restricted to included sessions),
so scripts 04-06 run unchanged with PNS_DATA=<out>.

Usage: python scripts/10_stable_units.py --out data_stable
"""
import argparse
import json
import shutil
from pathlib import Path

import numpy as np

from pns.config import load_config, load_frozen

N_PARTS = 5


def stable_mask(counts: np.ndarray, valid: np.ndarray, bin_s: float, min_rate: float) -> np.ndarray:
    idx = np.flatnonzero(valid)
    parts = np.array_split(idx, N_PARTS)
    rates = np.stack([counts[p].mean(0) / bin_s for p in parts])          # (5, p)
    return np.all(rates >= min_rate, axis=0)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="data_stable")
    args = ap.parse_args()
    cfg = load_config()
    src = Path(cfg["paths"]["data"])
    out = Path(args.out)
    if out.resolve() == src.resolve():
        raise SystemExit("--out must differ from the real data folder")
    (out / "interim").mkdir(parents=True, exist_ok=True)
    (out / "meta").mkdir(parents=True, exist_ok=True)
    frozen = load_frozen(cfg)
    keep_sessions, rows = [], []
    for s in frozen["sessions"]:
        eid = s["eid"]
        pre = dict(np.load(src / "interim" / f"{eid}.npz", allow_pickle=False))
        m = stable_mask(pre["counts"], pre["valid"].astype(bool), cfg["binning"]["bin_s"],
                        cfg["binning"]["min_rate_hz"])
        n_stable = int(m.sum())
        rows.append({"eid": eid, "subject": s["subject"], "n_units": int(len(m)), "n_stable": n_stable,
                     "included": n_stable >= cfg["inclusion"]["min_units"]})
        if n_stable < cfg["inclusion"]["min_units"]:
            continue
        pre["counts"] = pre["counts"][:, m]
        for k in [k for k in pre if k.startswith("win_")]:
            pre[k] = pre[k][..., m]
        if "unit_keep" in pre and pre["unit_keep"].dtype == bool and pre["unit_keep"].sum() == len(m):
            uk = pre["unit_keep"].copy()
            uk[np.flatnonzero(uk)[~m]] = False
            pre["unit_keep"] = uk
        np.savez(out / "interim" / f"{eid}.npz", **pre)
        keep_sessions.append(s)
    fz = dict(frozen)
    fz["sessions"] = keep_sessions
    fz["checkpoint"] = [e for e in frozen.get("checkpoint", []) if e in {s["eid"] for s in keep_sessions}]
    fz["note"] = "A12 stable-units copy (units >= min rate in every fifth of the session)"
    (out / "meta" / "frozen.json").write_text(json.dumps(fz, indent=1))
    (out / "meta" / "stable_units.json").write_text(json.dumps(rows, indent=1))
    for r in rows:
        print(f"{r['subject']:12s} {r['n_stable']:3d}/{r['n_units']:3d} stable  {'in' if r['included'] else 'EXCLUDED'}")
    print(f"{len(keep_sessions)}/{len(rows)} sessions included, "
          f"{len({s['subject'] for s in keep_sessions})} animals")


if __name__ == "__main__":
    main()
