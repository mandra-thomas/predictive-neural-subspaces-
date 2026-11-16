"""Shared plumbing for the numbered scripts: CLI, session selection, caching, parallelism, logging."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import traceback
from pathlib import Path

import numpy as np

from .config import ROOT, git_hash, load_config, load_frozen


def base_parser(desc: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=desc)
    p.add_argument("--eids", nargs="*", help="explicit session ids (default: frozen list)")
    p.add_argument("--subset", choices=("checkpoint", "all"), default="all")
    p.add_argument("--force", action="store_true", help="recompute even if outputs exist")
    p.add_argument("--n-jobs", type=int, default=None)
    p.add_argument("--config", default=None)
    p.add_argument("--residual", action="store_true",
                   help="add-on A11: analyse residuals after removing trial-locked responses")
    return p


def select_eids(cfg: dict, args) -> list[str]:
    if args.eids:
        return list(args.eids)
    frozen = load_frozen(cfg)
    if args.subset == "checkpoint":
        return list(frozen["checkpoint"])
    return [s["eid"] for s in frozen["sessions"]]


def out_dir(cfg: dict, *parts: str) -> Path:
    d = Path(cfg["paths"]["results"]).joinpath(*parts)
    d.mkdir(parents=True, exist_ok=True)
    return d


def interim_path(cfg: dict, eid: str) -> Path:
    d = Path(cfg["paths"]["data"]) / "interim"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{eid}.npz"


def load_npz(path: Path) -> dict:
    with np.load(path, allow_pickle=False) as z:
        out = {k: z[k] for k in z.files}
    return {k: (v.item() if v.ndim == 0 else v) for k, v in out.items()}


def run_sessions(fn, eids: list[str], n_jobs: int) -> list[dict]:
    """Run fn(eid) -> dict per session, in parallel; failures are captured, not raised."""
    def safe(eid):
        try:
            return {"eid": eid, "ok": True, **(fn(eid) or {})}
        except Exception as e:  # noqa: BLE001 - one bad session must not kill the batch
            return {"eid": eid, "ok": False, "error": f"{type(e).__name__}: {e}", "tb": traceback.format_exc()}
    if n_jobs == 1 or len(eids) == 1:
        return [safe(e) for e in eids]
    from joblib import Parallel, delayed
    return Parallel(n_jobs=n_jobs)(delayed(safe)(e) for e in eids)


def report(results: list[dict], step: str) -> None:
    bad = [r for r in results if not r["ok"]]
    print(f"[{step}] {len(results) - len(bad)}/{len(results)} sessions ok")
    for r in bad:
        print(f"  FAILED {r['eid']}: {r['error']}")


def log_run(cfg: dict, step: str, note: str) -> None:
    """Append one line to ANALYSIS_LOG.md (date, git hash, config hash, step, note). Runs on overridden
    data paths (e.g. synthetic smoke tests) log into their own results folder instead."""
    line = f"| {dt.datetime.now():%Y-%m-%d %H:%M} | {git_hash()} | {cfg['_hash']} | {step} | {note} |\n"
    real_data = Path(cfg["paths"]["data"]).resolve() == (ROOT / "data").resolve()
    log = ROOT / "ANALYSIS_LOG.md" if real_data else Path(cfg["paths"]["results"]) / "ANALYSIS_LOG.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a") as f:
        f.write(line)


def residual_guard(cfg: dict, args) -> None:
    """--residual runs must write to a separate results root (PNS_RESULTS), never over the main results."""
    if getattr(args, "residual", False) and Path(cfg["paths"]["results"]).resolve() == (ROOT / "results").resolve():
        raise SystemExit("--residual requires PNS_RESULTS (and PNS_FIGURES) pointing to a separate folder, "
                         "e.g. PNS_RESULTS=results_residual")


def setup(desc: str, extra=None):
    p = base_parser(desc)
    if extra:
        extra(p)
    args = p.parse_args()
    cfg = load_config(args.config)
    residual_guard(cfg, args)
    n_jobs = args.n_jobs or cfg["n_jobs"]
    return args, cfg, n_jobs


def write_json(path: Path, obj) -> None:
    def default(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, (np.bool_,)):
            return bool(o)
        return str(o)
    path.write_text(json.dumps(obj, indent=2, default=default))
