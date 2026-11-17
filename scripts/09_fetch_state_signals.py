"""Amendment A12: download probe-motion estimates and pupil diameter for every frozen session (needs the IBL
login, so it runs locally). Saves data/interim/state/{eid}.npz; only these derived arrays go to PACE ICE.
Does not analyse anything."""
import numpy as np

from pns.config import load_frozen
from pns.io_ibl import get_one, load_state_signals, probe_unit_counts
from pns.runner import interim_path, log_run, report, run_sessions, select_eids, setup

DRIFT_REVISION = "2024-05-06"        # the spike-sorting revision used by load_good_units


def main():
    args, cfg, _ = setup(__doc__)
    frozen = load_frozen(cfg)
    region = frozen["region"]
    pids = {s["eid"]: [p for p in s["pids"].split(",") if p] for s in frozen["sessions"]}
    one = get_one(cfg)
    out_dir = interim_path(cfg, "x").parent / "state"
    out_dir.mkdir(parents=True, exist_ok=True)

    def work(eid):
        f = out_dir / f"{eid}.npz"
        if f.exists() and not args.force:
            return {"skipped": True}
        w = probe_unit_counts(one, cfg, eid, region)
        sig = load_state_signals(one, eid, pids[eid], w, DRIFT_REVISION)
        np.savez(f, **sig)
        return {"has_pupil": "pupil" in sig, "n_probes": len(pids[eid])}

    res = run_sessions(work, select_eids(cfg, args), 1)          # serial: shared ONE client
    report(res, "09_fetch_state_signals")
    log_run(cfg, "09_fetch_state_signals", f"A12 pilot inputs; {sum(r['ok'] for r in res)}/{len(res)} ok")


if __name__ == "__main__":
    main()
