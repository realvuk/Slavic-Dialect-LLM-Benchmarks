#!/usr/bin/env python3
"""Render a combined Croatian vs. Chakavian heatmap for both benchmarks.

Reuses the per-benchmark loaders in ``benchmarks/piqa/visualize.py`` and
``benchmarks/copa/visualize.py`` (so renames, exclusions, and model ordering
stay in sync with the standalone figures), filters each down to Croatian and
Chakavian, and draws both as side-by-side heatmap panels in one figure.

PIQA and COPA are separate result sets, so they keep separate panels — they
just share the model rows on the Y axis. Output:

    plots/croatian_chakavian_heatmap.png

Usage:
    python visualize_croatian_chakavian.py
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "plots"

FOCUS_LANGS = ["Croatian", "Chakavian"]
CMAP = "RdYlGn"
VMIN, VMAX = 0.5, 1.0
ANNOT_FONTSIZE = 14

# (panel title, path to that benchmark's visualize.py)
BENCHMARKS = [
    ("PIQA", ROOT / "benchmarks" / "piqa" / "visualize.py"),
    ("COPA", ROOT / "benchmarks" / "copa" / "visualize.py"),
]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def focus_frame(mod) -> pd.DataFrame:
    """Run the benchmark's own loader, then keep only the focus languages."""
    df = mod.load_and_process_data(mod.RESULTS_PATH, mod.SETUP_FILTER)
    cols = [c for c in FOCUS_LANGS if c in df.columns]
    return df[cols]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    panels = []
    for title, path in BENCHMARKS:
        mod = load_module(path, f"viz_{title.lower().replace('-', '_')}")
        panels.append((title, focus_frame(mod)))

    # Shared, ordered model rows: union across panels, following the curated
    # order each benchmark already defines (identical between the two files).
    custom_order = load_module(BENCHMARKS[1][1], "viz_order_ref").CUSTOM_ORDER
    present = set()
    for _, df in panels:
        present.update(df.index)
    model_order = [m for m in custom_order if m in present]
    panels = [(title, df.reindex(model_order)) for title, df in panels]

    n_models = len(model_order)
    # square=True forces equal-aspect (square) cells, so the figure height drives
    # the cell size; width just needs to leave room for labels + colorbar. A small
    # wspace pulls the PIQA and COPA panels close together.
    fig, axes = plt.subplots(
        1, len(panels), figsize=(8.5, max(4, n_models * 0.55)),
        dpi=300, sharey=True, gridspec_kw={"wspace": 0.05},
    )
    if len(panels) == 1:
        axes = [axes]

    for i, (title, df) in enumerate(panels):
        ax = axes[i]
        sns.heatmap(
            df, ax=ax, cmap=CMAP, vmin=VMIN, vmax=VMAX,
            linewidths=0.5, linecolor="white", cbar=False, annot=False,
            square=False,
        )
        for x in range(df.shape[1]):
            for y in range(df.shape[0]):
                val = df.iat[y, x]
                if pd.isna(val):
                    continue
                ax.text(x + 0.5, y + 0.5, f"{val:.3f}", ha="center",
                        va="center", fontsize=ANNOT_FONTSIZE)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0, ha="center")
        ax.set_xlabel("")
        ax.set_ylabel("")
        # Drop the little tick dashes next to the model names (and column labels).
        ax.tick_params(left=False, bottom=False)
        ax.set_title(title, fontsize=13, fontweight="bold", pad=10)

    # One shared colorbar for both panels, kept slim and close to the panels.
    mappable = cm.ScalarMappable(norm=mcolors.Normalize(VMIN, VMAX), cmap=CMAP)
    cbar = fig.colorbar(mappable, ax=axes, fraction=0.04, pad=0.015)
    cbar.set_label("Accuracy")

    fig.suptitle("PIQA and COPA Benchmark results for Croatian and Chakavian", fontsize=15, fontweight="bold", y=0.99)

    output_path = OUTPUT_DIR / "croatian_chakavian_heatmap.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Combined heatmap saved: {output_path}")


if __name__ == "__main__":
    main()
