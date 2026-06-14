#!/usr/bin/env python3
"""Inspect DIALECT-COPA splits and submissions: field shapes, gold parallelism,
and submission indexing.

Answers three questions used when wiring up evaluation:
  1. What fields do labeled vs unlabeled splits carry?
  2. Are the labeled splits actually parallel (identical gold vectors)?
  3. What value range / indexing do the submission prediction lists use?

Usage:
    python tools/compare_splits.py
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "benchmarks" / "copa" / "data"
SUB = ROOT / "benchmarks" / "copa" / "submissions"


def load(path: Path) -> list[dict]:
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def main() -> None:
    # 1) What fields exist? Inspect one labeled + one unlabeled file.
    for name in ("copa-sr-test.jsonl", "copa-sr-tor-test.jsonl"):
        recs = load(DATA / name)
        print(f"\n{name}: {len(recs)} records")
        print("  keys:", list(recs[0].keys()))
        print("  sample:", {k: recs[0][k] for k in recs[0]})

    # 2) Are the labeled splits actually parallel? Compare their label vectors.
    labeled = {}
    for src in ("sr", "hr", "mk"):
        recs = load(DATA / f"copa-{src}-test.jsonl")
        labeled[src] = [int(r["label"]) for r in recs]
    print("\nLabel vectors identical across sr/hr/mk:",
          labeled["sr"] == labeled["hr"] == labeled["mk"])
    print("Label value set:", set(labeled["sr"]))

    # 3) What indexing do the submissions use?
    sub_files = sorted(glob.glob(str(SUB / "submission-*")))
    if sub_files:
        s = json.load(open(sub_files[0]))
        preds = s["predictions"][0]["predictions"]
        print(f"\n{Path(sub_files[0]).name} -> {s['predictions'][0]['test']}")
        print("  pred value set:", set(preds), "| first 10:", preds[:10])


if __name__ == "__main__":
    main()
