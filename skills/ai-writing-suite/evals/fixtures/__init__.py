"""LLM-judge before/after fixtures + the harness that runs them.

Two halves (see rubric.md for WHY both):
  - DETERMINISTIC: run the mechanical detector on every before/after, assert the
    scores land in the expected bands, and report the naive-baseline miss rate
    (the calibration check). Needs no model — runs in CI.
  - LLM-JUDGE: score each `after` against rubric.md with a model. Runs only when
    a model is wired in; otherwise the harness clearly marks those checks
    SKIPPED rather than passing them silently.
"""
