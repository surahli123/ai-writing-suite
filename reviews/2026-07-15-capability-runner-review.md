# Review record — architecture item 1 (refactor/capability-runner), 2026-07-15

Chain: orchestrator verification (branch-tip run: order, invariant lines, 350 tests)
→ code-reviewer (isolated worktree): APPROVE-WITH-FIXES — MAJOR: alphabetical order
demoted unit_tests from position 1; MINOR: discovery guard cannot guard its own
module (missing-SPEC silently skipped); MINOR: topo machinery unexercised.
→ Codex gpt-5.6-sol xhigh solo fact-check: APPROVED — all 7 invocations quoted
byte-parity vs old run_all.sh steps; import failures loud; exit contract equivalent;
exact-set discovery assertion; stdout inherited not captured. Its sole CONCERN +
hard question #2 independently converged on the same two defects the code-reviewer
found (order drift; guard-guards-itself hole) — zero-overlap dual-channel agreement.

Round-2 fixes (20b8bef): depends_on:["unit_tests"] on the other six SPECs (restores
sanity-gate-first AND exercises the topo sort); discover_capabilities raises
RuntimeError on a SPEC-less module instead of continue (proof-gated: SPEC renamed →
loud traceback → restored); cycle guard kept, now riding a live traversal path.

Post-fix verification: order starts [1/7] unit tests; ALL CHECKS PASSED; calibration
3/8 = 38% byte-identical; catalog 72; pytest 350 passed; packaging OK; CI untouched
(ci.yml calls run_all.sh, wrapper preserves path + exit contract).

VERIFIED_AGAINST: refactor/capability-runner @ 20b8bef
