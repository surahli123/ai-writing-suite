"""Unit tests for the mechanical detector. Run: python3 -m unittest discover.

Mirrors the coverage of the original avoid-ai `patterns.test.js`:
  - AI-heavy text scores high (pattern coverage didn't regress)
  - plain human prose scores low (no false-positive drift)
  - length gates fire (empty / too-short / too-long)
  - individual category detectors hit their canonical example
  - the trinary classifier is FN-biased (human prose never reads AI_ONLY)
"""

import unittest

from detector.detector import analyze


class LengthGates(unittest.TestCase):
    def test_empty(self):
        r = analyze("")
        self.assertEqual(r["label"], "Empty")
        self.assertEqual(r["issues"], [])

    def test_too_short(self):
        r = analyze("Short unscorable text snippet.")
        self.assertTrue(r["tooShort"])
        self.assertEqual(r["label"], "Too short")

    def test_too_long(self):
        r = analyze("word " * 10001)
        self.assertTrue(r["tooLong"])
        self.assertEqual(r["label"], "Text too long")


class ScoreBands(unittest.TestCase):
    def test_ai_heavy_scores_high(self):
        text = (
            "In today's ever-evolving landscape, we delve into the intricate "
            "tapestry of innovation. This seamless, robust paradigm showcases a "
            "comprehensive framework. Moreover, it truly is a game-changer. "
            "Furthermore, this pivotal moment underscores how we navigate the "
            "complexities of modern AI."
        )
        r = analyze(text)
        self.assertGreaterEqual(r["score"], 60, f"got {r['score']}")
        self.assertIn(r["label"], ("Strong AI signals", "Heavy AI patterns"))

    def test_plain_human_prose_stays_low(self):
        text = (
            "The build broke again this morning. Rolled back the auth refactor "
            "and tests pass now. Still need to figure out why the token refresh "
            "path hits a 401 for users on Safari but not Firefox, probably a "
            "cookie scope issue but I want to confirm before shipping a fix."
        )
        r = analyze(text)
        self.assertLessEqual(r["score"], 20, f"got {r['score']}")


class CategoryDetectors(unittest.TestCase):
    """Each AI-tell category fires on its canonical example."""

    def _types(self, text, mode="general"):
        return {i["type"] for i in analyze(text, mode)["issues"]}

    def test_cutoff_disclaimer(self):
        text = ("As an AI language model, I cannot give a definitive take here. "
                "As of my last update I do not have access to real-time data on "
                "the topic you raised in this short message to me today.")
        self.assertIn("cutoff-disclaimer", self._types(text))

    def test_chatbot_artifact(self):
        text = ("Great question! I hope this helps you understand the topic. "
                "Feel free to reach out if you have any other questions today.")
        self.assertIn("chatbot", self._types(text))

    def test_vague_attribution(self):
        text = ("Experts believe the change is good and studies show it works. "
                "Research indicates the trend will continue for several years.")
        self.assertIn("vague-attribution", self._types(text))

    def test_placeholder_fingerprint(self):
        text = ("Dear [Recipient Name], thank you for your message regarding "
                "the project. Please review the attached document at your "
                "earliest convenience and reply. Best, [Your Name]")
        self.assertIn("ai-placeholder", self._types(text))

    def test_citation_markup_leak(self):
        text = ("The result is well documented citeturn0search0 and confirmed "
                "by several independent sources that looked into this matter "
                "carefully over the past year of public reporting.")
        self.assertIn("ai-citation-markup", self._types(text))

    def test_hashtag_stuffing(self):
        text = ("Big launch today, so proud of the team and the work we did. "
                "#startup #growth #innovation #tech #founder #buildinpublic #ai")
        self.assertIn("hashtag-stuff", self._types(text))

    def test_title_case_header_general_mode(self):
        text = ("Strategic Negotiations And Key Partnerships\n\n"
                "We worked hard this quarter to close several deals with new "
                "customers and partners across the region and beyond as planned.")
        self.assertIn("title-case-header", self._types(text, "general"))

    def test_title_case_header_skipped_in_technical_mode(self):
        text = ("Strategic Negotiations And Key Partnerships\n\n"
                "We worked hard this quarter to close several deals with new "
                "customers and partners across the region and beyond as planned.")
        self.assertNotIn("title-case-header", self._types(text, "technical"))

    def test_tier2_cluster_requires_two(self):
        # One tier-2 word alone should not flag; two in a paragraph should.
        one = ("We harness the data to make a decision about the next release "
               "and ship it to customers before the end of this current month.")
        two = ("We harness the data and foster a culture that helps the team "
               "ship faster to customers before the end of this current month.")
        self.assertNotIn("tier2", self._types(one))
        self.assertIn("tier2", self._types(two))


class TrinaryClassifier(unittest.TestCase):
    def test_human_prose_never_ai_only(self):
        text = ("The build broke again this morning. Rolled back the auth "
                "refactor and tests pass now. Still need to figure out the 401.")
        r = analyze(text)
        self.assertNotEqual(r["classification"], "AI_ONLY")

    def test_cutoff_disclaimer_forces_ai_only(self):
        text = ("As an AI language model, I cannot provide legal advice, but I "
                "can offer some general thoughts on the question you have asked "
                "me here today in this fairly short message you sent over.")
        r = analyze(text)
        self.assertEqual(r["classification"], "AI_ONLY")
        self.assertEqual(r["confidence"], "high")


class ScoringMath(unittest.TestCase):
    def test_dedup_counts_distinct_signals(self):
        # Same phrase three times should produce ONE deduped issue, not three.
        text = ("Moreover, the plan works. Moreover, the plan works. Moreover, "
                "the plan works well and the team is happy with it overall now.")
        r = analyze(text)
        transitions = [i for i in r["issues"] if i["type"] == "transition"]
        self.assertEqual(len(transitions), 1)


if __name__ == "__main__":
    unittest.main()
