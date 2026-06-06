---
name: comms-polish
description: Polish prose that sounds AI-written while preserving meaning, facts, and author voice. Modes - detect, review, rewrite, edit - plus a 0-100 AI-tell score on demand. Use for docs, emails, posts, reports, and user-facing copy; do not use for code cleanup.
---

# comms-polish

Remove AI-shaped prose without turning the text into generic rewriting.

The job is narrow: preserve meaning, remove slop, keep the author's voice.

This is the migrated base of the suite's polish capability (formerly the
standalone humanizer). It does not carry its own pattern list — it reads the
consolidated catalog under `../../_shared/patterns/`, which is the single source
of truth for AI tells. Enrichment (scenario presets, a final-pass checklist,
voice-profile matching) lands in a later layer; this file is the base only.

## Pattern catalog

Before scanning or rewriting, load the consolidated catalog. Read the index first
to see what's where, then the category files relevant to the draft:

- `../../_shared/patterns/00-index.md` — index + how to read entries
- `lexical-tells.md` — AI vocabulary (tiered), copula avoidance, synonym cycling, false ranges, hyphen pairs, hollow intensifiers
- `significance-attribution.md` — significance/novelty inflation, vague attribution, name-dropping, promotional language, superficial -ing, speculative gap-filling, consultant-speak
- `structural-tells.md` — rule of three, negative parallelism, formulaic challenges, over-structure, inline-header lists, reshuffle immunity, treadmill effect
- `hedging-filler.md` — filler, stacked hedging, generic/future-narrative closers, confidence-calibration phrases, signposting
- `punctuation-formatting.md` — em dashes, bold overuse, emoji headers, curly quotes, title case, hashtag stuffing, placeholders, citation/UTM fingerprints
- `communication-artifacts.md` — chatbot tics, sycophancy, acknowledgment loops, cutoff disclaimers, reasoning-chain leaks, engagement hooks, emotional flatline
- `rhythm-stylometric.md` — sentence/paragraph uniformity (burstiness), low TTR, perplexity, register shift, **and the what-NOT-to-flag guardrails**

Always apply the guardrails in `rhythm-stylometric.md`: look for clusters, not
isolated tells. These are signals, not proof.

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

Infer voice from the text unless the user provides a writing sample.

When a sample exists, match:

- sentence length and rhythm
- plainness or formality
- punctuation habits
- paragraph shape
- tolerance for humor, warmth, bluntness, or personality
- preferred terms and phrases

When no sample exists, use the lightest voice that fits the context:

- `technical`: precise, compact, no hype
- `professional`: clear, measured, low-drama
- `warm`: supportive and direct
- `casual`: conversational, with contractions
- `blunt`: shortest viable version

## Rewrite Workflow

1. Identify the audience, purpose, and required structure.
2. Mark the factual anchors that must survive unchanged.
3. Scan against the pattern catalog and remove the tells you find:
   - throat-clearing and filler
   - inflated significance
   - vague attribution
   - promotional adjectives
   - forced three-item lists
   - "not X but Y" theatrics
   - uniform sentence length
   - chatbot artifacts
4. Replace vague abstractions with concrete actors, actions, examples, or consequences.
5. Vary rhythm without adding fake personality.
6. Return the requested output and mention any claim that still needs evidence.

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

## Output

- For `rewrite`: return the polished text only unless the user asks for notes.
- For `detect` or `review`: lead with findings and examples, grouped by severity.
- For `edit`: summarize changed files, what improved, verification, and any preserved uncertainty.
