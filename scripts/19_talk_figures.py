"""Two talk/report figures about the slow mode. Reads existing result files only: no new analyses, no refits.

fig4_slowmode_controls : for each recording-control data version (amendments A12, A13, A14), the elapsed-time
                         decoding R^2 of the 30 s lagged-RRR subspace (d = 5): per-animal points, the animal mean and
                         its 95% CI (from stats/d5/matrix.csv), a reference line at the original value and dashed
                         lines at 75% / 50% of it (the pre-registered "survives" / "removed" thresholds).
                         Per-animal points are session scores (stats/d5/session_scores.csv) averaged within animal;
                         their mean is checked against matrix.csv before plotting.
fig5_slowmode_examples : the sign-aligned slow mode (pns.slowmode.slow_mode: first readout direction of the
                         full-session 30 s subspace, activity projected on it, averaged in 30 s windows) against
                         time in session, one panel per session, with a least-squares straight line. By the rule below,
                         three of the six (CSHL058, CSHL060, KS023) are near-linear ramps, CSH_ZAD_024 rises in
                         several steps, and two (CSHL049, DY_014) are flat with a step; the title says so rather
                         than swapping sessions.

Session-selection rule for fig5 (fixed in advance, no cherry-picking): walk data/meta/frozen.json in its stored order
and take the first session of each of the first six distinct mice. The suptitle also reports the median correlation
of the slow mode with elapsed time over all 16 sessions, so the six panels can be compared with the full set.

Idempotent: rerunning overwrites figures/fig4_slowmode_controls.{pdf,png} and figures/fig5_slowmode_examples.{pdf,png}.
"""
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pns.config import ROOT
from pns.pipeline import session_S
from pns.plotting import INK, INK_2, MUTED, SERIES, SURFACE, style
from pns.slowmode import slow_mode, window_edges

D = 5
LONG_LAG = 60                    # bins of 0.5 s = 30 s
N_EXAMPLE_MICE = 6
FIG_DIR = ROOT / "figures"

# (results folder, plain-word label, post hoc?)
VERSIONS = [
    ("results", "Original units", False),
    ("results_stable", "Stable units only\n(active all session)", False),
    ("results_mua", "Sorting-free\nmulti-unit activity", False),
    ("results_ampstable", "Amplitude-stable units only", False),
    ("results_ampcorr_low", "Amplitude-corrected,\nconservative", False),
    ("results_ampcorr_high", "Amplitude-corrected,\nmaximal", False),
    ("results_ampcorr_slow", "Amplitude-corrected,\nslow-maximal", True),
]
# Values in RESULTS.md (2 d.p.); the script refuses to plot if the files disagree.
EXPECTED = {"results": 0.84, "results_stable": 0.77, "results_mua": 0.74, "results_ampstable": 0.49,
            "results_ampcorr_low": 0.85, "results_ampcorr_high": 0.80, "results_ampcorr_slow": 0.78}


def talk_style():
    style()
    plt.rcParams.update({"font.size": 12, "axes.titlesize": 14, "axes.labelsize": 13, "xtick.labelsize": 12,
                         "ytick.labelsize": 12, "legend.fontsize": 11})


def load_version(folder):
    st = ROOT / folder / "stats" / f"d{D}"
    m = pd.read_csv(st / "matrix.csv")
    m = m[(m.feature_set == f"rrr_{LONG_LAG}") & (m.variable == "elapsed_time")].iloc[0]
    s = pd.read_csv(st / "session_scores.csv")
    s = s[(s.feature_set == f"rrr_{LONG_LAG}") & (s.variable == "elapsed_time")]
    per_animal = s.groupby("subject")["score"].mean()
    mean = float(m["mean"])
    assert np.isclose(per_animal.mean(), mean, atol=1e-9), (folder, per_animal.mean(), mean)
    assert int(m["n_animals"]) == len(per_animal), folder
    assert round(mean, 2) == EXPECTED[folder], (folder, mean, EXPECTED[folder])
    return dict(mean=mean, lo=float(m["ci_lo"]), hi=float(m["ci_hi"]), animals=per_animal.to_numpy(),
                n_sess=s.eid.nunique(), n_anim=len(per_animal))


def fig_controls():
    data = {f: load_version(f) for f, _, _ in VERSIONS}
    ref = data["results"]["mean"]
    fig, ax = plt.subplots(figsize=(10, 6.2))
    n = len(VERSIONS)
    ys = np.arange(n)[::-1]
    ax.axvline(ref, color=INK_2, lw=1.2, zorder=0)
    box = dict(facecolor=SURFACE, edgecolor="none", pad=1.5)
    for frac, lbl in [(0.75, "75%\n'survives'"), (0.5, "50%\n'removed'")]:
        ax.axvline(frac * ref, color=INK_2, lw=1.2, ls="--", zorder=0)
        ax.text(frac * ref, n - 0.45, lbl, ha="center", va="bottom", fontsize=11, color=INK_2, bbox=box)
    ax.text(ref, n - 0.45, f"original\n{ref:.2f}", ha="center", va="bottom", fontsize=11, color=INK_2, bbox=box)
    rng = np.random.default_rng(0)
    for y, (folder, label, posthoc) in zip(ys, VERSIONS):
        r = data[folder]
        col = SERIES[1] if posthoc else SERIES[0]
        ax.scatter(r["animals"], y + rng.uniform(-0.17, 0.17, len(r["animals"])), s=26, color=MUTED,
                   edgecolor="none", zorder=1)
        ax.errorbar(r["mean"], y, xerr=[[r["mean"] - r["lo"]], [r["hi"] - r["mean"]]], fmt="o", ms=11,
                    color=col, ecolor=col, elinewidth=2.5, capsize=0, zorder=3)
        ax.text(1.02, y, f"{r['mean']:.2f}  ({100 * r['mean'] / ref:.0f}%)", transform=ax.get_yaxis_transform(),
                va="center", ha="left", fontsize=12, color=INK)
    ticklabels = [f"{lab}{'  (post hoc)' if ph else ''}\n{data[f]['n_sess']} sessions, {data[f]['n_anim']} mice"
                  for f, lab, ph in VERSIONS]
    ax.set_yticks(ys, ticklabels, fontsize=11)
    ax.set_ylim(-0.6, n + 0.35)
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("elapsed-time decoding R² of the 30 s subspace (held out)")
    ax.grid(axis="y", visible=False)
    ax.text(1.02, n - 0.45, "mean (% of\noriginal)", transform=ax.get_yaxis_transform(), ha="left", va="bottom",
            fontsize=11, color=INK_2)
    h1 = ax.scatter([], [], s=26, color=MUTED, label="one mouse")
    h2 = ax.errorbar([], [], xerr=[], fmt="o", ms=9, color=SERIES[0], label="mean over mice, 95% CI")
    h3 = ax.errorbar([], [], xerr=[], fmt="o", ms=9, color=SERIES[1], label="post hoc version")
    ax.set_title("Elapsed-time decoding from the 30 s subspace under each control", loc="left")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.legend(handles=[h1, h2, h3], loc="lower center", ncol=3, fontsize=12, bbox_to_anchor=(0.5, 0.0))
    fig.savefig(FIG_DIR / "fig4_slowmode_controls.pdf")
    fig.savefig(FIG_DIR / "fig4_slowmode_controls.png", dpi=300)
    plt.close(fig)
    return data


def session_trace(eid):
    pre = dict(np.load(ROOT / "data" / "interim" / f"{eid}.npz", allow_pickle=True))
    fits = dict(np.load(ROOT / "results" / "subspaces" / f"{eid}_d{D}.npz", allow_pickle=True))
    sw, _, _ = slow_mode(pre, fits, session_S(pre), LONG_LAG)
    ew = window_edges(pre)
    t_min = (0.5 * (ew[:-1] + ew[1:]) - ew[0]) / 60.0
    ok = np.isfinite(sw)
    z = (sw - np.nanmean(sw)) / np.nanstd(sw)
    r = float(np.corrcoef(t_min[ok], sw[ok])[0, 1])
    return t_min, z, ok, r


def fig_examples():
    frozen = json.loads((ROOT / "data" / "meta" / "frozen.json").read_text())
    chosen, seen = [], set()
    for s in frozen["sessions"]:
        if s["subject"] not in seen:
            seen.add(s["subject"])
            chosen.append((s["eid"], s["subject"]))
        if len(chosen) == N_EXAMPLE_MICE:
            break
    all_r = {s["eid"]: session_trace(s["eid"])[3] for s in frozen["sessions"]}
    med_r = float(np.median(list(all_r.values())))
    n_hi = sum(r >= 0.9 for r in all_r.values())
    fig, axs = plt.subplots(2, 3, figsize=(11, 6.2), sharey=True)
    for ax, (eid, subj) in zip(axs.flat, chosen):
        t, z, ok, r = session_trace(eid)
        b = np.polyfit(t[ok], z[ok], 1)
        ax.plot(t[ok], np.polyval(b, t[ok]), color=INK_2, lw=1.5, ls="--", zorder=1)
        ax.plot(t[ok], z[ok], color=SERIES[0], lw=2, marker="o", ms=3.5, zorder=2)
        ax.set_title(f"mouse {subj}", loc="left", fontsize=13)
        ax.text(0.97, 0.05, f"r = {r:.2f}", transform=ax.transAxes, ha="right", va="bottom", fontsize=12,
                color=INK)
    for ax in axs[-1]:
        ax.set_xlabel("time in session (min)")
    for ax in axs[:, 0]:
        ax.set_ylabel("slow mode (z-score)")
    fig.suptitle("Slow mode in 30 s windows: mostly a near-linear ramp, sometimes a step",
                 x=0.01, y=0.985, ha="left", va="top", fontsize=14, color=INK, fontweight="bold")
    fig.text(0.01, 0.935, f"First session of each of the first {N_EXAMPLE_MICE} mice; r = correlation with time; "
                 f"dashed = straight-line fit.\nAll {len(all_r)} sessions: median r = {med_r:.2f}, "
                 f"r ≥ 0.9 in {n_hi} of {len(all_r)}",
             ha="left", va="top", fontsize=12.5, color=INK_2)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(FIG_DIR / "fig5_slowmode_examples.pdf")
    fig.savefig(FIG_DIR / "fig5_slowmode_examples.png", dpi=300)
    plt.close(fig)
    return chosen, all_r, med_r, n_hi


def main():
    talk_style()
    FIG_DIR.mkdir(exist_ok=True)
    data = fig_controls()
    for f, lab, ph in VERSIONS:
        r = data[f]
        print(f"{f:22s} {r['n_sess']:2d} sessions {r['n_anim']:2d} mice  R2 {r['mean']:.4f} "
              f"[{r['lo']:.3f}, {r['hi']:.3f}]{'  post hoc' if ph else ''}")
    chosen, all_r, med_r, n_hi = fig_examples()
    for eid, subj in chosen:
        print(f"example {subj:12s} {eid}  r = {all_r[eid]:.3f}")
    print(f"median r over {len(all_r)} sessions = {med_r:.3f}; r >= 0.9 in {n_hi}")


if __name__ == "__main__":
    main()
