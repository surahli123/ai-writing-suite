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
3. **Knowledge QA (mini-RAG)** — answer questions over the playbook + best practices.
4. **Guided drafting** — draft a page using the playbook.

Plus a **human-gated self-improvement** loop: each session can *propose* new rules; you
approve before anything is written. Core skill logic is never auto-edited.

## Status

**Built, verified, and installable on Claude, Codex, and Cursor.** All four sub-skills ship as
working implementations: polish/de-AI (`comms-polish`), voice learning (`voice-onboard`),
knowledge QA (`comms-qa`), and guided drafting (`comms-draft`) — plus a generic pluggable KB seed
with an end-to-end retrieval smoke path, an eval harness (Python AI-tell detector + fixtures), and
a human-gated self-improvement hook.

- **Plan (read first):** [`docs/design-ai-writing-suite-v1-2026-06-06.md`](docs/design-ai-writing-suite-v1-2026-06-06.md)
  — decision log D1–D12, v1 scope, risks, eng+ceo review report.

## Install

One source of truth (`skills/ai-writing-suite/`) published to three hosts.

### Claude Code

```bash
claude plugin marketplace add surahli123/ai-writing-suite
claude plugin install ai-writing-suite@ai-writing-suite
```

Claude auto-discovers the sub-skills (`comms-polish`, `voice-onboard`, …); invoke by asking it to
polish/review prose, or call a skill by name.

### Codex

```bash
codex plugin marketplace add surahli123/ai-writing-suite
codex plugin add ai-writing-suite@ai-writing-suite
```

Codex resolves the plugin from the same source tree — no `--sparse` needed; the Codex
marketplace manifest sits at the repo root (`.agents/plugins/marketplace.json`).

### Cursor

Cursor reads Anthropic-format **Agent Skills** from `.cursor/skills/` — there is no marketplace, so
copy the skill tree into a discovery location:

```bash
git clone https://github.com/surahli123/ai-writing-suite
cp -R ai-writing-suite/skills/ai-writing-suite ~/.cursor/skills/ai-writing-suite
```

(Or copy into your project's `.cursor/skills/` for project-scoped use.) Cursor discovers the skills
on the next session; invoke with `/comms-polish`, `/voice-onboard`, … or by intent.

## Quickstart (paste-and-go)

After install, paste a prompt like this to your agent:

```
Detect AI tells in this and give me a score plus the top three edits:
"In today's fast-paced world, it's important to note that our solution
seamlessly leverages cutting-edge technology to deliver robust results."
Mode: detect
```

Expected output **shape** (not exact wording):

```
AI-tell score: 0–100 (higher = more AI-shaped)
Top tells found:
  1. <tell> — <why it reads AI-generated> — <concrete fix>
  2. …
  3. …
Suggested rewrite: <one tightened, human-sounding version>
```

Swap `Mode: detect` for `Mode: rewrite` to get the rewrite directly, or ask
`comms-draft` to draft a fresh page, `comms-qa` to answer from the knowledge base,
or `voice-onboard` to learn your voice first. More examples:
[`skills/ai-writing-suite/README.md`](skills/ai-writing-suite/README.md#how-to-use).

## Repo Layout

```text
.claude-plugin/marketplace.json    # Claude marketplace  → points at the source tree
.agents/plugins/marketplace.json   # Codex marketplace   → points at the source tree
skills/
  ai-writing-suite/                # THE SUITE — single source of truth
                                   #   (Claude + Codex install this; Cursor copies it)
    SKILL.md                       # thin router
    .claude-plugin/plugin.json     # Claude plugin manifest
    .codex-plugin/plugin.json      # Codex plugin manifest
    skills/                        # sub-skills: comms-polish, voice-onboard, comms-qa, comms-draft
    _shared/                       # patterns (engine) + knowledge (swappable KB) + voice profile
    evals/                         # AI-tell detector + fixtures + smoke tests
    NOTICE.md  LICENSE  README.md  CHANGELOG.md
docs/                              # design docs, handovers, plans, packaging
```

## Attribution

Absorbed material from other repos is MIT-licensed; each source's copyright + license is
preserved and credited in [`skills/ai-writing-suite/NOTICE.md`](skills/ai-writing-suite/NOTICE.md).
