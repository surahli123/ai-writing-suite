<!--
  FIXTURE — GOOD memo-scoped voice profile (expected to PASS every check).

  The second half of the spec-correct pair. voice-onboard/SKILL.md Step 1: "Mixed
  genres → offer to extract two profiles rather than averaging them into a blur."
  Every count below is WITHIN the memo genre.

    - learns the 4x habit word ("queue") and the 3x "dashboards" — both clear 3+
    - does NOT learn the 2x noise word ("kaleidoscope") or the 2x decoy ("boring")
    - does NOT import the tweet genre's habit word ("ledger" is 0x in memos)
    - mines the absences ("delve" / "leverage", 0x) into Vocabulary Don't
    - reports the MEMO rhythm (~32 words/sentence), not the blended cross-genre mean
    - writes "Unknown — not enough signal" where the memos carry no evidence
-->

# Host Profile — Mara Quill, memos (fictional, synthetic corpus)

## Meta

- **Author:** Mara Quill (fictional — synthetic eval corpus)
- **Genre scope:** memo (a separate tweet profile covers her short public register)
- **Extracted:** 2026-07-13
- **Sample count:** 3 internal memos
- **Sample time span:** synthetic — no real dates
- **Confidence:** Low (3 samples, one genre)

## Tone

- Flat, argued, unhurried. Builds the case in one long breath, then lands it with a
  short flat sentence. No hedging and no pep.

> Evidence: "The fix is boring: retry with backoff, alert on queue depth, and reconcile the numbers every morning before anyone looks at a chart."

## Sentence Length

Scoped to memos. Her tweet rhythm is a different profile; a figure blended across
both genres would describe neither.

- **memo — average words/sentence:** 32 (long, clause-stacked, held together by
  coordinating conjunctions rather than full stops)
- **Rhythm habit (memo):** one long argued sentence, then a shorter one to land it.

> Evidence (memo): "Every incident this quarter traces back to the same queue, and I would rather spend a week making that queue boring than spend another month explaining a kaleidoscope of dashboards to people who have already stopped trusting them."

## Vocabulary

- **First person:** "I" (3 occurrences) — she owns the argument rather than hiding
  behind the team.
- **Signature words:** "queue" (4 occurrences across 3 memos) and "dashboards"
  (3 occurrences). Both clear the 3+ bar in this genre.
- **Stock phrases / tics:** Unknown — not enough signal. Nothing else repeats 3 or
  more times across the memos.
- **Domain / in-group terms:** Unknown — not enough signal in 3 samples.

## Vocabulary Do

- Names the mechanism, not the outcome: the failure is a "queue", not "an issue".
- Sets the reliable artifact against the flattering one: "dashboards" are what she
  argues with, never what she trusts.

## Vocabulary Don't

<!-- STRONGEST signal: zero occurrences across the whole genre. -->
- "delve" — 0 occurrences. Never reaches for it.
- "leverage" — 0 occurrences. Never reaches for it.
- No hype register anywhere in the memos.

## Signature Moves

- **Not X but Y** reframe: "the cause was not the product but a queue that silently
  dropped retries after midnight".
- Ends on the consequence, not the summary.

## Punctuation & Formatting

- **Period vs comma:** comma-heavy inside long sentences; few sentence breaks.
- **Em-dash density:** never — 0 em-dashes across all 3 memos.
- **Ellipsis / exclamation:** 0 of each.
- **Lists:** a colon, then an inline series ("retry with backoff, alert on queue
  depth, and reconcile the numbers").
- **Emoji:** 0 in the samples.

## Openings & Closings

- **Opening habit:** opens on the finding or the number, never on a scene.
- **Closing habit:** closes on what the reader must now do or accept.

> Evidence (open): "Our onboarding funnel lost eleven percent of new accounts last month"
> Evidence (close): "a morning spent reconstructing what the system was doing while the rest of us slept."

## Uncertainty Style

- Unknown — not enough signal in samples. The memos assert throughout; none hedges or
  quantifies confidence, so this dimension stays blank rather than guessed.

## Things To Avoid

### Self-report Divergence

- **Stated:** the author reported using exclamation marks frequently.
- **Measured contradiction:** 0 exclamation marks across the 3 memo samples; this
  contradicts the self-report, so the feature is not learned as a memo trait.

- Marketing register and hype adjectives — absent from every memo.
- kaleidoscope — 2 occurrences in this genre, under the 3+ bar. A vivid word used
  twice is an accident, not a signature; do not write it back into her voice.
- boring — 2 occurrences, also under the bar. Do not promote it to a habit.

## Scope & Calibration

- **Applies to:** her internal memos — long, argued, one thesis each.
- **Re-calibrate for:** tweets and any short public register — see the tweet profile;
  do not carry these figures across.

## Changelog

- [2026-07-13] First created from 3 synthetic memo samples.
