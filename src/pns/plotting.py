"""Shared figure style: categorical slots in fixed order, recessive axes, text in ink (never series color).

Palette: first slots of the dataviz reference palette (light mode), used in their documented order
(adjacent-pair validated). Diverging: blue <-> red with a gray midpoint.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]      # blue, orange, aqua, yellow (fixed order)
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#a8a7a2"
SURFACE = "#fcfcfb"
GRID = "#e6e5e0"
SEQ_BLUE = LinearSegmentedColormap.from_list(
    "seq_blue", ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"])
DIVERGING = LinearSegmentedColormap.from_list("div_blue_red", ["#256abf", "#86b6ef", "#f0efec", "#ef8f8e", "#c43c3c"])


def style() -> None:
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": MUTED, "axes.labelcolor": INK_2, "axes.titlecolor": INK, "axes.titlesize": 10,
        "axes.titleweight": "bold", "axes.labelsize": 9, "xtick.color": INK_2, "ytick.color": INK_2,
        "xtick.labelsize": 8, "ytick.labelsize": 8, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
        "lines.linewidth": 2.0, "lines.markersize": 6, "legend.frameon": False, "legend.fontsize": 8,
        "font.size": 9, "pdf.fonttype": 42,
    })


def label_line_ends(ax, x, ys, texts, min_gap_frac: float = 0.06, dx: int = 8) -> None:
    """Direct labels at line ends, in ink, pushed apart vertically so they never collide.
    Call after the y-limits are final."""
    from matplotlib.transforms import offset_copy
    lo, hi = ax.get_ylim()
    gap = min_gap_frac * (hi - lo)
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    placed: list[float] = []
    for i in order:
        placed.append(ys[i] if not placed else max(ys[i], placed[-1] + gap))
    over = placed[-1] - (hi - gap / 2)
    if over > 0:
        placed = [y - over for y in placed]
    tr = offset_copy(ax.transData, fig=ax.figure, x=dx, y=0, units="points")
    for i, y in zip(order, placed):
        ax.text(x, y, texts[i], transform=tr, va="center", fontsize=8, color=INK_2, clip_on=False)


def timescale_panels(ax_a, ax_b, ts, blocks, acf_curves, registered=(0.5, 2, 8, 30), fs=7.5,
                     compact=False) -> None:
    """A17 Part 0 figure. ts: results/a17/timescales.csv; blocks: blocks.csv; acf_curves: prior_acf.csv.
    (a) the task's timescales on one log clock (seconds), with the registered lag range shaded;
    (b) the prior's predictable share rho(lag)^2 (median and IQR over sessions) against a linear ramp (rho = 1)."""
    import numpy as np
    rng = np.random.default_rng(0)
    band = dict(color=SERIES[0], alpha=0.10, lw=0)
    # (a) one clock
    rows = [("stimulus interval", ts["stim_interval_s"].to_numpy(), SERIES[3]),
            ("prior timescale $\\tau_\\pi$", ts["tau_pi_s"].to_numpy(), SERIES[0]),
            ("block duration", blocks["minutes"].dropna().to_numpy() * 60, SERIES[1]),
            ("session", ts["duration_min"].to_numpy() * 60, SERIES[2])]
    ax_a.axvspan(min(registered), max(registered), **band)
    for lag in registered:
        ax_a.axvline(lag, color=SERIES[0], lw=0.6, alpha=0.5)
    for i, (name, vals, col) in enumerate(rows):
        y = len(rows) - 1 - i
        ax_a.scatter(vals, y + rng.uniform(-0.18, 0.18, len(vals)), s=6, color=col, alpha=0.6, lw=0)
        med = float(np.median(vals))
        ax_a.plot([med, med], [y - 0.32, y + 0.32], color=INK, lw=1.2)
    ax_a.set_yticks(range(len(rows)), [r[0] for r in rows][::-1])
    ax_a.set_xscale("log")
    ax_a.set_xlim(0.3, 8000)
    ax_a.set_xticks([1, 10, 60, 600, 3600],
                    ["1 s", "", "1 min", "", "1 h"] if compact else ["1 s", "10 s", "1 min", "10 min", "1 h"])
    ax_a.minorticks_off()
    ax_a.grid(axis="y", visible=False)
    ax_a.text(np.sqrt(min(registered) * max(registered)), len(rows) - 0.45, "lags tested\n(0.5–30 s)",
              ha="center", va="bottom", fontsize=fs, color=INK_2)
    ax_a.set_ylim(-0.6, len(rows) - 0.45 + 0.9)
    # (b) predictable share
    piv = acf_curves.pivot(index="lag_s", columns="eid", values="rho") ** 2
    lag = piv.index.to_numpy()
    med, q1, q3 = piv.median(1), piv.quantile(0.25, 1), piv.quantile(0.75, 1)
    ax_b.axvspan(min(registered), max(registered), **band)
    ax_b.fill_between(lag, q1, q3, color=SERIES[0], alpha=0.25, lw=0)
    ax_b.plot(lag, med, color=SERIES[0])
    ax_b.axhline(1.0, color=INK_2, ls="--", lw=1.2)
    ax_b.text(0.6, 0.97, "session ramp ($\\rho^2 = 1$)", fontsize=fs, color=INK_2, va="top")
    for t in (30, 60, 120):
        v = float(np.interp(t, lag, med))
        ax_b.plot(t, v, "o", color=SERIES[0], ms=3.5)
        ax_b.annotate(f"{v:.2f}", (t, v), xytext=(4, 3), textcoords="offset points", fontsize=fs, color=INK_2)
    ax_b.text(0.6, 0.27, "block prior\n(median, IQR)", fontsize=fs, color=SERIES[0], va="top")
    ax_b.set_xscale("log")
    ax_b.set_xlim(0.5, 1200)
    ax_b.set_ylim(0, 1.1)
    ax_b.set_xticks([1, 10, 60, 600], ["1 s", "", "1 min", ""] if compact else ["1 s", "10 s", "1 min", "10 min"])
    ax_b.minorticks_off()
    ax_b.set_xlabel("prediction lag $\\Delta$")
    ax_b.set_ylabel("$\\rho(\\Delta)^2$")


def direct_label(ax, x, y, text, color_ink=INK_2, dx=4, dy=0):
    """Label at the line end, in ink (not the series colour)."""
    ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points", va="center", fontsize=8,
                color=color_ink)
