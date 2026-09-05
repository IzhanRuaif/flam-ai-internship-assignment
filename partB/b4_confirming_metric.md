\# Part B4 — Confirming Metric



\## Metric



\*\*KV-cache preemption recompute rate\*\*: the number of tokens

re-processed due to preempted sequences resuming, as a fraction of

total tokens processed, tracked per unit time (or per batch/request

cohort) in the production serving stack.



\## Expected value



Near zero at batch sizes where kv\_cache\_util stays below \~0.9 (e.g.

batch <=24 in this configuration). Should rise sharply and track

closely with `preempted\_seqs` once kv\_cache\_util approaches its

ceiling (\~0.97) -- i.e., the same inflection point already observed

between batch 24 and batch 32 in bench\_log.csv.



\## Why it confirms the hypothesis



Part B2/B3 concluded that the throughput collapse at batch 32/48 is

caused by preempted sequences being evicted and recomputed, wasting

compute without producing new output tokens. If this mechanism is

correct, a direct measurement of recompute volume should rise in

lockstep with `preempted\_seqs` and inversely with true goodput. If,

instead, recompute rate stayed flat while throughput still dropped,

that would point to a different cause (e.g. scheduler queuing

overhead unrelated to KV eviction), and the B2/B3 conclusion would

need revision. This metric is the most direct possible confirmation

because it measures the proposed mechanism itself, not just its

downstream symptoms (throughput, latency) which could plausibly

have other explanations.

