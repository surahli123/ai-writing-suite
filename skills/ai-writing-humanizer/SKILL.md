---
name: ai-writing-humanizer
description: Polish prose that sounds AI-written while preserving meaning, facts, and author voice. Use for docs, emails, posts, reports, and user-facing copy; do not use for code cleanup.
---

# AI Writing Humanizer

Use this skill to remove AI-shaped prose without turning the text into generic rewriting.

The job is simple: preserve meaning, remove slop, keep the author's voice.

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
| `rewrite` | The user pasted text and wants a polished version. | Polished text only unless notes are requested. |
| `edit` | The user asks to modify a file. | Targeted file edits plus verification. |
| `review` | The user wants prioritized writing feedback. | Findings first, with examples. |

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
3. Remove common AI tells:
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

When the user asks for a score, estimate AI-writing density. Do not claim detector certainty.

| Score | Meaning |
| --- | --- |
| 0-15 | Natural, specific, varied. |
| 16-35 | Mostly human, with a few model tells. |
| 36-60 | Noticeably AI-shaped. |
| 61-85 | Heavy AI smell. |
| 86-100 | Template-like or full of chatbot artifacts. |

## File Edits

For `edit` mode:

1. Read the file first.
2. Preserve frontmatter, headings, tables, links, code blocks, commands, and citations.
3. Make targeted prose edits only.
4. Run `git diff --check` or the repo's docs lint command when available.

## Output

- For `rewrite`: return the polished text only unless the user asks for notes.
- For `detect` or `review`: lead with findings and examples.
- For `edit`: summarize changed files, what improved, verification, and any preserved uncertainty.
