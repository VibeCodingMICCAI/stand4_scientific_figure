"""Two-ring Matplotlib composition chart inspired by the supplied reference.

Run: python create_composition.py --input approximate_data.csv --outdir .
Input columns: task, modality, dataset, approx_count.
Angles use raw counts, not logarithms. Repeated datasets across tasks are kept
separate: the total is an accounting total, not a deduplicated image count.
"""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Rectangle
from matplotlib.colors import to_rgb
import numpy as np

COLORS = {
    "Pathology": "#8BD6EA", "X-Ray": "#CFD6D4",
    "Radiology": "#B7A5CE", "Fundus": "#F8DEA0",
    "Mixture": "#BA9392", "CT": "#83B487",
    "Mammography": "#EDB786", "Ultrasound": "#ED9C9F",
    "Dermatology": "#DAB4C6", "Endoscopy": "#8BC6B5",
    "OCT": "#FFC47E", "MRI": "#ADBADC",
}
SHORT_TASK = {"Diagnosis": "Diag.", "WSI Analysis": "WSI",
              "Explainable AI": "XAI", "Retrieval": "Retrieval",
              "MRG": "MRG", "VQA": "VQA"}


def position(angle, radius):
    a = np.deg2rad(angle)
    return radius * np.cos(a), radius * np.sin(a)


def radial_label(ax, text, angle, radius, fontsize, weight="normal"):
    rotation = (angle + 180) % 360 - 180
    if rotation > 90:
        rotation -= 180
    elif rotation < -90:
        rotation += 180
    ax.text(*position(angle, radius), text, ha="center", va="center",
            rotation=rotation, rotation_mode="anchor", fontsize=fontsize,
            color="#30373D", weight=weight, linespacing=1.15)


def load_data(path):
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["approx_count"] = int(row["approx_count"])
        if row["approx_count"] <= 0:
            raise ValueError("All counts must be positive.")
    if not rows:
        raise ValueError("The input file is empty.")
    return rows


def create_chart(rows, outdir, label_min_angle=7.5):
    groups = defaultdict(list)
    for row in rows:
        groups[row["modality"]].append(row)
    ordered = sorted(groups, key=lambda m: -sum(r["approx_count"] for r in groups[m]))
    total = sum(row["approx_count"] for row in rows)
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})
    fig = plt.figure(figsize=(16, 11.5), facecolor="white")
    ax = fig.add_axes([.018, .12, .735, .80])
    ax.set(aspect="equal", xlim=(-1.10, 1.10), ylim=(-1.10, 1.10))
    ax.axis("off")
    fig.text(.05, .960, "Approximate dataset composition", fontsize=22,
             weight="bold", color="#273139")
    fig.text(.05, .925, "Inner ring: modality  •  Outer ring: dataset × task  •  Slice angles proportional to counts",
             fontsize=11, color="#606A73")

    theta = 90.0
    summary = []
    annotated = 0
    for i, modality in enumerate(ordered):
        items = sorted(groups[modality], key=lambda r: -r["approx_count"])
        count = sum(row["approx_count"] for row in items)
        width = 360 * count / total
        end = theta - width
        color = COLORS.get(modality, plt.get_cmap("tab20")(i % 20))
        summary.append(dict(modality=modality, approx_count=count,
                            percent=round(100 * count / total, 4), entries=len(items)))
        ax.add_patch(Wedge((0, 0), .70, end, theta, width=.34,
                           facecolor=color, edgecolor="#485158", linewidth=1.0))
        if width >= 9:
            radial_label(ax, f"{modality}\n{100 * count / total:.1f}%",
                         (theta + end) / 2, .535, fontsize=11.5)

        leaf_angle = theta
        for j, row in enumerate(items):
            span = 360 * row["approx_count"] / total
            leaf_end = leaf_angle - span
            # Mild shade variations preserve the common modality color.
            white_fraction = .035 * (j % 4)
            shade = np.array(to_rgb(color)) * (1 - white_fraction) + white_fraction
            ax.add_patch(Wedge((0, 0), 1.055, leaf_end, leaf_angle, width=.355,
                               facecolor=shade, edgecolor="#485158", linewidth=.65))
            if span >= label_min_angle:
                text = f"{row['dataset']}\n{SHORT_TASK.get(row['task'], row['task'])} · {row['approx_count']:,}"
                radial_label(ax, text, (leaf_angle + leaf_end) / 2, .88,
                             fontsize=9.2 if span >= 12 else 8.3)
                annotated += 1
            leaf_angle = leaf_end
        if abs(leaf_angle - end) > 1e-9:
            raise RuntimeError("Dataset wedges do not match their parent modality.")
        theta = end
    if abs(theta + 270) > 1e-9:
        raise RuntimeError("The composition does not fill a complete circle.")

    ax.text(0, .075, f"≈ {total / 1e6:.2f}M", fontsize=28, weight="bold",
            ha="center", va="center", color="#273139")
    ax.text(0, -.020, "summed task-specific counts", fontsize=10.5,
            ha="center", color="#606A73")
    ax.text(0, -.102, f"{len(rows)} entries · {len(groups)} modalities", fontsize=10,
            ha="center", color="#606A73")

    legend = fig.add_axes([.768, .205, .217, .61])
    legend.axis("off")
    legend.text(0, 1.06, "MODALITY", fontsize=11, weight="bold", color="#273139")
    legend.text(.98, 1.06, "SHARE", fontsize=11, weight="bold", color="#273139", ha="right")
    for i, s in enumerate(summary):
        y = 1 - i * .077
        legend.add_patch(Rectangle((0, y - .023), .06, .027,
                                  facecolor=COLORS.get(s["modality"], "#BBBBBB"),
                                  edgecolor="#485158", linewidth=.7))
        legend.text(.095, y, s["modality"], fontsize=11, va="center", color="#30373D")
        legend.text(.98, y, f"{s['percent']:.2f}%", fontsize=11, va="center",
                    ha="right", color="#30373D")
        legend.text(.095, y - .031, f"{s['approx_count']:,} summed counts",
                    fontsize=8.7, color="#727C84", va="center")
    fig.text(.05, .064,
             "Estimated from the earlier figure; repeated datasets across tasks may overlap. Total is not a unique-image count.",
             fontsize=10, color="#606A73")
    fig.text(.05, .037,
             "Diag. = Diagnosis; XAI = Explainable AI. Small slices are retained; all 62 entries are listed in the CSV.",
             fontsize=9.5, color="#606A73")
    outdir.mkdir(parents=True, exist_ok=True)
    fig.savefig(outdir / "dataset_composition.png", dpi=220, facecolor="white")
    fig.savefig(outdir / "dataset_composition.svg", facecolor="white")
    plt.close(fig)
    with (outdir / "modality_summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["modality", "approx_count", "percent", "entries"])
        writer.writeheader()
        writer.writerows(summary)
    print(f"Total: {total:,}; {len(rows)} outer slices; {len(groups)} modalities; {annotated} dataset labels.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).resolve().parents[1] / "sample-datasets" / "foundation_model_dataset.csv")
    parser.add_argument("--outdir", type=Path, default=Path(__file__).parent)
    parser.add_argument("--label-min-angle", type=float, default=7.5,
                        help="Minimum slice width in degrees for an internal dataset label.")
    args = parser.parse_args()
    create_chart(load_data(args.input), args.outdir, args.label_min_angle)
