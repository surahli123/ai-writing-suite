"""Regression tests for the audit-report output-contract checker.

The load-bearing tests are the DOCTORED-ARTIFACT ones: they take the shipped
conforming report, mutate it one contract-violating way at a time, and assert the
checker rejects each mutation with the right reason. This is what stops the
rigged-checker failure mode (a checker that only ever separates the two shipped
files by memorizing them, per reviews/2026-07-13-advisor-eval-method.md Q1): a
mutation family the checker never saw must still be caught. Stdlib unittest only.
"""

import os
import unittest

from audit_report.check_report import check_report, load_catalog_ids

HERE = os.path.dirname(os.path.abspath(__file__))


def _read(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return fh.read()


CATALOG = load_catalog_ids()
CONFORMING = _read("conforming.md")
NONCONFORMING = _read("nonconforming.md")


def _joined(ok, viols):
    return "\n".join(viols)


class CatalogRegistry(unittest.TestCase):
    def test_registry_non_vacuous(self):
        # If the registry were empty every tell-id would be "not in catalog" and
        # the not-in-catalog check would be meaningless. Anchor on real ids.
        self.assertGreaterEqual(len(CATALOG), 40)
        for tid in ("S1", "T1", "F1", "H2"):
            self.assertIn(tid, CATALOG)
        self.assertNotIn("Z9", CATALOG)


class ShippedArtifacts(unittest.TestCase):
    def test_conforming_passes(self):
        ok, viols = check_report(CONFORMING, CATALOG)
        self.assertTrue(ok, f"conforming.md should pass, got: {_joined(ok, viols)}")

    def test_conforming_is_non_vacuous(self):
        # Passing means something only if the artifact actually carries findings
        # with quotes + tell-ids + fixes. Guard against a checker that would pass
        # an empty shell.
        self.assertIn("**Quote:**", CONFORMING)
        self.assertIn("**Tell:** S1", CONFORMING)
        self.assertIn("**Fix:**", CONFORMING)

    def test_nonconforming_fails_with_planted_violations(self):
        ok, viols = check_report(NONCONFORMING, CATALOG)
        self.assertFalse(ok)
        blob = _joined(ok, viols)
        # planted #1: tiers have no italic definition line
        self.assertIn("italic one-clause tier definition", blob)
        # planted #2: a finding's quote is not actually quoted
        self.assertTrue(any("not a quoted snippet" in v for v in viols), blob)
        # planted #3: a tell id absent from the catalog
        self.assertTrue(any("'Z9'" in v and "not in" in v for v in viols), blob)


class DoctoredArtifacts(unittest.TestCase):
    """Mutate the conforming report one way at a time; each must be rejected."""

    def _expect_reject(self, mutated, needle):
        ok, viols = check_report(mutated, CATALOG)
        self.assertFalse(ok, f"mutation should be rejected: {needle}")
        self.assertTrue(any(needle in v for v in viols),
                        f"expected a violation containing {needle!r}, got: {viols}")

    def test_drop_lead_line(self):
        mutated = CONFORMING.split("\n", 1)[1]  # remove the biggest-problem line
        self._expect_reject(mutated, "lead")

    def test_numeric_only_lead(self):
        mutated = CONFORMING.replace(
            CONFORMING.splitlines()[0], "**Biggest problem:** 58/100")
        self._expect_reject(mutated, "no plain-language content")

    def test_drop_a_tier_definition(self):
        mutated = CONFORMING.replace(
            "## Critical\n*Tells that make the whole piece read as machine-written "
            "at a glance, or that distort meaning or trust.*\n",
            "## Critical\n")
        self._expect_reject(mutated, "italic one-clause tier definition")

    def test_strip_quote_marks_from_a_finding(self):
        mutated = CONFORMING.replace(
            '**Quote:** "represents a truly transformative leap forward for the team"',
            "**Quote:** represents a truly transformative leap forward for the team")
        self._expect_reject(mutated, "not a quoted snippet")

    def test_bogus_tell_id(self):
        mutated = CONFORMING.replace("S1 — Significance inflation",
                                     "Z9 — Not a real tell")
        self._expect_reject(mutated, "not in _shared/patterns/ catalog")

    def test_drop_a_fix_line(self):
        mutated = CONFORMING.replace(
            '  **Fix:** "cuts the weekly report from three tools down to one screen"\n',
            "")
        self._expect_reject(mutated, "missing **Fix:**")

    def test_drop_reads_well_section(self):
        idx = CONFORMING.index("## What already reads well")
        mutated = CONFORMING[:idx] + "**AI-tell score:** 58/100\n"
        self._expect_reject(mutated, "What already reads well")

    def test_reordered_tiers(self):
        mutated = CONFORMING.replace("## Critical", "## TMP").replace(
            "## Minor", "## Critical").replace("## TMP", "## Minor")
        self._expect_reject(mutated, "order")

    def test_score_before_reads_well_section(self):
        # Move the score line above the 'reads well' section -> misplacement.
        without = CONFORMING.replace("\n**AI-tell score:** 58/100\n", "\n")
        mutated = without.replace(
            "## What already reads well",
            "**AI-tell score:** 58/100\n\n## What already reads well")
        self._expect_reject(mutated, "closing line")

    def test_out_of_range_score(self):
        mutated = CONFORMING.replace("**AI-tell score:** 58/100",
                                     "**AI-tell score:** 580/100")
        self._expect_reject(mutated, "outside 0-100")


if __name__ == "__main__":
    unittest.main()
