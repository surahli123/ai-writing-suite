<!--
  FIXTURE — GOOD tweet-scoped voice profile (expected to PASS every check).

  Scoped to ONE genre on purpose. voice-onboard/SKILL.md Step 1: "Mixed genres →
  offer to extract two profiles rather than averaging them into a blur." The corpus
  is mixed (tweets + memos), so the spec-correct artifact is a PAIR of genre-scoped
  profiles, not one blended profile. (The previous "good" artifact here was blended,
  and averaged the two genres' rhythm into a single figure — it committed the exact
  failure this eval exists to detect.)

  What makes it good, per SKILL.md Step 2, all counts WITHIN the tweet genre:
    - learns the 4x habit word ("ledger" clears the 3+ rule in tweets)
    - does NOT learn the 2x noise word ("kaleidoscope" fails the 3+ rule) and does
      not learn the 1x sub-threshold decoy ("forecast")
    - does NOT import the memo genre's habit word ("queue" is 0x in tweets)
    - mines the absences ("delve" / "leverage", 0x) into Vocabulary Don't
    - reports the TWEET rhythm, not the blended cross-genre mean
    - writes "Unknown — not enough signal" where the tweets carry no evidence
-->

# Host Profile — Mara Quill, tweets (fictional, synthetic corpus)

## Meta

- **Author:** Mara Quill (fictional — synthetic eval corpus)
- **Genre scope:** tweet (a separate memo profile covers her long-form register)
- **Extracted:** 2026-07-13
- **Sample count:** 5 tweets
- **Sample time span:** synthetic — no real dates
- **Confidence:** Low (5 samples, one genre)

## Tone

- Blunt and unsentimental. States the result, then the cost, then stops. No warm-up,
  no reassurance.

> Evidence: "Shipped the pricing ledger today. Two weeks late. It works."

## Sentence Length

Scoped to tweets. Her memo rhythm is a different profile; a figure blended across
both would describe neither genre.

- **tweet — average words/sentence:** 4 (nothing in the samples runs past ~6 words)
- **Rhythm habit (tweet):** three-beat drop — claim, cost, verdict.

> Evidence (tweet): "Every forecast is a story. The ledger is the fact. Trust the ledger."

## Vocabulary

- **First person:** absent from the tweets — subject-less imperatives instead
  ("Trust the ledger", "Cut three").
- **Signature words:** "ledger" — 4 occurrences across 5 tweets, the only word in
  this genre that clears the 3+ bar.
- **Stock phrases / tics:** Unknown — not enough signal. Nothing else in the tweets
  repeats 3 or more times, and one occurrence is an accident, not a habit.
- **Domain / in-group terms:** Unknown — not enough signal in 5 short samples.

## Vocabulary Do

- Names the concrete artifact rather than the abstraction: "ledger", not "the data".

## Vocabulary Don't

<!-- STRONGEST signal: zero occurrences across the whole genre. -->
- "delve" — 0 occurrences. Never reaches for it.
- "leverage" — 0 occurrences. Never reaches for it.
- No hype register anywhere in the tweets.

## Signature Moves

- Three beats and out: claim, cost, verdict.
- Ends on the flat consequence, never on a summary.

## Punctuation & Formatting

- **Period vs comma:** period-heavy. Short declaratives, one clause each.
- **Em-dash density:** never — 0 em-dashes across all 5 tweets.
- **Ellipsis / exclamation:** 0 of each.
- **Lists:** none in the samples.
- **Emoji:** 0 in the samples.

## Openings & Closings

- **Opening habit:** leads with the fact or the object, never with a scene.
- **Closing habit:** ends on a two-or-three-word verdict.

> Evidence (open): "Shipped the pricing ledger today."
> Evidence (close): "It works."

## Uncertainty Style

- Unknown — not enough signal in samples. No tweet hedges, quantifies confidence, or
  softens a claim, so this dimension stays blank rather than guessed.

## Things To Avoid

### Self-report Divergence

- **Stated:** the author reported using exclamation marks frequently.
- **Measured contradiction:** 0 exclamation marks across the 5 tweet samples; this
  contradicts the self-report, so the feature is not learned as a tweet trait.

- Marketing register and hype adjectives — absent from every tweet.
- kaleidoscope — 2 occurrences in this genre, under the 3+ bar. It is an accident of
  two posts, not a signature word; do not write it back into her voice.
- Softening a late delivery. She states the slip plainly ("Two weeks late.").

## Scope & Calibration

- **Applies to:** her tweets — terse, public, three beats.
- **Re-calibrate for:** memos and any long-form register — see the memo profile; do
  not carry these figures across.

## Verbatim Anchors

- "Shipped the pricing ledger today." — direct factual opening
- "Two weeks late." — unsoftened cost beat
- "It works." — flat verdict closing

## Changelog

- [2026-07-13] First created from 5 synthetic tweet samples.
