"""Session census over candidate regions; freeze the region, the session list and the checkpoint subset.

Rule (fixed before any analysis): a region is eligible if it has >= 15 sessions and >= min_animals distinct
subjects meeting inclusion; among eligible regions pick the one with the strongest published prior decoding
(Findling et al. 2025, BWM region_info.csv `prior_dec_ep`). Writes data/meta/frozen.json (refuses to
overwrite without --force).
"""
import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd

from pns.config import frozen_path, git_hash
from pns.io_ibl import census, get_one
from pns.runner import log_run, setup, write_json

MIN_SESSIONS = 15


def findling_prior_evidence() -> pd.Series:
    import brainwidemap
    p = Path(brainwidemap.__file__).parent / "meta" / "region_info.csv"
    info = pd.read_csv(p)
    return info.set_index("Beryl")["prior_dec_ep"]


def pick_checkpoint(sessions: pd.DataFrame, n: int, seed: int) -> list[str]:
    """Seeded subset maximising distinct subjects: one random session per subject, subjects in random order,
    cycling until n sessions."""
    rng = np.random.default_rng(seed)
    by_subj = {s: list(rng.permutation(g["eid"].to_numpy())) for s, g in sessions.groupby("subject")}
    order = list(rng.permutation(sorted(by_subj)))
    out = []
    while len(out) < min(n, len(sessions)):
        for s in order:
            if by_subj[s] and len(out) < n:
                out.append(by_subj[s].pop())
    return out


def main():
    args, cfg, _ = setup(__doc__)
    fp = frozen_path(cfg)
    if fp.exists() and not args.force:
        raise SystemExit(f"{fp} exists: the dataset is frozen. Use --force only with a logged amendment.")
    one = get_one(cfg)
    rows = census(one, cfg)
    meta_dir = fp.parent
    meta_dir.mkdir(parents=True, exist_ok=True)
    rows.to_csv(meta_dir / "census.csv", index=False)

    evidence = findling_prior_evidence()
    summary = (rows.groupby("region").agg(n_sessions=("eid", "nunique"), n_subjects=("subject", "nunique"),
                                          median_units=("n_units", "median"))
               .join(evidence.rename("findling_prior_r2")))
    summary["eligible"] = (summary["n_sessions"] >= MIN_SESSIONS) & \
                          (summary["n_subjects"] >= cfg["inclusion"]["min_animals"])
    summary.to_csv(meta_dir / "region_counts.csv")
    print(summary.to_string())
    elig = summary[summary["eligible"]]
    if elig.empty:
        raise SystemExit("No region meets >=15 sessions and the minimum number of animals. "
                         "Decide an amendment (e.g. min_units 15, or add a region) and log it.")
    region = elig["findling_prior_r2"].idxmax()
    sess = rows[rows["region"] == region].sort_values(["subject", "date"]).reset_index(drop=True)
    checkpoint = pick_checkpoint(sess, cfg["inclusion"]["n_checkpoint"], cfg["seed"])
    frozen = {"region": region, "created": dt.datetime.now().isoformat(timespec="seconds"),
              "git": git_hash(), "config_hash": cfg["_hash"],
              "rule": "eligible: >=15 sessions and >=min_animals subjects; pick max Findling prior_dec_ep",
              "sessions": sess[["eid", "pids", "subject", "n_units", "n_trials_table"]].to_dict("records"),
              "checkpoint": checkpoint}
    write_json(fp, frozen)
    n_ck_subj = sess.set_index("eid").loc[checkpoint, "subject"].nunique()
    msg = (f"region={region}; {len(sess)} sessions / {sess['subject'].nunique()} subjects; "
           f"checkpoint {len(checkpoint)} sessions / {n_ck_subj} subjects")
    print(msg)
    log_run(cfg, "01_census", msg)


if __name__ == "__main__":
    main()
