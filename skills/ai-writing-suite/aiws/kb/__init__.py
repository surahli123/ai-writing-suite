"""aiws.kb — the pluggable-knowledge-base product module.

Owns index loading/retrieval, entry-file enumeration, and structural
validation for a fork's `_shared/knowledge/` KB. Extracted from
`evals/kb_lint.py`, `evals/smoke_test.py`, and `tools/kb_validate.py` so that
`tools/kb_validate.py` and `tools/kb_ingest.py` no longer import evals/ test
scaffolding to do their job (architecture review 2026-07-13, item 5).

Submodules:
  entries    — entry-file enumeration + the default KB path.
  retrieval  — INDEX.md loading + the keyword/summary retrieval protocol.
  structural — the add-an-entry structural contract (INDEX<->dir sync,
               related-entries validity, bidirectionality, keywords).
  ingest     — export -> KB-entry shaping (the fork onboarding tool's logic).
  validate   — the full fork-KB pre-flight validator, composed from the above.
"""
