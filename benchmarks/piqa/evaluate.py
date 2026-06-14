#!/usr/bin/env python3
"""Score CLASSLA-PIQA submissions against the gold labels.

Reads every ``submission-*.json`` in the submission folder, compares its
predictions to the ``label`` column of the matching ``data/<dataset>.tsv``, and
writes:

    results/results.json                      # one row per (model, dataset)
    results/tables/results-<dataset>.md       # per-dataset leaderboard
    results/tables/language-specific-results.md

Re-running is idempotent: results are keyed by (model, dataset), so a row is
overwritten rather than duplicated, and rows from earlier runs are preserved.

Usage:
    python evaluate.py                 # scores ./submissions
    python evaluate.py path/to/subs    # scores a different folder
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
RESULTS_DIR = HERE / "results"
TABLES_DIR = RESULTS_DIR / "tables"

# Display/order for the per-dataset markdown tables (stems of the .tsv files).
TARGET_DATASETS = [
    "ckm_latin",
    "eng_latin",
    "hrv_latin",
    "mkd_cyrl",
    "slv_latin_cerk",
    "slv_latin",
    "srp_cyrl",
    "srp_latin",
    "srp_tor_cyrl",
    "srp_tor_latin",
    "sl_prl",
]


def load_true_labels(dataset_name: str):
    """Load ground-truth labels from the TSV test file (label column)."""
    df = pd.read_csv(DATA_DIR / f"{dataset_name}.tsv", sep="\t")
    return df["label"].tolist()


def evaluate(submission_folder: Path) -> list[dict]:
    RESULTS_DIR.mkdir(exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    results_path = RESULTS_DIR / "results.json"

    # Key by (model, dataset) so re-running overwrites a row instead of appending
    # a duplicate. Existing results are loaded first, so accumulation works.
    results_dict = {}
    if results_path.exists():
        for res in json.loads(results_path.read_text()):
            results_dict[f"{res['Model']}_{res['Test Dataset']}"] = res

    for submission_file in sorted(os.listdir(submission_folder)):
        if not submission_file.startswith("submission-"):
            print(f"Skipping (not a submission file): {submission_file}")
            continue

        results = json.loads((Path(submission_folder) / submission_file).read_text())
        model = results["system"]
        dataset_name = results["predictions"][0]["test"]

        try:
            y_true = load_true_labels(dataset_name)
        except FileNotFoundError:
            print(f"WARNING: gold file data/{dataset_name}.tsv not found. "
                  f"Skipping {submission_file}.")
            continue

        y_pred = results["predictions"][0]["predictions"]
        accuracy = float(accuracy_score(y_true, y_pred))
        lang = dataset_name.replace("piqa-", "")

        results_dict[f"{model}_{dataset_name}"] = {
            "Model": model,
            "Test Dataset": dataset_name,
            "Accuracy": accuracy,
            "Language-Specific Scores": {lang: {"Accuracy": accuracy}},
        }

    results_list = list(results_dict.values())
    results_path.write_text(json.dumps(results_list, indent=2))
    print(f"\nAll evaluations completed ({len(results_list)} model×dataset rows). "
          f"Results written to {results_path}")
    return results_list


def write_tables(results_list: list[dict]) -> None:
    result_df = pd.DataFrame(results_list)
    master_path = TABLES_DIR / "language-specific-results.md"

    with open(master_path, "w") as master_f:
        for dataset in TARGET_DATASETS:
            if dataset not in result_df["Test Dataset"].values:
                continue

            subset = (
                result_df[result_df["Test Dataset"] == dataset]
                .drop(columns=["Language-Specific Scores"])
                .sort_values("Accuracy", ascending=False)
                .copy()
            )
            subset["Accuracy"] = subset["Accuracy"].round(3)
            markdown_table = subset.to_markdown(index=False)

            print(f"\n## {dataset}\n")
            print(markdown_table)
            print("\n------------------------------------------")

            (TABLES_DIR / f"results-{dataset}.md").write_text(
                f"## {dataset}\n\n{markdown_table}\n"
            )
            master_f.write(
                f"#### {dataset}\n\n{markdown_table}\n\n"
                f"------------------------------------------\n"
            )

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
