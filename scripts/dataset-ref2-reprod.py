"""Reproduce the supplied circular figure with Matplotlib.

Data are approximate image-digitized values, NOT verified source data.
Run: python reproduce_figure.py
Or:  python reproduce_figure.py --style horizontal
Dependencies: numpy, matplotlib. Data export uses only the standard library.
"""
from pathlib import Path
import argparse
import csv
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import numpy as np


# Angles run clockwise from the top. Radius is measured in source-image pixels.
# Approximate decade-tick calibration: r(10^5) = 310, 41.8 pixels per decade.
# The frame extends beyond the ticks; it is not itself the 10^5 tick.
TICK_R5 = 310.0
PIXELS_PER_DECADE = 41.8
BAR_BASE = 142.0
FRAME_INNER, FRAME_OUTER = 135.0, 318.0
TASK_INNER, TASK_OUTER, CATEGORY_OUTER = 333.0, 442.0, 612.0

# Each tuple is (task, modality, dataset, center_angle_deg, observed_tip_radius).
# Keep the observed radii so the approximation can be recalibrated transparently.
OBSERVATIONS = [
    ("Diagnosis", "X-Ray", "SIIM-ACR", 4.15, 231),
    ("Diagnosis", "X-Ray", "Covid-CXR2", 8.60, 255),
    ("Diagnosis", "X-Ray", "NLM-TB", 13.10, 193),
    ("Diagnosis", "X-Ray", "MedFMC (Chest)", 17.65, 207),
    ("Diagnosis", "X-Ray", "VinDr-PCXR", 22.15, 240),
    ("Diagnosis", "X-Ray", "VinDr-CXR", 26.65, 248),
    ("Diagnosis", "X-Ray", "RSNA", 31.15, 238),
    ("Diagnosis", "X-Ray", "VinDr-SpineXR", 35.65, 243),
    ("Diagnosis", "X-Ray", "NIH ChestX-ray14", 40.20, 293),
    ("Diagnosis", "X-Ray", "CheXpert", 44.65, 297),
    ("Diagnosis", "Fundus", "RFMiD2", 49.15, 192),
    ("Diagnosis", "Fundus", "DRD", 53.70, 308),
    ("Diagnosis", "Fundus", "Fundus JSIEC", 58.20, 194),
    ("Diagnosis", "Fundus", "ODIR", 62.75, 239),
    ("Diagnosis", "Pathology", "LC25000 (Colon)", 67.30, 242),
    ("Diagnosis", "Pathology", "LC25000 (Lung)", 71.80, 247),
    ("Diagnosis", "Pathology", "MedFMC (Colon)", 76.35, 237),
    ("Diagnosis", "Pathology", "PCam200", 80.90, 288),
    ("Diagnosis", "Endoscopy", "MedFMC (Endo)", 85.45, 202),
    ("Diagnosis", "Endoscopy", "WCE", 90.00, 225),
    ("Diagnosis", "Endoscopy", "HyperKvasir", 94.55, 242),
    ("Diagnosis", "Endoscopy", "Kvasir", 99.05, 239),
    ("Diagnosis", "Mammography", "VinDr-Mammo", 103.55, 252),
    ("Diagnosis", "Mammography", "DDSM", 108.15, 286),
    ("Diagnosis", "Mammography", "Breast Cancer", 112.70, 201),
    ("Diagnosis", "Dermatology", "HAM10000", 117.25, 239),
    ("Diagnosis", "Dermatology", "PAD-UFES-20", 121.80, 207),
    ("Diagnosis", "Ultrasound", "BUSBRA", 126.40, 203),
    ("Diagnosis", "Ultrasound", "UBIBC", 130.95, 225),
    ("Diagnosis", "Ultrasound", "BUID", 135.45, 191),
    ("Diagnosis", "Ultrasound", "HMC-QU", 140.05, 243),
    ("Diagnosis", "OCT", "OCTMNIST", 144.55, 236),
    ("Diagnosis", "OCT", "Retinal OCT", 149.15, 245),
    ("Diagnosis", "MRI", "Breast Tumor MRI", 153.70, 238),
    ("Diagnosis", "MRI", "Brain Tumor MRI", 158.25, 236),
    ("Diagnosis", "CT", "Brain Tumor CT", 162.80, 231),
    ("Diagnosis", "CT", "COVIDxCT", 167.40, 296),
    ("Retrieval", "Mixture", "PMC-9k", 185.30, 301),
    ("Retrieval", "Pathology", "Quilt-1M", 189.80, 306),
    ("MRG", "X-Ray", "MIMIC-CXR", 207.75, 307),
    ("MRG", "X-Ray", "IU X-Ray", 212.30, 252),
    ("VQA", "Radiology", "VQA-RAD", 230.10, 256),
    ("VQA", "Radiology", "SLAKE", 234.70, 308),
    ("WSI Analysis", "Pathology", "BRACS-3", 252.50, 215),
    ("WSI Analysis", "Pathology", "BRACS-7", 257.00, 215),
    ("WSI Analysis", "Pathology", "BRCA", 261.45, 308),
    ("WSI Analysis", "Pathology", "NSCLC", 265.95, 306),
    ("WSI Analysis", "Pathology", "Camelyon", 270.35, 289),
    ("WSI Analysis", "Pathology", "LUAD", 274.95, 266),
    ("WSI Analysis", "Pathology", "LUSC", 279.45, 265),
    ("Explainable AI", "Dermatology", "Derm7pt", 297.15, 242),
    ("Explainable AI", "Dermatology", "SkinCon", 301.65, 237),
    ("Explainable AI", "Pathology", "WBCAttr", 306.15, 309),
    ("Explainable AI", "Pathology", "MedFMC (Colon)", 310.65, 293),
    ("Explainable AI", "Ultrasound", "BrEaST", 315.15, 185),
    ("Explainable AI", "Ultrasound", "UBIBC", 319.55, 276),
    ("Explainable AI", "CT", "LUNA16", 324.05, 223),
    ("Explainable AI", "CT", "NLM-TB", 328.60, 222),
    ("Explainable AI", "X-Ray", "VinDr-PCXR", 333.05, 292),
    ("Explainable AI", "X-Ray", "VinDr-CXR", 337.50, 271),
    ("Explainable AI", "X-Ray", "RSNA", 342.00, 292),
    ("Explainable AI", "Mammography", "CBIS-DDSM", 346.45, 236),
]

TASKS = {
    "Diagnosis": (0.0, 171.5, "#4c897f"),
    "Retrieval": (180.1, 194.2, "#cad589"),
    "MRG": (202.4, 216.5, "#fac092"),
    "VQA": (224.5, 238.6, "#de6a82"),
    "WSI Analysis": (246.5, 285.0, "#af848e"),
    "Explainable AI": (291.6, 350.7, "#c89259"),
}


def two_significant_figures(value):
    return int(round(value, 1 - int(math.floor(math.log10(value)))))


DATA = [dict(task=t, modality=m, dataset=d, angle=a, tip_radius=r,
             approx_count=two_significant_figures(10 ** (5 + (r - TICK_R5) / PIXELS_PER_DECADE)))
        for t, m, d, a, r in OBSERVATIONS]


def radial_position(value):
    """Map count to radius explicitly; do not apply log to a bar's height."""
    return TICK_R5 + PIXELS_PER_DECADE * (np.log10(value) - 5)


def xy(angle, radius):
    theta = np.deg2rad(angle)
    return radius * np.sin(theta), radius * np.cos(theta)


def blend_white(color, white_fraction):
    from matplotlib.colors import to_rgb
    c = np.array(to_rgb(color))
    return tuple(c * (1 - white_fraction) + white_fraction)


def annulus(ax, start, end, inner, outer, **kwargs):
    # Wedge angles are counterclockwise from the right; ours are clockwise from top.
    ax.add_patch(Wedge((0, 0), outer, 90 - end, 90 - start,
                       width=outer - inner, **kwargs))


def radial_text(ax, text, angle, radius, **kwargs):
    rotation = 90 - angle
    if 180 < angle < 360:
        rotation += 180
    ax.text(*xy(angle, radius), text, rotation=rotation,
            rotation_mode="anchor", va="center", **kwargs)


def plot_circular(data, output):
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})
    fig, ax = plt.subplots(figsize=(17, 17), facecolor="white")
    ax.set(aspect="equal", xlim=(-870, 870), ylim=(-870, 870))
    ax.axis("off")
    for task, (start, end, color) in TASKS.items():
        rows = [row for row in data if row["task"] == task]
        annulus(ax, start, end, FRAME_INNER, FRAME_OUTER,
                facecolor="none", edgecolor="#555555", linewidth=.65)
        for row in rows:
            tip = radial_position(row["approx_count"])
            annulus(ax, row["angle"] - 1.6, row["angle"] + 1.6,
                    BAR_BASE, tip, facecolor=color, edgecolor="none")
        annulus(ax, start, end, TASK_INNER, TASK_OUTER,
                facecolor=color, edgecolor="none")
        mid = (start + end) / 2
        rotation = -mid + (180 if 90 < mid < 270 else 0)
        ax.text(*xy(mid, (TASK_INNER + TASK_OUTER) / 2), task,
                rotation=rotation, rotation_mode="anchor", ha="center", va="center",
                color="white", weight="bold", fontsize=11 if task == "Retrieval" else 16)

        # Each modality's span is determined by boundaries halfway between bars.
        groups = []
        for row in rows:
            if not groups or groups[-1][0] != row["modality"]:
                groups.append((row["modality"], [row]))
            else:
                groups[-1][1].append(row)
        for i, (modality, items) in enumerate(groups):
            left = start if i == 0 else (groups[i - 1][1][-1]["angle"] + items[0]["angle"]) / 2
            right = end if i == len(groups) - 1 else (items[-1]["angle"] + groups[i + 1][1][0]["angle"]) / 2
            fade = .79 - .11 * i if task == "Diagnosis" else .72 - .10 * i
            annulus(ax, left, right, TASK_OUTER, CATEGORY_OUTER,
                    facecolor=blend_white(color, max(.15, fade)), edgecolor="none")
            radial_text(ax, modality, (left + right) / 2,
                        (TASK_OUTER + CATEGORY_OUTER) / 2, ha="center", weight="bold",
                        fontsize=10 if len(items) == 1 else 14)

        for row in rows:
            radial_text(ax, row["dataset"], row["angle"], CATEGORY_OUTER + 7,
                        ha="right" if 180 < row["angle"] < 360 else "left", fontsize=13)

        # Repeat the decade labels beside each independent task sector.
        for exponent in range(2, 6):
            radius = radial_position(10 ** exponent)
            x1, y1 = xy(end, radius)
            x2, y2 = xy(end + 1.2, radius)
            ax.plot([x1, x2], [y1, y2], color="#555555", linewidth=.6)
            radial_text(ax, rf"$10^{exponent}$", end + 2.2, radius,
                        ha="center", fontsize=7.5)
    fig.subplots_adjust(left=.01, right=.99, bottom=.01, top=.99)
    fig.savefig(output.with_suffix(".png"), dpi=180, facecolor="white")
    fig.savefig(output.with_suffix(".svg"), facecolor="white")
    plt.close(fig)


def plot_horizontal(data, output):
    """Alternative for comparing magnitudes without rotated dataset labels."""
    fig, axes = plt.subplots(2, 3, figsize=(19, 17), layout="constrained")
    for ax, (task, (_, _, color)) in zip(axes.flat, TASKS.items()):
        rows = [row for row in data if row["task"] == task]
        ax.barh(np.arange(len(rows)), [row["approx_count"] for row in rows], color=color)
        ax.set_yticks(np.arange(len(rows)), [row["dataset"] for row in rows], fontsize=8)
        ax.invert_yaxis()
        ax.set_xscale("log")
        ax.set_xlim(10, 120000)
        ax.set_title(task, weight="bold")
        ax.set_xlabel("Approximate plotted count (log scale)")
        ax.grid(axis="x", alpha=.2)
        ax.set_axisbelow(True)
    fig.savefig(output.with_suffix(".png"), dpi=180)
    fig.savefig(output.with_suffix(".svg"))
    plt.close(fig)


def export_data(directory):
    fields = ["task", "modality", "dataset", "approx_count", "angle", "tip_radius"]
    with (directory / "approximate_data.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(DATA)
    introduction = """# Approximate values digitized from the supplied figure

These are visual estimates, rounded to two significant figures, rather than
verified original data. A practical reading uncertainty is about 10–15%, which
is an estimate and not a statistical confidence interval. The figure does not
label the unit or define which dataset split/sample is being counted. Dataset
names (e.g. Quilt-1M) are not substituted for the heights of their plotted bars.
Repeated datasets retain separate values for each task.

The source is a clockwise circular bar chart with a logarithmic radial mapping.
Approximate source-image center: (785, 837) pixels. Measured bar tips are stored
in the CSV and Python file. Calibration: r = 310 + 41.8*(log10(N)-5).
The bar baseline is r=142 and the frame is r=135…318; neither frame radius is
a decade-tick position. Pixel rounding, antialiasing and tick calibration limit
the numerical precision. Group names are transcribed as displayed.

## Run and edit

```bash
pip install numpy matplotlib
python reproduce_figure.py --outdir results
python reproduce_figure.py --style horizontal --outdir results
```

Edit `DATA` or `OBSERVATIONS` in the Python file to test other values. Both plot
functions accept a list of dictionaries with task, modality, dataset, angle,
and approx_count fields. The circular plot maps the *value* to radius explicitly
and preserves the blank center; a standard polar log axis can distort this.

## Values

| Task | Modality | Dataset | Approximate plotted count |
| --- | --- | --- | ---: |
"""
    table = "\n".join(f"| {r['task']} | {r['modality']} | {r['dataset']} | {r['approx_count']:,} |" for r in DATA)
    (directory / "approximate_data.md").write_text(introduction + table + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--style", choices=["circular", "horizontal"], default="circular")
    parser.add_argument("--outdir", type=Path, default=Path("."))
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    export_data(args.outdir)
    if args.style == "circular":
        plot_circular(DATA, args.outdir / "reproduced_figure")
    else:
        plot_horizontal(DATA, args.outdir / "horizontal_comparison")
    print(f"Exported {len(DATA)} approximate values and the {args.style} plot to {args.outdir.resolve()}")
