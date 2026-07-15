#!/usr/bin/env python3
"""Thin compatibility wrapper over `aiws.kb.structural` — lints the knowledge
base's add-an-entry contract (P2.5 KB wiki).

The four checks (INDEX<->dir sync, related-entries validity, bidirectionality,
keywords non-empty) moved to `aiws.kb.structural` (architecture review
2026-07-13, item 5), so the product module — not a test fixture — is the
source of truth `tools/kb_validate.py` reuses. This file stays in `evals/` as
the CLI entrypoint `python3 kb_lint.py [path]` and to keep
`evals/test_kb_wiki.py`'s `import kb_lint` working unchanged.

Run:  python3 kb_lint.py [path-to-knowledge-dir]   (exit 0 = all checks pass)
"""

import os
import re  # noqa: F401  (drop-in compat: this module used to define regexes with it)
import sys

# evals/ -> suite root, so `import aiws` resolves to the sibling aiws/ package.
_HERE = os.path.dirname(os.path.abspath(__file__))
HERE = _HERE  # drop-in compat: this module's own dir, as before the move
_SUITE_ROOT = os.path.normpath(os.path.join(_HERE, ".."))
if _SUITE_ROOT not in sys.path:
    sys.path.insert(0, _SUITE_ROOT)

from aiws.kb.structural import (  # noqa: E402  (path set above)
    DEFAULT_KB, NON_ENTRY_FILES, _entry_files,
    check_index_sync, check_related_entries, check_bidirectional,
    check_keywords, CHECKS, main,
)

if __name__ == "__main__":
    sys.exit(main())
