"""Schema-contract test for the voice profile (Phase 2a tripwire).

comms-polish reads the learned voice by `## H2` header from
`_shared/host-profile-template.md` (the blank form voice-onboard fills, and the
shape voice-profile.md inherits). If a header is renamed or dropped, comms-polish
SILENTLY falls back to generic voice with no error (see voice-onboard/SKILL.md +
comms-polish/SKILL.md "Voice Matching"). This stdlib-only test turns that silent
failure into a loud CI failure.

Scope: it does NOT judge voice quality (that needs a sample corpus — deferred to
Phase 2b). It only guards the header contract the two skills agree on.
"""

import os
import re
import unittest

# Headers comms-polish reads (comms-polish/SKILL.md "Voice Matching"). Apostrophes
# are normalized before comparison so a straight/curly swap doesn't false-fail.
REQUIRED_HEADERS = [
    "Tone",
    "Sentence Length",
    "Vocabulary Do",
    "Vocabulary Don't",
    "Signature Moves",
    "Punctuation & Formatting",
    "Openings & Closings",
    "Uncertainty Style",
    "Things To Avoid",
    "Scope & Calibration",
]

TEMPLATE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "_shared", "host-profile-template.md")


def _norm(s):
    return s.replace("’", "'").strip()


class VoiceProfileContract(unittest.TestCase):
    def test_template_exists(self):
        self.assertTrue(os.path.exists(TEMPLATE),
                        f"voice profile template missing: {TEMPLATE}")

    def test_all_consumer_headers_present(self):
        with open(TEMPLATE, encoding="utf-8") as fh:
            headers = {_norm(m.group(1))
                       for m in re.finditer(r"^##\s+(.+)$", fh.read(), re.M)}
        for h in REQUIRED_HEADERS:
            self.assertIn(
                _norm(h), headers,
                f"host-profile-template.md missing '## {h}' — comms-polish reads "
                f"this header; renaming it silently breaks voice matching")


if __name__ == "__main__":
    unittest.main()
