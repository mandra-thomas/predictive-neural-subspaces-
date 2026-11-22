"""Slide-sized versions of two talk figures (text 10-11 pt at the size they are shown). Reads existing result files
only: no new analyses, no refits. Does not touch the report figures from 07_figures.py or 19_talk_figures.py.

slide_fig5 : the slow mode (pns.slowmode.slow_mode, as in fig5) for ALL 16 sessions as small multiples, sorted by
             its correlation with elapsed time (r, printed in each panel); a dashed straight-line fit per panel.
             No session is selected, so the figure shows the full spread (12 of 16 have r >= 0.9).
slide_figS1: (a) nesting index per animal (the 0.5 s subspace containing the 30 s leading direction, and the reverse),
             with the isotropic chance level d/p marked as a low bar (no covariance-matched chance was computed);
             (b) current-side and prior decoding (null-corrected, animal means, 95% CI, from stats/d5/matrix.csv)
             from the full 0.5 s and 30 s subspaces and from each one projected off the other
             (pns.geometry.complement_basis: the part of span(A) orthogonal to span(B); this is generally a new
             5-D space, not a subset of A, so it can score higher than A itself).

Writes figures/slide_fig5.pdf and figures/slide_figS1.pdf (figures/ is gitignored; rebuild the slides after running).
"""
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pns.config import ROOT
from pns.pipeline import session_S
from pns.plotting import INK, INK_2, MUTED, SERIES, style
from pns.slowmode import slow_mode, window_edges

D = 5
LONG_LAG = 60                    # bins of 0.5 s = 30 s
FIG_DIR = ROOT / "figures"
W_IN = 5.6                       # final width on a 16:9 slide (full text width); heights per figure below
H_FIG5, H_FIGS1 = 2.3, 1.85


def slide_style():
    style()
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10, "xtick.labelsize": 10,
                         "ytick.labelsize": 10, "legend.fontsize": 10})


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
    sessions = [(s["eid"], s["subject"]) for s in frozen["sessions"]]
    traces = {eid: session_trace(eid) for eid, _ in sessions}
    rs = {eid: tr[3] for eid, tr in traces.items()}
    med = float(np.median(list(rs.values())))
    order = sorted(sessions, key=lambda es: -rs[es[0]])
    fig, axs = plt.subplots(4, 4, figsize=(W_IN, H_FIG5), sharey=True)
    for ax, (eid, subj) in zip(axs.flat, order):
        t, z, ok, r = traces[eid]
        b = np.polyfit(t[ok], z[ok], 1)
        ax.plot(t[ok], np.polyval(b, t[ok]), color=INK_2, lw=0.9, ls="--", zorder=1)
        ax.plot(t[ok], z[ok], color=SERIES[0], lw=1.1, zorder=2)
        ax.text(0.03, 0.97, f"r = {r:.2f}", transform=ax.transAxes, ha="left", va="top", fontsize=10, color=INK)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        ax.set_ylim(-3.2, 3.2)
    fig.supxlabel("time in session (each panel: one session, start to end)", fontsize=10, color=INK_2, y=0.0)
    fig.supylabel("slow mode", fontsize=10, color=INK_2, x=0.0)
    fig.tight_layout(pad=0.4, h_pad=0.25, w_pad=0.25)
    fig.savefig(FIG_DIR / "slide_fig5.pdf")
    plt.close(fig)
    picks = [(eid, subj, "") for eid, subj in order]
    return picks, rs, med


def fig_nesting():
    st = ROOT / "results" / "stats" / f"d{D}"
    eids = pd.read_csv(st / "geometry_sessions.csv")
    subj = dict(zip(eids.eid, eids.subject))
    metas = {e: json.loads((ROOT / "results" / "subspaces" / f"{e}_d{D}.json").read_text()) for e in subj}
    nest = pd.DataFrame([{"subject": subj[e], **{k: v for k, v in m.items() if k.startswith("nest_")}}
                         for e, m in metas.items()]).groupby("subject").mean()
    iso = float(np.mean([D / m["p"] for m in metas.values()]))
    matrix = pd.read_csv(st / "matrix.csv")
    fig, axs = plt.subplots(1, 2, figsize=(W_IN, H_FIGS1), gridspec_kw={"width_ratios": [1, 1.5]})
    ax = axs[0]
    cols = [("nest_short_contains_long_k1", "30 s dir.\nin 0.5 s"), ("nest_long_contains_short_k1", "0.5 s dir.\nin 30 s")]
    for j, (c, _) in enumerate(cols):
        ax.scatter(np.full(len(nest), j) + np.random.default_rng(j).uniform(-0.1, 0.1, len(nest)), nest[c],
                   color=MUTED, s=12, zorder=1)
        ax.plot([j - 0.25, j + 0.25], [nest[c].mean()] * 2, color=SERIES[0], lw=3, zorder=2)
    ax.axhline(iso, color=INK_2, ls="--", lw=1)
    ax.text(-0.45, iso + 0.03, "isotropic chance", fontsize=10, color=INK_2, ha="left", va="bottom")
    ax.set_xticks(range(2), [l for _, l in cols])
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("nesting index")
    ax.set_title("a  leading direction shared", loc="left", fontsize=10)
    ax = axs[1]
    sets = [("rrr_1", "0.5 s"), ("orth_short_not_long", "0.5 s off 30 s"),
            ("rrr_60", "30 s"), ("orth_long_not_short", "30 s off 0.5 s")]
    colors = [SERIES[0], "#9ec5f4", SERIES[1], "#f5b79a"]
    width = 0.19
    for j, var in enumerate(["cur_side", "prior"]):
        for i, (fs, lbl) in enumerate(sets):
            r = matrix[(matrix.variable == var) & (matrix.feature_set == fs)].iloc[0]
            v, lo, hi = float(r["mean"]), float(r["ci_lo"]), float(r["ci_hi"])
            xx = j + (i - 1.5) * (width + 0.02)
            ax.bar(xx, v, width, color=colors[i], label=lbl if j == 0 else None)
            ax.errorbar(xx, v, yerr=[[v - lo], [hi - v]], color=INK, lw=0.9, capsize=2)
    ax.axhline(0, color=INK_2, lw=0.8)
    ax.set_xticks(range(2), ["stimulus side\n(corrected AUC)", "prior\n(corrected R²)"])
    ax.set_ylim(-0.2, 0.64)
    ax.set_yticks([-0.2, 0, 0.2, 0.4])
    ax.legend(loc="upper right", ncol=2, fontsize=10, handlelength=0.8, borderaxespad=0.1, columnspacing=0.6,
              handletextpad=0.4)
    ax.set_title("b  decoding, full vs projected", loc="left", fontsize=10)
    fig.tight_layout(pad=0.3, w_pad=0.8)
    fig.savefig(FIG_DIR / "slide_figS1.pdf")
    plt.close(fig)
    return nest, iso


def main():
    slide_style()
    FIG_DIR.mkdir(exist_ok=True)
    picks, rs, med = fig_examples()
    print(f"median r over {len(rs)} sessions = {med:.3f}")
    for eid, subj, what in picks:
        print(f"  {subj:12s} r = {rs[eid]:.3f}  {eid}")
    nest, iso = fig_nesting()
    print(f"nesting short-contains-long mean {nest['nest_short_contains_long_k1'].mean():.3f}, "
          f"long-contains-short {nest['nest_long_contains_short_k1'].mean():.3f}, isotropic chance {iso:.3f}")


if __name__ == "__main__":
    main()
