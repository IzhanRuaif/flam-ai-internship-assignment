"""
Part B3 -- Compute honest goodput and compare to reported_tok_s,
using only the least ambiguous columns: num_requests, gen_len,
wall_clock_s (Method 1), cross-checked against reported_tok_s
(Method 2, the harness's own counter).
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

    print(f"{'batch':<7}{'prompt_len':<12}{'reported_tok_s':<16}"
          f"{'goodput':<12}{'diff':<10}{'diff_%':<10}{'preempted':<10}")
    print("-" * 90)

    for r in rows:
        num_requests = int(r["num_requests"])
        gen_len = int(r["gen_len"])
        wall_clock_s = float(r["wall_clock_s"])
        reported = float(r["reported_tok_s"])

        completed_output_tokens = num_requests * gen_len
        goodput = completed_output_tokens / wall_clock_s

        diff = reported - goodput
        diff_pct = (diff / goodput) * 100 if goodput else 0

        print(f"{r['batch_size']:<7}{r['prompt_len']:<12}{reported:<16.1f}"
              f"{goodput:<12.1f}{diff:<+10.1f}{diff_pct:<+9.2f}%{r['preempted_seqs']:<10}")


if __name__ == "__main__":
    main()