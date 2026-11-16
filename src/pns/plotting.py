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


def direct_label(ax, x, y, text, color_ink=INK_2, dx=4, dy=0):
    """Label at the line end, in ink (not the series colour)."""
    ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points", va="center", fontsize=8,
                color=color_ink)
