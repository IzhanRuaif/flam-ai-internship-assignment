# Tokenizer Fertility — Corrected Findings & Recommendation

## Headline

The original report's claim that Hindi's higher tokenizer fertility is "a property of the script, not the tokenizer" is incorrect. On the full 1,000-sentence FLORES corpus, GPT-2 shows extreme fertility for Tamil and Kannada (20-25x English) — far worse than the Hindi gap (7.8x) the original report measured on 10 lines. Switching to a multilingual-aware tokenizer (xlm-roberta-base) cuts Tamil/Kannada fertility to ~2.5x English, a ~10x improvement with no change to the underlying text. This shows that tokenizer choice materially changes the observed cross-language tokenization gap; the large gap under GPT-2 is therefore not an inherent, fixed property of the language alone, though language and script characteristics may still contribute to the residual ~2.5x gap that remains even under a multilingual tokenizer.

The original report also contained three confirmed methodology bugs (non-robust whitespace splitting, biased ratio-of-means aggregation, an asymmetric lowercasing confound) and relied on only 10 sentences per language — too small to support a serving-cost recommendation.

## Recommendation

Do not adopt separate per-language cost budgets based on the original analysis, and do not assume the fix is to arbitrarily swap the tokenizer of an already-deployed model — a model's tokenizer is fixed at pretraining time and is not a standalone, swappable component. Instead: **for model selection or future training, prefer a model whose native tokenizer demonstrates efficient tokenization on representative target-language traffic** (as xlm-roberta-base does here relative to gpt2). This finding should inform which base model to select or train for Indic-heavy traffic, not be read as a recommendation to modify an existing deployed model's tokenizer. Using tokens-per-sentence (which holds meaning approximately constant via FLORES's parallel alignment) as the comparison metric, the multilingual-tokenizer cost gap in this experiment is 1.25-1.35x English — not 6-25x.

## Biggest caveat

FLORES is professionally translated, domain-general benchmark text. It does not represent conversational assistant traffic: code-mixed language, transliteration, informal spelling, names, emojis, and URLs are all absent. Real production fertility for Indic languages may differ from this corpus, in either direction.

## Production metric to watch

**Tokens consumed per completed user request, broken out by detected input language.** If this metric shows a materially larger gap in production than the ~1.25-1.35x measured here, that would indicate this analysis underestimated real-world cost (likely due to code-mixing or informal text not represented in FLORES) and would be the trigger to revisit tokenizer choice or add per-language handling.
