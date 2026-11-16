"""Go/no-go gate: Findling-style prior decoding from the FULL regional population vs the pseudo-session null.

Lasso, nested interleaved 5-fold CV, pre-stimulus window (-600 to -100 ms). Session significance: real R^2
above the null's 95th percentile (one-sided p < 0.05); sessions combined with Fisher's method.
GO if the Fisher-combined p < 0.05 and the median null-corrected R^2 > 0. NO-GO invokes the proposal's risk
row 2 (report the other probes; prior content claims are not made).
"""
import numpy as np

from pns.config import session_seed
from pns.pipeline import gate_session
from pns.runner import (interim_path, load_npz, log_run, out_dir, report, run_sessions, select_eids, setup,
                        write_json)
from pns.stats import fisher_combine


def extra(p):
    p.add_argument("--n-pseudo", type=int, default=None)


def main():
    args, cfg, n_jobs = setup(__doc__, extra)
    n_pseudo = args.n_pseudo if args.n_pseudo is not None else cfg["gate"]["n_pseudo"]
    od = out_dir(cfg, "gate")
    eids = select_eids(cfg, args)

    def work(eid):
        f = od / f"{eid}.json"
        if f.exists() and not args.force:
            import json
            return json.loads(f.read_text())
        ip = interim_path(cfg, eid)
        st = ip.with_suffix(".status.json")
        if not ip.exists():
            raise FileNotFoundError("run 02_preprocess first")
        import json
        if st.exists() and not json.loads(st.read_text()).get("included", True):
            return {"excluded": True}
        pre = load_npz(ip)
        rng = np.random.default_rng(session_seed(eid, cfg["seed"], "gate"))
        g = gate_session(pre, cfg, rng, n_pseudo)
        np.save(od / f"{eid}_null.npy", g.pop("null"))
        write_json(f, g)
        return g

    res = run_sessions(work, eids, n_jobs)
    report(res, "03_prior_gate")
    ok = [r for r in res if r["ok"] and not r.get("excluded")]
    if not ok:
        raise SystemExit("no sessions gated")
    corr = np.array([r["corrected"] for r in ok])
    ps = np.array([r["p"] for r in ok])
    summary = {"n_sessions": len(ok), "median_corrected_r2": float(np.median(corr)),
               "frac_sessions_p05": float(np.mean(ps < 0.05)), "fisher_p": fisher_combine(ps),
               "n_pseudo": n_pseudo}
    summary["decision"] = "GO" if (summary["fisher_p"] < 0.05 and summary["median_corrected_r2"] > 0) else "NO-GO"
    write_json(od / "summary.json", summary)
    print(summary)
    log_run(cfg, "03_prior_gate", f"{summary['decision']}: {summary}")


if __name__ == "__main__":
    main()
