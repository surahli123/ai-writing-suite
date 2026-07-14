# Handover — AI Writing Suite: real publish + Phase 1 CI (2026-06-07)

Project: **AI Writing Suite** — `~/Documents/ai-writing-suite/`
GitHub: **github.com/surahli123/ai-writing-suite** (public, default branch `main`)
Branch: `main` @ `1278567` (clean; suite repo is `main`-only, local + remote)

## Last session summary

Started from a **false-ready** state: the recon found that despite "v1 shipped + packaging
verified," the published repo was **not installable** — the plugin body was gitignored (only
manifests reached the remote) and the Claude marketplace manifest wasn't resolvable. Fixed it by
switching to a **source-pointing architecture**, published + tagged `v1.0.0`, ran two independent
Codex reviews, cleaned up the umbrella repo, and built Phase 1 of the test plan (regression CI).

## Current state (all verified)

- **Installable on 3 hosts** from one source tree. Claude + Codex install via repo-root marketplace
  manifests; Cursor copies the tree. **Real-remote fresh-clone smoke passed on Claude + Codex**
  (4 skills discovered); literal README commands work from `main`.
- **Tags live:** `ai-writing-suite--v1.0.0` (Claude release) + `v1.0.0` (Codex `--ref` / semantic).
- **CI green:** `.github/workflows/ci.yml` runs `evals/run_all.sh` (23 unit + 3 KB smoke + 8 fixtures
  @ 38% calibration) on push to `main` + every PR. Verified green on GitHub + fail-injection bites.
- **Architecture:** root `.claude-plugin/marketplace.json` + `.agents/plugins/marketplace.json`, both
  → `./skills/ai-writing-suite`; in-source `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json`.
  The old generate-and-sync packaging (`packaging/` + `sync.sh`) was **removed**.
- **Umbrella cleanup:** PR **#5 OPEN** in `personal-productivity-skills` (removes the duplicated
  `ai-writing-humanizer` skill — that's its real name on `main`; the rename to `ai-writing-suite` only
  ever lived on the closed-unmerged PR #4 branch). **Awaiting your merge.**

## Next steps (priority order)

1. **Phase 2 — quality eval** (the real gap). Wire a model into the `evals/fixtures/rubric.md` judge
   path (currently emits SKIPPED), assemble ~15–25 real before/after items, and **calibrate the judge
   against your human labels first** (broken-ruler guard); cross-model judge to dodge self-preference.
   Full plan: `docs/test-plan-v1-2026-06-07.md`.
2. **Merge umbrella PR #5** (your call; backup repo).
3. **Small cleanups (optional):** fix `detector.py:19` `SyntaxWarning: invalid escape sequence '\S'`
   (raw string); add a CHANGELOG `[Unreleased]` line for the CI/runner; delete the umbrella's obsolete
   `rename-ai-writing-suite` branch (local + remote) after PR #5 merges.

## Key context / gotchas

- **Verify a publish with a FRESH-CLONE install on each host — never trust local `validate`.** Local
  `claude plugin validate` / `tag --dry-run` read the working tree, so a gitignored body passes
  locally but ships empty. The only real gate = clone the pushed remote + install. (This was the
  root cause of the false-ready state.)
- **Don't reintroduce generate-and-sync.** Both hosts read source directly; there is no generated
  body to commit. Adding `packaging/`/`sync.sh` back reopens the gitignored-body trap.
- **Codex review with a custom prompt:** use `codex exec --sandbox read-only <<'PROMPT' … PROMPT`
  (prompt via **stdin**). `codex review --base/--commit "prompt"` errors (can't combine), and
  `codex exec "prompt"` (argv) hangs on stdin.
- **Repo hooks:** block direct commits to `main` + committing `handover-*`/session artifacts.
  Workflow = feature branch → PR → `gh pr merge --rebase` (ff). Handovers/plans/reviews stay UNTRACKED.
- **Version authority:** the two `plugin.json` files are authoritative (`1.0.0`); `SKILL.md` has no
  version. Bump both together on release. See `docs/packaging.md`.

## Relevant files (read first)

- `docs/test-plan-v1-2026-06-07.md` — Phase 1 (done) + Phase 2 (next) test design.
- `docs/packaging.md` — the source-pointing publish model + how to verify/version.
- `docs/plan-publish-cleanup-test-2026-06-07.md` — the full session plan + evidence appendix.
- `reviews/2026-06-07-rereview-final.md` + `-adversarial-synthesis.md` — the two Codex reviews.
- `skills/ai-writing-suite/{.claude-plugin,.codex-plugin}/plugin.json`, root marketplace manifests.
- `skills/ai-writing-suite/evals/run_all.sh`, `.github/workflows/ci.yml`.

## Handover prompt (paste into a fresh session)

> Continue **AI Writing Suite** at `~/Documents/ai-writing-suite/` (public repo
> github.com/surahli123/ai-writing-suite, branch `main`). v1 is published + installable on Claude,
> Codex, Cursor (source-pointing architecture; tagged v1.0.0); Phase 1 regression CI is green. Read
> `docs/handover-2026-06-07-publish-and-ci.md` first, then `docs/test-plan-v1-2026-06-07.md`. I want
> to work on **Phase 2 — the comms-polish quality eval** (wire a model into `evals/fixtures/rubric.md`,
> assemble a real eval set, calibrate the judge against my human labels first). Repo hooks block
> direct `main` commits + `handover-*` files → branch + PR (rebase ff). Plan first, wait for my go.
