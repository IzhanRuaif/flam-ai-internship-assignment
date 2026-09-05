# Multilingual Evaluation Corpus

## Purpose

This corpus was constructed for auditing cross-language tokenizer efficiency. The goal is to compare how different tokenizers represent approximately equivalent content across languages while avoiding conclusions based on a very small smoke-test corpus.

## Dataset

The evaluation corpus is derived from the FLORES-200 multilingual benchmark. FLORES provides professionally translated multilingual evaluation data with aligned sentence identifiers across supported language configurations.

The following four languages were selected:

* English (`eng_Latn`)
* Hindi (`hin_Deva`)
* Tamil (`tam_Taml`)
* Kannada (`kan_Knda`)

English and Hindi satisfy the assignment requirements. Tamil and Kannada were selected as Dravidian languages and use distinct Indic scripts, allowing the evaluation to examine cross-script as well as cross-language tokenization behavior.

## Corpus Size

The final evaluation corpus contains 1,000 aligned parallel sentences for each language, drawn from the FLORES `devtest` split (1,012 sentences common across all four languages).

Each row represents the same sentence identifier across English, Hindi, Tamil, and Kannada. This alignment is important because it allows token counts to be compared while approximately holding semantic content constant.

The corpus is intentionally much larger than the provided smoke-test corpus of approximately ten sentences while remaining small enough for rapid, reproducible experimentation.

## Construction Procedure

The corpus construction script:

1. Loads the selected FLORES language configurations from the `devtest` split.
2. Identifies sentence IDs common to all four language datasets (1,012 found).
3. Aligns text using the common sentence IDs.
4. Applies Unicode NFC normalization.
5. Removes leading and trailing whitespace.
6. Rejects rows containing empty text in any language.
7. Retains the first 1,000 valid aligned sentence IDs in sorted order.
8. Saves the resulting corpus as UTF-8 CSV.

No lowercasing, punctuation removal, transliteration, stemming, or other linguistic normalization is applied. These transformations could themselves alter tokenizer behavior and would therefore confound the tokenizer comparison.

## Reproducibility

The corpus can be reconstructed by running:

`python partA/prepare_corpus.py`

The resulting file is saved as:

`partA/data/flores_parallel_1000.csv`

The corpus construction script records the number of aligned sentence IDs found (1,012), retained rows (1,000), and removed invalid rows (0).

## Limitations

This corpus evaluates tokenizer efficiency on a limited parallel multilingual dataset and does not represent all production traffic.

The domain and writing style of the source data may differ from conversational assistant traffic. The evaluation also cannot fully represent code-mixed language, transliterated Indic text, names, emojis, URLs, numbers, spelling variations, regional dialects, or highly informal conversational writing.

Parallel sentence alignment approximately controls for semantic content, but translations are not perfectly identical in wording or length. Therefore, differences in token counts should be interpreted as an evaluation signal rather than a universal estimate of production cost.