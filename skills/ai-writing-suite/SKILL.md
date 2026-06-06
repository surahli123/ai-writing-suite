---
name: ai-writing-suite
description: A suite of writing-assistant skills for professional and product communication — polish/de-AI prose, learn an author's voice, and (later) answer questions from a knowledge base and draft from it. Routes a request to the right sub-skill. Use for docs, emails, posts, reports, and user-facing copy; not for source-code cleanup.
---

# AI Writing Suite (router)

This is a thin router. It does not contain polishing or drafting logic itself —
it points the host at the sub-skill that does the work. Think of it as the
dispatch layer in front of four specialized writers.

## Sub-skills

| Sub-skill | What it does | Status |
| --- | --- | --- |
| `comms-polish` | Polish, review, detect, or edit prose to remove AI tells while preserving meaning and voice. 0-100 AI-tell score on demand. | **available (v1)** |
| `voice-onboard` | Interview the author and distill their historical writing into a reusable voice profile that `comms-polish` reads. | built in Layer 1 |
| `comms-qa` | Answer questions from the knowledge base (mini-RAG over the pluggable KB). | coming in v2 |
| `comms-draft` | Draft a new page guided by the knowledge base / playbook. | coming in v2 |

The sub-skills live under `skills/<name>/SKILL.md`. Shared assets (the AI-tell
pattern catalog, and later the voice profile and learned-rules log) live under
`_shared/`.

## How routing works

The right dispatch path depends on the host. Two cases:

### Claude / Codex / Cursor — host-native dispatch

These hosts already discover and trigger skills by their `name` + `description`.
Do **not** intercept or re-route here. Let the host pick the sub-skill from the
request. This router exists mainly as documentation and as the package entry
point; it is not a runtime interceptor on these surfaces. (Reinventing host
dispatch is a Layer 1 concern, deliberately out of scope.)

### RovoDev — explicit intent routing

RovoDev does not auto-trigger skills. When invoked there, read the user's intent
and route explicitly:

| If the user wants to… | Route to |
| --- | --- |
| clean up / de-AI / polish / review / score a draft | `comms-polish` |
| teach the tool their writing style, build a voice profile | `voice-onboard` (Layer 1; until then, fall back to `comms-polish` voice matching) |
| ask a question answered by the knowledge base | `comms-qa` (v2; until then, say it's not built yet) |
| draft a new page from the playbook | `comms-draft` (v2; until then, say it's not built yet) |

If intent is ambiguous, default to `comms-polish` (the most common job) and say
which sub-skill you chose.

## Boundary

This suite edits and produces prose, not code. For source-code cleanup or
refactoring, use a code-cleanup skill instead.

## Engine vs fuel

The suite is the *engine*; the knowledge base under `_shared/knowledge/` is the
*fuel*. The open-source build ships a generic KB; a company fork drops its own
playbook into the same slot. The playbook never enters this public repo. (KB seed
and retrieval are later layers — the slot is present but empty in this build.)
