# Part B4 — Confirming Metric

## Metric

**`preempted_seqs`, tracked continuously in production as a rate (preemption events per unit time, or preempted sequences as a fraction of total in-flight sequences), alongside `kv_cache_util`.** These are not invented metrics -- both are columns already exposed by the benchmarking harness in `bench_log.csv`, per the column notes in `model_spec.md`. The B4 ask is to monitor these two existing counters continuously in production rather than only in offline benchmark runs, since they are the most direct, already-instrumented signals available from the described serving setup.

## Expected value

Near zero preemption rate at concurrency levels where `kv_cache_util` stays below ~0.9 (e.g. batch <=24 in this configuration). Should rise sharply and track closely with the same inflection point already observed between batch 24 and batch 32 in `bench_log.csv` (kv_cache_util crossing ~0.9, preempted_seqs going from 0 to 7 to 23).

## Why it confirms the hypothesis

Part B2/B3 concluded that the throughput collapse at batch 32/48 coincides with KV-cache saturation and rising preemption counts. If this mechanism holds in production, live `preempted_seqs` and `kv_cache_util` should rise together and track inversely with delivered goodput, at the same concurrency threshold identified in the offline benchmark. If, instead, goodput dropped in production while `preempted_seqs` stayed near zero, that would point to a different cause (e.g. scheduler queuing overhead unrelated to KV eviction, or a client-side bottleneck), and the B2/B3 mechanism would need revision. Using metrics already exposed by the harness, rather than proposing a new unverified counter, keeps this confirmation grounded in what the described serving setup can actually report.