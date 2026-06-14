# Archive

Superseded files kept for reference. **Nothing here is part of the live
pipeline** — the canonical code lives in `benchmarks/` and `tools/`. API keys in
the notebooks below have been redacted (the real key lives only in the
git-ignored `.env` at the repo root).

| File | What it is | Superseded by |
|------|------------|----------------|
| `piqa_openrouter.ipynb` | Original PIQA inference notebook | `benchmarks/piqa/run.py` |
| `piqa_old_openrouter.ipynb` | Even older PIQA notebook | `benchmarks/piqa/run.py` |
| `copa_openrouter.ipynb` | Original COPA inference notebook | `benchmarks/copa/run.py` |
| `copa_openrouter_copy.ipynb` | A working copy of the COPA notebook | `benchmarks/copa/run.py` |
| `vuk_piqa_results.json` | Early PIQA results dump (long lang codes) | `benchmarks/piqa/results/results.json` |
| `copa_test_labels.txt` | Stray flat list of COPA gold labels | gold lives in `benchmarks/copa/data/*.jsonl` |
| `stale_results/piqa_old_results/` | Older duplicate of the PIQA results dir | `benchmarks/piqa/results/` |
| `stale_results/copa_old_results/results.json` | Empty (`[]`) leftover results file | `benchmarks/copa/results/results.json` |

You can safely delete this entire folder once you're confident nothing here is
needed.
