# Codex E2E Product Review (B1) — manifests, install transcript, RovoDev claims, NOTICE/CI/cruft

Model: gpt-5.6-sol xhigh, read-only sandbox. Date: 2026-07-13. VERDICT: PACKAGING FIX-FIRST
Scope note: evals/ explicitly off-limits (reviewed three times prior); this pass covers the PRODUCT surface.

---

## Manifest consistency & install

- **BLOCKER — [skills/ai-writing-suite/skills/comms-draft/SKILL.md:3](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:3)**  
  Claude reports invalid YAML frontmatter; at runtime `comms-draft` loads with empty metadata and is not reliably discoverable. The unquoted `[NEEDS: ...]` segment is the likely parser trigger. This breaks the auto-discovery promise at [README.md:43](/Users/surahli/Documents/ai-writing-suite/README.md:43).  
  **Fix:** quote or fold the entire `description`, then require both `claude plugin validate .` and `claude plugin validate skills/ai-writing-suite` to pass.

- **BLOCKER — [skills/ai-writing-suite/.claude-plugin/plugin.json:4](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/.claude-plugin/plugin.json:4), [skills/ai-writing-suite/.codex-plugin/plugin.json:3](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/.codex-plugin/plugin.json:3), [CHANGELOG.md:14](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/CHANGELOG.md:14)**  
  The working branch says `1.1.0`, but live public `main` is still `f0c77d0`, advertises/installs `1.0.0`, and has no `v1.1.0` tag. The current-branch-only 1.1 additions are: Gold-FAIL fixtures, false-positive fence, quoted-evidence/self-preference protocol, and the two router-description seam changes.  
  **Fix:** merge the intended release slice, verify live remote installation, then tag 1.1.0. Do not date/present the release as public before that gate.

- **CONCERN — [.claude-plugin/marketplace.json:4](/Users/surahli/Documents/ai-writing-suite/.claude-plugin/marketplace.json:4), [.claude-plugin/marketplace.json:12](/Users/surahli/Documents/ai-writing-suite/.claude-plugin/marketplace.json:12), [.codex-plugin/plugin.json:14](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/.codex-plugin/plugin.json:14)**  
  Marketplace descriptions still say QA/drafting arrive “in v2,” while the 1.1 changelog says both ship now.  
  **Fix:** make all manifest descriptions version-neutral or explicitly 1.1-current.

- **CONCERN — [README.md:62](/Users/surahli/Documents/ai-writing-suite/README.md:62)**  
  The Cursor source path matches the real layout, but a fresh machine can lack `~/.cursor/skills`, causing `cp` to fail; rerunning after installation can also create nested directories.  
  **Fix:** document `mkdir -p ~/.cursor/skills` and distinct fresh-install/update commands.

Names, repository URLs, two body versions, and both marketplace source paths otherwise agree and resolve correctly.

## RovoDev

- **CONCERN — [docs/packaging.md:94](/Users/surahli/Documents/ai-writing-suite/docs/packaging.md:94)**  
  The fallback tells an installed user to read `skills/ai-writing-suite/skills/...`, a repository-relative path that may not exist from their session directory. This partially reintroduces the exact cwd-resolution problem the suite-root protocol fixed.  
  **Fix:** tell RovoDev to locate the installed directory containing router `SKILL.md` plus `_shared/`, then open `skills/comms-polish/SKILL.md` relative to that root.

- **CONCERN — [docs/packaging.md:56](/Users/surahli/Documents/ai-writing-suite/docs/packaging.md:56), [CHANGELOG.md:122](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/CHANGELOG.md:122), [improvement-plan-deslop-landscape-2026-07-11.md:131](/Users/surahli/Documents/ai-writing-suite/docs/improvement-plan-deslop-landscape-2026-07-11.md:131)**  
  “Smoke-tested RovoDev support” rests on a 2026-06-08 registration test plus one `comms-polish` rewrite. The repo itself records that this predates current `comms-qa`, `comms-draft`, overstepping, and payoff behavior.  
  **Fix:** either rerun all four current sub-skills on RovoDev or narrow the claim to registration plus `comms-polish`.

- **CONCERN — [docs/design-ai-writing-suite-v1-2026-06-06.md:88](/Users/surahli/Documents/ai-writing-suite/docs/design-ai-writing-suite-v1-2026-06-06.md:88), [docs/design-ai-writing-suite-v1-2026-06-06.md:132](/Users/surahli/Documents/ai-writing-suite/docs/design-ai-writing-suite-v1-2026-06-06.md:132)**  
  A shipped, unmarked-as-superseded design document still prescribes removed `packaging/`/`sync.sh` machinery and says Cursor/RovoDev are deferred.  
  **Fix:** add a prominent historical/superseded banner linking to `docs/packaging.md`.

Tracked `skills/`, `_shared/`, and `docs/` contain no live `../../_shared` references. The stale occurrences found are historical prose in untracked documents.

## Trust, changelog, CI, cruft

- **BLOCKER — [NOTICE.md:46](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/NOTICE.md:46)**  
  `nature-skills` is recorded as MIT with no source revision. It was MIT before upstream commit `54eadc65` on 2026-06-18, but current upstream `main` is Apache-2.0. The old MIT grant remains usable, but the package cannot prove which MIT revision was absorbed.  
  **Fix:** record the exact absorbed commit and its MIT license snapshot. If any post-relicense material was incorporated, add Apache-2.0 compliance instead.

- **BLOCKER — [.github/workflows/ci.yml:17](/Users/surahli/Documents/ai-writing-suite/.github/workflows/ci.yml:17), [docs/packaging.md:41](/Users/surahli/Documents/ai-writing-suite/docs/packaging.md:41)**  
  CI runs only `evals/run_all.sh`; it omits the two packaging validations required by the maintainer documentation. Consequently all 259 tests pass while the Claude plugin body is invalid.  
  **Fix:** add manifest JSON/schema checks and both Claude validation commands to CI.

- **CONCERN — [NOTICE.md:115](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/NOTICE.md:115), [NOTICE.md:123](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/NOTICE.md:123), [LICENSE:3](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/LICENSE:3)**  
  NOTICE says LICENSE is at repository root, but it exists only under the plugin body; its copyright still says “AI Writing Humanizer contributors.”  
  **Fix:** add a root LICENSE/NOTICE or correct the wording, and rename the project copyright holder consistently.

- **CONCERN — [CHANGELOG.md:14](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/CHANGELOG.md:14), [evals/run_all.sh:12](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/run_all.sh:12)**  
  The 1.1.0 section omits the new `comms-draft` behavioral and `voice-onboard` extraction lanes now shipped as CI steps 5–6. Listed 1.1 features otherwise exist on this tree.  
  **Fix:** include those lanes in 1.1.0 or leave them under `Unreleased`.

- **CONCERN — [.gitignore:1](/Users/surahli/Documents/ai-writing-suite/.gitignore:1), [.claude/worktrees/agent-a5897476240b6a895/.git:1](/Users/surahli/Documents/ai-writing-suite/.claude/worktrees/agent-a5897476240b6a895/.git:1)**  
  The working tree contains five unignored nested Claude worktrees plus roughly thirty untracked historical docs/reviews. This is a serious accidental-`git add .` trap, although it is not yet public-repo cruft.  
  **Fix:** ignore runtime worktrees and explicitly curate the untracked documents before staging.

The other three named upstream notices—`anti-vibe-writing`, `avoid-ai-writing`, and `AI-Vibe-Writing-Skills`—match their upstream MIT copyright lines.

## Install transcript

Fresh isolated Claude Code 2.1.208, following only [README.md:36](/Users/surahli/Documents/ai-writing-suite/README.md:36):

1. `claude plugin marketplace add surahli123/ai-writing-suite`  
   **Exit 0:** public repository cloned; marketplace added.

2. `claude plugin install ai-writing-suite@ai-writing-suite`  
   **Exit 0:** installation reports success.

**First surprise:** `claude plugin list` shows version `1.0.0`, not the working tree’s `1.1.0`.

**First functional failure:** validation of that installed public body fails on `comms-draft` frontmatter; Claude warns its metadata is silently dropped. The README commands therefore appear successful while leaving one advertised sub-skill undiscoverable.

## Hard questions

1. Is `1.1.0` a release now, or a release candidate? The changelog says released, but public `main` and tags say otherwise.
2. What exact `nature-skills` commit was absorbed? Can that MIT-era provenance be recorded before shipping?
3. Does “RovoDev supported” mean all four current behaviors, or only router registration plus `comms-polish`?
4. Are the draft/voice behavioral evals part of 1.1.0? If so, why are they absent from its changelog?

PACKAGING: FIX-FIRST