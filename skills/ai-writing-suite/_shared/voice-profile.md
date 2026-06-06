<!--
================================================================================
  voice-profile.md  —  CANONICAL VOICE PROFILE (CONTRACT FILE)
================================================================================

  WHAT THIS IS
  ------------
  This is a SAMPLE/EXAMPLE voice profile. It is shipped filled-in so you can see
  the shape, but it is meant to be OVERWRITTEN per user. `voice-onboard` produces
  the real one by interviewing you + reading your writing samples.

  WHY IT EXISTS (the contract)
  ----------------------------
  Think of this file as a SHARED SCHEMA between two skills, the way a feature
  table is a contract between the pipeline that writes it and the model that
  reads it:
    - WRITER:  `voice-onboard`  fills this in from your samples.
    - READER:  `comms-polish`   reads it every run to match YOUR voice instead
               of imposing a generic "clean" register.

  Because both sides depend on it, the FIELD NAMES below are stable. Treat the
  `## H2 headers` as the column names of the contract. Add evidence and detail
  under them freely, but do not rename or drop the headers, or `comms-polish`
  will silently fall back to generic behavior (a silent-fallback bug we want to
  avoid).

  EVERY claim needs sample evidence. No evidence -> leave the field "Unknown"
  rather than inventing a trait. A profile built on guesses is worse than no
  profile, because `comms-polish` will trust it.

  STATUS OF THIS FILE: example only. Replace via `voice-onboard`.
================================================================================
-->

# Voice Profile

> SAMPLE PROFILE. Replace by running `voice-onboard`. The example below is a
> fictional author ("Sam, a data-scientist who blogs about search ranking") so
> the field shapes are concrete. Your real profile overwrites all of it.

## Meta

- **Author:** Sam (example)
- **Extracted:** 2026-06-06
- **Sample count:** 7
- **Sample sources:** personal blog posts, internal memos
- **Sample time span:** 2025-11 to 2026-05
- **Confidence:** Medium  <!-- Low if N<5, Medium if 5-10, High if 10+ -->

## Tone

<!-- The overall register. One or two sentences, plus the dominant flavor. -->
Direct and analytical, with dry humor. Confident but not salesy. Reads like a
practitioner explaining a tradeoff to a peer, not a brand talking to a market.

> Evidence: "The reranker helped NDCG by 2 points. It also doubled our latency,
> which nobody wanted to talk about."

## Sentence Length

<!-- Quantify. comms-polish uses this to avoid flattening rhythm to one length. -->
- **Average words/sentence:** ~16
- **Short sentences (<10 words) share:** ~30%
- **Long sentences (>30 words) share:** ~10%
- **Rhythm habit:** opens with a short punchy claim, then a longer sentence that
  qualifies it. "Claim. Then the caveat."

> Evidence: "It worked. But only because the query distribution was unusually
> clean that quarter, and we never re-tested on the messy tail."

## Vocabulary

- **First person:** uses "I" for opinions, "we" for team work; rarely subject-less.
- **Signature words:** "tradeoff", "signal", "tail", "calibrate", "noisy".
- **Stock phrases / tics:** "the honest answer is...", "in practice".
- **Domain / in-group terms:** NDCG, reranker, query understanding, holdout.

## Vocabulary Do

<!-- Words/constructions the author DOES reach for. comms-polish may keep these. -->
- Concrete metrics over adjectives ("2 points" not "significantly").
- Hedging that is quantified ("about 70% sure") rather than vague.

## Vocabulary Don't

<!-- The forbidden list. THIS IS THE STRONGEST SIGNAL. Words the author never
     uses are more diagnostic than words they do. comms-polish must avoid these. -->
- Never: "delve", "leverage", "synergy", "unlock", "in today's fast-paced world".
- Never: exclamation-point hype ("Amazing results!").
- Never: em-dash-heavy throat-clearing intros.

## Signature Moves

<!-- The structural fingerprints: how this author characteristically builds a
     point. These are positive patterns comms-polish can preserve. -->
- "Not X, but Y" reframes to correct a common assumption.
- Drops a number early to anchor the claim, then explains it.
- Ends on a concrete consequence, not a summary.

## Punctuation & Formatting

- **Period vs comma:** period-heavy; short declaratives over long comma chains.
- **Em-dash density:** occasional, for asides.
- **Ellipsis / exclamation:** ellipsis rare; exclamation almost never.
- **Lists:** uses bullets for tradeoffs; avoids numbered steps in prose.
- **Emoji:** none.

## Openings & Closings

- **Opening habit:** leads with the counterintuitive result or a number.
- **Closing habit:** lands on a specific consequence or open question, not a
  motivational wrap-up.

> Evidence (open): "We shipped the model nobody on the team liked."
> Evidence (close): "So the real question is whether the tail ever gets clean."

## Uncertainty Style

<!-- How the author signals they're unsure. comms-polish should match this rather
     than flattening everything to false confidence. -->
- Quantified and explicit ("about 60% confident", "I haven't tested the edge case").

## Things To Avoid

<!-- A catch-all for author-specific anti-patterns that don't fit the forbidden
     vocabulary list: structures, registers, or moves that read as "not them". -->
- Marketing register / superlatives.
- Symmetric "on one hand / on the other hand" balance that dodges a stance.
- Over-explaining domain terms to an expert audience.

## Scope & Calibration

<!-- A profile is genre-specific. Note where it applies and where it needs a
     fresh pass, so comms-polish doesn't misapply blog voice to a formal report. -->
- **Applies to:** blog posts, internal memos, LinkedIn.
- **Re-calibrate for:** formal external reports, customer-facing comms.

## Changelog

<!-- voice-onboard appends here on each update. Living file, not a one-shot. -->
- 2026-06-06: Example profile shipped as the schema contract (placeholder).

<!--
  ATTRIBUTION
  -----------
  Field set adapted from:
    - weijt606/anti-vibe-writing (host-profile-template.md, MIT) — the 10-dimension
      voice taxonomy (sentence length, vocabulary, punctuation rhythm, openings/
      closings, uncertainty style).
    - donghuixin/AI-Vibe-Writing-Skills (1_style_extractor.md, MIT) — the
      Do's / Don'ts "Style DNA" framing.
  Both MIT-licensed; see the suite NOTICE.md for full copyright lines.
-->
