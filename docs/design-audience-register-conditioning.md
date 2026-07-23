# Design — Audience and Register Conditioning (E3)

Date: 2026-07-22
Status: DESIGN ONLY — no profile or consumer contract is changed in this lane

## Problem and boundary

The suite currently learns one profile per genre. A `memo` profile can capture
how an author writes memos, but not that the same author is terse with peers,
more explicit with executives, and procedural in a PR review. Today
`voice-onboard` would either flatten those differences or require genre names to
carry a second, undeclared meaning.

The existing contract is load-bearing:

- the filename remains the genre key;
- `_shared/voice-profile.md` defines exactly 15 ordered H2 headers;
- `voice-onboard` writes those headers;
- `comms-polish` and `comms-draft` select one genre file and read it by header.

Register conditioning must be an optional, sparse layer inside that contract. It
must not create a second competing profile schema or make existing profiles
invalid.

## Model: baseline voice plus sparse register delta

The baseline body under each H2 remains the author's genre-level voice. A
register overlay records only evidence-backed differences for a recurring
audience/channel context:

```text
effective voice = genre baseline + selected register delta
```

Genre answers "what kind of artifact is this?" Register answers "how does this
author adapt that artifact for this audience and channel?" Examples include
`slack-peer`, `exec-review`, `pr-review`, and `public-customer`. Register IDs are
free-form slugs matching `[a-z0-9-]+`; they are not a fixed global taxonomy.

The layer is sparse by design. If evidence shows no register-specific difference
for punctuation, that register has no punctuation overlay and inherits the
baseline. Absence is not filled with a plausible stereotype.

## File shape without a new H2

The genre file path and 15 H2 headers remain unchanged. Baseline content stays
directly under each existing H2. Optional register deltas use H3 blocks within
the H2 they qualify:

```markdown
## Tone

Direct and analytical. States the tradeoff before the recommendation.

### Register: slack-peer

Warmer and more compressed; uses fragments when the thread supplies context.

### Register: exec-review

Names the decision and consequence before implementation detail.
```

No `## Register` header is added. No existing H2 is renamed, removed, repeated,
or reordered. The `Meta` body lists available register slugs:

```markdown
- **Register overlays:** slack-peer, exec-review
```

`Scope & Calibration` records sample counts, dates, and confidence per register.
`Verbatim Anchors` and `Measured Fingerprint` may carry H3 overlays when the
register has its own evidence. `Changelog` records overlay additions and
recalibrations.

The exact H3 grammar is `### Register: <slug>`. A future parser rejects duplicate
slugs within one H2 and rejects a slug not declared in `Meta`. The baseline is
the H2 content before the first register H3.

Existing files with no register H3s remain byte-for-byte valid. Existing
consumers must not encounter overlay-bearing files until they can parse the H3
grammar; otherwise reading the whole H2 could blend every register. The rollout
order is therefore binding:

1. teach both consumers to read the baseline plus at most one selected overlay,
   while verifying unchanged behavior on current profiles;
2. update the profile-contract eval and template to allow the optional H3 shape;
3. teach `voice-onboard` to write overlays;
4. only then create the first overlay-bearing real profile.

This is a compatibility migration, not a producer-only format change.

## Register selection

Genre selection runs first and remains exactly as today. After one genre file is
selected, the consumer resolves at most one register:

1. an explicit user request for a register slug;
2. a normalized-exact register supplied by the chosen scenario/channel context;
3. no register, which means baseline only.

Selection is lowercase, spaces-to-hyphens, exact string equality. There is no
fuzzy, prefix, or semantic matching. A requested register that is absent is
reported and falls back to baseline; it never selects the nearest name.

Audience prose alone does not silently manufacture a register ID. A scenario may
map a known channel to a declared register only when that mapping is explicit in
the run context. If two axes matter independently, such as `slack` and
`executive`, the producer creates one evidence-backed combined slug only when
the samples support that recurring context. The design deliberately avoids
stacking multiple overlays, which would create unmeasured interactions.

## Producer evidence rules

`voice-onboard` continues to group by genre first. Within a genre, it may propose
a register split only when:

- the samples identify a recurring audience/channel context;
- each proposed register has at least three samples, with the existing profile
  confidence thresholds still disclosed;
- the same dimension differs repeatedly across contexts;
- the user confirms that the split reflects how they actually adapt their
  writing.

One occurrence is noise. A generic belief such as "executive writing is more
formal" is not author evidence. When the corpus is too thin, the genre baseline
is written and the register is marked unlearned rather than invented.

Register overlays use the same sample-evidence, absence-mining, honest-gap, and
verbatim-provenance rules as baseline voice. A baseline trait is not copied into
every overlay; inheritance is implicit.

## Consumer application

A future consumer parses each selected H2 into:

```text
baseline_text
register_overlays[slug]
```

It applies baseline guidance first and the selected sparse delta second. A
register delta may narrow or override the same dimension, but only for that run.
It cannot alter factual anchors, safety rules, genre form constraints, or the
voice-over-catalog precedence policy.

The consumer's output note records the selected genre and register. When no
overlay matches, it says baseline was used rather than implying that register
conditioning occurred.

## Acceptance criteria

- The genre filename contract and all 15 canonical H2 headers remain unchanged,
  ordered, and required.
- Profiles without register overlays produce the same selection and guidance as
  before.
- Optional overlays use only `### Register: <slug>` blocks inside existing H2s;
  no sixteenth H2 or parallel profile schema is introduced.
- The baseline is always readable without a register, and one run applies at
  most one normalized-exact overlay.
- An absent or ambiguous register falls back to baseline without fuzzy matching
  or invented traits.
- Overlay claims meet the same evidence, honest-gap, and provenance rules as the
  baseline and are sparse deltas rather than copied profiles.
- Both by-header consumers gain parsing support and regression coverage before
  `voice-onboard` can emit an overlay-bearing file.
- Contract tests cover legacy profiles, one valid overlay, missing-register
  fallback, duplicate/undeclared slugs, and preservation of all 15 headers.

**Falsifiable next step:** Using at least 10 consented samples each for one
author's `slack-peer` and `pr-review` contexts within a single genre, derive
sparse overlays and run a blind owner preference test on 12 held-out rewrite
pairs. If the context-matched overlay is not preferred over baseline in at least
8 of 12 pairs, or if a legacy consumer test changes output on a no-overlay
profile, the register layer adds noise or breaks compatibility and must not be
built as designed.
