#!/usr/bin/env python3
"""Render the DIALECT-COPA leaderboard figures.

Reads the combined results (``results/all_results.json``, produced by the
repo-root ``combine_results.py``) and writes two publication-style figures to
``results/plots/``:

    paper_heatmap.png     accuracy per model × language
    paper_bar_chart.png   grouped bars per language

The figure style matches the PIQA script so the two benchmarks can sit side by
side.

Usage:
    python visualize.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Configuration
HERE = Path(__file__).resolve().parent
RESULTS_PATH = HERE / "results" / "all_results.json"
OUTPUT_DIR = HERE / "results" / "plots"
SETUP_FILTER = None  # COPA is zero-shot classification only; kept for parity with PIQA

PLOT_TITLE = "DIALECT-COPA Benchmark"

# Font size for the per-cell accuracy numbers in the heatmap.
ANNOT_FONTSIZE = 14

# COPA lang codes are dataset_name.replace("copa-", "") — keys must match results exactly.
LANG_DISPLAY = {
    "en":     "English",
    "sl":     "Slovenian",
    "hr":     "Croatian",
    "mk":     "Macedonian",
    "sr":     "Serbian",
    "hr-ckm": "Chakavian",
    "sl-cer": "Slovenian Cerkno",
    "sr-tor": "Serbian Torlak",
    "sl-prl": "Slovenian Prlekija",
    "sr-satro": "Serbian Satro",
}

# Desired column order — standard languages first, then dialect varieties.
LANG_ORDER = [
    "English",
    "Slovenian",
    "Croatian",
    "Serbian",
    "Macedonian",
    "Slovenian Cerkno",
    "Chakavian",
    "Serbian Torlak",
    "Slovenian Prlekija",
    "Serbian Satro",
]

RENAME_DICT = {
    "google/gemini-3.1-pro-preview": "Gemini 3.1 Pro",
    "anthropic/claude-opus-4.6": "Claude Opus 4.6",
    "google/gemini-3.1-flash-lite-preview": "Gemini 3.1 Flash",
    "anthropic/claude-sonnet-4.6": "Claude Sonnet 4.6",
    "openai/gpt-5": "GPT-5",
    "google/gemini-2.5-pro": "Gemini 2.5 Pro",
    "google/gemini-2.5-flash": "Gemini 2.5 Flash",
    "openai/gpt-4o": "GPT-4o",
    "anthropic/claude-haiku-4.5": "Claude Haiku 4.5",
    "mistralai/mistral-medium-3.1": "Mistral Medium",
    "meta-llama/llama-3.3-70b-instruct": "Llama 3.3 70B",
    "google/gemma-4-31b-it": "Gemma 4 31B IT",
    "google/gemma-4-26b-a4b-it": "Gemma 4 26B A4B IT",
    "google/gemma-3-27b-it": "Gemma 3 27B IT",
    "qwen/qwen3-32b": "Qwen 3 32B",
    "openai/gpt-3.5-turbo": "GPT-3.5 Turbo",
    "openai/gpt-5.4-pro": "GPT-5.4 Pro",
    "openai/gpt-5.4": "GPT-5.4",
    "mistralai/mistral-large-2512": "Mistral Large",
    "mistralai/mistral-small-2603": "Mistral Small",
    "meta-llama/llama-4-maverick": "Llama 4 Maverick",
    # old-run model ids
    "gpt-5-2025-08-07": "GPT-5",
    "gpt-4o-2024-08-06": "GPT-4o",
    "gpt-3.5-turbo-0125": "GPT-3.5 Turbo",
    "llama3.3:latest": "Llama 3.3 70B",
    "qwen3:32b": "Qwen 3 32B",
    "gemma3:27b": "Gemma 3 27B IT",
    "deepseek-r1:14b": "DeepSeek R1 14B",
    "GaMS-27B-quantized": "GaMS-27B (quant.)",
}

EXCLUDE_MODELS = [
    "Gemma 3 27B IT", "DeepSeek R1 14B", "GaMS-27B (quant.)", "GaMS-27B",
    "dummy-most_frequent", "dummy-stratified",
]

# Custom row order, models absent from the data are silently skipped.
CUSTOM_ORDER = [
    # OpenAI
    "GPT-5.4 Pro", "GPT-5.4", "GPT-5", "GPT-4o", "GPT-3.5 Turbo",
    # Google
    "Gemini 3.1 Pro", "Gemini 3.1 Flash", "Gemini 2.5 Pro", "Gemini 2.5 Flash",
    "Gemma 4 31B IT", "Gemma 4 26B A4B IT",
    # Anthropic
    "Claude Opus 4.6", "Claude Sonnet 4.6", "Claude Haiku 4.5",
    # Meta
    "Llama 4 Maverick", "Llama 3.3 70B",
    # Mistral
    "Mistral Large", "Mistral Medium", "Mistral Small",
    # Alibaba
    "Qwen 3 32B",
]


# Data Processing
def load_and_process_data(filepath: Path, setup_filter=None) -> pd.DataFrame:
    results = json.loads(Path(filepath).read_text())

    model_rows = {}
    for entry in results:
        model_id = entry["Model"]
        setup = entry.get("Setup", "")

        if setup_filter is not None and setup != setup_filter:
            continue

        model_name = RENAME_DICT.get(model_id, model_id)
        if EXCLUDE_MODELS and model_name in EXCLUDE_MODELS:
            continue
        if setup_filter is None and setup:
            model_name = f"{model_name} ({setup})"

        model_rows.setdefault(model_name, {"Model": model_name})

        for lang_code, lang_name in LANG_DISPLAY.items():
            score = (
                entry.get("Language-Specific Scores", {})
                .get(lang_code, {})
                .get("Accuracy")
            )
            if score is not None:
                model_rows[model_name][lang_name] = round(float(score), 3)

    df = pd.DataFrame(list(model_rows.values())).set_index("Model")

    def row_order_key(idx):
        base = idx.split(" (")[0]
        try:
            return (0, CUSTOM_ORDER.index(base), idx)
        except ValueError:
            return (1, 0, idx)

    df = df.loc[sorted(df.index, key=row_order_key)]

    ordered_cols = [c for c in LANG_ORDER if c in df.columns]
    remaining = [c for c in df.columns if c not in ordered_cols]
    return df[ordered_cols + remaining]


# Visualizations
def plot_bar_chart(df: pd.DataFrame, output_dir: Path, setup_filter=None) -> None:
    df_t = df.T
    df_t.index.name = "Language"

    n_models = len(df_t.columns)
    fig_width = max(14, n_models * 1.2)
    fig, ax = plt.subplots(figsize=(fig_width, 7), dpi=300)

    df_t.plot(kind="bar", width=0.9, colormap="tab20", ax=ax)

    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0, fontsize=8)
    ax.set_ylim(0.45, 1.0)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_ylabel("Accuracy")
    ax.set_xlabel("")

    ymin, ymax = ax.get_ylim()
    ax.set_yticks(np.arange(round(ymin, 2), round(ymax + 0.05, 2), 0.05))
    ax.yaxis.grid(True, linestyle="--", linewidth=0.8, color="gray", alpha=0.5)
    ax.set_axisbelow(True)

    title = PLOT_TITLE + (f" ({setup_filter})" if setup_filter else "")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)

    plt.tight_layout()
    output_path = output_dir / "paper_bar_chart.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Bar chart saved: {output_path}")


def plot_heatmap(df: pd.DataFrame, output_dir: Path) -> None:
    fig, ax = plt.subplots(
        figsize=(max(8, len(df.columns) * 1.2), max(4, len(df) * 0.6)), dpi=300
    )

    sns.heatmap(
        df, ax=ax, cmap="RdYlGn", vmin=0.5, vmax=1.0,
        linewidths=0.5, linecolor="white",
        cbar_kws={"label": "Accuracy"}, annot=False,
    )

    for x in range(df.shape[1]):
        for y in range(df.shape[0]):
            val = df.iat[y, x]
            if pd.isna(val):
                continue
            ax.text(x + 0.5, y + 0.5, f"{val:.3f}", ha="center", va="center",
                    fontsize=ANNOT_FONTSIZE)

    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_ylabel("")
    ax.set_title(PLOT_TITLE, fontsize=13, fontweight="bold", pad=12)

    plt.tight_layout()
    output_path = output_dir / "paper_heatmap.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Heatmap saved: {output_path}")


# Execution
def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading and processing data...")
    results_df = load_and_process_data(RESULTS_PATH, SETUP_FILTER)

    print(f"Models processed:   {len(results_df)}")
    print(f"Models in order:    {list(results_df.index)}")
    print(f"Languages in order: {list(results_df.columns)}")

    plot_bar_chart(results_df, OUTPUT_DIR, SETUP_FILTER)
    plot_heatmap(results_df, OUTPUT_DIR)
    print("All visualizations complete.")


if __name__ == "__main__":
    main()