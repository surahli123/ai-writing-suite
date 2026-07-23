"""Guard the distributable tree against maintainer-specific live state."""

import os
import re
import unittest


_EVALS = os.path.dirname(os.path.abspath(__file__))
_SHARED = os.path.join(_EVALS, "..", "_shared")
_VOICE_PROFILES = os.path.join(_SHARED, "voice-profiles")
_LEARNED_RULES = os.path.join(_SHARED, "learned-rules.md")
_SAMPLE_BANNER = "> SAMPLE PROFILE."


class NoMaintainerStateInPackage(unittest.TestCase):
    def test_no_real_voice_profiles_ship(self):
        if not os.path.isdir(_VOICE_PROFILES):
            return

        real_profiles = []
        for name in sorted(os.listdir(_VOICE_PROFILES)):
            if not name.endswith(".md"):
                continue
            path = os.path.join(_VOICE_PROFILES, name)
            if not os.path.isfile(path):
                continue
            with open(path, encoding="utf-8") as fh:
                if _SAMPLE_BANNER not in fh.read():
                    real_profiles.append(name)

        self.assertEqual(
            [], real_profiles,
            "shipped _shared/voice-profiles/ contains real profile(s): "
            + ", ".join(real_profiles))

    def test_no_active_or_proposed_real_learned_rules_ship(self):
        with open(_LEARNED_RULES, encoding="utf-8") as fh:
            content = fh.read()

        real_live_rules = []
        blocks = re.finditer(
            r"^###\s+LR-(\d{3})\b(?P<body>.*?)(?=^###\s+LR-\d{3}\b|\Z)",
            content,
            re.MULTILINE | re.DOTALL,
        )
        for block in blocks:
            rule_id = block.group(1)
            if rule_id == "000":
                continue
            status = re.search(
                r"^\s*(?:-\s*)?\*{0,2}status:\*{0,2}\s*(active|proposed)\b",
                block.group("body"),
                re.MULTILINE | re.IGNORECASE,
            )
            if status:
                real_live_rules.append(
                    "LR-{} ({})".format(rule_id, status.group(1).lower()))

        self.assertEqual(
            [], real_live_rules,
            "shipped _shared/learned-rules.md contains live real rule(s): "
            + ", ".join(real_live_rules))


if __name__ == "__main__":
    unittest.main()
