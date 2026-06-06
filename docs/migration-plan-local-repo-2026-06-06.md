# Migration Plan — AI Writing Suite → Independent LOCAL Repo

Date: 2026-06-06
Status: **PLAN ONLY — awaiting explicit "go"**
Scope: **Local filesystem + local git only. NO GitHub actions in this phase.**

---

## 0. Restate (confirm before I act)

- **(a) Plan-only or plan+build?** Plan-only now → migrate after you approve → build the v1 suite
  in a *separate* approved phase. This doc covers the **migration only**, not the v1 build.
- **(b) In scope:** create a new independent local repo for `ai-writing-suite`; the existing
  Codex-path copy stays untouched as a backup until you confirm deletion.
- **(c) Expected output:** a working independent local git repo + a 3-line "done" report.

---

## 1. Your decisions (this session)

| Q | Decision | Effect on plan |
|---|----------|----------------|
| Migration shape | **Move local folder only** + override: *"local repo, not GitHub as of now"* | Local-only. No new GitHub repo, no push, no remote rename. |
| Git history | **Preserve suite history** | Use `git clone` (local), not fresh `git init`. |
| PR #4 | "Close PR #4" — **but** GitHub override defers it | PR #4 left OPEN for now; close it later when we do the GitHub phase. |

---

## 2. The one open decision in this plan

**How much to carry over + the mechanic.** Two clean options — I recommend **A**:

### Option A — Local clone, then prune (RECOMMENDED)
1. `git clone` the umbrella repo (local path → local path). Full history preserved automatically,
   including the design doc, the rename commit, and everything else.
2. In the new copy: delete `skills/agent-goal-contracts/`, flatten/keep `skills/ai-writing-suite/`,
   update `README.md` + `CLAUDE.md` to be suite-only. Commit that as one "extract to standalone repo" commit.
3. Remove the `origin` remote so we can't accidentally push to the umbrella. (No GitHub this phase.)

- **Pros:** simplest, safest, preserves *all* history (incl. root-level `docs/`), nothing on GitHub touched.
- **Cons:** the new repo's *history* still mentions `agent-goal-contracts` (it's deleted in the latest
  commit, just visible in `git log`). Cosmetic only.

### Option B — `git subtree split` (surgical extract)
- Extract only `skills/ai-writing-suite/` history into a brand-new repo.
- **Pros:** history contains *only* suite commits.
- **Cons:** (1) misses root-level `docs/` (design doc, handovers live at repo root, not under the skill);
  (2) the `ai-writing-humanizer → ai-writing-suite` rename means pre-rename history may not follow the
  prefix cleanly. More steps, more gotchas. Overkill for a personal project.

> **My recommendation: Option A.** It honors "preserve history" with the least risk, and the only
> downside is cosmetic log entries. You're a learner — A is the boring, safe choice.

---

## 3. Proposed new local home

`~/Documents/ai-writing-suite/`  (out of `~/Documents/Codex/2026-06-01/...`)

Confirm this path or give me another.

---

## 4. Step-by-step (Option A) — what I'll run after "go"

```bash
# 1. Sanity: confirm clean-ish state, current branch (rename-ai-writing-suite has the latest content)
cd ~/Documents/Codex/2026-06-01/personal-productivity-skills
git status --short
git branch --show-current

# 2. Local clone to the new home (full history, local-to-local, no network)
git clone . ~/Documents/ai-writing-suite

# 3. In the new repo: check out the branch that has the rename + v1 design, make it the working line
cd ~/Documents/ai-writing-suite
git checkout rename-ai-writing-suite      # or merge it into a fresh main locally

# 4. Remove the GitHub remote (no GitHub actions this phase)
git remote remove origin

# 5. Prune to suite-only (separate, reviewable commit — I'll show staged files first)
git rm -r skills/agent-goal-contracts
#   + edit README.md / CLAUDE.md to drop umbrella + agent-goal-contracts language
#   + (optional) flatten skills/ai-writing-suite/* to repo root — DECISION below

# 6. Commit the extraction (after you approve the staged file list)

# 7. Verify (see §6)
```

### Sub-decision: flatten or keep nesting?
- **Keep `skills/ai-writing-suite/`** (no flatten) → matches the design doc's eventual multi-sub-skill
  layout (`skills/comms-polish/`, etc.). **Recommended** — the suite *grows into* sub-skills.
- **Flatten to root** → simpler now, but fights the planned architecture later.

> Recommend **keep nesting** — the v1 design already assumes a `skills/` + `_shared/` layout.

---

## 5. What I will NOT do (guardrails)

- ❌ No `git push`, no new GitHub repo, no closing PR #4, no remote rename — **nothing on GitHub**.
- ❌ No deleting the original Codex-path copy until you confirm (it's our backup/rollback).
- ❌ No starting the v1 suite build — that's a separate approval.
- ❌ No new deps, no new files beyond this plan + the migration commits.

---

## 6. Verification (how I'll prove the migration worked)

1. `git -C ~/Documents/ai-writing-suite log --oneline -10` → history present (preserved).
2. `git -C ~/Documents/ai-writing-suite remote -v` → **empty** (no GitHub remote).
3. `ls ~/Documents/ai-writing-suite/skills/` → `ai-writing-suite/` present, `agent-goal-contracts/` gone.
4. `git -C ~/Documents/ai-writing-suite status` → clean tree.
5. Original `~/Documents/Codex/.../personal-productivity-skills` → **untouched** (verify git log + remote intact).

Report back as a 5-line PASS/FAIL table, then ask before any cleanup of the original.

---

## 7. After migration (NOT now — your call later)

- GitHub phase (when you're ready): create `surahli123/ai-writing-suite`, push, close PR #4 on the umbrella.
- v1 suite build: follow `docs/design-ai-writing-suite-v1-2026-06-06.md` §5 (separate approval).
- Update memory `project_ai_writing_suite.md` with the new local path.

---

## 8. Open questions for you (answer inline, I'll proceed)

1. **Option A (clone-then-prune)** or B (subtree split)? — I recommend **A**.
2. **New local path** = `~/Documents/ai-writing-suite/`? — yes / give another.
3. **Keep `skills/` nesting** (recommended) or flatten to root?
4. Anything else you want carried/dropped (e.g. the `.omc/` state dir, untracked handovers)?
