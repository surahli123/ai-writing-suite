"""SKILL.md frontmatter contract test (engine-polish #2 guard).

The engine-polish change edited 4 sub-skill `description:` lines (negative
routing). A typo or a broken `---` block silently breaks host skill discovery
(Claude/Codex/Cursor read name+description from frontmatter) with NO runtime
error. This test turns that silent failure into a red CI check.

It asserts every `skills/*/SKILL.md` has a frontmatter block with a non-empty
`name:` and a non-empty single-line `description:`. Stdlib-only (no yaml dep),
no network. Runs under `run_all.sh` via `unittest discover`.
"""

import glob
import os
import unittest

# evals/ -> <skill-root> -> skills/*/SKILL.md
SKILLS_GLOB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "skills", "*", "SKILL.md")


def _frontmatter(path):
    """Return the lines between the first two '---' fences, or [] if absent."""
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i]
    return []


def _field(fm_lines, key):
    prefix = key + ":"
    for ln in fm_lines:
        if ln.startswith(prefix):
            return ln[len(prefix):].strip()
    return None


class SkillManifests(unittest.TestCase):
    def test_skills_found(self):
        self.assertGreaterEqual(len(glob.glob(SKILLS_GLOB)), 4,
                                "expected >=4 sub-skills with SKILL.md")

    def test_every_skill_has_name_and_description(self):
        for path in sorted(glob.glob(SKILLS_GLOB)):
            fm = _frontmatter(path)
            self.assertTrue(fm, f"{path}: no frontmatter '---' block")
            name = _field(fm, "name")
            desc = _field(fm, "description")
            self.assertTrue(name, f"{path}: missing/empty 'name:'")
            self.assertTrue(desc, f"{path}: missing/empty 'description:'")


if __name__ == "__main__":
    unittest.main()
