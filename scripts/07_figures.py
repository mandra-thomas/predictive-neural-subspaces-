"""The three proposal figures plus a supplementary nesting / orthogonal-complement figure.

fig1_geometry   : (a) half-A x half-B mean principal angle across lags with the covariance-matched chance
                  level, (b) per-animal cross-lag vs same-lag angles, (c) all d principal angles.
fig2_content    : variables x subspaces matrix of held-out decoding (each row on its own scale;
                  experimenter-generated variables are null-corrected).
fig3_estimator  : held-out R^2 of future activity vs lag for RRR, PCA, random and full-rank ridge.
figS1_nesting   : nesting index and orthogonal-complement decoding.
"""
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pns.config import load_frozen
from pns.plotting import DIVERGING, INK, INK_2, MUTED, SEQ_BLUE, SERIES, direct_label, label_line_ends, style
from pns.runner import out_dir, setup

VAR_LABEL = {"cur_side": "Current stim side (AUC, corr.)", "prev_side": "Previous stim side (AUC, corr.)",
             "prior": "Bayes-optimal prior (R², corr.)", "elapsed_time": "Elapsed time (R²)",
             "choice": "Choice (AUC)", "feedback": "Feedback (AUC)", "wheel_speed": "Wheel speed (R²)"}
CORE = ["cur_side", "prev_side", "prior", "elapsed_time"]
SUPP = ["choice", "feedback", "wheel_speed"]


def extra(p):
    p.add_argument("--d", type=int, default=None)


def main():
    args, cfg, _ = setup(__doc__, extra)
    d = args.d or cfg["model"]["d"]
    style()
    lags = list(cfg["lags_bins"])
    lag_s = [lag * cfg["binning"]["bin_s"] for lag in lags]
    lag_lbl = [f"{s:g} s" for s in lag_s]
    st = out_dir(cfg, "stats", f"d{d}")
    fig_dir = cfg["paths"]["figures"]
    fig_dir.mkdir(parents=True, exist_ok=True)
    frozen = load_frozen(cfg)
    subjects = {s["eid"]: s["subject"] for s in frozen["sessions"]}
    eids = pd.read_csv(st / "geometry_sessions.csv")["eid"].tolist()
    geo = pd.concat([pd.read_parquet(out_dir(cfg, "geometry") / f"{e}_d{d}.pqt") for e in eids])
    est = pd.concat([pd.read_parquet(out_dir(cfg, "estimator") / f"{e}_d{d}.pqt") for e in eids])
    metas = {e: json.loads((out_dir(cfg, "subspaces") / f"{e}_d{d}.json").read_text()) for e in eids}
    gs = pd.read_csv(st / "geometry_sessions.csv")
    matrix = pd.read_csv(st / "matrix.csv")
    n_anim = len(set(subjects[e] for e in eids))

    # ------------------------------------------------------------------ figure 1: geometry
    g = geo[(geo.alpha_mode == "session") & (geo.basis == "Vin")]
    M = g.groupby(["lag_A", "lag_B"])["mean_deg"].mean().unstack().loc[lags, lags]
    floor = np.mean([m["floor_mean_deg_mean"] for m in metas.values()])
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.8), gridspec_kw={"width_ratios": [1, 1, 1.1]})
    ax = axs[0]
    im = ax.imshow(M.to_numpy(), cmap=SEQ_BLUE, vmin=0, vmax=90)
    for a in range(len(lags)):
        for b in range(len(lags)):
            v = M.to_numpy()[a, b]
            ax.text(b, a, f"{v:.0f}°", ha="center", va="center", fontsize=8, color="white" if v > 50 else INK)
    ax.set_xticks(range(len(lags)), lag_lbl)
    ax.set_yticks(range(len(lags)), lag_lbl)
    ax.set_xlabel("lag of fit on half B")
    ax.set_ylabel("lag of fit on half A")
    ax.grid(False)
    ax.set_title("a  Mean principal angle", loc="left")
    cb = fig.colorbar(im, ax=ax, shrink=0.8)
    cb.set_label(f"degrees (chance ≈ {floor:.0f}°)", color=INK_2)
    ax = axs[1]
    gs["subject"] = gs["eid"].map(subjects)
    a = gs.groupby("subject")[["same_short", "cross", "same_long"]].mean()
    x = np.arange(3)
    for _, r in a.iterrows():
        ax.plot(x, r.to_numpy(), color=MUTED, lw=1, marker="o", ms=4, zorder=1)
    ax.plot(x, a.mean().to_numpy(), color=SERIES[0], lw=2.5, marker="o", ms=8, zorder=2)
    direct_label(ax, 2, a.mean().iloc[2], "animal mean", dx=8)
    ax.axhline(floor, color=INK_2, lw=1, ls="--")
    ax.text(0, floor, " chance", color=INK_2, fontsize=8, va="bottom")
    ax.set_xticks(x, [f"same lag\n{lag_lbl[0]} vs {lag_lbl[0]}", f"cross lag\n{lag_lbl[0]} vs {lag_lbl[-1]}",
                      f"same lag\n{lag_lbl[-1]} vs {lag_lbl[-1]}"])
    ax.set_ylabel("mean principal angle (deg)")
    ax.set_title(f"b  Cross-lag vs split-half floor ({n_anim} animals)", loc="left")
    ax = axs[2]
    angle_cols = sorted([c for c in g.columns if c.startswith("angle") and c.endswith("_deg")],
                        key=lambda c: int(c[5:-4]))
    k = np.arange(1, len(angle_cols) + 1)
    short, long_ = lags[0], lags[-1]
    curves = {
        f"same lag {lag_lbl[0]}": g[(g.lag_A == short) & (g.lag_B == short)][angle_cols].mean(),
        f"cross lag": pd.concat([g[(g.lag_A == short) & (g.lag_B == long_)][angle_cols],
                                 g[(g.lag_A == long_) & (g.lag_B == short)][angle_cols]]).mean(),
        f"same lag {lag_lbl[-1]}": g[(g.lag_A == long_) & (g.lag_B == long_)][angle_cols].mean(),
    }
    for (name, cvals), col in zip(curves.items(), SERIES):
        ax.plot(k, cvals.to_numpy(), color=col, marker="o", ms=6, label=name)
    ax.set_xlim(0.7, k[-1] + 1.8)
    ax.set_xticks(k)
    ax.set_xlabel("principal angle index (1 = smallest)")
    ax.set_ylabel("angle (deg)")
    ax.set_ylim(0, 90)
    ax.legend(loc="upper left")
    label_line_ends(ax, k[-1], [c.to_numpy()[-1] for c in curves.values()], list(curves))
    ax.set_title("c  All principal angles (session means)", loc="left")
    fig.tight_layout()
    fig.savefig(fig_dir / f"fig1_geometry_d{d}.pdf")
    fig.savefig(fig_dir / f"fig1_geometry_d{d}.png", dpi=200)
    plt.close(fig)

    # ------------------------------------------------------------------ figure 2: content matrix
    cols = [f"rrr_{lag}" for lag in lags] + ["pca", "random"]
    col_lbl = [f"RRR {s}" for s in lag_lbl] + ["PCA", "random"]
    rows = [v for v in CORE + SUPP if v in set(matrix.variable)]
    fig, axs = plt.subplots(len(rows), 1, figsize=(8, 0.62 * len(rows) + 1.2), sharex=True)
    axs = np.atleast_1d(axs)
    for ax, var in zip(axs, rows):
        sub = matrix[matrix.variable == var].set_index("feature_set").reindex(cols)
        vals = sub["mean"].to_numpy()
        center = 0.5 if var in ("choice", "feedback") else 0.0
        span = np.nanmax(np.abs(vals - center)) or 1.0
        ax.imshow((vals - center)[None, :], cmap=DIVERGING, vmin=-span, vmax=span, aspect="auto")
        for j, (v, lo, hi) in enumerate(zip(vals, sub["ci_lo"], sub["ci_hi"])):
            ax.text(j, 0, f"{v:.3f}\n[{lo:.3f}, {hi:.3f}]", ha="center", va="center", fontsize=7, color=INK)
        ax.set_yticks([0], [VAR_LABEL.get(var, var)])
        ax.grid(False)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(length=0)
        if var == CORE[-1] and SUPP[0] in rows:
            ax.axhline(0.5, color=INK, lw=1.5)
    axs[-1].set_xticks(range(len(cols)), col_lbl)
    axs[0].set_title(f"Decoding from each subspace (animal means, 95% CI; {n_anim} animals)\n"
                     "Each row has its own colour scale; 'corr.' = real − pseudo-session null median",
                     loc="left", fontsize=9)
    fig.tight_layout()
    fig.savefig(fig_dir / f"fig2_content_d{d}.pdf")
    fig.savefig(fig_dir / f"fig2_content_d{d}.png", dpi=200)
    plt.close(fig)

    # ------------------------------------------------------------------ figure 3: estimator check
    est["subject"] = est["eid"].map(subjects)
    fig, ax = plt.subplots(figsize=(6, 3.8))
    spec = [("rrr", "r2_session_alpha", "lagged RRR"), ("pca", "r2_best", "PCA"),
            ("random", "r2_best", "random (cov-matched)"), ("ridge", "r2_best", "full-rank ridge")]
    order = [3, 0, 1, 2]                       # draw full-rank first; colours stay fixed per method
    ends = {}
    for i in order:
        m, col, name = spec[i]
        a = est[est.method == m].groupby(["subject", "lag"])[col].mean().unstack()
        mu, se = a.mean(), a.std() / np.sqrt(len(a))
        x = np.array(lag_s)
        ax.plot(x, mu[lags].to_numpy(), color=SERIES[i], marker="o", ms=6, label=name)
        ax.fill_between(x, (mu - se)[lags], (mu + se)[lags], color=SERIES[i], alpha=0.15, lw=0)
        ends[name] = float(mu[lags].to_numpy()[-1])
    ax.set_xscale("log")
    ax.set_xticks(lag_s, lag_lbl)
    ax.minorticks_off()
    ax.set_xlim(lag_s[0] * 0.8, lag_s[-1] * 4)
    ax.axhline(0, color=INK_2, lw=0.8)
    ax.set_xlabel("prediction lag")
    ax.set_ylabel("held-out R² of future activity")
    ax.set_title(f"Estimator check, d = {d} (mean ± s.e.m. over {n_anim} animals)", loc="left")
    ax.legend(loc="upper right")
    label_line_ends(ax, lag_s[-1], list(ends.values()), list(ends))
    fig.tight_layout()
    fig.savefig(fig_dir / f"fig3_estimator_d{d}.pdf")
    fig.savefig(fig_dir / f"fig3_estimator_d{d}.png", dpi=200)
    plt.close(fig)

    # ------------------------------------------------------------------ figure S1: nesting + complements
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.4))
    nest = pd.DataFrame([{"subject": subjects[e], **{k: v for k, v in m.items() if k.startswith("nest_")}}
                         for e, m in metas.items()]).groupby("subject").mean()
    ax = axs[0]
    labels = {"nest_short_contains_long_k1": f"{lag_lbl[-1]} lead dir.\nin {lag_lbl[0]} subspace",
              "nest_long_contains_short_k1": f"{lag_lbl[0]} lead dir.\nin {lag_lbl[-1]} subspace"}
    for j, (c, lbl) in enumerate(labels.items()):
        ax.scatter(np.full(len(nest), j) + np.random.default_rng(j).uniform(-0.08, 0.08, len(nest)),
                   nest[c], color=MUTED, s=18, zorder=1)
        ax.plot([j - 0.2, j + 0.2], [nest[c].mean()] * 2, color=SERIES[0], lw=3, zorder=2)
    ax.axhline(d / metas[eids[0]]["p"], color=INK_2, ls="--", lw=1)
    ax.text(1.45, d / metas[eids[0]]["p"], "isotropic\nchance", fontsize=7, color=INK_2, va="center")
    ax.set_xticks(range(2), list(labels.values()))
    ax.set_xlim(-0.5, 1.9)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("nesting index")
    ax.set_title("a  Nesting of leading predictive direction", loc="left")
    ax = axs[1]
    sets = [("orth_short_not_long", f"{lag_lbl[0]} only"), ("orth_long_not_short", f"{lag_lbl[-1]} only")]
    width = 0.36
    for j, var in enumerate(["cur_side", "prior"]):
        for i, (fs, lbl) in enumerate(sets):
            r = matrix[(matrix.variable == var) & (matrix.feature_set == fs)]
            if r.empty:
                continue
            v, lo, hi = float(r["mean"].iloc[0]), float(r["ci_lo"].iloc[0]), float(r["ci_hi"].iloc[0])
            xx = j + (i - 0.5) * (width + 0.04)
            ax.bar(xx, v, width, color=SERIES[i], label=lbl if j == 0 else None)
            ax.errorbar(xx, v, yerr=[[v - lo], [hi - v]], color=INK, lw=1, capsize=3)
    ax.axhline(0, color=INK_2, lw=0.8)
    ax.set_xticks(range(2), ["current stim side\n(AUC, corr.)", "prior\n(R², corr.)"])
    ax.set_ylabel("null-corrected score")
    ax.legend(title="subspace part", loc="upper left", bbox_to_anchor=(1.0, 1.0), title_fontsize=8)
    ax.set_title("b  Decoding from orthogonal complements", loc="left")
    fig.tight_layout()
    fig.savefig(fig_dir / f"figS1_nesting_d{d}.pdf")
    fig.savefig(fig_dir / f"figS1_nesting_d{d}.png", dpi=200)
    plt.close(fig)
    print(f"figures written to {fig_dir}")


if __name__ == "__main__":
    main()
