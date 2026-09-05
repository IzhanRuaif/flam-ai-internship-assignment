"""
Experiment 1: Does `line.split(" ")` (original) vs `line.split()`
(robust) change the word count denominator on the real corpus?
"""

from pathlib import Path

ENG_PATH = Path("partA/starter_kit_copy/eng_sample.txt")
HIN_PATH = Path("partA/starter_kit_copy/hin_sample.txt")


def load_raw_lines(path):
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if line:
                lines.append(line)
    return lines


def compare_split_methods(lines, label):
    print(f"\n{label}")
    print("-" * 70)
    total_diff = 0
    for i, line in enumerate(lines):
        original_split = line.split(" ")       # buggy: literal single space
        robust_split = line.split()            # robust: any whitespace run
        if len(original_split) != len(robust_split):
            diff = len(original_split) - len(robust_split)
            total_diff += diff
            print(f"Line {i}: original_split={len(original_split)} "
                  f"robust_split={len(robust_split)} diff={diff}")
            print(f"  -> {line!r}")
    print(f"\nTotal lines affected: word-count discrepancy sum = {total_diff}")


def main():
    eng_lines = load_raw_lines(ENG_PATH)
    hin_lines = load_raw_lines(HIN_PATH)

    compare_split_methods(eng_lines, "ENGLISH")
    compare_split_methods(hin_lines, "HINDI")


if __name__ == "__main__":
    main()