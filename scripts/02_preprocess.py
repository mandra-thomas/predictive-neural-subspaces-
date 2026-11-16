"""Download and preprocess each frozen session: bins, trial windows, wheel speed, Bayes-optimal prior.

Writes data/interim/{eid}.npz and {eid}_units.csv. Sessions failing the live checks (masked trials < min,
units < min, prior not positively correlated with probabilityLeft, BWM truncation assertion) are recorded
in data/interim/{eid}.status.json and skipped downstream.
"""
import json

import numpy as np

from pns.config import load_frozen
from pns.io_ibl import get_one, load_session
from pns.pipeline import preprocess_session
from pns.runner import interim_path, log_run, report, run_sessions, select_eids, setup, write_json


def main():
    args, cfg, n_jobs = setup(__doc__)
    frozen = load_frozen(cfg)
    region = frozen["region"]
    pids_of = {s["eid"]: s["pids"].split(",") for s in frozen["sessions"]}
    eids = select_eids(cfg, args)
    inc = cfg["inclusion"]

    def work(eid):
        out = interim_path(cfg, eid)
        status_p = out.with_suffix(".status.json")
        if out.exists() and not args.force:
            return json.loads(status_p.read_text()) if status_p.exists() else {"skipped": True}
        one = get_one(cfg)
        try:
            raw = load_session(one, cfg, eid, pids_of[eid], region)
        except AssertionError as e:          # brainwidemap truncate_to_pass could not make the session pass
            status = {"included": False, "reason": f"truncate_to_pass: {e}"}
            write_json(status_p, status)
            return status
        pre = preprocess_session(raw["spike_times"], raw["spike_clusters"], raw["n_units"], raw["trials"],
                                 raw["mask"], raw["wheel_t"], raw["wheel_v"], cfg)
        n_trials, p = int(pre["mask"].sum()), int(pre["counts"].shape[1])
        reasons = []
        if n_trials < inc["min_trials"]:
            reasons.append(f"masked trials {n_trials} < {inc['min_trials']}")
        if p < inc["min_units"]:
            reasons.append(f"units after rate filter {p} < {inc['min_units']}")
        if not pre["prior_pleft_corr"] > 0:
            reasons.append(f"prior/probabilityLeft corr {pre['prior_pleft_corr']:.2f} <= 0 (sign error?)")
        np.savez_compressed(out, **pre)
        raw["units"].assign(kept=pre["unit_keep"]).to_csv(out.with_name(f"{eid}_units.csv"), index=False)
        status = {"included": not reasons, "reason": "; ".join(reasons), "n_trials_masked": n_trials,
                  "n_units": p, "T_bins": int(pre["counts"].shape[0]), "prior_pleft_corr": pre["prior_pleft_corr"],
                  "median_trial_s": pre["median_trial_s"]}
        write_json(status_p, status)
        return status

    res = run_sessions(work, eids, n_jobs)
    report(res, "02_preprocess")
    inc_n = sum(1 for r in res if r.get("included"))
    for r in res:
        if r["ok"] and r.get("included") is False:
            print(f"  excluded {r['eid']}: {r['reason']}")
    log_run(cfg, "02_preprocess", f"{len(eids)} sessions requested; {inc_n} included")


if __name__ == "__main__":
    main()
