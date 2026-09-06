# Part B3 — Correcting the Serving Throughput Section

## What REPORT_v0.md got wrong

REPORT_v0.md's Section 2 reads `reported_tok_s` from the harness at face value and concludes "longer prompts clearly give better GPU utilization" and recommends packing more context per request. This is incorrect on two independent grounds, both confirmed below.

## Issue 1: reported_tok_s is total processed-token throughput, misread as generation throughput

Every row's `reported_tok_s` is exactly explained by:

reported_tok_s = (prompt_len + gen_len) x num_requests / wall_clock_s

This is confirmed by an exact, constant ratio to true goodput (completed output tokens / wall time) across every row: +200% (3x) for prompt_len=512 rows and +700% (8x) for prompt_len=3584 rows -- matching (prompt_len+gen_len)/gen_len exactly in both cases (768/256=3, 4096/512=8). This ratio is exact and constant across every batch size, which indicates `reported_tok_s` is internally consistent as a definition -- it appears to be total processed-token throughput (prefill + decode combined), not a broken or inconsistent counter. The error is in REPORT_v0.md's interpretation: it reads this column as generated-token goodput. Prefill tokens are processed once, in parallel, in a single forward pass -- far cheaper per-token than autoregressive decode -- so a metric that counts them alongside generated tokens makes long-prompt requests look artificially fast when read as a generation-speed indicator. This misinterpretation is the direct cause of the report's incorrect "longer prompts = better utilization" conclusion.

## Issue 2: a median-based latency metric does not surface preemption's effect on goodput

An independent cross-check using itl_ms_p50 (median inter-token latency) as a decode-rate estimate confirms true goodput (completed_output_tokens / wall_clock_s) is the more appropriate capacity-planning metric here, and reveals a second issue: at batch 32 and 48, where preempted_seqs is nonzero (7 and 23), the median-based ITL estimate keeps climbing (249.8 -> 314.4 -> 480.0) while true wall-clock goodput collapses (200.9 -> 173.0 -> 162.3). Because itl_ms_p50 is a median, it reflects the "typical" token's decode latency for sequences that are progressing normally, and does not by itself surface the effect of preempted sequences on overall delivered throughput. A capacity-planning decision based on itl_ms_p50 alone would miss the real throughput collapse visible in wall-clock goodput once preemption begins.

## Corrected goodput table

| batch | prompt_len | reported_tok_s | true goodput | preempted |
|---|---|---|---|---|
| 16 | 3584 | 1311.4 | 163.9 | 0 |
| 24 | 3584 | 1607.4 | 200.9 | 0 |
| 32 | 3584 | 1384.0 | 173.0 | 7 |
| 48 | 3584 | 1298.5 | 162.3 | 23 |

True goodput (the number that should have gone in the deck) also peaks at batch 24 and declines afterward -- confirming Part B2's conclusion (cap batch size at 24 for long-context requests) using a metric that isolates generated output tokens, independent of the prefill-vs-generation interpretation issue above.

## What the report should have concluded

1. reported_tok_s should not be read as a generation-throughput capacity-planning metric as REPORT_v0.md uses it; it appears to measure total processed tokens (prefill + generated), which inflates apparent generation speed when prompts are long.
2. Longer prompts do not give "better GPU utilization" in any generation-throughput sense -- the apparent improvement is an artifact of counting cheap prefill tokens in the same numerator as generated tokens.
3. True (goodput-based) throughput still peaks at batch 24 for