# Codex Adversarial Re-Review — eval-hardening (round 3, verification pass)

Model: gpt-5.6-sol, reasoning effort xhigh, read-only sandbox
Date: 2026-07-13
VERIFIED_AGAINST: feat/eval-hardening-now @ 3546b87

Round 2 (`...-round2.md`) closed BLOCKER 1 and left BLOCKER 2 open: judge
discrimination was measured from the negative cohort alone, so a constant
always-FAIL judge scored perfectly. Commit 3546b87 replaced that with a combined
confusion matrix. Codex was asked to verify it independently, not to trust the
commit message.

## Capture caveat (read first)

The reviewer's structured output was piped through `tail -c 4500`, which truncated
the run before its final `VERDICT:` line. **This file therefore does NOT contain a
verbatim APPROVED verdict token** — it contains Codex's own summary of its probe
results, quoted below, plus the orchestrator's independent probes that reproduce the
same numbers. Treat the closure claim as supported by two agreeing probe runs, not
by a quoted verdict line.

## Codex's summary (verbatim)

> The judge blocker is independently closed: perfect `1.00/1.00/1.00`; always-FAIL
> `1.00/0.00/0.50`; always-PASS `0.00/1.00/0.50`; mixed `0.50/0.79/0.64`, all with
> exit `0`. Two unparseable reps were excluded (`TP=3,TN=13,skipped=2`),
> all-unparseable alone exited `1`, and the full 157-test suite passed. Quote pairing
> is fixed, but newline-wrapped evidence still returns `malformed`, so that half of
> the prior concern remains.

## Status

- **BLOCKER (round 2) — CLOSED.** Sensitivity/specificity/balanced accuracy are
  computed across both cohorts. Constant classifiers now report balanced accuracy
  0.5 (chance) instead of a perfect score. Skipped/unparseable reps are excluded
  from the matrix rather than folded into a cell. The matrix is advisory: it never
  drives the exit code; `live_error` (configured but 0/N scored) remains the only
  judge condition that does.
- **CONCERN (round 2), quote pairing — CLOSED.** Each opener is matched to its own
  closer; a straight-open + smart-close quote is now `malformed` rather than
  silently accepted.
- **CONCERN (round 2), newline-wrapped quotes — DELIBERATE, NOT FIXED.** A quote
  spanning a newline is classified `malformed` by design. A bounded multiline state
  machine was judged over-engineering for an advisory path that never gates CI;
  instead the rubric's judge-prompt template now states that each dimension verdict
  must be one line and its EVIDENCE quote must not span lines, and a test pins that
  instruction. Verbatim validation independently prevents silently accepted
  fabricated evidence, which was the actual risk. Revisit if a real judge model is
  observed wrapping quotes in practice.

## Independent reproduction (orchestrator, same HEAD)

    perfect judge          sens=1.0  spec=1.0  bal=1.0
    constant ALWAYS-FAIL   sens=1.0  spec=0.0  bal=0.5
    constant ALWAYS-PASS   sens=0.0  spec=1.0  bal=0.5

    straight-open + smart-close quote -> evidence_status: malformed
    properly paired smart quotes      -> evidence_status: ok

    run_all.sh: ALL CHECKS PASSED; calibration 3/8 = 38%; 157 tests OK
