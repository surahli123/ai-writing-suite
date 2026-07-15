# Handover — AI Writing Suite: RovoDev verified + Phase 2b calibration prep (2026-06-09)

Project: **AI Writing Suite** — `~/Documents/ai-writing-suite/`
GitHub: **github.com/surahli123/ai-writing-suite** (public, default `main`)
Branch: `main` @ `947ada5` (after PR #5 + #6 merged). **Two PRs OPEN, awaiting owner merge: #7, #8.**

## What shipped this session (4 PRs)

1. **PR #5 — cleanup** (detector `\S+` SyntaxWarning + CHANGELOG) — **MERGED** (`e470194`).
2. **PR #6 — RovoDev: self-sufficient router + experimental manual-install doc** — **MERGED** (`947ada5`).
   Router (`SKILL.md`) now tells the agent to READ the chosen sub-skill on demand; `packaging.md`
   gained a manual-install section. (Was "deferred to v2".)
3. **PR #7 — docs(rovodev): correct discovery claims after smoke test; mark verified** — **OPEN**,
   CI green, mergeable. Branch `docs/rovodev-verified-corrections`.
4. **PR #8 — feat(evals): miss-target calibration table (Phase 2b prep)** — **OPEN**, CI green,
   mergeable. Branch `feat/calibration-miss-target-table`.

## Big result: RovoDev VERIFIED working (supersedes "deferred to v2")

On-device smoke test on the owner's **in-house RovoDev** (2026-06-08):
- **Explicit invocation** (auto-trigger is OFF on the in-house build — confirmed).
- `/skills` registered the **router AND all four nested sub-skills** → RovoDev **does crawl nested
  dirs** (overturned the earlier "only the router" prediction).
- `comms-polish` produced a real **before/after** rewrite end-to-end.
→ **Option B (flat repackage) is moot.** PR #7 corrects the now-false predictions in `main`'s docs
(README + `packaging.md` + the router note) and adds a CHANGELOG entry.

## Calibration table (PR #8) — Phase 2b prep

New stdlib helper `evals/fixtures/calibration.py` (+ `test_calibration.py`):
- `valid_miss_counts(n)` / `miss_target(n)` / `table()` / `format_table()`: which naive-baseline
  miss counts keep the fail rate in the live **30-40%** band, per eval-set size *n*.
- Turns the calibration knife-edge into a **lookup** to run BEFORE adding/removing fixtures.
  CLI: `python3 -m fixtures.calibration 5 26`.
- **Findings:** n=4 and n=7 are **UNCALIBRATABLE** (no integer miss fits the band). Planned
  ~24-item 2b set → **target 8 misses (33.3%)**. Current n=8 → 3 misses (37.5%), unchanged.
- `miss_target` rule = closest to 35% midpoint (max edge margin; ties→lower).
- `AgreesWithLiveFixtures` test ties the table to live `fixtures.json` (no drift). Does **NOT**
  touch `run_fixtures.py` — live 3/8 = 38% path unchanged.
- Verified: `run_all.sh` green, **58 tests** (was 51), calibration in band.

## Current state (verified)
- `main` @ `947ada5`; 51 tests on main (→ 58 once #8 merges). CI green on every PR.
- **OMC updated 4.14.4 → 4.14.6** this session — **restart Claude Code** to load it. Backup of
  global CLAUDE.md at `~/.claude/backups/CLAUDE.md.pre-omc-4.14.5-20260609` (only the OMC version
  marker changed; user customizations intact).

## NEXT (ordered)
1. **Merge PR #7 then #8** (owner's call; both green/mergeable). Possible trivial CHANGELOG
   conflict (both add `### Added` bullets, at different anchors by design — check on merge).
2. **Phase 2b proper — STILL BLOCKED** on owner collecting **~16-24 real AI-shaped drafts on the
   ENTERPRISE computer.** Once collected: use the calibration table to pick a calibratable size +
   miss target (n=24 → 8 misses); add real two-class GOLD + fabrication-trap fixtures paired with
   rebalancing catch fixtures; wire cross-family judge live (3× replication, majority-vote);
   **calibrate vs human labels BEFORE trusting numbers** (broken-ruler guard); frozen dev/test
   holdout the self-improvement loop never reads.
3. Optional: promote RovoDev **v2→v1** in the project `CLAUDE.md` "Target surfaces" line (left
   untouched this session — owner's roadmap call; PR #7 already updates README + packaging.md).

## Gotchas (carry forward)
- **Calibration knife-edge:** at n=8 only 3 misses (38%) is in band. Run
  `evals/fixtures/calibration.py` BEFORE adding any fixture. n=4 and n=7 are uncalibratable.
- **RovoDev:** explicit invocation only (no auto-trigger on the in-house build); it DOES discover
  nested sub-skills; router is patched self-sufficient as belt-and-suspenders.
- **Repo hooks** block direct `main` commits + committing `handover-*`/`plan-*` docs → those stay
  UNTRACKED (this handover too). Branch → PR (rebase ff).
- **Two open PRs off different bases:** #7 off the corrections branch, #8 off `main` (pre-#7).
  Disjoint files; no conflict expected except possibly CHANGELOG.
- **CI stays stdlib-only + key-free.** Never wire the judge into CI.

## Relevant files
- `evals/fixtures/calibration.py` + `evals/fixtures/test_calibration.py` (new this session)
- `skills/ai-writing-suite/SKILL.md` (router; RovoDev section)
- `docs/packaging.md` (RovoDev manual install)
- `docs/plan-phase2-quality-eval-2026-06-07.md` (2b design)
- `docs/plan-rovodev-install-readiness-2026-06-08.md` (RovoDev readiness plan)

## Handover prompt (paste into a fresh session)
> Continue **AI Writing Suite** at `~/Documents/ai-writing-suite/` (public repo
> github.com/surahli123/ai-writing-suite, branch `main` @ `947ada5`). Read
> `docs/handover-2026-06-09-rovodev-and-calibration.md` first. RovoDev is **verified working**
> (manual install + explicit invocation; discovers nested sub-skills). **Two PRs open awaiting my
> merge: #7** (RovoDev doc corrections) **and #8** (miss-target calibration table, Phase 2b prep).
> NEXT after merging: **Phase 2b proper is still BLOCKED on me collecting ~16-24 real AI-shaped
> drafts on my enterprise computer**; once I have them, use `evals/fixtures/calibration.py` to pick
> a calibratable set size + miss target (n=24 → 8 misses), add real GOLD + fabrication-trap
> fixtures, wire the cross-family judge live, and calibrate vs my hand labels BEFORE reporting
> numbers. Repo hooks block direct `main` commits + committing handover/plan files → branch + PR
> (rebase ff). Plan first, wait for my go. (OMC was updated to 4.14.6 — restart if not already.)
