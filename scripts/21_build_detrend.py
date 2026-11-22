"""Amendment A16 part 1 (post hoc, local): detrended copies of the data for refitting with the trend removed.

data_detrend_q/  each unit's sqrt counts minus a least-squares quadratic in time (fit on valid bins)
data_detrend_c/  minus a cosine basis with periods >= 20 min (about 3x the mean block duration)
Uses the pipeline's residual hook (S_resid, Swin_resid_*); trial windows get the trend at their alignment time
(event time + window centre), exactly as pipeline.residualize_session does for trial-locked responses.
"""
import argparse
import json
from pathlib import Path

import numpy as np

from pns.config import load_config, load_frozen
from pns.transform import sqrt_counts

MIN_PERIOD_MIN = 20.0


def design(t_min, kind, t0, length):
    u = (t_min - t0) / length                       # 0..1 over the task epoch
    if kind == "q":
        return np.column_stack([u, u ** 2])
    kmax = int(np.floor(2 * length / MIN_PERIOD_MIN))
    return np.column_stack([np.cos(np.pi * k * u) for k in range(1, kmax + 1)])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kinds", nargs="+", default=["q", "c"])
    args = ap.parse_args()
    cfg = load_config()
    src = Path(cfg["paths"]["data"])
    frozen = load_frozen(cfg)
    for kind in args.kinds:
        root = Path(f"data_detrend_{kind}")
        (root / "interim").mkdir(parents=True, exist_ok=True)
        (root / "meta").mkdir(parents=True, exist_ok=True)
        r2s = []
        for s in frozen["sessions"]:
            eid = s["eid"]
            pre = dict(np.load(src / "interim" / f"{eid}.npz", allow_pickle=False))
            edges = pre["edges"]
            tc = 0.5 * (edges[:-1] + edges[1:]) / 60.0
            valid = np.asarray(pre["valid"], bool)
            t0, length = tc[valid][0], tc[valid][-1] - tc[valid][0]
            S = sqrt_counts(pre["counts"])
            D = design(tc, kind, t0, length)
            dm, sm = D[valid].mean(0), S[valid].mean(0)
            Dc, Sc = D[valid] - dm, S[valid] - sm
            beta = np.linalg.lstsq(Dc, Sc, rcond=None)[0]
            pre["S_resid"] = S - (D - dm) @ beta
            for name, spec in cfg["windows"].items():
                ev = (np.asarray(pre[spec["event"]], float) + 0.5 * (spec["win"][0] + spec["win"][1])) / 60.0
                W = sqrt_counts(pre[f"win_{name}"])
                ok = np.isfinite(ev)
                Dw = np.zeros((len(ev), D.shape[1]))
                Dw[ok] = design(ev[ok], kind, t0, length)
                pre[f"Swin_resid_{name}"] = W - (Dw - dm) @ beta
            r2 = float(1 - np.sum((Sc - Dc @ beta) ** 2) / np.sum(Sc ** 2))
            pre["detrend_r2"] = r2
            r2s.append(r2)
            np.savez(root / "interim" / f"{eid}.npz", **pre)
        fz = dict(frozen)
        fz["note"] = f"A16 detrended copy ({'quadratic' if kind == 'q' else 'cosine >= 20 min'})"
        (root / "meta" / "frozen.json").write_text(json.dumps(fz, indent=1))
        print(f"{kind}: {len(r2s)} sessions; variance removed by trend, median {np.median(r2s):.3f} "
              f"(range {min(r2s):.3f}-{max(r2s):.3f})")


if __name__ == "__main__":
    main()
