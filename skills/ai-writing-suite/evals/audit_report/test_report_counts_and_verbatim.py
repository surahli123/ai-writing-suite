"""Step 9 D+E: quote grammar, ×N counts, verbatim quotes, Fix fidelity, and
honest strengths (audit-report-contract.md §2 "Instances and counts" and §3).

Each rule has a passing control and a mutant that must be rejected, so a rule
that silently stops firing (or starts over-firing) fails here. Plan:
docs/plan-step9-and-comms-shape-2026-11-02.md §D, §E.
"""

import os
import unittest

from audit_report.check_report import (
    _fix_numbers_not_in_draft,
    _numbers,
    check_report,
    extract_fenced_report,
    load_catalog_ids,
)

HERE = os.path.dirname(os.path.abspath(__file__))
SUITE_ROOT = os.path.dirname(os.path.dirname(HERE))
CATALOG = load_catalog_ids()


def _read(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as fh:
        return fh.read()


CONFORMING = _read(HERE, "conforming.md")
DRAFT = _read(HERE, "draft.md")

DRAFT2 = ("Moreover, the rollout went well. Moreover, the pilot users stayed. "
          "Furthermore, churn fell 3% in week two.")


def report(quote_block, why, fix='"The rollout went well."',
           strengths="- Nothing here reads well yet: every sentence carries a flagged pattern."):
    return (
        "**Biggest problem:** stacked connectives make every sentence sound like a transition.\n\n"
        "## Critical\n*Tells that make the whole piece read as machine-written at a glance.*\n\n"
        f"- **Quote:**{quote_block}\n"
        "  **Tell:** H7 — Signposting / announcements\n"
        f"  **Why:** {why}\n"
        f"  **Fix:** {fix}\n\n"
        "## Moderate\n*Clear tells a careful reader notices.*\n\n- None.\n\n"
        "## Minor\n*Cosmetic or low-frequency tells.*\n\n- None.\n\n"
        f"## What already reads well\n{strengths}\n"
    )


TWO = ('\n  - "Moreover, the rollout went well"'
       '\n  - "Moreover, the pilot users stayed"')


class CanonicalExamplesAgainstTheirDraft(unittest.TestCase):
    def test_conforming_passes_with_draft(self):
        ok, viols = check_report(CONFORMING, CATALOG, draft=DRAFT)
        self.assertTrue(ok, viols)

    def test_worked_example_passes_with_draft(self):
        doc = _read(SUITE_ROOT, "skills", "comms-polish", "references",
                    "audit-report-format.md")
        ok, viols = check_report(extract_fenced_report(doc), CATALOG, draft=DRAFT)
        self.assertTrue(ok, viols)

    def test_examples_no_longer_invent_facts(self):
        for text in (CONFORMING, _read(SUITE_ROOT, "skills", "comms-polish",
                                       "references", "audit-report-format.md")):
            for invented in ("three tools", "three metrics", "under a second"):
                self.assertNotIn(invented, text)
            self.assertNotIn("the draft is AI throughout", text)


class QuoteGrammarAndCounts(unittest.TestCase):
    def ok(self, text, draft=DRAFT2):
        ok, viols = check_report(text, CATALOG, draft=draft)
        self.assertTrue(ok, viols)

    def rejects(self, text, needle, draft=DRAFT2):
        ok, viols = check_report(text, CATALOG, draft=draft)
        self.assertFalse(ok, f"expected rejection: {needle}")
        self.assertTrue(any(needle in v for v in viols), viols)

    def test_multi_instance_with_count_passes(self):
        self.ok(report(TWO, "×2 connectives open back-to-back sentences."))

    def test_count_must_match_instances(self):
        self.rejects(report(TWO, "×3 connectives open back-to-back sentences."),
                     "×3 claimed but 2 instance(s) quoted")

    def test_sub_bullets_need_a_leading_count(self):
        self.rejects(report(TWO, "connectives open back-to-back sentences."),
                     "needs ×N (N ≥ 2)")

    def test_count_elsewhere_in_why_is_ignored(self):
        self.ok(report(' "Moreover, the rollout went well"',
                       "it promises a x10 gain in flow; the connective adds nothing."))

    def test_count_with_set_aside_passes(self):
        self.ok(report(TWO, "×2 (+1 set aside: 'Furthermore' carries a real contrast) "
                            "connectives open back-to-back sentences."))

    def test_trailing_location_is_allowed(self):
        self.ok(report(' "Moreover, the rollout went well" (¶1)',
                       "a connective opens the update."))

    def test_location_with_quote_marks_is_rejected(self):
        # The location may contain no quote marks (contract §2).
        self.rejects(report(' "Moreover, the rollout went well" (see "intro")',
                            "a connective opens the update."),
                     "is not a quoted snippet")

    def test_hallucinated_quote_is_rejected(self):
        self.rejects(report(' "Moreover, the launch went smoothly"',
                            "a connective opens the update."),
                     "not found verbatim")

    def test_overlapping_instances_are_rejected(self):
        draft = "Moreover, the dashboard is fast."
        block = '\n  - "Moreover"\n  - "Moreover,"'
        self.rejects(report(block, "×2 connectives.", fix='"The dashboard is fast."'),
                     "overlaps another instance", draft=draft)

    def test_repeated_text_in_two_places_may_be_quoted_twice(self):
        draft = "Moreover, it shipped. Later: Moreover, it shipped."
        block = '\n  - "Moreover, it shipped"\n  - "Moreover, it shipped"'
        self.ok(report(block, "×2 connectives.", fix='"It shipped."'), draft=draft)

    def test_without_a_draft_grammar_still_applies(self):
        ok, viols = check_report(report(TWO, "×3 connectives."), CATALOG)
        self.assertFalse(ok)
        ok, _ = check_report(report(' "anything at all"', "a connective."), CATALOG)
        self.assertTrue(ok)  # verbatim needs the draft


class FixFidelity(unittest.TestCase):
    def rejects(self, fix, needle):
        ok, viols = check_report(report(' "Furthermore, churn fell 3% in week two"',
                                        "a connective opens the result.", fix=fix),
                                 CATALOG, draft=DRAFT2)
        self.assertFalse(ok)
        self.assertTrue(any(needle in v for v in viols), viols)

    def passes(self, fix):
        ok, viols = check_report(report(' "Furthermore, churn fell 3% in week two"',
                                        "a connective opens the result.", fix=fix),
                                 CATALOG, draft=DRAFT2)
        self.assertTrue(ok, viols)

    def test_invented_number_is_rejected(self):
        self.rejects('"Churn fell 5% in week two."', "introduces the number 5%")

    def test_number_word_equivalence_passes(self):
        self.passes('"Churn fell three percent in week two."')

    def test_number_inside_needs_is_not_a_claim(self):
        self.passes('"Churn fell 3%. [NEEDS: churn for the 2 other cohorts]"')

    def test_plain_one_is_not_a_number(self):
        self.passes('"Pick one."')

    def test_draft_side_parses_one_half_and_compositions(self):
        draft = _numbers("one dashboard, half the team, three thousand rows, one in five")
        for fix, ok in (('"1 dashboard"', True), ('"50% of the team"', True),
                        ('"3,000 rows"', True), ('"3 thousand rows"', True),
                        ('"1 in 5"', True), ('"4,000 rows"', False)):
            self.assertEqual(_fix_numbers_not_in_draft(fix, draft) == [], ok, fix)


class HonestStrengths(unittest.TestCase):
    def test_unquoted_praise_is_rejected(self):
        text = report(' "Moreover, the rollout went well"', "a connective.",
                      strengths="- The tone is clear and professional.")
        ok, viols = check_report(text, CATALOG)
        self.assertFalse(ok)
        self.assertTrue(any("must quote the draft" in v for v in viols), viols)

    def test_nothing_mixed_with_quoted_strength_is_rejected(self):
        text = report(' "Moreover, the rollout went well"', "a connective.",
                      strengths=("- \"churn fell 3% in week two\" is a checkable result.\n"
                                 "- Nothing else reads well yet."))
        ok, viols = check_report(text, CATALOG)
        self.assertFalse(ok)
        self.assertTrue(any("mixed with quoted strengths" in v for v in viols), viols)

    def test_quoted_strength_must_be_verbatim_with_draft(self):
        good = report(' "Moreover, the rollout went well"', "a connective.",
                      strengths="- \"churn fell 3% in week two\" is a checkable result.")
        bad = good.replace("churn fell 3% in week two\" is", "churn fell 4% in week two\" is")
        self.assertTrue(check_report(good, CATALOG, draft=DRAFT2)[0])
        ok, viols = check_report(bad, CATALOG, draft=DRAFT2)
        self.assertFalse(ok)
        self.assertTrue(any("strengths: quote not found verbatim" in v for v in viols), viols)

    def test_praising_a_fact_in_a_flagged_sentence_is_allowed(self):
        # Owner ruling R4: no string-overlap rule. A sentence can hold a
        # checkable fact and a vague modifier; praising the fact is fine.
        text = report(' "Furthermore, churn fell 3% in week two"', "a connective.",
                      fix='"Churn fell 3% in week two."',
                      strengths="- \"churn fell 3% in week two\" is a checkable result.")
        ok, viols = check_report(text, CATALOG, draft=DRAFT2)
        self.assertTrue(ok, viols)


if __name__ == "__main__":
    unittest.main()


class ContractText(unittest.TestCase):
    def test_contract_states_the_rules(self):
        c = _read(SUITE_ROOT, "skills", "comms-polish", "references",
                  "audit-report-contract.md")
        for phrase in ("Why **starts** with `×N`",
                       "with no ellipses",
                       "non-overlapping span",
                       "**Counts describe; they never become quotas or rewrite targets.**",
                       "A Fix uses only material in the draft",
                       "Assume your pull is toward\n   crediting the draft",
                       "Nothing here reads well yet: every sentence carries a flagged pattern.",
                       "A \"Nothing\" bullet never sits next to quoted strengths."):
            self.assertIn(phrase, c)
