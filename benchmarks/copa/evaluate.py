#!/usr/bin/env python3
"""Score DIALECT-COPA submissions against the gold labels.

COPA is a parallel corpus: the gold label (which alternative is the correct
cause/effect) is invariant across language and dialect. Several splits ship with
gold stripped (VarDial held-out targets), so for those we borrow the shared gold
from a labeled split, aligned by ``idx``.

Reads every ``submission-*.json`` in the submission folder and writes:

    results/results.json                      # one row per (model, dataset)
    results/tables/results-<dataset>.md       # per-dataset leaderboard
    results/tables/language-specific-results.md

Re-running is idempotent: results are keyed by (model, dataset).

Usage:
    python evaluate.py                 # scores ./submissions
    python evaluate.py path/to/subs    # scores a different folder
"""
from __future__ import annotations

import argparse
import json
import os
from functools import lru_cache
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
RESULTS_DIR = HERE / "results"
TABLES_DIR = RESULTS_DIR / "tables"

DATASETS = [
    "copa-en", "copa-sl", "copa-hr", "copa-hr-ckm",
    "copa-mk", "copa-sl-cer", "copa-sr", "copa-sr-tor", "copa-sl-prl",
]

LANGUAGES = [d.replace("copa-", "") for d in DATASETS]


@lru_cache(maxsize=1)
def _load_reference_gold():
    """Borrow the shared parallel-corpus gold from a labeled split, keyed by idx.
    Cached so it is read once per run rather than once per stripped split."""
    for ref in ("copa-sr", "copa-hr", "copa-mk"):
        path = DATA_DIR / f"{ref}-test.jsonl"
        if not path.exists():
            continue
        gold = {}
        for line in open(path):
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            gold[int(entry["idx"])] = int(entry["label"])
        return gold
    raise FileNotFoundError("No labeled reference split found among copa-sr/hr/mk.")


def load_true_labels(dataset_name: str):
    """Load ground-truth labels for a split, in file order.

    If the split carries its own labels, use them. Otherwise fall back to the
    shared parallel-corpus gold borrowed from a labeled split, aligned by idx, so
    labels line up positionally with the submission's prediction list."""
    path = DATA_DIR / f"{dataset_name}-test.jsonl"
    entries = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))

    if entries and "label" in entries[0]:
        return [int(e["label"]) for e in entries]

    gold = _load_reference_gold()
    missing = [int(e["idx"]) for e in entries if int(e["idx"]) not in gold]
    if missing:
        raise KeyError(
            f"{dataset_name}: {len(missing)} idx values have no reference gold "
            f"(e.g. {missing[:5]}). Splits are not aligned."
        )
    return [gold[int(e["idx"])] for e in entries]


def evaluate(submission_folder: Path) -> list[dict]:
    RESULTS_DIR.mkdir(exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    results_path = RESULTS_DIR / "results.json"

    # Key by (model, dataset) so re-running overwrites a row instead of appending
    # a duplicate. Existing results are loaded first, so accumulation works.
    results = {}
    if results_path.exists():
        for r in json.loads(results_path.read_text()):
            results[(r["Model"], r["Test Dataset"])] = r

    skipped = []
    for submission_file in sorted(os.listdir(submission_folder)):
        if not submission_file.startswith("submission-"):
            print(f"Skipping (not a submission file): {submission_file}")
            continue

        try:
            submission = json.loads((Path(submission_folder) / submission_file).read_text())
            model = submission["system"]
            dataset_name = submission["predictions"][0]["test"]

            y_true = load_true_labels(dataset_name)
            y_pred = submission["predictions"][0]["predictions"]
            if len(y_true) != len(y_pred):
                raise ValueError(f"length mismatch: {len(y_true)} gold vs {len(y_pred)} preds")

            acc = float(accuracy_score(y_true, y_pred))
            lang = dataset_name.replace("copa-", "")
            results[(model, dataset_name)] = {
                "Model": model,
                "Test Dataset": dataset_name,
                "Accuracy": acc,
                "Language-Specific Scores": {lang: {"Accuracy": acc}},
            }
        except Exception as e:
            print(f"  !! skipped {submission_file}: {type(e).__name__}: {e}")
            skipped.append((submission_file, f"{type(e).__name__}: {e}"))
            continue

    results_list = list(results.values())
    results_path.write_text(json.dumps(results_list, indent=2))

    print(f"\nAll evaluations completed ({len(results_list)} model×dataset rows). "
          f"Results written to {results_path}")
    if skipped:
        print(f"\n{len(skipped)} submission(s) skipped:")
        for name, reason in skipped:
            print(f"  - {name}: {reason}")
    return results_list


def write_tables(results_list: list[dict]) -> None:
    result_df = pd.DataFrame(results_list)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    # ── Per-dataset markdown tables ─────────────────────────────────────────
    for dataset in DATASETS:
        if dataset not in result_df["Test Dataset"].values:
            continue

        subset = (
            result_df[result_df["Test Dataset"] == dataset]
            .drop(columns=["Language-Specific Scores"])
            .sort_values("Accuracy", ascending=False)
            .copy()
        )
        subset["Accuracy"] = subset["Accuracy"].round(3)

        print(f"\n## {dataset}\n")
        print(subset.to_markdown(index=False))
        print("\n------------------------------------------")

        (TABLES_DIR / f"results-{dataset}.md").write_text(
            f"## {dataset}\n\n{subset.to_markdown(index=False)}"
        )

    # ── Per-language markdown tables ────────────────────────────────────────
    lang_rows = []
    for result in results_list:
        lang = result["Test Dataset"].replace("copa-", "")
        if lang in result.get("Language-Specific Scores", {}):
            lang_rows.append({
                "Model": result["Model"],
                "Test Dataset": result["Test Dataset"],
                "Language": lang,
                "Accuracy": result["Language-Specific Scores"][lang]["Accuracy"],
            })

    lang_df = pd.DataFrame(lang_rows)
    master_path = TABLES_DIR / "language-specific-results.md"
    with open(master_path, "w") as f:
        for lang in LANGUAGES:
            subset = (
                lang_df[lang_df["Language"] == lang]
                .sort_values("Accuracy", ascending=False)
                .copy()
            )
            if subset.empty:
                continue
            subset["Accuracy"] = subset["Accuracy"].round(3)
            f.write(f"\n#### {lang}\n\n")
            f.write(subset.to_markdown(index=False))
            f.write("\n\n------------------------------------------\n")

    print(f"\nLanguage-specific results written to {master_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("submission", nargs="?", default=str(HERE / "submissions"),
                        help="Folder of submission JSON files (default: ./submissions).")
    args = parser.parse_args()

    results_list = evaluate(Path(args.submission))
    write_tables(results_list)


if __name__ == "__main__":
    main()