"""Aggregate all sessions and run the pre-registered primary tests and secondary analyses.

Writes results/stats/d{d}/{primary,secondary,matrix,geometry_sessions,drift,session_scores}.csv.
"""
import json
from pathlib import Path

import pandas as pd

from pns.analysis import run_analysis
from pns.config import load_frozen
from pns.runner import log_run, out_dir, select_eids, setup


def extra(p):
    p.add_argument("--d", type=int, default=None)


def _read(dirp: Path, eids, d):
    frames = [pd.read_parquet(dirp / f"{e}_d{d}.pqt") for e in eids if (dirp / f"{e}_d{d}.pqt").exists()]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def main():
    args, cfg, _ = setup(__doc__, extra)
    d = args.d or cfg["model"]["d"]
    frozen = load_frozen(cfg)
    subjects = {s["eid"]: s["subject"] for s in frozen["sessions"]}
    eids = select_eids(cfg, args)
    sd = out_dir(cfg, "subspaces")
    metas = {}
    for e in eids:
        f = sd / f"{e}_d{d}.json"
        if f.exists():
            m = json.loads(f.read_text())
            if not m.get("excluded"):
                metas[e] = m
    eids = list(metas)
    if not eids:
        raise SystemExit("no fitted sessions found")
    res = run_analysis(subjects, metas, _read(out_dir(cfg, "estimator"), eids, d),
                       _read(out_dir(cfg, "geometry"), eids, d), _read(out_dir(cfg, "decoding"), eids, d),
                       _read(out_dir(cfg, "null"), eids, d), list(cfg["lags_bins"]),
                       cfg["inclusion"]["min_animals"], cfg["seed"])
    od = out_dir(cfg, "stats", f"d{d}")
    for k in ("primary", "secondary", "matrix", "geometry_sessions", "drift", "session_scores"):
        res[k].to_csv(od / f"{k}.csv", index=False)
    pd.set_option("display.width", 200)
    print(f"{len(eids)} sessions, {res['n_animals']} animals")
    for w in res["warnings"]:
        print("WARNING:", w)
    print(res["primary"][["test", "n", "p", "p_holm"]].to_string(index=False))
    print(f"drift-flagged sessions: {int(res['drift']['drift_flag'].sum())}/{len(res['drift'])}")
    log_run(cfg, "06_stats", f"d={d}; {len(eids)} sessions/{res['n_animals']} animals; "
            + "; ".join(f"{r.test.split(':')[0]} p_holm={r.p_holm:.3g}" for r in res["primary"].itertuples()))


if __name__ == "__main__":
    main()
