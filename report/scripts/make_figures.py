"""Report-specific figures at print size (readable fonts), built only from existing result files.

Run from the repository root with the project environment:
    python report/scripts/make_figures.py
Writes report/figures/{rfig_geometry,rfig_content,rfig_controls}.pdf. Reads results*/ (not modified).
Summary convention: sessions are averaged within mouse, then averaged over mice (as in the primary tests);
95% CIs are percentile bootstraps over mice (10,000 resamples, seed 0) unless taken from matrix.csv.
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from pns.plotting import INK, INK_2, MUTED, SERIES, style  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

OUT = ROOT / "report" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
FROZEN = json.load(open(ROOT / "data" / "meta" / "frozen.json"))
SUBJ = {s["eid"]: s["subject"] for s in FROZEN["sessions"]}
RNG = np.random.default_rng(0)


def boot_ci(x, n=10000):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    m = RNG.choice(x, size=(n, len(x)), replace=True).mean(1)
    return np.quantile(m, [0.025, 0.975])


def rc():
    style()
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "xtick.labelsize": 7.5,
                         "ytick.labelsize": 7.5, "legend.fontsize": 7.5, "lines.linewidth": 1.6,
                         "lines.markersize": 4.5, "figure.facecolor": "white", "axes.facecolor": "white",
                         "savefig.facecolor": "white"})


# ----------------------------------------------------------------------------- geometry
def fig_geometry():
    g = pd.concat([pd.read_parquet(f).assign(eid=Path(f).name[:36]) for f in glob.glob(str(ROOT / "results/geometry/*_d5.pqt"))])
    g = g[g.alpha_mode == "session"]
    g["subject"] = g.eid.map(SUBJ)
    meta = pd.DataFrame([{"eid": Path(f).name[:36], **json.load(open(f))} for f in glob.glob(str(ROOT / "results/subspaces/*_d5.json"))])
    meta["subject"] = meta.eid.map(SUBJ)
    chance = meta.groupby("subject").floor_mean_deg_mean.mean()

    def comp(basis, a, b, col):
        x = g[(g.basis == basis) & (((g.lag_A == a) & (g.lag_B == b)) | ((g.lag_A == b) & (g.lag_B == a)))]
        return x.groupby(["eid", "subject"])[col].mean().groupby("subject").mean()

    fig, axs = plt.subplots(1, 3, figsize=(5.5, 1.95), gridspec_kw={"width_ratios": [1.15, 1, 1]})
    labels = ["same\n0.5 s", "cross\nlag", "same\n30 s"]
    for k, (basis, title) in enumerate([("Vin", "a  Readout basis (tested)"), ("Vout", "c  Loading basis")]):
        ax = axs[0] if k == 0 else axs[2]
        cols = [comp(basis, 1, 1, "mean_deg"), comp(basis, 1, 60, "mean_deg"), comp(basis, 60, 60, "mean_deg")]
        df = pd.concat(cols, axis=1)
        for _, r in df.iterrows():
            ax.plot([0, 1, 2], r.values, color=MUTED, lw=0.8, marker="o", ms=2.5, zorder=1)
        ax.plot([0, 1, 2], df.mean().values, color=SERIES[0], lw=2, marker="o", ms=5, zorder=3)
        if basis == "Vin":
            ax.axhline(chance.mean(), color=INK_2, ls="--", lw=0.9)
            ax.text(-0.25, 86, f"dashed: chance {chance.mean():.1f}", fontsize=6.5, color=INK_2, va="center", ha="left")
        means = df.mean().values
        ax.set_xticks([0, 1, 2], [f"{l}\n({m:.1f})" for l, m in zip(labels, means)])
        ax.set_xlim(-0.3, 2.3)
        ax.set_ylim(22, 90)
        ax.set_ylabel("mean principal angle (deg)" if k == 0 else "")
        ax.set_title(title, loc="left")
    # b: all principal angles, readout basis, mouse means
    ax = axs[1]
    angle_cols = [f"angle{i}_deg" for i in range(1, 6)]
    for (a, b), name, c in [((1, 1), "0.5 s vs 0.5 s", SERIES[0]), ((1, 60), "cross lag", SERIES[1]),
                             ((60, 60), "30 s vs 30 s", SERIES[2])]:
        vals = [comp("Vin", a, b, col).mean() for col in angle_cols]
        ax.plot(range(1, 6), vals, marker="o", color=c, label=name)
    ax.set_xticks(range(1, 6))
    ax.set_xlabel("principal angle index")
    ax.set_ylim(25, 100)
    ax.set_ylabel("angle (deg)")
    ax.set_title("b  All five angles", loc="left")
    ax.legend(loc="lower right", handlelength=0.9, borderaxespad=0.1, fontsize=6.5, labelspacing=0.25, handletextpad=0.4)
    fig.tight_layout(w_pad=0.6)
    fig.savefig(OUT / "rfig_geometry.pdf")
    plt.close(fig)
    return {"readout": [float(c.mean()) for c in [comp("Vin", 1, 1, "mean_deg"), comp("Vin", 1, 60, "mean_deg"), comp("Vin", 60, 60, "mean_deg")]],
            "loading": [float(c.mean()) for c in [comp("Vout", 1, 1, "mean_deg"), comp("Vout", 1, 60, "mean_deg"), comp("Vout", 60, 60, "mean_deg")]],
            "chance": float(chance.mean())}


# ----------------------------------------------------------------------------- content vs lag
def fig_content():
    ss = pd.read_csv(ROOT / "results/stats/d5/session_scores.csv")
    mx = pd.read_csv(ROOT / "results/stats/d5/matrix.csv").set_index(["feature_set", "variable"])
    sets = ["rrr_1", "rrr_4", "rrr_16", "rrr_60", "pca", "random"]
    xt = ["0.5 s", "2 s", "8 s", "30 s", "PCA", "rand."]
    xs = [0, 1, 2, 3, 4.4, 5.4]
    panels = [("prior", "a  Block prior\n(corrected $R^2$)"), ("cur_side", "b  Current stimulus side\n(corrected AUC)"),
              ("elapsed_time", "c  Elapsed time\n(interpolated $R^2$)")]
    fig, axs = plt.subplots(1, 3, figsize=(5.5, 2.05))
    out = {}
    for ax, (var, title) in zip(axs, panels):
        am = ss[(ss.variable == var) & ss.feature_set.isin(sets)].groupby(["subject", "feature_set"]).value.mean().unstack()[sets]
        for _, r in am.iterrows():
            ax.plot(xs[:4], r.values[:4], color=MUTED, lw=0.6, zorder=1)
            ax.scatter(xs[4:], r.values[4:], color=MUTED, s=5, zorder=1)
        mean = [mx.loc[(s, var), "mean"] for s in sets]
        lo = [mx.loc[(s, var), "ci_lo"] for s in sets]
        hi = [mx.loc[(s, var), "ci_hi"] for s in sets]
        ax.errorbar(xs[:4], mean[:4], yerr=[np.subtract(mean[:4], lo[:4]), np.subtract(hi[:4], mean[:4])],
                    color=SERIES[0], marker="o", ms=4.5, lw=1.8, capsize=2, zorder=3)
        ax.errorbar(xs[4:], mean[4:], yerr=[np.subtract(mean[4:], lo[4:]), np.subtract(hi[4:], mean[4:])],
                    color=SERIES[1], marker="s", ms=4, lw=0, elinewidth=1.4, capsize=2, zorder=3)
        if var != "elapsed_time":
            ax.axhline(0, color=INK_2, lw=0.8)
        if var == "prior":
            a16 = pd.read_csv(ROOT / "results/a16/sessions_d5.csv")
            full = a16.groupby("subject").ridge_full_corr.mean().mean()
            ax.axhline(full, color=SERIES[2], lw=1.0, ls=":")
            ax.text(5.75, full + 0.015, f"full population {full:.3f}", fontsize=6.3, color=SERIES[2], ha="right", va="bottom")
            out["full_population"] = {"mouse_mean": full}
        ax.set_xticks(xs, xt, rotation=0)
        ax.tick_params(axis="x", labelsize=6.8)
        ax.set_title(title, loc="left")
        out.setdefault(var, {}).update(dict(zip(sets, mean)))
    axs[0].set_xlabel("RRR lag", fontsize=7.5, loc="left")
    fig.tight_layout(w_pad=0.5)
    fig.savefig(OUT / "rfig_content.pdf")
    plt.close(fig)
    return out


# ----------------------------------------------------------------------------- recording controls
def fig_controls():
    orig = pd.read_csv(ROOT / "results/stats/d5/drift.csv").set_index("eid")
    versions = [("results", "Original units"), ("results_stable", "Stable units only"),
                ("results_mua", "Sorting-free multi-unit"), ("results_ampstable", "Rate- and amplitude-stable units"),
                ("results_ampcorr_high", "Amplitude-corrected, maximal"),
                ("results_ampcorr_slow", "Amplitude-corrected, slow-maximal (post hoc)")]
    fig, ax = plt.subplots(figsize=(5.5, 2.45))
    rows = []
    for k, (root, name) in enumerate(versions):
        d = pd.read_csv(ROOT / root / "stats/d5/drift.csv")
        am = d.groupby("subject").elapsed_long.mean()
        base = orig.loc[d.eid].reset_index().groupby("subject").elapsed_long.mean()
        pca = d.groupby("subject").elapsed_pca.mean()
        lo, hi = boot_ci(am.values)
        y = len(versions) - 1 - k
        ax.scatter(am.values, np.full(len(am), y) + RNG.uniform(-0.12, 0.12, len(am)), color=MUTED, s=6, zorder=1)
        c = SERIES[1] if "post hoc" in name else SERIES[0]
        ax.plot([lo, hi], [y, y], color=c, lw=2, zorder=2)
        ax.plot(am.mean(), y, "o", color=c, ms=6, zorder=3)
        if root != "results":
            ax.plot(base.mean(), y, "o", mfc="white", mec=INK, ms=5, zorder=4)
        nses, nm = d.eid.nunique(), am.size
        ax.text(1.02, y, f"{am.mean():.2f} vs {base.mean():.2f}  ({nses}/{nm})", va="center", fontsize=7, color=INK,
                transform=ax.get_yaxis_transform())
        rows.append({"version": name, "n_sessions": nses, "n_mice": nm, "r2": am.mean(), "ci": (lo, hi),
                     "same_session_original": base.mean(), "pca": pca.mean()})
    o = orig.groupby("subject").elapsed_long.mean().mean()
    ax.axvline(o, color=INK_2, lw=0.9)
    for f, lab in [(0.75, "75%"), (0.5, "50%")]:
        ax.axvline(f * o, color=INK_2, lw=0.8, ls="--")
        ax.text(f * o, len(versions) - 0.45, lab, ha="center", fontsize=6.8, color=INK_2)
    ax.set_yticks(range(len(versions)), [v[1] for v in versions][::-1])
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.6, len(versions) - 0.2)
    ax.set_xlabel("elapsed-time $R^2$ of the 30 s subspace (interpolated)")
    ax.text(1.02, len(versions) - 0.45, "copy vs original,\nsame sessions (sess./mice)", fontsize=6.5, color=INK_2,
            transform=ax.get_yaxis_transform(), va="bottom")
    fig.tight_layout()
    fig.subplots_adjust(right=0.74)
    fig.savefig(OUT / "rfig_controls.pdf")
    plt.close(fig)
    return rows


if __name__ == "__main__":
    rc()
    print(json.dumps(fig_geometry(), indent=1))
    print(json.dumps({k: {s: round(v, 3) for s, v in d.items()} for k, d in fig_content().items()}, indent=1))
    for r in fig_controls():
        print(r)
