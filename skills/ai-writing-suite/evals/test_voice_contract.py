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
import sys
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

# New in the stylometric-fingerprint feature: the quantitative half of the
# profile. ADDED headers (the 10 above are unchanged and still guarded). This
# header is what carries the measured numbers the eval asserts on.
MEASURED_HEADERS = [
    "Measured Fingerprint",
]

TEMPLATE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "_shared", "host-profile-template.md")

# stylometry.py lives in the suite root's _shared/ (voice-onboard resolves it by
# suite-root-relative path). Add that dir to sys.path to import it here.
_SHARED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_shared")
sys.path.insert(0, _SHARED)


def _norm(s):
    return s.replace("’", "'").strip()


class VoiceProfileContract(unittest.TestCase):
    def test_template_exists(self):
        self.assertTrue(os.path.exists(TEMPLATE),
                        f"voice profile template missing: {TEMPLATE}")

    def _headers(self):
        with open(TEMPLATE, encoding="utf-8") as fh:
            return {_norm(m.group(1))
                    for m in re.finditer(r"^##\s+(.+)$", fh.read(), re.M)}

    def test_all_consumer_headers_present(self):
        headers = self._headers()
        for h in REQUIRED_HEADERS:
            self.assertIn(
                _norm(h), headers,
                f"host-profile-template.md missing '## {h}' — comms-polish reads "
                f"this header; renaming it silently breaks voice matching")

    def test_measured_fingerprint_header_present(self):
        # The added quantitative section. Guarded so it cannot be dropped without
        # a loud CI failure, same as the 10 qualitative headers.
        headers = self._headers()
        for h in MEASURED_HEADERS:
            self.assertIn(
                _norm(h), headers,
                f"host-profile-template.md missing '## {h}' — this header carries "
                f"the measured stylometric numbers the eval asserts on")


class MeasuredNumbersAreRecomputable(unittest.TestCase):
    """The property that makes the eval honest (advisor Q3c): every measured
    number in a profile must be RECOMPUTABLE from its stated corpus.

    We build a small per-genre corpus, produce a profile block exactly as
    voice-onboard would (via stylometry.format_fingerprint), then parse the
    numbers back out and recompute them from the SAME corpus — some via the
    module, and the load-bearing ones via an INDEPENDENT hand computation so the
    property is not just the module agreeing with itself.
    """

    CORPUS = {
        "blog": [
            "We shipped the reranker nobody liked. NDCG rose 2 points. Latency "
            "doubled, which nobody wanted to say out loud.",
            "The tail stayed messy. We never re-tested on it. That was the real "
            "risk, not the 2 point win.",
            "Ship first, measure second is how you get a 40% regression you only "
            "notice in the postmortem three weeks later.",
        ],
    }

    def _profile_and_fp(self):
        import stylometry as S
        fp = S.compute_fingerprint(self.CORPUS["blog"], genre="blog")
        return S.format_fingerprint(fp), fp

    def test_stated_mean_matches_independent_recompute(self):
        rendered, _ = self._profile_and_fp()
        m = re.search(r"mean=([0-9.]+)", rendered)
        self.assertIsNotNone(m, "profile block has no sentence-length mean")
        stated_mean = float(m.group(1))

        # Independent recomputation (different code path than the module):
        text = "\n\n".join(self.CORPUS["blog"])
        sents = [s for s in re.split(r"[.!?]+", text) if s.strip()]
        lengths = [len(re.findall(r"[A-Za-z0-9]+(?:['\-][A-Za-z0-9]+)*", s))
                   for s in sents]
        indep_mean = round(sum(lengths) / len(lengths), 1)
        self.assertEqual(stated_mean, indep_mean,
                         "profile's sentence-length mean is not recomputable "
                         "from its stated corpus")

    def test_stated_testable_number_count_matches_corpus(self):
        rendered, _ = self._profile_and_fp()
        m = re.search(r"\((\d+) figures\)", rendered)
        self.assertIsNotNone(m)
        stated = int(m.group(1))
        # Corpus contains exactly these figures: 2, 2, 40 -> 3 testable numbers.
        self.assertEqual(stated, 3)

    def test_stated_ai_register_count_is_zero_and_true(self):
        rendered, fp = self._profile_and_fp()
        m = re.search(r"AI-register words: (\d+) hits", rendered)
        self.assertIsNotNone(m)
        self.assertEqual(int(m.group(1)), 0)
        # And it is genuinely zero in the corpus, not just asserted in prose.
        self.assertEqual(fp["ai_register"]["total_hits"], 0)

    def test_provenance_present_on_every_measured_block(self):
        # A number with no provenance is worse than no number: the rendered block
        # must state genre, N, and confidence.
        rendered, _ = self._profile_and_fp()
        self.assertRegex(rendered, r"genre=blog")
        self.assertRegex(rendered, r"N=3 samples")
        self.assertRegex(rendered, r"confidence=(Low|Medium|High|Insufficient)")


if __name__ == "__main__":
    unittest.main()
