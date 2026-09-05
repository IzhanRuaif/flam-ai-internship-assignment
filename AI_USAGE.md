\# AI Usage



\## Where AI helped



\- Helped structure the overall project workflow (folder layout,

&#x20; phase sequencing, commit strategy) before any coding began.

\- Helped write boilerplate/scaffolding code for each script

&#x20; (prepare\_corpus.py, fertility audit experiments, tokenizer

&#x20; comparison, KV-cache calculations, goodput analysis).

\- Helped formulate testable hypotheses for the fertility.py audit

&#x20; (Part A2) before running any experiment -- e.g. predicting that

&#x20; lowercasing would asymmetrically affect English vs Hindi due to

&#x20; case sensitivity, which was then verified experimentally.

\- Helped derive the KV-cache capacity formula (Part B1) and explained

&#x20; the reasoning step by step before implementing it in code.

\- Helped debug environment/tooling issues along the way: a gated

&#x20; Hugging Face dataset requiring authentication, a broken local ZIP

&#x20; extraction that produced 0-byte starter kit files, and a stray

&#x20; duplicate NOTEBOOK.md created in the wrong directory.

\- Helped draft the written deliverables (audit\_results.md,

&#x20; results\_interpretation.md, corrected\_report\_section.md,

&#x20; recommendation memos, this file) based on actual script output.



\## Where I verified independently



\- Every reported number in this submission (corpus stats, audit

&#x20; experiment results, tokenizer fertility figures, KV-cache

&#x20; calculations, goodput figures) was produced by running the actual

&#x20; scripts in this repository on my own machine and pasting the real

&#x20; terminal output back for interpretation -- no numbers were

&#x20; invented or assumed.

\- I ran every script myself in PowerShell and confirmed outputs

&#x20; matched expectations (or investigated when they didn't) before any

&#x20; conclusion was written down.

\- I manually inspected the generated corpus CSV to confirm correct

&#x20; script rendering (Tamil/Kannada text, alignment across languages).

\- I verified `random.seed(1337)` in fertility.py was genuinely dead

&#x20; code via a direct grep search, rather than accepting the

&#x20; suspicious-looking line at face value.

\- I independently confirmed the git/GitHub setup and pushed every

&#x20; commit myself, resolving issues (missing commits, wrong working

&#x20; directory, gated dataset auth) as they came up rather than having

&#x20; them silently fixed for me.



\## Where AI was misleading or required correction



\- An initial synthetic example for the aggregation-bias experiment

&#x20; (Part A2) was designed to expose mean-of-ratios vs sum/sum bias

&#x20; but failed to do so (0.00% difference), because it varied line

&#x20; length rather than per-line ratio variance. This was documented

&#x20; honestly in NOTEBOOK.md as a revision rather than discarded or

&#x20; hidden, and the real corpus data was used instead to confirm the

&#x20; bias.

\- Early file-sharing attempts (uploading the starter kit folder and

&#x20; individual bench/corpus\_sample folders) failed silently, producing

&#x20; empty files. This required explicit debugging (checking file sizes

&#x20; and types) before real content could be extracted and used, rather

&#x20; than proceeding on the assumption the first upload had worked.

