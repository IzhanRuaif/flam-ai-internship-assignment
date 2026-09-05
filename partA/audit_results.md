\# Audit of fertility.py (v0)



\## Summary



The original script (`fertility.py`) contains three real, confirmed

methodological issues. Correcting all three changes the reported

fertility ratio from 5.89x to 6.11x — the corrected number is

slightly \*higher\*, not lower. The bugs did not fabricate the report's

headline finding; they happened to roughly cancel out on this

10-line sample. The core problem with REPORT\_v0.md is not that its

number is wrong, but that it draws strong conclusions ("no further

measurement needed," "a property of the script, not the tokenizer")

from a flawed and extremely small sample.



\## Experiment 1: Whitespace splitting (`line.split(" ")`)



\*\*Hypothesis:\*\* literal single-space splitting undercounts words on

lines with multiple consecutive spaces.



\*\*Method:\*\* compared `line.split(" ")` vs `line.split()` on every

line of the real eng/hin samples.



\*\*Result:\*\* confirmed. 1 line in each language sample contains a

double space (`eng\_sample.txt` line 7, `hin\_sample.txt` line 10),

each producing one phantom empty-string token that inflates the word

count by 1. Effect on this 10-line sample is small (1 line each,

same direction in both languages), but this is a general robustness

bug that would scale with corpus size and messiness of source text

(e.g. scraped or OCR'd data).



\*\*Verdict: confirmed bug.\*\*



\## Experiment 2: Aggregation method (mean of ratios vs sum/sum)



\*\*Hypothesis:\*\* averaging per-line fertility ratios is a biased

estimator relative to computing fertility at the corpus level

(`sum(tokens) / sum(words)`).



\*\*Method:\*\* compared both aggregation methods on a synthetic example

and on the real samples.



\*\*Result:\*\* the initial synthetic example (a 1-word line vs an

11-word line) failed to expose the bias, because both lines

happened to have a per-line ratio near 1.0 despite differing length

— the bias depends on variance in per-line \*ratios\*, not line

length. On the real corpus: mean-of-ratios overstates fertility by

+0.96% for English and +0.61% for Hindi relative to sum/sum. Small

at this corpus size, but a real, direction-consistent bias that

could compound differently on a larger, more heterogeneous corpus

(e.g. the 1,000-sentence FLORES corpus from Part A1).



\*\*Verdict: confirmed bug, small magnitude at this sample size.\*\*



\## Experiment 3: Lowercasing confound (`line.lower()`)



\*\*Hypothesis:\*\* lowercasing before tokenization affects English

(case-sensitive BPE tokens) but not Hindi (Devanagari has no case),

introducing a language-asymmetric confound.



\*\*Method:\*\* compared fertility with and without lowercasing on both

languages.



\*\*Result:\*\* confirmed exactly as hypothesized. English fertility

changes by +3.12% when lowercased (1.2152 -> 1.2532). Hindi fertility

is completely unaffected (0.00% change), since Devanagari has no

case distinction for `.lower()` to act on. Lowercasing measures

English on non-natural text (real traffic is not all-lowercase) and

is not a neutral preprocessing choice for a cross-language

comparison.



\*\*Verdict: confirmed bug (methodological, language-asymmetric).\*\*



\## Experiment 4: `random.seed(1337)`



\*\*Method:\*\* searched the script for any use of the `random` module

beyond the seed call.



\*\*Result:\*\* `random` is imported and seeded but never used anywhere

else in the script. GPT-2's BPE tokenizer (via `tiktoken`) is fully

deterministic, so this seed has no effect on any output.



\*\*Verdict: not a bug. Harmless dead code\*\*, likely leftover

scaffolding from an earlier version of the script that used

sampling. Not flagged as an issue in the corrected version.



\## Experiment 5: NFC normalization



`unicodedata.normalize("NFC", line)` is standard practice for

Indic scripts (guards against inconsistent Unicode composition of

the same visual character) and was not found to introduce any

distortion. Not flagged as a bug.



\## Corrected result



| lang | fertility (tok/word) | tok/char |

|---|---|---|

| eng | 1.2308 | 0.2143 |

| hin | 7.5246 | 1.5828 |



Corrected fertility ratio (hin/eng): \*\*6.11x\*\*

Corrected tok/char ratio (hin/eng): \*\*7.39x\*\*



Original report claimed 5.89x fertility, 7.0x tok/char.



\## On the report's "two metrics agree, so it's robust" claim



REPORT\_v0.md argues that because tok/word and tok/char "agree"

(5.89x and 7.0x), the result is independently confirmed and needs

no further measurement. This reasoning is flawed: both metrics share

the same numerator (`tokens`, from the same buggy tokenization call)

and were computed over the same 10-line sample with the same

preprocessing. Agreement between two metrics that share their most

important input is not independent confirmation — it is expected

even if the shared input is flawed.



\## Sample size caveat



Both the original and corrected numbers are computed on 10 lines

per language. This is a smoke-test corpus, not a basis for a

production serving-cost recommendation. Part A3 re-runs this

comparison on the 1,000-sentence parallel FLORES corpus built in

Part A1 to check whether the \~6x ratio holds at scale.

