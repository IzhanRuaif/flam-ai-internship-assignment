# Part A3 — Corrected Tokenizer Comparison Results

## Setup

Ran on the full 1,000-sentence parallel FLORES corpus (Part A1), using the corrected methodology from Part A2 (no lowercasing, robust whitespace splitting, corpus-level sum/sum aggregation). Compared two tokenizers: `gpt2` (tiktoken) and `xlm-roberta-base` (HuggingFace SentencePiece).

## Results

| Tokenizer | Language | tok/word | tok/grapheme | tok/byte | tok/sentence |
|---|---|---|---|---|---|
| gpt2 | english | 1.2355 | 0.2051 | 0.2049 | 26.74 |
| gpt2 | hindi | 7.8199 | 1.5295 | 0.5947 | 198.34 |
| gpt2 | tamil | 25.0338 | 2.7256 | 0.9965 | 415.46 |
| gpt2 | kannada | 22.8017 | 2.6613 | 0.9787 | 363.21 |
| xlm-roberta-base | english | 1.4000 | 0.2324 | 0.2322 | 30.31 |
| xlm-roberta-base | hindi | 1.4905 | 0.2915 | 0.1134 | 37.81 |
| xlm-roberta-base | tamil | 2.4644 | 0.2683 | 0.0981 | 40.90 |
| xlm-roberta-base | kannada | 2.5735 | 0.3004 | 0.1105 | 40.99 |

## Headline finding

GPT-2's fertility on Tamil and Kannada is 20-25x English's, versus only 1.24x-7.82x for the eng/hin pair the original report measured. Switching to a multilingual-aware tokenizer (XLM-R) drops Tamil and Kannada fertility to ~2.5x English — roughly a 10x improvement, with no change to the underlying text.

This experiment shows that tokenizer choice materially changes the observed cross-language tokenization gap, directly challenging REPORT_v0.md's claim that fertility differences are purely "a property of the script, not the tokenizer." The large gap under gpt2 is therefore not an inherent, fixed property of the language alone. This does not prove language/script has zero effect: a residual gap (~1.25-1.35x under XLM-R by tokens-per-sentence) remains even with a multilingual tokenizer, so script and language characteristics likely still contribute some real cost. The original report's conclusion was drawn from testing only one tokenizer (gpt2) on only two languages, on a 10-line sample, which is not enough evidence to attribute the full gap to script alone.

## Metric selection: why tokens-per-sentence

We recommend **tokens per parallel sentence** as the primary routing metric, not tokens-per-word or tokens-per-byte:

- **tokens-per-word** is unreliable across scripts because word segmentation conventions differ; Tamil and Kannada are agglutinative, so "words" are not comparable units across languages.
- **tokens-per-byte** is biased toward multi-byte scripts: Indic scripts use ~3 bytes/character in UTF-8, which inflates the byte denominator and makes Tamil/Kannada appear artificially efficient under XLM-R (0.098-0.110 tok/byte vs English's 0.232) despite requiring more tokens for the same content.
- **tokens-per-sentence** uses the FLORES corpus's parallel alignment to hold semantic content approximately constant across languages, which most directly answers the actual routing/cost question: how many tokens does it cost to serve equivalent user content in language X?

By tokens-per-sentence with XLM-R: Hindi costs 1.25x English, Tamil 1.35x, Kannada 1.35x -- a moderate and actionable range, in sharp contrast to the double-digit multiples seen with gpt2.

## Grapheme metric caveat

The grapheme count used here is an approximation (NFC-normalized Unicode codepoint count), not a true Unicode grapheme cluster count (UAX #29), which would require a dedicated library. This is documented as an approximation and tok/grapheme should be read as directional, not exact.

## Revised recommendation

The original report's recommendation ("route all Indic traffic to a separate Indic-specialized tokenizer/model, budget 6x serving