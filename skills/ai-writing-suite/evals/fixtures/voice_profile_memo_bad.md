<!--
  FIXTURE — BAD memo-scoped voice profile (the PLANTED POSITIVE; expected to FAIL).

  Same 10-H2 contract as the good memo profile — it passes test_voice_contract.py's
  header check and is still wrong on content.

  Its declared failure modes (each MUST trip):
    - learns_habit_word     : never claims "queue" (4x in memos) — misses the habit
    - omits_noise_word      : promotes "kaleidoscope" (2x, under the bar) to a
                              signature word
    - no_subthreshold_claims: claims "boring" (2x) as a construction she reaches for
    - no_invented_traits    : claims "synergy" (0x) and asserts exclamation marks,
                              em-dashes and emoji the memos do not contain; also
                              imports "ledger", which is 0x in memos — it is the
                              TWEET genre's habit word, and pooling is how it got here
    - lists_absence         : never mines the 0x absences ("delve" / "leverage")
    - genre_scoped_rhythm   : reports the BLENDED cross-genre mean (13) instead of the
                              memo figure (~32) — the averaging failure the SKILL forbids
    - honest_gap            : fills Uncertainty Style confidently on zero evidence
    - scope_declared        : claims to generalize to all of her writing
    - anchor_provenance     : includes an anchor absent from every memo sample
-->

# Host Profile — Mara Quill, memos (fictional, synthetic corpus)

## Meta

- **Author:** Mara Quill (fictional — synthetic eval corpus)
- **Genre scope:** all of her writing
- **Extracted:** 2026-07-13
- **Sample count:** 8 samples, pooled
- **Sample time span:** synthetic — no real dates
- **Confidence:** High

## Tone

- Upbeat and motivational, with a knack for the memorable image.

> Evidence: "Cut three."

## Sentence Length

- **Average words/sentence:** 13
- **Rhythm habit:** even, medium-length sentences throughout; pacing does not shift.

> Evidence: "It works."

## Vocabulary

- **First person:** "we"
- **Signature words:** "kaleidoscope", "ledger", "synergy"
- **Stock phrases / tics:** closes on a rallying line.
- **Domain / in-group terms:** alignment, roadmap

## Vocabulary Do

- Reaches for vivid visual metaphor: "kaleidoscope".
- Calls her own fixes "boring" as a self-deprecating move.
- Frames cross-team work as "synergy".

## Vocabulary Don't

- Avoids the word "furthermore".

## Signature Moves

- Opens with a rhetorical question, then answers it.
- Frequent exclamation marks; heavy em-dash use for emphasis.

## Punctuation & Formatting

- **Period vs comma:** balanced.
- **Em-dash density:** often.
- **Ellipsis / exclamation:** frequent exclamation marks for emphasis.
- **Lists:** numbered steps.
- **Emoji:** yes, usually a rocket at the end of a launch post.

## Openings & Closings

- **Opening habit:** rhetorical question.
- **Closing habit:** upbeat call to action.

> Evidence (open): "Every forecast is a story."
> Evidence (close): "It works."

## Uncertainty Style

- Hedged: softens claims with "perhaps" and "it may be that".

## Things To Avoid

- Being too blunt with stakeholders.

## Scope & Calibration

- **Applies to:** all of her writing, memos and tweets alike.
- **Re-calibrate for:** nothing — the profile generalizes.

## Verbatim Anchors

- "The fix is boring: retry with backoff, alert on queue depth, and reconcile the numbers every morning before anyone looks at a chart." — colon-led inline action list
- "Our onboarding funnel lost eleven percent of new accounts last month" — number-led finding
- "The moonlit queue sings in perfect harmony." — lyrical closing

## Changelog

- [2026-07-13] First created from 8 synthetic samples, pooled across genres.
