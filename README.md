# AI Writing Suite

An open-source, MIT-licensed agent skill suite for **writing assistance** — the public
version of a writing-assistant skillset for a company Data Science team. It polishes,
drafts, and reviews prose against a **pluggable knowledge base** (a "DS Comms Playbook"
in the company fork; a generic best-practices KB in this OSS build).

> **Engine vs fuel:** this repo is the *engine*. The knowledge base is *fuel* — swappable.
> The OSS build ships a generic KB; a company fork drops its real playbook into the same
> slot. The proprietary playbook never enters this public repo.

## What it does (target)

1. **Polish / review** — de-AI and tighten prose while preserving meaning and author voice.
2. **Voice learning** — interview + distill a writer's historical style into a reusable profile.
3. **Knowledge QA (mini-RAG)** — answer questions over the playbook + best practices *(v2)*.
4. **Guided drafting** — draft a page using the playbook *(v2)*.

Plus a **human-gated self-improvement** loop: each session can *propose* new rules; you
approve before anything is written. Core skill logic is never auto-edited.

## Status

**v1 in progress.** Today the suite ships the polish/humanize capability; the v1 build adds
a suite skeleton + router, an enriched `comms-polish`, `voice-onboard`, a generic KB seed
with an end-to-end retrieval smoke path, an eval harness, and the self-improvement hook.

- **Plan (read first):** [`docs/design-ai-writing-suite-v1-2026-06-06.md`](docs/design-ai-writing-suite-v1-2026-06-06.md)
  — decision log D1–D12, v1 scope, risks, eng+ceo review report.

## Repo Layout

```text
skills/
  ai-writing-suite/        # the suite (router + sub-skills as the build progresses)
    SKILL.md
    README.md
    NOTICE.md
    LICENSE
docs/                      # design docs, handovers, migration notes
```

## Attribution

Absorbed material from other repos is MIT-licensed; each source's copyright + license is
preserved and credited in [`skills/ai-writing-suite/NOTICE.md`](skills/ai-writing-suite/NOTICE.md).
