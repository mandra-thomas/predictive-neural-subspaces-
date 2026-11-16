"""Write a synthetic frozen dataset (frozen.json + interim .npz) so scripts 03-07 can be smoke-tested
without IBL data. Point PNS_DATA / PNS_RESULTS / PNS_FIGURES at a scratch directory first, e.g.

    PNS_DATA=/tmp/pns_syn/data PNS_RESULTS=/tmp/pns_syn/results PNS_FIGURES=/tmp/pns_syn/fig \
        python scripts/make_synthetic_dataset.py --n-sessions 8
"""
import argparse

import numpy as np

from pns.config import ROOT, frozen_path, load_config
from pns.pipeline import preprocess_session
from pns.runner import interim_path, write_json
from pns.synth import simulate_session


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n-sessions", type=int, default=8)
    p.add_argument("--n-trials", type=int, default=500)
    p.add_argument("--prior-gain", type=float, default=2.0)
    p.add_argument("--drift-gain", type=float, default=0.0)
    args = p.parse_args()
    cfg = load_config()
    fp = frozen_path(cfg)
    if fp.resolve().is_relative_to((ROOT / "data").resolve()):
        raise SystemExit("refusing to write synthetic data into the real data/ folder; set PNS_DATA")
    fp.parent.mkdir(parents=True, exist_ok=True)
    sessions = []
    for k in range(args.n_sessions):
        eid = f"synthetic-{k:03d}"
        sim = simulate_session(n_trials=args.n_trials, seed=100 + k, prior_gain=args.prior_gain,
                               drift_gain=args.drift_gain)
        pre = preprocess_session(sim["spike_times"], sim["spike_clusters"], sim["n_units"], sim["trials"],
                                 sim["mask"], sim["wheel_t"], sim["wheel_v"], cfg)
        ip = interim_path(cfg, eid)
        np.savez_compressed(ip, **pre)
        write_json(ip.with_suffix(".status.json"), {"included": True, "reason": "", "synthetic": True})
        sessions.append({"eid": eid, "pids": "none", "subject": f"SYN{k:02d}", "n_units": sim["n_units"],
                         "n_trials_table": args.n_trials})
    write_json(fp, {"region": "SYNTHETIC", "sessions": sessions,
                    "checkpoint": [s["eid"] for s in sessions[: cfg["inclusion"]["n_checkpoint"]]]})
    print(f"wrote {len(sessions)} synthetic sessions under {fp.parent.parent}")


if __name__ == "__main__":
    main()
