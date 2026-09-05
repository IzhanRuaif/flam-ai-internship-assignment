# Part B3 — Correcting the Serving Throughput Section

## What REPORT_v0.md got wrong

REPORT_v0.md's Section 2 reads `reported_tok_s` from the harness at
face value and concludes "longer prompts clearly give better GPU
utilization" and recommends packing more context per request. This
is incorrect on two independent grounds, both confirmed below.

## Bug 1: reported_tok_s counts prefill tokens as generated output

Every row's `reported_tok_s` is exactly explained by:

reported_tok_s = (prompt_len + gen_len) x num_requests / wall_clock_s

This is confirmed by an exact, constant ratio to true goodput
(completed output tokens / wall time) across every row: +200%
(3x) for prompt_len=512 rows and +700% (8x) for prompt_len=3584
rows -- matching (prompt_len+gen_len)/gen_len exactly in both cases
(768/256=3, 4096/512=8). Prefill tokens are processed once, in
parallel, in a single forward pass -- far cheaper per-token than
autoregressive decode -- so counting them as generated throughput
makes long-prompt requests look artificially fast. This is the
direct cause of the report's incorrect "longer prompts = better
utilization" conclusion.

## Bug 2: median-based decode latency hides preemption damage

An independent cross-check using itl_ms_p50 (median inter-token
latency) as a decode-rate estimate confirms true goodput
(completed_output_tokens / wall_clock_s) is the right metric, and
reveals a second issue: at batch 32 and 48, where preempted_seqs is
nonzero (7 and 23), the median-based ITL estimate keeps climbing
(249.8 -> 314.4 -> 480.0) while true wall-clock goodput collapses
(200.9 -> 173.0 -> 162.3). Because itl_ms_p50 is a median, it
reflects the "typical" token's decode latency and does not capture
the repeated stalls and recompute cost experienced by preempted
sequences. Any capacity-planning decision based on itl_ms_p50 alone
would miss the real throughput collapse under preemption.

## Corrected goodput table

| batch | prompt_len | reported_tok_s | true goodput | preempted |
|---|---|---|---|---|
| 16 | 3584 | 1311.4 | 163.9 | 0 |
| 24 | 3584 | 1607.4 | 200.9 | 0 |
| 32 | 3584 | 1384.0 | 173.0 | 7 |
| 48 | 3584 | 1298.5 | 162.3 | 23 |

True goodput (the number that should have gone in the deck) also
peaks at batch 24 and declines afterward -- confirming Part B2's
conclusion (cap batch size at 24 for long-context requests) using a
methodologically sound metric, independent of the prefill-counting
bug.

## What the report should have concluded

1. reported_tok_s is not a valid capacity-planning metric as
   currently defined; it inflates throughput by counting prefill
   tokens as generated output.
2. Longer prompts do not give "better GPU utilization" in any
   generation-throughput sense -- the apparent improvement is an
   artifact of counting cheap prefill tokens in the numerator.
3. True (goodput-based) throughput still peaks at batch 24 for
   long-context requests and declines afterward due to KV-cache
   saturation and preemption (Part B2), confirming batch 24 as the
   correct capacity ceiling under this configuration -- not batch
   48 as the original report implied.