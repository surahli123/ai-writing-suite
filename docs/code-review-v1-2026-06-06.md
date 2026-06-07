# Code Review — AI Writing Suite v1 (Opus, independent worktree pass)

Date: 2026-06-06
Reviewer: oh-my-claudecode:code-reviewer (Opus), isolated git worktree
Scope: `feat/ai-writing-suite-v1`, commits `d4ed904..d6616a4` (Layers 0-3)

## Verdict

**v1 is sound and ship-able. No BLOCKERs.** Must-fix before OSS release = two stale-doc
contradictions (M1, M2). Detector is logically correct + crash-proof on every adversarial
input. Eval calibration genuinely enforces the 30-40% band (real 38%; cannot pass vacuously).
Voice-profile contract aligns field-for-field. D5 (zero-dep), D6 (human-gated), D12 (real
smoke chain) all honored.

## Tests (run by reviewer)

| Command | Result | Exit |
|---|---|---|
| `python3 -m unittest discover -p 'test_*.py'` | 23 tests OK | 0 |
| `python3 smoke_test.py` | 2/2 PASS | 0 |
| `python3 -m fixtures.run_fixtures` | 8/8, miss 38%, "in target band: YES" | 0 |

stdlib-only confirmed (no package.json/requirements/pyproject) → D5 holds. `sync.sh` idempotent;
packaged SKILLs byte-identical to source → no drift.

## Adversarial detector inputs → all crash-proof, no nonsense scores

empty / whitespace / 1-word / emoji-only / fenced code / CJK / unicode-mix → UNSCORED (length
gate). huge 35k words → "Text too long" (MAX_WORDS=10000). AI control → 82 AI_ONLY. human
control → 0 HUMAN_ONLY. Zero crashes.

---

## MAJOR

**M1 — Stale "empty KB slot" claims contradict the seeded KB.**
`SKILL.md:62` ("the slot is present but empty in this build") + `skills/comms-qa/SKILL.md:11-13`
("KB slot exists but is empty"). Layer 2 actually seeded 5 entries + INDEX + SMOKE-TEST. Readers
conclude the KB doesn't work → undermines the D11/D12 product claim. Fix: update both to "ships a
generic 5-entry KB; full comms-qa retrieval is v2." Re-run `sync.sh`.

**M2 — NOTICE marks the detector "(v2)" but it ships in v1.**
`NOTICE.md:29` "detector foundation (v2)". The Python port (`evals/detector/`) is a v1
deliverable. Wrong scope tag on the one piece of executable ported logic = worst place to be
sloppy on attribution. Fix: drop "(v2)".

## MINOR

**m1 — Smoke Case 2 discriminates on a SINGLE token → near-vacuous.**
`smoke_test.py` + `SMOKE-TEST.md:84-96`. Query retrieves `audience.md` overlap (1,0) — only
"who" matches; lure words hit zero entries, `tone.md` scores 0. No competing signal → proves
little. Fix: add a query where both `tone.md` and `audience.md` score >0 so the tie-break is real.

**m2 — Empty/garbage query passes Case 1 by stable-order fallback (no overlap guard).**
`smoke_test.py retrieve()`. `""` returns `clarity.md` (overlap (0,0), first-table default) →
would vacuously satisfy Case 1. Fix: assert `best_score > 0`; treat zero-overlap as no match.

**m3 — Dead branch in `_classify`.** `detector.py:342` `elif score >= 40 and strong >= 1:` is
unreachable (line 340 already catches every `strong>=1`). Delete lines 342-343.

**m4 — Detector blind to CJK / non-space scripts.** `_count_words` (`\S+`) collapses Japanese/
Chinese to wordCount=1 → always "Too short", silently UNSCORED (reads as "clean"). Acceptable for
v1 (bilingual = v2) but fix: note the limitation in the docstring so UNSCORED isn't misread.

## NIT

- **n1** `evals/` excluded from packaged targets (CI-only) — document why in `packaging/README.md`.
- **n2** `_sentences` splits on `[.!?]+` → abbreviations over-split, mild burstiness skew. Low impact.
- **n3** `run_fixtures` reads `before_band_min/max` but `test_fixtures REQUIRED` omits them; a
  typo'd key would silently skip the assert. Consider asserting band presence per difficulty.

## Positive observations

- Calibration is real, not theater (3/8 subtle fixtures score literally 0; flip one → band breaks).
- Detector port faithful + defensively correct (dedup, log2 normalization, tiered thresholds,
  FN-biased classifier, length gates).
- Voice contract aligns field-for-field (identical 10 H2 names writer↔reader); degradation real.
- D6 self-improvement genuinely human-gated (read+propose autonomously; append needs approval;
  core never auto-edited). Router stays thin.
- Honest scaffolding (v2 stubs labeled; P31-P43 corruption disclosed; sync.sh single-source rule).
