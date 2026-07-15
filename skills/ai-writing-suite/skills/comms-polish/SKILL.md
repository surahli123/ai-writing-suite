---
name: comms-polish
description: Polish prose that sounds AI-written while preserving meaning, facts, and author voice. Modes - detect, review, rewrite, edit - plus a 0-100 AI-tell score on demand. Use for docs, emails, posts, reports, and user-facing copy. Not for code cleanup, and not for learning or extracting an author's voice - that is voice-onboard. A mixed request to polish AND add new content routes to comms-draft, which treats the existing text as immutable source, returns the fully revised document, and runs this polish final-pass itself - polishing here never adds substance.
---

# comms-polish

Remove AI-shaped prose without turning the text into generic rewriting.

The job is narrow: preserve meaning, remove slop, keep the author's voice.

This is the suite's polish capability (formerly the standalone humanizer). It
does not carry its own pattern list — it reads the consolidated catalog under
`_shared/patterns/`, which is the single source of truth for AI tells.

Three enrichments sit alongside the catalog:

- `references/scenario-presets.md` — per-genre weighting (tweet / LinkedIn /
  README / memo): which tells matter most here, target tone/length, what to leave
  alone.
- `references/final-pass-checklist.md` — the pre-ship sweep run before returning
  any rewrite.
- `_shared/voice-profiles/` — the user's learned per-genre voices (one file per
  genre); the matching one is read when present so rewrites bias toward how *they*
  write (see Voice Matching). Legacy single-file fallback: `_shared/voice-profile.md`.

## Locating shared assets (suite root)

All `_shared/...` paths in this file are **suite-root-relative**. The suite root is the
installed directory that directly contains `_shared/` and the suite's router `SKILL.md`
(e.g. `.../ai-writing-suite/`). Do not resolve these paths against your session's working
directory. To find the root: start from this SKILL.md's own location and walk up until a
directory contains `_shared/`. If you cannot find it, say so and ask for the suite's
install path — do not guess or silently skip the shared assets.

## Pattern catalog

Before scanning or rewriting, load the consolidated catalog. Read the index first
to see what's where, then the category files relevant to the draft:

- `_shared/patterns/00-index.md` — index + how to read entries
- `_shared/patterns/lexical-tells.md` — AI vocabulary (tiered), copula avoidance, synonym cycling, false ranges, hyphen pairs, hollow intensifiers
- `_shared/patterns/significance-attribution.md` — significance/novelty inflation, vague attribution, name-dropping, promotional language, superficial -ing, speculative gap-filling, consultant-speak
- `_shared/patterns/structural-tells.md` — rule of three, negative parallelism, formulaic challenges, over-structure, inline-header lists, reshuffle immunity, treadmill effect
- `_shared/patterns/hedging-filler.md` — filler, stacked hedging, generic/future-narrative closers, confidence-calibration phrases, signposting
- `_shared/patterns/punctuation-formatting.md` — em dashes, bold overuse, emoji headers, curly quotes, title case, hashtag stuffing, placeholders, citation/UTM fingerprints
- `_shared/patterns/communication-artifacts.md` — chatbot tics, sycophancy, acknowledgment loops, cutoff disclaimers, reasoning-chain leaks, engagement hooks, emotional flatline
- `_shared/patterns/rhythm-stylometric.md` — sentence/paragraph uniformity (burstiness), low TTR, perplexity, register shift, **and the what-NOT-to-flag guardrails**
- `_shared/patterns/overstepping-presumption.md` — over-stepping (反代入式越位感): presumed cognition, strawman misconception, projected mental image, self-Q&A-as-judge. Self-scan: does the draft think *for* the reader ("you assume X / 你以为 X / Can you…? Yes —")? Flag only when the presumed prior is a **manufactured** strawman; keep it when X is a real, widespread belief (the validity condition). Judge-only — preserve legitimate contrasts.

Always apply the guardrails in `_shared/patterns/rhythm-stylometric.md`: look for
clusters, not isolated tells. These are signals, not proof.

The catalog is the rule source. The local references decide *how* to apply it:

- `references/scenario-presets.md` — weights catalog categories per genre.
- `references/final-pass-checklist.md` — the pre-ship sweep.

## Boundary

This skill edits prose, not code.

- Use for: README prose, docs, emails, reports, posts, launch notes, UX copy, and narrative summaries.
- Do not use for: source-code cleanup, architecture simplification, test rewriting, or changing program behavior.
- Preserve: facts, citations, numbers, file paths, commands, API names, quoted text, and claims unless the user explicitly asks to change them.
- Flag unsupported claims instead of inventing evidence.
- **Mixed polish-plus-add is not this skill.** If the request also asks to ADD new
  content (a new section, new material, not just rewording), hand it to
  `comms-draft`: it treats your existing text as immutable source, returns the
  fully revised whole document, and runs the final-pass itself. Polishing never
  adds substance — do not write the new section here.

## Modes

Pick the mode from the user's request. If unclear, use `rewrite`.

| Mode | Use When | Output |
| --- | --- | --- |
| `detect` | The user wants to know what sounds AI-written. | Findings and examples, no rewrite. |
| `review` | The user wants prioritized writing feedback. | Findings first, with examples. |
| `rewrite` | The user pasted text and wants a polished version. | Polished text only unless notes are requested. |
| `edit` | The user asks to modify a file. | Targeted file edits plus verification. |

## Voice Matching

Voice has three sources, in priority order:

1. **A learned per-genre voice profile** under `_shared/voice-profiles/`, produced
   by `voice-onboard` — one file per genre, the filename is the genre key. Look it
   up cheaply, before any rewrite:
   - **List** `_shared/voice-profiles/*.md` — one directory read, filenames only,
     no body parsing.
   - **Select one file** by this precedence, first match wins: (1) **explicit user
     request** — user named a genre ("use my LinkedIn voice") → that file; if it is
     absent, say so and drop to rule 4; (2) **normalized-exact preset/genre match**
     — normalize the run's genre preset and each filename slug the same way
     (lowercase, spaces→hyphens) and match by string equality, no fuzzy/prefix/alias
     (`formal-report` ≠ `report`); (3) **single-profile fallback** — exactly one
     file exists → use it; (4) **no match** → degrade (below). IF the user explicitly
     asked for their own voice, make the Q8 offer once (offer to create the
     named/needed genre; shares the one offer budget) then degrade; OTHERWISE
     degrade silently — inferred voice with no question asked. Either way, if
     profiles exist but none match, the degraded note lists which genres DO exist
     so the user can redirect.
   - **Read** the full body of the one selected file only.
   - **Directory absent or empty** → fall back to the legacy single file
     `_shared/voice-profile.md`, still gated by the `> SAMPLE PROFILE.` banner: a
     file carrying that banner counts as **no profile** (the shipped sample) →
     degrade per rule 4 (Q8 offer only on an explicit my-voice request). A profile
     is valid only with the banner absent.
   It is loose coupling: comms-polish does not create or own these files — it reads
   whatever fields are present in the selected profile and biases edits toward them.
   The profile's header set is the **canonical ordered list at the top of
   `_shared/voice-profile.md`** (the single source of truth; do not restate a
   divergent subset here). Use every header present that carries voice guidance —
   Tone, Sentence Length, Vocabulary Don't (the strongest signal), and every other
   header on that list, **including Measured Fingerprint** (the quantitative rhythm/
   punctuation targets). Read what's there; ignore what isn't — never fail on a
   missing section.
2. **A writing sample the user pastes** in this request — match it directly.
3. **Inferred voice** from the draft itself, when neither of the above exists.

**Graceful degradation:** if the source #1 lookup yields no profile (empty
`_shared/voice-profiles/` and no valid legacy file — see source #1), do not error
and do not block. Polish
normally using a pasted sample or inferred voice. The profile is a bias signal,
never a hard dependency. A hard genre constraint (e.g. a tweet's 280-char limit)
still wins over a profile preference. Any "no profile found" mention here is
**conversational** — it belongs in the chat around the deliverable, not inside the
polished `rewrite` text. (The one exception to text-only output is the
degraded-voice note in the explicit my-voice case below.)

**Voice-onboard offer budget: at most ONE offer per session, SUITE-WIDE.** The
budget is shared across the whole suite, not just this skill — an offer already
made by `comms-polish`, `comms-draft`, or the router spends it. Check the
conversation for a prior voice-onboard offer before making one; the two triggers
below also share this single budget. An offer is always offer-only: never auto-run
`voice-onboard`, never block the deliverable on it.

- **Pre-run — "in my voice" with no matching profile (Q8).** When the user
  explicitly asks for *their own* voice ("in my voice", "match how I write") and the
  source #1 lookup found no matching profile, offer `voice-onboard` once — e.g. "I
  can learn your voice from a few samples first (more accurate), or infer it from
  this draft. Which?" — offering to create the named/needed genre. If profiles exist
  but none match, say which genres DO exist so the user can redirect. **The question
  never blocks:** if the user does not answer in this turn, proceed with inferred
  voice and add the one-line degraded-voice note to the output (see Output — the
  sole text-only exception). Spends the shared offer budget.
- **Post-run / visible manual edits (owner rider).** After a polish run —
  *especially* when the user's **manual edits** to a previous output are visible in
  the session — offer to capture their voice with `voice-onboard`, noting that the
  delta between what you returned and what they changed by hand is the strongest
  voice signal there is. Which file the capture updates depends on this run: if a
  profile *resolved* (source #1), the capture updates **that genre's file**; if the
  run was degraded/inferred (no profile matched), the capture creates a **new
  `_shared/voice-profiles/<genre>.md`** for this run's genre — the edit delta seeds
  a file that did not exist. This offer is **conversational: it lives after the
  output block, not inside the polished text.** Skip it if the shared offer budget
  is already spent.

When a profile or sample exists, match:

- sentence length and rhythm
- plainness or formality
- punctuation habits
- paragraph shape
- tolerance for humor, warmth, bluntness, or personality
- preferred terms and phrases

When neither exists, use the lightest voice that fits the context:

- `technical`: precise, compact, no hype
- `professional`: clear, measured, low-drama
- `warm`: supportive and direct
- `casual`: conversational, with contractions
- `blunt`: shortest viable version

## Rewrite Workflow

1. Identify the audience, purpose, and required structure.
2. **Pick the genre preset.** Match the draft to a preset in
   `references/scenario-presets.md` (tweet / LinkedIn / README / memo). It tells
   you which catalog categories to weight harder and what to leave alone in this
   genre. If no preset fits, scan the catalog evenly.
3. **Select and load the voice profile.** Run the source #1 lookup (list
   `_shared/voice-profiles/*.md`, pick one file by the precedence, read that one
   body; legacy `_shared/voice-profile.md` on an empty directory, banner = no
   profile — see Voice Matching). No match → pasted sample or inferred voice, and
   degrade gracefully.
4. Mark the factual anchors that must survive unchanged — **and the modality
   anchors too**: each claim's observed-vs-inferred, possible-vs-certain, and
   step-toward-vs-achieved status is an anchor, not free to strengthen.
5. Scan against the pattern catalog, weighted by the preset, and remove the tells
   you find:
   - throat-clearing and filler
   - inflated significance
   - vague attribution
   - promotional adjectives
   - forced three-item lists
   - "not X but Y" theatrics
   - uniform sentence length
   - chatbot artifacts
   Before editing on any tell you find here, run the **False-positive protection
   gate** in `_shared/patterns/rhythm-stylometric.md` — any "yes" (inside a quote,
   citation, code, command, or file path; an official term of art; present in the
   voice profile; genre-normal per the preset; or a second-language construction)
   makes the flag advisory only, not an edit. An all-"no" gate is not a mandate
   either — the cluster guardrail still applies (signals, not proof).
6. Make concrete details **already in the source** more prominent — surface the
   specific actor, action, example, or consequence the text already names, instead
   of leaving it buried under an abstraction. If the source has no such detail,
   **preserve the abstraction or flag the missing detail** — never invent an
   actor, action, example, number, or consequence that is not in the source
   (Safety Rules).
7. Vary rhythm without adding fake personality. Bias word choice and cadence
   toward the voice profile when one was loaded.
8. **Re-scan your rewrite against the pattern catalog** (repeat step 5 on the *output*).
   Rewriting reintroduces tells — fixing one often plants another. Treat the rewrite as a
   fresh draft, scan it, and remove any tell you find before the final pass.
9. **Run `references/final-pass-checklist.md`** before returning anything.
10. Return the requested output and mention any claim that still needs evidence.

## Safety Rules

- Do not change the author's position to make the prose smoother.
- Do not add examples, numbers, citations, or claims that were not present.
- **Preserve epistemic modality — a protected class alongside facts, numbers, and
  quotes.** Keep each claim's modal status exactly as written: observed stays
  observed (not inferred), possible stays possible (not certain), "a step toward
  X" stays a step (not "X achieved"), an estimate stays an estimate (not a
  measurement). A smoothing pass that hardens a hedge into a fact changes the
  meaning as surely as changing a number. (This exact defect — "step toward
  improving" strengthened to "improves" — was caught by adversarial review in this
  repo on 2026-07-13.)
- Do not resolve a correlation into a cause, or a projection into a result, to
  make a sentence read cleaner.
- Do not remove caveats that carry real uncertainty.
- Do not polish away legal, medical, financial, or safety warnings.
- Do not rewrite quoted text unless the user asks.

## Before And After Examples

### Technical docs

Before:

```text
This robust workflow enables teams to seamlessly leverage contextual insights, ensuring a more effective and streamlined development experience.
```

After:

```text
This workflow gives teams contextual insights for a more effective, streamlined development experience.
```

(Every term in the *after* — workflow, teams, contextual insights, more effective,
streamlined development experience — is present in the *before*. Polish drops the
empty intensifiers ("robust", "seamlessly leverage", "enables ... ensuring"); it
adds nothing the source did not say — note it does **not** invent "editing" or any
timing the source never mentioned.)

### Status update

Before:

```text
It is important to note that the migration represents a pivotal step toward improving reliability, scalability, and operational efficiency.
```

After:

```text
The migration is a step toward more reliable, scalable, efficient operation.
```

(Every term in the *after* traces to the *before*: "step toward" **keeps the
original modality** — the migration is *aiming at* these gains, not proven to
deliver them — and the reliability/scalability/efficiency triple is inherited from
the source, not composed here (polish preserves meaning, it does not restructure
the facts). Polish strips the throat-clearing ("It is important to note that") and
the inflation ("pivotal"); it does **not** strengthen "step toward improving" into
"improves", add a fact, or restructure the claim.)

### Personal note

Before:

```text
I wanted to take a moment to express my sincere appreciation for your invaluable support throughout this journey.
```

After:

```text
Thank you for sticking with me through this.
```

(The *after* keeps only what the *before* carried — thanks for support through the
whole thing. The dropped draft closer "It helped more than you probably know"
would have invented a magnitude *and* presumed the reader's mind (an
overstepping-presumption tell in our own catalog) — polish removes slop, it does
not add either.)

## Scoring

When the user asks for a score, estimate AI-writing density on a 0-100 scale
(lower is more human). Do not claim detector certainty.

| Score | Verdict | Meaning |
| --- | --- | --- |
| 0-20 | Pristine | Reads like a specific human wrote it. |
| 21-40 | Mostly human | One or two minor tells, easy to clean. |
| 41-60 | Mixed | Half-AI half-human; partial editing likely. |
| 61-80 | AI-leaning | Multiple structural tells; detectors will probably catch it. |
| 81-100 | Pure AI smell | Wholesale chatbot output with no editing. |

Weight structural tells (rhythm uniformity, reshuffle immunity, treadmill effect)
above vocabulary hits — structure is the harder signal to mask.

## File Edits

For `edit` mode:

1. Read the file first.
2. Preserve frontmatter, headings, tables, links, code blocks, commands, and citations.
3. Make targeted prose edits only; leave already-human passages untouched.
4. Re-read the file and confirm the flagged patterns are resolved.
5. Run `git diff --check` or the repo's docs lint command when available.

## Self-improvement (human-gated)

This skill participates in the suite's human-gated self-improvement loop. The
full protocol is in `_shared/self-improvement.md`; follow it, do not restate
it. In short:

- **On start:** read `_shared/learned-rules.md` (alongside the voice profile)
  and apply any entry whose `status: active` and whose scope is `comms-polish` or
  `all`. Degrade gracefully if the file is absent.
- **On end:** if a repeatable polish correction surfaced this session, **propose**
  one candidate rule (rule + session-grounded rationale + scope `comms-polish`) and
  **wait for explicit approval** before appending it to `learned-rules.md`. Propose
  nothing if nothing repeatable surfaced.
- **Never** auto-edit this SKILL.md or the pattern catalog — approved rules live
  only in `learned-rules.md` (append-only). Each rule is eval-measured in Layer 3
  before it is trusted.

## Output

- For `rewrite`: return the polished text only unless the user asks for notes.
  Two narrow additions are sanctioned, both appended *after* the polished text,
  never woven into it:
  - **Degraded-voice line (Q8).** When the user asked for *their own* voice but no
    profile was found and you degraded to inferred voice, append a single one-line
    note — e.g. `Note: no voice profile found — inferred voice used; run
    voice-onboard to capture yours.` This is the only voice-related addition allowed.
  - **`Notes:` block for evidence flags (finding 9).** When step 6 preserved an
    abstraction for lack of a source, or step 10 found a claim still needing
    evidence, append an optional `Notes:` block listing only those
    missing-evidence / unsupported-claim flags — nothing else. Omit the block when
    there are none. (Conversational voice-onboard offers stay outside the output
    block entirely, per Voice Matching — do not fold them in here.)
- For `detect` or `review`: follow the **Audit Report Contract** below.
- For `edit`: summarize changed files, what improved, verification, and any preserved uncertainty.

### Audit Report Contract (detect / review only)

`detect` and `review` output is a fixed report so two audits of the same draft —
even by different models — can be diffed and skimmed. Produce these sections **in
this order**. Inside each section the wording is yours (genre-appropriate); the
structure below is the contract, not a straitjacket.

**Conformance is byte-literal for structure, normalized for punctuation style.**
Section headings, the four field markers (`**Quote:**` / `**Tell:**` / `**Why:**`
/ `**Fix:**`), their order, and the tier names must appear exactly as written
here — that's what makes two reports diffable. Straight `"..."`, typographic
`"..."`, and guillemet `«...»` quotes are treated as equivalent wherever a quoted
snippet is required (paste-from-Word and model output both carry typographic
quotes routinely); a leading byte-order-mark is stripped before checking. Genre
flexibility applies to the *prose inside* each field, never to the markers,
order, or tier names themselves.

**This contract governs `detect` and `review` output only. `rewrite` and `edit`
are unchanged by it** — a rewrite still returns polished text, an edit still
returns its file summary.

1. **Lead line — the one biggest problem, in plain words.** First line, format
   `**Biggest problem:** <one sentence>`. Name the single worst thing a reader
   would react to (Ogilvy: lead with the one thing). Plain language, **never a
   number** — the 0-100 score is not the lead, and severity never collapses into a
   single headline figure.

2. **Findings, grouped under three named severity tiers, each tier defined.**
   Use `## Critical`, `## Moderate`, `## Minor` headings in that order. The line
   immediately under each heading is a one-clause *italic* definition of the tier,
   so two audits sort the same finding the same way:
   - **Critical** — *tells that make the whole piece read as machine-written at a
     glance, or that distort meaning or trust.*
   - **Moderate** — *clear tells a careful reader notices, but that don't dominate
     the piece.*
   - **Minor** — *cosmetic or low-frequency tells only a scan catches.*
   A tier with no findings still keeps its heading and definition, with a single
   `- None.` bullet and **no other bullets in that tier** — `- None.` never sits
   alongside real findings in the same tier.
   Every finding uses this four-part shape, **in exactly this order, once each**:
   - `**Quote:**` the exact snippet from the draft, quoted (not paraphrased).
   - `**Tell:**` the catalog id + name it matches — e.g. `S1 — Significance
     inflation` — and the id **must** be a real entry from `_shared/patterns/`.
   - `**Why:**` one line on why it reads as AI.
   - `**Fix:**` the corrected snippet, **shown** — quoted or in a code span —
     never just described in prose.

3. **`## What already reads well`.** One or two genuinely strong things, tied to a
   specific passage, so the report is calibrated instead of a pile-on. Per the
   repo's review standard, **no fake praise**: if nothing reads well yet, say so
   plainly (e.g. `- Nothing here reads well yet — the draft is AI throughout.`).

4. **Score — only when asked, always last.** When the user requested a score,
   place the 0-100 AI-tell score as the **final non-blank line of the entire
   report** — nothing follows it, no trailing commentary or sign-off —
   `**AI-tell score:** NN/100`, scored per the Scoring table. Never as the lead;
   omit it entirely when no score was requested.

A complete worked example built from real catalog tells is in
`references/audit-report-format.md`.
