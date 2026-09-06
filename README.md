# FlamAI AI Intern Assignment

## Overview

This repository audits and corrects a set of tokenizer efficiency and LLM serving capacity claims from a draft internal report (`REPORT_v0.md`). Part A builds a 1,000-sentence multilingual parallel corpus, audits a flawed fertility-measurement script, and shows that tokenizer choice — not language/script — is the dominant driver of cross-language tokenization cost. Part B reconciles theoretical GPU KV-cache capacity against observed benchmark behavior and identifies a metric-definition bug that caused the original report to badly overstate serving throughput. Part C is a resource-constrained decision memo recommending an approach for making model outputs more casual/conversational.

## Repository Structure
partA/
prepare_corpus.py -- builds the 1,000-sentence FLORES corpus
corpus_stats.py -- corpus statistics
corpus_documentation.md -- corpus methodology & limitations
data/flores_parallel_1000.csv
audit/ -- Part A2: fertility.py bug audit experiments
audit_results.md
corrected_analysis/ -- Part A3: corrected tokenizer comparison
recommendation_memo.md -- Part A4: 1-page memo

partB/
calculations.md -- Part B1: KV-cache capacity math
calculate_capacity.py
bench_log.csv
analyze_bench.py -- Part B2: throughput anomaly analysis
throughput_anomaly.md
correct_goodput.py -- Part B3: goodput correction
goodput_crosscheck.py
corrected_report_section.md
b4_confirming_metric.md -- Part B4: production confirming metric

partC/
memo.md -- decision memo (SFT vs rewriter vs prompt eng)

NOTEBOOK.md -- lab notebook (hypotheses, results, revisions, organized by part)
AI_USAGE.md -- accounting of AI assistance and independent verification
requirements.txt

## Setup

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt
```

Some scripts require a Hugging Face account and access token, since the FLORES-200 dataset is gated:

```bash
hf auth login
```

Accept the dataset terms at https://huggingface.co/datasets/facebook/flores before running `prepare_corpus.py`.

## Reproducing Results

```bash
python partA/prepare_corpus.py
python partA/corpus_stats.py
python partA/audit/experiment_01_whitespace.py
python partA/audit/experiment_02_aggregation.py
python partA/audit/experiment_03_lowercasing.py
python partA/audit/corrected_fertility.py
python partA/corrected_analysis/evaluate_tokenizers.py
python partB/calculate_capacity.py
python partB/analyze_bench.py
python partB/correct_goodput.py
python partB/goodput_crosscheck.py
```

All results above have been independently reproduced from a fresh `git clone` and a clean virtual environment, with identical output.

## Part A Summary

Audited `fertility.py` and confirmed three methodological bugs (non-robust whitespace splitting, biased mean-of-ratios aggregation, an asymmetric lowercasing confound). Corrected Hindi/English fertility ratio: 6.11x (vs the original report's 5.89x — similar magnitude, but for the wrong reasons). At scale, on the full 1,000-sentence corpus, GPT-2 shows extreme fertility for Tamil and Kannada (20-25x English) — far worse than the Hindi gap the original report measured. Switching to a multilingual tokenizer (xlm-roberta-base) cuts this to ~2.5x, proving the gap is a property of the tokenizer, not the script, contradicting the original report's stated conclusion.

## Part B Summary

Derived theoretical KV-cache capacity (~28.93 concurrent sequences at 4096-token context) and reconciled it against observed benchmark saturation (batch 24-32). Found the benchmark's `reported_tok_s` column counts prompt (prefill) tokens as generated output, inflating throughput by a constant 3x-8x factor depending on prompt length — directly explaining the original report's incorrect "longer prompts = better GPU utilization" claim. True goodput peaks at batch 24 and declines afterward due to KV-cache saturation and preemption, the opposite of the original report's linear-scaling recommendation.

## Part C Summary

Recommended prompt engineering over SFT or a rewriter model, given that reviewer bandwidth (not compute) is the binding constraint under the stated resources. Includes explicit success metric, kill criterion, and first-experiment plan.

## Key Findings

1. Tokenizer choice, not language script, is the dominant factor in cross-language tokenization cost (Part A3).
2. The original report's throughput metric silently counted prefill tokens as generated output, inflating results by 3-8x (Part B3).
3. True serving throughput peaks at batch 24 and declines past it due to KV-cache saturation — contradicting the original report's recommendation to increase batch size (Part B2/B3).

## Limitations

- The FLORES corpus is professionally translated benchmark text and does not represent conversational, code-mixed, or informal production traffic.
- The grapheme-cluster metric in Part A3 is an approximation (NFC-normalized codepoint count), not a true Unicode grapheme cluster count.
- KV-cache capacity assumptions (non-KV overhead) in Part B1 are stated as estimates in `model_spec.md`, not measured values.