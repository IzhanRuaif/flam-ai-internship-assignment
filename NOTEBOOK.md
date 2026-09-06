# Lab Notebook

## Part A1 — Corpus construction

### Goal
Construct a multilingual evaluation corpus substantially larger than the supplied smoke-test corpus.

### Initial hypothesis
A parallel multilingual corpus would be more useful than independently sampled text because aligned sentences approximately control for semantic content across languages.

### Dataset decision
Selected FLORES-200 because it provides multilingual translated evaluation data with aligned sentence identifiers. Required requesting gated access and authenticating via `hf auth login`.

Selected languages: English, Hindi, Tamil, Kannada.

### Corpus size decision
Target size: 1,000 aligned sentences. This is a compromise between being substantially larger than the ~10-sentence smoke-test corpus and remaining small enough for rapid, reproducible analysis.

### Preprocessing decision
Minimal preprocessing only: Unicode NFC normalization, leading/trailing whitespace removal, empty-row filtering. No lowercasing or punctuation removal, since these could change tokenizer behavior and confound comparison.

### Preliminary observations
Tamil and Kannada sentences show notably fewer whitespace-delimited words than English or Hindi (16.6 and 15.9 vs 21.65 and 25.36 respectively) despite comparable or greater character counts. This is consistent with their agglutinative morphology, where a single orthographic word can encode information expressed as multiple words in English. This observation motivated using multiple denominators (words, graphemes, bytes) rather than relying on whitespace-word count alone in Part A3.

### Result
Ran `prepare_corpus.py` against the FLORES `devtest` split. Found 1,012 sentence IDs common to all four languages. Retained 1,000 valid parallel sentences with 0 empty rows removed. Output saved to `partA/data/flores_parallel_1000.csv`.

### Revision
None required — script worked as designed on first successful run (after resolving Hugging Face gated-dataset authentication).

---

## Part A2 — Auditing fertility.py

### Goal
Audit the previous intern's `fertility.py` script for methodological issues, verifying every claim experimentally rather than assuming bugs exist.

### Initial hypotheses
1. `line.split(" ")` may undercount/miscount words on lines with irregular whitespace.
2. Averaging per-line fertility ratios (mean of ratios) may differ from corpus-level aggregation (sum/sum).
3. Lowercasing before tokenization may affect English (case-sensitive BPE) differently than Hindi (no case distinction).
4. `random.seed(1337)` looks suspicious but may be harmless dead code.
5. NFC normalization may or may not distort results.

### Result
- **Whitespace splitting (confirmed bug):** 1 line in each of eng/hin samples contains a double space, producing a phantom empty-string token that inflates word count by 1 per affected line.
- **Aggregation bias (confirmed bug, small magnitude):** mean-of-ratios overstates fertility by +0.96% (English) and +0.61% (Hindi) vs sum/sum on the real 10-line samples. Note: an initial synthetic test (1-word line vs 11-word line) failed to expose this bias, since both lines had per-line ratio ≈1.0 despite differing length — the bias depends on variance in per-line ratios, not line length.
- **Lowercasing confound (confirmed bug):** English fertility changes by +3.12% when lowercased; Hindi is completely unaffected (0.00%), since Devanagari has no case. Confirms lowercasing is not a neutral preprocessing choice for cross-language comparison.
- **`random.seed(1337)`:** verified via grep that `random` is never used elsewhere in the script. Harmless dead code, not a bug — GPT-2 BPE via tiktoken is deterministic regardless.
- **NFC normalization:** standard practice for Indic scripts, no distortion found. Not a bug.

### Corrected result
Applying all three confirmed fixes (no lowercasing, `split()`, sum/sum aggregation) on the same 10-line samples: fertility ratio (hin/eng) = 6.11x, tok/char ratio = 7.39x — versus the original report's claimed 5.89x and 7.0x.

### Revision
The corrected ratio came out slightly *higher* than the original, not lower. The bugs were real but happened to roughly cancel out on this small sample rather than inflating the headline number. The core problem with REPORT_v0.md is not that its number was fabricated, but that it draws strong, unqualified conclusions from a flawed methodology and an extremely small (10-line) sample.

---

## Part A3 — Corrected tokenizer comparison at scale

### Goal
Re-run the corrected fertility methodology (from Part A2 audit) on the full 1,000-sentence FLORES corpus, comparing two tokenizers across four denominators, to check whether the original report's findings hold at scale and across tokenizer choice.

### Initial hypothesis
Expected Hindi to show moderately higher fertility than English with gpt2, consistent with Part A2's small-sample result (~6x). Did not have a strong prior on Tamil/Kannada behavior with gpt2, or on how much a multilingual tokenizer (xlm-roberta-base) would change results.

### Tokenizer decision
Chose xlm-roberta-base as the second tokenizer: fully open (no gating/login required, unlike gemma-2), well-documented, SentencePiece-based, native support for Devanagari, Tamil, and Kannada scripts.

### Result
gpt2 fertility (tok/word): eng 1.24, hin 7.82, tam 25.03, kan 22.80.
xlm-roberta-base fertility (tok/word): eng 1.40, hin 1.49, tam 2.46, kan 2.57.

Tamil and Kannada fertility under gpt2 (20-25x English) was far worse than anticipated, and far worse than the eng/hin gap the original report measured. Switching to xlm-roberta-base reduced Tamil/Kannada fertility to ~2.5x English — roughly a 10x improvement from tokenizer choice alone, on the same text.

This challenges REPORT_v0.md's absolute claim that fertility differences are purely "a property of the script, not the tokenizer" — the evidence shows tokenizer choice materially changes the gap, though a residual ~1.25-1.35x gap (by tokens-per-sentence, XLM-R) remains even with a multilingual tokenizer, so script/language characteristics likely still contribute some real cost.

### Metric decision
Selected tokens-per-sentence as the primary routing metric over tokens-per-word (unreliable across scripts with different word segmentation conventions) and tokens-per-byte (biased toward multi-byte scripts like Tamil/Kannada, which use ~3 bytes/char in UTF-8 and so appear artificially efficient by this metric).

### Revision
None needed to the analysis script itself. Note for future reference: grapheme count is an NFC-codepoint approximation, not a true Unicode grapheme cluster count — documented as a caveat in `results_interpretation.md` rather than treated as exact.

---

## Part A4 — Recommendation memo

Wrote the 1-page memo based on A2+A3 findings. Core message: the original report's root-cause claim was wrong (tokenizer, not script), the recommended fix is tokenizer standardization rather than per-language cost budgeting, and FLORES's lack of code-mixed/informal text is the key caveat before trusting these numbers in production. Part A complete.

---

## Part B1 — KV-cache capacity calculation

### Goal
Derive theoretical KV-cache capacity from the model spec and reconcile it against observed benchmark behavior.

### Result
Calculated theoretical max concurrent sequences at max_model_len (4096 tokens): ~28.93 (floor 28), using KV bytes/token = 114,688 (derived from layers x KV_heads x head_dim x 2 x 2 bytes fp16). Observed KV saturation (util >0.9, preemption starting) occurs between batch 24-32 in bench_log.csv — reasonably close to theory, with the residual gap plausibly explained by page-level allocation fragmentation, the non-KV overhead being a stated assumption rather than a measurement, and possible GB/GiB unit ambiguity.

---

## Part B2 — Throughput anomaly

### Result
reported_tok_s peaks at batch 24 (1607.4 tok/s) and declines at batch 32 (1384.0) and batch 48 (1298.5), contradicting REPORT_v0.md's linear-scaling claim (predicted ~3200 tok/s at batch 48). Mechanism: kv_cache_util saturates near 0.97 from batch 32 onward, triggering preemption (7 then 23 sequences), which forces wasted recompute.

---

## Part B3 — Correcting the goodput calculation

### Result (major finding)
Found that reported_tok_s itself is miscalculated: it counts prompt (prefill) tokens as if they were generated output, following reported_tok_s = (prompt_len+gen_len) x num_requests / wall_clock_s — confirmed by an exact constant ratio to true goodput (3x for short prompts, 8x for long prompts) across every row regardless of batch size. True goodput (completed_output_tokens / wall_clock_s) is far lower than reported, and still peaks at batch 24, confirming B2's capacity recommendation on corrected numbers. Cross-checked with an independent itl_ms_p50-based estimate: the two methods agree when preempted_seqs=0, but diverge sharply once preemption begins, because itl_ms_p50 is a median and does not capture preemption stalls — a second, distinct measurement issue from the prefill-counting bug.

### Revision
Initial B3 script only computed one goodput method; added the independent itl_ms_p50 cross-check after noticing the constant-ratio pattern suggested a definitional bug worth verifying two ways rather than trusting a single derivation.

---

## Part B4 — Confirming metric

Selected `preempted_seqs` (tracked as a live rate) alongside `kv_cache_util` as the confirming production metrics, since both are already exposed by the benchmarking harness per model_spec.md's column notes -- deliberately avoided proposing a new, unverified counter name not grounded in the described serving setup.

---

## Part C — Decision memo

### Goal
Recommend one of SFT / rewriter model / prompt engineering for making outputs more casual/conversational, under stated resource constraints.

### Decision
Recommended prompt engineering. Under the given constraints (1x A100-80GB for 14 days, ~10 reviewer-hours/week), reviewer bandwidth is the binding constraint, not compute. SFT and rewriter approaches both require building labeled data first, which would consume most of the available reviewer time before any training or evaluation could happen. Prompt engineering needs no training data, ships immediately, and is fully reversible.

### Arithmetic
Reviewer capacity over 2 weeks: 10 hrs/week x 2 = 20 hours total, x 40 samples/hour = 800 samples. Day 1 budget: 2 hours = 80 samples.

### Success/kill criteria
Success: >=75% of outputs rated both casual and meaning-preserving. Kill: if no prompt variant reaches 60% dual-pass rate across 3 variants on an 80-sample first batch, escalate to the rewriter approach using the reserved GPU budget.

### Revision
None — assumptions and thresholds were set directly based on the stated constraints without needing course-correction.