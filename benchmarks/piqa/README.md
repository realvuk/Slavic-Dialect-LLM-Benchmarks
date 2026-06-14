# CLASSLA-PIQA

Zero-shot **physical commonsense reasoning** across South-Slavic languages,
scripts, and dialects. Each example gives a goal/situation and two candidate
solutions; the model picks the more plausible one.

## Data (`data/*.tsv`)

Tab-separated, one example per row. Columns used by the pipeline:

| Column | Meaning |
|--------|---------|
| `prompt` | the goal / situation |
| `solution0` | candidate answer 0 |
| `solution1` | candidate answer 1 |
| `label` | gold answer (`0` or `1`) |

(Extra columns such as `language`, `gemini_translated0/1`, `example_id` are
carried along but not used for scoring.)

### Language / dialect variants

| Stem | Variety |
|------|---------|
| `eng_latin` | English (reference) |
| `slv_latin` | Slovenian |
| `hrv_latin` | Croatian |
| `srp_cyrl` / `srp_latin` | Serbian (Cyrillic / Latin) |
| `mkd_cyrl` | Macedonian |
| `slv_latin_cerk` | Slovenian — Cerkno dialect |
| `ckm_latin` | Chakavian |
| `srp_tor_cyrl` / `srp_tor_latin` | Serbian — Torlak (Cyrillic / Latin) |
| `sl_prl` | Slovenian — Prlekija dialect |

## Pipeline

```bash
# 1. inference  (needs OPENROUTER_API_KEY; writes submissions/)
python run.py                                   # curated models × all datasets
python run.py --models openai/gpt-5 --datasets srp_latin

# 2. evaluate   (submissions/ -> results/results.json + results/tables/)
python evaluate.py

# 3. combine    (run from repo root: new + taja -> results/all_results.json)
python ../../combine_results.py

# 4. visualize  (results/all_results.json -> results/plots/*.png)
python visualize.py
```

`run.py` is resume-safe: existing submissions are skipped, and runs that are
mostly the sentinel value `2` (API/parse failures) are auto-purged and retried
unless you pass `--keep-failed`. Use `--force` for a clean re-run.

## Outputs

- `submissions/submission-<model>-<dataset>.json` — raw predictions per run.
- `results/results.json` — this project's scored runs (one row per model×dataset).
- `results/taja_results.json` — collaborator baseline runs (input, not generated).
- `results/all_results.json` — combined, consumed by `visualize.py`.
- `results/tables/*.md` — per-dataset leaderboards.
- `results/plots/paper_heatmap.png`, `paper_bar_chart.png` — figures.
