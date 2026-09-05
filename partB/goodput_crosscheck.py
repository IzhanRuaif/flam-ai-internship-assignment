"""
Part B3 -- Independent cross-check of goodput using itl_ms_p50
(median inter-token latency during decode), which is computed
differently from wall_clock_s/gen_len and doesn't depend on
whether reported_tok_s counts prefill tokens.
"""

import csv
from pathlib import Path

BENCH_PATH = Path("partB/bench_log.csv")


def load_bench():
    rows = []
    with open(BENCH_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def main():
    rows = load_bench()

    print(f"{'batch':<7}{'prompt_len':<12}{'goodput(M1)':<14}"
          f"{'itl_estimate(M2)':<18}{'preempted':<10}")
    print("-" * 70)

    for r in rows:
        num_requests = int(r["num_requests"])
        gen_len = int(r["gen_len"])
        wall_clock_s = float(r["wall_clock_s"])
        batch_size = int(r["batch_size"])
        itl_ms = float(r["itl_ms_p50"])

        goodput_m1 = (num_requests * gen_len) / wall_clock_s
        # decode throughput estimate: batch_size sequences, each producing
        # one token per itl_ms_p50 milliseconds, decoded in parallel
        itl_estimate_m2 = batch_size / (itl_ms / 1000)

        print(f"{r['batch_size']:<7}{r['prompt_len']:<12}{goodput_m1:<14.1f}"
              f"{itl_estimate_m2:<18.1f}{r['preempted_seqs']:<10}")


if __name__ == "__main__":
    main()