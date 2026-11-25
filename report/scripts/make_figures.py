"""Report-specific figures at print size (readable fonts), built only from existing result files.

Run from the repository root with the project environment:
    python report/scripts/make_figures.py
Writes report/figures/{rfig_geometry,rfig_content,rfig_controls,rfig_estimator,rfig_nesting}.pdf. Reads results*/ (not modified).
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
            # session median: the summary A19 fixed in advance for post hoc reference values, because the corrected
            # score is unbounded and one session (1.59) inflates the mouse mean (0.159)
            full = a16.ridge_full_corr.median()
            ax.axhline(full, color=SERIES[2], lw=1.0, ls=":")
            ax.text(3.7, full + 0.012, f"full pop.\n{full:.3f}", fontsize=6.0, color=SERIES[2], ha="center", va="bottom")
            out["full_population"] = {"session_median": full,
                                      "mouse_mean": a16.groupby("subject").ridge_full_corr.mean().mean()}
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
        ax.text(f * o + 0.012, len(versions) - 0.45, lab, ha="left", fontsize=6.8, color=INK_2)
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


# ----------------------------------------------------------------------------- appendix: estimator, nesting
def fig_estimator():
    e = pd.concat([pd.read_parquet(f).assign(eid=Path(f).name[:36]) for f in glob.glob(str(ROOT / "results/estimator/*_d5.pqt"))])
    e["subject"] = e.eid.map(SUBJ)
    lags, xl = [1, 4, 16, 60], ["0.5 s", "2 s", "8 s", "30 s"]
    spec = [("ridge", "r2_best", "full-rank ridge", SERIES[3]), ("rrr", "r2_session_alpha", "lagged RRR", SERIES[0]),
            ("pca", "r2_best", "PCA + ridge", SERIES[1]), ("random", "r2_best", "covariance-matched random", SERIES[2])]
    fig, ax = plt.subplots(figsize=(4.2, 2.4))
    for m, col, name, c in spec:
        mu, se = [], []
        for lag in lags:
            a = e[(e.lag == lag) & (e.method == m)].groupby("subject")[col].mean()
            mu.append(a.mean()); se.append(a.std(ddof=1) / np.sqrt(len(a)))
        mu, se = np.array(mu), np.array(se)
        ax.plot(range(4), mu, marker="o", color=c, label=name)
        ax.fill_between(range(4), mu - se, mu + se, color=c, alpha=0.15, lw=0)
    ax.set_xticks(range(4), xl)
    ax.set_xlabel("prediction lag")
    ax.set_ylabel("held-out $R^2$ of future activity")
    ax.set_ylim(0, 0.42)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "rfig_estimator.pdf")
    plt.close(fig)


def fig_nesting():
    meta = pd.DataFrame([{"eid": Path(f).name[:36], **json.load(open(f))} for f in glob.glob(str(ROOT / "results/subspaces/*_d5.json"))])
    meta["subject"] = meta.eid.map(SUBJ)
    mx = pd.read_csv(ROOT / "results/stats/d5/matrix.csv").set_index(["feature_set", "variable"])
    fig, axs = plt.subplots(1, 2, figsize=(5.5, 2.2))
    ax = axs[0]
    for k, (col, lab) in enumerate([("nest_short_contains_long_k1", "30 s direction\nin 0.5 s subspace"),
                                    ("nest_long_contains_short_k1", "0.5 s direction\nin 30 s subspace")]):
        a = meta.groupby("subject")[col].mean()
        ax.scatter(np.full(len(a), k) + RNG.uniform(-0.12, 0.12, len(a)), a.values, color=MUTED, s=8, zorder=1)
        lo, hi = boot_ci(a.values)
        ax.errorbar(k, a.mean(), yerr=[[a.mean() - lo], [hi - a.mean()]], color=SERIES[0], marker="o", ms=5, capsize=3, zorder=3)
    iso = (5 / meta.p).groupby(meta.subject).mean().mean()
    ax.axhline(iso, color=INK_2, ls="--", lw=0.8)
    ax.text(1.45, iso + 0.02, f"isotropic {iso:.2f}", fontsize=6.5, color=INK_2, ha="right", va="bottom")
    ax.set_xticks([0, 1], ["30 s direction\nin 0.5 s subspace", "0.5 s direction\nin 30 s subspace"])
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("nesting index")
    ax.set_title("a  Nesting (13 mice)", loc="left")
    ax = axs[1]
    for k, (var, lab) in enumerate([("cur_side", "current side\n(AUC, corr.)"), ("prior", "prior\n($R^2$, corr.)")]):
        for j, (fs, c, nm) in enumerate([("orth_short_not_long", SERIES[0], "0.5 s only"), ("orth_long_not_short", SERIES[1], "30 s only")]):
            m, lo, hi = mx.loc[(fs, var), ["mean", "ci_lo", "ci_hi"]]
            x = k + (j - 0.5) * 0.35
            ax.bar(x, m, width=0.33, color=c, label=nm if k == 0 else None)
            ax.errorbar(x, m, yerr=[[m - lo], [hi - m]], color=INK, capsize=2, lw=1)
    ax.axhline(0, color=INK_2, lw=0.8)
    ax.set_xticks([0, 1], ["current side\n(AUC, corr.)", "prior\n($R^2$, corr.)"])
    ax.set_title("b  Orthogonal complements", loc="left")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "rfig_nesting.pdf")
    plt.close(fig)


# ----------------------------------------------------------------------------- timescales (A17 part 0, post hoc)
def fig_timescales():
    from pns.plotting import timescale_panels
    a17 = ROOT / "results" / "a17"
    ts, bl, ac = (pd.read_csv(a17 / f) for f in ("timescales.csv", "blocks.csv", "prior_acf.csv"))
    fig, axs = plt.subplots(1, 2, figsize=(5.5, 2.1), gridspec_kw={"width_ratios": [1.35, 1]})
    timescale_panels(axs[0], axs[1], ts, bl, ac)
    axs[0].set_title("a  Timescales on one clock", loc="left")
    axs[1].set_title("b  Predictable share", loc="left")
    fig.tight_layout()
    fig.savefig(OUT / "rfig_timescales.pdf")
    plt.close(fig)


GRID_C = "#e6e5e0"


def fig_simulation():
    """A18 part A: means over the 16 tasks (two seeds each, averaged) with 95% intervals resampling tasks, from
    results/a18/task_intervals.csv (script 26, stage task_intervals); raw pipeline."""
    ti = pd.read_csv(ROOT / "results" / "a18" / "task_intervals.csv").set_index(["cell", "quantity"])
    rt = json.load(open(ROOT / "results" / "a18" / "real_targets.json"))
    conds = [("nodrift", "no\ndrift"), ("lowrank_x0.33", "drift\n1/3"), ("lowrank_x1", "drift\nx1"),
             ("neg_history_strong", "memory\nonly"), ("neg_pure", "neither")]
    series = [("prior_full", "full population", "o"), ("prior_rrr_60", "30 s subspace", "s"),
              ("prior_rrr_1", "0.5 s subspace", "^")]
    fig, axs = plt.subplots(1, 2, figsize=(5.5, 2.5), gridspec_kw={"width_ratios": [1.9, 1]})
    ax = axs[0]
    x = np.arange(len(conds))
    for j, (col, lab, mk) in enumerate(series):
        m = np.array([ti.loc[(k, col), "mean"] for k, _ in conds])
        ci = np.array([[ti.loc[(k, col), "ci_lo"], ti.loc[(k, col), "ci_hi"]] for k, _ in conds])
        xx = x + (j - 1) * 0.22
        ax.errorbar(xx, m, yerr=[m - ci[:, 0], ci[:, 1] - m], fmt=mk, color=SERIES[j], ms=4.5, lw=1.2,
                    capsize=0, label=lab)
    ax.axhline(0, color=MUTED, lw=0.8)
    ref = rt["session_median"]["full_prior_corr"]
    ax.axhline(ref, color=INK_2, lw=0.9, ls=":")
    ax.text(-0.45, ref - 0.006, "recordings (median)", fontsize=6.3, color=INK_2, ha="left", va="top")
    ax.axvline(2.5, color=GRID_C, lw=0.8)
    ax.text(1.0, -0.175, "prior present", fontsize=6.5, color=INK_2, ha="center")
    ax.text(3.5, -0.175, "no prior", fontsize=6.5, color=INK_2, ha="center")
    ax.set_ylim(-0.19, 0.31)
    ax.set_xticks(x)
    ax.set_xticklabels([l for _, l in conds], fontsize=6.8)
    ax.set_ylabel("corrected prior $R^2$")
    ax.set_title("a  Simulated prior score", loc="left")
    ax.legend(frameon=False, fontsize=6.5, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.0),
              handletextpad=0.2, columnspacing=0.8)
    ax = axs[1]
    pc = [("nodrift", "no\ndrift"), ("lowrank_x0.33", "drift\n1/3"), ("lowrank_x1", "drift\nx1")]
    m = np.array([ti.loc[(k, "p2_change"), "mean"] for k, _ in pc])
    ci = np.array([[ti.loc[(k, "p2_change"), "ci_lo"], ti.loc[(k, "p2_change"), "ci_hi"]] for k, _ in pc])
    ax.errorbar(np.arange(3), m, yerr=[m - ci[:, 0], ci[:, 1] - m], fmt="o", color=SERIES[0], ms=4.5, lw=1.2)
    p2 = pd.read_csv(ROOT / "results" / "stats" / "d5" / "primary.csv")
    r = p2[p2.test.str.startswith("P2")].iloc[0]
    ax.errorbar([3.2], [r["mean"]], yerr=[[r["mean"] - r.ci_lo], [r.ci_hi - r["mean"]]], fmt="D", color=INK,
                ms=4.5, lw=1.2)
    # the recordings' median over mice (the mean is pulled down by a heavy tail)
    ax.scatter([3.2], [r["median"]], marker="D", s=22, facecolors="white", edgecolors=INK, linewidths=1.0, zorder=4)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_xticks([0, 1, 2, 3.2])
    ax.set_xticklabels([l for _, l in pc] + ["record-\nings"], fontsize=6.8)
    ax.set_ylabel("change in corrected $R^2$")
    ax.set_title("b  30 s minus 0.5 s", loc="left")
    for a in axs:
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "rfig_simulation.pdf")
    plt.close(fig)


if __name__ == "__main__":
    import sys as _sys
    if _sys.argv[1:] == ["simulation"]:
        rc()
        fig_simulation()
        raise SystemExit
    if _sys.argv[1:] == ["timescales"]:
        rc()
        fig_timescales()
        raise SystemExit
    rc()
    print(json.dumps(fig_geometry(), indent=1))
    print(json.dumps({k: {s: round(v, 3) for s, v in d.items()} for k, d in fig_content().items()}, indent=1))
    for r in fig_controls():
        print(r)
    fig_estimator()
    fig_nesting()
