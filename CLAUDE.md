# AI Writing Suite — Project Instructions

Public, MIT-licensed agent skill suite for writing assistance, packaged under `skills/`.

## Repo Layout

- `skills/ai-writing-suite/` — AI writing-assistant suite (currently ships the polish/humanize capability; growing into a full suite — see plan below).
- `docs/` — design docs, handovers, migration notes, session closeouts.

**Dedicated repo.** Extracted from the `personal-productivity-skills` umbrella on 2026-06-06
(`agent-goal-contracts` stays in the umbrella) and published to
**github.com/surahli123/ai-writing-suite** (public, default branch `main`). Never commit to
`main` directly — feature branch → PR; confirm before pushing.

## AI Writing Suite (active work)

The OSS version of a writing-assistant skillset for a company DS team, driven by a
proprietary **DS Comms Playbook** through a **pluggable knowledge base**.

- **Plan (read first):** `docs/design-ai-writing-suite-v1-2026-06-06.md` — decision log
  D1–D12, v1 scope, risks, eng+ceo review report.
- **Engine vs fuel:** OSS ships the engine + a generic KB (distilled from 4 MIT repos).
  The company forks and drops the real playbook into `_shared/knowledge/` via a Confluence
  page. The playbook never enters this public repo.
- **Target surfaces:** Claude + Codex + Cursor (v1); RovoDev (v2). All hosts read the single
  source tree directly — Claude/Codex via repo-root marketplace manifests, Cursor by copying
  `skills/ai-writing-suite/`. There is no generated package body (the old generate/sync model
  was removed); see `docs/packaging.md`.
- **Keep separate** from the personal `writing-vault` pipeline. That project's "AI scaffolds,
  never ghostwrites" rule does NOT apply here — this suite may draft and rewrite.

## Conventions

- **Attribution:** absorbed material from other repos is MIT; preserve each source's
  copyright + license and credit it in the skill's `NOTICE.md`.
- **Skill structure:** each skill = `SKILL.md` (frontmatter `name` + `description`) +
  `README.md` + `NOTICE.md` + `LICENSE`, optional `references/`, `assets/`, `evals/`.
- **RAG/KB:** pure markdown + `INDEX.md`, zero external deps, portable across all target
  surfaces. Do not depend on host-specific MCP tools (e.g. OMC wiki) for core retrieval.
- **Evals:** a self-improving skill needs a holdout. Keep `evals/` fixtures; calibrate the
  baseline to fail ~30-40% of cases so regressions are catchable.

## Working Style

- **Plan first.** Outline → approve → build in visible stages. The owner is the product owner.
- **Git:** never commit to `main`; feature branch → PR. Show staged files before committing.
- **Verify:** for skills, "done" = loads without error on target surfaces + an eval/demo
  with before/after evidence, not "no errors thrown".
