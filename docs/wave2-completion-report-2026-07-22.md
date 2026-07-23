# Wave-2 Completion Report — 2026-07-22

**Status: MERGED. All 8 lanes landed on `main` as PRs #53–#60 (owner-approved, 2026-07-22), in the order below with zero merge conflicts. Final main @ `2a54b28`: 407 tests, calibration 3/8 = 38%, 71 voice evals, refusal + artifact fixtures live, ALL CHECKS PASSED — verified locally and by CI on every merge push.**

Base: `main` @ `84aca44`. Worktrees under `~/Documents/aiws-wave2/`. Same pipeline as Wave-1: Codex (`gpt-5.6-sol`, high) implements per lane; the orchestrating session re-runs every eval suite itself; OMC reviewers (Sonnet; Opus architect for the design docs) verify; FAIL verdicts loop back through the same Codex session.

## Scoreboard

| Lane | Branch | Commits | Review |
|---|---|---|---|
| eval-integrity (A1-A3) | `feat/w2-eval-integrity` | 4 (incl. surface-enum pin `78a215e`) | PASS, 1 MINOR → fixed |
| eval-additions (B3-B6) | `feat/w2-eval-additions` | 4 | PASS, 1 informational |
| packaging (B7) | `feat/w2-packaging` | 4 (incl. two coverage commits after review) | FAIL → delta PASS (name + plugin-name dimensions both covered, red-proofed twice) |
| text-seam (B8) | `feat/w2-text-seam` | 1 | PASS via eval-additions review (documented-mirror escape hatch, exactly as planned R3) |
| hygiene (D1-D4) | `docs/w2-hygiene` | 4 (incl. index-wording fix) | PASS, 1 MINOR → fixed; all 11 PR attributions ground-truthed vs `gh pr list` |
| research (E1-E4) | `docs/w2-research-designs` | 5 (incl. review edits `0268202`) | Architect: E1/E4 ACCEPT, E2/E3 ACCEPT-WITH-EDITS → all 4 edits applied |
| polish-train (B1-B2) | `feat/w2-polish-train` | 2 | PASS, 2 MINOR (no rule loss) |
| artifact-lane (C1-C4) | `feat/w2-artifact-lane` (stacks on polish-train) | 2 | PASS; expect_baseline usage traced as correct (3-mechanism gate, precedent-consistent) |

Invariants held in every lane and re-verified by the orchestrator: full suite `ALL CHECKS PASSED`; calibration denominator exactly 8 with `3/8 = 38%`; 71 voice evals; refusal line present. comms-polish/SKILL.md: 433 → 305 → 311 lines (progressive disclosure + artifact routing), against the official 500-line cap.

## What shipped, by owner decision

- **Q2-A**: smoke expectations now doc-driven (magic index dead), untrusted-content body + surface enumeration pinned, harder `_CAP_RUN` holdout probe (closed a real blind spot).
- **Q2-B**: router decision-table pinned; retrieve() negative branch covered; draft criteria coupled to SKILL.md prose; `_CJK_RE` sync-pinned; packaging validator covers all 4 manifests + root router with a 4-test self-suite; stylometry mirror documented (single-sourcing rejected for standalone portability, per three in-repo sources).
- **Q2-C + Q3-1 + D2**: `artifact-density-budget.md` (C1 ruling, artifact-lane-only, prose stays deletion-first), `artifact-preflight.md` (durable-source tracing, visibility classes, hotspot-first, must-keep acceptance criteria, stop conditions, RUNTIME-ADVISORY rendered verification), conditional edit-mode routing, `artifact-01-status-card-en` fixture (detector_blind, must_preserve ×3).
- **Q2-D**: CHANGELOG current through Wave-1 (all PR attributions verified), `docs/00-index.md`, `.omx/` ignored, design-doc scope banner.
- **Q2-E**: four design docs; architect ruled **E1 (detector false-positive eval) as the first build lane** — fully grounded, clones the working false_positives capability pattern, zero calibration risk.
- **Q5-1**: folded into polish-train's progressive disclosure.

## Merge order (owner approval required; nothing pushed)

1. `feat/w2-eval-integrity`, `feat/w2-eval-additions`, `feat/w2-packaging`, `feat/w2-text-seam`, `docs/w2-hygiene`, `docs/w2-research-designs` — any order; file sets verified disjoint.
2. `feat/w2-polish-train`.
3. `feat/w2-artifact-lane` — last (contains polish-train; merging after it keeps the PR diff clean).

After each merge: `bash skills/ai-writing-suite/evals/run_all.sh` → `ALL CHECKS PASSED` with `3/8 = 38%` before the next.

## Follow-ups (non-blocking, next wave's candidates)

1. Build lane for E1 per the architect's ruling (then E2 with its two named guards).
2. comms-draft `### 2. Load the inputs` still carries a condensed banner paraphrase — point it at `_shared/voice-lookup.md` (polish reviewer's out-of-scope note).
3. B4's two negative tests exercise one guard branch (two input shapes); a structurally distinct negative would widen coverage.
4. C1's checklist citation is a paraphrase; quote "never a hard length target" literally if precision wanted.
5. E4's voice-onboard consent hook (deliberately deferred; design complete).

## Process notes

- One review FAIL (packaging) was empirical: the reviewer proved by /tmp revert experiments that half the new validator logic had zero test coverage; two follow-up commits closed both name dimensions, each red-proofed independently.
- Three MINORs were fixed directly by the orchestrator (index wording, surface-enum pin, plugin-name test) — each committed on its lane with branch-check, all re-verified.
- The text-seam BLOCKED report carried the spec's exact escape-hatch string in the handoff result; a reviewer note to the contrary was checked and dismissed against that evidence.

## Evidence trail

Plan: `docs/implementation-plan-wave2-2026-07-22.md` · handoff results: `~/.handoff/tasks/0722-cx-07..16.result.md` · reviewer verdicts summarized above (session transcripts) · Wave-1 context: `docs/wave1-completion-report-2026-07-22.md`.
