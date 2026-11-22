"""Amendment A15 (local, cached data only): build data_region2/, the largest non-MOs region per frozen session.

Region rule: the non-MOs Beryl region (excluding root and void) with the most good units over the session's MOs
probes; ties alphabetical. Preprocessing and inclusion are identical to scripts/02_preprocess.py. Sessions failing
inclusion are left out of data_region2/meta/frozen.json and listed in data_region2/meta/a15_sessions.json.
"""
import argparse
import collections
import json
from pathlib import Path

import numpy as np

from pns.config import load_config, load_frozen
from pns.io_ibl import get_one, load_session
from pns.pipeline import preprocess_session

EXCLUDE = {"MOs", "root", "void"}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="data_region2")
    args = ap.parse_args()
    cfg = load_config()
    frozen = load_frozen(cfg)
    inc = cfg["inclusion"]
    root = Path(args.out)
    if root.resolve() == Path(cfg["paths"]["data"]).resolve():
        raise SystemExit("output folder must differ from the real data folder")
    (root / "interim").mkdir(parents=True, exist_ok=True)
    (root / "meta").mkdir(parents=True, exist_ok=True)
    one = get_one(cfg)
    from brainwidemap.bwm_loading import load_good_units
    from iblatlas.regions import BrainRegions
    br = BrainRegions()
    keep, rows = [], []
    for s in frozen["sessions"]:
        eid, pids = s["eid"], s["pids"].split(",")
        cnt, by_probe = collections.Counter(), collections.defaultdict(set)
        for pid in pids:
            _, cl = load_good_units(one, pid, qc=1.0)
            for r, n in collections.Counter(br.id2acronym(cl["atlas_id"].to_numpy(), mapping="Beryl")).items():
                if r not in EXCLUDE:
                    cnt[r] += n
                    by_probe[r].add(pid)
        cands = sorted(((-n, r) for r, n in cnt.items() if n >= inc["min_units"]))
        row = {"eid": eid, "subject": s["subject"], "region2": None, "included": False}
        if not cands:
            row["reason"] = "no non-MOs region with >= min_units good units"
            rows.append(row)
            print(f"{s['subject']:12s} OUT ({row['reason']})")
            continue
        region = cands[0][1]
        raw = load_session(one, cfg, eid, pids, region)
        pre = preprocess_session(raw["spike_times"], raw["spike_clusters"], raw["n_units"], raw["trials"],
                                 raw["mask"], raw["wheel_t"], raw["wheel_v"], cfg)
        n_trials, p = int(pre["mask"].sum()), int(pre["counts"].shape[1])
        mos_pids = set(pids)
        row.update({"region2": region, "n_good_units": int(cnt[region]), "n_units": p, "n_trials_masked": n_trials,
                    "region2_probes": sorted(by_probe[region]),
                    "same_probe_as_mos": bool(by_probe[region] & mos_pids)})
        reasons = []
        if n_trials < inc["min_trials"]:
            reasons.append(f"masked trials {n_trials} < {inc['min_trials']}")
        if p < inc["min_units"]:
            reasons.append(f"units after rate filter {p} < {inc['min_units']}")
        if not pre["prior_pleft_corr"] > 0:
            reasons.append("prior/probabilityLeft corr <= 0")
        row["included"] = not reasons
        row["reason"] = "; ".join(reasons)
        if row["included"]:
            np.savez_compressed(root / "interim" / f"{eid}.npz", **pre)
            raw["units"].assign(kept=pre["unit_keep"]).to_csv(root / "interim" / f"{eid}_units.csv", index=False)
            keep.append(dict(s, region2=region))
        rows.append(row)
        print(f"{s['subject']:12s} {region:6s} units {p:3d} {'in' if row['included'] else 'OUT ' + row['reason']}")
    fz = dict(frozen)
    fz["sessions"] = keep
    ke = {s["eid"] for s in keep}
    fz["checkpoint"] = [e for e in frozen.get("checkpoint", []) if e in ke]
    fz["region"] = "largest non-MOs region per session (A15)"
    (root / "meta" / "frozen.json").write_text(json.dumps(fz, indent=1))
    (root / "meta" / "a15_sessions.json").write_text(json.dumps(rows, indent=1))
    print(f"region2: {len(keep)}/{len(frozen['sessions'])} sessions, {len({s['subject'] for s in keep})} animals")


if __name__ == "__main__":
    main()
