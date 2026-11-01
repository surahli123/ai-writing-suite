"""Deterministic fidelity-class checker: mutant table plus fixture tie-in.

Each class has a positive mutant (the strength or scope change must be caught)
and a negative control (a faithful rewrite must pass). Fixtures opt in with
`fidelity_check: true` (a PASS fixture must be clean) or `fidelity_class`
(a gold-FAIL fixture must be caught for its declared class).
"""
import json
import unittest
from pathlib import Path

from fixtures.fidelity import fidelity_violations

HERE = Path(__file__).resolve().parent / "fixtures"

# (class, before, bad_after, good_after)
MUTANTS = [
    ("scope", "Only 3 regions saw a lift.", "3 regions saw a lift.", "Just 3 regions saw a lift, only those."),
    ("scope", "Run it at least twice.", "Run it twice.", "Run it at least twice before merging."),
    ("approximator", "Churn was roughly 60% of the base.", "Churn was 60% of the base.", "Churn was about 60% of the base."),
    ("approximator", "It took about a 5% hit.", "It took a 5% hit.", "It took roughly a 5% hit."),
    ("units", "Retention rose 1.2 pp.", "Retention rose 1.2%.", "Retention rose 1.2 percentage points."),
    ("units", "Up 0.4 percentage points.", "Up 0.4%.", "Up 0.4 pp."),
    ("significance", "The lift was not statistically significant (p=0.2).", "The change had no effect.", "The lift was not statistically significant (p=0.2)."),
    ("significance", "No detectable effect on retention.", "The reminder made no difference.", "There was no detectable effect on retention."),
    ("interval", "CTR +2.1% (95% CI +0.4% to +3.8%).", "CTR +2.1%.", "CTR rose 2.1% (95% CI +0.4% to +3.8%)."),
    ("strength", "The review suggests the deploy caused it.", "The review shows the deploy caused it.", "The review suggests the deploy caused it."),
    ("strength", "The rollback may fix latency.", "The rollback will fix latency.", "Rolling back may fix latency."),
    ("strength", "We hope to ship by Friday.", "We'll ship by Friday.", "We hope to ship it by Friday."),
    ("strength", "Analysts expect demand to soften.", "Demand will soften.", "Analysts expect demand to soften next year."),
    ("added_qualification", "Retention rose 1.2 pp after the redesign.",
     "Retention rose 1.2 pp after the redesign, though this does not by itself establish that the redesign caused it.",
     "After the redesign, retention rose 1.2 pp."),
    ("added_qualification", "The new model cut false positives by 30%.",
     "The new model cut false positives by 30%, but these results should be interpreted with caution.",
     "False positives fell 30% with the new model."),
]


class FidelityMutants(unittest.TestCase):
    def test_every_class_has_a_mutant(self):
        self.assertEqual({c for c, *_ in MUTANTS},
                         {"scope", "approximator", "units", "significance", "interval", "strength",
                          "added_qualification"})

    def test_bad_rewrites_are_caught_for_their_class(self):
        for cls, before, bad, _ in MUTANTS:
            with self.subTest(cls=cls, bad=bad):
                self.assertIn(cls, {c for c, _ in fidelity_violations(before, bad)})

    def test_faithful_rewrites_pass(self):
        for cls, before, _, good in MUTANTS:
            with self.subTest(cls=cls, good=good):
                self.assertEqual(fidelity_violations(before, good), [])

    def test_identity_is_always_clean(self):
        for _, before, _, _ in MUTANTS:
            self.assertEqual(fidelity_violations(before, before), [])


class FidelityFixtures(unittest.TestCase):
    def test_opted_in_pass_fixtures_are_clean(self):
        fx = [f for f in json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))["fixtures"] if f.get("fidelity_check")]
        self.assertGreaterEqual(len(fx), 2)
        for f in fx:
            with self.subTest(f=f["id"]):
                self.assertEqual(fidelity_violations(f["before"], f["after"]), [])
                self.assertTrue(f.get("detector_blind"))  # stays out of the calibration band

    def test_gold_fail_fixtures_are_caught_for_declared_class(self):
        fx = [f for f in json.loads((HERE / "fixtures_fail.json").read_text(encoding="utf-8"))["fixtures"] if f.get("fidelity_class")]
        self.assertGreaterEqual(len(fx), 5)
        for f in fx:
            with self.subTest(f=f["id"]):
                found = {c for c, _ in fidelity_violations(f["before"], f["after"])}
                self.assertIn(f["fidelity_class"], found)
                self.assertEqual(f["fail_dimension"], "meaning_preserved")


if __name__ == "__main__":
    unittest.main()
