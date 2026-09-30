"""Plot the supplied approximate counts. Requires matplotlib.

Run: python plot_dataset_pie.py
Or:  python plot_dataset_pie.py --group-by modality --output modality_pie.png
Counts are summed as supplied; repeated datasets are not deduplicated.
"""

import argparse
import csv
from collections import defaultdict
from io import StringIO
from pathlib import Path

import matplotlib.pyplot as plt


DATA = """Task|Modality|Dataset|Count
Diagnosis|X-Ray|SIIM-ACR|1300
Diagnosis|X-Ray|Covid-CXR2|4800
Diagnosis|X-Ray|NLM-TB|160
Diagnosis|X-Ray|MedFMC (Chest)|340
Diagnosis|X-Ray|VinDr-PCXR|2100
Diagnosis|X-Ray|VinDr-CXR|3300
Diagnosis|X-Ray|RSNA|1900
Diagnosis|X-Ray|VinDr-SpineXR|2500
Diagnosis|X-Ray|NIH ChestX-ray14|39000
Diagnosis|X-Ray|CheXpert|49000
Diagnosis|Fundus|RFMiD2|150
Diagnosis|Fundus|DRD|90000
Diagnosis|Fundus|Fundus JSIEC|170
Diagnosis|Fundus|ODIR|2000
Diagnosis|Pathology|LC25000 (Colon)|2400
Diagnosis|Pathology|LC25000 (Lung)|3100
Diagnosis|Pathology|MedFMC (Colon)|1800
Diagnosis|Pathology|PCam200|30000
Diagnosis|Endoscopy|MedFMC (Endo)|260
Diagnosis|Endoscopy|WCE|930
Diagnosis|Endoscopy|HyperKvasir|2400
Diagnosis|Endoscopy|Kvasir|2000
Diagnosis|Mammography|VinDr-Mammo|4100
Diagnosis|Mammography|DDSM|27000
Diagnosis|Mammography|Breast Cancer|250
Diagnosis|Dermatology|HAM10000|2000
Diagnosis|Dermatology|PAD-UFES-20|340
Diagnosis|Ultrasound|BUSBRA|280
Diagnosis|Ultrasound|UBIBC|930
Diagnosis|Ultrasound|BUID|140
Diagnosis|Ultrasound|HMC-QU|2500
Diagnosis|OCT|OCTMNIST|1700
Diagnosis|OCT|Retinal OCT|2800
Diagnosis|MRI|Breast Tumor MRI|1900
Diagnosis|MRI|Brain Tumor MRI|1700
Diagnosis|CT|Brain Tumor CT|1300
Diagnosis|CT|COVIDxCT|46000
Retrieval|Mixture|PMC-9k|61000
Retrieval|Pathology|Quilt-1M|80000
MRG|X-Ray|MIMIC-CXR|85000
MRG|X-Ray|IU X-Ray|4100
VQA|Radiology|VQA-RAD|5100
VQA|Radiology|SLAKE|90000
WSI Analysis|Pathology|BRACS-3|530
WSI Analysis|Pathology|BRACS-7|530
WSI Analysis|Pathology|BRCA|90000
WSI Analysis|Pathology|NSCLC|80000
WSI Analysis|Pathology|Camelyon|31000
WSI Analysis|Pathology|LUAD|8900
WSI Analysis|Pathology|LUSC|8400
Explainable AI|Dermatology|Derm7pt|2400
Explainable AI|Dermatology|SkinCon|1800
Explainable AI|Pathology|WBCAttr|95000
Explainable AI|Pathology|MedFMC (Colon)|39000
Explainable AI|Ultrasound|BrEaST|100
Explainable AI|Ultrasound|UBIBC|15000
Explainable AI|CT|LUNA16|830
Explainable AI|CT|NLM-TB|780
Explainable AI|X-Ray|VinDr-PCXR|37000
Explainable AI|X-Ray|VinDr-CXR|12000
Explainable AI|X-Ray|RSNA|37000
Explainable AI|Mammography|CBIS-DDSM|1700
"""


def aggregate(group_by="task"):
    totals = defaultdict(int)
    for row in csv.DictReader(StringIO(DATA), delimiter="|"):
        totals[row[group_by.capitalize()]] += int(row["Count"])
    return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))


def plot_pie(group_by="task", output="dataset_pie.png", show=False):
    totals = aggregate(group_by)
    labels, counts = list(totals), list(totals.values())
    total = sum(counts)
    palette = ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377",
               "#BBBBBB", "#332288", "#44AA99", "#999933", "#882255", "#661100", "#6699CC"]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12})
    fig, ax = plt.subplots(figsize=(11, 6.6), facecolor="white")
    fig.subplots_adjust(left=0.03, right=0.63, top=0.80, bottom=0.13)
    wedges, _, percentages = ax.pie(
        counts,
        colors=palette[:len(counts)],
        startangle=90,
        counterclock=False,
        autopct=lambda pct: f"{pct:.1f}%" if pct >= 2 else "",
        pctdistance=0.73,
        wedgeprops={"linewidth": 2, "edgecolor": "white"},
        textprops={"fontsize": 12, "fontweight": "bold"},
    )
    ax.set_aspect("equal")
    legend_labels = [f"{label}   {count:,} ({count / total:.1%})"
                     for label, count in totals.items()]
    ax.legend(wedges, legend_labels, title=group_by.capitalize(),
              loc="center left", bbox_to_anchor=(1.02, 0.5),
              frameon=False, labelspacing=1.3, fontsize=11)
    fig.text(0.065, 0.92, f"Approximate counts by {group_by}",
             fontsize=22, fontweight="bold", color="#202C3A")
    fig.text(0.065, 0.855, f"Share of the supplied total: {total:,}",
             fontsize=13, color="#556270")
    fig.text(0.065, 0.055,
             "Source: supplied table. Counts are approximate; repeated datasets are included as listed.",
             fontsize=10, color="#556270")
    destination = Path(output)
    fig.savefig(destination, dpi=300, facecolor="white")
    if show:
        plt.show()
    plt.close(fig)
    print(f"Saved {destination.resolve()}")
    print(f"Total: {total:,}")
    for label, count in totals.items():
        print(f"{label}: {count:,} ({count / total:.1%})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group-by", choices=["task", "modality"], default="task")
    parser.add_argument("--output", default="dataset_pie.png")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()
    plot_pie(args.group_by, args.output, args.show)
