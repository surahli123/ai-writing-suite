# Handover — 2026-07-13: v1.1.0 shipped, four feature lanes + E2E remediation merged

**Repo:** `~/Documents/ai-writing-suite` → github.com/surahli123/ai-writing-suite (PUBLIC)
**Branch:** `main` @ `89d8c2b` — everything merged; **push policy: main is PR-only, never
commit directly; feature branch → PR → merge (all nine PRs this session went that way).**
**Tag:** `v1.1.0` cut at `8220432` and pushed.
**Suite state (verified at close):** `evals/run_all.sh` 7/7 steps green; 341 unit tests OK;
calibration exactly `3/8 = 38%`; `scripts/validate_packaging.py` green; no open PRs.

## What this session shipped (PRs #15–#23, all merged)

1. **#15 eval hardening + v1.1.0** — gold-FAIL judge-discrimination fixtures; synthetic FP
   fence (planted controls); quoted-evidence judge protocol with verbatim validation;
   confusion-matrix discrimination (a constant always-FAIL judge now reads balanced
   accuracy 0.5, not 4/4); THE production fix: comms-draft frontmatter was invalid strict
   YAML since June → skill silently undiscoverable on fresh installs (fixed + class
   regression test).
2. **#16 behavioral evals** (comms-draft/voice-onboard artifact-contract graders, mutant
   families + black-box holdout) + the session's full paper trail (12 review records,
   16 owner decisions, remediation plan, integration ledger).
3. **#17 release hygiene** — root LICENSE, NOTICE nature-skills MIT-era provenance
   (bounds proven; upstream SHA is a dated candidate w/ TODO), CI packaging validator,
   README reconciliation + quickstart, RovoDev claims narrowed (Q15).
4. **#18 catalog/lifecycle** — register-shift consolidated w/ validity condition (Q16),
   C2/H7/H8 + S9/L1 dedup, R1→C8 fix-loop closed, lifecycle schema repaired
   (graduated status, 4 scopes, concrete promotion procedure).
5. **#19–#22 the four product lanes** — narrative-shape category (N1–N4, judge-only),
   stylometric fingerprint (per-genre, recomputable numbers, CJK refuse), audit-report
   output contract (step 7), KB ingestion/validation tooling.
6. **#23 CHANGELOG close-out.**

## Read first, in order

1. `docs/integration-notes-2026-07-13.md` — FINAL STATE section (bottom) = ground truth.
2. `docs/decisions-2026-07-13.md` — the sixteen owner rulings; Q7–Q10 govern the next task.
3. `docs/remediation-plan-e2e-2026-07-13.md` — items 1.8–1.13 are the open queue.
4. `reviews/2026-07-13-e2e-product-prose.md` — the A1 findings the next task fixes.
5. `reviews/2026-07-13-architecture-improve-review.md` — the unblocked refactor roadmap.

## Next steps (priority order)

1. **Prose mega-fix** (remediation 1.8–1.13 + decisions Q7/Q8/Q9): comms-polish's
   fabricating worked example (A1 BLOCKER — the example invents a retry job the rules
   forbid); router executable classify-and-load step (it currently REFUSES to route when
   directly invoked); Q7 full-document mixed mode (existing text = immutable source,
   draft returns the whole revised doc + runs polish final-pass); Q8 offer-then-degrade
   voice fallback PLUS the owner rider: offer voice capture after comms-polish runs AND
   after user manual edits (edit delta = strongest voice signal — research #16 as product
   behavior); Q9 comms-qa frontmatter says source-locked KB answer + separately-labeled
   extras, user can request strict; voice-profile canonical header list (producer/consumer
   drift); stale router status prose; dead refs (voice "project plan R1",
   scenario-presets "design §5").
2. **Q10 multi-genre voice-profile contract — DESIGN DOC FIRST** (owner overrode the
   one-genre recommendation; wants it built). Storage (per-genre files), IDs,
   default-selection rules, consumer lookup in comms-polish + comms-draft. Owner reviews
   the design before any build.
3. **Architecture roadmap** (all unblocked by Q1–Q6): capability-runner discovery to
   replace run_all.sh ordinal steps (now 7 and counting); pattern-markdown-as-registry
   (Q1 two-fields severity/enforcement; Q5 checked-in generated projections); one
   text-analysis seam before #14 (Q4 versioned measurement policy); judge.py facade;
   tools→evals dependency reversal.
4. **Cleanup:** delete merged local branches (feat/*, fix/*, integrate/*, chore/*) + the
   empty `feat/audit-report-template`; prune `.claude/worktrees/` agent worktrees
   (now gitignored); curate ~30 untracked June-era docs/ + reviews/ files (decide
   commit-or-archive — they include the June handovers).

## Gotchas / parked

- **Never commit to main** (repo CLAUDE.md); every change this session went branch→PR.
- **Calibration invariant:** naive-baseline line must read exactly `3/8 = 38%`;
  detector_blind + gold-FAIL fixtures are excluded from the denominator by design —
  never "fix" the filter (fixtures.json `_doc` explains).
- **Premise guards WILL fire on cohort changes** — test_fixtures.py pins (18, 5) cohort
  sizes and audit_report pins 71 catalog ids. Adding fixtures/patterns → re-derive the
  hand-computed expectations (never weaken; this session did it twice: 14/4→18/5, 67→71).
- **Codex CLI:** always `timeout 600` + `-o <file>` (--output-last-message) — piping
  through `tail -c` DESTROYED two structured verdicts this session before the flag was
  adopted. Scope a single run to ≤ one subsystem or it times out (two 600s timeouts).
- **INDEX.md (KB) retrieval semantics FROZEN** (Q13 re-confirmed); kb_ingest now
  preserves the shipped header — keep it that way.
- **Deterministic evals are output-contract fences, NOT behavioral coverage** (advisor
  ruling; honest wording is load-bearing in README/CHANGELOG). Live behavior = only the
  opt-in judge lane; scheduled lane purpose = release regression (Q2).
- The stylometry function-word baseline is register-(c) approximate (documented in
  BASELINE_RATES); a corpus-derived baseline is a v2 item.
- nature-skills exact upstream SHA = dated candidate + TODO in NOTICE §4 — do not
  present it as confirmed.

## Stale-memory corrections (vault/index vs disk now)

- `~/agent-memory/projects/ai-writing-suite.md` says "main @ b2db0e5, 65 tests,
  v1.1 optional bump parked" — NOW: main @ 89d8c2b, 341 tests, v1.1.0 TAGGED and
  released, 9 PRs merged 2026-07-13. P3 eval upgrade is STILL owner-gated on real
  enterprise drafts (unchanged).
- That memory also says "OMC subagents return terse final tokens" — this session's
  pattern: lane agents often go idle WITHOUT a final report; SendMessage the same agent
  to resume (it keeps branch + context) — strictly better than re-dispatch.
- The router seam clause (#30, merged) is now KNOWN-INSUFFICIENT — A1 proved mixed
  requests route to a skill that forbids editing existing text. Q7's full-document
  contract is the real fix (next session's task 1).

## Kickoff prompts

**Fresh Claude Code session (task 1+2, the prose mega-fix + Q10 design):**

```
Continue ai-writing-suite work at ~/Documents/ai-writing-suite (branch off main @ 89d8c2b;
never commit to main). Read docs/handover-2026-07-13-e2e-hardening-shipped.md first, then
its "Read first" list. Task 1: the prose mega-fix — remediation items 1.8–1.13 in
docs/remediation-plan-e2e-2026-07-13.md, implementing owner decisions Q7 (full-document
mixed mode), Q8 (offer-then-degrade + post-edit voice-capture rider), Q9 (qa labeled-extra
+ frontmatter fix) from docs/decisions-2026-07-13.md; A1 findings with file:line are in
reviews/2026-07-13-e2e-product-prose.md. Dispatch Opus executors per my routing table;
review with code-reviewer + /adversarial-review (Codex gpt-5.6-sol xhigh, timeout 600,
-o flag, one subsystem per run). Task 2 (before building anything for it): a one-page
design doc for Q10 multi-genre voice-profile contract (storage/IDs/selection/consumer
lookup) → my review gate. Done = run_all.sh 7/7 green, calibration exactly 3/8 = 38%,
341+ tests OK, packaging validator green, PR(s) opened.
```

**Codex second-opinion (GPT-5.6 Sol, xhigh) on the finished prose fix:**

```
timeout 600 codex exec --model gpt-5.6-sol -c model_reasoning_effort='"xhigh"' \
  --sandbox read-only -o /tmp/codex-prose-review.md \
  "Adversarial review of branch <BRANCH> vs main in this repo: the prose mega-fix for
   skills/ai-writing-suite/skills/*/SKILL.md + the suite router. Verify against
   reviews/2026-07-13-e2e-product-prose.md findings 1-15 and owner decisions Q7/Q8/Q9
   in docs/decisions-2026-07-13.md. Probe: does the router now execute a classify-and-load
   step when directly invoked? does the polish worked example contain ZERO facts absent
   from its before-text? trace the mixed request 'polish this doc and add a risks section,
   in my voice' end to end. BLOCKER/CONCERN/SUGGESTION + file:line + VERDICT line."
```
