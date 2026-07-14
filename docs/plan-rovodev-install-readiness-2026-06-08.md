# Plan — RovoDev install readiness for ai-writing-suite (2026-06-08)

**Status: PLAN ONLY — awaiting owner go before any mutation.**
Source: read-only audit workflow `wf_baa477e0-e0c` (4 agents: repo audit + RovoDev doc research
+ router/invocation analysis → synthesis). RovoDev is currently **deferred to v2** in the repo
(`README` RovoDev section + `packaging.md:55-58`); no RovoDev packaging/install/test exists yet.

---

## Headline

- **Verdict: `small_packaging_work`. You can test TODAY** via copy-folder + explicit invocation —
  no code change strictly required to *start*.
- The whole question turns on **two unknowns only answerable on your actual in-house RovoDev**:
  (1) which dir it discovers skills from, (2) whether it crawls *nested* skill dirs. A 5-minute
  manual smoke test answers both before any code is written.

## Confirmed (read from repo files) vs Unconfirmed (from public Atlassian docs / your build)

| Finding | Status |
|---|---|
| Router `SKILL.md` maps intent → sub-skill **name** but never says "READ that file" → on a non-crawling host the sub-skill logic won't load by itself | **CONFIRMED (files)** |
| Suite is pure-markdown, self-contained; no pip/MCP/host-specific deps in the retrieval path | **CONFIRMED (files)** |
| `comms-polish` frontmatter has no `allowed-tools` pin → RovoDev tool-name mismatch is low risk | **CONFIRMED (files)** |
| RovoDev is v2-deferred; zero existing evidence it loads there. "Works on Claude/Cursor" does NOT transfer | **CONFIRMED (repo)** |
| RovoDev discovery dir is `~/.rovodev/skills/` or `~/.agents/skills/` | **UNCONFIRMED** — public docs; verify on your build |
| RovoDev only does **flat** per-skill discovery, won't see nested `skills/ai-writing-suite/skills/comms-polish/` | **UNCONFIRMED** — the load-bearing unknown |
| RovoDev auto-triggers by description | **CONFLICTS** — public docs say yes; your MEMORY says in-house build has NO auto-trigger. Plan for explicit invocation |

## The core fragility (why "install it and it works" may not hold)

The 4 real capabilities (comms-polish, comms-draft, comms-qa, voice-onboard) live one level deep:
`skills/ai-writing-suite/skills/<name>/SKILL.md`. Claude auto-discovers them (a Claude feature).
A flat-discovery host likely registers **only the top-level router**, not the sub-skills. So
"install ≠ discover ≠ trigger" — three separate gates. Install may pass; discovery of the
sub-skills is the risk.

---

## Recommended plan (staged — smallest first, learn before building)

### Track A — YOU, on the company laptop (trivial, highest information)
A 5-minute manual smoke test that answers the two unknowns **before** any code:

1. Get the repo onto the laptop: `git clone https://github.com/surahli123/ai-writing-suite`
   (or copy the folder if corp policy blocks cloning).
2. Copy the suite into RovoDev's discovery dir (try the one `/skills` reports; candidates):
   ```
   cp -R ai-writing-suite/skills/ai-writing-suite ~/.rovodev/skills/ai-writing-suite
   # or: ~/.agents/skills/ai-writing-suite   (where your OMC/hyperframes skills already live)
   ```
   Dir name MUST equal the frontmatter `name:` → `ai-writing-suite`.
3. Fresh RovoDev session → run `/skills`. **Record: does only `ai-writing-suite` (the router)
   appear, or also the 4 sub-skills?** ← this single observation decides Option A vs B.
4. Invoke explicitly (don't rely on auto-trigger):
   > Use the ai-writing-suite skill. Rewrite this so it sounds less AI-generated; keep facts and
   > my voice. Mode: rewrite.  [paste draft]
5. If the agent reads only the router and stops, force it:
   > Read skills/ai-writing-suite/skills/comms-polish/SKILL.md and the files it references under
   > _shared/patterns/, then run the rewrite.
   Needing step 5 by hand = confirms the router self-sufficiency gap (Track B fixes it).

### Track B — ME, in the repo now (small, low-risk, can run in parallel with Track A)
6. **Patch the router to be self-sufficient.** In `skills/ai-writing-suite/SKILL.md` RovoDev
   section, after the intent→name table add: *"After selecting a sub-skill, READ
   `skills/<name>/SKILL.md` and every file it references (`../../_shared/patterns/*`,
   `references/*`, voice profile if present) before performing the task."* Forward-compatible —
   Claude/Cursor ignore it (they auto-load). Lowest-risk fix; may be enough if the router registers.
7. **Add a RovoDev install + invoke section to `docs/packaging.md`** (currently v2-deferred, no
   doc): confirmed dir path, copy command, explicit-invocation phrasing, `/skills` verify step.
8. **Add a one-line RovoDev load smoke check** mirroring the existing manifest smoke checks:
   skill registers in `/skills` + comms-polish produces before/after on a fixture draft = "done"
   on RovoDev (per the project verify rule: loads + before/after evidence).

### Track C — conditional (only if Track A shows nested NOT discovered AND router patch unreliable)
9. **Option B — flat repackage** of comms-polish as its own top-level RovoDev skill dir
   (`~/.rovodev/skills/comms-polish/`) with `_shared/patterns` copied alongside and relative paths
   fixed. RovoDev-specific; do NOT disturb the nested Claude/Cursor layout that already works.
   Effort: medium. Decide only after the smoke test.

## Still-open from earlier (don't lose these)
- **PR #5** (`chore/syntaxwarning-changelog`) — green, mergeable, awaiting your merge.
- **Phase 2b quality eval** — blocked on you collecting ~16-24 real drafts on the enterprise machine.

## Open questions only YOU can answer (from your real RovoDev)
1. Real skills discovery dir — `~/.rovodev/skills/`, `~/.agents/skills/`, or a corp path? (`/skills` shows it.)
2. Does it crawl NESTED skill dirs (SKILL.md two levels deep) or only flat? ← decides nested vs repackage.
3. Is description auto-trigger on, or explicit-only (your MEMORY says explicit-only)?
4. Install mechanism — `/skills` wizard, manual dir copy, or a locked internal registry that bans local folders?

## Git note
Repo hooks block direct `main` commits + committing plan/handover files → Track B/C go on a
feature branch → PR (rebase ff). This plan file stays UNTRACKED (like the other `docs/plan-*`).
