"""
Experiment 3: Does line.lower() change fertility asymmetrically
across English (has case) vs Hindi (no case, Devanagari)?
"""

import tiktoken

enc = tiktoken.get_encoding("gpt2")


def encode(s):
    return enc.encode(s)


def fertility(lines, apply_lower):
    total_tokens = 0
    total_words = 0
    for line in lines:
        text = line.lower() if apply_lower else line
        tokens = encode(text)
        words = text.split(" ")
        total_tokens += len(tokens)
        total_words += len(words)
    return total_tokens / total_words


def run(label, lines):
    with_lower = fertility(lines, apply_lower=True)
    without_lower = fertility(lines, apply_lower=False)
    diff = with_lower - without_lower
    pct = (diff / without_lower) * 100
    print(f"\n{label}")
    print(f"  Fertility WITH lowercasing:    {with_lower:.4f}")
    print(f"  Fertility WITHOUT lowercasing: {without_lower:.4f}")
    print(f"  Absolute difference:           {diff:+.4f}")
    print(f"  Relative difference:           {pct:+.2f}%")


def main():
    with open("partA/starter_kit_copy/eng_sample.txt", "r", encoding="utf-8") as f:
        eng_lines = [l.strip() for l in f if l.strip()]
    run("ENGLISH", eng_lines)

    with open("partA/starter_kit_copy/hin_sample.txt", "r", encoding="utf-8") as f:
        hin_lines = [l.strip() for l in f if l.strip()]
    run("HINDI", hin_lines)


if __name__ == "__main__":
    main()