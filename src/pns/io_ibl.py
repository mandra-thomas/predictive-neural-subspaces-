"""The only module that imports ONE / brainbox / brainwidemap / iblatlas (imports are lazy).

Verified against source on 2026-11-16 (see AMENDMENTS.md / plan):
* ONE >= 3.6 needs an explicit username for the public server.
* download_aggregate_tables must be given tag '2024_Q2_IBL_et_al_BWM' (the 2026_Q2 default has no trials hash).
* bwm_units is avoided (it calls download_aggregate_tables with the default tag and crashes).
* load_good_units does not add a Beryl column; merge_probes mutates inputs, so probes are merged here.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .pipeline import TRIAL_KEYS


def get_one(cfg: dict):
    """Connect with the user's own account: username from $PNS_ONE_USERNAME, config, or ONE's saved params;
    the password is never stored in the repo (ONE caches a token after one interactive login)."""
    import os

    from one.api import ONE
    cache = Path(cfg["paths"]["one_cache"])
    cache.mkdir(parents=True, exist_ok=True)
    kw = {}
    username = os.environ.get("PNS_ONE_USERNAME") or cfg["data"].get("one_username")
    if username:
        kw["username"] = username
    return ONE(base_url=cfg["data"]["one_base_url"], silent=True, cache_dir=cache, **kw)


def aggregate_tables(one, cfg: dict) -> tuple[Path, Path]:
    from brainwidemap.bwm_loading import download_aggregate_tables
    tag = cfg["data"]["agg_tag"]
    return (Path(download_aggregate_tables(one, type="trials", tag=tag)),
            Path(download_aggregate_tables(one, type="clusters", tag=tag)))


def census(one, cfg: dict) -> pd.DataFrame:
    """One row per (region, eid) for candidate regions meeting the unit and trial criteria.
    Trial counts come from the aggregate table's precomputed `bwm_include` (verified live in 02)."""
    from brainwidemap.bwm_loading import bwm_query, filter_sessions, filter_units_region
    inc = cfg["inclusion"]
    bwm = bwm_query()                                       # 2023_12 freeze, packaged CSV
    trials_path, clusters_path = aggregate_tables(one, cfg)
    eids = filter_sessions(bwm["eid"].unique(), trials_table=trials_path, min_trials=inc["min_trials"])
    units = filter_units_region(eids, clusters_table=clusters_path, mapping="Beryl", min_qc=1.0,
                                min_units_sessions=(inc["min_units"], 1))
    units = units[units["Beryl"].isin(cfg["candidate_regions"])]
    tdf = pd.read_parquet(trials_path)
    n_trials = tdf[tdf["bwm_include"]].groupby("eid").size().rename("n_trials_table")
    if "pid" in units.columns:
        rows = (units.groupby(["Beryl", "eid"])
                .agg(n_units=("cluster_id", "size"), pids=("pid", lambda s: ",".join(sorted(set(s)))))
                .reset_index())
    else:   # fall back to every BWM insertion of the session; load_session filters units by region anyway
        rows = units.groupby(["Beryl", "eid"]).agg(n_units=("cluster_id", "size")).reset_index()
        pid_map = bwm.groupby("eid")["pid"].apply(lambda s: ",".join(sorted(set(s))))
        rows["pids"] = rows["eid"].map(pid_map)
    subj = bwm.drop_duplicates("eid").set_index("eid")[["subject", "lab", "date"]]
    rows = rows.join(subj, on="eid").join(n_trials, on="eid")
    return rows.rename(columns={"Beryl": "region"})


def load_session(one, cfg: dict, eid: str, pids: list[str], region: str) -> dict:
    """Good units in `region` (pooled over probes), full trial table + BWM mask, and wheel velocity."""
    from brainbox.io.one import SessionLoader
    from brainwidemap.bwm_loading import load_good_units, load_trials_and_mask
    from iblatlas.regions import BrainRegions

    if len(pids) > 2:
        raise ValueError(f"{eid}: more than 2 probes ({len(pids)}) not supported")
    br = BrainRegions()
    times, clus, offset, unit_info = [], [], 0, []
    for pid in pids:
        spikes, clusters = load_good_units(one, pid, qc=1.0)
        beryl = br.id2acronym(clusters["atlas_id"].to_numpy(), mapping="Beryl")
        keep = np.flatnonzero(beryl == region)
        if len(keep) == 0:
            continue
        remap = -np.ones(len(clusters), dtype=np.int64)
        remap[keep] = np.arange(len(keep)) + offset
        new = remap[np.asarray(spikes["clusters"], dtype=np.int64)]
        sel = new >= 0
        times.append(np.asarray(spikes["times"])[sel])
        clus.append(new[sel])
        info = clusters.iloc[keep][[c for c in ("uuids", "cluster_id", "atlas_id", "acronym") if c in clusters]].copy()
        info["pid"] = pid
        unit_info.append(info)
        offset += len(keep)
    if offset == 0:
        raise ValueError(f"{eid}: no good units in {region}")
    t = np.concatenate(times)
    c = np.concatenate(clus)
    order = np.argsort(t, kind="stable")

    sl = SessionLoader(one=one, eid=eid, revision=cfg["data"]["trials_revision"])
    trials_df, mask = load_trials_and_mask(one, eid, sess_loader=sl, revision=cfg["data"]["trials_revision"])
    sl.load_wheel()
    trials = {k: trials_df[k].to_numpy() for k in TRIAL_KEYS if k != "intervals"}
    trials["intervals"] = trials_df[["intervals_0", "intervals_1"]].to_numpy()
    return {"spike_times": t[order], "spike_clusters": c[order], "n_units": offset, "trials": trials,
            "mask": np.asarray(mask, dtype=bool), "wheel_t": sl.wheel["times"].to_numpy(),
            "wheel_v": sl.wheel["velocity"].to_numpy(), "units": pd.concat(unit_info, ignore_index=True)}


def probe_unit_counts(one, cfg: dict, eid: str, region: str) -> dict:
    """Good units in `region` per probe insertion (from the aggregate clusters table), for weighting probe motion."""
    from brainwidemap.bwm_loading import filter_units_region
    _, clusters_path = aggregate_tables(one, cfg)
    u = filter_units_region([eid], clusters_table=clusters_path, mapping="Beryl", min_qc=1.0,
                            min_units_sessions=(1, 1))
    u = u[u["Beryl"] == region]
    return u.groupby("pid").size().to_dict() if "pid" in u.columns else {}


def load_state_signals(one, eid: str, pids: list[str], weights: dict, drift_revision: str) -> dict:
    """Probe-motion estimate (pykilosort drift registration, mean over depth points, unit-weighted across probes)
    and left-camera pupil diameter (smoothed) for one session (amendment A12)."""
    traces, ws, t_ref = [], [], None
    for pid in pids:
        _, pname = one.pid2eid(pid)
        coll = f"alf/{pname}/pykilosort"
        dt = np.asarray(one.load_dataset(eid, "drift.times.npy", collection=coll, revision=drift_revision))
        dm = np.asarray(one.load_dataset(eid, "drift.um.npy", collection=coll, revision=drift_revision))
        tr = dm.mean(axis=1) if dm.ndim == 2 else dm
        if t_ref is None:
            t_ref = dt
        traces.append(np.interp(t_ref, dt, tr))
        ws.append(float(weights.get(pid, 0)))
    ws = np.asarray(ws)
    if ws.sum() == 0:
        ws = np.ones(len(ws))
    motion = np.average(np.vstack(traces), axis=0, weights=ws)
    out = {"motion_t": t_ref, "motion_um": motion, "probe_weights": ws}
    try:
        feats = one.load_dataset(eid, "_ibl_leftCamera.features.pqt", collection="alf")
        cam_t = np.asarray(one.load_dataset(eid, "_ibl_leftCamera.times.npy", collection="alf"))
        pup = feats["pupilDiameter_smooth"].to_numpy(dtype=float)
        n = min(len(pup), len(cam_t))
        out.update({"pupil_t": cam_t[:n], "pupil": pup[:n], "pupil_len_mismatch": int(len(pup) != len(cam_t))})
        recs = [d for d in one.list_datasets(eid) if d.endswith("_ibl_leftCamera.features.pqt")]
        out["pupil_datasets"] = np.array(recs)
    except Exception as e:                                         # missing video: recorded, session excluded
        out["pupil_error"] = np.array(str(e)[:300])
    return out
