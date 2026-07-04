# Handover — voice-onboard Exemplars + Hard Rules (B+C): spec + plan done, ready to execute

- **Date:** 2026-07-03
- **Project:** AI Writing Suite — `~/Documents/ai-writing-suite` (public github.com/surahli123/ai-writing-suite)
- **Branch:** `feat/voice-onboard-exemplars-hardrules` (off `main`, commit `59b8180`, **NOT pushed**)

## What this session did (docs only — no product code)

Started from a Dana X post ("why your AI sucks at writing") and turned it into a scoped,
reviewed, planned feature for the `voice-onboard` sub-skill:

- **brainstorming** → distilled Dana's method vs the current skill → 5 candidates.
- **grill-me** (21 branches, all owner-approved) → scope locked to **B (Exemplars) + C (Hard Rules)**;
  F/A/E/D deferred or dropped.
- **SPEC** written in EN + zh mirror.
- **Adversarial review** via a Workflow-orchestrated OMC panel (1 architect + 3 critic, Opus,
  grounded in repo, each finding refuted): **25 agents, 21 findings, 0 survived.** Verdict SOUND.
  7 SUGGESTION-level residuals surfaced; **R1-R5 folded into the spec**.
- **TDD implementation plan** written (7 tasks) + self-reviewed.
- Committed 5 design docs (`59b8180`).

## Current state

- **SPEC is SOUND and owner-approved.** No BLOCKER/CONCERN.
- **No product code written yet.** Task 1 of the plan is the first change.
- The feature: append `## Exemplars` + `## Hard Rules` (append-only) to the voice-profile
  contract `_shared/voice-profile.md`, consumed by `comms-polish` + `comms-draft`.

## NEXT STEP (the point of the new session)

**Execute the 7-task plan using OMC subagents (subagent-driven), fresh session.**

- Plan: `docs/plan-voice-onboard-exemplars-hardrules-2026-07-03.md` — task-by-task, TDD, exact
  paths, real content, real test code. Do tasks **1 → 7 in order** (Task 1 = the contract, everything depends on it).
- Run tests from `skills/ai-writing-suite/`: `python3 -m pytest evals/ -q` (78 tests today; each task adds a tripwire).
- Recommended executor: `oh-my-claudecode:executor` (Sonnet for mechanical markdown/test edits;
  `model=opus` only if judgment needed). Review between tasks with `oh-my-claudecode:code-reviewer`.
- Owner routing (per ~/.claude/CLAUDE.md): executor + **caveman ultra** output mode; never haiku.

## Key constraints / gotchas (do NOT violate)

- **Frozen contract, append-only:** consumers read `voice-profile.md` by **named H2 header** —
  only append `## Exemplars` / `## Hard Rules`, never rename/drop existing headers.
- **Advisory, not gating:** Hard Rules flag; only genre hard-constraints (280 chars, code) + facts block.
- **Exemplars = reference, never copy** (anti-copy guardrail at every consumption point).
- **Fictional Sam only** in the shipped sample; **never invent voice** — thin data → `Unknown — not enough signal` / `None yet`.
- **Tests stdlib-only, CI-safe.** Quality numbers (voice-match, hard-rule precision/recall) stay
  **BLOCKED on 16-24 real enterprise drafts (P3)** — do not report/fabricate. Only the anti-copy
  overlap scorer (Task 6) runs now (synthetic inputs).
- **Version bump 1.1.0 → 1.2.0 only AFTER implement + owner acceptance** (not during).
- **F (tacit-knowledge interview) is a separate NEXT round** — owner flagged it, out of this scope.
- **Git:** never commit to `main`; stay on the feature branch; show staged files before commit.

## Corrections to stale project-memory notes (verified this session)

- **OMC subagents WORK on this personal Mac.** The old handover's "OMC subagents BROKEN on this
  machine" was **company-RovoDev-specific**. Here the OMC Workflow ran 25 agents (architect + critic,
  Opus) with 0 errors. **Use Workflow with a `schema`** to force StructuredOutput — dodges the known
  OMC terse-final-token ("Done.") problem.
- **Feature-branch commits are NOT blocked.** The old "hooks block main commits + handover/plan
  files → untracked" note did not apply on the feature branch — `59b8180` committed 5 docs cleanly.

## Relevant files (read first, in order)

1. `docs/plan-voice-onboard-exemplars-hardrules-2026-07-03.md` — **execute this**.
2. `docs/design-voice-onboard-exemplars-hardrules-2026-07-03.md` (+ `.zh.md`) — the spec (the "why").
3. `docs/review-adversarial-spec-voice-onboard-2026-07-03.md` — the adversarial review + residuals.
4. `docs/brainstorm-voice-onboard-dana-sharpen-2026-07-03.md` — the full decision trail (21 branches).
5. Files the plan touches: `skills/ai-writing-suite/_shared/{voice-profile,host-profile-template}.md`,
   `skills/ai-writing-suite/skills/{voice-onboard,comms-polish,comms-draft}/SKILL.md`,
   `skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md`, `evals/`.

---

## Handover prompt (paste into the new session)

> Continue AI Writing Suite. Repo `~/Documents/ai-writing-suite`, branch
> `feat/voice-onboard-exemplars-hardrules` (commit `59b8180`, not pushed). The B+C feature
> (add `## Exemplars` + `## Hard Rules` to the voice-profile contract, consumed by comms-polish +
> comms-draft) is fully specced, adversarially reviewed (0/21 survived), and has a TDD plan at
> `docs/plan-voice-onboard-exemplars-hardrules-2026-07-03.md`. **Execute that plan task-by-task
> (1→7) using OMC subagents (executor, sonnet; code-reviewer between tasks).** Run tests from
> `skills/ai-writing-suite/`: `python3 -m pytest evals/ -q`. Honor the constraints in
> `docs/handover-2026-07-03-voice-onboard-bc-spec-plan.md` (append-only contract, advisory rules,
> anti-copy, fictional Sam, quality numbers blocked on P3, never commit to main). OMC subagents
> work on this Mac.
