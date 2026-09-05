# Part B1 — KV-Cache Capacity Calculation

## Model & hardware inputs (from model_spec.md)

- Layers: 28
- KV heads (GQA): 8
- Head dimension: 128
- KV cache precision: fp16 (2 bytes/value)
- Model parameters: 4.2B, fp16 weights (2 bytes/param)
- GPU: 1× NVIDIA L4, 24 GB
- `gpu_memory_utilization`: 0.92
- Non-KV runtime overhead: assumed ~1.6 GB
- `max_model_len`: 4096

## Step 1: KV bytes per token

KV bytes/token = layers × KV_heads × head_dim × 2 (K and V) × 2 bytes (fp16)
= 28 × 8 × 128 × 2 × 2
= 114,688 bytes/token (112.00 KiB/token)


## Step 2: Available memory for KV cache

usable GPU memory = 24 GiB × 0.92 = 22.080 GiB
model weights = 4.2B params × 2 bytes = 7.823 GiB
non-KV overhead = 1.600 GiB

available for KV cache = 22.080 - 7.823 - 1.600 = 12.657 GiB


## Step 3: Max concurrent sequences at max_model_len (4096 tokens)

KV bytes per 4096-token sequence = 114,688 × 4096 = 469,762,048 bytes (0.4375 GiB)

max sequences = 12.657 GiB / 0.4375 GiB ≈ 28.93 (floor: 28)


## Result

**Theoretical max concurrent sequences at full 4096-token context: ~28.93 (28 whole sequences).**

Computed via `partB/calculate_capacity.py`, output matches this derivation exactly (28.93, floor 28).

## Reconciliation against observed behavior (bench_log.csv)

At `prompt_len=3584, gen_len=512` (total 4096 tokens per sequence,
matching `max_model_len`):

| batch_size | kv_cache_util | preempted_seqs |
|---|---|---|
| 16 | 0.62 | 0 |
| 24 | 0.93 | 0 |
| 32 | 0.97 | 7 |
| 48 | 0.97 | 23 |

Observed KV saturation (util crossing 0.9, preemption beginning)
occurs between batch 24 and batch 32 — reasonably close to the
theoretical ~28.93 sequence ceiling, not wildly divergent. The
remaining small gap is plausibly explained by:

1. **Page-level allocation fragmentation** — KV cache is typically
   allocated in fixed-size blocks/pages, not exact byte counts, so
   real usable capacity rounds down below the raw theoretical
   division.
2. **Overhead is an assumption, not a measurement** — `model_spec.md`
   states non-KV overhead as "assume ~1.6 GB," not a measured value.
   Actual activation/CUDA-graph memory at 24-32 concurrent sequences
   may exceed this flat assumption, reducing real available KV
   memory below what was calculated.
3. **GB vs GiB ambiguity** — `gpu_memory_utilization` could be
   applied against decimal GB (10^9) or binary GiB (2^30) depending
   on the serving framework's convention, which shifts the
   theoretical number by ~7%.

Full mechanism analysis of *why* throughput itself drops once
preemption begins is in `partB/throughput_anomaly.md` (Part B2).