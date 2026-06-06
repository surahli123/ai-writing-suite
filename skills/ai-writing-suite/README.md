# AI Writing Suite

Polish prose that sounds AI-written without changing what the author meant.

The differentiator is not "rewrite this better." It is:

```text
preserve meaning, remove AI slop, keep author voice
```

Use it when a draft has the usual model tells: filler, vague claims, inflated importance, forced structure, and rhythm that sounds too even.

## What It Does

`ai-writing-suite` is a four-part writing-assistant skillset:

1. **comms-polish** (v1) — identify tells, preserve meaning, remove AI-shaped prose patterns, match author voice or register.
2. **voice-onboard** (v1) — interview, collect writing samples, distill your voice signature.
3. **comms-qa** (v2) — knowledge QA over a pluggable writing playbook.
4. **comms-draft** (v2) — guided drafting workflow using playbook best practices.

An agent using the suite can:

1. Identify the audience and purpose
2. Preserve facts, citations, numbers, commands, and claims
3. Remove AI-shaped prose patterns
4. Match the author's voice or the document's register
5. Return either a rewrite, a review, a detection score, or targeted file edits

## Engine vs Fuel

The OSS version ships the **engine** (comms-polish, voice-onboard, eval harness, self-improvement) with a generic **knowledge base** distilled from four open-source projects.

The company version reuses the same engine and swaps a proprietary **DS Comms Playbook** into the knowledge slot via a Confluence page. The playbook never enters this public repository.

```
OSS:     engine + generic KB
Company: engine + proprietary playbook (dropped in as data, not code)
```

No code changes needed to switch playbooks.

## When To Use It

Use the suite for:

- docs and README prose
- emails and status updates
- social posts and personal notes
- reports and summaries
- launch notes and user-facing copy

Do not use it for source-code cleanup. Use a code cleanup or refactoring skill for that.

## Sub-Skills

### comms-polish (Ships in v1)

Polish prose and detect AI tells.

**Modes:**
- `detect` — find AI tells and estimate density without rewriting.
- `rewrite` — produce polished prose from pasted text.
- `edit` — modify a prose file in place while preserving structure.
- `review` — give prioritized writing findings without rewriting everything.

**Features:**
- Consolidated AI-tell pattern catalog (seven deduplicated sources, each pattern source-tagged for attribution).
- Scenario presets (tweet, LinkedIn, README, memo).
- Final-pass checklist before publishing.
- Voice matching (reads `_shared/voice-profile.md` to calibrate tone and style if present).
- 0–100 AI-tell density score for before/after comparison.

**Example:**

Before:
```text
This robust workflow enables teams to seamlessly leverage contextual insights, ensuring a more effective and streamlined development experience.
```

After:
```text
This workflow gives teams the context they need before they start editing.
```

### voice-onboard (Ships in v1)

Interview and distill your writing voice.

**Features:**
- Guided conversation to collect writing samples (local files or pasted text).
- Extracts voice signature (tone, vocabulary, sentence shape, register preferences).
- Writes `_shared/voice-profile.md` for reuse across sessions.
- Structured host-profile template for consistent capture.

### comms-qa (v2)

Knowledge QA over a pluggable playbook.

**Features:**
- Wiki-style markdown KB (zero external dependencies, portable across Claude / Codex / Cursor / RovoDev).
- Pure markdown + `INDEX.md` navigation; no host-specific MCP tools.
- Pluggable slot: OSS ships generic KB; company forks and drops a Confluence-sourced playbook.
- End-to-end smoke test in v1 proves the company step is "drop in a page", not "build a RAG engine".

### comms-draft (v2)

Guided drafting workflow using playbook best practices.

**Features:**
- Playbook-driven interview flow.
- Real-time feedback on audience, structure, clarity.
- Cite-as-you-go pattern matching against the KB.

## Self-Improvement (Human-Gated)

After each session, the suite proposes new rules based on error analysis:

1. Analyze edits you made or approved.
2. Propose candidate rules (e.g., "remove 'seamlessly'" or "tighten 'important to note'").
3. You approve; we eval-test the rule against the baseline.
4. Approved rules append to `_shared/learned-rules.md` (append-only, never auto-editing core logic).

Rules improve over time without drift or degradation.

## Knowledge Base

The knowledge base lives in `_shared/knowledge/`:

- `INDEX.md` — wiki-style navigation index.
- Topic markdown files — audience, clarity, revision, structure, tone, and more.

**For OSS:** Generic best-practices entries distilled from four MIT-licensed source projects.

**For company:** Drop in a Confluence page link; the engine reads and retrieves from your playbook.

## Install

Clone or copy this repo, then symlink the skill into your target environment.

### Claude

```bash
# Copy to your Claude Code skills directory
cp -r skills/ai-writing-suite ~/.claude/skills/ai-writing-suite
```

Restart Claude Code so the skill list refreshes.

### Codex

```bash
# Copy to your Codex skills directory
cp -r skills/ai-writing-suite ~/.codex/skills/ai-writing-suite
```

Restart Codex so the skill list refreshes.

### Cursor / RovoDev (v2)

See `packaging/` for surface-specific installation instructions (coming in v2).

## How to Use

### Invoke comms-polish

```
I wrote this: "[pasted text]"
Rewrite it to sound less AI-generated, keeping the facts and my voice.
Mode: rewrite
Audience: technical docs / LinkedIn post / memo / etc.
```

Or:

```
Detect AI tells in this: "[pasted text]"
Give me a score and top three edits I could make.
Mode: detect
```

### Invoke voice-onboard

```
I want to teach you my writing voice. Here are some samples: [paste or link files]
```

The skill interviews you, extracts your voice signature, and saves it for all future sessions.

### Read the learned rules

```
What rules have we learned so far?
```

The suite shows `_shared/learned-rules.md`, which grows as new patterns emerge from your writing.

## Evaluation

The suite ships with:

- **Before/after fixtures** across genres (tweet, LinkedIn, README, memo).
- **LLM-judged scoring** — a rubric calibrated so the baseline fails 30–40% of cases.
- **Mechanical regression gate** — ported from avoid-ai JavaScript detector.
- **Self-improvement integration** — each proposed rule is eval-tested before you approve it.

See `evals/` for details.

## Attribution

This suite absorbs and extends patterns, templates, and methodologies from seven open-source projects, all MIT-licensed:

1. **weijt606/anti-vibe-writing** — bilingual patterns, scenario presets, host-profile template.
2. **conorbronsdon/avoid-ai-writing** — JS detector, CATEGORIES taxonomy, packaging patterns.
3. **donghuixin/AI-Vibe-Writing-Skills** — style-extractor prompts, memory patterns, self-improvement shape.
4. **Yuan1z0825/nature-skills** — academic polish rubric, structural patterns, plugin conventions.
5. **stop-slop** by Hardik Pandya — core directness rules, scoring methodology.
6. **blader/humanizer** by Brandon Wise — 43-pattern catalog, voice calibration.
7. **aboudjem/humanizer-skill** — 30-pattern catalog derived from Wikipedia "Signs of AI writing".

See `NOTICE.md` for full copyright and license details. Every absorbed pattern is source-tagged in `_shared/patterns/00-index.md` for traceability.

## Design Decisions

For a full account of why the suite is built this way, see:

- `docs/design-ai-writing-suite-v1-2026-06-06.md` — decision log (D1–D12), risks, success criteria.
- `CLAUDE.md` — project-specific conventions and working style.

Key decisions include:

- **D1 (Product):** Full suite, not a narrow humanizer; OSS face of a company DS skillset.
- **D2 (Reuse):** Absorb all MIT sources with preserved attribution.
- **D5 (RAG):** Pure markdown + convention, not host-specific MCP tools; portable across Claude / Codex / Cursor / RovoDev.
- **D6 (Safety):** Human-gated self-improvement; never auto-edit core logic.
- **D12 (v1 Scope):** Prove one end-to-end KB smoke path so company step is "drop in a page", not "build a RAG".

## License

MIT License. See `LICENSE` and `NOTICE.md` for details.
