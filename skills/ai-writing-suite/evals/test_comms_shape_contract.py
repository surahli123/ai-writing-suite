"""Contract tests for comms-shape (step 10; owner ruling R4).

These pin the instruction text that carries the skill's design decisions and the
three fixes from the 2026-11-02 pilot (notes/eval-comms-shape-2026-11-02/report.md).
They do not prove behavior; the pilot measures that.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHAPE = ROOT / "skills" / "comms-shape" / "SKILL.md"
ARCHIVE = ROOT.parent.parent / "archive" / "comms-draft"


def text():
    return SHAPE.read_text(encoding="utf-8")


class Flow(unittest.TestCase):
    def test_two_required_stops_and_intake_cap(self):
        t = text()
        self.assertIn("### 2. Thesis (required stop 1)", t)
        self.assertIn("### 3. Outline (required stop 2)", t)
        self.assertIn("Ask at most three questions, in one message", t)
        self.assertIn("**in the same message** as the outline", t)

    def test_request_classes_and_transitions(self):
        t = text()
        for cls in ("(a) From notes or an idea", "(b) Pressure-test", "(c) Mixed", "(d) Explicit skip"):
            self.assertIn(cls, t)
        self.assertIn("collapse the stops, not the\nstages", t)
        self.assertIn("**one** classifying question", t)
        self.assertIn("Return the whole revised document", t)

    def test_ledger_and_neutrality(self):
        t = text()
        self.assertIn("**Approval is a tag, not a source.**", t)
        self.assertIn("Unsourced-claims check.", t)
        self.assertIn("Do not praise the thesis, the outline, or the author's answers.", t)
        self.assertIn("claims not decisions", t)


class PilotFixes(unittest.TestCase):
    def test_fill_from_material_before_marking_needs(self):
        t = text()
        self.assertIn("Fill every slot the notes or the author's answers already hold first.", t)
        self.assertIn("check every\n`[NEEDS]` against the notes and answers once more", t)

    def test_meta_sections_stay_outside_the_document(self):
        self.assertIn("Nothing below is ever written inside the\ndocument's body", text())

    def test_labels_are_claims(self):
        self.assertIn("**Labels are claims.**", text())


class Archive(unittest.TestCase):
    def test_comms_draft_is_archived_and_not_discoverable(self):
        self.assertFalse((ROOT / "skills" / "comms-draft").exists())
        self.assertTrue((ARCHIVE / "SKILL.archived.md").is_file())
        self.assertFalse((ARCHIVE / "SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
