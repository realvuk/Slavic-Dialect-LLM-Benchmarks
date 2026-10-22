# Revised draft — The Dialect Gap (JT-DH camera-ready)

> **READ FIRST — canonical-run assumption.** The uploaded PDF mixes two versions: the prose and Table 1 describe the *old* model pool (GaMS-27B, DeepSeek-R1-Distill, no GPT-5.4 line, no Prlekija), while Figures 1–2 show a *newer* pool (GPT-5.4 / GPT-5.4 Pro, Gemma 4, Llama 4 Maverick, Mistral Large/Small, Slovenian Prlekija columns, Torlak already in PIQA). This rewrite assumes **the figures reflect the final run**. Every number below taken or derived from the figures is tagged; verify each against your final results files before submission. If the old run is canonical instead, the structure still holds but the numbers and several claims revert.

---

## Title candidates (pick one)

1. **Frontier LLMs narrow but do not close the dialect gap in South Slavic commonsense reasoning** — safest; states both findings; fully supported without new analysis.
2. **Newer, not bigger: model generation tracks dialect robustness in South Slavic commonsense reasoning** — use only if the Spearman/size analysis (see revision plan) is added.
3. **From chance to near-parity: three LLM generations on South Slavic dialect commonsense reasoning** — emphasizes the longitudinal angle.

Avoid "dictates" and "strongest predictor" unless the correlation analysis is in the paper — both R2 and R3 flagged exactly this, and the current PDF title ("dictates") is *stronger* than the submitted title they already objected to.

## Abstract (optional — add if the camera-ready format allows one)

Millions of people communicate daily in dialects that large language models rarely see during training. LLMs now match fine-tuned baselines on standard South Slavic languages, but benchmarks almost never include the dialects spoken alongside them. Whether current models handle dialectal input — and whether newer generations are improving — has therefore remained untested under a consistent protocol. Here we evaluate [AUTHOR: N] models spanning three release generations on causal (COPA) and physical (Global PIQA) commonsense reasoning across four standard South Slavic languages and [AUTHOR: three/four] dialects. Most models lose 20–40 accuracy points on dialect input, but the gap narrows sharply with model generation: the newest flagship systems approach standard-language parity on COPA dialects, while PIQA-Chakavian remains unsolved (best accuracy [0.850, AUTHOR: verify]). Generation, not parameter count, best tracks dialect robustness in our pool [AUTHOR: ρ = …, p = …]. We anticipate these results will inform dialect coverage in pretraining and evaluation for low-resource varieties.

**Contribution line:** This paper contributes by quantifying, under a single protocol, how successive LLM generations shrink — but do not eliminate — the commonsense-reasoning gap between standard South Slavic languages and their dialects.

---

## 1 Introduction

Most current large language models perform well on standard South Slavic languages, but their usability drops sharply on dialects: varieties that appear rarely in training data and are almost absent from benchmarks, yet are used daily by millions of speakers. Whether modern LLMs can handle dialectal input is therefore an open and practically important question, and one that standard benchmarks do not answer. The South Slavic language group is a well-suited setting for investigating it: it includes several standard languages (Slovenian, Croatian, Serbian, Macedonian) alongside living dialects with distinct phonology, lexicon, and morphology, including Chakavian, the Slovenian Cerkno dialect, Serbian Torlak, and Slovenian Prlekija [AUTHOR: confirm Prlekija is in the final run].

Our prior work (Pungeršek et al., 2025) benchmarked zero-shot LLM prompting on classification and commonsense reasoning across South Slavic languages, showing that frontier models match or approach fine-tuned baselines on the standard languages. That standard-language result is inherited here and is not our contribution. The present paper asks what standard-language evaluation cannot show: how models behave on dialect input, and whether the dialect gap is closing across model generations. Our contribution is threefold. First, we extend the model pool with the newest frontier releases ([AUTHOR: final list — per the figures: Gemini 3.1 Pro/Flash, Claude Opus 4.6, Claude Sonnet 4.6, GPT-5.4, GPT-5.4 Pro, Gemma 4, Llama 4 Maverick, Mistral Large/Small]), enabling a comparison across three model generations under one protocol, with earlier results reproduced from our prior work under an identical protocol, test set, and scoring procedure. Second, we operationalize the dialect gap as the difference between each model's mean standard-language and mean dialect accuracy, and track this quantity across generations. Third, we report confidence intervals and paired significance tests for all headline comparisons.

## 2 Benchmarks and experimental setup

The evaluation protocol, prompt templates, label definitions, dataset splits, and scoring procedure follow our prior work. We evaluate on two benchmarks:

- **Global PIQA**: a South Slavic subset of Global Physical Interaction Question Answering (Chang et al., 2025), covering English, Slovenian, Croatian, Serbian (Latin and Cyrillic scripts), Macedonian, and the dialects Cerkno, Chakavian, Torlak (both scripts), and Prlekija [AUTHOR: verify coverage and item counts; the text previously said 100 items per language, 150 for Serbian — update for Torlak/Prlekija].
- **COPA**: a causal commonsense suite extending DIALECT-COPA (Ljubešić et al., 2024a), covering English, Slovenian, Croatian, Serbian, and Macedonian plus the dialects Cerkno, Chakavian, Torlak, and Prlekija [AUTHOR: verify], with 500 test items per language.

Table 1 lists all models with provider, release date, parameter count where disclosed, and the benchmarks each was run on. [AUTHOR: rebuild Table 1 as a single deduplicated table with columns: model | provider | release date | params (open-weight only, "n.d." for closed) | PIQA | COPA. This table doubles as the input to the recency analysis. Resolve the naming inconsistency: the old table says "Gemini 3 Flash Preview" and "Gemini 3.1 Flash Lite", the figures say "Gemini 3.1 Flash" — use the exact OpenRouter model identifiers, and list those identifiers plus query dates in Appendix [X].]

All models are queried through the OpenRouter API with a retry schedule of 30, 60, 90, 120, and 180 seconds on rate-limit errors. Using a single unified access stack removes one source of variance between conditions at the cost of routing all traffic through a third-party gateway. We request temperature 0 for all models; however, this parameter is not honored by all systems — [AUTHOR: list the models for which OpenRouter/the provider ignores or does not expose temperature (e.g., reasoning-mode variants); state that provider defaults apply there]. All results are single-run. We mitigate the resulting uncertainty statistically rather than by repetition: because every model answers the identical items, headline pairwise comparisons use McNemar's exact test on paired outcomes, and we report Wilson 95% confidence intervals for accuracies. At n = 100 items (PIQA), the interval half-width is roughly ±8–10 points in the observed accuracy range, so PIQA differences below ~10 points are not interpreted; at n = 500 (COPA) it is roughly ±2–4 points. [AUTHOR: confirm final per-condition n.]

We evaluate all models by direct zero-shot classification. Each model receives the task in the source language with both candidate options and selects the more plausible one, returning a JSON object with a binary answer. Both tasks are binary forced-choice with label-balanced test sets, so random guessing converges to 0.5 accuracy; scores clustering around 0.5 indicate the model is effectively guessing rather than reasoning. Predicted labels are extracted in two stages: strict JSON parsing, then a regular-expression fallback when reasoning text surrounds the JSON — a pattern most common with Claude variants. If both stages fail, or the API returns an empty or errored response after the retry schedule, the item is scored incorrect. Reported accuracy is therefore *effective* accuracy under our prompting protocol. Parsing failures are rare enough not to drive the comparisons: [AUTHOR: insert counts — e.g., "Claude Sonnet 4.6: k of N items (x%) on condition Y; all other models < z%"]. Per-model parse-failure counts and accuracies conditional on parseable output are given in Appendix [X]. [MOVE → SUPPLEMENT]

**Data contamination.** [AUTHOR: R2 explicitly asked for this and praised its earlier version — it is missing from the current PDF. Restore and sharpen along these lines:] The DIALECT-COPA training and validation splits have been publicly available since [AUTHOR: date]; the test split we evaluate [AUTHOR: was/was not public at the time each model's training data was collected — specify split and dates]. Global PIQA was released in [AUTHOR: month/year]; models with earlier training cutoffs cannot have seen it, whereas for the newest systems ([AUTHOR: list]) contamination cannot be excluded. Two observations argue against contamination driving our headline result: the same newest models that excel on COPA dialects still fail to close PIQA-Chakavian, and [AUTHOR: any additional argument, e.g., performance on held-out vs. public splits, if available]. We nevertheless treat cross-generation comparisons, run under one protocol, as the primary evidence rather than absolute scores.

## 3 Results

Figures 1 and 2 summarize accuracy across all conditions for COPA and PIQA. Table 2 operationalizes the dialect gap: for each model, Δ = mean accuracy on the four standard South Slavic languages minus mean accuracy on the dialect conditions. Four patterns emerge.

**Parity on standard languages.** Frontier models perform at or near English parity on Slovenian, Croatian, Serbian, and Macedonian on both benchmarks, with the strongest systems at or above 0.95 throughout and differences within confidence intervals. Serbian script choice shows no consistent effect: Cyrillic and Latin conditions produce essentially identical scores for every model that handles either [AUTHOR: largest observed script difference + whether within CI].

**A sharp dialect drop for most models.** Most models lose 20–40 accuracy points moving from standard varieties to Chakavian or Cerkno, and several mid-tier systems collapse to near-chance (COPA-Cerkno: Claude Haiku 4.5 at 0.562, Llama 3.3 70B at 0.536, Mistral Medium at 0.532 [derived from Fig. 1 — AUTHOR: verify]). On PIQA, the Chakavian drop is consistently the most severe: models that handle Cerkno reasonably still fall toward chance on Chakavian.

**The gap narrows with model generation.** Table 2 shows Δ shrinking across release generations, and the effect is cleanest *within* provider families, where architecture lineage and data pipeline are most comparable — the comparison R2 identified as our strongest evidence [CLAIM RESIZED: "recency dictates performance" → "the gap narrows with generation; generation is the strongest observable correlate in our pool"]. On COPA, within the OpenAI flagship line, Δ falls monotonically across four generations: 0.179 (GPT-3.5 Turbo) → 0.155 (GPT-4o) → 0.052 (GPT-5) → 0.019 (GPT-5.4 Pro). The Gemini flagship line shows the same movement (0.053 for 2.5 Pro → 0.009 for 3.1 Pro). [All Δ values derived from Fig. 1 as printed — AUTHOR: recompute from final run.] Across the full pool, release date correlates with Δ at Spearman ρ = [AUTHOR], p = [AUTHOR], and with mean dialect accuracy at ρ = [AUTHOR]. Parameter count is a weaker predictor within the open-weight subset where it is observable (ρ = [AUTHOR]); for closed models parameter counts are undisclosed, so we make no scale claims about them.

An important qualification: the generational effect concentrates in flagship tiers. Lighter same-generation variants show gaps comparable to previous-generation flagships (COPA Δ: GPT-5.4 at 0.135 vs. GPT-5 at 0.052; Gemini 3.1 Flash at 0.148 vs. Gemini 2.5 Pro at 0.053 [derived from Fig. 1 — AUTHOR: verify]), and within a single generation the tier gradient is large (Claude Haiku 4.5 / Sonnet 4.6 / Opus 4.6: Δ = 0.190 / 0.075 / 0.052). Generation shifts the frontier; it does not lift all tiers equally.

**Closure is benchmark-specific.** On COPA, the two newest flagships largely close the gap: Gemini 3.1 Pro scores 0.974–0.998 across all dialect conditions and GPT-5.4 Pro 0.964–0.992 [derived from Fig. 1 — AUTHOR: verify; add McNemar tests vs. the next generation]. On PIQA, no model closes Chakavian: the best score is 0.850 (GPT-5.4 Pro [AUTHOR: verify]), with the Gemini flagships at 0.790 — 10–15 points below the same models' standard-language scores, a deficit outside the 95% CI even at n = 100. By contrast, PIQA-Cerkno is nearly closed by the newest flagships (0.960 [AUTHOR: verify]), isolating Chakavian as the outlier. [Deleted: the "exact tie at 0.790" observation — at n = 100 an exact tie is uninformative (R3), and in the newer run it is no longer the best score.]

[AUTHOR — optional but directly answers R1's second point; recipe in the revision plan:] **Error overlap across generations.** Of the COPA-Cerkno items missed by a majority of pre-[year] models, the newest flagships solve [X]%, while [Y]% of items are missed by all models regardless of generation — suggesting the residual difficulty is [item-specific / broadly distributed]. Pairwise error-overlap statistics are given in Appendix [X]. [MOVE → SUPPLEMENT]

Table 2 (main text): model | release date | standard-language mean | dialect mean | Δ, per benchmark, rows sorted by release date. A compact "best model per dialect condition, with 95% CI" table can replace or accompany it to satisfy R3's request for tabular results. [AUTHOR: fill from final run; worked COPA examples above.]

## 4 Discussion

**The difficulty is the dialect form itself.** Dialectal items are not simply harder due to regional customs or local knowledge. Two observations support this. First, the strongest current systems answer near-perfectly the same COPA dialect items on which other frontier models fail, so the items are solvable. Second, the degradation appears on COPA, which tests abstract causal reasoning, as strongly as on PIQA, which is grounded in physical and culturally embedded situations. If cultural specificity alone were responsible, models would struggle on PIQA dialects but not on COPA dialects; their joint failure points to the dialectal form as the primary source of difficulty.

**Why generation? A hypothesis.** The most plausible driver of the generational trend is expanded multilingual — and incidentally dialectal — pretraining coverage, consistent with Ljubešić et al. (2024b), who showed that even modest in-context dialect exposure improves mid-tier models. We stress that this is a hypothesis, not a measured cause: "recency" bundles training-data cutoff and coverage, post-training methods, and architecture, which our observational design cannot separate. Within-family comparisons hold the provider constant and still show the gap closing, which weakens purely architectural explanations, but the underlying mechanism remains unidentified.

**The PIQA-Chakavian residual, as a hypothesis.** The persistence of the PIQA-Chakavian gap even for the strongest systems is the main open puzzle. We hypothesize two contributing factors [CLAIM RESIZED from "Two factors drive this result"]. Chakavian is more lexically distant from standard Croatian than Cerkno is from standard Slovenian, and PIQA items are lexically dense: they hinge on specific nouns for tools, containers, food items, and everyday objects — precisely the vocabulary most likely to diverge across varieties — whereas COPA items rely on abstract causal frames that survive lexical substitution. Aggregate accuracy cannot separate lexical from cultural sources of difficulty, so we treat this account as a hypothesis and make it the primary target of the item-level analysis planned below. [This replaces the earlier contradiction where the same paragraph both asserted the mechanism and disclaimed it — R2.]

**Limitations.** Our design is single-run at requested temperature 0, with the temperature caveat above; test sets are small for PIQA (CIs reported); contamination cannot be fully excluded for the newest models (Section 2); parsing failures are scored incorrect and quantified in Appendix [X]; and routing all queries through one gateway means provider-side serving changes are outside our control. [AUTHOR: add anything model-specific you observed.]

## 5 Conclusion and future work

Frontier LLMs have reached parity with English on standard South Slavic commonsense reasoning, but dialect input reveals a gap invisible in standard evaluation: most models lose 20–40 points on Chakavian and Cerkno. The gap narrows sharply with model generation at the flagship tier — the newest systems approach standard-language parity on all COPA dialects — while PIQA-Chakavian remains unsolved at [0.850, AUTHOR: verify], and lighter model tiers lag roughly a generation behind.

Future work follows three technical directions [reframed per R3 — continuous re-benchmarking demoted from headline direction to infrastructure note]. First, item-level error analysis on PIQA-Chakavian to separate lexical from cultural sources of difficulty, including error-overlap analysis across model generations. Second, few-shot prompting with in-context dialectal examples as a tractable, retraining-free intervention for mid-tier open-weight models, following Ljubešić et al. (2024b). Third, extending dialect coverage to further low-resource varieties [AUTHOR: name them; note that Torlak-in-PIQA and Prlekija, listed as future work in the previous draft, are already in the figures — either report them as results or restore them here, but not both]. We maintain the benchmark for re-evaluation as new models appear [AUTHOR: if you commit to R3's suggestion of a public tracking page, add the URL; otherwise cut this sentence].

## Acknowledgments

[Unchanged, but AUTHOR: verify the grant agreement number — "10116903" has eight digits; HORIZON-MSCA grant agreement numbers have nine.]

## Appendices

- A, B: prompt templates (unchanged).
- [NEW] C: exact OpenRouter model identifiers, release dates, and query dates. [MOVE → SUPPLEMENT]
- [NEW] D: parse-failure counts per model and accuracies conditional on parseable output. [MOVE → SUPPLEMENT]
- [NEW, optional] E: pairwise error-overlap (agreement) statistics on dialect conditions. [MOVE → SUPPLEMENT]

---

### Minor language pass (apply throughout)

- "dialectical" → "dialectal" wherever it appears in the source files (R2 flagged it; it is not in this PDF's text layer, so it may live in the submitted version or figures).
- Add missing articles: "On *the* COPA benchmark", "on *the* PIQA benchmark".
- "Figures 2 and 1 summarise" → "Figures 1 and 2 summarize" (order + pick one spelling variant consistently; the draft mixes -ise/-ize).
- "The present paper wants to test" → "The present paper tests".
- Citation syntax: "consistent with (Ljubešić et al., 2024b), who" → "consistent with Ljubešić et al. (2024b), who"; "following the approach of (Ljubešić et al., 2024b)" → "following Ljubešić et al. (2024b)".
- Unify dialect naming: "Prlekija" vs. "Prleščina" — pick one, introduce the other in parentheses once.
- Unify model naming with OpenRouter identifiers (see Table 1 note).
