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
import re
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


class SharedPathReferences(unittest.TestCase):
    # Parent-relative `../_shared` paths silently break on RovoDev manual installs
    # (the agent resolves them against the session cwd) — only suite-root-relative
    # `_shared/...` is allowed; the SKILL.md suite-root protocol defines resolution.
    def test_no_parent_relative_shared_paths(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        paths = [os.path.join(root, "SKILL.md")]
        paths += glob.glob(os.path.join(root, "skills", "*", "SKILL.md"))
        paths += glob.glob(os.path.join(root, "skills", "*", "references", "*.md"))
        self.assertGreaterEqual(len(paths), 5,
                                "expected router SKILL.md + >=4 sub-skill docs")
        banned = re.compile(r"\.\./.*_shared")
        for path in sorted(paths):
            with open(path, encoding="utf-8") as fh:
                for lineno, line in enumerate(fh.read().splitlines(), 1):
                    self.assertIsNone(
                        banned.search(line),
                        f"{path}:{lineno}: parent-relative _shared reference "
                        f"(use root-relative '_shared/...'): {line.strip()}")


class ReferencedSharedFilesExist(unittest.TestCase):
    # Catches broken suite-root-relative references at CI time: a SKILL.md can
    # name a `_shared/...` or `skills/.../references/...` file that does not exist
    # and nothing errors until an agent tries to load it on a real host.
    def test_referenced_shared_files_exist(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        paths = [os.path.join(root, "SKILL.md")]
        paths += glob.glob(os.path.join(root, "skills", "*", "SKILL.md"))
        self.assertGreaterEqual(len(paths), 5,
                                "expected router SKILL.md + >=4 sub-skill docs")
        # Only references inside inline-code spans (`...`) count, so prose like
        # "_shared/ holds shared assets" is not mistaken for a file reference.
        shared_re = re.compile(r"`(_shared/[A-Za-z0-9_/.-]+\.md)`")
        ref_re = re.compile(
            r"`(skills/[a-z-]+/references/[A-Za-z0-9_.-]+\.md)`")
        found = set()
        for path in sorted(paths):
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            for rel in shared_re.findall(text) + ref_re.findall(text):
                found.add(rel)
                target = os.path.join(root, rel)
                self.assertTrue(
                    os.path.isfile(target),
                    f"{path}: referenced file does not exist: {rel}")
        # Non-vacuous floor: the regex must actually be matching real references,
        # not passing because it found nothing to check.
        self.assertGreaterEqual(len(found), 6,
                                f"expected >=6 distinct references, found {sorted(found)}")


if __name__ == "__main__":
    unittest.main()
