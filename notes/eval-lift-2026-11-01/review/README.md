# Adversarial review of the skill-lift eval (2026-11-01)

The owner suspected the eval was biased. An independent reviewer agent (a
different model tier from both the generators and the judges) received only the
code and the raw data, not the orchestrator's own suspicions. It was asked to
confirm or refute each possible bias with computations.

Its central finding is that **bare and main outputs are byte-identical across
v0 and all four step runs.** Every difference in their scores between runs is
therefore pure judge noise. That gives an exact test-retest experiment.
Scripts: `analyze.py` and `items_deep.py` (stdlib; data paths as arguments).
Outputs: `analysis_out.txt` (sections A–L) and `items_deep_out.txt`. The step
run artifacts they read are in `../runs/`.

## Verdict

- **The step gate as pre-registered carries no information.**
  - When identical text is fed to the gate as if it were a new version, it
    passes only **3 of 12** run pairs (analysis section I). The orchestrator
    re-checked this number.
  - Re-judging the same `main` text five times gives a meaning-changes total
    of 9 / 12 / 15 / 6 / 12, and a would-send total of 42–45.
  - The zero-tolerance `≥`/`≤` checks sit inside that noise band. So every
    PASS/FAIL so far (step0 FAIL, step1 FAIL, step2 FAIL, step3 PASS) is
    noise.
- **The v0 claim "beats no skill on meaning drift, p=0.04" did not replicate.**
  - The direction holds in all five judgings of the identical texts: main is
    better on 6–9 items and worse on 1–2.
  - The p-values are 0.039 / 0.125 / 0.109 / 0.125 / 0.065. The 0.039 is one
    of ten or more uncorrected comparisons.
  - The effect comes mostly from items the suite left unchanged while bare made
    a small edit.
  - Honest statement: *the suite edits less than bare Sonnet; a one-line
    instruction produces the same restraint.*
- **"Ties the one-line prompt" is supported and robust.**
- **The PR #67 conclusion was decided by the rubric, not the data.** The judge
  prompt says "a change that corrects the draft to match the notes is not a
  meaning change", which is the very rule in dispute.
- **The step-specific extra items discriminated nothing.** Every arm scored
  2/2 on every extra item in steps 1–3. The extras were also written from each
  rule's own text (teaching to the test).

## Threats, ranked by the reviewer

The full table, with numbers, is in the reviewer's report (summarized here):

1. **The zero-tolerance gate is applied to noisy totals.** High severity.
2. **Ceiling effects reward doing nothing.** 16 of the 24 frozen items need no
   change. An unchanged output is sent 99% of the time, and 53–60% of `new`'s
   would-send points come from outputs it left unchanged. High severity.
3. **Each arm has one generation, and the baseline is one frozen draw.** Two
   generations from the same arm differ by ≥0.30 edit ratio on exactly the
   items that move the gate. High severity.
4. **Item circularity.** The fixtures were written by the suite's author, and
   the extras were written from the rule text. High severity.
5. **The rubric pre-decides contested design questions.** One example is the
   PR #67 rule. Another: the judges reject the suite's own gold rewrite of
   overstep-05, the "You might think X, but…" sentence, 10 times out of 10.
   Medium-high severity.
6. **The `meaning_changes` metric is a loose count.** 36–41% of the listed
   changes are typed "other", and the headline uses an uncorrected p-value.
   Medium severity.
7. **Judge context changes between v0 (6 candidates) and the steps (3
   candidates).** The same text flips on linkedin-01: 0/2 sent in v0, but sent
   on 7 of 8 judgments in the steps. Medium severity.
8. **Position effects.** Best pick and rank depend on label position
   (p≈0.0005). would-send by position is flat. Medium severity.
9. **The judge is the same model family as the generators, and the judge model
   is not logged.** Medium severity.
10. **The judge prefers smaller edits.** In 78–86% of sent-vs-not-sent pairs,
    the sent candidate was the less-edited one. This may be correct fidelity or
    may be judge conservatism; there is no human anchor. Low-medium severity.

Refuted, meaning not present as a differential bias:

- **Length or verbosity bias.** The sent candidate was the shorter one in only
  55% of pairs.
- **Notes leaking which arm wrote an output.** A classifier trained on the notes
  scored at chance, 17%. The suite's jargon does repeat across items, though.

Also found:

- **The deterministic rows are near-vacuous.** "hedges lost = 2" comes from
  the "might" in "You might think…".
- **The noise rule is optional stopping.** A re-run happens only after a
  failure, which inflates the pass rate.

## Fixes, ranked by value per cost

1. **Use a noise-calibrated gate** (free).
   - Use the identical-text re-judgings as the null distribution.
   - Report "no evidence of regression" instead of PASS.
   - Fail only beyond about 2 standard deviations, or on a paired sign test
     over the discordant items.
   - Drop the deterministic rows, or fix them.
2. **Re-generate the baseline too, with K≥3 runs for both new and main.**
3. **Gate only on items that can move.**
   - Add 15–25 items with planted failures.
   - Have a separate agent write them from failure descriptions, not from the
     rule text.
   - Hold out half of them so the author of a fix never sees them.
4. **Calibrate the judge with known-answer sentinel pairs mixed into every
   packet.**
5. **Judge new against main pairwise, in both orders**, on the items that
   discriminate.
6. **Hide the notes when scoring the gated metric.**
7. **Gate only on typed severe changes**, recorded as a binary per candidate
   (number change, added claim, dropped fact, strengthened certainty).
8. **Use a judge panel across tiers** (Haiku, Sonnet, Opus), and log the model
   id.
9. **Pre-register K.** No re-run only after a failure.
10. **Add a human anchor.** The owner labels the roughly 8 items that ever
    discriminate. Someone must decide whether the catalog or the judge is
    right, for example on overstep-05.
11. **Stop reporting p-values from 24 items.** Report paired differences with
    the minimum detectable effect instead (Miller 2024).

Literature the reviewer cited:

- Zheng et al. 2023 (MT-Bench: position, verbosity, and self-enhancement bias);
- Shi et al. 2024 (position bias is largest when quality gaps are small);
- Panickssery et al. 2024 and Wataoka et al. 2024 (self-preference);
- Ye et al. 2024 (CALM bias taxonomy);
- Miller 2024, "Adding Error Bars to Evals";
- arXiv 2503.01747 (no CLT intervals below a few hundred datapoints);
- arXiv 2511.21140 (report judge error rates using a labeled calibration set).
