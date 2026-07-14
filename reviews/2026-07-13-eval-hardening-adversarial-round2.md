# Codex Adversarial Re-Review — eval-hardening (round 2)

Model: gpt-5.6-sol, reasoning effort xhigh, read-only sandbox
Date: 2026-07-13
VERIFIED_AGAINST: feat/eval-hardening-now @ da6b135

Re-reviews the remediation of the round-1 critique
(`reviews/2026-07-13-eval-hardening-adversarial.md`). Codex was told to verify, not
to trust the commit message, and probed the implementation itself.

---

## Prior BLOCKERs

1. CLOSED — judge evidence validation.

   - Paired parsing no longer treats contraction apostrophes as closers: [judge.py:95-121](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/judge.py:95).
   - Quotes are whitespace-normalized and checked against `before`/`after`: [judge.py:325-347](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/judge.py:325).
   - Accepted quotes and missing/malformed/fabricated warnings are surfaced: [run_fixtures.py:248-273](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_fixtures.py:248).
   - Probes confirmed contractions and smart quotes parse fully; straight/single mismatches and empty quotes are malformed; fabricated quotes return `not_verbatim`; multiline dimension records parse.

2. STILL-OPEN — constant always-FAIL judge still receives perfect “discrimination.”

   - The narrower fix works: driver `PASS` plus unrelated `FAIL` produced `0/1` right-reason and `1` wrong-reason.
   - However, failing every dimension still produced `4/4 caught for the right reason`. The code explicitly admits this limitation: [run_fixtures.py:174-190](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_fixtures.py:174).
   - The test suite locks that behavior in: [test_fixtures.py:689-698](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/test_fixtures.py:689).
   - Full-path probe returned `0/14` PASS-fixture agreement alongside `4/4` FAIL “discrimination,” with no combined confusion matrix or balanced accuracy. `main()` discards both counters after printing separate summaries: [run_fixtures.py:413-416](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_fixtures.py:413).

   Concrete fix: report TP/FN/TN/FP across both cohorts, plus sensitivity, specificity, and balanced accuracy. Keep driver agreement as a separate attribution metric. An all-FAIL judge should report sensitivity `1.0`, specificity `0.0`, balanced accuracy `0.5`—not perfect discrimination.

## NEW finding

CONCERN — evidence parsing is not strictly paired and does not support wrapped quotes.

[judge.py:82-83](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/judge.py:82) accepts any opener with any configured closer, so `"text”` is accepted as `ok`. A quote spanning a newline is classified `malformed`; the “multiline” test only covers separate one-line records: [test_judge_protocol.py:121-128](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/test_judge_protocol.py:121).

Concrete fix: map each opener to its matching closer and parse wrapped evidence with a bounded multiline state machine. This is non-blocking because verbatim validation still prevents silent fabricated evidence.

## Verification

- `bash run_all.sh`: 146 tests passed; all four stages passed.
- Calibration: `3/8 = 38%`.
- Judge remains advisory and opt-in; credentials with `AIWS_JUDGE_RUN=0` made zero network calls.
- CI remains key-free: [ci.yml:10-18](/Users/surahli/Documents/ai-writing-suite/.github/workflows/ci.yml:10).
- Changed eval runners import only stdlib plus local modules.
- No existing test was weakened, but the all-dimensions-FAIL test preserves the unresolved blocker.
- FP claim narrowing, empty-cohort guards, exit-code tests, rubric/denominator pins, statistic removal, and contested-prior note are present.
- `git diff --check origin/main...HEAD` passed.

VERDICT: REVISE
