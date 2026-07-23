"""Deterministic lint for the shared untrusted-content contract.

This gate verifies that the shared contract and adversarial fixture are present
and that every suite entry point references the contract exactly once. Whether
an agent quotes rather than obeys the fixture requires a model judge and is not
claimed by this deterministic test.
"""

from pathlib import Path
import unittest


SUITE_ROOT = Path(__file__).resolve().parent.parent
CONTRACT = SUITE_ROOT / "_shared" / "untrusted-content.md"
FIXTURE = SUITE_ROOT / "evals" / "fixtures" / "untrusted_kb_entry.md"
REFERENCE = "_shared/untrusted-content.md"
EMBEDDED_INSTRUCTION_MARKER = "embedded-instruction-marker"
SKILL_FILES = [
    SUITE_ROOT / "SKILL.md",
    SUITE_ROOT / "skills" / "comms-polish" / "SKILL.md",
    SUITE_ROOT / "skills" / "comms-draft" / "SKILL.md",
    SUITE_ROOT / "skills" / "comms-qa" / "SKILL.md",
    SUITE_ROOT / "skills" / "voice-onboard" / "SKILL.md",
]


class UntrustedContentContract(unittest.TestCase):
    def test_contract_exists(self):
        self.assertTrue(CONTRACT.is_file(), f"missing shared contract: {CONTRACT}")

    def test_every_skill_references_contract_once(self):
        for skill_file in SKILL_FILES:
            with self.subTest(skill_file=skill_file):
                body = skill_file.read_text(encoding="utf-8")
                self.assertEqual(
                    body.count(REFERENCE),
                    1,
                    f"{skill_file} must reference {REFERENCE} exactly once",
                )

    def test_adversarial_fixture_has_embedded_instruction_marker(self):
        self.assertTrue(FIXTURE.is_file(), f"missing adversarial fixture: {FIXTURE}")
        body = FIXTURE.read_text(encoding="utf-8")
        self.assertIn(
            EMBEDDED_INSTRUCTION_MARKER,
            body,
            f"{FIXTURE} must mark its embedded instruction",
        )


if __name__ == "__main__":
    unittest.main()
