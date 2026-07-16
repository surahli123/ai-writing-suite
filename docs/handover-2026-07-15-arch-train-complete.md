# Handover — 2026-07-15: architecture roadmap 5/5 complete, 15 PRs landed

**Repo:** `~/Documents/ai-writing-suite` → github.com/surahli123/ai-writing-suite (PUBLIC)
**Branch:** `main` @ `357f645` — **push policy: main is PR-only, never commit directly;
feature branch → PR → merge (all 15 PRs this session went that way).**
**Suite state (verified at close):** run_all discovery-ordered 7 capabilities green
(`ALL CHECKS PASSED`); **366 unit tests**; calibration exactly `3/8 = 38%` (never moved
across the entire session); catalog registry **72 tell ids**; packaging validator green;
zero open PRs; local branches = main only; no leftover worktrees.

## What this session shipped (2026-07-13 → 07-15, PRs #25–#37 minus superseded #27)

1. **Prose train** — #25 prose mega-fix (remediation 1.8–1.13 + Q7/Q8/Q9), #26 Q10
   multi-genre voice profiles, #33 A1 follow-ups (successor to auto-closed #27),
   #32 research adoptions (epistemic invariants A1, FP-gate A2, S10 invented-jargon A3
   → catalog 71→72, deletion-first B5).
2. **Architecture train — the full approved roadmap (plan in PR #28)**: #30 aiws/kb
   dependency reversal (item 5), #31 judge evaluate() facade (item 4), #35 capability-runner
   discovery (item 1), #36 pattern registry + sole parser + checked-in projections (item 2),
   #37 aiws/text.py seam with zero band movement (item 3).
3. **Decisions & docs** — #28 approved arch plan + review records, #29 June-era docs archive
   (28 files) + the six-source research report, #34 C3 voice-precedence policy + D4 deferred
   (`docs/decisions-2026-07-15.md` — owner-delegated rulings, honestly labeled).
4. **Research loop** — 6-agent Sonnet workflow read 4 X threads (all replies, sentiment) +
   2 GitHub writing skills; 14 already-covered, 7 gaps (4 adopted, merged), 2 philosophy
   conflicts rejected. Artifacts: research decisions brief + what's-next console (claude.ai
   artifacts), `notes/research-writing-skills-landscape-2026-07-14.md`.

## Read first, in order

1. `docs/plan-architecture-roadmap-2026-07-14.md` — the executed plan (all 5 items DONE).
2. `docs/decisions-2026-07-15.md` + `docs/decisions-2026-07-13.md` — the complete ruling set.
3. `reviews/2026-07-15-pattern-registry-review.md` — contains the **9-rating owner-review
   list** (the main open item).
4. `reviews/2026-07-15-text-seam-review.md` — the Codex-executor/Codex-reviewer pipeline record.
5. `notes/research-writing-skills-landscape-2026-07-14.md` — adopted/deferred research map.

## Next steps (priority order)

1. **Owner: confirm/amend 9 metadata ratings** — S2 S6 T5 T9 R5 C11 (executor low-confidence)
   + R3 R4 F4 (axis question: severity=low may be detection-confidence leaking into the harm
   axis). Listed in `reviews/2026-07-15-pattern-registry-review.md`. Pure judgment pass; edits
   are one-word table changes + `python3 -m aiws.catalog` regen.
2. **Follow-up pool (S/M, all optional):** comms-polish catalog-list de-enumeration (deferred
   from item 2; collision reason now stale); recovery playbook (`references/recovery-playbook.md`
   sketch in the research gaps); genre presets +2 (PR description, release note); A1 findings
   context-bloat trim remainder (~1.7k tokens).
3. **Deferred by ruling (do NOT build without new owner word):** D4 agent-audience preset
   (decisions-2026-07-15). v2 pool unchanged: CJK detector scoring, corpus-derived stylometry
   baseline, RovoDev 4-skill re-verification (#27 owner-scheduled, company machine).

## Gotchas / parked

- **Calibration invariant:** the line must read exactly `3/8 = 38%`; premise-guard pins now:
  registry 72 (`test_report_contract.py:55`), cohorts (18,5), specificity 15/18. Adding a
  catalog entry → hand re-derive the pin (done twice: 67→71→72); never weaken.
- **Metadata enums are closed sets** (`aiws/catalog.py` VALID_SEVERITY/VALID_ENFORCEMENT) —
  unknown values raise. Regenerate projections with `python3 -m aiws.catalog`; freshness test
  fails on hand-edits inside marker blocks.
- **stylometry.py is deliberately NOT importing aiws.text** — it ships self-contained inside
  `_shared/` (portability); drift is blocked by a `(pattern, flags)` sync-pin test in
  `evals/test_text_seam.py`. Do not "clean up" the duplication.
- **Codex CLI operating rules (hard-won):** fact-check probes only (behavior-trace probes
  time out at xhigh — 3-strike circuit breaker fired 07-13); NEVER two codex exec in parallel
  (both parallel attempts double-timed-out; every solo run succeeded); execution tasks in
  staged ≤600s runs with `--sandbox workspace-write` in a dedicated worktree, orchestrator
  holds commit rights; always `timeout 600` + `-o <file>` + `</dev/null`.
- **Stacked-PR merge trap:** retarget the downstream PR's base to main BEFORE deleting the
  just-merged branch — GitHub auto-closed #27 on base deletion and refuses reopen (successor
  PR was the only recovery).
- **`gh pr merge --delete-branch` also deletes the local branch** when run inside the clone —
  don't double-delete afterward.
- The June-era `docs/handover-2026-06-02-personal-productivity-skills-next.md` is pre-extraction
  personal planning, committed in #29 with a flag in the PR body — owner OK'd by merging, but
  it's the file to pull if the public-repo stance ever changes.

## Stale-memory corrections (vault/index vs disk now)

- `~/agent-memory/projects/ai-writing-suite.md` and any note saying "341 tests / catalog 71 /
  architecture roadmap unblocked-but-not-started": NOW 366 tests, catalog 72, roadmap 5/5
  MERGED, evals are discovery-run (run_all.sh is a wrapper), aiws/ package exists
  (kb/catalog/text), judge behind evaluate().
- The 2026-07-13 handover's "Codex: scope a single run to ≤ one subsystem or it times out"
  is now refined: probe TYPE and CONCURRENCY are the real variables (see Gotchas).
- `feat/voice-onboard-exemplars-hardrules` was never local-only — it lives on origin
  (tracking config was merely absent); local copy deleted 07-15.

## Kickoff prompts

**Fresh Claude Code session (next hop: rating review + follow-up pool):**

```
Continue ai-writing-suite at ~/Documents/ai-writing-suite (branch off main @ 357f645; never
commit to main). Read docs/handover-2026-07-15-arch-train-complete.md first, then its "Read
first" list. Task 1 (owner-gated, interactive): walk me through the 9 metadata ratings queued
in reviews/2026-07-15-pattern-registry-review.md (S2 S6 T5 T9 R5 C11 + R3 R4 F4 axis
question) one at a time with the entry prose in front of me; apply my confirm/amend calls,
regen projections (python3 -m aiws.catalog), verify (run_all ALL CHECKS PASSED, 366+ tests,
calibration exactly 3/8 = 38%, registry 72), PR. Task 2 (if time): comms-polish catalog-list
de-enumeration + genre presets +2 (PR description, release note) per the follow-up pool —
one branch each, review per repo convention. Done = all green + PRs opened.
```

**Codex second-opinion on any new diff (per the hard-won operating rules):**

```
timeout 600 codex exec --model gpt-5.6-sol -c model_reasoning_effort='"xhigh"' \
  --sandbox read-only -o /tmp/codex-review.md \
  "TIGHT fact-check of git diff main...<BRANCH> in this repo. Mechanical quote-and-compare
   probes only — no end-to-end behavior tracing. <3-5 numbered probes>. Output ≤300 words:
   BLOCKER/CONCERN/SUGGESTION + file:line, VERDICT line, VERIFIED_AGAINST: <BRANCH> @ <sha>." \
  </dev/null
```
