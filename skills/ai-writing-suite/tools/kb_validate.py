#!/usr/bin/env python3
"""Thin CLI entrypoint over `aiws.kb.validate` — the fork-KB pre-flight
validator a company runs AFTER dropping in its playbook and BEFORE first use.

All the check logic (structural contract + ingestion-specific checks +
retrieval smoke) lives in `aiws.kb.validate`; see that module's docstring for
the full contract. This file only wires up the CLI (architecture review
2026-07-13, item 5 — this tool used to `sys.path.insert` into `evals/` and
import test scaffolding directly: `kb_lint`, `smoke_test`, plus a private
`kb_lint._entry_files` reach and a `smoke_test.INDEX_PATH` mutation. All of
that is gone; the checks now live in the product package `aiws.kb` and this
tool imports only that).

`kb_lint` is kept as a local alias below purely for backward compatibility
with existing call sites (e.g. `kb_validate.kb_lint.check_index_sync(...)`)
— it now points at `aiws.kb.structural`, the product module, not at
`evals/kb_lint.py`.

Run:  python3 tools/kb_validate.py <knowledge-dir>
"""

import os
import sys

# tools/ -> suite root, so `import aiws` resolves to the sibling aiws/ package.
_HERE = os.path.dirname(os.path.abspath(__file__))
_SUITE_ROOT = os.path.normpath(os.path.join(_HERE, ".."))
if _SUITE_ROOT not in sys.path:
    sys.path.insert(0, _SUITE_ROOT)

from aiws.kb import structural as kb_lint  # noqa: E402  (back-compat alias)
from aiws.kb.validate import (  # noqa: E402
    NON_ENTRY_FILES, CHECKS, validate, check_summary_non_empty,
    check_no_todo_markers, check_entry_meta_non_empty,
    check_index_matches_entry_meta, check_retrieval_smoke,
    warn_generic_shadowing, main,
)

if __name__ == "__main__":
    sys.exit(main())
