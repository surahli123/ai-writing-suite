# Implementation Plan — Eval Hardening ("Now" batch from the 2026-07-11 de-slop landscape research)

Date: 2026-07-13
Status: EXECUTING (product owner authorized plan + build + review pipeline this session)
Source: `docs/improvement-plan-deslop-landscape-2026-07-11.md` — suggested sequencing step 1
Branch: `feat/eval-hardening-now` (off `origin/main` @ `f0c77d0`)
Baseline evidence: `run_all.sh` green — 13/13 deterministic fixtures, calibration 38% (in 30-40% band)

## Scope (exactly the critic-verified "Now" batch)

| Item | What | Files touched |
| --- | --- | --- |
| #1 | Gold-FAIL prose fixtures (3-5 `expected_verdict: FAIL` before/after pairs: fabricated number, over-corrected overstepping, payoff_clear stub) in a **separate file** so the 30-40% calibration band is untouched | `evals/fixtures/fixtures_fail.json` (new), `evals/fixtures/run_fixtures.py`, `evals/fixtures/test_fixtures.py` |
| #6 | O2 presumed-misconception strawman fixture (`overstep-06-strawman-en`) — the one overstepping sub-type with zero dedicated example | `evals/fixtures/fixtures.json`, `evals/fixtures/test_fixtures.py` |
| #2 | Adversarial false-positive suite: clean human prose (incl. non-native-English + stylistically unusual) the detector must NOT flag; should-not-trigger pass rate reported as a new `run_all.sh` step | `evals/fixtures/false_positives.json` (new), `evals/fixtures/run_false_positives.py` (new), `evals/run_all.sh`, new test file |
| #5 | Quoted-evidence judge protocol (every dimension verdict must cite a quoted snippet) + cross-family runtime warning (judge model family == rewriter family) | `evals/fixtures/rubric.md`, `evals/fixtures/judge.py`, `evals/fixtures/test_judge_protocol.py` (new) |
| #26 | Version 1.1.0: `[Unreleased]` → `[1.1.0] - 2026-07-13` in CHANGELOG + bump both plugin.json manifests. **No git tag** (owner-gated, cut after merge) | `CHANGELOG.md`, `skills/ai-writing-suite/.claude-plugin/plugin.json` (or wherever the two manifests live), Codex `plugin.json` |
| #30 | Router seam fix: one disambiguating clause each in comms-polish + comms-draft frontmatter descriptions for mixed "polish this AND add a section" requests | `skills/comms-polish/SKILL.md`, `skills/comms-draft/SKILL.md` frontmatter only |

Out of scope (explicitly NOT built this session): everything in P2-P5 except #26/#30; anything
owner-gated (#20 retry tradeoff, #25 ingestion tooling, #29 positioning); the unverified
completeness-critic candidates (#7, #14, #17, #18, #22, #23).

## Hard invariants (every agent must respect)

1. **Never edit `fixtures.json`'s existing 13 fixtures or the calibration exclusion filter** to make anything pass. FAIL fixtures live in a separate file excluded from the naive-baseline miss-rate denominator.
2. The 30-40% calibration band must still read 38% (or in-band) after every change.
3. Stdlib-only — no pip installs; CI stays key-free (judge remains opt-in via `AIWS_JUDGE_*`).
4. INDEX.md / KB entries untouched.
5. CHANGELOG is written by the release agent (#26) and orchestrator only — implementation agents return a suggested bullet instead of editing it.

## Execution: 4 parallel Opus executors (OMC), disjoint file sets

- **Agent A** — #1 + #6 (fixture authoring + wiring). Forbidden: `run_all.sh`, `judge.py`, `rubric.md`, CHANGELOG.
- **Agent B** — #2 (FP suite, self-contained runner + new `run_all.sh` step 4). Forbidden: `fixtures.json`, `run_fixtures.py`, `test_fixtures.py`, `judge.py`, CHANGELOG.
- **Agent C** — #5 (judge protocol). Forbidden: `fixtures.json`, `fixtures_fail.json`, `test_fixtures.py`, `run_all.sh`, CHANGELOG.
- **Agent D** — #26 + #30 (release hygiene + frontmatter). Forbidden: everything under `evals/`.

## Verification & review pipeline (after implementation)

1. Orchestrator re-runs `run_all.sh` — all green + calibration in band, with output pasted.
2. `oh-my-claudecode:code-reviewer` (worktree-isolated) over the full diff.
3. `oh-my-claudecode:test-engineer` — test-adequacy/TDD pass (do the new evals actually
   discriminate? revert-guard spot checks).
4. `/adversarial-review` via Codex (GPT-5.6 Sol, xhigh reasoning) — BLOCKER/CONCERN/SUGGESTION
   verdict persisted under `reviews/`.
5. Fix findings, re-run suite, then PR (feature branch → main; owner merges + tags v1.1.0).

## Done means

- `run_all.sh` green including the new FP step; calibration still in band.
- New gold-FAIL fixtures demonstrably discriminate: unit tests assert the FAIL path
  (deterministically, via the canned-judge-response pattern already used in `test_fixtures.py`).
- FP suite reports a should-not-trigger pass rate and fails the run if a clean sample trips
  the detector at the flag threshold.
- Judge prompt template demands quoted evidence; parser surfaces it; missing evidence
  degrades to a warning (advisory judge stays advisory).
- Version strings + CHANGELOG consistent; both manifests say 1.1.0.
- All three review lanes' findings addressed or explicitly deferred with reasons.
