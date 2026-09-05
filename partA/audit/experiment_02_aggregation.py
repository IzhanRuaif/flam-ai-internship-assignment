"""
Experiment 2: Does averaging per-line fertility ratios (original)
differ meaningfully from computing fertility at the corpus level
(sum tokens / sum words)?

Uses a synthetic example designed to expose the bias, then checks
the real sample corpus.
"""

import tiktoken

enc = tiktoken.get_encoding("gpt2")


def encode(s):
    return enc.encode(s)


def original_method(lines):
    """mean(tokens_i / words_i) -- as in fertility.py"""
    ratios = []
    for line in lines:
        tokens = encode(line.lower())
        words = line.lower().split(" ")
        ratios.append(len(tokens) / len(words))
    return sum(ratios) / len(ratios)


def corpus_level_method(lines):
    """sum(tokens) / sum(words) -- corrected aggregation"""
    total_tokens = 0
    total_words = 0
    for line in lines:
        tokens = encode(line.lower())
        words = line.lower().split(" ")
        total_tokens += len(tokens)
        total_words += len(words)
    return total_tokens / total_words


def run(label, lines):
    orig = original_method(lines)
    corrected = corpus_level_method(lines)
    diff = orig - corrected
    pct = (diff / corrected) * 100
    print(f"\n{label}")
    print(f"  Original (mean of ratios):     {orig:.4f}")
    print(f"  Corrected (sum/sum):           {corrected:.4f}")
    print(f"  Absolute difference:           {diff:+.4f}")
    print(f"  Relative difference:           {pct:+.2f}%")


def main():
    # --- Synthetic example designed to expose the bias ---
    # One very short line (extreme ratio) + one long line (typical ratio)
    synthetic = [
        "a",                                                    # 1 word, extreme ratio
        "the quick brown fox jumps over the lazy dog again today",  # 11 words, typical ratio
    ]
    run("SYNTHETIC (short + long line mix)", synthetic)

    # --- Real corpus ---
    with open("partA/starter_kit_copy/eng_sample.txt", "r", encoding="utf-8") as f:
        eng_lines = [l.strip() for l in f if l.strip()]
    run("REAL ENGLISH SAMPLE", eng_lines)

    with open("partA/starter_kit_copy/hin_sample.txt", "r", encoding="utf-8") as f:
        hin_lines = [l.strip() for l in f if l.strip()]
    run("REAL HINDI SAMPLE", hin_lines)


if __name__ == "__main__":
    main()