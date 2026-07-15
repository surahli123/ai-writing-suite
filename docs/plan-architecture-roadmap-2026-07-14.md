# Plan — Architecture Roadmap (Q1–Q6 unblocked), 2026-07-14
`Status: APPROVED 2026-07-14 (owner) — items 5+4 started in parallel per the sequence below`

Five refactors from `reviews/2026-07-13-architecture-improve-review.md` (verdict NEEDS-WORK), now unblocked by owner rulings Q1–Q6 (`docs/decisions-2026-07-13.md:9-14`). Baseline is main @ 087cbec: 7-step `run_all.sh` green, 341 tests, calibration 3/8 = 38%, packaging validator green (`docs/integration-notes-2026-07-13.md:142-145`). All eight feature/fix branches are already merged, so the "merge-hot" gate the review imposed on four of the five items has lifted — the work is now safe to start.

## Sequence and dependency rationale

Recommended order: **5 → 4 → 1 → 2 → 3**. Reasoning:

- **Item 5 first** (reverse `tools→evals`). It creates the `aiws/` package that does not yet exist (`ls aiws/` → absent). Items 2 and 3 both add modules *under* `aiws/`, so 5 establishes the package convention and `__init__.py` they rebase onto. Smallest blast radius, no shared hot files (kb lane added `tools/` + `test_kb_ingest.py` with zero overlap per `integration-notes:78-79`).
- **Item 4 second** (judge `evaluate()` facade). Fully independent of 5 — could run in parallel. Pure internal refactor behind a facade; characterization tests are the guard. Do it early so item 1's runner and a future live lane compose a trustworthy judge.
- **Item 1 third** (capability runner). Structural but mechanical; touches the orchestration spine (`run_all.sh`, 7 steps at `run_all.sh:21-40`). Independent of 2/3. Do the runner protocol + discovery test + compat wrapper, then cut over `run_all.sh`.
- **Item 2 fourth** (pattern registry). Depends on 5's `aiws/` convention for the `aiws/catalog.py` loader. Must reconcile with two *existing* parallel parsers: `test_catalog_sync.py` (syncs only the TIER1↔lexical table, `test_catalog_sync.py:22-28`) and the audit checker's own live-heading parser (`audit_report/check_report.py:41` `_CATALOG_HEADER`, `load_catalog_ids` at `:87`). Highest annotation cost. **Only item that touches SKILL.md prose** → coordinate with PR #25 (below).
- **Item 3 last** (`aiws/text.py` seam). Highest calibration risk: shared tokenization can shift detector bands (Q4 hard question d). Isolating it last means band recalibration is the only moving part when it lands. Q4's versioned-policy ruling (`decisions:12`) makes a band shift a deliberate, committed policy-version bump, not silent drift.

Items 4 and 5 are mutually independent and may run concurrently; 1 is independent of 2/3.

## Per-item detail

**5 — aiws/kb/ product module.** Goal: move `load_index/retrieve`, entry enumeration, structural validation into `aiws/kb/`; tools become thin entrypoints. Files: new `aiws/kb/`, `tools/kb_validate.py`, `tools/kb_ingest.py`, `evals/smoke_test.py`. Contract that must not break: run_all step 2 KB smoke (`run_all.sh:24-25`), `test_kb_ingest.py`, `test_kb_wiki.py`. Premise guard: today `kb_validate.py:44-48` does `sys.path.insert(0,_EVALS); import kb_lint, smoke_test`, calls private `kb_lint._entry_files` and mutates `smoke_test.INDEX_PATH` — the refactor must reverse this so evals import the product module, not vice-versa. Verify: `bash evals/run_all.sh` + `python3 scripts/validate_packaging.py`. Size: **S–M**.

**4 — judge.py behind evaluate().** Goal: one `evaluate(JudgeRequest)->JudgeResult` facade over the concerns `judge.py` already owns — transport `score` (`judge.py:176`), `parse_dimensions` (`:251`), `verify_evidence` (`:337`), `model_family` (`:362`), `majority_vote`/`aggregate` (`:409,445`). Files: `evals/fixtures/judge.py`, `run_fixtures.py`, `run_draft_cases.py`. Contract: `test_judge_protocol.py` + byte-identical verdicts through both runners; **do not split into shallow utils** (review depth rule, `reviews:76`). Premise guard: the (18,5) confusion-matrix cohorts at `test_fixtures.py:823` depend on stable judge output; the `AIWS_JUDGE_RUN=1` spend gate stays. Verify: `python3 -m unittest discover -p 'test_*.py'` + facade characterization tests. Size: **S–M**.

**1 — capability-runner discovery.** Goal: `evals/run.py` discovers capability descriptors; `run_all.sh` becomes a numberless wrapper. Files: new `evals/core/` + `evals/run.py`, `run_all.sh`. Contract: the 7 steps (`run_all.sh:21-40`) must all still execute; all 341 tests via `unittest discover`. Premise guard: step count is **7 and load-bearing** — the whole review is motivated by the 3-branch renumbering collision (`integration-notes:73-76`); discovery must catch every capability or a suite silently drops. Verify: `bash evals/run_all.sh` prints 7 discovered capabilities green. Size: **M**.

**2 — pattern markdown as registry.** Goal: uniform metadata table per `### <id> — <name>` entry with **Severity** (editorial harm) + **Enforcement** (mechanism) as separate fields per Q1 (`decisions:9`); one stdlib `aiws/catalog.py` loader; 00-index/rubric/coverage projections become checked-in, marker-bounded, CI-freshness-checked lockfiles per Q5 (`decisions:13`). Files: all 9 `_shared/patterns/*.md`, `evals/fixtures/rubric.md`, new `aiws/catalog.py`, `test_catalog_sync.py`, `audit_report/check_report.py`, and `comms-polish/SKILL.md:35` (de-enumerate tell names). Contract: `audit_report/test_report_contract.py:55` pins `len(CATALOG)==71`; `test_catalog_sync.py` pins the TIER1↔lexical table. Premise guard: **71 catalog ids (67+N1–N4)** — never renumber; `load_catalog_ids` must return 71 unchanged, and the new loader must not fork a fourth parser (fold `check_report`'s `_CATALOG_HEADER` and `test_catalog_sync` into it). Verify: `run_all.sh` step 7 + freshness check on generated projections. Size: **M** (annotation-dominated).

**3 — aiws/text.py seam.** Goal: `segment(text, language="auto")->TextDocument` (script class, support status, tokens, sentences, words); detector + voice grader + stylometry consume it. Files: new `aiws/text.py`, `evals/detector/detector.py` (replaces `_WORD_RE`/`_TOKEN_RE` at `detector.py:32-33`), `run_voice_extraction.py:101`, `_shared/stylometry.py`. Contract: detector bands feed calibration **3/8 = 38%** (`evals/fixtures/test_calibration.py:22` `miss_target(8)==3`) and the (18,5) cohorts with specificity 15/18 (`test_fixtures.py:904,921`). Premise guard: these three numbers are re-derived, never weakened — Q4 (`decisions:12`) requires a measurement-policy-version bump + band-recalibration commit *if* tokenization shifts a band; start with one whitespace impl + explicit unsupported-script result, **no premature adapter hierarchy** (`reviews:67`). Verify: `run_all.sh` step 3 asserts 38%; if bands move, the recalibration commit is the deliverable. Size: **M** (fixture-recalibration risk).

## Branch strategy

**Independent branches off main, one per item — not one train.** Land order 5 → 4 → 1 → 2 → 3; rebase each on the prior only where files touch (2 and 3 rebase onto 5 for `aiws/__init__.py`). Rationale: each item has a distinct blast radius and its own review evidence, matching the one-PR-per-lane discipline that worked for the eight merged lanes (`integration-notes:49`).

**PR #25 conflict check:** items 1, 3, 4, 5 touch **zero** SKILL.md/prose files → no overlap. **Item 2 is the sole collision** — it edits `comms-polish/SKILL.md:35`. Mitigation: land item 2 *after* the prose train merges.

## Risks (top 3)

1. **Item 3 band drift breaks the 38% invariant.** Mitigation: Q4 versioned-policy — treat any band change as a deliberate recalibration commit (policy version + re-derived 3/8, 15/18, (18,5)), gated on owner sign-off; never tune fixtures to hit the number.
2. **Item 2 grows a fourth catalog parser instead of retiring the three.** Mitigation: acceptance criterion is that `aiws/catalog.py` becomes the *sole* parser — `test_catalog_sync` and `check_report.load_catalog_ids` must import it, and `len==71` holds.
3. **Item 1 discovery silently drops a capability.** Mitigation: a discovery test asserting exactly the 7 known capability ids are found before cutover; the numbered wrapper stays until that test is green.

## Out of scope

No new features. No eval-semantics changes beyond what Q1 (two severity/enforcement fields), Q4 (versioned measurement policy), and Q5 (checked-in projections) explicitly require. No CJK/multilingual implementation (that is #14, downstream of item 3's seam). No `judge.py` provider-adapter or transport rework (`reviews:76`). No KB ingestion redesign — move functions unchanged (`reviews:85`). Q2/Q3/Q6 rulings inform items 1/2 but their consumers (live lane #8, multilingual #14) are not built here.

## Orchestrator notes (2026-07-14, appended at plan intake)

- Citations spot-checked against HEAD: kb_validate sys.path hack, the 71-id pin (`test_report_contract.py:55`), run_all step lines, judge.py symbol lines — all exact. Two corrected in this copy: detector regexes live at `detector.py:32-33` (planner cited 34-35); the calibration pin lives at `evals/fixtures/test_calibration.py:22` (planner cited `evals/test_calibration.py`).
- Item 2's prose collision is wider than PR #25: the stacked branches `feat/q10-multi-genre-voice` and `fix/a1-followups` (in flight today) also edit comms-polish/SKILL.md. Item 2 waits for the whole prose train to merge.
