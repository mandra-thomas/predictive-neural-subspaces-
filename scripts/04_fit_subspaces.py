"""Fit lagged reduced-rank ridge subspaces (full session and halves), the estimator check and geometry.

Outputs per session (d in the file name): results/subspaces/{eid}_d{d}.npz (+ .json meta),
results/estimator/{eid}_d{d}.pqt, results/geometry/{eid}_d{d}.pqt.
"""
import json

import numpy as np

from pns.config import session_seed
from pns.pipeline import fit_session
from pns.runner import (interim_path, load_npz, log_run, out_dir, report, run_sessions, select_eids, setup,
                        write_json)


def extra(p):
    p.add_argument("--d", type=int, default=None, help="subspace dimension (default: config model.d)")


def main():
    args, cfg, n_jobs = setup(__doc__, extra)
    d = args.d or cfg["model"]["d"]
    sd, ed, gd = out_dir(cfg, "subspaces"), out_dir(cfg, "estimator"), out_dir(cfg, "geometry")
    eids = select_eids(cfg, args)

    def work(eid):
        tag = f"{eid}_d{d}"
        if (sd / f"{tag}.json").exists() and not args.force:
            return json.loads((sd / f"{tag}.json").read_text())
        ip = interim_path(cfg, eid)
        st = ip.with_suffix(".status.json")
        if st.exists() and not json.loads(st.read_text()).get("included", True):
            meta = {"excluded": True, "reason": json.loads(st.read_text()).get("reason", "")}
            write_json(sd / f"{tag}.json", meta)
            return meta
        pre = load_npz(ip)
        p = pre["counts"].shape[1]
        if d == 10 and p < cfg["model"]["d10_min_units"]:
            meta = {"excluded": True, "reason": f"d=10 needs > 40 units (p={p})"}
            write_json(sd / f"{tag}.json", meta)
            return meta
        rng = np.random.default_rng(session_seed(eid, cfg["seed"], f"fit{d}"))
        fits, est, geo, meta = fit_session(pre, cfg, d, rng)
        np.savez_compressed(sd / f"{tag}.npz", **fits)
        est.assign(eid=eid, d=d).to_parquet(ed / f"{tag}.pqt")
        geo.assign(eid=eid, d=d).to_parquet(gd / f"{tag}.pqt")
        write_json(sd / f"{tag}.json", meta)
        return meta

    res = run_sessions(work, eids, n_jobs)
    report(res, "04_fit_subspaces")
    weak = [(r["eid"], [k for k, v in r.get("weak_lag", {}).items() if v]) for r in res if r["ok"]]
    for eid, lags in weak:
        if lags:
            print(f"  weak lags (held-out R2 <= 0 for every alpha) in {eid}: {lags}")
    log_run(cfg, "04_fit_subspaces", f"d={d}; {sum(r['ok'] for r in res)}/{len(res)} ok")


if __name__ == "__main__":
    main()
