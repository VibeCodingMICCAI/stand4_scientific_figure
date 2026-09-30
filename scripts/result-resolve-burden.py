"""Matplotlib reconstruction of Figure 3a, using the supplied mean DSC data.

Reference: https://papers.miccai.org/miccai-2026/paper/0562_paper.pdf
The paper's gain annotations are written as percentages; here they are labeled
in percentage points (pp), as in the user's table. The 62.2% agreement reference
is reported on a smaller, independently annotated subset (not the full test set).
"""

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnnotationBbox, DrawingArea
from matplotlib.patches import Circle, Ellipse, PathPatch, Polygon
from matplotlib.path import Path as MplPath


def physician_icon():
    """A small vector physician icon, drawn entirely with Matplotlib."""
    icon = DrawingArea(22, 27, 0, 0)
    # White coat and neck.
    icon.add_artist(Polygon(
        [(2, 1), (2, 8), (5, 11), (8, 12), (14, 12), (17, 11),
         (20, 8), (20, 1), (15, 0), (7, 0)],
        closed=True, facecolor="white", edgecolor="black", linewidth=1,
    ))
    icon.add_artist(Polygon(
        [(8, 12), (8, 15), (14, 15), (14, 12), (11, 10)],
        facecolor="white", edgecolor="black", linewidth=0.8,
    ))
    icon.add_artist(Ellipse((11, 19), 10, 13, facecolor="white", edgecolor="black", linewidth=1))
    # Hair swept across the forehead.
    icon.add_artist(PathPatch(MplPath(
        [(6, 19), (5, 25), (8, 27), (13, 27), (17, 25), (16, 19),
         (15, 23), (13, 23), (10, 20), (6, 19)],
        [MplPath.MOVETO] + [MplPath.CURVE3] * 8 + [MplPath.CLOSEPOLY],
    ), facecolor="black", edgecolor="black", linewidth=0.6))
    # Stethoscope, pocket, and coat seam.
    icon.add_artist(PathPatch(MplPath(
        [(7, 11), (7, 8), (4, 8), (4, 4), (7, 3), (9, 4), (9, 8), (7, 8)],
        [MplPath.MOVETO] + [MplPath.LINETO] * 7,
    ), facecolor="none", edgecolor="black", linewidth=0.8))
    icon.add_artist(PathPatch(MplPath(
        [(15, 11), (15, 6), (11, 10), (11, 1)],
        [MplPath.MOVETO, MplPath.LINETO, MplPath.MOVETO, MplPath.LINETO],
    ), facecolor="none", edgecolor="black", linewidth=0.7))
    icon.add_artist(Circle((15, 5), 1.2, facecolor="white", edgecolor="black", linewidth=0.8))
    return icon


labels = ["image-only", "multimodal", "longitudinal", "longitudinal & multimodal"]
scores = [48.7, 49.0, 50.6, 51.1]
colors = ["#003449", "#FFC347", "#FF8500", "#D62728"]
agreement = 62.2

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "svg.fonttype": "none", "axes.linewidth": 1.1,
})
fig, ax = plt.subplots(figsize=(4.9, 5.6))
fig.subplots_adjust(left=0.22, right=0.96, bottom=0.33, top=0.94)

ax.bar(range(4), scores, width=0.55, color=colors, edgecolor="black", linewidth=1.1)
ax.axhline(scores[0], color="#555555", linewidth=1.5)
ax.axhline(agreement, color="#444444", linewidth=1.5, linestyle=(0, (3, 2)))

for i in range(1, 4):
    ax.arrow(
        i, 52.3, 0, 2.2, width=0.16, head_width=0.34, head_length=1.1,
        length_includes_head=True, color=colors[i], linewidth=0,
    )
    ax.text(
        i, 55.7, f"+{scores[i] - scores[0]:.1f} pp",
        ha="center", va="bottom", color=colors[i], fontsize=13,
        fontweight="bold", fontstretch="condensed",
    )

for x in (1.56, 1.95, 2.34):
    ax.add_artist(AnnotationBbox(
        physician_icon(), (x, 63.3), frameon=False, box_alignment=(0.5, 0),
        pad=0, annotation_clip=False,
    ))
ax.text(3.44, 62.9, "62.2%", ha="right", va="bottom", fontsize=11)

# Match the reference's deliberately cropped axis and angled category labels.
ax.set_ylim(30, 72)
ax.set_xlim(-0.45, 3.45)
ax.set_yticks([30, 40, 50, 60, 70])
ax.set_ylabel("DSC (%)")
ax.set_xticks(range(4), labels, rotation=25, ha="right", rotation_mode="anchor")
ax.tick_params(axis="both", direction="out", length=6, width=1.1, pad=4)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(False)
fig.text(0.60, 0.06, "(a) segmentation results", ha="center", fontsize=12)

output = Path(__file__).resolve().parent
fig.savefig(output / "figure3a_reproduction.png", dpi=300, bbox_inches="tight")
fig.savefig(output / "figure3a_reproduction.svg", bbox_inches="tight")
plt.show()
