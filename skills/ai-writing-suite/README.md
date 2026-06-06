# AI Writing Suite

Polish prose that sounds AI-written without changing what the author meant.

The differentiator is not "rewrite this better." It is:

```text
preserve meaning, remove AI slop, keep author voice
```

Use it when a draft has the usual model tells: filler, vague claims, inflated importance, forced structure, and rhythm that sounds too even.

## What It Does

`ai-writing-suite` helps an agent:

1. identify the audience and purpose
2. preserve facts, citations, numbers, commands, and claims
3. remove AI-shaped prose patterns
4. match the author's voice or the document's register
5. return either a rewrite, a review, a detection score, or targeted file edits

## When To Use It

Use this skill for:

- docs and README prose
- emails and status updates
- social posts and personal notes
- reports and summaries
- launch notes and user-facing copy

Do not use it for source-code cleanup. Use a code cleanup or refactoring skill for that.

## Modes

| Mode | Purpose |
| --- | --- |
| `detect` | Find AI tells and estimate density without rewriting. |
| `rewrite` | Produce polished prose from pasted text. |
| `edit` | Modify a prose file in place while preserving structure. |
| `review` | Give prioritized writing findings without rewriting everything. |

## Examples

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

## Good For

- making generated drafts sound less generic
- tightening verbose status updates
- removing hype from technical docs
- matching an author's sample instead of replacing their voice
- reviewing prose before publishing

## Not For

- changing facts to sound better
- adding evidence that is not in the draft
- editing source code
- removing necessary uncertainty or safety warnings
- rewriting quoted text without permission

## Install

Clone or copy this repo, then symlink the skill into your Codex skills directory:

```bash
ln -s "$(pwd)/skills/ai-writing-suite" ~/.codex/skills/ai-writing-suite
```

Restart Codex so the skill list refreshes.

## Attribution

This is an independently packaged public skill adapted from a local personal writing-polish workflow. It uses high-level ideas from anti-slop and humanizer writing guides while avoiding wholesale reuse of their catalogs.

See [`NOTICE.md`](NOTICE.md) for the reuse boundary.
