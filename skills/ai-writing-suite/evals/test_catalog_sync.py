"""Catalog/detector sync test (engine-polish #3 drift guard).

The polish catalog `_shared/patterns/lexical-tells.md` ships a "replace-on-sight"
table that mirrors the detector's `TIER1` swap dict in `detector/patterns.py`.
Two copies of the same data drift silently — so this test fails CI if they
diverge. (v2: generate the table from patterns.py and delete this.)

It parses the actual markdown table into {word: swap} and asserts it EQUALS
TIER1 — so a dropped row, an extra row, OR a changed swap all turn the test red.
A naive substring scan ("is the word anywhere in the file?") would pass even with
a deleted row, because these words also appear in the doc's prose (e.g.
`intricate` is a substring of `intricacies`) — that false-pass is the exact bug
this version closes.

Stdlib-only, no network. Runs under `run_all.sh` via `unittest discover`.
"""

import os
import sys
import unittest

from detector.patterns import TIER1

# evals/ -> <skill-root>, so `import aiws` resolves to the sibling aiws/ package.
_SUITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SUITE_ROOT not in sys.path:
    sys.path.insert(0, _SUITE_ROOT)

# The catalog is parsed in ONE place — aiws.catalog. The replace-on-sight table
# parser that used to live here was folded into it (architecture review
# 2026-07-13, item 2); this test now imports it instead of duplicating the regex.
from aiws.catalog import parse_replace_table  # noqa: E402  (path set above)

CATALOG = os.path.join(_SUITE_ROOT, "_shared", "patterns", "lexical-tells.md")


class CatalogSync(unittest.TestCase):
    def test_catalog_exists(self):
        self.assertTrue(os.path.exists(CATALOG), f"catalog missing: {CATALOG}")

    def test_replace_table_matches_detector_tier1_exactly(self):
        with open(CATALOG, encoding="utf-8") as fh:
            table = parse_replace_table(fh.read())
        self.assertEqual(
            table, dict(TIER1),
            "lexical-tells.md replace-on-sight table drifted from "
            "detector/patterns.py TIER1 (missing/extra word or changed swap). "
            "Re-sync the table with the TIER1 dict.")


if __name__ == "__main__":
    unittest.main()
