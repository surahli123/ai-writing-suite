<!--
  FIXTURE — BAD tweet-scoped voice profile (the PLANTED POSITIVE; expected to FAIL).

  Same 10-H2 contract as the good profile — that is the point. test_voice_contract.py's
  header check passes on this file and it is still wrong. Shape is not quality.

  Its declared failure modes (run_voice_extraction.py asserts EACH one trips; if any
  stops tripping, the checker is broken, not the profile):
    - learns_habit_word     : never claims "ledger" (4x in tweets) — misses the habit
    - omits_noise_word      : promotes "kaleidoscope" (2x, under the bar) to a
                              signature word — the accident-as-habit error
    - no_subthreshold_claims: claims "forecast" (1x) as a signature word
    - no_invented_traits    : claims "synergy" (0x) and asserts exclamation marks,
                              em-dashes and emoji the corpus does not contain; also
                              imports "queue", which is 0x in tweets (it belongs to
                              the memo genre — this is what cross-genre pooling does)
    - lists_absence         : never mines the 0x absences ("delve" / "leverage")
    - genre_scoped_rhythm   : reports the BLENDED cross-genre mean (13) as the tweet
                              figure — the averaging failure the SKILL forbids
    - honest_gap            : fills Uncertainty Style confidently on zero evidence
    - scope_declared        : claims to generalize to all of her writing
    - anchor_provenance     : includes an anchor absent from every tweet sample
    - self_report_divergence: adopts the false stated exclamation-mark habit and
                              never surfaces its contradiction with the corpus
-->

# Host Profile — Mara Quill, tweets (fictional, synthetic corpus)

## Meta

- **Author:** Mara Quill (fictional — synthetic eval corpus)
- **Genre scope:** all of her writing
- **Extracted:** 2026-07-13
- **Sample count:** 8 samples, pooled
- **Sample time span:** synthetic — no real dates
- **Confidence:** High

## Tone

- Visionary and energetic, with a strong collaborative streak.

> Evidence: "Nobody reads them. Cut three."

## Sentence Length

- **Average words/sentence:** 13
- **Short sentences (<10 words) share:** 50%
- **Rhythm habit:** consistently medium-length sentences with steady, even pacing.

> Evidence: "Cut three."

## Vocabulary

- **First person:** "we"
- **Signature words:** "kaleidoscope", "forecast", "synergy"
- **Stock phrases / tics:** opens with a rhetorical question.
- **Domain / in-group terms:** queue depth, alignment

## Vocabulary Do

- Reaches for vivid visual metaphor: "kaleidoscope".
- Frames team work as "synergy" between functions.

## Vocabulary Don't

- Avoids the word "furthermore".

## Signature Moves

- Opens with a rhetorical question, then answers it in the next line.
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
> Evidence (close): "Cut three."

## Uncertainty Style

- Hedged: softens claims with "perhaps" and "it may be that".

## Things To Avoid

- Being too blunt with stakeholders.

## Scope & Calibration

- **Applies to:** all of her writing, tweets and memos alike.
- **Re-calibrate for:** nothing — the profile generalizes.

## Verbatim Anchors

- "Shipped the pricing ledger today." — direct factual opening
- "Two weeks late." — unsoftened cost beat
- "The moonlit ledger sings in perfect harmony." — lyrical closing

## Changelog

- [2026-07-13] First created from 8 synthetic samples, pooled across genres.
