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
import re
import unittest

from detector.patterns import TIER1

# This file lives at <skill-root>/evals/test_catalog_sync.py, so the catalog is
# two levels up: evals/ -> <skill-root> -> _shared/patterns/lexical-tells.md.
CATALOG = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "_shared", "patterns", "lexical-tells.md")

# A data row in the replace-on-sight table: "| word | swap |". The word is
# lowercase letters/hyphens (matches every TIER1 key); the header ("| AI word |"
# — uppercase) and separator ("| --- |") rows don't match, so they're skipped.
_ROW = re.compile(r"^\|\s*([a-z][a-z-]+)\s*\|\s*(.+?)\s*\|\s*$", re.M)


def _parse_replace_table(text):
    """Parse the 'replace-on-sight' markdown table into {word: swap}.

    Scoped to the table block (header through the next blank line) so unrelated
    pipe characters elsewhere in the doc can't leak in.
    """
    start = text.find("| AI word | Plain swap |")
    if start == -1:
        return {}
    block = text[start:]
    end = block.find("\n\n")  # table ends at the first blank line
    if end != -1:
        block = block[:end]
    return {m.group(1).strip(): m.group(2).strip() for m in _ROW.finditer(block)}


class CatalogSync(unittest.TestCase):
    def test_catalog_exists(self):
        self.assertTrue(os.path.exists(CATALOG), f"catalog missing: {CATALOG}")

    def test_replace_table_matches_detector_tier1_exactly(self):
        with open(CATALOG, encoding="utf-8") as fh:
            table = _parse_replace_table(fh.read())
        self.assertEqual(
            table, dict(TIER1),
            "lexical-tells.md replace-on-sight table drifted from "
            "detector/patterns.py TIER1 (missing/extra word or changed swap). "
            "Re-sync the table with the TIER1 dict.")


if __name__ == "__main__":
    unittest.main()
