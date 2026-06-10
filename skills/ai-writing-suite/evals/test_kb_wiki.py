"""KB wiki-contract test (P2.5 guard).

WHY this exists: kb_lint.py enforces the add-an-entry contract a company fork
must keep valid, but a lint tool only helps if it is wired into CI. This test
runs each kb_lint check against the SHIPPED KB so a regression — a deleted
back-link, an INDEX row that drifts from the files, an entry that loses its
`## Related entries` footer — turns red under `run_all.sh`, not at an agent's
runtime on a real host. It is the same pattern test_skill_manifests.py uses for
the frontmatter contract: import the checker, assert it passes the real tree.

Stdlib-only (unittest, no deps). Collected automatically by
`python3 -m unittest discover -p 'test_*.py'` in run_all.sh.
"""

import unittest

import kb_lint  # same evals/ dir; discover runs with that dir on sys.path


class KBWikiContract(unittest.TestCase):
    def test_index_directory_sync(self):
        ok, problems = kb_lint.check_index_sync(kb_lint.DEFAULT_KB)
        self.assertTrue(ok, f"INDEX<->dir sync failed:\n" + "\n".join(problems))

    def test_related_entries_valid(self):
        ok, problems = kb_lint.check_related_entries(kb_lint.DEFAULT_KB)
        self.assertTrue(ok, "Related-entries validity failed:\n"
                        + "\n".join(problems))

    def test_links_bidirectional(self):
        ok, problems = kb_lint.check_bidirectional(kb_lint.DEFAULT_KB)
        self.assertTrue(ok, "Bidirectionality failed:\n" + "\n".join(problems))

    def test_keywords_non_empty(self):
        ok, problems = kb_lint.check_keywords(kb_lint.DEFAULT_KB)
        self.assertTrue(ok, "Keywords non-empty failed:\n" + "\n".join(problems))

    def test_non_vacuous_entry_floor(self):
        # WHY: every check above passes trivially over an empty KB (no files =
        # no problems). Assert the shipped KB actually has entries so a missing
        # or mis-pathed KB fails loudly instead of green-by-vacuity. The seed
        # ships 5 entries; this floor matches that.
        n_entries = len(kb_lint._entry_files(kb_lint.DEFAULT_KB))
        self.assertGreaterEqual(
            n_entries, 5,
            f"expected >=5 KB entries checked, found {n_entries} "
            f"(KB path: {kb_lint.DEFAULT_KB})")


if __name__ == "__main__":
    unittest.main()
