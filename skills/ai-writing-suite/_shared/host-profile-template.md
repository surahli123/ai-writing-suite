<!--
================================================================================
  host-profile-template.md  —  BLANK VOICE FORM
================================================================================

  WHAT THIS IS
  ------------
  The reusable blank form that `voice-onboard` fills in, one field at a time,
  from your interview answers + writing samples. When complete, its contents
  are written to `<state>/voice-profiles/<genre-slug>.md` (one file per genre),
  with `<state>` resolved through `_shared/state-location.md`. The legacy
  `voice-profile.md` is the shipped sample + fallback, never the write target.

  HOW TO USE
  ----------
  Copy this file. Fill each field from the user's samples. Keep the SAME H2
  headers as `voice-profile.md` — that file is the contract, this is its blank
  twin. Renaming headers here breaks the hand-off.

  THE ONE RULE
  ------------
  Every field needs sample evidence. No evidence -> write "Unknown — not enough
  signal in samples". Do NOT invent a trait to fill a blank. A guessed profile
  is worse than an empty one, because the reader skill will trust it.

  CONFIDENCE
  ----------
  A trait counts only if it shows up 3+ times. One occurrence is noise, not a
  habit. With <5 samples, mark Confidence = Low and fill conservatively.
================================================================================
-->

# Host Profile — [author name]

## Meta

- **Author:** [name / id]
- **Genre:** [genre-slug, matching this file's name, e.g. blog / linkedin / formal-report]  <!-- self-description; the FILENAME is the source of truth on conflict -->
- **Extracted:** [YYYY-MM-DD]
- **Sample count:** [N]
- **Sample sources:** [blog / LinkedIn / X / internal memos / other]
- **Sample time span:** [earliest — latest]
- **Confidence:** [Low (N<5) / Medium (5-9) / High (10+)]

## Tone

- [overall register in 1-2 sentences: e.g. direct / warm / dry / formal]

> Evidence: [paste 1 sentence that shows the tone]

## Sentence Length

- **Average words/sentence:** [number]
- **Short sentences (<10 words) share:** [%]
- **Long sentences (>30 words) share:** [%]
- **Rhythm habit:** [e.g. "short hook, then long qualifier"; or "Unknown"]

> Evidence: [paste 1-2 sentences]

## Vocabulary

- **First person:** ["I" / "we" / subject-less / depends]
- **Signature words:** [3-8 distinctive words, after stripping generic ones]
- **Stock phrases / tics:** [list, or "none obvious"]
- **Domain / in-group terms:** [3-5]

## Vocabulary Do

- [words / constructions the author actively reaches for]

## Vocabulary Don't

<!-- STRONGEST signal. Common words the author NEVER uses. -->
- [forbidden words: e.g. "delve", "leverage", "unlock", hype punctuation]

## Signature Moves

- [characteristic ways they build a point: e.g. "not X but Y" reframes, leads
  with a number, ends on a consequence]

## Punctuation & Formatting

- **Period vs comma:** [period-heavy / comma-heavy / balanced]
- **Em-dash density:** [often / occasional / never]
- **Ellipsis / exclamation:** [density]
- **Lists:** [uses bullets? numbered steps?]
- **Emoji:** [yes / no / which ones / position]

## Openings & Closings

- **Opening habit:** [scene / claim / question / number / contrarian / other]
- **Closing habit:** [hook / consequence / open question / trails off / other]

> Evidence (open): "[paste original opening]"
> Evidence (close): "[paste original closing]"

## Uncertainty Style

- [quantified ("70% sure") / blunt ("I don't know") / hedged ("perhaps") / avoids]

> Evidence: [paste 1 sentence]

## Things To Avoid

- [author-specific anti-patterns beyond the forbidden word list: registers,
  structures, moves that read as "not them"]

## Scope & Calibration

- **Applies to:** [genres these samples cover]
- **Re-calibrate for:** [genres not covered — flag so the reader doesn't misapply]

## Verbatim Anchors

<!-- Exactly 3 anchors, separate from the 10 style dimensions. Each quoted line
     must be copied verbatim from a declared sample (a whitespace-normalized
     substring), and each tag names exactly one habit that line proves. -->
- "<verbatim line from a sample>" — <the single habit it proves>
- "<verbatim line from a sample>" — <the single habit it proves>
- "<verbatim line from a sample>" — <the single habit it proves>

## Measured Fingerprint

<!--
  QUANTITATIVE half of the profile. Produced by `_shared/stylometry.py`, NOT by
  eyeballing. Every number here must be RECOMPUTABLE from the stated samples +
  the constants in stylometry.py — that is what lets the eval assert on numbers
  instead of on adjectives. A number with no provenance is worse than no number.

  HARD RULES (both enforced by voice-onboard):
    - PER GENRE. One `### <genre>` block per genre. NEVER pool genres into one
      block — pooling a tweet and a report yields a mean/variance that describes
      neither (see stylometry.py --demo). If samples span two genres, run two
      blocks.
    - 3+ samples. Below 3 samples the block still prints but every number is
      marked indicative-only; do not present it as an established habit.
    - CJK / non-whitespace scripts AT OR ABOVE 20% of letters: stylometry.py
      emits NO numbers and writes an UNSUPPORTED line instead. Never hand-fill
      numbers it refused to compute.
    - CJK BELOW 20% (a genuinely mixed-script sample): the numbers still print,
      but they only measure the whitespace-delimited (non-CJK) portion — the
      CJK fraction never matches the word/sentence tokenizer, so it is silently
      excluded unless flagged. Copy stylometry.py's `partial_scripts` field into
      a **Caveat** line (below) whenever it is present. A block with CJK content
      and no Caveat line is a silent-partial-measurement bug, not a clean pass.
    - No content: empty/whitespace-only/zero-word samples get an UNSUPPORTED
      line too (`reason=no_content`) — never a silent all-zero block.

  Copy the `### <genre>` block once per genre. The lines below mirror
  `stylometry.py` output verbatim, so what the user confirmed is what is stored.
-->

### [genre — e.g. blog]

- **Provenance:** genre=[genre], N=[sample count], [word count] words, confidence=[Insufficient(N<3) / Low / Medium / High]
- **Caveat (if any CJK content below the 20% refuse threshold):** [partial_scripts: e.g. "CJK 12% excluded from tokenization"] <!-- omit this line entirely when stylometry.py reports no partial_scripts -->
- **Sentence length:** mean=[x], variance=[x], burstiness(CV)=[x] over [n] sentences  <!-- variance is the rhythm signal, not the mean -->
- **Punctuation /1k words:** em-dash=[x], semicolon=[x], ellipsis=[x], exclamation=[x]
- **Testable numbers:** [x] per 100 words ([n] figures)  <!-- version strings (v1.1) stripped; bare 1900-2099 years excluded by design -->
- **AI-register words:** [n] hits across [n] terms checked  <!-- 0 is the strong signal; list offenders if nonzero -->
- **Function-word deltas /1k (vs generic baseline):** over-uses [word +x, ...]; under-uses [word -x, ...]
- **Char 3-gram top:** ['gram' freq, ...]

<!-- For a CJK-dominant (>=20%) or no-content genre, replace the block body with
     a single line instead of the fields above:
  - **UNSUPPORTED (CJK):** CJK / non-whitespace script — no stylometry numbers (v2). N=[n]
  - **UNSUPPORTED (no_content):** samples empty / zero measurable words. N=[n] -->

## Changelog

- [YYYY-MM-DD] First created from N samples.
- [YYYY-MM-DD] [added/removed trait X — reason: user said "X felt off"]

<!--
  ATTRIBUTION
  -----------
  Adapted from weijt606/anti-vibe-writing host-profile-template.md (MIT):
  ported from Chinese to English and aligned to the suite's voice-profile.md
  field contract. Do's/Don'ts framing borrowed from
  donghuixin/AI-Vibe-Writing-Skills 1_style_extractor.md (MIT). Full copyright
  lines in the suite NOTICE.md. Bilingual (Chinese) path = v2 per design D-scope.
-->
