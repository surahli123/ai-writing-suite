# Handover — AI Writing Suite: Phase 2a judge + engine-polish + cleanups (2026-06-08)

Project: **AI Writing Suite** — `~/Documents/ai-writing-suite/`
GitHub: **github.com/surahli123/ai-writing-suite** (public, default branch `main`)
Branch: `main` @ `1e6c2de` (clean; suite repo is `main`-only). PR #5 open (cleanups).

## What shipped this session (3 PRs)

1. **PR #3 — Phase 2a: opt-in advisory LLM judge** (MERGED → `0a4de7f`). Wired an
   opt-in, advisory judge into the eval harness. `evals/fixtures/judge.py` (stdlib-only,
   env-driven, key-gated 3-state gate: absent→SKIP / `AIWS_JUDGE_RUN=1`→call /
   auth·transport error→loud nonzero). Parses per-dimension PASS/FAIL and **re-computes
   the verdict in Python** (`no_fabrication`-overrides-FAIL), ignoring the model's
   self-reported VERDICT line. Always injects `no_fabrication` into the prompt (3/8
   fixtures omitted it). `expected_verdict` gold labels added (field-only; calibration
   intact). Advisory: never gates CI except a liveness 0/N tripwire. Adversarially
   reviewed (Codex): BLOCKER (subtle_tell placeholder leak) + CONCERN (incomplete-rep
   aggregation) fixed.

2. **PR #4 — engine-polish: distilled cross-skill hygiene** (MERGED → `1e6c2de`). 5 edits
   distilled from 4 external writing skills (huashu, khazix, Waza), adversarially pruned:
   (1) comms-polish re-scans output vs catalog before returning; (2) negative-routing
   hand-offs in sub-skill frontmatter; (3) deterministic Tier-1 word→swap table in
   `lexical-tells.md` + a **sync-test** (`evals/test_catalog_sync.py`) that parses the
   table and asserts it EQUALS `detector/patterns.py` TIER1; (4) human-gated GRADUATION
   step in `self-improvement.md` (never weakens "never auto-edit the catalog"); (5) layered
   `final-pass-checklist.md` with a hard L1 facts-floor + L4 acceptance question. Tri-reviewed
   (Codex + OMC code-reviewer + OMC test-engineer) — converged finding: the sync-test was a
   vacuous substring scan → fixed to parse-and-exact-match; added `test_skill_manifests.py`.

3. **PR #5 — chore: SyntaxWarning + CHANGELOG** (OPEN, CI green, awaiting your merge).
   `detector.py` docstring `\S+` was an invalid escape (fires on clean compile) → escaped;
   evals tree compiles clean under `-W error::SyntaxWarning`. CHANGELOG `[Unreleased]`
   updated with all the above.

## Current state (verified)
- **51 stdlib-only tests green**; `run_all.sh` (unit + KB smoke + fixture calibration @
  3/8=38%) passes; CI green on every PR. `run_all.sh` / `ci.yml` / `.gitignore` unchanged
  by all this work; the judge is never called in CI (no key).
- Both Phase 2a and engine-polish are on `main` and installable on Claude/Codex/Cursor
  (source-pointing architecture, unchanged).

## NEXT: Phase 2b — the comms-polish quality eval (the real gap)
This is the suite's bigger "trust" lever: actually **measure** rewrite quality with a
calibrated judge. **Blocked on you collecting ~16–24 of your own real AI-shaped drafts on
your ENTERPRISE computer** (the 2b eval set = hybrid: your real drafts primary + synthetic
fill). Once collected:
1. Assemble the before/after eval set (~24 items, 4 genres × 6, stratified by difficulty);
   add real two-class GOLD incl. fabrication-trap fixtures **paired with a rebalancing catch
   fixture** so the 30-40% calibration band holds (precompute the miss-target per n).
2. Run the judge live (cross-family — judge with a non-Claude model since rewrites are
   Claude) at 3× replication, majority-vote.
3. **Calibrate the judge BEFORE trusting numbers** (broken-ruler guard): per-dimension
   agreement vs your gold; defer kappa until ≥40 items (noise below that).
4. Frozen dev/test holdout the self-improvement loop never reads.
5. Live end-to-end: feed a real `before` through comms-polish, judge the live `after`
   (v1 only scores static hand-written rewrites — proves the judge, not the skill).
Full design: `docs/plan-phase2-quality-eval-2026-06-07.md` + `docs/test-plan-v1-2026-06-07.md`.

## Other open / parked
- **PR #5** (this repo) — merge when ready.
- **Umbrella PR #5** in `personal-productivity-skills` (removes the duplicated
  `ai-writing-humanizer`) — still awaiting your merge (separate repo, your call).
- Engine-polish optional #6/#7 (somatic C9 entry; comms-draft/comms-qa design notes) were
  deferred. Distillation proposal: `docs/proposal-distill-writing-skills-2026-06-07.md`.

## Key gotchas (carry forward)
- **CI stays stdlib-only + key-free.** `run_all.sh` never passes `--judge`; `test_catalog_sync`
  + `test_skill_manifests` are stdlib-only. A test (`CIClean`) enforces the deterministic path
  makes no network call. Don't add a pip dep or wire the judge into CI.
- **Calibration is a knife-edge** at n=8 (only 3 misses = 38% is in-band). Adding any fixture
  shifts the denominator — design each addition to keep miss-rate ~33%. Field-only edits are safe.
- **The judge re-computes verdicts in Python** — never trust the model's VERDICT line; SKIP
  (None) on unparseable, never fake PASS. Parser tolerates bulleted/bold/numbered lines.
- **Reviews:** OMC subagents return terse final tokens (`"Done."`) — pull findings from their
  transcript (parse assistant text), not the final message. Codex `exec` single-pass review
  (no delegation) finishes in budget; the `code-review` skill auto-spawns sub-lanes that blow
  the 10-min cap.
- **Verify publishes via fresh-clone install, never local validate.**

## Handover prompt (paste into a fresh session)
> Continue **AI Writing Suite** at `~/Documents/ai-writing-suite/` (public repo
> github.com/surahli123/ai-writing-suite, branch `main` @ `1e6c2de`). Phase 2a (opt-in
> advisory judge) + engine-polish are MERGED; cleanups PR #5 may be merged. 51 tests green.
> Read `docs/handover-2026-06-08-phase2a-enginepolish.md` first, then
> `docs/plan-phase2-quality-eval-2026-06-07.md`. NEXT = **Phase 2b quality eval** — I'm
> collecting ~16–24 real AI-shaped drafts on my enterprise computer for the eval set; once I
> have them, assemble the before/after set (keep the 30-40% calibration band), wire the
> cross-family judge live, and calibrate it against my hand labels BEFORE reporting any
> quality numbers. Repo hooks block direct `main` commits + committing `handover-*`/plan
> files → branch + PR (rebase ff). Plan first, wait for my go.
