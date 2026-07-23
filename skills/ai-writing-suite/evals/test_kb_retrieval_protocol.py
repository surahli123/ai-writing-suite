"""Regression tests for the published INDEX retrieval protocol."""

import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_SUITE_ROOT = os.path.normpath(os.path.join(_HERE, ".."))
if _SUITE_ROOT not in sys.path:
    sys.path.insert(0, _SUITE_ROOT)

from aiws.kb.retrieval import retrieve  # noqa: E402


class RetrievalProtocol(unittest.TestCase):
    def test_summary_heavy_entry_outscores_incidental_keyword_entry(self):
        entries = [
            {
                "file": "incidental-keyword.md",
                "summary": "",
                "keywords": {"alpha"},
                "summary_kw": set(),
            },
            {
                "file": "summary.md",
                "summary": "alpha beta",
                "keywords": set(),
                "summary_kw": {"alpha", "beta"},
            },
        ]

        self.assertEqual(retrieve("alpha beta", entries),
                         (["summary.md"], (2, 2)))

    def test_full_tie_returns_both_filenames(self):
        entries = [
            {
                "file": "first.md",
                "summary": "beta",
                "keywords": {"alpha"},
                "summary_kw": {"beta"},
            },
            {
                "file": "second.md",
                "summary": "beta",
                "keywords": {"alpha"},
                "summary_kw": {"beta"},
            },
        ]

        self.assertEqual(retrieve("alpha beta", entries),
                         (["first.md", "second.md"], (2, 1)))


if __name__ == "__main__":
    unittest.main()
