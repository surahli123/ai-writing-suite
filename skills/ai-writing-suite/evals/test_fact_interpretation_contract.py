"""Contract tests for the shared fact-to-interpretation boundary.

These checks pin the instruction plumbing and the mode-specific authority split.
They do not pretend that deterministic substring checks can judge whether a real
source warrants a causal or interpretive claim; the advisory fixture lane owns
that behavior evidence.
"""

from functools import cache
from pathlib import Path
import unittest


SUITE_ROOT = Path(__file__).resolve().parent.parent
CONTRACT = SUITE_ROOT / "_shared" / "fact-interpretation-boundary.md"
DRAFT = SUITE_ROOT / "skills" / "comms-draft" / "SKILL.md"
POLISH = SUITE_ROOT / "skills" / "comms-polish" / "SKILL.md"
FINAL_PASS = (
    SUITE_ROOT
    / "skills"
    / "comms-polish"
    / "references"
    / "final-pass-checklist.md"
)
CATALOG = SUITE_ROOT / "_shared" / "patterns" / "significance-attribution.md"
EXAMPLES = (
    SUITE_ROOT
    / "skills"
    / "comms-polish"
    / "references"
    / "before-after-examples.md"
)
REFERENCE = "_shared/fact-interpretation-boundary.md"


@cache
def read(path):
    """Read a contract surface once per test process."""
    return path.read_text(encoding="utf-8")

CONTRACT_RULES = [
    "confirmed fact",
    "supported interpretation",
    "unanswered question",
    "cause, motive, significance, trend, or conclusion",
    "co-occurrence",
    "may be related to",
    "author hypothesis",
    "Cues locate; evidence decides.",
]


class SharedFactInterpretationContract(unittest.TestCase):
    def test_shared_contract_exists_and_carries_relation_decision_rules(self):
        self.assertTrue(CONTRACT.is_file(), f"missing shared contract: {CONTRACT}")
        for phrase in CONTRACT_RULES:
            self.assertIn(phrase, read(CONTRACT))

    def test_both_skill_entrypoints_load_the_shared_contract_once(self):
        for skill in (DRAFT, POLISH):
            with self.subTest(skill=skill):
                self.assertEqual(read(skill).count(REFERENCE), 1)

    def test_draft_contract_uses_source_buckets_and_visible_causal_gap(self):
        self.assertIn("classify the source packet", read(DRAFT))
        self.assertIn("[NEEDS: causal evidence]", read(DRAFT))
        self.assertIn("new prose", read(DRAFT))

    def test_polish_contract_distinguishes_complete_and_standalone_sources(self):
        self.assertIn("independent source packet", read(POLISH))
        self.assertIn("support was not assessed", read(POLISH))
        self.assertIn("substantive author interpretation", read(POLISH))
        self.assertIn("redundant gloss", read(POLISH))

    def test_user_supplied_source_authorizes_alignment(self):
        # Skill-lift v0 (notes/eval-lift-2026-11-01): preserve-and-flag with a
        # user-supplied source lost 2/6 vs 6/6 would-send, and contradicted the
        # factbridge gold answers. A supplied source authorizes the repair.
        for surface in (CONTRACT, POLISH):
            with self.subTest(surface=surface.name):
                body = read(surface)
                self.assertIn("authorizes factual", body)
                self.assertIn("Never", body)
        self.assertIn("never make the change silently", read(CONTRACT).lower())
        self.assertIn("never change it silently", read(POLISH).lower())
        self.assertNotIn("preserve the position and flag\n   it through the existing output surface unless the user authorized",
                         read(POLISH))
        self.assertIn("Supplying the\nsource is the authorization", read(EXAMPLES))

    def test_final_pass_rechecks_relation_without_a_cue_word_ban(self):
        self.assertIn("fact-to-interpretation", read(FINAL_PASS))
        self.assertIn("source support", read(FINAL_PASS))
        self.assertIn("not a word blacklist", read(FINAL_PASS))

    def test_s2_and_s7_define_support_and_construction_validity(self):
        body = read(CATALOG)
        s2 = body[body.index("### S2"):body.index("### S3")]
        s7 = body[body.index("### S7"):body.index("### S8")]
        for phrase in ("cause, motive, significance, trend, or conclusion",
                       "author hypothesis", "support was not assessed"):
            self.assertIn(phrase, s2)
        for phrase in ("not the `-ing` form", "subject is clear",
                       "are not banned", "may be reflecting"):
            self.assertIn(phrase, s7)

    def test_worked_example_covers_the_support_matrix(self):
        for phrase in ("Fact-only repair", "The two changes coincided",
                       "may be related to", "My working hypothesis",
                       "source directly says", "support was not assessed"):
            self.assertIn(phrase, read(EXAMPLES))


if __name__ == "__main__":
    unittest.main()
