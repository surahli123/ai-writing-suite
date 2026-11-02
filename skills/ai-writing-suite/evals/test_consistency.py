"""Document consistency check (aiws.consistency): mutants plus known-human negatives.

Each mutant takes a consistent document and changes one number, which must be
flagged. Each negative is a legitimate document that must pass: different
denominators, from/to pairs, exact repeats, shares that sum to 100.
"""
import os
import subprocess
import sys
import unittest

# evals/ -> <suite-root>, so ``import aiws`` resolves to the sibling package.
_SUITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SUITE_ROOT not in sys.path:
    sys.path.insert(0, _SUITE_ROOT)

from aiws.consistency import check  # noqa: E402  (path set above)

CONSISTENT = """Retention rose 12% after the onboarding redesign, and setup tickets fell by a third.

| Cohort | Retention change |
|---|---|
| New users | +12% |
| Returning | +4% |

Traffic mix: mobile 61%, desktop 33%, tablet 6% of sessions."""

MUTANTS = [
    ("near-miss", CONSISTENT.replace("| New users | +12% |", "| New users | +11.6% |")),
    ("share-sum", CONSISTENT.replace("tablet 6%", "tablet 10%")),
    ("near-miss", "We served 1.2M sessions in the test.\n\nOver the 14 days the test logged 1.25M sessions in total."),
    ("share-sum", "Survey answers:\n- Confusing: 61%\n- Fine: 30%\n- Easy: 14%"),
]

NEGATIVES = [
    CONSISTENT,
    # Different metrics that happen to be close are not a contradiction when the lead value also appears.
    "Churn rose from 4.1% to 5.3%.\n\nChurn was 4.1% in Q2 and 5.3% in Q3; annual-plan churn stayed at 1.2%.",
    # Two named denominators: lead 61% of respondents, body 60% of all users is a different number on purpose,
    # but it is outside the lead/body near-miss band only if tolerance is respected; keep it far apart here.
    "61% of respondents found onboarding confusing.\n\nAmong all active users the estimate is closer to 45%.",
    # Shares that sum to 100.
    "Traffic: mobile 61%, desktop 33%, tablet 6% of sessions.",
    # Unitless numbers (years, counts) are never compared.
    "We shipped 3 models in 2025.\n\nIn 2026 we plan 4 models.",
    # A single paragraph has no lead/body split.
    "CTR rose 2.1% (95% CI 0.4% to 3.8%), and the headline 2.1% may overstate the steady-state lift.",
]


class Consistency(unittest.TestCase):
    def test_mutants_are_flagged_for_their_kind(self):
        for kind, doc in MUTANTS:
            with self.subTest(kind=kind, doc=doc[:40]):
                self.assertIn(kind, {k for k, _ in check(doc)})

    def test_consistent_documents_pass(self):
        for doc in NEGATIVES:
            with self.subTest(doc=doc[:40]):
                self.assertEqual(check(doc), [])

    def test_cli_exit_codes(self):
        tool = os.path.join(os.path.dirname(__file__), "..", "tools", "consistency_check.py")
        ok = subprocess.run([sys.executable, tool, "-"], input=CONSISTENT, text=True, capture_output=True)
        bad = subprocess.run([sys.executable, tool, "-"], input=MUTANTS[0][1], text=True, capture_output=True)
        usage = subprocess.run([sys.executable, tool], text=True, capture_output=True)
        self.assertEqual((ok.returncode, bad.returncode, usage.returncode), (0, 1, 2))
        self.assertIn("[near-miss]", bad.stdout)


if __name__ == "__main__":
    unittest.main()
