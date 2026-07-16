"""Contract tests for comms-polish genre presets.

Presets are instruction prose, so these tests pin their selectable shapes and
load-bearing reader tasks rather than pretending to score writing quality.
"""

import os
import re
import unittest


SUITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRESETS = os.path.join(
    SUITE_ROOT, "skills", "comms-polish", "references", "scenario-presets.md"
)
COMMS_POLISH = os.path.join(SUITE_ROOT, "skills", "comms-polish", "SKILL.md")

EXPECTED_PRESETS = [
    "Tweet / X",
    "LinkedIn",
    "README",
    "Memo / Internal Doc",
    "PR Description",
    "Release Note",
]
REQUIRED_LABELS = [
    "**Form constraints:**",
    "**Weight these tells harder",
    "**Target tone/length:**",
    "**Leave alone:**",
    "**Endings that work:**",
]


def _preset_blocks(text):
    matches = list(re.finditer(r"^## \d+\. (.+)$", text, flags=re.MULTILINE))
    blocks = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks[match.group(1)] = text[match.start():end]
    return blocks


class ScenarioPresetContract(unittest.TestCase):
    def setUp(self):
        with open(PRESETS, encoding="utf-8") as fh:
            self.text = fh.read()
        self.blocks = _preset_blocks(self.text)

    def test_preset_registry_has_the_six_supported_genres(self):
        self.assertEqual(list(self.blocks), EXPECTED_PRESETS)

    def test_every_preset_has_the_complete_instruction_shape(self):
        for name, block in self.blocks.items():
            with self.subTest(preset=name):
                for label in REQUIRED_LABELS:
                    self.assertIn(label, block)

    def test_new_presets_keep_their_reader_tasks_explicit(self):
        pr = self.blocks["PR Description"].lower()
        for phrase in ("why", "verification", "required repository template"):
            self.assertIn(phrase, pr)

        release = self.blocks["Release Note"].lower()
        for phrase in ("user-visible", "breaking", "migration"):
            self.assertIn(phrase, release)

    def test_comms_polish_advertises_and_selects_the_new_presets(self):
        with open(COMMS_POLISH, encoding="utf-8") as fh:
            skill = fh.read()
        enrichments = skill[
            skill.index("Three enrichments"):skill.index("## Locating shared assets")
        ].lower()
        workflow = skill[
            skill.index("## Rewrite Workflow"):skill.index("## File Edits")
        ].lower()
        enrichments = re.sub(r"\s+", " ", enrichments)
        workflow = re.sub(r"\s+", " ", workflow)
        for phrase in ("pr description", "release note"):
            self.assertIn(phrase, enrichments)
            self.assertIn(phrase, workflow)


if __name__ == "__main__":
    unittest.main()
