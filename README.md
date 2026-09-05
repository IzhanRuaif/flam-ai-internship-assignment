\# FlamAI AI Intern Assignment



\## Overview



This repository audits and corrects a set of tokenizer efficiency

and LLM serving capacity claims from a draft internal report

(`starter kit/REPORT\_v0.md`). Part A builds a 1,000-sentence

multilingual parallel corpus, audits a flawed fertility-measurement

script, and shows that tokenizer choice -- not language/script --

is the dominant driver of cross-language tokenization cost. Part B

reconciles theoretical GPU KV-cache capacity against observed

benchmark behavior and identifies a metric-definition bug that

caused the original report to badly overstate serving throughput.

Part C is a resource-constrained decision memo recommending an

approach for making model outputs more casual/conversational.



\## Repository Structure



partA/

prepare\_corpus.py -- builds the 1,000-sentence FLORES corpus

corpus\_stats.py -- corpus statistics

corpus\_documentation.md -- corpus methodology \& limitations

data/flores\_parallel\_1000.csv

audit/ -- Part A2: fertility.py bug audit experiments

audit\_results.md

corrected\_analysis/ -- Part A3: corrected tokenizer comparison

recommendation\_memo.md -- Part A4: 1-page memo



partB/

calculations.md -- Part B1: KV-cache capacity math

calculate\_capacity.py

bench\_log.csv

analyze\_bench.py -- Part B2: throughput anomaly analysis

throughput\_anomaly.md

correct\_goodput.py -- Part B3: goodput correction

goodput\_crosscheck.py

corrected\_report\_section.md

b4\_confirming\_metric.md -- Part B4: production confirming metric



partC/

memo.md -- decision memo (SFT vs rewriter vs prompt eng)



NOTEBOOK.md -- chronological lab notebook (hypotheses, results, revisions)

AI\_USAGE.md -- accounting of AI assistance and independent verification

requirements.txt





\## Setup



```bash

python -m venv .venv

.venv\\Scripts\\Activate.ps1        # Windows

pip install -r requirements.txt

```



Some scripts require a Hugging Face account and access token, since

the FLORES-200 dataset is gated:



```bash

hf auth login

```



Accept the dataset terms at https://huggingface.co/datasets/facebook/flores

before running `prepare\_corpus.py`.



\## Reproducing Results



```bash

python partA/prepare\_corpus.py

python partA/corpus\_stats.py

python partA/audit/experiment\_01\_whitespace.py

python partA/audit/experiment\_02\_aggregation.py

python partA/audit/experiment\_03\_lowercasing.py

python partA/audit/corrected\_fertility.py

python partA/corrected\_analysis/evaluate\_tokenizers.py

python partB/calculate\_capacity.py

python partB/analyze\_bench.py

python partB/correct\_goodput.py

python partB/goodput\_crosscheck.py

```



\## Part A Summary



Audited `fertility.py` and confirmed three methodological bugs

(non-robust whitespace splitting, biased mean-of-ratios aggregation,

an asymmetric lowercasing confound). Corrected Hindi/English

fertility ratio: 6.11x (vs the original report's 5.89x -- similar

magnitude, but for the wrong reasons). At scale, on the full

1,000-sentence corpus, GPT-2 shows extreme fertility for Tamil and

Kannada (20-25x English) -- far worse than the Hindi gap the

original report measured. Switching to a multilingual tokenizer

(xlm-roberta-base) cuts this to \~2.5x, proving the gap is a property

of the tokenizer, not the script, contradicting the original

report's stated conclusion.



\## Part B Summary



Derived theoretical KV-cache capacity (\~28.93 concurrent sequences

at 4096-token context) and reconciled it against observed benchmark

saturation (batch 24-32). Found the benchmark's `reported\_tok\_s`

column counts prompt (prefill) tokens as generated output, inflating

throughput by a constant 3x-8x factor depending on prompt length --

directly explaining the original report's incorrect "longer prompts

= better GPU utilization" claim. True goodput peaks at batch 24 and

declines afterward due to KV-cache saturation and preemption, the

opposite of the original report's linear-scaling recommendation.



\## Part C Summary



Recommended prompt engineering over SFT or a rewriter model, given

that reviewer bandwidth (not compute) is the binding constraint

under the stated resources. Includes explicit success metric, kill

criterion, and Day 1 experiment plan.



\## Key Findings



1\. Tokenizer choice, not language script, is the dominant factor in

&#x20;  cross-language tokenization cost (Part A3).

2\. The original report's throughput metric silently counted prefill

&#x20;  tokens as generated output, inflating results by 3-8x (Part B3).

3\. True serving throughput peaks at batch 24 and declines past it

&#x20;  due to KV-cache saturation -- contradicting the original report's

&#x20;  recommendation to increase batch size (Part B2/B3).



\## Limitations



\- The FLORES corpus is professionally translated benchmark text and

&#x20; does not represent conversational, code-mixed, or informal

&#x20; production traffic.

\- The grapheme-cluster metric in Part A3 is an approximation

&#x20; (NFC-normalized codepoint count), not a true Unicode grapheme

&#x20; cluster count.

\- KV-cache capacity assumptions (non-KV overhead) in Part B1 are

&#x20; stated as estimates in `model\_spec.md`, not measured values.

