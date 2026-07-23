# Wave-1 Completion Report — 2026-07-22

**Status: MERGED. All 10 lanes landed on `main` as PRs #42–#51 (owner-approved, 2026-07-22), in the order below. Final main @ `82af62d`: 394 tests, calibration 3/8 = 38%, 71 voice evals, ALL CHECKS PASSED — verified locally and by CI on every merge push. Two cross-lane conflicts (C↔G in `run_fixtures.py`, I↔J in the voice eval files) were resolved additively with the integrated suite re-run before each affected merge; F rebased clean.**

Base: `origin/main` @ `8dd1418`. Worktrees under `~/Documents/aiws-wave1/`. Implementation: Codex CLI (`gpt-5.6-sol`, reasoning=high) via handoff, one isolated worktree/branch per lane. Verification: every lane's `bash evals/run_all.sh` re-run by the orchestrating session (never trusting executor self-reports). Review: OMC code-reviewer (Sonnet) per lane, read-only, findings below.

## Scoreboard

| Lane | Branch | Commits | Eval evidence (independently re-run) | Review |
|---|---|---|---|---|
| E T0-5 calibration policy | `docs/t0-5-calibration-policy` | 1 | ALL CHECKS PASSED | PASS, 0 findings |
| D T0-4 fabrication gate | `feat/t0-4-fabrication-gate-honesty` | 2 | ALL CHECKS PASSED; 3 gold-catch verb-claim tests | PASS, 1 MINOR (OR-grounding design note) |
| G T1-8 must_preserve | `feat/t1-8-must-preserve-eval` | 2 | ALL CHECKS PASSED; substring trap closed (150⊅50 repro) | PASS, 1 MINOR (belt+suspenders substring check) |
| A T0-1 state boundary | `feat/t0-1-user-state-boundary` | 3 (incl. LR-001 archive) | ALL CHECKS PASSED; guard test fires on planted LR-999 | PASS, 1 MAJOR → resolved (LR-001 archived to `docs/retired-learned-rules-archive.md`) |
| F T1-4 untrusted-content | `feat/t1-4-untrusted-content-contract` | 2 | ALL CHECKS PASSED | PASS, 1 MINOR (contract body not content-pinned) |
| C T0-3 CJK refusal | `feat/t0-3-detector-cjk-refusal` | 2 (after approved scope extension) | ALL CHECKS PASSED; `[PASS] overstep-04-selfqa-zh refusal: as declared`; old-vs-new Latin byte-identical | PASS, 0 findings |
| B T0-2 KB retrieval | `feat/t0-2-kb-retrieval-protocol` | 4 | ALL CHECKS PASSED; smoke 5/5 with exact tie-set + exclusivity assertions | FAIL → delta PASS (Case-1 latent tie surfaced, pinned, documented) |
| H T1-3 precedence policy | `feat/t1-3-precedence-policy` (stacks on A) | 1 | ALL CHECKS PASSED | PASS, 1 MINOR (hyperlink style nit, skipped) |
| I T1-1 self-report divergence | `feat/t1-1-self-report-divergence` (stacks on H) | 4 (incl. link-convention fix) | ALL CHECKS PASSED; 62 voice evals; `self_report_divergence` 10/10 must-catch | PASS, 1 MINOR → fixed (`a30974e`) |
| J T1-2 voice anchors | `feat/t1-2-voice-anchors-cleanroom` (stacks on H) | 2 | ALL CHECKS PASSED; 62 voice evals; `anchor_provenance` 6/6 must-catch | PASS, clean-room audit CLEAN |

Calibration invariant held in every lane: `Naive-baseline miss rate: 3/8 = 38% ... in target band: YES`.

## Merge order (owner executes; nothing pushed)

1. `feat/t0-2-kb-retrieval-protocol`, `feat/t0-3-detector-cjk-refusal`, `feat/t0-4-fabrication-gate-honesty`, `docs/t0-5-calibration-policy`, `feat/t1-8-must-preserve-eval` — any order (disjoint file sets).
2. `feat/t0-1-user-state-boundary`.
3. `feat/t1-3-precedence-policy` (contains A).
4. `feat/t1-1-self-report-divergence` (contains H).
5. `feat/t1-2-voice-anchors-cleanroom` — contains H, NOT I; merge after I and resolve the trivial overlap in voice-onboard/comms-polish SKILL.md (both lanes append near the same sections).
6. `feat/t1-4-untrusted-content-contract` — REBASE onto post-1-5 main first (its one-line SKILL.md refs conflict trivially with A/H/I/J), re-run the suite, then merge LAST.

After each merge: `bash skills/ai-writing-suite/evals/run_all.sh` must print `ALL CHECKS PASSED` with the 3/8 = 38% line before the next merge.

## Mid-wave decisions (all recorded rulings)

- **B semantics (owner ruling):** freeze-time hand-computed smoke expectations are canonical; scoring stays union-primary/summary-tiebreak; only tie handling + a clarifying `aiws/kb/RETRIEVAL-SEMANTICS.md` changed. The keyword-strict reading was rejected.
- **B latent tie (orchestrator ruling, owner veto at merge):** the surfaced Case-1 tie `['clarity.md','revision.md']` is protocol-conformant (frozen INDEX tie clause); accepted + pinned with exact-set assertions; SMOKE-TEST.md narrative corrected — including a second correction (`39759c7`) after review disproved the "revision.md added later" timeline claim (both entered in `edd3404`; the tie was an overlooked token collision in the original hand computation).
- **C scope extension (owner ruling):** refusal-aware PASS-suite branch + `expect_refusal` on `overstep-04-selfqa-zh` only; calibration-8 untouched. Review confirmed the old behavior mislabeled CJK input "Too short"/score 0 — a false clean signal now fixed.
- **A LR-001 (orchestrator ruling):** archived verbatim to `docs/retired-learned-rules-archive.md` instead of silent loss; deslop-landscape task #31 keeps its fixture text.

## Non-blocking follow-ups (Wave-2 candidates)

1. B: `smoke_test.py` hardcodes the tie case by index (`if i == 1`) — replace with per-case expected-file markers parsed from SMOKE-TEST.md.
2. F: pin the untrusted-content contract's key phrases in its test (currently existence-only; `test_voice_contract.py` REQUIRED_HEADERS is the stronger pattern).
3. D: OR-grounding note — a verb-claim dodges detection if only its object coincidentally grounds; spec-conformant, revisit with real-draft corpus.
4. G: substring+token dual check can theoretically false-FAIL on reordered token-complete phrases; watch when fixtures grow.
5. J/D5: the wave-1 SPEC's own phrasing ("tagged with the single habit it proves") echoes jpcaparas's "Note what each line proves" — implementation is clean-room clean; the echo lives in the spec text. Record alongside the D5 license decision.
6. Plan-doc errata: SPEC-T0-5 overclaims what `test_calibration.py:19-27` pins (band constants actually pinned at :62-63).
7. Holdout note repeated in every run: 100% closed probes — add a harder verbatim probe.

## Process notes

- Two lanes BLOCKED correctly via escape hatches (B, C) instead of improvising — both resolved by explicit rulings, zero constraint violations.
- One reviewer (lane A) violated read-only rules with a modify-then-restore experiment (`git checkout --`); net effect zero (verified twice), rule tightened to an absolute ban + /tmp-copy alternative for all subsequent reviewers, who complied.
- Codex-side facts for the record: `codex exec resume` accepts only `-c` config overrides (not `-C/-s/-m`); handoff resume run_id = first task's file stem.

## Evidence trail

Plan: `docs/plan-systematic-improvement-2026-07-21.md` · implementation plan: `docs/implementation-plan-wave1-2026-07-21.md` · research review: `reviews/2026-07-21-codex-adversarial-research-review.md` · handoff results: `~/.handoff/tasks/0721-cx-*.result.md`, `0722-cx-*.result.md` · reviewer verdicts: session transcripts (summarized above).
