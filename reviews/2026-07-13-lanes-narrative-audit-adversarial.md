# Codex Adversarial Review — narrative-shape (C) + audit-report (D) lanes

Model: gpt-5.6-sol xhigh, read-only. Date: 2026-07-13.
VERIFIED_AGAINST: feat/narrative-shape-category @ 6141dd3; feat/audit-report-contract @ 5ea555c
VERDICT: BLOCK | BLOCK

Capture caveat: output piped through tail -c 6000 — the opening of branch C's findings
was truncated at capture time (a fragment referencing FAIL-labeling survives). The
surviving text covers the load-bearing findings; fixes will be independently re-verified.

---

 label them FAIL.

- `fixtures/fixtures_fail.json:5-13` — the new exemplar is incompatible with PR #15’s enforced schema. It lacks `rubric_focus`, so `fail_dimension: narrative_shape_ok` is not actually presented to the judge. `feat/eval-hardening-now:run_fixtures.py:34-35,129-143` and `test_fixtures.py:580-599` will reject it. `git merge-tree` also confirms an add/add conflict on this file.

  Concrete fix: merge into PR #15’s file shape, add at least `"rubric_focus": ["narrative_shape_ok", "meaning_preserved", "no_fabrication"]`, preserve its existing fixtures, and use its validated runner path.

### CONCERN

- `skills/comms-draft/SKILL.md:76-98` — Step 1 says to plan from the KB and consult `narrative-shape.md`, but Step 2 is where the KB, preset, and catalog are first loaded. The plan is required before its inputs exist. Shape also becomes an implicit sixth acceptance dimension, while Step 6 still checks only the original five.

  Concrete fix: load inputs before planning, add `shape` explicitly to the acceptance criteria, and verify it in Step 6.

- `run_fixtures.py:210-230` — the green suite proves detector bands only. It never loads `fixtures_fail.json`; the judge runs only with `--judge`, remains advisory, and was not invoked by `run_all.sh`.

  Concrete fix: after schema reconciliation, run the FAIL fixture’s deterministic validation in CI and add a key-free prompt-contract test.

### SUGGESTION

- `rubric.md:131-184` and `run_fixtures.py:120-126` — this part is correct today: the narrative block and validity condition are inside the first extracted fence. Add a regression test asserting the extracted template contains both `NARRATIVE-SHAPE CHECK` and `VALIDITY CONDITION`.

- `run_fixtures.py:71-96` — calibration logic is correct: all four new fixtures have `detector_blind: true`, so the denominator remains eight. Fresh result was exactly `3/8 = 38%`.

Hard questions:

1. What evidence available to the judge proves replica lag, balance corruption, and refund growth are “REAL” rather than fabricated, when it receives only `before`, `after`, and author-written `subtle_tell`?
2. If N3 simultaneously triggers rule-of-three and uniform-rhythm tells, what does a PASS establish specifically about `narrative_shape_ok`?
3. Why is document shape planned before the workflow loads the KB and catalog it must plan from?

Per-branch verdict: **BLOCK — request changes.**

## Branch D — `feat/audit-report-contract` (`5ea555c`)

### BLOCKER

- `evals/audit_report/check_report.py:90-120,169-176` contradicts the contract in `comms-polish/SKILL.md:274-280,287-290`. Executed mutations proved the checker incorrectly PASSes:

  - `Tell` before `Quote`;
  - an unquoted/descriptive `Fix`;
  - `- None.` mixed with actual findings;
  - commentary after the supposedly final score.

  The parser searches for fields independently instead of enforcing their order, returns early whenever `- None.` appears, and merely checks that the score occurs after the positive section.

  Concrete fix: parse each finding with an ordered state machine; require exactly Quote → Tell → Why → Fix; forbid mixing `None` with findings; require a quoted Fix; require the score to be the final nonblank line. Add doctored tests for each case.

- `references/audit-report-format.md:1-24` — the worked example itself FAILs the checker because the first nonblank line is its documentation heading, not `**Biggest problem:**`. Only the embedded report might conform; no test extracts or verifies it.

  Concrete fix: make the canonical example a report-only fixture, or fence the report and add a shared extraction helper used by both documentation tests and the checker.

### CONCERN

- `check_report.py:34-38,102-106` is stricter than the flexibility promise in `SKILL.md:250-253`. Fresh variation results:

  - CRLF: PASS
  - extra blank line: PASS
  - multiline quote: PASS
  - smart quotes: FAIL
  - Markdown-equivalent `__Quote:__`/`__Tell:__`: FAIL

  Concrete fix: normalize Markdown bold variants and accept paired ASCII or smart quote delimiters—or explicitly declare literal byte-level syntax and remove the “not a straitjacket” promise.

- `check_report.py:34,50-58` — catalog loading scans pattern files and silently accepts only headings matching `### letters+digits — name`. IDs are collapsed into a set, so malformed headings and duplicate IDs disappear silently. `test_report_contract.py:33-40` only checks `>=40` IDs plus four anchors; losing several other IDs stays green.

  Concrete fix: return an ID-to-source mapping, raise on duplicate IDs or any pattern-like H3 that fails schema, and test the full registry integrity rather than a low floor.

- `evals/run_all.sh:17-28` — merge-coordination hazard confirmed. This branch hardcodes four steps, while `feat/eval-hardening-now` defines a different step 4 and `feat/behavioral-evals-draft-voice` hardcodes six steps. Manual conflict resolution can silently drop a check or leave incorrect numbering.

  Concrete fix: reconcile runner additions in one integration commit, or define commands in an array and derive the total automatically.

### SUGGESTION

- `comms-polish/SKILL.md:242-257` — the mode firewall is clean: only detect/review behavior is redirected; rewrite/edit contracts remain explicitly unchanged. Preserve this boundary with a small test asserting rewrite/edit output instructions remain outside the audit contract.

Hard questions:

1. Is conformance based on rendered Markdown semantics or exact marker bytes? If semantic, why do smart quotes and `__...__` fail?
2. Why does the checker claim ordered four-part findings and a closing score while accepting reordered fields and trailing content?
3. What prevents a catalog formatting edit or duplicate ID from silently shrinking/corrupting the 67-ID registry?
4. Why is the advertised worked example not itself checker-conforming?

Per-branch verdict: **BLOCK — request changes.**

VERDICT: BLOCK | BLOCK
