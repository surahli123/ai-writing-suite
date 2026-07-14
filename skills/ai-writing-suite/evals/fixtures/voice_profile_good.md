<!--
  FIXTURE — GOOD voice profile (expected to PASS every check).

  A pre-authored artifact standing in for what voice-onboard SHOULD produce from
  voice_corpus.json. It is graded by run_voice_extraction.py, not by a model.
  It follows _shared/host-profile-template.md's H2 contract exactly.

  What makes it "good", per voice-onboard/SKILL.md Step 2:
    - learns the 4x habit word ("ledger" clears the 3+ rule)
    - does NOT learn the 2x noise word (fails the 3+ rule; one accident is not a habit)
    - mines the absences: "delve" / "leverage" appear 0x -> Vocabulary Don't
    - splits sentence length by genre instead of averaging tweets and memos into a blur
    - writes "Unknown — not enough signal" where the corpus carries no evidence
-->

# Host Profile — Mara Quill (fictional, synthetic corpus)

## Meta

- **Author:** Mara Quill (fictional — synthetic eval corpus)
- **Extracted:** 2026-07-13
- **Sample count:** 5
- **Sample sources:** 3 tweets, 2 internal memos
- **Sample time span:** synthetic — no real dates
- **Confidence:** Low (N<5 per genre; 3 tweets + 2 memos)

## Tone

- Blunt and unsentimental. States the result, then the cost, then stops. No warm-up,
  no reassurance.

> Evidence: "Shipped the pricing ledger today. Two weeks late. It works."

## Sentence Length

Split by genre — the two genres have genuinely different rhythm, so a single average
would describe neither.

- **tweet — average words/sentence:** 4 (short sentences dominate; nothing over ~6 words)
- **memo — average words/sentence:** 31 (long, clause-stacked, held together by "and" / "but")
- **Rhythm habit (tweet):** three-beat drop — claim, cost, verdict.
- **Rhythm habit (memo):** one long argued sentence, then a short flat one to land it.

> Evidence (tweet): "Every forecast is a story. The ledger is the fact. Trust the ledger."
> Evidence (memo): "The revenue ledger we maintain in finance is the only artifact in this company that has never lied to us, and I would rather ship a forecast late than ship one that disagrees with it."

## Vocabulary

- **First person:** "I" in memos; subject-less imperatives in tweets.
- **Signature words:** "ledger" (4 occurrences across both genres — the clearest habit in
  the corpus), "forecast", "dashboards"
- **Stock phrases / tics:** none clears the 3+ bar. Everything else in the samples is a
  single occurrence — noise, not habit.
- **Domain / in-group terms:** finance reconciliation, funnel, queue depth

## Vocabulary Do

- Reaches for concrete nouns over abstractions: "ledger", "queue", "logs".
- Calls the unglamorous fix what it is: "boring".

## Vocabulary Don't

<!-- STRONGEST signal: zero occurrences across the whole corpus. -->
- "delve" — 0 occurrences. Never reaches for it.
- "leverage" — 0 occurrences. Never reaches for it.
- No hype register anywhere in the samples; no exclamation marks.

## Signature Moves

- **Not X but Y** reframe: "the cause was not the product but a queue that silently
  dropped retries".
- Ends a memo on the consequence, not the summary.

## Punctuation & Formatting

- **Period vs comma:** period-heavy in tweets; comma-heavy inside long memo sentences.
- **Em-dash density:** never — 0 em-dashes across all 5 samples.
- **Ellipsis / exclamation:** 0 of each.
- **Lists:** uses a colon then an inline series ("retry with backoff, alert on queue
  depth, and reconcile").
- **Emoji:** Unknown — not enough signal in samples.

## Openings & Closings

- **Opening habit:** leads with the fact or the number, never with a scene.
- **Closing habit:** ends on a consequence or a flat verdict.

> Evidence (open): "Our onboarding funnel lost eleven percent of new accounts last month"
> Evidence (close): "It works."

## Uncertainty Style

- Unknown — not enough signal in samples. The corpus contains no hedged or quantified
  uncertainty claims, so this dimension stays blank rather than guessed.

## Things To Avoid

- Marketing register and hype adjectives — absent from every sample.
- Softening a late delivery. She states the slip plainly ("Two weeks late.").

## Scope & Calibration

- **Applies to:** terse public tweets and long internal memos.
- **Re-calibrate for:** any longer public genre (essay, blog, talk) — no samples cover it.

## Changelog

- [2026-07-13] First created from 5 synthetic samples (3 tweets, 2 memos).
