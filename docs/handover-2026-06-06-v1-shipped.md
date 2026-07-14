# Handover — AI Writing Suite v1 (built, reviewed, published)

Date: 2026-06-06
Project: **AI Writing Suite** — `~/Documents/ai-writing-suite/`
GitHub: **https://github.com/surahli123/ai-writing-suite** (PUBLIC, default branch `main`)
Branch: `main` (fully pushed; `feat/ai-writing-suite-v1` + `chore/standalone-repo-extraction` merged in, kept locally)

## Last session summary

Took the project from "plan only, living inside a Codex-session umbrella repo" all the way to
a **published standalone public repo**. Migrated it out of the umbrella (local clone-then-prune,
history preserved), built the full v1 suite with OMC subagents in 4 dependency layers, ran an
independent Opus code review (fixed all findings), verified both Claude + Codex packaging against
the live CLIs, then created the public GitHub repo and pushed. Umbrella PR #4 closed as obsolete.

## Current state (all working / verified)

- **v1 suite** under `skills/ai-writing-suite/`: thin router + `comms-polish` (enriched) +
  `voice-onboard` + `comms-qa`/`comms-draft` (v2 stubs) + `_shared/{patterns,knowledge,...}` +
  human-gated self-improvement + Python detector/eval harness + Claude & Codex packaging.
- **Verification (executed):** 23/23 unit tests, KB smoke 3/3, eval calibration 38% (in the
  30-40% band), live polish demo 62/100→0/100, detector crash-proof on adversarial inputs.
- **Code review:** Opus, worktree-isolated — no BLOCKERs; 2 MAJOR + 4 MINOR all fixed
  (`docs/code-review-v1-2026-06-06.md`).
- **Packaging:** Claude validated via `claude plugin tag --dry-run`; Codex restructured to the
  conformant marketplace layout (`.agents/plugins/marketplace.json` + `plugins/ai-writing-suite/`)
  and live-verified via `codex plugin marketplace add` (then removed — config restored).
- Repo manifest URLs use the correct handle `surahli123` (NOT `surahli`).

## Next steps (priority order — all optional, nothing is blocking)

1. **(optional) Publish to a marketplace** — manifests validate; would need a marketplace listing
   (Claude: `claude plugin tag` to release-tag; Codex: host the marketplace dir).
2. **(optional) Umbrella cleanup** — `personal-productivity-skills` still has the now-duplicated
   ai-writing-suite skill copy; remove it there so it isn't maintained in two places (separate PR).
3. **(optional) Tidy local branches** — `git branch -d feat/ai-writing-suite-v1 chore/standalone-repo-extraction`.
4. **v2 roadmap** — `comms-qa` full RAG, `comms-draft`, host-side detector, Cursor + RovoDev
   packaging, Confluence ingestion, CJK detector scoring.

## Key context / gotchas (read before working)

- **Git hooks**: this repo BLOCKS direct commits to `main` and BLOCKS committing `docs/handover-*`
  / personal session artifacts. Workflow: do work on a `feat/`/`chore/` branch, then
  `git checkout main && git merge --ff-only <branch>` (fast-forward bypasses the commit hook).
  Handovers/closeouts stay UNTRACKED on disk by design.
- **Packaging is generated**: `packaging/{claude,codex}/` content is gitignored; only the
  hand-maintained manifests are tracked. Regenerate with `bash skills/ai-writing-suite/packaging/sync.sh`.
  Never hand-edit generated package content — edit the source under `skills/ai-writing-suite/`.
- **Engine vs fuel**: `_shared/patterns/` (de-AI tells) is the ENGINE and must survive a KB swap;
  `_shared/knowledge/` (best-practices) is the swappable FUEL the company replaces with its playbook.
- **OMC subagents swallow their findings** — if a dispatched code-reviewer/guide returns a terse
  "Done", the report is in its transcript `.output` JSONL, not the result (see mistakes_and_learnings).
- **Verify plugin/CLI specifics live** — `claude plugin validate` does NOT exist; use
  `claude plugin tag --dry-run`. Codex is marketplace-based (`codex plugin marketplace add/remove`).

## Relevant files (read first)

- `docs/design-ai-writing-suite-v1-2026-06-06.md` — the approved design (decisions D1–D12).
- `docs/code-review-v1-2026-06-06.md` — the Opus review + fixes.
- `skills/ai-writing-suite/SKILL.md` — the router (entry point).
- `skills/ai-writing-suite/packaging/README.md` — verified Claude + Codex packaging specs.
- `skills/ai-writing-suite/evals/README.md` — how to run the detector + fixtures + smoke test.
- Memory: `~/.claude/projects/-Users-surahli/memory/project_ai_writing_suite.md`.

## Handover prompt (paste into a fresh session to continue)

> Continue the **AI Writing Suite** project at `~/Documents/ai-writing-suite/` (public repo
> github.com/surahli123/ai-writing-suite, branch `main`). v1 is built, Opus-reviewed, and
> published; Claude + Codex packaging are live-verified. Read `docs/handover-2026-06-06-v1-shipped.md`
> first. Repo hooks block direct commits to `main` and handover-* files — work on a branch then
> ff-merge. I want to work on: <PICK — marketplace publish / umbrella cleanup / v2 (comms-qa RAG,
> comms-draft, Cursor+RovoDev packaging) / something else>. Plan first, then wait for my go.
