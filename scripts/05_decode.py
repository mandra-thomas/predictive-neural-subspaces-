"""Decode task variables from each subspace; pseudo-session null for experimenter-generated variables.

Outputs: results/decoding/{eid}_d{d}.pqt (real scores) and results/null/{eid}_d{d}.pqt (pseudo scores; the
same pseudo sequences are shared by every feature set and lag, enabling paired-difference nulls).
"""
import json

import numpy as np

from pns.config import session_seed
from pns.pipeline import decode_session
from pns.runner import interim_path, load_npz, log_run, out_dir, report, run_sessions, select_eids, setup


def extra(p):
    p.add_argument("--d", type=int, default=None)
    p.add_argument("--n-pseudo", type=int, default=None)


def main():
    args, cfg, n_jobs = setup(__doc__, extra)
    d = args.d or cfg["model"]["d"]
    n_pseudo = args.n_pseudo if args.n_pseudo is not None else cfg["null"]["n_pseudo"]
    sd, dd, nd = out_dir(cfg, "subspaces"), out_dir(cfg, "decoding"), out_dir(cfg, "null")
    eids = select_eids(cfg, args)

    def work(eid):
        tag = f"{eid}_d{d}"
        if (dd / f"{tag}.pqt").exists() and not args.force:
            return {"skipped": True}
        if not (sd / f"{tag}.npz").exists():
            meta = sd / f"{tag}.json"
            if meta.exists() and json.loads(meta.read_text()).get("excluded"):
                return {"excluded": True}
            raise FileNotFoundError("run 04_fit_subspaces first")
        pre = load_npz(interim_path(cfg, eid))
        fits = load_npz(sd / f"{tag}.npz")
        rng = np.random.default_rng(session_seed(eid, cfg["seed"], "null"))   # same pseudo draws for every d
        real, null = decode_session(pre, fits, cfg, rng, n_pseudo)
        real.assign(eid=eid, d=d).to_parquet(dd / f"{tag}.pqt")
        null.assign(eid=eid, d=d, n_pseudo=n_pseudo).to_parquet(nd / f"{tag}.pqt")
        return {"n_real": len(real), "n_null": len(null)}

    res = run_sessions(work, eids, n_jobs)
    report(res, "05_decode")
    log_run(cfg, "05_decode", f"d={d}; n_pseudo={n_pseudo}; {sum(r['ok'] for r in res)}/{len(res)} ok")


if __name__ == "__main__":
    main()
