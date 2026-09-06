# Part B2 — Throughput Anomaly

## Observation

At prompt_len=3584 (near max_model_len=4096), reported throughput does not scale linearly with batch size as REPORT_v0.md claims. Instead, it peaks at batch 24 and declines as batch size increases further:

| batch | kv_cache_util | preempted_seqs | reported_tok_s |
|---|---|---|---|
| 4  | 0.16 | 0  | 565.4  |
| 8  | 0.31 | 0  | 902.6  |
| 16 | 0.62 | 0  | 1311.4 |
| 24 | 0.93 | 0  | **1607.4 (peak)** |
| 32 | 0.97 | 7  | 1384.0 |
| 48 | 0.97 | 23 | 1298.5 |

REPORT_v0.md's claim -- "assume ~1600 tok/s per L4 (best observed) and scale linearly with batch size, so batch 48 should give us ~3200 tok/s" -- is directly contradicted by the actual data. The real batch-48 throughput (1298.5 tok/s) is lower than even batch 16 (1311.4 tok/s), not double the peak.

## Mechanism

`kv_cache_util` crosses 0.9 at batch 24 and caps near its ceiling (0.97) from batch 32 onward. At that point `preempted_seqs` becomes nonzero (7 at batch 32, 23 at batch 48): the scheduler is evicting in-progress sequences from the KV cache to free space for others. `model_spec.md` and the starter kit do not document the serving stack's exact preemption-recovery mechanism, so the precise recovery cost cannot be confirmed from the provided materials; conservatively, preemption requires at minimum additional recomputation or restoration work before an evicted sequence continues, consuming serving resources without producing new output tokens in the meantime.

This is consistent with the throughput drop: as batch size increases past the point of KV cache saturation, wall-clock goodput (completed_output_tokens / wall_clock_s, see Part B3) falls even though the GPU is fully occupied, suggesting an increasing share of total compute is spent on preemption-related overhead rather than generating new tokens. Note that `reported_tok_s` itself is examined separately in Part B3 and should not be assumed to directly measure generated-token throughput (see Caveat below).

This is also visible in `e2e_ms_p95`, which grows far faster than proportionally with batch size once preemption begins: from batch 24 to batch 48 (2x the batch size), e2e p95 latency grows from 69,221 ms to 105,427 ms (1.52x) while throughput *drops* -- consistent with requests spending time being repeatedly preempted and re-processed rather than simply queueing.

## Recommended change

Cap batch size at 24 for prompt_len ~3584 (near max context length), rather than allowing it to scale to 32 or 48. This is the last batch size before kv_cache_util exceeds ~0.9 and preemption begins.

**Quantitative prediction:** capping batch size at 24 should sustain throughput at approximately 1607 tok/s for long-context requests, compared to the 1298.5 tok/s actually observed at batch 48 in the current configuration -- an approximately 24% throughput improvement by