"""
Part A3 -- Corrected multilingual tokenizer comparison.

Runs on the full 1,000-sentence parallel FLORES corpus (Part A1),
using the corrected methodology from the Part A2 audit:
  - no lowercasing
  - line.split() (robust whitespace) for word counts
  - corpus-level aggregation: sum(tokens) / sum(denominator)

Compares two tokenizers:
  - Tokenizer A: gpt2 (tiktoken)
  - Tokenizer B: xlm-roberta-base (HuggingFace, SentencePiece)

Computes four metrics per language per tokenizer:
  1. tokens per whitespace word
  2. tokens per grapheme cluster (approximated via NFC-normalized
     Unicode codepoints -- true grapheme clustering would need the
     `regex` or `grapheme` package; documented as an approximation)
  3. tokens per UTF-8 byte
  4. tokens per parallel sentence
"""

import csv
import unicodedata
from pathlib import Path

import tiktoken
from transformers import AutoTokenizer

CORPUS_PATH = Path("partA/data/flores_parallel_1000.csv")
RESULTS_PATH = Path("partA/corrected_analysis/results/tokenizer_comparison.csv")

LANGUAGES = ["english", "hindi", "tamil", "kannada"]


def load_corpus():
    rows = []
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def get_gpt2_encoder():
    enc = tiktoken.get_encoding("gpt2")
    return enc.encode


def get_xlmr_encoder():
    tok = AutoTokenizer.from_pretrained("xlm-roberta-base")
    return lambda s: tok.encode(s, add_special_tokens=False)


def grapheme_approx_count(text):
    """
    Approximate grapheme cluster count.

    True grapheme clustering (per Unicode UAX #29) requires a
    dedicated library. As an approximation, we count NFC-normalized
    codepoints, which merges most combining marks in Indic scripts
    into their base character but is not a fully correct grapheme
    cluster count. Documented as an approximation, not exact.
    """
    normalized = unicodedata.normalize("NFC", text)
    return len(normalized)


def analyze_language(rows, language, encode_fn):
    total_tokens = 0
    total_words = 0
    total_graphemes = 0
    total_bytes = 0
    total_sentences = len(rows)

    for row in rows:
        text = row[language]  # already NFC-normalized in Part A1, no lowercasing
        tokens = encode_fn(text)
        words = text.split()
        graphemes = grapheme_approx_count(text)
        byte_len = len(text.encode("utf-8"))

        total_tokens += len(tokens)
        total_words += len(words)
        total_graphemes += graphemes
        total_bytes += byte_len

    return {
        "language": language,
        "tokens": total_tokens,
        "words": total_words,
        "graphemes": total_graphemes,
        "bytes": total_bytes,
        "sentences": total_sentences,
        "tokens_per_word": total_tokens / total_words,
        "tokens_per_grapheme": total_tokens / total_graphemes,
        "tokens_per_byte": total_tokens / total_bytes,
        "tokens_per_sentence": total_tokens / total_sentences,
    }


def main():
    print("Loading corpus...")
    rows = load_corpus()
    print(f"Loaded {len(rows)} parallel sentences.")

    tokenizers = {
        "gpt2": get_gpt2_encoder(),
        "xlm-roberta-base": get_xlmr_encoder(),
    }

    all_results = []

    for tok_name, encode_fn in tokenizers.items():
        print(f"\nAnalyzing with tokenizer: {tok_name}")
        for language in LANGUAGES:
            result = analyze_language(rows, language, encode_fn)
            result["tokenizer"] = tok_name
            all_results.append(result)
            print(
                f"  {language:<10} "
                f"tok/word={result['tokens_per_word']:.4f}  "
                f"tok/grapheme={result['tokens_per_grapheme']:.4f}  "
                f"tok/byte={result['tokens_per_byte']:.4f}  "
                f"tok/sentence={result['tokens_per_sentence']:.4f}"
            )

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "tokenizer", "language", "tokens", "words", "graphemes",
            "bytes", "sentences", "tokens_per_word", "tokens_per_grapheme",
            "tokens_per_byte", "tokens_per_sentence",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_results:
            writer.writerow(row)

    print(f"\nResults saved to {RESULTS_PATH.resolve()}")


if __name__ == "__main__":
    main()