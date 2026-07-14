---
name: ai-writing-suite
description: A suite of writing-assistant skills for professional and product communication — polish/de-AI prose, learn an author's voice, answer questions from a knowledge base, and draft from it. Classifies a request and loads the right sub-skill. Use for docs, emails, posts, reports, and user-facing copy; not for source-code cleanup.
---

# AI Writing Suite (router)

This is the router for the suite. When this skill is selected, it classifies the
request and loads the sub-skill that does the work — it does not polish or draft
itself. Think of it as the dispatch layer in front of four specialized writers.

## Sub-skills

| Sub-skill | What it does | Status |
| --- | --- | --- |
| `comms-polish` | Polish, review, detect, or edit existing prose to remove AI tells while preserving meaning and voice. 0-100 AI-tell score on demand. | **available** |
| `voice-onboard` | Interview the author and distill their historical writing into a reusable voice profile that `comms-polish` and `comms-draft` read. | **available** |
| `comms-qa` | Answer a question from the pluggable KB/playbook, citing the entry the answer came from; says so when the KB does not cover it. Never invents playbook guidance. | **available** |
| `comms-draft` | Draft a new page from a brief — or revise a document that mixes existing text with a requested addition — guided by the KB/playbook; bakes anti-AI discipline (concreteness, varied rhythm, self-scan) into the draft and never fabricates, marking gaps with `[NEEDS: …]`. | **available** |

The sub-skills live under `skills/<name>/SKILL.md`. Shared assets (the AI-tell
pattern catalog, the voice profile, and the learned-rules log) live under
`_shared/`.

## How to route (executable)

When **this router skill is the one selected or invoked**, classify the request
and load the matching child skill, then follow that child's own instructions.
Skip this classification only when a child skill was already selected directly —
in that case just run that child.

Classify by what the request asks you to **do**:

| If the user wants to… | Route to |
| --- | --- |
| clean up / de-AI / polish / review / score / edit existing text, with no new content added | `comms-polish` |
| add new content — a new page from a brief, a new section, or a mix of polishing existing text **and** adding to it | `comms-draft` |
| ask a question the knowledge base answers | `comms-qa` |
| teach the tool their writing style / build a voice profile | `voice-onboard` |

**Precedence rule for mixed requests.** Any request that asks for a substantive
**addition** — even when it also asks to polish existing text ("polish this and
add a risks section") — routes to `comms-draft`. Drafting owns everything that
adds substance; `comms-polish` never adds content. Route to `comms-polish` only
when the request is pure rewording with no new material. This one rule breaks
every polish-vs-draft tie — there is no "ambiguous defaults to polish" fallback
for mixed cases.

If a request genuinely matches none of the four (e.g. "translate this, no other
change"), say so plainly and pick the closest fit rather than stalling.

## Then load and run the child skill

Once you have chosen a child skill, load it and let **it** decide what else to
read:

1. Open `skills/<name>/SKILL.md` (e.g. `skills/comms-polish/SKILL.md`), relative
   to this suite's root.
2. Follow that child skill's own instructions. The child decides which referenced
   assets it needs — its pattern-catalog categories, the voice profile, the KB
   entries — and loads them selectively. Do **not** pre-load every referenced
   file from here; that defeats the child's selective loading and bloats context.
   The actual logic lives in the child, not in this router's summary.

### Host note

On Claude / Codex / Cursor the host may discover and trigger a child skill
directly from its `name` + `description`; when that happens this router is
bypassed and the child runs on its own. The classify-and-load step above is what
runs when the router itself is the selected skill — including on RovoDev, which
does not auto-trigger nested skills. Either path ends in the same place: the right
child skill loaded and followed.

## Boundary

This suite edits and produces prose, not code. For source-code cleanup or
refactoring, use a code-cleanup skill instead.

## Engine vs fuel

The suite is the *engine*; the knowledge base under `_shared/knowledge/` is the
*fuel*. The open-source build ships a generic KB; a company fork drops its own
playbook into the same slot. The playbook never enters this public repo. (This
build ships a generic 5-entry KB seed + `INDEX.md` + a working retrieval smoke
path, and the `comms-qa` sub-skill that answers questions over it.)
