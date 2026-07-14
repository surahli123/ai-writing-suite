"""Output-contract checker for comms-polish detect/review audit reports.

This package is an OUTPUT-CONTRACT check, not behavioral coverage: it verifies the
STRUCTURE of a report against the Audit Report Contract in comms-polish/SKILL.md
(sections present + ordered, each finding carries quote+tell-id+why+fix, tell ids
resolve against the live _shared/patterns/ registry). It never scores prose
quality or claim correctness — those are not honestly checkable by stdlib regex
(see reviews/2026-07-13-advisor-eval-method.md Q1-Q2). Ships a conforming and a
nonconforming artifact and a checker that discriminates them; the checker is
itself regression-tested (including doctored-artifact tests that prove it can fail).
"""
