# DIALECT-COPA

Zero-shot **causal commonsense reasoning** (Choice of Plausible Alternatives)
across South-Slavic languages and dialects. Each example gives a premise and two
hypotheses; the model picks the more plausible cause or effect.

## Data (`data/*-test.jsonl`)

One JSON object per line. Fields used by the pipeline:

| Field | Meaning |
|-------|---------|
| `premise` | the situation |
| `choice1` / `choice2` | the two candidate hypotheses |
| `question` | `"cause"` or `"effect"` — what we're reasoning about |
| `label` | gold answer (`0` = choice1, `1` = choice2) — may be absent on held-out splits |
| `idx` | stable example id, used to align gold across parallel splits |

### Parallel-corpus gold

COPA is a parallel corpus: the correct alternative is the **same across every
language and dialect**. Some splits (VarDial held-out targets) ship with gold
stripped. `evaluate.py` handles this by borrowing the shared gold from a labeled
split (`copa-sr`/`hr`/`mk`), aligned by `idx` — so every split can still be
scored. See `_load_reference_gold()` in `evaluate.py`.

### Language / dialect variants

| Stem | Variety |
|------|---------|
| `copa-en` | English (reference) |
| `copa-sl` | Slovenian |
| `copa-hr` | Croatian |
| `copa-sr` | Serbian |
| `copa-mk` | Macedonian |
| `copa-sl-cer` | Slovenian — Cerkno dialect |
| `copa-hr-ckm` | Chakavian |
| `copa-sr-tor` | Serbian — Torlak |
| `copa-sl-prl` | Slovenian — Prlekija dialect |

## Pipeline

```bash
# 1. inference  (needs OPENROUTER_API_KEY; writes submissions/)
python run.py                                   # curated models × all datasets
python run.py --models openai/gpt-5 --datasets copa-sr copa-sr-tor

# 2. evaluate   (submissions/ -> results/results.json + results/tables/)
python evaluate.py

# 3. combine    (run from repo root: new + taja -> results/all_results.json)
python ../../combine_results.py

# 4. visualize  (results/all_results.json -> results/plots/*.png)
python visualize.py
```

`run.py` skips submissions that already exist; use `--force` to re-run. Model
answers (1/2) are stored 0-indexed (answer−1) to match the gold `label`.

## Outputs

- `submissions/submission-<model>-<dataset>.json` — raw predictions per run.
- `results/results.json` — this project's scored runs (one row per model×dataset).
- `results/taja_results.json` — collaborator baseline runs (input, not generated).
- `results/all_results.json` — combined, consumed by `visualize.py`.
- `results/tables/*.md` — per-dataset + per-language leaderboards.
- `results/plots/paper_heatmap.png`, `paper_bar_chart.png` — figures.
