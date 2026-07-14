"""Regression tests for the audit-report output-contract checker.

The load-bearing tests are the DOCTORED-ARTIFACT ones: they take the shipped
conforming report, mutate it one contract-violating way at a time, and assert the
checker rejects each mutation with the right reason. This is what stops the
rigged-checker failure mode (a checker that only ever separates the two shipped
files by memorizing them, per reviews/2026-07-13-advisor-eval-method.md Q1): a
mutation family the checker never saw must still be caught. Stdlib unittest only.
"""

import os
import tempfile
import unittest

from audit_report.check_report import (
    check_report,
    extract_fenced_report,
    load_catalog_ids,
)

HERE = os.path.dirname(os.path.abspath(__file__))
SUITE_ROOT = os.path.dirname(os.path.dirname(HERE))


def _read(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return fh.read()


CATALOG = load_catalog_ids()
CONFORMING = _read("conforming.md")
NONCONFORMING = _read("nonconforming.md")


def _joined(viols):
    return "\n".join(viols)


class CatalogRegistry(unittest.TestCase):
    def test_registry_non_vacuous(self):
        # If the registry were empty every tell-id would be "not in catalog"
        # and the not-in-catalog check would be meaningless. Anchor on real ids.
        self.assertGreaterEqual(len(CATALOG), 40)
        for tid in ("S1", "T1", "F1", "H2"):
            self.assertIn(tid, CATALOG)
        self.assertNotIn("Z9", CATALOG)

    def test_registry_exact_count_and_no_dupes(self):
        # Pins the CURRENT registry size (67, verified 2026-07-13) so a catalog
        # heading edit that silently drops or duplicates a tell id is caught
        # immediately instead of hiding behind a low floor. load_catalog_ids
        # itself raises on a duplicate id (dict keys can't collide silently),
        # so len(CATALOG) == len(set(CATALOG)) is true by construction — the
        # exact-count assert is what actually catches shrinkage/growth.
        self.assertEqual(len(CATALOG), 71)  # 67 + N1-N4 (narrative-shape, merged 2026-07-13)

    def test_malformed_heading_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "bad.md"), "w", encoding="utf-8") as fh:
                fh.write("# Category\n\n### S1Significance inflation\n- Tell: x\n")
            with self.assertRaises(ValueError) as ctx:
                load_catalog_ids(tmp)
            self.assertIn("does not match", str(ctx.exception))

    def test_duplicate_id_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "a.md"), "w", encoding="utf-8") as fh:
                fh.write("### S1 — Significance inflation\n- Tell: x\n")
            with open(os.path.join(tmp, "b.md"), "w", encoding="utf-8") as fh:
                fh.write("### S1 — Duplicate of same id\n- Tell: x\n")
            with self.assertRaises(ValueError) as ctx:
                load_catalog_ids(tmp)
            self.assertIn("duplicate tell id", str(ctx.exception))

    def test_00_index_template_line_is_not_a_violation(self):
        # 00-index.md's own "### <id> — <name>" template line documents the
        # schema; it must not be mistaken for a malformed catalog entry.
        ids = load_catalog_ids(os.path.join(SUITE_ROOT, "_shared", "patterns"))
        self.assertNotIn("<id>", ids)


class ShippedArtifacts(unittest.TestCase):
    def test_conforming_passes(self):
        ok, viols = check_report(CONFORMING, CATALOG)
        self.assertTrue(ok, f"conforming.md should pass, got: {_joined(viols)}")

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
        blob = _joined(viols)
        # planted #1: tiers have no italic definition line
        self.assertIn("italic one-clause tier definition", blob)
        # planted #2: a finding's quote is not actually quoted
        self.assertTrue(any("not a quoted snippet" in v for v in viols), blob)
        # planted #3: a tell id absent from the catalog
        self.assertTrue(any("'Z9'" in v and "not in" in v for v in viols), blob)


class WorkedExampleConforms(unittest.TestCase):
    """The canonical example (SKILL.md references/audit-report-format.md) must
    itself pass the checker — an example that fails its own contract teaches
    the wrong shape. Extracted via the shared extract_fenced_report() helper,
    the same routine a host would use to pull the fenced report out of prose."""

    def test_worked_example_extracts_and_conforms(self):
        path = os.path.join(SUITE_ROOT, "skills", "comms-polish",
                             "references", "audit-report-format.md")
        with open(path, encoding="utf-8") as fh:
            doc = fh.read()
        report = extract_fenced_report(doc)
        self.assertIsNotNone(report, "expected a fenced ``` block in the worked example")
        ok, viols = check_report(report, CATALOG)
        self.assertTrue(ok, f"worked example must conform to its own contract: "
                            f"{_joined(viols)}")


class ModeFirewall(unittest.TestCase):
    """Pin that rewrite/edit mode instructions live OUTSIDE the Audit Report
    Contract subsection — a regression guard against the contract's rules
    (findings, tiers, score placement) leaking into modes it doesn't govern."""

    def test_rewrite_and_edit_sections_precede_the_contract(self):
        path = os.path.join(SUITE_ROOT, "skills", "comms-polish", "SKILL.md")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        contract_idx = text.index("### Audit Report Contract")
        rewrite_idx = text.index("## Rewrite Workflow")
        edit_idx = text.index("## File Edits")
        self.assertLess(rewrite_idx, contract_idx,
                        "Rewrite Workflow must precede the Audit Report Contract")
        self.assertLess(edit_idx, contract_idx,
                        "File Edits must precede the Audit Report Contract")
        # The contract must also explicitly say it doesn't govern those modes.
        contract_body = text[contract_idx:]
        self.assertIn("`rewrite` and `edit`", contract_body)
        self.assertIn("are unchanged by it", contract_body)


class InputNormalization(unittest.TestCase):
    """Legitimate reports carrying typographic quotes or a leading BOM (both
    routine from comms-polish output / paste-from-Word) must still PASS —
    these are punctuation-style variants, not structural violations."""

    def test_smart_quotes_accepted(self):
        mutated = CONFORMING.replace(
            '"represents a truly transformative leap forward"',
            "“represents a truly transformative leap forward”")
        ok, viols = check_report(mutated, CATALOG)
        self.assertTrue(ok, f"typographic quotes should be accepted: {_joined(viols)}")

    def test_guillemet_quotes_accepted(self):
        mutated = CONFORMING.replace(
            '"represents a truly transformative leap forward"',
            "\xabrepresents a truly transformative leap forward\xbb")
        ok, viols = check_report(mutated, CATALOG)
        self.assertTrue(ok, f"guillemet quotes should be accepted: {_joined(viols)}")

    def test_leading_bom_accepted(self):
        mutated = "﻿" + CONFORMING
        ok, viols = check_report(mutated, CATALOG)
        self.assertTrue(ok, f"a leading BOM should not break the lead-line check: "
                            f"{_joined(viols)}")


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
        self._expect_reject(mutated, "fields must appear in order")

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
        self._expect_reject(mutated, "must come after")

    def test_out_of_range_score(self):
        mutated = CONFORMING.replace("**AI-tell score:** 58/100",
                                     "**AI-tell score:** 580/100")
        self._expect_reject(mutated, "outside 0-100")

    # --- Codex-mutation-proven holes (this round's fixes) -------------------

    def test_tell_before_quote_is_rejected(self):
        # FINDING 1(a): swapping field order inside one finding must fail —
        # the ordered state machine, not independent per-field search.
        mutated = CONFORMING.replace(
            '- **Quote:** "represents a truly transformative leap forward for the team"\n'
            '  **Tell:** S1 — Significance inflation\n',
            '- **Tell:** S1 — Significance inflation\n'
            '  **Quote:** "represents a truly transformative leap forward for the team"\n')
        self._expect_reject(mutated, "fields must appear in order")

    def test_descriptive_unquoted_fix_is_rejected(self):
        # FINDING 1(b): a Fix that describes the edit instead of showing it
        # (no quotes, no fence) must fail.
        mutated = CONFORMING.replace(
            '**Fix:** "cuts the weekly report from three tools down to one screen"',
            "**Fix:** cut the report down to one screen")
        self._expect_reject(mutated, "must show the replacement")

    def test_none_mixed_with_real_finding_is_rejected(self):
        # FINDING 1(c): '- None.' alongside an actual finding in the same tier
        # must fail, not short-circuit-pass via the early 'None' return.
        mutated = CONFORMING.replace(
            '- **Quote:** "We built it — from the ground up — to empower everyone."\n'
            '  **Tell:** F1 — Em / en dashes\n'
            '  **Why:** a parenthetical em-dash aside in the AI-favored cadence; '
            'the interruption adds nothing.\n'
            '  **Fix:** "We built it for the whole team."\n',
            '- **Quote:** "We built it — from the ground up — to empower everyone."\n'
            '  **Tell:** F1 — Em / en dashes\n'
            '  **Why:** a parenthetical em-dash aside in the AI-favored cadence; '
            'the interruption adds nothing.\n'
            '  **Fix:** "We built it for the whole team."\n'
            '- None.\n')
        self._expect_reject(mutated, "mixed with")

    def test_commentary_after_score_is_rejected(self):
        # FINDING 1(d): trailing prose after the "final" score line must fail —
        # score checked as "final non-blank line", not merely "occurs after
        # the positive section".
        mutated = CONFORMING + "\nThanks for reading, let me know if you have questions!\n"
        self._expect_reject(mutated, "final non-blank line")


if __name__ == "__main__":
    unittest.main()
