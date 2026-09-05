"""
Part B2 -- Compare theoretical KV-cache capacity (from B1) against
observed behavior in bench_log.csv.
"""

import csv
from pathlib import Path

BENCH_PATH = Path("partB/bench_log.csv")  # copy bench_log.csv here first
THEORETICAL_MAX_SEQUENCES = 28.93  # from calculate_capacity.py


def load_bench():
    rows = []
    with open(BENCH_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def main():
    rows = load_bench()

    # Focus on the long-prompt rows (prompt_len=3584), since these are
    # closest to max_model_len=4096 and where KV pressure is highest.
    long_prompt_rows = [r for r in rows if r["prompt_len"] == "3584"]

    print("LONG-PROMPT ROWS (prompt_len=3584, gen_len=512)")
    print(f"Total tokens per sequence: 3584 + 512 = 4096 (= max_model_len)")
    print("-" * 90)
    print(f"{'batch':<7}{'kv_util':<10}{'preempted':<12}{'reported_tok_s':<16}{'e2e_p95_ms':<12}")
    print("-" * 90)

    for r in long_prompt_rows:
        print(f"{r['batch_size']:<7}{r['kv_cache_util']:<10}{r['preempted_seqs']:<12}"
              f"{r['reported_tok_s']:<16}{r['e2e_ms_p95']:<12}")

    print(f"\nTheoretical max concurrent sequences (from B1): {THEORETICAL_MAX_SEQUENCES:.2f}")

    print("\nObservation:")
    print("KV cache utilization crosses 0.9 at batch 24, and preemption")
    print("(scheduler evicting sequences mid-generation) begins at batch 32,")
    print("where kv_cache_util caps at 0.97. This is reasonably close to")
    print("the theoretical ~28.93 max, given that:")
    print("  - real KV cache blocks are typically allocated in fixed-size")
    print("    pages, so usable capacity rounds down to whole pages")
    print("    (page-level fragmentation reduces effective sequences below")
    print("    the raw byte-division theoretical number)")
    print("  - the model_spec's 1.6 GB non-KV overhead is stated as an")
    print("    assumption ('assume ~1.6 GB'), not measured -- actual")
    print("    activation/CUDA-graph overhead at batch 24-32 concurrent")
    print("    sequences may be higher than the flat assumption, which")
    print("    would reduce real available KV memory further")
    print("  - GB vs GiB unit ambiguity in how gpu_memory_utilization is")
    print("    applied could shift the theoretical number by a few percent")


if __name__ == "__main__":
    main()