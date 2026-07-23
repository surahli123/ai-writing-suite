"""Self-test for the repository packaging validator."""

import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_packaging  # noqa: E402


class ValidatePackagingExitCodes(unittest.TestCase):
    """The packaging gate must pass the real tree and fail a broken manifest."""

    def _run_from(self, root):
        suite = root / "skills" / "ai-writing-suite"
        output = io.StringIO()
        with mock.patch.object(validate_packaging, "ROOT", str(root)), \
                mock.patch.object(validate_packaging, "SUITE", str(suite)), \
                contextlib.redirect_stdout(output):
            rc = validate_packaging.main()
        return rc, output.getvalue()

    def _copy_packaging_tree(self, destination):
        suite = destination / "skills" / "ai-writing-suite"
        manifest_paths = (
            Path(".claude-plugin/marketplace.json"),
            Path(".agents/plugins/marketplace.json"),
            Path("skills/ai-writing-suite/.claude-plugin/plugin.json"),
            Path("skills/ai-writing-suite/.codex-plugin/plugin.json"),
        )
        for relative in manifest_paths:
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO_ROOT / relative, target)

        source_skills = REPO_ROOT / "skills" / "ai-writing-suite" / "skills"
        for skill_md in source_skills.glob("*/SKILL.md"):
            target = suite / "skills" / skill_md.parent.name / "SKILL.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(skill_md, target)

    def test_real_tree_exits_zero_and_prints_ok(self):
        rc, output = self._run_from(REPO_ROOT)

        self.assertEqual(rc, 0)
        self.assertIn("packaging validation OK", output)

    def test_broken_agents_marketplace_source_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            scratch_root = Path(tmp)
            self._copy_packaging_tree(scratch_root)
            manifest = scratch_root / ".agents" / "plugins" / "marketplace.json"
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["plugins"][0]["source"]["path"] = "./skills/not-ai-writing-suite"
            manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            rc, output = self._run_from(scratch_root)

        self.assertEqual(rc, 1)
        self.assertIn(".agents/plugins/marketplace.json", output)
        self.assertIn("source", output)

    def test_mismatched_agents_marketplace_name_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            scratch_root = Path(tmp)
            self._copy_packaging_tree(scratch_root)
            manifest = scratch_root / ".agents" / "plugins" / "marketplace.json"
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["name"] = "not-ai-writing-suite"
            manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            rc, output = self._run_from(scratch_root)

        self.assertEqual(rc, 1)
        self.assertIn("manifest name mismatch", output)
        self.assertIn("agents-marketplace.name", output)


if __name__ == "__main__":
    unittest.main()
