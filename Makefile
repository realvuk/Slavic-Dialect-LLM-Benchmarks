.PHONY: help setup run-piqa run-copa eval eval-piqa eval-copa combine viz viz-piqa viz-copa report clean

PYTHON ?= python3

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup:  ## Install Python dependencies
	$(PYTHON) -m pip install -r requirements.txt

# ── Stage 1: run inference (needs OPENROUTER_API_KEY, costs money) ──────────────
run-piqa:  ## Run PIQA inference (curated models x all datasets)
	$(PYTHON) benchmarks/piqa/run.py

run-copa:  ## Run COPA inference (curated models x all datasets)
	$(PYTHON) benchmarks/copa/run.py

# ── Stage 2: evaluate submissions -> results.json + markdown tables ─────────────
eval-piqa:  ## Score PIQA submissions
	$(PYTHON) benchmarks/piqa/evaluate.py

eval-copa:  ## Score COPA submissions
	$(PYTHON) benchmarks/copa/evaluate.py

eval: eval-piqa eval-copa  ## Score both benchmarks

# ── Stage 3: merge with collaborator baselines -> all_results.json ──────────────
combine:  ## Combine new + taja results into all_results.json
	$(PYTHON) combine_results.py

# ── Stage 4: render figures from all_results.json -> results/plots/ ─────────────
viz-piqa:  ## Render PIQA figures
	$(PYTHON) benchmarks/piqa/visualize.py

viz-copa:  ## Render COPA figures
	$(PYTHON) benchmarks/copa/visualize.py

viz: viz-piqa viz-copa  ## Render both benchmarks' figures

# ── Convenience: everything except the (paid) inference stage ───────────────────
report: eval combine viz  ## Re-score, combine, and render figures from existing submissions

clean:  ## Remove generated figures and caches (keeps submissions + results.json)
	rm -f benchmarks/*/results/plots/*.png
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	find . -name '.DS_Store' -delete
