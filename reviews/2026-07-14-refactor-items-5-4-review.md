# Review record — architecture items 5+4 (refactor/aiws-kb-module, refactor/judge-facade), 2026-07-14

## Chain per branch

**Item 5 (aiws/kb dependency reversal):**
- code-reviewer (isolated worktree): APPROVE. AST body-diff old→new = zero logic drift;
  dep graph clean (no tools→evals, no aiws→evals|tools); back-compat alias exercised by
  test_kb_ingest:202,219,232; before/after kb_validate CLI output byte-identical.
- Codex gpt-5.6-sol xhigh (attempt 2, sampled probes — attempt 1 timed out at 600s on
  exhaustive 11-file diff): REVISE. Sole CONCERN: thin wrappers dropped public names
  (kb_lint.HERE/re; smoke_test.HERE/STOPWORDS). Orchestrator arbitration: git grep = ZERO
  consumers → downgraded, but fixed anyway (shims promise drop-in compat). Fix dispatched.
- Codex-parallelism lesson CONFIRMED: parallel xhigh runs timed out twice (07-13 A+B, 07-14
  kb+judge); every solo run completed. Codex reviews now run serially.

**Item 4 (judge evaluate() facade):**
- code-reviewer: APPROVE. Facade sole external entry (grep-verified); spend gate before
  network (pinned by test); characterization tests independent (hand-wired originals vs
  facade output), mutation-probed non-tautological.
- Independent judge = oh-my-claudecode:critic subagent in fresh worktree (owner directive
  after the Codex lane timed out; adversarial refute-the-claims framing): APPROVED.
  Claims 1/2/3/5 CONFIRMED with file:line; claim 4 partially REFUTED — verify_evidence is
  provably SYMMETRIC in before/after (needle in nb or na), so the characterization test
  cannot detect an argument swap (harmless: symmetric = no behavior change, but the
  docstring overclaimed). CONCERNs: JudgeResult.warnings computed but consumed by zero
  runners (wire-or-drop); Optional type hints. Fixes dispatched.

## Fix batch (dispatched 2026-07-14)
- kb: re-export HERE/re (kb_lint wrapper) + HERE/STOPWORDS (smoke_test wrapper).
- judge: _report_evidence consumes result.warnings iff byte-identical (else drop field);
  raw/verdict → Optional; docstring symmetry correction.

VERIFIED_AGAINST: refactor/aiws-kb-module @ e40f02e · refactor/judge-facade @ 13b09e0
