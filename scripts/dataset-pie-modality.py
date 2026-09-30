"""Plot the supplied approximate counts with Python and Matplotlib.

Run: python plot_dataset_pie.py
Or:  python plot_dataset_pie.py --group Task --output task_pie.png
Requires: pip install matplotlib
Each table row contributes its count; repeated datasets are not deduplicated.
"""

import argparse
import csv
import io
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


DATA = """Modality,Task,Dataset,Count
X-Ray,Diagnosis,SIIM-ACR,1300
X-Ray,Diagnosis,Covid-CXR2,4800
X-Ray,Diagnosis,NLM-TB,160
X-Ray,Diagnosis,MedFMC (Chest),340
X-Ray,Diagnosis,VinDr-PCXR,2100
X-Ray,Diagnosis,VinDr-CXR,3300
X-Ray,Diagnosis,RSNA,1900
X-Ray,Diagnosis,VinDr-SpineXR,2500
X-Ray,Diagnosis,NIH ChestX-ray14,39000
X-Ray,Diagnosis,CheXpert,49000
Fundus,Diagnosis,RFMiD2,150
Fundus,Diagnosis,DRD,90000
Fundus,Diagnosis,Fundus JSIEC,170
Fundus,Diagnosis,ODIR,2000
Pathology,Diagnosis,LC25000 (Colon),2400
Pathology,Diagnosis,LC25000 (Lung),3100
Pathology,Diagnosis,MedFMC (Colon),1800
Pathology,Diagnosis,PCam200,30000
Endoscopy,Diagnosis,MedFMC (Endo),260
Endoscopy,Diagnosis,WCE,930
Endoscopy,Diagnosis,HyperKvasir,2400
Endoscopy,Diagnosis,Kvasir,2000
Mammography,Diagnosis,VinDr-Mammo,4100
Mammography,Diagnosis,DDSM,27000
Mammography,Diagnosis,Breast Cancer,250
Dermatology,Diagnosis,HAM10000,2000
Dermatology,Diagnosis,PAD-UFES-20,340
Ultrasound,Diagnosis,BUSBRA,280
Ultrasound,Diagnosis,UBIBC,930
Ultrasound,Diagnosis,BUID,140
Ultrasound,Diagnosis,HMC-QU,2500
OCT,Diagnosis,OCTMNIST,1700
OCT,Diagnosis,Retinal OCT,2800
MRI,Diagnosis,Breast Tumor MRI,1900
MRI,Diagnosis,Brain Tumor MRI,1700
CT,Diagnosis,Brain Tumor CT,1300
CT,Diagnosis,COVIDxCT,46000
Mixture,Retrieval,PMC-9k,61000
Pathology,Retrieval,Quilt-1M,80000
X-Ray,MRG,MIMIC-CXR,85000
X-Ray,MRG,IU X-Ray,4100
Radiology,VQA,VQA-RAD,5100
Radiology,VQA,SLAKE,90000
Pathology,WSI Analysis,BRACS-3,530
Pathology,WSI Analysis,BRACS-7,530
Pathology,WSI Analysis,BRCA,90000
Pathology,WSI Analysis,NSCLC,80000
Pathology,WSI Analysis,Camelyon,31000
Pathology,WSI Analysis,LUAD,8900
Pathology,WSI Analysis,LUSC,8400
Dermatology,Explainable AI,Derm7pt,2400
Dermatology,Explainable AI,SkinCon,1800
Pathology,Explainable AI,WBCAttr,95000
Pathology,Explainable AI,MedFMC (Colon),39000
Ultrasound,Explainable AI,BrEaST,100
Ultrasound,Explainable AI,UBIBC,15000
CT,Explainable AI,LUNA16,830
CT,Explainable AI,NLM-TB,780
X-Ray,Explainable AI,VinDr-PCXR,37000
X-Ray,Explainable AI,VinDr-CXR,12000
X-Ray,Explainable AI,RSNA,37000
Mammography,Explainable AI,CBIS-DDSM,1700
"""


def plot_pie(group="Modality", output="modality_pie.png", show=False):
    totals = Counter()
    for row in csv.DictReader(io.StringIO(DATA)):
        totals[row[group]] += int(row["Count"])

    labels, counts = zip(*totals.most_common())
    total = sum(counts)
    colors = plt.get_cmap("tab20").colors[:len(labels)]

    fig, ax = plt.subplots(figsize=(12, 7.5), facecolor="white")
    fig.subplots_adjust(left=0.04, right=0.63, top=0.83, bottom=0.13)
    wedges, _, _ = ax.pie(
        counts,
        colors=colors,
        startangle=90,
        counterclock=False,
        autopct=lambda pct: f"{pct:.1f}%" if pct >= 3 else "",
        pctdistance=0.72,
        wedgeprops={"edgecolor": "white", "linewidth": 1.2},
        textprops={"fontsize": 12, "fontweight": "bold"},
    )
    ax.set_aspect("equal")
    legend_labels = [
        f"{label}: {count:,} ({100 * count / total:.1f}%)"
        for label, count in zip(labels, counts)
    ]
    ax.legend(
        wedges, legend_labels, title=group,
        loc="center left", bbox_to_anchor=(1.0, 0.5),
        frameon=False, fontsize=11, title_fontsize=12,
        labelspacing=1.0,
    )
    fig.suptitle(
        f"Approximate counts by {group.lower()}",
        x=0.08, ha="left", fontsize=21, fontweight="bold",
    )
    fig.text(
        0.08, 0.87, f"All table rows combined | Total: {total:,}",
        fontsize=12, color="#555555",
    )
    fig.text(
        0.08, 0.06,
        "Counts are approximate. Repeated datasets across tasks are counted separately.",
        fontsize=10, color="#555555",
    )
    output = Path(output)
    fig.savefig(output, dpi=300, facecolor="white", bbox_inches="tight")
    print(f"Saved {output.resolve()} (total = {total:,})")
    for label, count in zip(labels, counts):
        print(f"{label}: {count:,}")
    if show:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=["Modality", "Task"], default="Modality")
    parser.add_argument("--output", default="modality_pie.png")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()
    plot_pie(args.group, args.output, args.show)
