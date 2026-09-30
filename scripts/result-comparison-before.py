"""Plot AIME 2024 base vs. base+RL pass@k results with Matplotlib.

Requires pandas and matplotlib. Uses CSVs in sample-datasets/ by default.
Run from the repository root: python scripts/result-comparison-before.py
Optional: --data-dir /path/to/csvs --output chart.png
"""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, ScalarFormatter
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    script_dir = Path(__file__).resolve().parent
    default_data = script_dir.parent / "sample-datasets"
    parser.add_argument("--data-dir", type=Path, default=default_data)
    parser.add_argument("--output", type=Path, default=script_dir.parent / "output" / "result-comparison-before.png")
    args = parser.parse_args()

    datasets = [
        ("Qwen2.5-14B", "aime24_qwen2_5_14b.csv"),
        ("Qwen2.5-32B", "aime24_qwen2_5_32b.csv"),
    ]
    plt.rcParams.update({"font.size": 11, "axes.titlesize": 14, "axes.labelsize": 12})
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), sharey=True)

    for ax, (model, filename) in zip(axes, datasets):
        df = pd.read_csv(args.data_dir / filename).sort_values("k")
        if df["k"].duplicated().any() or (df["k"] <= 0).any():
            raise ValueError(f"{filename}: k must be positive and unique")
        rates = df[["base_pass_at_k", "rl_pass_at_k"]]
        if rates.isna().any().any() or not rates.ge(0).all().all() or not rates.le(1).all().all():
            raise ValueError(f"{filename}: pass@k values must be in [0, 1]")

        ax.plot(df["k"], df["base_pass_at_k"], label="Base", color="#2878B5",
                linewidth=2.4, marker="o", markersize=3.5)
        ax.plot(df["k"], df["rl_pass_at_k"], label="Base + RL", color="#D55E00",
                linewidth=2.4, linestyle="--", marker="s", markersize=3.5)
        # A logarithmic axis makes both low and high sampling budgets readable.
        ax.set_xscale("log", base=2)
        ax.set_xticks([1, 4, 16, 64, 256, 1024])
        ax.xaxis.set_major_formatter(ScalarFormatter())
        ax.set_xlim(1, 1024)
        ax.set_ylim(0, 1)
        ax.set_yticks([i / 10 for i in range(11)])
        ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
        ax.set_title(model, pad=12)
        ax.set_xlabel("Number of samples, k (log scale)")
        ax.grid(True, which="major", color="#D9DDE3", linewidth=0.7, alpha=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(loc="upper left", frameon=False)

    axes[0].set_ylabel("Pass@k (%)")
    fig.suptitle("AIME 2024: Base vs. Base + RL", fontsize=17, fontweight="bold", y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
