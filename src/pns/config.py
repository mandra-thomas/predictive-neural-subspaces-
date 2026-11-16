"""Load the frozen configuration and provide provenance helpers (config hash, git hash, seeds)."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]

_PATH_ENV = {"one_cache": "PNS_ONE_CACHE", "data": "PNS_DATA", "results": "PNS_RESULTS", "figures": "PNS_FIGURES"}


def load_config(path: str | os.PathLike | None = None) -> dict:
    """Read config.yaml, resolve paths (env vars override), and add derived values."""
    path = Path(path or os.environ.get("PNS_CONFIG", ROOT / "config.yaml"))
    raw = path.read_text()
    cfg = yaml.safe_load(raw)
    for key, env in _PATH_ENV.items():
        p = Path(os.environ.get(env, cfg["paths"][key]))
        cfg["paths"][key] = p if p.is_absolute() else ROOT / p
    start, stop, num = cfg["model"]["alpha_log10"]
    cfg["model"]["alphas"] = np.logspace(start, stop, int(num))
    cfg["_hash"] = hashlib.sha1(raw.encode()).hexdigest()[:10]
    cfg["_path"] = str(path)
    return cfg


def git_hash() -> str:
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, check=True)
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=no"],
                               capture_output=True, text=True).stdout.strip()
        return out.stdout.strip() + ("-dirty" if dirty else "")
    except Exception:
        return "nogit"


def session_seed(eid: str, base_seed: int = 0, salt: str = "") -> int:
    """Deterministic per-session seed, independent of joblib scheduling order."""
    h = hashlib.sha256(f"{base_seed}:{salt}:{eid}".encode()).hexdigest()
    return int(h[:8], 16)


def frozen_path(cfg: dict) -> Path:
    return Path(cfg["paths"]["data"]) / "meta" / "frozen.json"


def load_frozen(cfg: dict) -> dict:
    p = frozen_path(cfg)
    if not p.exists():
        raise FileNotFoundError(f"{p} not found: run scripts/01_census.py first")
    return json.loads(p.read_text())


def lag_seconds(cfg: dict) -> list[float]:
    return [lag * cfg["binning"]["bin_s"] for lag in cfg["lags_bins"]]
