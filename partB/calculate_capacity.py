"""
Part B1 -- KV-cache capacity calculation.

All numbers sourced from model_spec.md. Uses GiB (1024^3 bytes)
consistently to avoid GB/GiB ambiguity, which is flagged as a
possible source of discrepancy between predicted and observed
capacity.
"""

GIB = 1024 ** 3

# --- Model spec (from model_spec.md) ---
LAYERS = 28
KV_HEADS = 8
HEAD_DIM = 128
BYTES_PER_VALUE_FP16 = 2
K_AND_V = 2  # one K vector and one V vector per token per layer

PARAMS = 4.2e9
WEIGHT_BYTES_PER_PARAM = 2  # fp16

# --- Hardware / serving config ---
GPU_TOTAL_GB = 24
GPU_MEM_UTILIZATION = 0.92
NON_KV_OVERHEAD_GB = 1.6
MAX_MODEL_LEN = 4096


def kv_bytes_per_token():
    return LAYERS * KV_HEADS * HEAD_DIM * K_AND_V * BYTES_PER_VALUE_FP16


def available_kv_memory_bytes():
    usable = GPU_TOTAL_GB * GPU_MEM_UTILIZATION * GIB
    weights = PARAMS * WEIGHT_BYTES_PER_PARAM
    overhead = NON_KV_OVERHEAD_GB * GIB
    return usable - weights - overhead


def main():
    kvbpt = kv_bytes_per_token()
    print(f"KV bytes/token: {kvbpt:,} bytes ({kvbpt/1024:.2f} KiB)")

    usable = GPU_TOTAL_GB * GPU_MEM_UTILIZATION * GIB
    weights = PARAMS * WEIGHT_BYTES_PER_PARAM
    overhead = NON_KV_OVERHEAD_GB * GIB
    available = available_kv_memory_bytes()

    print(f"\nUsable GPU memory (24GB x 0.92): {usable/GIB:.3f} GiB")
    print(f"Model weights (4.2B x 2 bytes):   {weights/GIB:.3f} GiB")
    print(f"Non-KV overhead:                  {overhead/GIB:.3f} GiB")
    print(f"Available for KV cache:           {available/GIB:.3f} GiB")

    kv_per_sequence = kvbpt * MAX_MODEL_LEN
    print(f"\nKV bytes per {MAX_MODEL_LEN}-token sequence: "
          f"{kv_per_sequence:,} bytes ({kv_per_sequence/GIB:.4f} GiB)")

    max_sequences = available / kv_per_sequence
    print(f"\nTheoretical max concurrent sequences at "
          f"{MAX_MODEL_LEN} tokens: {max_sequences:.2f} "
          f"(floor: {int(max_sequences)})")


if __name__ == "__main__":
    main()