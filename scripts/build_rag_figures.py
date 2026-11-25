# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib", "numpy"]
# ///
"""Figures for the RAG slides: a sketch of an embedding space and the angle between two vectors.

The cosine values (0.46, 0.16) are real, from text-embedding-3-small.
Usage: uv run --script scripts/build_rag_figures.py slides/sesion5/img
"""

import sys
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

bg, ink, muted = "#f0f1eb", "#2b2b2b", "#6b6b66"
C = {
    "Capital": "#2a78d6",
    "Liquidity": "#eb6834",
    "Retail lending": "#1baf7a",
    "Money laundering": "#6250d6",
}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13})
out = sys.argv[1]

# 1) schematic map of meaning
pts = {
    "Capital": [
        ((1.0, 4.2), "CET1 capital ratio"),
        ((1.9, 4.75), "own funds requirements"),
        ((0.6, 3.5), "capital conservation buffer"),
    ],
    "Liquidity": [
        ((5.2, 4.6), "liquidity coverage ratio"),
        ((6.0, 3.9), "high-quality liquid assets"),
        ((4.8, 3.6), "cash outflows over 30 days"),
    ],
    "Retail lending": [
        ((5.6, 1.4), "mortgage interest rate"),
        ((6.6, 0.8), "fixed-rate home loan"),
        ((4.9, 0.7), "credit card limit"),
    ],
    "Money laundering": [
        ((1.2, 1.3), "suspicious cash deposits"),
        ((0.5, 0.6), "customer due diligence"),
        ((2.6, 0.45), "sanctions screening"),
    ],
}
fig, ax = plt.subplots(figsize=(11, 5), dpi=150)
fig.patch.set_facecolor(bg)
ax.set_facecolor(bg)
for g, items in pts.items():
    xs = [p[0][0] for p in items]
    ys = [p[0][1] for p in items]
    ax.add_patch(
        matplotlib.patches.Ellipse(
            (np.mean(xs) + 0.4, np.mean(ys)), 3.3, 1.75, color=C[g], alpha=0.10, lw=0
        )
    )
    ax.text(
        np.mean(xs) + 0.4,
        max(ys) + 0.55,
        g,
        color=C[g],
        fontsize=14,
        fontweight="bold",
        ha="center",
    )
    for (x, y), t in items:
        ax.scatter(x, y, s=80, color=C[g], edgecolor=bg, linewidth=2, zorder=3)
        ax.text(x + 0.12, y - 0.05, t, color=ink, fontsize=11.5, va="center")
qx, qy = 1.6, 3.95
ax.scatter(qx, qy, s=320, marker="*", color=ink, zorder=4)
ax.annotate(
    'question: "How much capital\nmust a bank hold?"',
    (qx, qy),
    xytext=(3.0, 2.55),
    color=ink,
    fontsize=12,
    fontweight="bold",
    arrowprops=dict(arrowstyle="->", color=muted, lw=1.5),
)
ax.set_xlim(0, 8.6)
ax.set_ylim(0, 5.7)
ax.axis("off")
fig.tight_layout()
fig.savefig(out + "/embedding_map.png", facecolor=bg)

# 2) angle between vectors
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), dpi=150)
fig.patch.set_facecolor(bg)


def panel(ax, a2, label2, col2, title, cos):
    ax.set_facecolor(bg)
    ax.axis("off")
    ax.set_xlim(-0.2, 1.6)
    ax.set_ylim(-0.25, 1.35)
    ax.set_aspect("equal")
    a1 = np.deg2rad(20)
    a2 = np.deg2rad(a2)
    for a, col, lab in [(a1, ink, '"How much capital\nmust a bank hold?"'), (a2, col2, label2)]:
        ax.annotate(
            "",
            xy=(np.cos(a), np.sin(a)),
            xytext=(0, 0),
            arrowprops=dict(arrowstyle="-|>", color=col, lw=3, mutation_scale=20),
        )
        ax.text(1.06 * np.cos(a), 1.06 * np.sin(a), lab, color=ink, fontsize=11.5, va="center")
    th = np.linspace(a1, a2, 50)
    ax.plot(0.28 * np.cos(th), 0.28 * np.sin(th), color=muted, lw=1.5)
    ax.text(
        0.02,
        -0.17,
        f"{title}: cosine similarity {cos}",
        color=ink,
        fontsize=12.5,
        fontweight="bold",
    )


panel(axs[0], 38, '"CET1 capital ratio"', C["Capital"], "Small angle", "0.46")
panel(axs[1], 100, '"mortgage interest rate"', C["Retail lending"], "Large angle", "0.16")
fig.tight_layout()
fig.savefig(out + "/embedding_angle.png", facecolor=bg)
