"""
Corrected fertility analysis.

Fixes applied (each independently confirmed via experiments 01-03):
1. line.split() instead of line.split(" ")  -- robust whitespace handling
2. sum(tokens)/sum(words) instead of mean(per-line ratios) -- unbiased aggregation
3. No lowercasing -- avoids asymmetric confound (affects English, not Hindi)

random.seed(1337) intentionally omitted: verified dead code, doesn't
affect anything since tiktoken's gpt2 encoding is deterministic.
"""

import tiktoken

enc = tiktoken.get_encoding("gpt2")


def encode(s):
    return enc.encode(s)


def read_lines(path):
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if line:
                lines.append(line)
    return lines


def corrected_fertility(lines):
    total_tokens = 0
    total_words = 0
    total_chars = 0
    for line in lines:
        tokens = encode(line)          # no lowercasing
        words = line.split()           # robust whitespace split
        total_tokens += len(tokens)
        total_words += len(words)
        total_chars += len(line)
    fertility = total_tokens / total_words
    tok_per_char = total_tokens / total_chars
    return fertility, tok_per_char


def main():
    eng_lines = read_lines("partA/starter_kit_copy/eng_sample.txt")
    hin_lines = read_lines("partA/starter_kit_copy/hin_sample.txt")

    eng_fert, eng_tpc = corrected_fertility(eng_lines)
    hin_fert, hin_tpc = corrected_fertility(hin_lines)

    print("CORRECTED FERTILITY ANALYSIS")
    print("=" * 60)
    print(f"{'lang':<8}{'fertility (tok/word)':>22}{'tok/char':>12}")
    print("-" * 42)
    print(f"{'eng':<8}{eng_fert:>22.4f}{eng_tpc:>12.4f}")
    print(f"{'hin':<8}{hin_fert:>22.4f}{hin_tpc:>12.4f}")

    ratio_fert = hin_fert / eng_fert
    ratio_tpc = hin_tpc / eng_tpc

    print(f"\nCorrected fertility ratio (hin/eng): {ratio_fert:.2f}x")
    print(f"Corrected tok/char ratio (hin/eng):   {ratio_tpc:.2f}x")

    print("\n--- COMPARISON TO ORIGINAL REPORT ---")
    print(f"Original report claimed: 5.89x fertility, 7.0x tok/char")
    print(f"Corrected result:        {ratio_fert:.2f}x fertility, {ratio_tpc:.2f}x tok/char")


if __name__ == "__main__":
    main()