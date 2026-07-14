"""KB entry-file enumeration + the default KB path.

Moved unchanged from `evals/kb_lint.py` (architecture review 2026-07-13, item
5), with one rename: `_entry_files` -> `entry_files` (public — the private
name was a defect: `tools/kb_validate.py` reached into it across the
tools->evals boundary as `kb_lint._entry_files`).
"""

import os

# aiws/kb/ -> aiws/ -> <suite-root> -> _shared/knowledge. Resolve relative to
# THIS file so the default works from any cwd (same convention the original
# kb_lint.py / smoke_test.py / run_all.sh used).
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_KB = os.path.normpath(os.path.join(HERE, "..", "..", "_shared", "knowledge"))

# Files in the knowledge dir that are NOT retrieval entries: they are
# infrastructure (the index, the human README, the smoke-test fixture) and must
# be excluded from the "every *.md is an entry" accounting on both sides.
NON_ENTRY_FILES = {"INDEX.md", "README.md", "SMOKE-TEST.md"}


def entry_files(kb):
    """Return the set of *.md filenames in the KB dir that ARE entries.

    Everything except the three infrastructure files above counts as an entry,
    so a fork that drops in `pricing.md` is held to the same contract without
    editing this module."""
    return {
        f for f in os.listdir(kb)
        if f.endswith(".md") and f not in NON_ENTRY_FILES
    }
