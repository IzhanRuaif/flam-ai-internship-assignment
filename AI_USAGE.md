# AI Usage

## Where AI helped

- Helped structure the overall project workflow (folder layout, phase sequencing, commit strategy) before any coding began.
- Helped write boilerplate/scaffolding code for each script (prepare_corpus.py, fertility audit experiments, tokenizer comparison, KV-cache calculations, goodput analysis).
- Helped formulate testable hypotheses for the fertility.py audit (Part A2) before running any experiment -- e.g. predicting that lowercasing would asymmetrically affect English vs Hindi due to case sensitivity, which was then verified experimentally.
- Helped derive the KV-cache capacity formula (Part B1) and explained the reasoning step by step before implementing it in code.
- Helped debug environment/tooling issues along the way: a gated Hugging Face dataset requiring authentication, a broken local ZIP extraction that produced 0-byte starter kit files, and a stray duplicate NOTEBOOK.md created in the wrong directory.
- Helped draft the written deliverables (audit_results.md, results_interpretation.md, corrected_report_section.md, recommendation memos, this file) based on actual script output.

## Where I verified independently

- Every reported number in this submission (corpus stats, audit experiment results, tokenizer fertility figures, KV-cache calculations, goodput figures) was produced by running the actual scripts in this repository on my own machine and pasting the real terminal output back for interpretation -- no numbers were invented or assumed.
- I ran every script myself in PowerShell and confirmed outputs matched expectations (or investigated when they didn't) before any conclusion was written down.
- I manually inspected the generated corpus CSV to confirm correct script rendering (Tamil/Kannada text, alignment across languages).
- I verified `random.seed(1337)` in fertility.py was genuinely dead code via a direct grep search, rather than accepting the suspicious-looking line at face value.
- I independently confirmed the git/GitHub setup and pushed every commit myself, resolving issues (missing commits, wrong working directory, gated dataset auth) as they came up rather than having them silently fixed for me.

## Where AI was misleading or required correction

- An initial synthetic example for the aggregation-bias experiment (Part A2) was designed to expose mean-of-ratios vs sum/sum bias but failed to do so (0.00% difference), because it varied line length rather than per-line ratio variance. This was documented honestly in NOTEBOOK.md as a revision rather than discarded or hidden, and the real corpus data was used instead to confirm the bias.
- Early file-sharing attempts (uploading the starter kit folder and individual bench/corpus_sample folders) failed silently, producing empty files. This required explicit debugging (checking file sizes and types) before real content could be extracted and used, rather than proceeding on the assumption the first upload had worked.