#!/usr/bin/env python3
"""Merge each benchmark's own runs with the old baseline runs
into a single ``all_results.json`` per task, which the visualize scripts read.

For each task it concatenates:
    benchmarks/<task>/results/results.json        # this project's OpenRouter runs
    benchmarks/<task>/results/taja_results.json    # baseline runs from a previous project

normalises every row to a common shape (a short language code, plus a "Source"
tag of "new" or "taja"), sorts by (language, model), and writes:
    benchmarks/<task>/results/all_results.json

Run from anywhere, paths resolve relative to this file.

Usage:
    python combine_results.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# (path relative to ROOT, task, source)
FILES = [
    ("benchmarks/copa/results/results.json", "copa", "new"),
    ("benchmarks/copa/results/old_results.json", "copa", "taja"),
    ("benchmarks/piqa/results/results.json", "piqa", "new"),
    ("benchmarks/piqa/results/old_results.json", "piqa", "taja"),
]

PIQA_NEW_LANG = {
    "eng_latin":      "en",
    "hrv_latin":      "hr",
    "ckm_latin":      "hr-ckm",
    "mkd_cyrl":       "mk",
    "slv_latin":      "sl",
    "slv_latin_cerk": "sl-cer",
    "sl_prl":         "sl-prl",
    "srp_cyrl":       "sr_cyrl",
    "srp_latin":      "sr_latn",
    "srp_tor_cyrl":   "sr-tor_cyrl",
    "srp_tor_latin":  "sr-tor_latn",
}

OUTPUTS = {
    "copa": ROOT / "benchmarks/copa/results/all_results.json",
    "piqa": ROOT / "benchmarks/piqa/results/all_results.json",
}


def lang_code(dataset: str, task: str, source: str) -> str:
    if task == "piqa" and source == "new":
        return PIQA_NEW_LANG.get(dataset, dataset)
    # taja files and new COPA use "copa-xx" / "piqa-xx" names
    return dataset.removeprefix(f"{task}-")


def main() -> None:
    combined = {"copa": [], "piqa": []}
    for rel_path, task, source in FILES:
        path = ROOT / rel_path
        if not path.exists():
            print(f"  skipping missing input: {rel_path}")
            continue
        for rec in json.loads(path.read_text()):
            lang = lang_code(rec["Test Dataset"], task, source)
            combined[task].append({
                "Model": rec["Model"],
                "Test Dataset": rec["Test Dataset"],
                "Language": lang,
                "Source": source,
                "Accuracy": rec["Accuracy"],
                "Language-Specific Scores": {lang: {"Accuracy": rec["Accuracy"]}},
            })

    for task, records in combined.items():
        records.sort(key=lambda r: (r["Language"], r["Model"]))
        out = OUTPUTS[task]
        out.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n")
        print(f"Wrote {len(records)} records to {out}")


if __name__ == "__main__":
    main()