"""Contract tests for comms-polish edit restraint (step 1 of the 2026-11-01 plan).

Why: the skill-lift v0 eval (notes/eval-lift-2026-11-01) found the suite's losses
were over-edits. It deleted an author's stance and an attribution, and expanded
terse text. The outside sources that measure this (theclaymethod/unslop's
NO-SHIP, millwright) say damage on clean text is what decides shipping. These
tests pin the instructions and the fixture pairing. They do not claim that
substring checks prove the behavior; the step gate in notes/ measures that.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POLISH = ROOT / "skills" / "comms-polish" / "SKILL.md"
FINAL = ROOT / "skills" / "comms-polish" / "references" / "final-pass-checklist.md"
S_CAT = ROOT / "_shared" / "patterns" / "significance-attribution.md"
FIX = ROOT / "evals" / "fixtures"


def text(p):
    return p.read_text(encoding="utf-8")


class EditRestraintContract(unittest.TestCase):
    def test_light_edit_mode_is_a_listed_mode(self):
        self.assertIn("| `light-edit` |", text(POLISH))
        self.assertIn("clean text comes back unchanged", text(POLISH))

    def test_restraint_rules_present(self):
        body = text(POLISH)
        for phrase in ("Unchanged is a valid result.",
                       "Match the edit to the request",
                       "improvements that change no meaning",
                       "Change a sentence only for a failure you can name.",
                       "A single catalog match is not a failure on its own",
                       "Fix the wording, keep the claim.",
                       "Never move an attributed claim onto the author.",
                       "Restructure only when it helps a judgment document.",
                       "do not expand bullets into prose"):
            self.assertIn(phrase, body)

    def test_final_pass_has_reversion_and_cut_checks(self):
        body = text(FINAL)
        self.assertIn("**Reversion test:**", body)
        self.assertIn("**Cut check:**", body)
        self.assertIn("stance, attributions, and commitments survive", body)
        # Restraint runs before the style layer.
        self.assertLess(body.index("L1b"), body.index("L2"))

    def test_vague_attribution_fix_never_invents_or_reassigns(self):
        s4 = text(S_CAT)
        s4 = s4[s4.index("### S4"):s4.index("### S5")]
        self.assertIn("never invent the source", s4)
        self.assertIn("attributed claim into the author's own claim", s4)

    def test_clean_text_fixture_is_identity_and_has_a_fail_partner(self):
        passes = {f["id"]: f for f in json.loads(text(FIX / "fixtures.json"))["fixtures"]}
        fails = {f["id"]: f for f in json.loads(text(FIX / "fixtures_fail.json"))["fixtures"]}
        clean = passes["restraint-01-clean-human-en"]
        self.assertEqual(clean["before"], clean["after"])
        self.assertTrue(clean.get("detector_blind"))  # stays out of the calibration band
        partner = fails["fail-restraint-overedit-en"]
        self.assertEqual(partner["before"], clean["before"])
        self.assertNotEqual(partner["after"], clean["before"])
        self.assertEqual(fails["fail-stance-dropped-en"]["fail_dimension"], "meaning_preserved")


if __name__ == "__main__":
    unittest.main()
