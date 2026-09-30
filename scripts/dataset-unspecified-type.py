"""Plot all 62 supplied task/dataset rows using Matplotlib.

Run: python plot_datasets.py
Requires: pip install matplotlib
Outputs a PNG and an editable vector SVG beside this script.
"""

from io import StringIO
from pathlib import Path
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator


DATA = """task\tmodality\tdataset\tapprox_count
Diagnosis\tX-Ray\tSIIM-ACR\t1300
Diagnosis\tX-Ray\tCovid-CXR2\t4800
Diagnosis\tX-Ray\tNLM-TB\t160
Diagnosis\tX-Ray\tMedFMC (Chest)\t340
Diagnosis\tX-Ray\tVinDr-PCXR\t2100
Diagnosis\tX-Ray\tVinDr-CXR\t3300
Diagnosis\tX-Ray\tRSNA\t1900
Diagnosis\tX-Ray\tVinDr-SpineXR\t2500
Diagnosis\tX-Ray\tNIH ChestX-ray14\t39000
Diagnosis\tX-Ray\tCheXpert\t49000
Diagnosis\tFundus\tRFMiD2\t150
Diagnosis\tFundus\tDRD\t90000
Diagnosis\tFundus\tFundus JSIEC\t170
Diagnosis\tFundus\tODIR\t2000
Diagnosis\tPathology\tLC25000 (Colon)\t2400
Diagnosis\tPathology\tLC25000 (Lung)\t3100
Diagnosis\tPathology\tMedFMC (Colon)\t1800
Diagnosis\tPathology\tPCam200\t30000
Diagnosis\tEndoscopy\tMedFMC (Endo)\t260
Diagnosis\tEndoscopy\tWCE\t930
Diagnosis\tEndoscopy\tHyperKvasir\t2400
Diagnosis\tEndoscopy\tKvasir\t2000
Diagnosis\tMammography\tVinDr-Mammo\t4100
Diagnosis\tMammography\tDDSM\t27000
Diagnosis\tMammography\tBreast Cancer\t250
Diagnosis\tDermatology\tHAM10000\t2000
Diagnosis\tDermatology\tPAD-UFES-20\t340
Diagnosis\tUltrasound\tBUSBRA\t280
Diagnosis\tUltrasound\tUBIBC\t930
Diagnosis\tUltrasound\tBUID\t140
Diagnosis\tUltrasound\tHMC-QU\t2500
Diagnosis\tOCT\tOCTMNIST\t1700
Diagnosis\tOCT\tRetinal OCT\t2800
Diagnosis\tMRI\tBreast Tumor MRI\t1900
Diagnosis\tMRI\tBrain Tumor MRI\t1700
Diagnosis\tCT\tBrain Tumor CT\t1300
Diagnosis\tCT\tCOVIDxCT\t46000
Retrieval\tMixture\tPMC-9k\t61000
Retrieval\tPathology\tQuilt-1M\t80000
MRG\tX-Ray\tMIMIC-CXR\t85000
MRG\tX-Ray\tIU X-Ray\t4100
VQA\tRadiology\tVQA-RAD\t5100
VQA\tRadiology\tSLAKE\t90000
WSI Analysis\tPathology\tBRACS-3\t530
WSI Analysis\tPathology\tBRACS-7\t530
WSI Analysis\tPathology\tBRCA\t90000
WSI Analysis\tPathology\tNSCLC\t80000
WSI Analysis\tPathology\tCamelyon\t31000
WSI Analysis\tPathology\tLUAD\t8900
WSI Analysis\tPathology\tLUSC\t8400
Explainable AI\tDermatology\tDerm7pt\t2400
Explainable AI\tDermatology\tSkinCon\t1800
Explainable AI\tPathology\tWBCAttr\t95000
Explainable AI\tPathology\tMedFMC (Colon)\t39000
Explainable AI\tUltrasound\tBrEaST\t100
Explainable AI\tUltrasound\tUBIBC\t15000
Explainable AI\tCT\tLUNA16\t830
Explainable AI\tCT\tNLM-TB\t780
Explainable AI\tX-Ray\tVinDr-PCXR\t37000
Explainable AI\tX-Ray\tVinDr-CXR\t12000
Explainable AI\tX-Ray\tRSNA\t37000
Explainable AI\tMammography\tCBIS-DDSM\t1700
"""

COLORS = {
    "X-Ray": "#2878B5", "Fundus": "#D49A00", "Pathology": "#8C60B0",
    "Endoscopy": "#339B80", "Mammography": "#D26887", "Dermatology": "#BD6942",
    "Ultrasound": "#16A6B3", "OCT": "#839E37", "MRI": "#465990",
    "CT": "#C34242", "Mixture": "#797979", "Radiology": "#664B33",
}


def plot_panel(ax, task, rows, letter):
    """Use the same log scale in every panel; preserve the supplied row order."""
    for i, row in enumerate(rows):
        count = row["approx_count"]
        color = COLORS[row["modality"]]
        if i % 2 == 0:
            ax.axhspan(i - 0.5, i + 0.5, color="#F5F7F9", zorder=0)
        ax.scatter(count, i, s=58, color=color, edgecolor="white", linewidth=0.7, zorder=3)
        ax.annotate(f"{count:,}", (count, i), xytext=(7, 0), textcoords="offset points",
                    va="center", fontsize=10, color="#344054")
    ax.set_xscale("log")
    ax.set_xlim(70, 260000)
    ax.set_ylim(len(rows) - 0.45, -0.55)
    ax.set_yticks(range(len(rows)), [row["dataset"] for row in rows])
    ax.xaxis.set_major_locator(FixedLocator([100, 1000, 10000, 100000]))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.grid(axis="x", color="#D9E0E7", linewidth=0.7, zorder=1)
    ax.tick_params(axis="both", length=0, labelsize=10, pad=7)
    ax.set_xlabel("Approximate count (log scale)", fontsize=10, color="#56616F", labelpad=8)
    ax.set_title(f"{letter}  {task}", loc="left", fontsize=14, fontweight="bold", pad=13)
    for spine in ax.spines.values():
        spine.set_visible(False)


def main():
    rows = list(csv.DictReader(StringIO(DATA), delimiter="\t"))
    for row in rows:
        row["approx_count"] = int(row["approx_count"])
    assert len(rows) == 62
    assert len({(r["task"], r["modality"], r["dataset"]) for r in rows}) == 62
    tasks = list(dict.fromkeys(r["task"] for r in rows))
    grouped = {task: [r for r in rows if r["task"] == task] for task in tasks}

    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none",
                         "text.color": "#182432", "axes.labelcolor": "#182432",
                         "xtick.color": "#56616F", "ytick.color": "#182432"})
    fig = plt.figure(figsize=(19, 17), facecolor="white")
    outer = fig.add_gridspec(1, 2, left=0.16, right=0.96, bottom=0.09, top=0.83,
                            wspace=0.49)
    plot_panel(fig.add_subplot(outer[0]), tasks[0], grouped[tasks[0]], "A")
    right = outer[1].subgridspec(5, 1, height_ratios=[2.3, 2.3, 2.3, 7, 12], hspace=0.58)
    for index, task in enumerate(tasks[1:]):
        plot_panel(fig.add_subplot(right[index]), task, grouped[task], chr(ord("B") + index))

    fig.text(0.035, 0.968, "Medical datasets by task and modality", fontsize=25,
             fontweight="bold", va="top")
    fig.text(0.035, 0.935, "62 dataset–task entries · values reproduced from the supplied table",
             fontsize=13, color="#56616F", va="top")
    handles = [Line2D([0], [0], marker="o", color="none", markerfacecolor=color,
                      markeredgecolor="none", markersize=8, label=modality)
               for modality, color in COLORS.items()]
    fig.legend(handles=handles, title="Modality", loc="upper left", bbox_to_anchor=(0.029, 0.915),
               ncol=6, frameon=False, fontsize=11, title_fontsize=11,
               columnspacing=2.1, handletextpad=0.35, labelspacing=0.65)
    fig.text(0.035, 0.033,
             "Equal horizontal distances represent equal ratios (×10 between labeled ticks). "
             "Labels show the supplied approximate counts.\n"
             "Repeated dataset names remain separate entries under their respective tasks; "
             "counts are not summed across tasks.",
             fontsize=11, color="#56616F", linespacing=1.6)
    output_dir = Path(__file__).resolve().parent
    for extension in ("png", "svg"):
        output_path = output_dir / f"medical_datasets.{extension}"
        fig.savefig(output_path, dpi=220, facecolor="white")
        print(output_path)
    plt.close(fig)
    print(f"Verified {len(rows)} rows; task sizes: " +
          ", ".join(f"{task}: {len(items)}" for task, items in grouped.items()))


if __name__ == "__main__":
    main()
