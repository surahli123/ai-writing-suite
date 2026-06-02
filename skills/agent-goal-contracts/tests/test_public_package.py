import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicPackageTest(unittest.TestCase):
    def test_skill_frontmatter_uses_new_identity(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("name: agent-goal-contracts", skill)
        self.assertNotIn("name: goal-forge", skill)
        self.assertIn("Runner Adapter", skill)
        self.assertIn("Oracle", skill)

    def test_readme_carries_required_attribution(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for repo in [
            "michaelpersonal/goal-forge",
            "lidangzzz/goal-driven",
            "grp06/goalcraft",
            "tolibear/goalbuddy",
            "majiayu000/awesome-goal-prompts",
        ]:
            self.assertIn(repo, readme)

        self.assertIn("goal-driven is used as conceptual inspiration only", readme)

    def test_reference_modules_exist(self) -> None:
        for relative in [
            "references/contract_schema.md",
            "references/mode_adapters.md",
            "references/runner_adapters.md",
            "references/oracle_and_proof.md",
            "references/reference_prompt_catalog.md",
            "NOTICE.md",
        ]:
            self.assertTrue((ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
