# Handover — three-wave improvement train complete (2026-07-23)

**Project:** ai-writing-suite · `~/Documents/ai-writing-suite` · branch `main` @ `87b7e00` (clean)

## Last sessions (2026-07-21 → 07-23)

Four-lane research (STORM workflow over 5 external skill repos + /improve nine-category audit + travel-agent humanizer-feedback review + Codex `gpt-5.6-sol` adversarial pass with disk arbitration) fed an owner-approved plan, then three implementation waves — every lane: Codex implements in an isolated worktree, orchestrator independently re-runs the eval suite, OMC reviewer verifies, FAIL verdicts loop back through the same Codex session.

- **Wave 1 (PRs #42–#52):** Tier-0 correctness — user-state/package boundary + resolver, KB tie-set retrieval + frozen-semantics doc, detector CJK refusal, fabrication verb-claim class, calibration measurement policy, untrusted-content contract, must_preserve eval, precedence policy, self-report divergence (blind-first), voice anchors (clean-room).
- **Wave 2 (PRs #53–#62):** eval-integrity (doc-driven smoke, contract-body pins, harder holdout probe), four deterministic pins (router/retrieval/draft-coupling/CJK), packaging validator + self-tests, stylometry mirror documented, hygiene (CHANGELOG/docs-index/.omx/banner), four research design docs (E1–E4), comms-polish 433→311 lines (voice-lookup extraction + progressive disclosure), artifact edit lane (density ruling C1, preflight, conditional routing, fixture).
- **Wave 3 (PRs #63–#64):** E1 known-human FP eval built (stdlib runner, provenance/checksum validation, Wilson intervals, capability separated from calibration) + 8-sample public-domain seed corpus — **first empirical specificity datum: 0/8 FP @ threshold 14** (supplemental-labeled); wave-2 follow-ups closed incl. the empty-entries sentinel-path negative.

Also outside the repo: **Codex plugin registration fixed** (`ai-writing-suite@ai-writing-suite` installed+enabled v1.1.0, source-pointing; verified via `codex plugin list`) and the stale `~/.codex/skills/ai-writing-humanizer` converted to a redirect stub (legacy body archived in its references/).

## Current state

- Suite: 419 tests, calibration 3/8 = 38% band intact, 71 voice evals, CJK refusal + artifact + known-human capabilities live, CI green on every merge push through #64.
- All wave worktrees/branches cleaned; only `main` remains.
- Evidence trail in-repo: `docs/plan-systematic-improvement-2026-07-21.md`, `docs/implementation-plan-wave{1,2}-*.md`, `docs/wave{1,2}-completion-report-2026-07-22.md`, `reviews/2026-07-21-codex-adversarial-research-review.md`, `notes/research-no-ai-slop-2026-07-22.md`, four `docs/design-*.md`.

## Next steps (priority order)

1. **Owner rulings pending:** (a) no-ai-slop absorption lane — 3 catalog candidates (faux-insight setup entry; C7 statement-form colon-reveal extension; delete-don't-rewrite kicker remediation line) + NOTICE.md credit (MIT, petergyang/no-ai-slop); (b) detect-mode 0-100 score epistemics — keep / evidence-first-score-second / drop (see notes/research-no-ai-slop-2026-07-22.md §Process-level findings).
2. **E1 falsifiable next step:** license-audit + score 100 public-domain samples (25 × 4 genre proxies) @ threshold 14; >5 flagged ⇒ specificity overclaimed. Design: `docs/design-detector-false-positive-eval.md`.
3. **E2 build lane** (tell-catalog versioning) — with its two named guards: test_catalog_projection regeneration + the two-column `_META_*` parser pin (catalog.py:60-61).
4. Owner-gated real-writer FP set (consent + de-identified, per E1 design) and the still-blocked P3 quality-eval corpus (~16-24 real enterprise drafts).
5. E4's voice-onboard consent hook (design complete, deliberately deferred).
6. RovoDev live acceptance test of the suite (long-standing).

## Key context / gotchas

- Calibration denominator = the 8 `expect_baseline` non-detector_blind fixtures; only 3/8 passes the 30–40% band. Any fixture change goes through `evals/fixtures/calibration-policy.md` versioning.
- INDEX.md retrieval semantics FROZEN; smoke expectations are doc-driven via `**Expected files:**` markers in SMOKE-TEST.md; Case 1 is a genuine documented tie `['clarity.md','revision.md']`.
- stylometry.py is intentionally standalone — mirrors of `_SENT_SPLIT`/`_CJK_RE` are guarded by StylometrySyncPin, do not single-source them.
- Rendered/browser verification is runtime-advisory ONLY (ruling D2); density budgets are artifact-lane-only (ruling C1/Q3-1).
- The proven pipeline discipline: Codex produces / orchestrator independently verifies / reviewer verdicts / owner merges. Escape hatches must STOP, not improvise.

## Read first

`docs/wave2-completion-report-2026-07-22.md` (freshest full picture) → `notes/research-no-ai-slop-2026-07-22.md` (pending rulings) → `docs/design-detector-false-positive-eval.md` (next build).
