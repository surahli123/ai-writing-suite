<!--
  FIXTURE — BAD voice profile (the PLANTED POSITIVE; expected to FAIL).

  Same H2 contract as the good profile — that is the point. The header check
  (test_voice_contract.py's contract) passes on this file, and it is still wrong.
  Shape is not quality; only the content checks in run_voice_extraction.py can tell
  these two artifacts apart.

  Its declared failure modes (run_voice_extraction.py asserts EACH one trips; if any
  stops tripping, the checker is broken and the run fails):
    - learns_habit_word   : never mentions "ledger" (4x) — misses the real habit
    - omits_noise_word    : promotes "kaleidoscope" (2x) to a signature word — the
                            classic "learn an accident as a habit" error the SKILL warns about
    - lists_absence       : never mines the absences ("delve"/"leverage", 0x)
    - splits_genres       : flattens tweets and memos into one averaged figure
    - no_invented_traits  : claims "synergy", which appears 0x in the corpus
    - honest_gap          : fills every field confidently; nothing marked Unknown
-->

# Host Profile — Mara Quill (fictional, synthetic corpus)

## Meta

- **Author:** Mara Quill (fictional — synthetic eval corpus)
- **Extracted:** 2026-07-13
- **Sample count:** 5
- **Sample sources:** mixed writing
- **Sample time span:** synthetic — no real dates
- **Confidence:** High

## Tone

- Visionary and energetic, with a strong collaborative streak.

> Evidence: "Nobody reads them. Cut three."

## Sentence Length

- **Average words/sentence:** 15
- **Short sentences (<10 words) share:** 50%
- **Long sentences (>30 words) share:** 20%
- **Rhythm habit:** consistently medium-length sentences with steady, even pacing.

> Evidence: "Cut three."

## Vocabulary

- **First person:** "we"
- **Signature words:** "kaleidoscope", "synergy"
- **Stock phrases / tics:** opens with a rhetorical question.
- **Domain / in-group terms:** dashboards, alignment

## Vocabulary Do

- Reaches for vivid visual metaphor: "kaleidoscope".
- Frames team work as "synergy" between functions.

## Vocabulary Don't

- Avoids the word "furthermore".

## Signature Moves

- Opens with a rhetorical question, then answers it in the next line.

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

- **Applies to:** all of her writing.
- **Re-calibrate for:** nothing — the profile generalizes.

## Changelog

- [2026-07-13] First created from 5 synthetic samples.
