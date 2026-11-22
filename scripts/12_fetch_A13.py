"""Amendment A13, local step (needs the IBL login): fetch and extract compact inputs for the second pilot.

Per session, writes data/interim/a13/{eid}.npz with
  mua_t, mua_ch        every detected spike (any cluster/label) at depths within the probe's MOs channel span:
                       time (float64) and 50 um depth-bin channel index (int16, offset across probes)
  mua_ch_depth, mua_ch_probe   depth (um, bin centre) and probe index of each channel
  unit_t, unit_idx, unit_amp   spikes of the analysed (kept) MOs good units from passingSpikes: time, index into
                       the interim unit order, amplitude
  depth_coords_note    which depth field was used
and downloads the IBL engagement table to data/external/engage/ (sha256 recorded in data/interim/a13/manifest.json).
No analysis is done here.
"""
import hashlib
import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

from pns.config import load_frozen
from pns.io_ibl import get_one
from pns.runner import interim_path, log_run, report, run_sessions, select_eids, setup

REV = "2024-05-06"
BIN_UM = 50.0
ENGAGE_URL = "https://raw.githubusercontent.com/int-brain-lab/engage/main/merged_behavioral_and_states.pqt"


def mos_span(one, eid, pname, region):
    from iblatlas.regions import BrainRegions
    coll = f"alf/{pname}/pykilosort"
    lc = np.asarray(one.load_dataset(eid, "channels.localCoordinates.npy", collection=coll, revision=REV))
    ids = np.asarray(one.load_dataset(eid, "channels.brainLocationIds_ccf_2017.npy", collection=coll, revision=REV))
    beryl = BrainRegions().id2acronym(ids, mapping="Beryl")
    y = lc[beryl == region, 1]
    return (float(y.min()), float(y.max())) if len(y) else None


def main():
    args, cfg, _ = setup(__doc__)
    frozen = load_frozen(cfg)
    region = frozen["region"]
    pids = {s["eid"]: [p for p in s["pids"].split(",") if p] for s in frozen["sessions"]}
    one = get_one(cfg)
    root = interim_path(cfg, "x").parent
    od = root / "a13"
    od.mkdir(parents=True, exist_ok=True)
    ext = Path(cfg["paths"]["data"]) / "external" / "engage"
    ext.mkdir(parents=True, exist_ok=True)
    eng = ext / "merged_behavioral_and_states.pqt"
    if not eng.exists():
        urllib.request.urlretrieve(ENGAGE_URL, eng)
    manifest = {"engage_url": ENGAGE_URL, "engage_sha256": hashlib.sha256(eng.read_bytes()).hexdigest(),
                "spike_revision": REV, "bin_um": BIN_UM}

    def work(eid):
        f = od / f"{eid}.npz"
        if f.exists() and not args.force:
            return {"skipped": True}
        units = pd.read_csv(root / f"{eid}_units.csv")
        kept = units[units["kept"]].reset_index(drop=True)
        mua_t, mua_ch, ch_depth, ch_probe = [], [], [], []
        u_t, u_idx, u_amp = [], [], []
        ch_off = 0
        for k, pid in enumerate(pids[eid]):
            _, pname = one.pid2eid(pid)
            coll = f"alf/{pname}/pykilosort"
            span = mos_span(one, eid, pname, region)
            if span is not None:
                t = np.asarray(one.load_dataset(eid, "spikes.times.npy", collection=coll, revision=REV))
                dep = np.asarray(one.load_dataset(eid, "spikes.depths.npy", collection=coll, revision=REV))
                lo, hi = span[0] - BIN_UM / 2, span[1] + BIN_UM / 2
                sel = (dep >= lo) & (dep < hi)
                b = np.floor((dep[sel] - lo) / BIN_UM).astype(np.int16)
                n_b = int(np.ceil((hi - lo) / BIN_UM))
                mua_t.append(t[sel])
                mua_ch.append((b + ch_off).astype(np.int16))
                ch_depth.append(lo + BIN_UM * (np.arange(n_b) + 0.5))
                ch_probe.append(np.full(n_b, k, dtype=np.int16))
                ch_off += n_b
            # analysed good units on this probe: their spikes and amplitudes from passingSpikes
            mine = kept[kept["pid"] == pid]
            if len(mine):
                ps = one.load_dataset(eid, "passingSpikes.table.pqt", collection=coll, revision=REV)
                cmap = dict(zip(mine["cluster_id"].astype(int), mine.index.to_numpy()))
                m = ps["clusters"].isin(list(cmap))
                u_t.append(ps.loc[m, "times"].to_numpy())
                u_idx.append(ps.loc[m, "clusters"].map(cmap).to_numpy().astype(np.int16))
                u_amp.append(ps.loc[m, "amps"].to_numpy().astype(np.float32))
        out = {"mua_t": np.concatenate(mua_t) if mua_t else np.zeros(0),
               "mua_ch": np.concatenate(mua_ch) if mua_ch else np.zeros(0, np.int16),
               "mua_ch_depth": np.concatenate(ch_depth) if ch_depth else np.zeros(0),
               "mua_ch_probe": np.concatenate(ch_probe) if ch_probe else np.zeros(0, np.int16),
               "unit_t": np.concatenate(u_t), "unit_idx": np.concatenate(u_idx), "unit_amp": np.concatenate(u_amp),
               "n_units_kept": np.array(len(kept)),
               "depth_coords_note": np.array("spikes.depths (pykilosort revision 2024-05-06)")}
        np.savez(f, **out)
        return {"n_mua_spikes": int(len(out["mua_t"])), "n_channels": int(ch_off),
                "units_found": int(len(np.unique(out["unit_idx"]))), "n_units_kept": int(len(kept))}

    res = run_sessions(work, select_eids(cfg, args), 1)
    report(res, "12_fetch_A13")
    for r in res:
        if r["ok"] and not r.get("skipped"):
            print(f"  {r['eid'][:8]} mua spikes {r['n_mua_spikes']:>9d}  channels {r['n_channels']:3d}  "
                  f"units found {r['units_found']}/{r['n_units_kept']}")
    (od / "manifest.json").write_text(json.dumps(manifest, indent=1))
    log_run(cfg, "12_fetch_A13", f"A13 inputs; {sum(r['ok'] for r in res)}/{len(res)} ok")


if __name__ == "__main__":
    main()
