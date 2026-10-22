# Frontier LLMs narrow but do not close the dialect gap in South Slavic commonsense reasoning

<!-- Title: protocol-compliant (declarative, states both findings, no over-claim).
     If you fill the Spearman analysis in §3, the alternative "Newer, not bigger:
     model generation tracks dialect robustness in South Slavic commonsense
     reasoning" also becomes defensible. Do NOT reuse "dictates" or "strongest
     predictor" — R2.1/R3.1 objected to weaker versions of both. -->

Vuk DINIĆ,¹ Taja KUZMAN PUNGERŠEK,¹ Peter RUPNIK,¹ Ivan PORUPSKI,¹ Nikola LJUBEŠIĆ¹²³

¹ Institut Jožef Stefan, Ljubljana, Slovenia
² Faculty of Computer and Information Science, University of Ljubljana, Slovenia
³ Institute of Contemporary History, Ljubljana, Slovenia

**Keywords:** LLM evaluation, large language models, South Slavic languages, dialects, commonsense reasoning, multilingual NLP

---

## Abstract

<!-- OPTIONAL — include only if the camera-ready format allows one; delete otherwise. -->

Millions of people communicate daily in dialects that large language models rarely see during training. LLMs now match fine-tuned baselines on standard South Slavic languages, but benchmarks almost never include the dialects spoken alongside them. Whether current models handle dialectal input — and whether newer generations are improving — has therefore remained untested under a consistent protocol. Here we evaluate 20 models spanning three release generations on causal (COPA) and physical (Global PIQA) commonsense reasoning across four standard South Slavic languages and four dialects. Most models lose 20–40 accuracy points on dialect input, but the gap narrows sharply with model generation: the newest flagship systems approach standard-language parity on all COPA dialect conditions, while PIQA-Chakavian remains unsolved (best accuracy 0.85, 95% CI [0.77, 0.91]). The narrowing concentrates in flagship tiers; lighter same-generation variants lag roughly a generation behind. We anticipate these results will inform dialect coverage in pretraining and evaluation for low-resource varieties.

---

## 1 Introduction

Most current large language models perform well on standard South Slavic languages, but their usability drops sharply on dialects: varieties that appear rarely in training data and are almost absent from benchmarks, yet are used daily by millions of speakers. Whether modern LLMs can handle dialectal input is therefore an open and practically important question, and one that standard benchmarks do not answer. The South Slavic language group is a well-suited setting for investigating it: it includes several standard languages (Slovenian, Croatian, Serbian, Macedonian) alongside living dialects with distinct phonology, lexicon, and morphology, including Chakavian, the Slovenian Cerkno dialect, Serbian Torlak, and the Slovenian Prlekija dialect (Prleščina).

Our prior work (Pungeršek et al., 2025) benchmarked zero-shot LLM prompting on classification and commonsense reasoning across South Slavic languages, showing that frontier models match or approach fine-tuned baselines on the standard languages. That standard-language result is inherited here and is not our contribution. The present paper asks what standard-language evaluation cannot show: how models behave on dialect input, and whether the dialect gap is closing across model generations. Our contribution is threefold. First, we extend the model pool to 20 systems whose release dates span three model generations — from GPT-3.5-era models, through the mid-2025 releases, to the newest flagships (Table 1) — evaluated under one protocol, with earlier results reproduced from our prior work under an identical test set and scoring procedure. Second, we operationalize the dialect gap as Δ, the difference between each model's mean standard-language and mean dialect accuracy, and track this quantity across generations (Table 2). Third, we report 95% confidence intervals for all headline comparisons.

## 2 Benchmarks and experimental setup

The evaluation protocol, prompt templates, label definitions, dataset splits, and scoring procedure follow our prior work. We evaluate on two benchmarks:

- **Global PIQA**: a South Slavic subset of Global Physical Interaction Question Answering (Chang et al., 2025), covering English, Slovenian, Croatian, Serbian (Latin and Cyrillic scripts), Macedonian, and the dialects Cerkno, Chakavian, Torlak (both scripts), and Prlekija, with 100 test items per condition.
- **COPA**: a causal commonsense suite extending DIALECT-COPA (Ljubešić et al., 2024a), covering English, Slovenian, Croatian, Serbian, and Macedonian plus the dialects Cerkno, Chakavian, Torlak, and Prlekija, with 500 test items per condition. All non-English items are translations of the same English originals into the respective languages and dialects.

Table 1 lists all models with provider, release date, parameter count where disclosed, and the benchmarks each was run on.

**Table 1: Models evaluated on both benchmarks.** <!-- Single deduplicated table (both benchmarks use the same pool). This table doubles as the input to the recency analysis in §3 — the dates must be verified before the Spearman is computed. Dates below marked [AUTHOR] postdate the assistant's reliable knowledge; the others should also be checked. -->

| Model | Provider | Release date | Params | PIQA | COPA |
|---|---|---|---|---|---|
| GPT-3.5 Turbo | OpenAI | 2023-03 | n.d. | ✓ | ✓ |
| GPT-4o | OpenAI | 2024-08 | n.d. | ✓ | ✓ |
| Llama 3.3 70B | Meta | 2024-12 | 70B | ✓ | ✓ |
| Qwen 3 32B | Alibaba | 2025-04 | 32B | ✓ | ✓ |
| Llama 4 Maverick | Meta | 2025-04 | [AUTHOR: 400B total, 17B active — verify] | ✓ | ✓ |
| Gemini 2.5 Flash | Google | 2025-06 | n.d. | ✓ | ✓ |
| Gemini 2.5 Pro | Google | 2025-06 | n.d. | ✓ | ✓ |
| GPT-5 | OpenAI | 2025-08 | n.d. | ✓ | ✓ |
| Mistral Medium 3.1 | Mistral | 2025-08 | n.d. | ✓ | ✓ |
| Claude Haiku 4.5 | Anthropic | 2025-10 | n.d. | ✓ | ✓ |
| Claude Sonnet 4.6 | Anthropic | [AUTHOR: date] | n.d. | ✓ | ✓ |
| Claude Opus 4.6 | Anthropic | [AUTHOR: date] | n.d. | ✓ | ✓ |
| Gemini 3.1 Flash Lite | Google | [AUTHOR: date] | n.d. | ✓ | ✓ |
| Gemini 3.1 Pro | Google | [AUTHOR: date] | n.d. | ✓ | ✓ |
| Mistral Large | Mistral | 2025-12 | [AUTHOR: params or n.d.] | ✓ | ✓ |
| Gemma 4 31B IT | Google | [AUTHOR: date] | 31B | ✓ | ✓ |
| Gemma 4 26B A4B IT | Google | [AUTHOR: date] | 26B (4B active) | ✓ | ✓ |
| Mistral Small | Mistral | 2026-03 | [AUTHOR: params or n.d.] | ✓ | ✓ |
| GPT-5.4 | OpenAI | [AUTHOR: date] | n.d. | ✓ | ✓ |
| GPT-5.4 Pro | OpenAI | [AUTHOR: date] | n.d. | ✓ | ✓ |

<!-- Naming: this table and the figures must agree. The figures currently label
     google/gemini-3.1-flash-lite-preview as "Gemini 3.1 Flash" — pick one name
     and change RENAME_DICT in just_viz/{copa,piqa}_visualize.py to match. -->

All newly added models, and all models on the newly added dialect conditions (Prlekija; Torlak in PIQA), are queried through the OpenRouter API with a retry schedule of 30, 60, 90, 120, and 180 seconds on rate-limit errors; results for older models on previously covered conditions are reproduced from our prior work [AUTHOR: that work queried these models via {provider APIs / local runs} — state which, since it qualifies the "single access stack" claim below]. Using a single unified access stack for all new measurements removes one source of variance between conditions, at the cost of routing traffic through a third-party gateway. We request temperature 0 for all models; this parameter is not honored by all systems — [AUTHOR: list the models for which the provider ignores or does not expose temperature, e.g., reasoning-mode variants]; provider defaults apply there. Exact model identifiers and query dates are listed in Appendix C.

All results are single-run. We mitigate the resulting uncertainty statistically rather than by repetition: we report Wilson 95% confidence intervals for accuracies, and because at n = 100 items (PIQA) the interval half-width is roughly ±8–10 points in the observed accuracy range, we do not interpret PIQA differences below 10 points; at n = 500 (COPA) the half-width is roughly ±2–4 points, and we do not interpret COPA differences below 4 points.

We evaluate all models by direct zero-shot classification. Each model receives the task in the source language with both candidate options and selects the more plausible one, returning a JSON object with a binary answer. Both tasks are binary forced-choice with label-balanced test sets, so random guessing converges to 0.5 accuracy; scores clustering around 0.5 indicate the model is effectively guessing rather than reasoning. Predicted labels are extracted in two stages: strict JSON parsing, then a regular-expression fallback when reasoning text surrounds the JSON. If both stages fail, or the API returns an empty or errored response after the retry schedule, the item is scored incorrect. Reported accuracy is therefore *effective* accuracy under our prompting protocol. Such failures are rare enough not to drive any comparison: at most 1 of 5,000 COPA items and 14 of 1,100 PIQA items (1.3%, Gemini 3.1 Pro) for any model. <!-- [AUTHOR: these counts were derived from non-binary prediction values in the submission files — confirm against the scoring code that this is the failure encoding.] -->

**Data contamination.** The DIALECT-COPA training and validation splits have been publicly available since [AUTHOR: month] 2024; the test split we evaluate, including its dialectal translations, [AUTHOR: was/was not] public at the time each model's training data was collected — [AUTHOR: verify per release date]. Global PIQA was released publicly in October 2025; models with earlier training cutoffs cannot have seen it, whereas for the newest systems contamination cannot be excluded. Two observations argue against contamination driving our headline result. First, the COPA dialect conditions — where the evaluated translations were not available for training — show the same generational pattern as PIQA, so the trend does not depend on data a model could have memorized. Second, the same newest models that excel on COPA dialects still fail to close PIQA-Chakavian. We nevertheless treat cross-generation comparisons, run under one protocol, as the primary evidence rather than absolute scores.

## 3 Results

Figures 1 and 2 summarize accuracy across all conditions for COPA and PIQA. Table 2 operationalizes the dialect gap: for each model, Δ is the mean accuracy over the four standard South Slavic languages minus the mean accuracy over the dialect conditions (English serves as a control and enters neither mean; on PIQA, the two Serbian scripts are first averaged into one Serbian value and the two Torlak scripts into one Torlak value, so no variety is double-weighted). Four patterns emerge.

**Parity on standard languages.** Frontier models perform at or near English parity on Slovenian, Croatian, Serbian, and Macedonian on both benchmarks, with the strongest systems at or above 0.95 throughout and differences within confidence intervals. Serbian script choice shows no consistent effect: the largest observed difference between Cyrillic and Latin conditions is 4 points on standard Serbian (Gemma 4 31B IT) and 6 points on Torlak (GPT-5.4), both within the interpretation thresholds defined in Section 2.

**A sharp dialect drop for most models.** Most models lose 20–40 accuracy points moving from standard varieties to Chakavian or Cerkno, and several mid-tier systems collapse to near-chance (COPA-Cerkno: Claude Haiku 4.5 at 0.562, Llama 3.3 70B at 0.536, Mistral Medium at 0.532). On PIQA, the Chakavian drop is consistently the most severe: models that handle Cerkno reasonably still fall toward chance on Chakavian (e.g., Gemini 2.5 Pro: 0.95 on Cerkno, 0.79 on Chakavian).

**The gap narrows with model generation.** Table 2 shows Δ shrinking across release generations on both benchmarks, and the effect is cleanest *within* provider families, where architecture lineage and data pipeline are most comparable. On COPA, within the OpenAI flagship line, Δ falls monotonically across four generations: 0.179 (GPT-3.5 Turbo) → 0.155 (GPT-4o) → 0.052 (GPT-5) → 0.019 (GPT-5.4 Pro); on PIQA the same ladder reads 0.283 → 0.217 → 0.116 → 0.069. The Gemini flagship line shows the same movement on COPA (0.053 for 2.5 Pro → 0.009 for 3.1 Pro), while on PIQA it is flat (0.090 → 0.091), a difference within noise at n = 100. Across the full pool, release date correlates with Δ at Spearman ρ = [AUTHOR], p = [AUTHOR], and with mean dialect accuracy at ρ = [AUTHOR]. Parameter count is observable only for the open-weight subset, where it is a weaker correlate (ρ = [AUTHOR]); for closed models parameter counts are undisclosed, so we make no scale claims about them. <!-- If the Spearman analysis is not run, delete these two sentences; the within-family ladders then carry the claim, and the title must stay in its current resized form. -->

An important qualification: the generational effect concentrates in flagship tiers. Lighter same-generation variants show gaps comparable to previous-generation flagships (COPA Δ: GPT-5.4 at 0.135 vs. GPT-5 at 0.052; Gemini 3.1 Flash Lite at 0.147 vs. Gemini 2.5 Pro at 0.053), and within a single generation the tier gradient is large (Claude Haiku 4.5 / Sonnet 4.6 / Opus 4.6: Δ = 0.190 / 0.075 / 0.052 on COPA). Generation shifts the frontier; it does not lift all tiers equally.

**Closure is benchmark-specific.** On COPA, the two newest flagships largely close the gap: Gemini 3.1 Pro scores 0.974–0.998 across all dialect conditions and GPT-5.4 Pro 0.964–0.992. On PIQA, no model brings Δ below 0.069, and no model closes Chakavian: the best score is 0.85 (GPT-5.4 Pro), whose entire confidence interval [0.77, 0.91] lies below the same model's standard-language scores, with the Gemini flagships at 0.79. By contrast, the best systems reach 0.96 on PIQA-Cerkno and PIQA-Torlak and 0.93 on PIQA-Prlekija, isolating Chakavian as the outlier. Table 3 reports the best result per dialect condition with confidence intervals.

**Table 2: The dialect gap Δ per model and benchmark** (mean standard-language accuracy − mean dialect accuracy; rows sorted by release date). <!-- Values computed from the final results files (just_viz/tables/table2_dialect_gap.md); full std/dial means available there if the venue's width allows six data columns. -->

| Model | COPA Δ | PIQA Δ |
|---|---|---|
| GPT-3.5 Turbo | 0.179 | 0.283 |
| GPT-4o | 0.155 | 0.217 |
| Llama 3.3 70B | 0.220 | 0.310 |
| Qwen 3 32B | 0.179 | 0.244 |
| Llama 4 Maverick | 0.213 | 0.276 |
| Gemini 2.5 Flash | 0.134 | 0.201 |
| Gemini 2.5 Pro | 0.053 | 0.090 |
| GPT-5 | 0.052 | 0.116 |
| Mistral Medium 3.1 | 0.213 | 0.276 |
| Claude Haiku 4.5 | 0.190 | 0.346 |
| Claude Sonnet 4.6 | 0.075 | 0.250 |
| Claude Opus 4.6 | 0.052 | 0.210 |
| Gemini 3.1 Flash Lite | 0.147 | 0.205 |
| Gemini 3.1 Pro | **0.009** | 0.091 |
| Mistral Large | 0.214 | 0.336 |
| Gemma 4 31B IT | 0.177 | 0.272 |
| Gemma 4 26B A4B IT | 0.233 | 0.327 |
| Mistral Small | 0.200 | 0.316 |
| GPT-5.4 | 0.135 | 0.219 |
| GPT-5.4 Pro | 0.019 | **0.069** |

**Table 3: Best result per dialect condition, with Wilson 95% CIs.**

| Benchmark | Condition | Best model | Accuracy | 95% CI |
|---|---|---|---|---|
| COPA | Slovenian Cerkno | Gemini 3.1 Pro | 0.994 | [0.983, 0.998] |
| COPA | Chakavian | Gemini 3.1 Pro | 0.974 | [0.956, 0.985] |
| COPA | Serbian Torlak | Gemini 3.1 Pro | 0.998 | [0.989, 1.000] |
| COPA | Slovenian Prlekija | GPT-5.4 Pro | 0.990 | [0.977, 0.996] |
| PIQA | Slovenian Cerkno | Gemini 3.1 Pro | 0.96 | [0.90, 0.98] |
| PIQA | Chakavian | GPT-5.4 Pro | 0.85 | [0.77, 0.91] |
| PIQA | Serbian Torlak (Cyrillic) | Gemini 3.1 Pro | 0.96 | [0.90, 0.98] |
| PIQA | Serbian Torlak (Latin) | GPT-5 | 0.96 | [0.90, 0.98] |
| PIQA | Slovenian Prlekija | GPT-5.4 Pro | 0.93 | [0.86, 0.97] |

*Figure 1 caption:* Accuracy on COPA (500 items per condition). Columns group each standard language with its dialect(s); rows are sorted by release date, oldest first. The color scale is anchored at 0.5 = chance (white); blue indicates above-chance accuracy, red below. *(File: `just_viz/plots/copa_heatmap_v2.png`.)*

*Figure 2 caption:* Accuracy on Global PIQA (100 items per condition), same layout and scale as Figure 1. *(File: `just_viz/plots/piqa_heatmap_v2.png`.)*

## 4 Discussion

**The difficulty is the dialect form itself.** Dialectal items are not simply harder due to regional customs or local knowledge. Two observations support this. First, the strongest current systems answer near-perfectly the same COPA dialect items on which other frontier models fail, so the items are solvable. Second, the degradation appears on COPA, which tests abstract causal reasoning, as strongly as on PIQA, which is grounded in physical and culturally embedded situations. If cultural specificity alone were responsible, models would struggle on PIQA dialects but not on COPA dialects; their joint failure points to the dialectal form as the primary source of difficulty.

**Why generation? A hypothesis.** The most plausible driver of the generational trend is expanded multilingual — and incidentally dialectal — pretraining coverage, consistent with Ljubešić et al. (2024b), who showed that even modest in-context dialect exposure improves mid-tier models. We stress that this is a hypothesis, not a measured cause: "recency" bundles training-data cutoff and coverage, post-training methods, and architecture, which our observational design cannot separate. Within-family comparisons hold the provider constant and still show the gap closing, which weakens purely architectural explanations, but the underlying mechanism remains unidentified.

**The PIQA-Chakavian residual, as a hypothesis.** The persistence of the PIQA-Chakavian gap even for the strongest systems is the main open puzzle. We hypothesize two contributing factors. Chakavian is more lexically distant from standard Croatian than Cerkno is from standard Slovenian, and PIQA items are lexically dense: they hinge on specific nouns for tools, containers, food items, and everyday objects — precisely the vocabulary most likely to diverge across varieties — whereas COPA items rely on abstract causal frames that survive lexical substitution. Aggregate accuracy cannot separate lexical from cultural sources of difficulty, so we treat this account as a hypothesis and make it the primary target of the item-level analysis planned below.

**Limitations.** Our design is single-run at requested temperature 0, with the temperature caveat of Section 2; test sets are small for PIQA, so we interpret only differences beyond the stated thresholds; contamination cannot be fully excluded for the newest models (Section 2); parsing failures are scored incorrect and quantified in Section 2; and routing all new queries through one gateway means provider-side serving changes are outside our control.

## 5 Conclusion and future work

Frontier LLMs have reached parity with English on standard South Slavic commonsense reasoning, but dialect input reveals a gap invisible in standard evaluation: most models lose 20–40 points on Chakavian and Cerkno. The gap narrows sharply with model generation at the flagship tier — the newest systems approach standard-language parity on all COPA dialect conditions — while PIQA-Chakavian remains unsolved at 0.85, and lighter model tiers lag roughly a generation behind.

Future work follows three technical directions. First, item-level error analysis on PIQA-Chakavian to separate lexical from cultural sources of difficulty, including error-overlap analysis across model generations. Second, few-shot prompting with in-context dialectal examples as a tractable, retraining-free intervention for mid-tier open-weight models, following Ljubešić et al. (2024b). Third, extending dialect coverage to further low-resource South Slavic varieties, for which our prior evaluations of Bosnian and Bulgarian provide natural starting points. We will continue re-evaluating new models on the benchmark as they appear. <!-- [AUTHOR: if you commit to R3's public tracking page, add the URL here; otherwise this single sentence is the appropriately demoted version of continuous re-benchmarking.] -->

## Acknowledgments

This paper was produced as part of the "Learning Network for AI and Data-Powered Social Innovation and Co-Creation of Transformative Change" project, acronym Data2Action, funded by the European Union's HORIZON-MSCA-2023-DN-01 programme under Marie Skłodowska-Curie grant agreement No. 10116903. <!-- [AUTHOR: verify — HORIZON-MSCA grant agreement numbers have nine digits; this one has eight.] -->

## Appendix A: Global PIQA prompt template

<!-- Unchanged from the current draft, EXCEPT: the code block in the current
     camera-ready PDF is truncated at the right margin ("…a value should b").
     In Overleaf, wrap the verbatim lines (e.g., listings with breaklines=true,
     or manual line breaks as in the originally reviewed version) so the full
     prompt text is visible — a truncated prompt fails reproducibility. -->

## Appendix B: COPA prompt template

<!-- Unchanged; same line-wrapping fix as Appendix A. -->

## Appendix C: Model identifiers and query dates

All new measurements used the following OpenRouter identifiers (query dates: [AUTHOR: date range]):

`openai/gpt-5.4-pro`, `openai/gpt-5.4`, `openai/gpt-5`, `openai/gpt-4o`, `openai/gpt-3.5-turbo`, `google/gemini-3.1-pro-preview`, `google/gemini-3.1-flash-lite-preview`, `google/gemini-2.5-pro`, `google/gemini-2.5-flash`, `google/gemma-4-31b-it`, `google/gemma-4-26b-a4b-it`, `anthropic/claude-opus-4.6`, `anthropic/claude-sonnet-4.6`, `anthropic/claude-haiku-4.5`, `meta-llama/llama-4-maverick`, `meta-llama/llama-3.3-70b-instruct`, `mistralai/mistral-large-2512`, `mistralai/mistral-medium-3.1`, `mistralai/mistral-small-2603`, `qwen/qwen3-32b`.

Results reproduced from our prior work used [AUTHOR: the identifiers of that run — the result files record `gpt-5-2025-08-07`, `gpt-4o-2024-08-06`, `gpt-3.5-turbo-0125`, and local identifiers `llama3.3:latest`, `qwen3:32b` — state the access route for each].

## References

<!-- Keep the current reference list, with two fixes:
     1. Remove the Zotero export artifacts: the dangling "Other Preprint." line
        (Chang et al.) and "Other 17 pages; 4 figures; 3 tables. Submitted to
        the LLMs4SSH workshop…" (Pungeršek et al.).
     2. Entries needed: Chang et al. 2025 (Global PIQA); Ljubešić et al. 2024a
        (DIALECT-COPA); Ljubešić et al. 2024b (JSI & WüNLP shared task);
        Pungeršek et al. 2025. If you keep Discussion citations from the
        originally reviewed version (Dai et al. 2025; Tran et al. 2025; Ahuja
        et al. 2023; Roemmele et al. 2011; Golchin & Surdeanu 2023), restore
        those entries too — the current camera-ready cut the paragraphs citing
        them, so by default they should stay out. -->
