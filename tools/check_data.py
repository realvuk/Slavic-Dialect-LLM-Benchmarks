#!/usr/bin/env python3
"""Print per-file label/changed distributions for the DIALECT-COPA splits.

A quick sanity check on the data: record counts, label balance, and how many
examples are marked ``changed``. Defaults to benchmarks/copa/data but accepts a
different folder.

Usage:
    python tools/check_data.py
    python tools/check_data.py path/to/jsonl/dir
"""
from __future__ import annotations

import argparse
import glob
import json
from collections import Counter
from pathlib import Path

DEFAULT_DIR = Path(__file__).resolve().parents[1] / "benchmarks" / "copa" / "data"


def inspect(data_dir: Path) -> None:
    jsonl_files = sorted(glob.glob(str(data_dir / "*.jsonl")))
    if not jsonl_files:
        print(f"No .jsonl files found in {data_dir}")
        return

    for filepath in jsonl_files:
        records = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))

        labels = [r["label"] for r in records if "label" in r]
        changed = [r["changed"] for r in records if "changed" in r]

        print(f"\n📄 {Path(filepath).name}")
        print(f"   Total records : {len(records)}")
        print(f"   Label dist    : {Counter(labels)}")
        print(f"   Changed dist  : {Counter(changed)}")
        print(f"   Has 'label'   : {'label' in records[0] if records else 'N/A'}")
        print(f"   Has 'changed' : {'changed' in records[0] if records else 'N/A'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("data_dir", nargs="?", default=str(DEFAULT_DIR),
                        help="Folder of *.jsonl files (default: benchmarks/copa/data).")
    args = parser.parse_args()
    inspect(Path(args.data_dir))


if __name__ == "__main__":
    main()
