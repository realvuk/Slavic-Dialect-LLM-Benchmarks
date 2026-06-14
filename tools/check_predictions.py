#!/usr/bin/env python3
"""Compare the per-line ``label`` field across several JSONL files.

Useful for confirming that parallel COPA splits share the same gold-label
pattern, or that two prediction dumps agree line-for-line.

Usage:
    python tools/check_predictions.py a.jsonl b.jsonl c.jsonl
"""
from __future__ import annotations

import argparse
import json


def compare_label_patterns(file_paths: list[str]) -> None:
    file_handles = [open(f, "r") for f in file_paths]
    line_number = 0
    mismatch_count = 0
    max_mismatches_to_show = 5

    print("Beginning pattern comparison...")
    try:
        # zip iterates through all files line-by-line at the same time.
        for lines in zip(*file_handles):
            line_number += 1
            labels = [json.loads(line).get("label") for line in lines]

            # A set removes duplicates; if all labels match, its length is 1.
            if len(set(labels)) > 1:
                mismatch_count += 1
                if mismatch_count <= max_mismatches_to_show:
                    print(f"Mismatch at line {line_number}: {labels}")
                elif mismatch_count == max_mismatches_to_show + 1:
                    print("...further mismatches suppressed to save space.")

        if any(f.readline() for f in file_handles):
            print("\nWarning: The files do not have the same number of lines.")
            return
    except json.JSONDecodeError as e:
        print(f"Error reading JSON at line {line_number + 1}: {e}")
        return
    finally:
        for f in file_handles:
            f.close()

    print("\n--- Final Report ---")
    if mismatch_count == 0:
        print(f"Perfect Match: all {len(file_paths)} files share the exact same "
              f"pattern for {line_number} lines.")
    else:
        agreement = ((line_number - mismatch_count) / line_number) * 100
        print(f"Pattern Divergence: {mismatch_count} mismatched lines out of "
              f"{line_number} total ({agreement:.2f}% agreement).")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+", help="JSONL files to compare (2 or more).")
    args = parser.parse_args()
    if len(args.files) < 2:
        parser.error("provide at least two files to compare")
    compare_label_patterns(args.files)


if __name__ == "__main__":
    main()
