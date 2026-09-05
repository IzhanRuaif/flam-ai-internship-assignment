\# Decision Memo: Making Outputs More Casual \& Conversational



\## 1. Recommendation



\*\*C. Prompt engineering.\*\*



Given the stated resource envelope (1x A100-80GB for 14 days,

\~10 reviewer-hours/week), the binding constraint is reviewer

bandwidth, not compute. SFT requires building a labeled dataset from

scratch -- consuming most of the available reviewer time on data

creation before any model training or evaluation can even begin. A

rewriter model needs less labeled data than SFT but still requires

training, a serving path, and added latency per request. Prompt

engineering requires no training data, no GPU time, ships

immediately, and is fully reversible if it underperforms -- making

it the correct choice to attempt first under this constraint, with

a defined escalation path if it fails (see Kill Criterion).



\## 2. Assumptions



\- Average response length: \~150 tokens.

\- A trained human reviewer can evaluate approximately 40 output

&#x20; samples/hour for casualness + meaning preservation (two short

&#x20; judgments per sample).

\- Reviewer availability: 10 hours/week.

\- GPU availability: 1x A100-80GB for 14 days (used only if prompt

&#x20; engineering fails and escalation to a rewriter/SFT becomes

&#x20; necessary).

\- Baseline model already exists and is queryable; no base model

&#x20; training is in scope.



\## 3. Arithmetic



\*\*Reviewer capacity over the experiment window (2 weeks):\*\*



reviewer hours = 10 hrs/week x 2 weeks = 20 hours

reviewer capacity = 20 hours x 40 samples/hour = 800 samples





\*\*Day 1 experiment budget (see Section 6):\*\*



Day 1 reviewer time = 2 hours (out of the 20-hour budget)

Day 1 sample capacity = 2 x 40 = 80 samples





\*\*GPU budget (held in reserve, not spent on prompt engineering):\*\*



1x A100-80GB x 14 days = fully available if escalation to

rewriter/SFT is triggered by the kill criterion.





\## 4. Success metric



At least \*\*75% of sampled outputs\*\* are rated by a human reviewer as

both (a) casual/conversational in tone and (b) preserving the

original semantic meaning of the baseline output. Both conditions

must hold simultaneously -- a casual-but-inaccurate rewrite does not

count as a success.



\## 5. Kill criterion



If, after testing 3 distinct prompt variants across an 80-sample

Day-1 batch, no variant reaches \*\*60% dual-pass rate\*\* (casual AND

meaning-preserved), abandon prompt engineering and escalate to the

rewriter-model approach, allocating the reserved GPU budget. This

threshold is set below the 75% success bar specifically to catch

prompt engineering clearly failing, without abandoning it over

noise from a single weak variant.



\## 6. Day 1 experiment



1\. Draft 3 prompt variants (e.g. differing in explicit tone

&#x20;  instruction, few-shot examples, and instruction placement).

2\. Run each variant against the same fixed set of \~27 baseline

&#x20;  inputs (81 total generations, rounding to the 80-sample budget).

3\. Reviewer scores each output pair (original vs rewritten) on two

&#x20;  binary axes: casual tone (yes/no), meaning preserved (yes/no).

4\. Compute dual-pass rate per variant.

5\. Compare against the 60% kill threshold and 75% success bar;

&#x20;  select the best-performing variant or trigger escalation.

