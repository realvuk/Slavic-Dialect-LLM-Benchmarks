#!/usr/bin/env python3
"""Run CLASSLA-PIQA inference against OpenRouter models.

For every (model, dataset) pair this queries the model once per example with a
zero-shot, JSON-only prompt and writes a submission file to ``submissions/``:

    submissions/submission-<model-short>-<dataset>.json

Submissions already on disk are skipped, so the script is safe to re-run and
resume. A run that mostly produced the sentinel value ``2`` (API/parse failures)
is treated as failed and regenerated unless ``--keep-failed`` is passed.

Usage examples
--------------
    # default curated model list, all datasets
    python run.py

    # one model, two datasets
    python run.py --models openai/gpt-5 --datasets srp_latin srp_cyrl

    # force a clean re-run of everything
    python run.py --force

The OpenRouter key is read from ``OPENROUTER_API_KEY`` (see ``.env.example`` at
the repo root).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path

import pandas as pd
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
SUBMISSIONS_DIR = HERE / "submissions"

# Curated default sweep. Comment items in/out or override with --models / --datasets.
DEFAULT_MODELS = [
    "google/gemini-3.1-pro-preview",
    "anthropic/claude-opus-4.6",
    "google/gemini-3.1-flash-lite-preview",
    "anthropic/claude-sonnet-4.6",
    "openai/gpt-5",
    "google/gemini-2.5-pro",
    "google/gemini-2.5-flash",
    "openai/gpt-4o",
    "anthropic/claude-haiku-4.5",
    "mistralai/mistral-medium-3.1",
    "meta-llama/llama-3.3-70b-instruct",
    "google/gemma-4-31b-it",
    "google/gemma-4-26b-a4b-it",
    "qwen/qwen3-32b",
    "openai/gpt-3.5-turbo",
    "openai/gpt-5.4-pro",
    "openai/gpt-5.4",
    "mistralai/mistral-large-2512",
    "mistralai/mistral-small-2603",
    "meta-llama/llama-4-maverick",
]

# Dataset stems matching the .tsv files in data/ (language/script/dialect variants).
DEFAULT_DATASETS = [
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

# Sentinel recorded when a prediction can't be obtained/parsed. PIQA answers are
# 0/1, so 2 is unambiguous and lets evaluate.py / re-runs spot failed instances.
SENTINEL = 2

def build_client() -> OpenAI:
    """Construct the OpenRouter client from OPENROUTER_API_KEY."""
    load_dotenv(find_dotenv())
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit(
            "OPENROUTER_API_KEY is not set. Copy .env.example to .env at the repo "
            "root and add your OpenRouter key (https://openrouter.ai/keys)."
        )
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

def is_failed_submission(path: Path, fail_ratio: float = 0.9) -> bool:
    """Return True if a submission file is mostly sentinels (a failed run)."""
    try:
        data = json.loads(path.read_text())
        preds = data["predictions"][0]["predictions"]
        if not preds:
            return True
        n_sentinel = sum(1 for p in preds if p == SENTINEL)
        return (n_sentinel / len(preds)) >= fail_ratio
    except Exception:
        return True  # unreadable/corrupt -> treat as failed

def extract_answer(raw: str):
    """Two-stage parse: strict JSON first, then a regex fallback.

    Reasoning models often wrap or precede the JSON with prose, so a bare
    json.loads is not enough. Returns 0/1, or None if nothing is parseable."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    # Stage 1: strict JSON on the first complete {...} object.
    candidate = raw
    if not candidate.startswith("{"):
        m = re.search(r"\{[^{}]*\}", candidate)
        candidate = m.group() if m else None
    if candidate:
        try:
            val = int(json.loads(candidate)["answer"])
            if val in (0, 1):
                return val
        except Exception:
            pass

    # Stage 2: regex fallback over the whole response.
    m = re.search(r'"?\'?answer"?\'?\s*:\s*([01])', raw)
    if m:
        return int(m.group(1))

    return None

def build_prompt(entry) -> str:
    return (
        f"### Task\n"
        f"    Given the following situation, which option is more likely to be correct?\n\n"
        f"    Situation: {entry['prompt']}\n\n"
        f"    Option 0: {entry['solution0']}\n\n"
        f"    Option 1: {entry['solution1']}\n\n"
        f"### Output format\n"
        f"    Return a valid JSON dictionary with the following key: 'answer' "
        f"and a value should be either 0 (if option 0 is more plausible) "
        f"or 1 (if option 1 is more plausible). "
        f"Answer ONLY with the JSON dictionary, no explanation."
    )

def predict(client: OpenAI, dataset: str, model: str, *, force: bool,
            keep_failed: bool, fail_ratio: float, max_tokens: int) -> None:
    SUBMISSIONS_DIR.mkdir(exist_ok=True)
    model_short = model.split("/")[-1]
    out_path = SUBMISSIONS_DIR / f"submission-{model_short}-{dataset}.json"

    if out_path.exists() and not force:
        if not keep_failed and is_failed_submission(out_path, fail_ratio):
            print(f"  purging failed submission, will regenerate: {out_path.name}")
            out_path.unlink()
        else:
            print(f"  skipping (already exists): {out_path.name}")
            return

    tsv_path = DATA_DIR / f"{dataset}.tsv"
    if not tsv_path.exists():
        print(f"  WARNING: missing {tsv_path}, skipping.")
        return
    df = pd.read_csv(tsv_path, sep="\t")

    responses = []
    n_api_fail = n_parse_fail = 0
    start = time.time()

    for _, entry in df.iterrows():
        prompt = build_prompt(entry)

        completion = None
        for attempt in range(4):
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                    # Headroom for reasoning models; the visible JSON is tiny but
                    # thinking tokens count against this budget.
                    max_tokens=max_tokens,
                    extra_body={
                        "provider": {
                            "allow_fallbacks": True,
                            "order": ["deepinfra", "parasail", "novita"],
                            "data_collection": "allow",
                        }
                    },
                )
                break
            except Exception as e:
                if "429" in str(e) and attempt < 3:
                    wait = [30, 60, 90][attempt]
                    print(f"  rate limited, waiting {wait}s... (attempt {attempt + 1}/4)")
                    time.sleep(wait)
                else:
                    print(f"  API error, recording sentinel: {e}")
                    break

        if completion is None:
            responses.append(SENTINEL)
            n_api_fail += 1
            continue

        try:
            content = completion.choices[0].message.content
            if content is None or not content.strip():
                # Empty content usually means the output was truncated before any
                # visible tokens (finish_reason='length') -- flag it loudly.
                fr = completion.choices[0].finish_reason
                print(f"  empty content (finish_reason={fr}); recording sentinel")
                responses.append(SENTINEL)
                n_parse_fail += 1
                continue
            predicted = extract_answer(content)
            if predicted is None:
                print(f"  could not parse answer from: {content[:80]!r}")
                responses.append(SENTINEL)
                n_parse_fail += 1
            else:
                responses.append(predicted)
        except Exception as e:
            print(f"  error extracting label: {e}")
            responses.append(SENTINEL)
            n_parse_fail += 1

    elapsed = time.time() - start
    n = len(responses)
    if n:
        print(f"  done. {elapsed / 60:.2f} min | {elapsed / n:.3f} s/instance "
              f"| api_fail={n_api_fail} parse_fail={n_parse_fail} "
              f"({(n_api_fail + n_parse_fail) / n:.1%} sentinel)")
    else:
        print(f"  done. {elapsed / 60:.2f} min | 0 instances")

    out_path.write_text(json.dumps({
        "system": model,
        "predictions": [{"train": "NA (zero-shot)", "test": dataset, "predictions": responses}],
    }))
    print(f"  saved: {out_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS,
                        help="OpenRouter model ids (default: curated list).")
    parser.add_argument("--datasets", nargs="+", default=DEFAULT_DATASETS,
                        help="Dataset stems matching data/<stem>.tsv (default: all).")
    parser.add_argument("--force", action="store_true",
                        help="Regenerate even if a submission already exists.")
    parser.add_argument("--keep-failed", action="store_true",
                        help="Do not auto-purge/regenerate mostly-sentinel submissions.")
    parser.add_argument("--fail-ratio", type=float, default=0.9,
                        help="Sentinel fraction at/above which a run counts as failed.")
    parser.add_argument("--max-tokens", type=int, default=4096,
                        help="max_tokens per request (headroom for reasoning models).")
    args = parser.parse_args()

    client = build_client()
    for model in args.models:
        for dataset in args.datasets:
            print(f"\n=== {model} | {dataset} ===")
            predict(client, dataset, model, force=args.force,
                    keep_failed=args.keep_failed, fail_ratio=args.fail_ratio,
                    max_tokens=args.max_tokens)


if __name__ == "__main__":
    main()