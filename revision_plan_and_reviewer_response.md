# Revision plan & reviewer-response map

**VERDICT: Major revision** — the reviewers converge on accept-with-revisions (1, 2, 1), but the current PDF cannot go out as-is: the prose describes one experimental run while the figures show another, and the central claim is stated more strongly in this version's title ("dictates") than in the submitted title the reviewers already called overstated.

## Scorecard (protocol Phase 1)

| Dimension | Score | Evidence (quoted from draft) | Fix |
|---|---|---|---|
| A Fit & significance | 4/5 | "dialect inputs reveal a problem invisible in standard-language evaluations"; "used daily by millions of speakers" — lead narrative: *reveal the hidden*, quantified | Keep framing; support headline claim with the Spearman + Δ analysis so significance is demonstrated, not asserted |
| B Title | 2/5 | "MODEL RECENCY **DICTATES** COMMONSENSE REASONING PERFORMANCE" | Replace with a resized declarative title (three candidates in the draft) |
| C Abstract | n/p | No abstract present (extended-abstract format) | Optional five-step abstract provided in the draft if the camera-ready allows one |
| D Prose | 3/5 | "Two factors drive this result … cannot be determined from aggregate accuracy alone" (internal contradiction); "The present paper wants to test"; missing articles | Hypothesis framing in Discussion; language pass list at end of draft |
| E Structure | 3/5 | §1/§2 overlap ("This work extends our prior work…" appears in both); Conclusion leads future work with "rerunning this benchmark every three to six months" | Merge §1–2; limitations paragraph added; future work reordered to technical directions |
| F Data strategy | 2/5 | Table 1 pool ≠ figure pool (GaMS/DeepSeek in text, GPT-5.4/Gemma 4/Llama 4/Mistral L-S in figures); "the best result is 0.79" vs. Fig. 2 showing GPT-5.4 Pro at 0.850; heatmaps only, colorbar starting at 0.5 without a chance anchor | P0 reconciliation below; Δ table + best-per-condition table; figure spec below |

**RED FLAGS:** text–figure version mismatch (evidence-integrity risk — blocks everything else) | headline claim asserted without a test (R2, R3) | "exact tie" narrative built on n=100 noise (R3) | contamination discussion that R2 references and asks to revise is absent from this PDF entirely (verified via text extraction — the word does not occur) | conclusion lists as future work (Torlak→PIQA, Prlekija) what the figures already contain as results.

## Fix plan (ranked)

1. **P0 — reconcile versions.** Decide which run is canonical. If the new figures are final: rebuild Table 1, delete/replace all GaMS and DeepSeek prose (including the DeepSeek-distillation observation and the "Gemma 3/Qwen 3 vs. GaMS" contrast R2 praised — it needs a successor, e.g., Gemma 4 vs. older larger models, or restore GaMS to the run), and re-derive every in-text number. If the old run is final: regenerate the figures. Do this before anything else.
2. **Add minimal statistics and resize claims accordingly** (Wilson CIs, McNemar on headline pairs, Spearman for recency, Δ table). This is the joint core of R1.1, R1.3, R2, R3.
3. **Rebuild results presentation**: grouped standard+dialect columns, chance-anchored colormap, rows sorted by release date, larger figures, plus the Δ / best-per-condition tables (R2, R3).
4. **Restore the limitations material**: contamination specifics with split-availability dates, temperature-support caveat, parse-failure counts, single-run design (R2, R3).
5. **Discussion/Conclusion rewrite + language pass** (hypothesis framing, future-work reordering, article/spelling fixes) — done in the draft, pending your numbers.

## Reviewer point → change map

| # | Reviewer point (abridged) | Change | Where |
|---|---|---|---|
| R1.1 | Add statistical significance testing | Wilson CIs stated with interpretation thresholds; McNemar exact tests for headline pairs | §2 stats paragraph; §3 |
| R1.2 | Inter-model agreement / error overlap | Optional error-overlap paragraph + appendix; recipe below | §3; App. E |
| R1.3 | Operationalize "gap narrowing" | Δ = standard-mean − dialect-mean per model; Table 2 tracked across generations, with worked family ladders | §3, Table 2 |
| R2.1 | "Strongest predictor" asserted, not tested; include Spearman or soften | Spearman ρ slots added; claim resized in title, §3, §5; [CLAIM RESIZED] tags mark each spot | Title; §3; §5 |
| R2.2 | Report CIs; 0.790 tie and ten-point gaps may be noise | CIs + "not interpreted below ±10 pts (PIQA)" rule; tie observation deleted | §2; §3 |
| R2.3 | Recency confounded with scale/architecture/data | Explicit confound paragraph; within-family ladders foregrounded as strongest evidence; flagship-vs-light-tier qualification added | §3; §4 |
| R2.4 | Quantify Claude formatting failures scored incorrect | Counts slot in §2 + conditional-accuracy appendix | §2; App. D |
| R2.5 | Enlarge heatmaps | Figure spec below | Figs 1–2 |
| R2.6 | Revise contamination discussion; specify which splits public, when | Contamination paragraph restored with dated split-availability slots (it was missing from this PDF) | §2 |
| R2.7 | PIQA-Chakavian explanation as hypothesis | "Two factors drive" → "we hypothesize two contributing factors"; contradiction removed | §4 |
| R2.8 | Parameter count unavailable for closed models | Scale claims restricted to open-weight subset; "n.d." in Table 1 | §3; Table 1 |
| R2.9 | Clarify uniform temperature-0 claim | "Requested temperature 0; not honored by all systems: [list]" | §2 |
| R2.10 | Language pass (articles; dialectical→dialectal) | Checklist at end of draft (note: "dialectical" isn't in this PDF's text layer — check the submitted version/figures) | throughout |
| R3.1 | Compare on other tasks, else recency effect "nothing special" | Reframe: the sharp claim is that generation predicts the *gap* Δ, not just overall skill (standard languages are near ceiling, so generic improvement can't explain Δ shrinking); optionally cite whether recency also tracked your prior-work classification results [AUTHOR: check] | §3; response letter |
| R3.2 | Misleading color scale; stack standard+dialect pairs | Figure spec below | Figs 1–2 |
| R3.3 | Small test sets; tie/parity claims within noise; single run | CIs, McNemar, single-run mitigation paragraph; tie deleted; "parity" claims stated with CI qualifier | §2; §3 |
| R3.4 | "Rerun every 3–6 months" is trivial; prefer technical challenges; webpage if serious | Future work reordered: item-level analysis → few-shot ICL → coverage extension; re-benchmarking demoted to one sentence with optional leaderboard URL | §5 |
| R3.5 | Best results in tabular form | Table 2 (Δ) + optional best-per-dialect-condition table with CIs | §3 |

## Statistics — exact recipes

**CI anchors** (Wilson, 95%): n=100 → half-width ≈ ±0.080 at p̂=0.79, ±0.098 at p̂=0.5; n=500 → ≈ ±0.036 at p̂=0.79, ±0.019 at p̂=0.95. Hence the interpretation rule in §2: PIQA differences <10 pts and COPA differences <4 pts are treated as noise. Formal pairwise claims use McNemar (paired items are far more powerful than comparing independent CIs). With ~20 models × ~10 conditions, don't test everything — pre-select the headline pairs named in the text and apply Holm correction.

**Recency:** Spearman ρ between release date and (a) mean dialect accuracy, (b) Δ, per benchmark. Complement with the within-family ladders already in the draft (they answer R2.3's confound better than any pooled correlation). Scale: correlate params with dialect accuracy on the open-weight subset only. [AUTHOR: fill release dates in Table 1 — several models postdate my reliable knowledge, so I have left all dates to you rather than guess.]

**Agreement (R1.2):** per dialect condition, pairwise error-overlap Jaccard J = |E_i ∩ E_j| / |E_i ∪ E_j|; plus the two headline fractions: share of items missed by a majority of older models that the newest flagships solve, and share missed by *all* models.

```python
import numpy as np
from scipy.stats import spearmanr
from statsmodels.stats.proportion import proportion_confint
from statsmodels.stats.contingency_tables import mcnemar

# df: columns [model, condition, item_id, correct] with correct in {0,1}

def wilson(k, n):
    return proportion_confint(k, n, method="wilson")

def mcnemar_pair(a, b):          # a, b: boolean arrays aligned on item_id
    tbl = [[int(np.sum(a & b)),  int(np.sum(a & ~b))],
           [int(np.sum(~a & b)), int(np.sum(~a & ~b))]]
    return mcnemar(tbl, exact=True)

def jaccard_errors(a, b):        # error-set overlap
    ea, eb = ~a, ~b
    return ea.__and__(eb).sum() / (ea | eb).sum()

rho, p = spearmanr(release_date_ordinal, delta_gap)   # per benchmark
```

## Figure & table spec

- Columns grouped standard-next-to-its-dialects: Slovenian · Cerkno · Prlekija | Croatian · Chakavian | Serbian · Torlak | Macedonian | English(control). (R3.2)
- Diverging colormap anchored at 0.5 = chance (white or neutral at 0.5; label "0.5 = chance" on the colorbar). A 0–1 scale as R3 suggests wastes half the range on a binary task — anchoring at chance answers the underlying objection (that the current 0.5-floored red-green scale exaggerates differences) while keeping resolution; say so in the response letter.
- Rows sorted by release date (oldest at top) — this makes the recency trend visible at a glance and quietly supports the resized claim.
- Enlarge to full text width; consider splitting each heatmap across two rows of conditions if the venue's column width is tight. (R2.5)
- Table 2 in main text (Δ per model per benchmark, sorted by date); best-per-dialect-condition table with CIs either in main text or appendix. (R1.3, R3.5)

## Suggested response-letter openers

- To R2 on contamination: acknowledge, state the restored paragraph now gives split-by-split public-availability dates.
- To R3.1: agree that generic improvement is expected; point out the operationalized claim is about Δ, which generic improvement on near-ceiling standard languages cannot produce; note prior-work classification results [if they support it].
- To all: disclose the model-pool update between submission and camera-ready (new figures) and that all numbers were re-derived from the final run — reviewers respond well to this being volunteered rather than discovered.

**LIMITS:** I judged communication and editorial fit only — I cannot verify your data, per-item outputs, release dates, or which experimental run is canonical, and every number tagged above must be checked against your final results files.
