"""Pin comms-draft's acceptance-criteria prose to the eval constants."""

import pathlib
import re
import unittest

from fixtures.run_draft_cases import CRITERIA_DIMENSIONS


SUITE_ROOT = pathlib.Path(__file__).resolve().parents[2]
SKILL = SUITE_ROOT / "skills" / "comms-draft" / "SKILL.md"


class DraftCriteriaCoupling(unittest.TestCase):
    def test_skill_criteria_dimensions_match_runner_constants(self):
        text = SKILL.read_text(encoding="utf-8")
        match = re.search(
            r"^### 1\. Derive per-task acceptance criteria "
            r"\(before writing a word\)\s*$\n\n"
            r"(?P<criteria>.*?)(?:\n\n|\Z)",
            text,
            re.M | re.S,
        )
        self.assertIsNotNone(
            match,
            "comms-draft step-1 acceptance-criteria prose is not parseable",
        )

        prose_dimensions = re.findall(
            r"\*\*([^*]+)\*\*",
            match.group("criteria"),
        )
        self.assertEqual(
            len(prose_dimensions),
            5,
            "comms-draft step 1 must name exactly five bolded dimensions",
        )
        self.assertEqual(
            set(prose_dimensions),
            set(CRITERIA_DIMENSIONS),
            "comms-draft step-1 dimensions drifted from CRITERIA_DIMENSIONS",
        )


if __name__ == "__main__":
    unittest.main()
