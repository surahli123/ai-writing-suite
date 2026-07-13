---
name: comms-polish
description: Polish prose that sounds AI-written while preserving meaning, facts, and author voice. Modes - detect, review, rewrite, edit - plus a 0-100 AI-tell score on demand. Use for docs, emails, posts, reports, and user-facing copy. Not for code cleanup, and not for learning or extracting an author's voice - that is voice-onboard. A mixed request to polish AND add a new section or content routes to comms-draft - polishing never adds substance.
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
- `_shared/voice-profile.md` — the user's learned voice, read when present
  so rewrites bias toward how *they* write (see Voice Matching).

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
- `lexical-tells.md` — AI vocabulary (tiered), copula avoidance, synonym cycling, false ranges, hyphen pairs, hollow intensifiers
- `significance-attribution.md` — significance/novelty inflation, vague attribution, name-dropping, promotional language, superficial -ing, speculative gap-filling, consultant-speak
- `structural-tells.md` — rule of three, negative parallelism, formulaic challenges, over-structure, inline-header lists, reshuffle immunity, treadmill effect
- `hedging-filler.md` — filler, stacked hedging, generic/future-narrative closers, confidence-calibration phrases, signposting
- `punctuation-formatting.md` — em dashes, bold overuse, emoji headers, curly quotes, title case, hashtag stuffing, placeholders, citation/UTM fingerprints
- `communication-artifacts.md` — chatbot tics, sycophancy, acknowledgment loops, cutoff disclaimers, reasoning-chain leaks, engagement hooks, emotional flatline
- `rhythm-stylometric.md` — sentence/paragraph uniformity (burstiness), low TTR, perplexity, register shift, **and the what-NOT-to-flag guardrails**
- `overstepping-presumption.md` — over-stepping (反代入式越位感): presumed cognition, strawman misconception, projected mental image, self-Q&A-as-judge. Self-scan: does the draft think *for* the reader ("you assume X / 你以为 X / Can you…? Yes —")? Flag only when the presumed prior is a **manufactured** strawman; keep it when X is a real, widespread belief (the validity condition). Judge-only — preserve legitimate contrasts.

Always apply the guardrails in `rhythm-stylometric.md`: look for clusters, not
isolated tells. These are signals, not proof.

The catalog is the rule source. The local references decide *how* to apply it:

- `references/scenario-presets.md` — weights catalog categories per genre.
- `references/final-pass-checklist.md` — the pre-ship sweep.

## Boundary

This skill edits prose, not code.

- Use for: README prose, docs, emails, reports, posts, launch notes, UX copy, and narrative summaries.
- Do not use for: source-code cleanup, architecture simplification, test rewriting, or changing program behavior.
- Preserve: facts, citations, numbers, file paths, commands, API names, quoted text, and claims unless the user explicitly asks to change them.
- Flag unsupported claims instead of inventing evidence.

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

1. **A learned voice profile** at `_shared/voice-profile.md`. This is produced
   by the `voice-onboard` sub-skill.
   **Before any rewrite, check whether this file exists and read it if it does.**
   It is loose coupling: comms-polish does not create or own that file — it reads
   whatever fields are present and biases edits toward them. Sections to use when
   present: Tone, Sentence Length, Vocabulary Do / Vocabulary Don't, Signature
   Moves, Punctuation & Formatting, Openings & Closings, Uncertainty Style, Things
   To Avoid, and Scope & Calibration (which says where the profile applies). Read
   what's there; ignore what isn't — never fail on a missing section.
2. **A writing sample the user pastes** in this request — match it directly.
3. **Inferred voice** from the draft itself, when neither of the above exists.

**Graceful degradation:** if `_shared/voice-profile.md` is absent, do not error
and do not block. Note briefly that no profile was found, then polish normally
using a pasted sample or inferred voice. The profile is a bias signal, never a
hard dependency. A hard genre constraint (e.g. a tweet's 280-char limit) still
wins over a profile preference.

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
3. **Load the voice profile if present.** Check for `_shared/voice-profile.md`
   and read it if it exists; otherwise use a pasted sample or inferred voice
   (see Voice Matching). Degrade gracefully when absent.
4. Mark the factual anchors that must survive unchanged.
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
6. Replace vague abstractions with concrete actors, actions, examples, or consequences.
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
This workflow gives teams the context they need before they start editing.
```

### Status update

Before:

```text
It is important to note that the migration represents a pivotal step toward improving reliability, scalability, and operational efficiency.
```

After:

```text
The migration removes the retry job that caused last week's duplicate sends.
```

### Personal note

Before:

```text
I wanted to take a moment to express my sincere appreciation for your invaluable support throughout this journey.
```

After:

```text
Thank you for sticking with me through this. It helped more than you probably know.
```

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
  one candidate rule (rule + session-grounded rationale + scope) and **wait for
  explicit approval** before appending it to `learned-rules.md`. Propose nothing
  if nothing repeatable surfaced.
- **Never** auto-edit this SKILL.md or the pattern catalog — approved rules live
  only in `learned-rules.md` (append-only). Each rule is eval-measured in Layer 3
  before it is trusted.

## Output

- For `rewrite`: return the polished text only unless the user asks for notes.
- For `detect` or `review`: lead with findings and examples, grouped by severity.
- For `edit`: summarize changed files, what improved, verification, and any preserved uncertainty.
