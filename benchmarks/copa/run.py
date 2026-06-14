#!/usr/bin/env python3
"""Run DIALECT-COPA inference against OpenRouter models.

For every (model, dataset) pair this queries the model once per example with a
zero-shot, JSON-only prompt and writes a submission file to ``submissions/``:

    submissions/submission-<model-short>-<dataset>.json

The COPA prompt asks which of two hypotheses is the more plausible cause/effect
of a premise; the model answers 1 or 2 and we store it 0-indexed (answer-1) to
match the gold ``label`` field. Existing submissions are skipped, so the script
is safe to re-run and resume.

Usage examples
--------------
    python run.py                                   # curated models, all datasets
    python run.py --models openai/gpt-5 --datasets copa-sr copa-sr-tor
    python run.py --force                            # clean re-run of everything

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

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
SUBMISSIONS_DIR = HERE / "submissions"

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

# Dataset stems matching the *-test.jsonl files in data/.
DEFAULT_DATASETS = [
    "copa-en",
    "copa-sl",
    "copa-hr",
    "copa-hr-ckm",
    "copa-mk",
    "copa-sl-cer",
    "copa-sr",
    "copa-sr-tor",
    "copa-sl-prl",
]


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


def get_completion(client: OpenAI, model: str, prompt: str, retries: int = 3):
    """Request a JSON-object completion with exponential backoff."""
    for attempt in range(retries):
        try:
            completion = client.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            choice = completion.choices[0] if completion.choices else None
            content = choice.message.content if choice else None
            if content:
                return content
            reason = getattr(choice, "finish_reason", None) if choice else None
            err = getattr(completion, "error", None)
            print(f"  empty response (finish_reason={reason}, error={err}), "
                  f"retry {attempt + 1}/{retries}")
        except Exception as e:
            print(f"  request failed: {e}, retry {attempt + 1}/{retries}")
        time.sleep(2 ** attempt)
    return None


def build_prompt(entry, dataset: str) -> str:
    if dataset == "copa-en":
        prompt = (
            "You will be given a task. The task definition is in English, "
            "as is the task itself. Here is the task!\n"
            f'Given the premise "{entry["premise"]}",'
        )
    else:
        prompt = (
            "You will be given a task. The task definition is in English, "
            "but the task itself is in another language. Here is the task!\n"
            f'Given the premise "{entry["premise"]}",'
        )

    if entry["question"] == "cause":
        prompt += " and that we are looking for the cause of this premise,"
    else:
        prompt += " and that we are looking for the result of this premise, "

    prompt += (
        "which hypothesis is more plausible?\n"
        f'Hypothesis 1: "{entry["choice1"]}".\n'
        f'Hypothesis 2: "{entry["choice2"]}".\n\n'
        "### Output format\n"
        "Return a valid JSON dictionary with the following key: 'answer' "
        "and a value should be an integer -- either 1 (if hypothesis 1 is "
        "more plausible) or 2 (if hypothesis 2 is more plausible)."
    )
    return prompt


def predict(client: OpenAI, dataset: str, model: str, *, force: bool) -> None:
    SUBMISSIONS_DIR.mkdir(exist_ok=True)
    model_short = model.split("/")[-1]
    out_path = SUBMISSIONS_DIR / f"submission-{model_short}-{dataset}.json"

    if out_path.exists() and not force:
        print(f"  skipping (already exists): {out_path.name}")
        return

    data_path = DATA_DIR / f"{dataset}-test.jsonl"
    if not data_path.exists():
        print(f"  WARNING: missing {data_path}, skipping.")
        return

    responses = []
    start = time.time()
    for line in open(data_path):
        line = line.strip()
        if not line:
            continue
        entry = json.loads(line)
        prompt = build_prompt(entry, dataset)

        raw = get_completion(client, model, prompt)
        if raw is None:
            print(f"  instance {len(responses)}: no usable output, defaulting to 0")
            responses.append(0)
            continue

        match = re.search(r'"?\'?answer"?\'?\s*:\s*([12])', raw)
        if match:
            responses.append(int(match.group(1)) - 1)  # store 0-indexed
        else:
            print(f"  could not parse answer from: {raw[:120]!r}")
            responses.append(0)

    elapsed = time.time() - start
    n = len(responses)
    if n:
        print(f"  done. {elapsed / 60:.2f} min for {n} instances "
              f"— {elapsed / n:.3f} s/instance.")
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
                        help="Dataset stems matching data/<stem>-test.jsonl (default: all).")
    parser.add_argument("--force", action="store_true",
                        help="Regenerate even if a submission already exists.")
    args = parser.parse_args()

    client = build_client()
    for model in args.models:
        for dataset in args.datasets:
            print(f"\n=== {model} | {dataset} ===")
            predict(client, dataset, model, force=args.force)


if __name__ == "__main__":
    main()