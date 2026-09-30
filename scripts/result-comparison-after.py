"""Plot AIME 2024 base vs. base+RL pass@k results with Matplotlib.

Requires pandas and matplotlib. Uses CSVs in sample-datasets/ by default.
Run from the repository root: python scripts/result-comparison-after.py
Optional: --data-dir /path/to/csvs --output chart.png
"""

import argparse
import math
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
    parser.add_argument("--output", type=Path, default=script_dir.parent / "output" / "result-comparison-after.png")
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
        # Interpolate in log(k), matching the displayed straight line segments.
        points = list(df.itertuples(index=False))
        crossings = []
        for left, right in zip(points, points[1:]):
            d0 = left.rl_pass_at_k - left.base_pass_at_k
            d1 = right.rl_pass_at_k - right.base_pass_at_k
            if d0 * d1 < 0:
                fraction = d0 / (d0 - d1)
                x = 2 ** (math.log2(left.k) + fraction * (math.log2(right.k) - math.log2(left.k)))
                y = left.base_pass_at_k + fraction * (right.base_pass_at_k - left.base_pass_at_k)
                crossings.append((x, y))
        crossings.extend((p.k, p.base_pass_at_k) for p in points
                         if p.base_pass_at_k == p.rl_pass_at_k)
        if crossings:
            x_cross, y_cross = zip(*crossings)
            ax.scatter(x_cross, y_cross, marker="*", s=240,
                       facecolor="#D55E00", edgecolor="black", linewidth=1,
                       zorder=5, label="Crossover")
            for x, y in crossings:
                print(f"{model} crossover: k ≈ {x:.1f}, pass@k ≈ {100 * y:.2f}%")
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
