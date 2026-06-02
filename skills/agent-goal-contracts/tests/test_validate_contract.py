import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_contract.py"


VALID_CONTRACT = "\n".join(
    [
        "/goal",
        "GOAL:",
        "Ship a focused regression fix for the auth callback white screen.",
        "",
        "CONTEXT:",
        "- Read AGENTS.md and the auth callback test output first.",
        "",
        "CONSTRAINTS:",
        "- Do not change public auth API response shapes.",
        "",
        "ORACLE:",
        "- `npm test -- auth-callback` exits 0 and the stale-cookie case is covered.",
        "",
        "DONE WHEN:",
        "- The stale-cookie callback regression test passes.",
        "- Existing auth tests pass.",
        "",
        "VERIFY:",
        "- Run `npm test -- auth-callback`.",
        "",
        "ITERATION POLICY:",
        "- Make one focused change, run the auth callback test, then reassess.",
        "",
        "STOP RULES:",
        "- Stop if production credentials or an auth product decision is required.",
        "",
        "OUTPUT:",
        "- Report changed files, root cause, verification, and remaining risk.",
    ]
) + "\n"


class ValidateContractTest(unittest.TestCase):
    def run_validator(self, text: str, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), *extra_args],
            input=text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_accepts_contract_with_required_sections_and_oracle(self) -> None:
        result = self.run_validator(VALID_CONTRACT)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("status=ok", result.stdout)
        self.assertIn("section_count=9", result.stdout)

    def test_rejects_contract_without_oracle(self) -> None:
        result = self.run_validator(VALID_CONTRACT.replace("ORACLE:", "PROOF:"))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required section: ORACLE", result.stderr)

    def test_rejects_required_section_without_content(self) -> None:
        result = self.run_validator(
            VALID_CONTRACT.replace(
                "ORACLE:\n- `npm test -- auth-callback` exits 0 and the stale-cookie case is covered.\n",
                "ORACLE:\n",
            )
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("empty required section: ORACLE", result.stderr)

    def test_rejects_goal_text_over_strict_runtime_target(self) -> None:
        long_goal = "/goal " + ("x" * 3410)

        result = self.run_validator(long_goal, "--strict-runtime-target")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("runtime objective exceeds target", result.stderr)

    def test_rejects_hidden_flag_shape_after_goal_command(self) -> None:
        result = self.run_validator("/goal --tokens 50K fix tests")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("starts with a flag-like token", result.stderr)

    def test_rejects_goalish_prefix(self) -> None:
        result = self.run_validator("/goalish fix tests")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contract must start with /goal", result.stderr)


if __name__ == "__main__":
    unittest.main()
