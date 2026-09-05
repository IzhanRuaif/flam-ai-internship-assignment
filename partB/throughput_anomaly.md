\# Part B2 — Throughput Anomaly



\## Observation



At prompt\_len=3584 (near max\_model\_len=4096), reported throughput

does not scale linearly with batch size as REPORT\_v0.md claims.

Instead, it peaks at batch 24 and declines as batch size increases

further:



| batch | kv\_cache\_util | preempted\_seqs | reported\_tok\_s |

|---|---|---|---|

| 4  | 0.16 | 0  | 565.4  |

| 8  | 0.31 | 0  | 902.6  |

| 16 | 0.62 | 0  | 1311.4 |

| 24 | 0.93 | 0  | \*\*1607.4 (peak)\*\* |

| 32 | 0.97 | 7  | 1384.0 |

| 48 | 0.97 | 23 | 1298.5 |



REPORT\_v0.md's claim -- "assume \~1600 tok/s per L4 (best observed)

and scale linearly with batch size, so batch 48 should give us

\~3200 tok/s" -- is directly contradicted by the actual data. The

real batch-48 throughput (1298.5 tok/s) is lower than even batch 16

(1311.4 tok/s), not double the peak.



\## Mechanism



`kv\_cache\_util` crosses 0.9 at batch 24 and caps near its ceiling

(0.97) from batch 32 onward. At that point `preempted\_seqs` becomes

nonzero (7 at batch 32, 23 at batch 48): the scheduler is evicting

in-progress sequences from the KV cache to free space for others.

A preempted sequence's KV cache must be recomputed from scratch when

it resumes, consuming compute without producing new output tokens.



This explains the throughput drop: as batch size increases past the

point of KV cache saturation, an increasing share of total compute

goes to wasted recomputation rather than generating new tokens, so

\*reported\* throughput (which appears to count total tokens generated

over wall time) falls even though the GPU is fully occupied.



This is also visible in `e2e\_ms\_p95`, which grows far faster than

proportionally with batch size once preemption begins: from batch 24

to batch 48 (2x the batch size), e2e p95 latency grows from 69,221 ms

to 105,427 ms (1.52x) while throughput \*drops\* -- consistent with

requests spending time being repeatedly preempted and re-processed

rather than simply queueing.



\## Recommended change



Cap batch size at 24 for prompt\_len \~3584 (near max context length),

rather than allowing it to scale to 32 or 48. This is the last batch

size before kv\_cache\_util exceeds \~0.9 and preemption begins.



\*\*Quantitative prediction:\*\* capping batch size at 24 should sustain

throughput at approximately 1607 tok/s for long-context requests,

compared to the 1298.5 tok/s actually observed at batch 48 in the

current configuration -- an approximately 24% throughput improvement

by \*reducing\* concurrency, the opposite of the original report's

recommendation to increase batch size.



\## Caveat



This analysis is based on `reported\_tok\_s` as given in the harness

output; Part B3 examines whether this column itself is measuring

the right thing (completed useful output vs. total including wasted

preemption recompute).

