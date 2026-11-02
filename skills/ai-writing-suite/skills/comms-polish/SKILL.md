---
name: comms-polish
description: "Edit existing prose so it reads like a person wrote it, without changing facts, numbers, hedges, or the author's voice. Use when the user asks to polish, clean up, de-AI, proofread, lightly edit, or review a draft (Slack update, email, memo, readout, README, post), or asks what in it sounds AI-written. Modes are rewrite, light-edit, review, detect, and file edit, with an optional AI-pattern density score. Not for adding new sections or content (that is comms-draft), learning a voice (voice-onboard), answering playbook questions (comms-qa), or code."
---

# comms-polish

Remove AI-shaped prose without turning the text into generic rewriting.

The job is narrow: preserve meaning, remove slop, keep the author's voice.

This is the suite's polish capability (formerly the standalone humanizer). It
does not carry its own pattern list — it reads the consolidated catalog under
`_shared/patterns/`, which is the single source of truth for AI tells.

Three enrichments sit alongside the catalog:

- `references/scenario-presets.md` — per-genre weighting (tweet / LinkedIn /
  README / memo / PR description / release note): which tells matter most here,
  target tone/length, what to leave alone.
- `references/final-pass-checklist.md` — the pre-ship sweep run before returning
  any rewrite.
- resolved `<state>/voice-profiles/` — the user's learned per-genre voices (one file per
  genre); the matching one is read when present so rewrites bias toward how *they*
  write (see Voice Matching). Legacy single-file fallback: `_shared/voice-profile.md`.

## Locating shared assets (suite root)

All `_shared/...` paths in this file are **suite-root-relative**. The suite root is the
installed directory that directly contains `_shared/` and the suite's router `SKILL.md`
(e.g. `.../ai-writing-suite/`). Do not resolve these paths against your session's working
directory. To find the root: start from this SKILL.md's own location and walk up until a
directory contains `_shared/`. If you cannot find it, say so and ask for the suite's
install path — do not guess or silently skip the shared assets.

Resolve all mutable profile and learned-rules paths through
`_shared/state-location.md`; reference that resolver, never copy its rules here.

## Pattern catalog

Before scanning or rewriting, load the consolidated catalog. Start with:

- `_shared/patterns/00-index.md` — index, entry format, category descriptions,
  and the generated inventory of current category files.

Treat that generated inventory as the authoritative file list. For a targeted
rewrite, read the category files whose descriptions match the draft. For a
detect/review request or other comprehensive scan, read every category file
listed in the generated inventory. Do not maintain a second filename list here.

Always apply the guardrails in `_shared/patterns/rhythm-stylometric.md`: look for
clusters, not isolated tells. These are signals, not proof.

The catalog is the rule source. The local references decide *how* to apply it:

- `references/scenario-presets.md` — weights catalog categories per genre.
- `references/final-pass-checklist.md` — the pre-ship sweep.

For factual or analytical prose, also load
`_shared/fact-interpretation-boundary.md`. It governs whether a fact supports an
attached cause, motive, significance, trend, or conclusion. Catalog cues locate
the bridge; the available source evidence decides whether it is warranted.

## Boundary

This skill edits prose, not code.

Follow the suite-wide content trust boundary in `_shared/untrusted-content.md`.

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
| `light-edit` | The user asks for a light edit, a proofread, minimal changes, or to keep their voice. | Only sentences with a named failure change; clean text comes back unchanged. |
| `edit` | The user asks to modify a file. | Targeted file edits plus verification. |

## Edit restraint (all modes that change text)

**Match the edit to the request** (owner ruling 2026-11-01):

- **`light-edit`** (light edit, proofread, minimal changes, keep my voice): every
  sentence starts as kept. Unchanged is a valid result.
- **`rewrite`** (polish, clean up, make it read better): also make readability
  improvements that change no meaning, wherever they help the reader. Examples:
  paragraph breaks in a wall of text, a lead that reaches the point, consistent
  formatting across list items, typo and grammar fixes, a clunky sentence made
  plain. Return the text unchanged only when it is already as readable as it can
  be.

In both modes:

- **Change a sentence only for a failure you can name.** Valid failures:
  - a grammar or spelling error;
  - an ambiguity;
  - a factual mismatch with a source the user supplied;
  - a house-style or preset rule;
  - filler that carries nothing;
  - a *cluster* of AI tells;
  - in `rewrite` only, a readability problem the reader would notice.

  A single catalog match is not a failure on its own; apply the cluster
  guardrail and the false-positive gate. In `light-edit`, filler and tell
  clusters count only when they hurt clarity.
- **Fix the wording, keep the claim.** When slop wording carries the author's
  stance (an evaluation like "it was valuable"), an attribution ("analysts
  expect"), a commitment, or a conclusion, rewrite the words and keep that
  content. Never move an attributed claim onto the author.
- **Restructure only when it helps a judgment document.** Answer-first or pyramid
  reordering is for documents that ask the reader to accept a conclusion or
  decision. Leave timelines, runbooks, logs, tutorials, thank-you notes and
  exploratory notes in their own order. Keep terse genres (Slack, status,
  incident updates) terse; do not expand bullets into prose. A light cleanup of
  terse text is still welcome when asked for: consistent bullet formatting,
  typos, and an unclear abbreviation spelled out once.
- **If nothing has a named failure, return the text unchanged** and say so in one
  line of notes.

## Voice Matching

Voice has three sources, in priority order:

1. **A learned per-genre voice profile** under resolved `<state>/voice-profiles/`, produced
   by `voice-onboard` — one file per genre, the filename is the genre key. Before
   any rewrite, follow the canonical lookup, fallback, banner-rejection,
   graceful-degradation, and Q8 offer rules in `_shared/voice-lookup.md`.
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

**Voice precedence over the catalog (C3 ruling, 2026-07-15).** When a construction
is both a learned voice habit (in the loaded profile's samples or fields) and a
listed catalog tell, **the voice profile wins in that author's own writing**: it is
their voice by definition, so the tell may be noted as advisory, never auto-edited.
This is the same outcome the false-positive gate's question 3 enforces per flag —
stated here as policy so no future catalog entry overrides it.

**Graceful degradation:** if the source #1 lookup yields no profile (empty
resolved `<state>/voice-profiles/` and no valid legacy file — see source #1), do not error
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
  `<state>/voice-profiles/<genre>.md`** for this run's genre — the edit delta seeds
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
   `references/scenario-presets.md` (tweet / LinkedIn / README / memo / PR
   description / release note). It tells you which catalog categories to weight
   harder and what to leave alone in this genre. If no preset fits, scan the
   catalog evenly.
3. **Select and load the voice profile.** Run the source #1 lookup (list
   and select through `_shared/voice-lookup.md`, then read only the selected
   body). No match → pasted sample or inferred voice, and degrade gracefully.
4. Mark the factual anchors that must survive unchanged — **and the modality
   anchors too**: each claim's observed-vs-inferred, possible-vs-certain, and
   step-toward-vs-achieved status is an anchor, not free to strengthen. Establish
   source completeness at the same time: when an **independent source packet** is
   supplied, classify its confirmed facts, supported interpretations, and
   unanswered questions. When the draft is the only material, preserve every
   substantive author interpretation and state that support was not assessed;
   the draft is not independent proof that its own analysis is unsupported.
5. Scan against the pattern catalog, weighted by the preset, and remove the tells
   you find:
   - throat-clearing and filler
   - inflated significance
   - vague attribution
   - promotional adjectives
   - forced three-item lists
   - "not X but Y" theatrics
   - uniform sentence length in running prose
   - chatbot artifacts
   Before editing on any tell you find here, run the **False-positive protection
   gate** in `_shared/patterns/rhythm-stylometric.md` — any "yes" (inside a quote,
   citation, code, command, or file path; an official term of art; present in the
   voice profile; genre-normal per the preset; or a second-language construction)
   makes the flag advisory only, not an edit. An all-"no" gate is not a mandate
   either — the cluster guardrail still applies (signals, not proof).
   For a parallel set (status list, feed, cards, titles), follow
   `references/scenario-presets.md` → "Parallel items": one shape is correct
   there, and status, actor, order and facts never change.
6. Apply the shared fact-to-interpretation protocol to each bridge that adds a
   cause, motive, significance, trend, or conclusion. Preserve a supported
   relation and its certainty; use co-occurrence wording for timing alone; retain
   calibrated possibility. A source packet the user supplies with the request
   authorizes factual alignment. If it shows a substantive author interpretation
   exceeds the evidence, cut the unsupported bridge or restate it at the strength
   the source allows, and say what changed in `Notes:`. Never change it silently.
   This covers claims, not decisions. The author's own recommendation or plan
   is never rewritten to fit the notes: keep it and flag the gap in `Notes:`.
   Preserve the position and flag it instead only when the user asked you not to
   change the substance. Without a packet, delete only a **redundant gloss** that
   carries no position or useful information. In review mode, keep the exact
   quote and offer a fact-only repair through `Quote / Tell / Why / Fix`.
7. Make concrete details **already in the source** more prominent — surface the
   specific actor, action, example, or consequence the text already names, instead
   of leaving it buried under an abstraction. If the source has no such detail,
   **preserve the abstraction or flag the missing detail** — never invent an
   actor, action, example, number, or consequence that is not in the source
   (Safety Rules).
8. In running prose, let rhythm follow the content (R1); the items of a
   parallel set keep one shape (R1 validity condition). Add no fake
   personality. Bias word choice and cadence
   toward the voice profile when one was loaded. Treat its `Verbatim Anchors` as
   fidelity anchors: bias the rewrite toward reproducing each tagged habit under
   `_shared/precedence-policy.md`, without copying unrelated sample content.
9. **Re-scan your rewrite against the pattern catalog** (repeat step 5 on the *output*).
   Rewriting reintroduces tells — fixing one often plants another. Treat the rewrite as a
   fresh draft, scan it, and remove any tell you find before the final pass.
10. **Run `references/final-pass-checklist.md`** before returning anything.
11. Return the requested output and mention any claim that still needs evidence.

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
- **Keep quantitative and scope wording exact.** These are protected like
  numbers:
  - **Scope words:** only, all, most, every, never, first, at least, up to.
  - **Approximators:** "roughly 60%" never becomes "60%".
  - **Units of change:** percentage points never become percent, and relative
    never becomes absolute.
  - **Date precision:** a specific date stays specific.
  - **Statistical status:** "not statistically significant" or "no detectable
    effect" never becomes "no effect". A stated interval stays with its effect.
  - **Attribution and intent verbs:** "suggests" never becomes "shows",
    "expects" never becomes "will", and "we hope to" or "we plan to" never
    becomes "we will".
- Do not remove caveats that carry real uncertainty.
- **Do not add caveats the source lacks either.** No new qualifications,
  limits, or negative scoping ("this does not by itself establish…", "results
  should be interpreted with caution"), even when the user asks for something
  "more rigorous" or "review-proof". A rewrite that hedges a claim the author
  stated plainly changes its meaning as surely as one that hardens a hedge. If a
  claim looks under-supported, say so in notes and let the author decide.
- Do not polish away legal, medical, financial, or safety warnings.
- Do not rewrite quoted text unless the user asks.

For worked before/after examples, read
`references/before-after-examples.md`.

## Scoring

When the user asks for a score, estimate **AI-pattern density** on a 0-100 scale
(lower = fewer catalogued patterns). The score describes surface patterns in this
text. It is **not** evidence of who or what wrote it: human writers trip these
patterns, AI-edited human text scores differently from AI-drafted text, and no
detector can tell editing from drafting. Never state or imply authorship ("this
was written by AI"), and never present the number as a detector prediction.
Named, quoted findings are the evidence; the number only summarizes their density.

| Score | Band | Meaning |
| --- | --- | --- |
| 0-20 | Clean | Few or no catalogued patterns. |
| 21-40 | Light | One or two minor patterns, easy to clean. |
| 41-60 | Mixed | Patterns in several places; partial cleanup needed. |
| 61-80 | Heavy | Multiple structural patterns throughout. |
| 81-100 | Saturated | Patterns in nearly every sentence. |

When you give a score in a report, put a `**Coverage:**` line directly before
it. The Coverage line says which categories you checked by rule, which by
judgment, and what you did not check. End the score line with "(surface
patterns only, not authorship)". The exact format is in
`references/audit-report-contract.md`.

Weight structural tells (rhythm uniformity, reshuffle immunity, treadmill effect)
above vocabulary hits — structure is the harder signal to mask.

## File Edits

For `edit` mode:

When the target is a rendered artifact — a component or page whose visible copy
comes from a static file, template, generated output, JS render, sidecar, or
deploy copy — read `references/artifact-preflight.md` and
`references/artifact-density-budget.md` first. Plain Markdown and email keep the
lightweight path below.

1. Read the file first.
2. Preserve frontmatter, headings, tables, links, code blocks, commands, and citations.
3. Make targeted prose edits only; leave already-human passages untouched.
4. Re-read the file and confirm the flagged patterns are resolved.
5. Run `git diff --check` or the repo's docs lint command when available.

## Self-improvement (human-gated)

This skill participates in the suite's human-gated self-improvement loop. The
full protocol is in `_shared/self-improvement.md`; follow it, do not restate
it. In short:

- **On start:** read resolved `<state>/learned-rules.md` (alongside the voice profile)
  and apply any entry whose `status: active` and whose scope is `comms-polish` or
  `all`. Degrade gracefully if the file is absent.
- **On end:** if a repeatable polish correction surfaced this session, **propose**
  one candidate rule (rule + session-grounded rationale + scope `comms-polish`) and
  **wait for explicit approval** before appending it to resolved `<state>/learned-rules.md`. Propose
  nothing if nothing repeatable surfaced.
- **Never** auto-edit this SKILL.md or the pattern catalog — approved rules live
  only in resolved `<state>/learned-rules.md` (append-only). Each rule is eval-measured in Layer 3
  before it is trusted.

## Output

- For `rewrite`: return the polished text only unless the user asks for notes.
  Two narrow additions are sanctioned, both appended *after* the polished text,
  never woven into it:
  - **Degraded-voice line (Q8).** When the user asked for *their own* voice but no
    profile was found and you degraded to inferred voice, append a single one-line
    note — e.g. `Note: no voice profile found — inferred voice used; run
    voice-onboard to capture yours.` This is the only voice-related addition allowed.
  - **`Notes:` block (finding 9).** Append an optional `Notes:` block that holds
    exactly four classes of item, each with its location, and nothing else:
    - evidence flags: a source-to-claim gap (step 6), an abstraction preserved
      for lack of a source (step 7), or a claim still needing evidence (step 11);
    - alignment changes: what step 6 changed to match a user-supplied source,
      and why;
    - decision-gap flags: an author's recommendation kept as written although
      the notes support less (owner ruling R1, claims not decisions);
    - consistency conflicts from the final pass ("The document agrees with
      itself").

    Omit the block when there are none. (Conversational voice-onboard offers stay outside the output
    block entirely, per Voice Matching — do not fold them in here.)
- For `detect` or `review`: follow the **Audit Report Contract** below.
- For `edit`: summarize changed files, what improved, verification, and any preserved uncertainty.

### Audit Report Contract (detect / review only)

This contract governs `detect` and `review` output only.
`rewrite` and `edit` are unchanged by it.

Full field-by-field contract in `references/audit-report-contract.md` — read it
when producing `detect`/`review` output.

A complete worked example built from real catalog tells is in
`references/audit-report-format.md`.
