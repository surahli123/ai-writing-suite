# Plan — Steps 1–3 + v1 Test Discussion (2026-06-07)

Status: **PLAN ONLY — awaiting owner go before any mutation.** Read-only recon done via a
4-agent workflow (`wf_3df55f48-6dc`). Every claim below is backed by the agents' cited evidence
(commands + `gh api` + `git check-ignore`), summarized in the Evidence appendix.

---

## ⚠️ Headline finding (this changes Step 1)

**v1 is NOT actually installable from the published repo — on either Claude or Codex.**
The handover/memory say "v1 shipped + packaging live-verified," but that verification only ever
ran against the **local working tree**. On GitHub, the published artifact is broken:

1. **The plugin body was never pushed.** `.gitignore` keeps only the manifest files; all generated
   content (SKILL.md, skills/, _shared/, NOTICE/LICENSE) under `packaging/{claude,codex}/` is
   ignored. `gh api` confirms the remote `packaging/claude/` contains **only** `.claude-plugin/`
   and `packaging/codex/plugins/ai-writing-suite/` contains **only** `.codex-plugin/`. A user who
   installs gets an **empty plugin**.
2. **The marketplace manifest is in the wrong place for one-liner install.** `claude plugin
   marketplace add <src>` looks for `<src>/.claude-plugin/marketplace.json`. The repo has **no
   root** `.claude-plugin/` (`gh api` → 404); the only one is buried 4 levels deep. So
   `claude plugin marketplace add surahli123/ai-writing-suite` 404s. Codex's is similarly nested
   (needs a long, fragile `--sparse skills/ai-writing-suite/packaging/codex`).

**Why the earlier "verified" was a false positive:** `claude plugin validate <pkg-dir>` and
`claude plugin tag --dry-run` both **pass locally** because the generated body exists on disk.
They read the working tree, not the remote. *Local green ≠ remote-installable.* This is the exact
failure mode the project's own "done = loads on target surfaces" rule was meant to catch — but the
load-on-host check was never run end-to-end from a clean checkout.

**Consequence:** "Step 1: publish to a marketplace" is really **two** things — (1a) *make the repo
actually installable* (the real work), then (1b) *optionally tag/list it*. There's a genuine design
tradeoff inside 1a (below) that is the product owner's call.

---

## Step 1 — Make installable, then publish

### The crux decision: where does the published plugin BODY live?

The repo deliberately gitignores generated package content (design decision **R4: avoid sync drift**
across 4 target surfaces). But to be installable, the body must be **git-tracked on the remote**.
Two ways to resolve the conflict:

| | **Option A — publish the source tree** | **Option B — commit the generated package** |
|---|---|---|
| What | Add a **repo-root** `.claude-plugin/marketplace.json` whose `source` points at the already-tracked `skills/ai-writing-suite/`. No gitignore change. | Un-ignore `packaging/{claude,codex}/` output, run `sync.sh`, commit the generated tree. |
| Install UX | `claude plugin marketplace add surahli123/ai-writing-suite` (one-liner) | Same one-liner if manifest moved to root |
| Pro | Fastest; nothing to keep in sync; one source of truth | Clean plugin-only artifact (no dev scaffolding shipped) |
| Con | Ships `evals/` + `packaging/` to consumers (minor bloat) | Reintroduces the **sync-drift risk R4 was created to prevent** → needs a CI guardrail (`sync.sh` + "fail if committed tree stale") |
| **Recommendation** | **✅ for v1** — simplest, no drift surface, matches "boring code wins" | defer to v2 when a CI release step exists |

**Claude vs Codex asymmetry (important):** Option A is clean for **Claude** (a plugin can point
straight at the source tree). **Codex** needs its specific `.agents/plugins/marketplace.json` +
`plugins/<name>/.codex-plugin/plugin.json` layout with the body beside it, so Codex effectively
needs **committed body content** regardless. Net: even under Option A, Codex likely needs a small
committed/tracked body (or we ship Codex slightly later). This is why "host scope" is a second
decision.

### Work items (after the decision)
- Add repo-root marketplace manifest (Claude; mirror for Codex per its layout).
- Make the body tracked per the chosen option; `claude plugin validate <root> --strict`.
- **End-to-end install smoke from a fresh clone** on each host (this is the real "done" check —
  see "Verification gates"). NOT optional.
- Add a **Quickstart** to the top-level `README.md` (today it has **zero** install instructions):
  exact `marketplace add` + `install` commands per host.
- Branch → PR → (adversarial review, since this is outward-facing/production) → merge → push.
- **(1b, optional, outward-facing)** `claude plugin tag` → `ai-writing-suite--v1.0.0` (+ `--push`);
  Codex release tag for `--ref` pinning. **Do this only AFTER the install path is fixed + smoke-passed**
  — tagging a release that doesn't install would mislead early adopters.
- **(optional)** community listing (awesome-list / third-party registry). No first-party central
  registry exists in `claude` 2.1.168 (`marketplace add` only takes URL/path/owner+repo; no
  `claude plugin publish`). Outward-facing, removal not in your control.

**Outward-facing / irreversible steps (need explicit go each):** push to `main`, push a public git
tag, submit a community listing.

---

## Step 2 — Umbrella cleanup (separate PR) — CLEAN, ready to execute

Repo: `~/Documents/Codex/2026-06-01/personal-productivity-skills`
(github.com/surahli123/personal-productivity-skills, default branch `main`).
PR #4 (the rename) **confirmed CLOSED-unmerged** (`closedAt 2026-06-07`, `mergedAt null`).

- **Base off `main`, NOT the current `rename-ai-writing-suite` branch** (that branch is 2 commits
  ahead carrying the *obsolete rename* — basing off it would pollute the PR).
- **Remove:** `skills/ai-writing-suite/` (4 tracked files) + `docs/design-ai-writing-suite-v1-2026-06-06.md`
  (duplicate-only design doc).
- **Scrub references:** `README.md` lines 8, 58 (layout block), 92, 93 + reword line 5
  ("two skills" → single); `CLAUDE.md` line 8 + the whole `## AI Writing Suite (active work)` section.
- **Preserve:** `skills/agent-goal-contracts/` (the surviving skill) untouched.
- **Careful staging:** use explicit `git add README.md CLAUDE.md` — **never** `git add -A` (5 untracked
  docs + `.omc/` are present and must not be swept in).
- Commit (single concern) → push branch → `gh pr create --base main`.
- Branch name proposed: `remove-ai-writing-suite-skill` (owner confirm).

Full ordered command list is in the recon output (`umbrella.removalPlan`).

---

## Step 3 — Branch tidy (suite repo) — TRIVIAL, ready

Pre-action check already proved both are **fully merged into `main`** (`git branch --merged main`
listed both), and neither was ever pushed → safe local delete:
```
git -C ~/Documents/ai-writing-suite branch -d feat/ai-writing-suite-v1 chore/standalone-repo-extraction
```
(`-d`, not `-D`: refuses if not merged — a built-in safety net.)
Optional follow-up: delete the umbrella's obsolete `rename-ai-writing-suite` (local+remote) after
Step 2 merges.

---

## Verification gates (what "done" means)

- **Step 1 done** = a fresh clone installs and the skill **loads + triggers** on Claude AND Codex
  (canned prompt → `comms-polish` fires). This is identical to **test-option (a)** below, so Step 1
  and the "how to test v1" discussion partially merge: the install/load smoke is not a separate
  later task — it's the acceptance test for Step 1.
- **Step 2 done** = PR merged, `git grep ai-writing-suite` clean in umbrella tracked files,
  agent-goal-contracts intact.
- **Step 3 done** = branches gone, `git branch` clean.

---

## Then: how to test v1 (menu for discussion — not picking)

The cited verification (23 unit tests, smoke 3/3, calibration 38%) is **all mechanical** — it tests
the Python AI-tell *detector* and fixture calibration. It does **not** test (i) whether the suite
loads on a host, or (ii) whether `comms-polish` actually polishes well (the LLM-judge half of the
eval **never runs** — no model is wired into `rubric.md`/`--judge`; the "62→0 demo" was a one-off,
not a checked-in asset).

| Option | Tests | Effort | Value for v1 |
|---|---|---|---|
| **(a) Install/load smoke on Claude+Codex** | Does it actually run where users run it? | Low-med | **High** — literal "done"; merges with Step 1 |
| **(b) comms-polish de-AI quality eval** | Does polish lower tells + preserve meaning/voice? Wire a model into the existing `rubric.md` judge path. | Med | **Very high** — the core promise; today only a one-off demo |
| **(c) Regression harness + CI** | Keep detector/fixtures/smoke stable over edits; add `run_all.sh` + GH Actions | Low | Med-high — cheap insurance; makes self-improvement "eval-gated" real |
| **(d) Detector accuracy on labeled set** | True precision/recall/FP rate | Med-high | Med — detector is a secondary signal |
| **(e) Dogfood on owner's real writing** | End-to-end usefulness; exercises voice-onboard (0 tests today) | Low to start | High for confidence, low as regression guard |

**Suggested priority:** (a) [folds into Step 1] → (b) → (c). (d)/(e) opportunistic.

---

## Open decisions for the owner
1. **Publish body approach:** Option A (source tree) vs Option B (commit generated). *Rec: A for v1.*
2. **Host scope:** fix + publish Claude **and** Codex now, or **Claude first** then Codex (given the
   Codex layout asymmetry adds work)?
3. **Tag v1.0.0 now or after smoke-pass?** *Rec: after.*
4. **Umbrella:** confirm branch name `remove-ai-writing-suite-skill`; confirm removing the design doc
   too (rec: yes); leave the 5 untracked docs + `.omc/` as-is (rec: yes).
5. **Adversarial review** before the outward-facing publish PR (CLAUDE.md default for production)?

## Risks (top)
- **False-ready repeat:** trust ONLY a fresh-clone install smoke as publish-readiness, never local
  `validate`/`tag --dry-run`.
- **Outward-facing & irreversible:** pushing to public `main`, public tags, community listings.
- **Umbrella wrong-base / `git add -A`** sweeping untracked artifacts — mitigated by explicit base +
  explicit add.
- **Option B sync drift** if chosen without a CI guardrail.

## Evidence appendix (key proofs)
- `gh api .../contents/.claude-plugin` → **404** (no root manifest on remote).
- `gh api .../packaging/claude` → only `.claude-plugin/`; `.../packaging/codex/plugins/ai-writing-suite` → only `.codex-plugin/` (no body on remote).
- `git check-ignore -v .../packaging/claude/SKILL.md` → ignored (`.gitignore:9`).
- `claude plugin marketplace add /tmp/empty` → "Marketplace file not found at <src>/.claude-plugin/marketplace.json" (proves resolution path).
- `claude --version` 2.1.168; no `claude plugin publish` subcommand; `claude plugin tag --dry-run` → `ai-writing-suite--v1.0.0`.
- `codex` 0.137.0; `marketplace add` supports `--ref`, `--sparse`; working git marketplaces (EveryInc/compound-engineering) **commit** their plugin body.
- Umbrella: `gh pr view 4` CLOSED unmerged; `git log origin/main..rename-ai-writing-suite` = 2 ahead; `git branch --merged main` (suite) lists both feature branches.
- Tests re-run green this session: 23/23 unittest, smoke 3/3, fixtures 8/8 @ 38%; LLM-judge path emits SKIPPED (no model wired).

---

# UPDATE (2026-06-07, later) — Owner decisions + Cursor recon → consolidated 3-host plan

**Owner decisions:** publish body = **Option A (point at tracked source tree)**; host scope =
**Claude + Codex + Cursor, all now** (RovoDev still out). This supersedes the Claude-first framing.

## Cursor recon (separate read-only agent; live cursor.com docs)
- **`cursor` CLI NOT installed locally** → Cursor install/load **cannot be smoke-tested on this
  machine.** Verify by structure + frontmatter, or owner installs Cursor.
- **Mechanism:** Cursor natively reads **`.cursor/skills/<name>/SKILL.md`** (same frontmatter as
  this suite), auto-discovered from `.cursor/skills/` + `.agents/skills/` (project) and
  `~/.cursor/skills/` + `~/.agents/skills/` (global). Invoked by relevance or `/skill-name`.
  Also-exist-but-wrong-primitive: `.cursor/rules/*.mdc` (passive context injection), `AGENTS.md`.
  **No plugin/marketplace concept.** (Source: cursor.com/docs/skills, /docs/rules.)
- **DOC BUG to fix:** design doc §4 + `packaging/README.md:189` + `CHANGELOG.md` (`cursor-rules/`)
  all specify `.cursor/rules/*.mdc` for Cursor — WRONG. Correct to `.cursor/skills/` + `SKILL.md`.
- **Cursor needs zero manifest** — just the SKILL.md tree in a discovery location.

## The wrinkle Option A can't fully cover (decision needed)
"Point at the tracked source tree" is clean for some hosts but not all, because each host discovers
content differently:

| Host | Can it point straight at `skills/ai-writing-suite/`? | What it actually needs |
|---|---|---|
| **Claude** | ✅ Yes | Root `.claude-plugin/marketplace.json` (+`plugin.json`) whose `source` = the tracked source tree. **No committed body.** |
| **Cursor** | ✅ Yes (as a copy) | Install doc: copy `skills/ai-writing-suite/` → user's `.cursor/skills/ai-writing-suite/`. Source SKILL.md is already Cursor-valid. **No committed body** (accepts evals/ bloat, like Claude). |
| **Codex** | ❌ No | Codex marketplace entry `source:{source:local, path:./plugins/<name>}` needs the body **committed at that path**. A relative `../../` escape to the source tree is unverified/risky. → Codex is the **one host that needs a committed generated body**. |

So the real decision is how uniform to be:

- **Plan 1 — Minimal (recommended):** Claude points at source (no body); Cursor install = copy
  source subtree (no body); **Codex** gets a committed generated body via `sync.sh` + a drift
  guardrail (`sync.sh --check` in CI). Smallest committed surface; honors Option A everywhere it can.
- **Plan 2 — Uniform:** commit generated bodies for all three + guardrail. More consistent, larger
  sync surface (re-expands the R4 drift risk to all hosts).

## Consolidated execution order (after the decision + go)
1. **Doc-correct Cursor primitive** (design doc / packaging README / CHANGELOG: rules → skills). Small.
2. **Wire `sync.sh`** for the chosen plan: add a Cursor target (generates `.cursor/skills/...`); for
   Codex ensure the body is produced + (per plan) tracked; add `sync.sh --check` (stale-detect).
3. **Add tracked manifests:** root `.claude-plugin/marketplace.json` (+ plugin.json) → source tree;
   root-level Codex `.agents/plugins/marketplace.json` (relocate from the deep path for one-liner UX)
   + committed Codex body.
4. **README Quickstart:** exact install per host (Claude `marketplace add surahli123/ai-writing-suite`
   + `plugin install`; Codex `marketplace add … [--sparse]`; Cursor copy-dir / GitHub import).
5. **VERIFY (the real gate):**
   - Claude: fresh-clone `marketplace add` + `plugin install` → canned prompt → `comms-polish` fires. ✅ local
   - Codex: fresh-clone `marketplace add` + `plugin add` → canned prompt. ✅ local
   - Cursor: ⚠️ structure/frontmatter validation only unless owner installs Cursor.
6. **Branch → PR → adversarial review (outward-facing/production default) → merge → push.**
7. **(optional, after smoke-pass, outward-facing)** tag `v1.0.0` for Claude + Codex `--ref` pinning.
8. **Step 2 (umbrella cleanup)** + **Step 3 (branch tidy)** as already specified — independent, can
   run in parallel with the publish work or after.

## Verification matrix (honest)
| Host | Local smoke possible? | Confidence after this work |
|---|---|---|
| Claude | Yes (claude 2.1.168) | High (fresh-clone install proven) |
| Codex | Yes (codex 0.137.0) | High |
| Cursor | **No (no CLI here)** | Medium — docs/structure only, unless Cursor installed |

## Updated open decisions
- **D-A:** Plan 1 (minimal, recommended) vs Plan 2 (uniform) for committed bodies.
- **D-B:** Cursor verification — accept docs/structure-only, or install Cursor to smoke it?
- (carried) tag timing (rec: after smoke), umbrella branch name, adversarial review before publish PR.
