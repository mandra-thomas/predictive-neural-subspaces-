"""Amendment A18 part B (post hoc): the latent state-space model on simulated sessions only. See AMENDMENTS.md, A18
part B.

For the cells nodrift, lowrank_x1, neg_history_strong and neg_pure of the A18 part A sweep (seeds 1000-1031, the same
simulated sessions, regenerated deterministically), fit the trial-indexed latent model (pns.sim_a18.lds_readout) and
decode the prior from each trial's instantaneous latent estimate with the subspace decoder and the same pseudo
sessions. Applies the gate fixed in A18 part B at the task level (the two seeds of each task averaged; 16 tasks).
Writes results/a18/lds_sim_seeds.csv and results/a18/lds_gate.json. No real neural data is used.
"""
import json

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.stats import binom

from pns.config import ROOT
from pns.runner import log_run, setup, write_json
from pns.sim_a18 import lds_readout

OUT = ROOT / "results" / "a18"
CELLS = ("nodrift", "lowrank_x1", "neg_history_strong", "neg_pure")
NEED = 12            # of 16 tasks: one-sided binomial P(X >= 12) = 0.038


def _s26():
    import importlib.util
    spec = importlib.util.spec_from_file_location("s26", ROOT / "scripts" / "26_sim_A18.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def job(cell, seed, cfg):
    s26 = _s26()
    cal = json.loads((OUT / "calibration.json").read_text())
    mode, params = s26.cells(cal)[cell]
    eid, sim, pre, sn, pn = s26.simulate(seed, (seed - s26.SWEEP_SEEDS[0]) % 16, params, mode, cfg)
    from pns.sim_a18 import calibration_stats
    full = calibration_stats(pre, cfg, sn, pn)["full_prior_corr"]
    out = lds_readout(pre, cfg, sn, pn, np.random.default_rng([seed, 97]))
    out["lds_tau"] = json.dumps(out["lds_tau"])
    return {"cell": cell, "seed": seed, "task": (seed - s26.SWEEP_SEEDS[0]) % 16, "task_eid": eid,
            "full_prior_regen": full, **out}


def gate(df):
    tk = df.groupby(["cell", "task"])[["lds_all", "lds_band", "full_prior_regen"]].mean().reset_index()
    res = {}
    for cell, g in tk.groupby("cell"):
        x = g.lds_all.to_numpy()
        res[cell] = {"lds_all_mean": float(x.mean()), "lds_all_npos_tasks": int((x > 0).sum()),
                     "lds_all_binom_p": float(binom.sf(int((x > 0).sum()) - 1, 16, 0.5)),
                     "lds_band_mean": float(np.nanmean(g.lds_band)), "full_mean": float(g.full_prior_regen.mean())}
    lr, hs, npure = res["lowrank_x1"], res["neg_history_strong"], res["neg_pure"]
    b1 = lr["lds_all_npos_tasks"] >= NEED and lr["lds_all_mean"] >= 0.5 * lr["full_mean"]
    b2 = hs["lds_all_npos_tasks"] < NEED and hs["lds_all_mean"] <= 0.25 * lr["lds_all_mean"]
    null_ok = npure["lds_all_npos_tasks"] < NEED
    if not null_ok:
        reading = "readout miscalibrated (null cell positive): stop"
    elif b1 and b2:
        reading = "gate passed: retains the prior under drift and is not fooled by stimulus memory"
    elif b1:
        reading = "recovers a correlated signal but does not separate belief from stimulus memory: stop"
    else:
        reading = "does not retain the prior under calibrated drift: stop"
    return {"cells": res, "B1_prior_retained": bool(b1), "B2_history_not_mimicked": bool(b2),
            "null_calibrated": bool(null_ok), "reading": reading, "n_tasks": 16, "need_tasks": NEED}


def main():
    args, cfg, n_jobs = setup(__doc__)
    s26 = _s26()
    jobs = [(c, s) for c in CELLS for s in s26.SWEEP_SEEDS]
    rows = Parallel(n_jobs=n_jobs, verbose=5)(delayed(job)(c, s, cfg) for c, s in jobs)
    df = pd.DataFrame(rows)
    # reproduction check: the regenerated sessions are the A18 part A sessions
    ref = pd.read_csv(OUT / "sim_seeds.csv")
    ref = ref[ref.pipeline == "raw"].set_index(["cell", "seed"])["full_prior_corr"]
    diff = np.abs(df.set_index(["cell", "seed"])["full_prior_regen"] - ref.reindex(df.set_index(["cell", "seed"]).index))
    df.to_csv(OUT / "lds_sim_seeds.csv", index=False)
    out = gate(df)
    out["reproduction_max_abs_diff"] = float(diff.max())
    out["n_converged"] = int(df.lds_converged.sum())
    out["n_fits"] = len(df)
    write_json(OUT / "lds_gate.json", out)
    print(json.dumps(out, indent=1))
    log_run(cfg, "27_lds_sim_A18", f"A18 part B gate: {out['reading']}; reproduction diff {out['reproduction_max_abs_diff']:.1e}")


if __name__ == "__main__":
    main()
