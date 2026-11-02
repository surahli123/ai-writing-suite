# Experiment readout: verdict first, then effects with their uncertainty

> **Generic best-practice entry.** Compiled from public DS-communication
> practice: experimentation readout guides, GRADE-style evidence statements,
> and the round-2 research note `notes/research-best-practices-round2-2026-11-01.md`.
> Open-source KB; a company fork replaces it with its own readout standard via
> the same slot (`README.md`).

## Principle

A readout exists to support a decision, so it opens with the verdict and whether
the test can be trusted. Each effect is stated with enough context for a reader
to judge its size and its uncertainty without opening the notebook. The writer
reports what the test can and cannot show. The decision rule belongs to the
experiment owner, not to the prose.

## Moves

- **Slots, in order.** A readout that is missing one gets a `[NEEDS: …]` marker,
  never an invented value.
  1. **Verdict:** ship / don't ship / iterate / inconclusive, in one line.
  2. **Validity:** sample-ratio check, exposure window, and any guardrail that
     vetoes the result.
  3. **Primary effect:** stated in full (see the next move).
  4. **Guardrails and secondary metrics.**
  5. **Segments:** pre-registered segments are kept apart from exploratory ones,
     which are labeled exploratory.
  6. **What we don't know.**
  7. **Next step**, with an owner and a date.
- **An effect statement carries five parts:**
  - the estimate with its baseline ("7-day retention rose from 40.1% to 41.3%");
  - its unit of change (percentage points versus percent);
  - the interval and its level;
  - the population, the n and the window;
  - what it means against the decision threshold.

  Never compute or guess an interval the analysis did not produce; mark it
  `[NEEDS: interval]`.
- **Three different nulls.** Never collapse them into "no effect":
  - **Precise null:** "the interval rules out a change larger than X".
  - **Underpowered:** "no detectable effect; the test could only detect changes
    of Y or more, so a smaller effect is not ruled out".
  - **Negative:** "the treatment reduced Z".
- **Correlation stays correlation.** Segment differences and pre/post comparisons
  are associations unless the design randomized them.

## Before / After

- **Before:** The new onboarding drove a meaningful uplift in retention and had
  no impact on revenue.
- **After:** Ship to 50%. 7-day retention rose 1.2 percentage points (40.1% →
  41.3%, 95% CI 0.3 to 2.1; 210k new users, Sept 2–16). Revenue per user moved
  +0.6%, which is not statistically significant (p=0.21). The test could not
  detect revenue changes under 2%.

## When this matters most

A/B test readouts, holdout analyses, launch reviews, and any memo where a reader
will decide something from an estimated effect.

## Sources

- Round-2 research synthesis (`notes/research-best-practices-round2-2026-11-01.md`,
  R2-4: readout slots, effect-statement slots, the three nulls). Its community
  sources are MIT/Apache, used for ideas only, and no text was copied.
- GRADE-style standardized narrative statements (ideas only, wording our own).

## Related entries

- `structure.md` — the verdict-first order is BLUF applied to a readout.
- `decision-memo.md` — when the readout feeds a decision, the memo carries the options and the change trigger.
