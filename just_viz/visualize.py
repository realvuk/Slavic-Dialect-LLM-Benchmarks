#!/usr/bin/env python3
"""Render benchmark leaderboard heatmaps (accuracy per model × language).

Run with no args to render every ``*results*.json`` next to this script, or
pass specific JSON paths. Figures land in ``plots/`` beside the script, named
after each results file. Works from any folder; no API key needed.

    python visualize.py
    python visualize.py copa_all_results.json piqa_all_results.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

HERE = Path(__file__).resolve().parent
OUTPUT_DIR = HERE / "plots"
ANNOT_FONTSIZE = 14

# One superset covers COPA and PIQA; each file uses only the codes it contains.
# Dict order is the column order.
LANG_DISPLAY = {
    "en": "English",
    "sl": "Slovenian",
    "hr": "Croatian",
    "sr": "Serbian",
    "sr_cyrl": "Serbian (Cyrillic)",
    "sr_latn": "Serbian (Latin)",
    "mk": "Macedonian",
    "sl-cer": "Slovenian Cerkno",
    "hr-ckm": "Chakavian",
    "sr-tor": "Serbian Torlak",
    "sr-tor_cyrl": "Serbian Torlak (Cyrillic)",
    "sr-tor_latn": "Serbian Torlak (Latin)",
    "sl-prl": "Slovenian Prlekija",
}

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
    "qwen/qwen3-32b": "Qwen 3 32B",
    "openai/gpt-3.5-turbo": "GPT-3.5 Turbo",
    "openai/gpt-5.4-pro": "GPT-5.4 Pro",
    "openai/gpt-5.4": "GPT-5.4",
    "mistralai/mistral-large-2512": "Mistral Large",
    "mistralai/mistral-small-2603": "Mistral Small",
    "meta-llama/llama-4-maverick": "Llama 4 Maverick",
    # old-run ids
    "gpt-5-2025-08-07": "GPT-5",
    "gpt-4o-2024-08-06": "GPT-4o",
    "gpt-3.5-turbo-0125": "GPT-3.5 Turbo",
    "llama3.3:latest": "Llama 3.3 70B",
    "qwen3:32b": "Qwen 3 32B",
}

# Row order AND whitelist: anything whose base name isn't here is dropped
# (handles dummies, local-run models, and malformed merged ids).
CUSTOM_ORDER = [
    "GPT-5.4 Pro",
    "GPT-5.4",
    "GPT-5",
    "GPT-4o",
    "GPT-3.5 Turbo",
    "Gemini 3.1 Pro",
    "Gemini 3.1 Flash",
    "Gemini 2.5 Pro",
    "Gemini 2.5 Flash",
    "Gemma 4 31B IT",
    "Gemma 4 26B A4B IT",
    "Claude Opus 4.6",
    "Claude Sonnet 4.6",
    "Claude Haiku 4.5",
    "Llama 4 Maverick",
    "Llama 3.3 70B",
    "Mistral Large",
    "Mistral Medium",
    "Mistral Small",
    "Qwen 3 32B",
]


def load_results(path: Path) -> pd.DataFrame:
    rows: dict[str, dict] = {}
    for entry in json.loads(path.read_text()):
        name = RENAME_DICT.get(entry["Model"], entry["Model"])
        if entry.get("Setup"):
            name = f"{name} ({entry['Setup']})"
        row = rows.setdefault(name, {})
        for code, lang in LANG_DISPLAY.items():
            score = (
                entry.get("Language-Specific Scores", {}).get(code, {}).get("Accuracy")
            )
            if score is not None:
                row[lang] = round(float(score), 3)

    df = pd.DataFrame.from_dict(rows, orient="index")
    df = df.reindex(columns=[c for c in LANG_DISPLAY.values() if c in df.columns])

    rank = {name: i for i, name in enumerate(CUSTOM_ORDER)}
    base = lambda n: n.split(" (")[0]
    keep = sorted(
        (n for n in df.index if base(n) in rank), key=lambda n: (rank[base(n)], n)
    )
    return df.loc[keep]


def plot_heatmap(df: pd.DataFrame, output_path: Path, title: str) -> None:
    fig, ax = plt.subplots(
        figsize=(max(8, len(df.columns) * 1.2), max(4, len(df) * 0.6)), dpi=300
    )
    sns.heatmap(
        df,
        ax=ax,
        cmap="RdYlGn",
        vmin=0.5,
        vmax=1.0,
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "Accuracy"},
        annot=False,
    )
    for x in range(df.shape[1]):
        for y in range(df.shape[0]):
            val = df.iat[y, x]
            if not pd.isna(val):
                ax.text(
                    x + 0.5,
                    y + 0.5,
                    f"{val:.3f}",
                    ha="center",
                    va="center",
                    fontsize=ANNOT_FONTSIZE,
                )

    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_ylabel("")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def main() -> None:
    paths = [Path(a).expanduser() for a in sys.argv[1:]] or sorted(
        HERE.glob("*results*.json")
    )
    if not paths:
        raise SystemExit(f"No results JSON found in {HERE}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    for path in paths:
        name = path.stem.replace("_all_results", "").replace("_results", "")
        df = load_results(path)
        out = OUTPUT_DIR / f"{name}_heatmap.png"
        plot_heatmap(df, out, f"{name.upper()} Benchmark")
        print(f"{path.name}: {len(df)} models -> {out}")


if __name__ == "__main__":
    main()
