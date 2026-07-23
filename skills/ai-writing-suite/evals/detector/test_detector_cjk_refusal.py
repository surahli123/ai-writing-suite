"""Regression tests for the detector's CJK refusal seam."""

import unittest

from detector.detector import analyze


class CjkRefusal(unittest.TestCase):
    def test_cjk_dominant_text_is_unsupported_before_scoring(self):
        for text in ("界abcd", "界abcd " * 10):
            with self.subTest(text=text):
                result = analyze(text)

                self.assertIsNone(result["score"])
                self.assertEqual(result["label"], "Unsupported script")
                self.assertEqual(result["classification"], "UNSUPPORTED")
                self.assertNotEqual(result["classification"], "HUMAN_ONLY")
                self.assertEqual(result["stats"]["scriptClass"], "CJK")

    def test_latin_text_result_is_unchanged(self):
        text = (
            "The build broke again this morning. Rolled back the auth refactor "
            "and tests pass now. Still need to figure out why the token refresh "
            "path hits a 401 for users on Safari but not Firefox, probably a "
            "cookie scope issue but I want to confirm before shipping a fix."
        )

        self.assertEqual(
            analyze(text),
            {
                "score": 0,
                "label": "Clean",
                "issues": [],
                "stats": {
                    "wordCount": 49,
                    "contextMode": "general",
                    "tier1Count": 0,
                    "tier2Count": 0,
                    "tier2Clusters": 0,
                    "tier3Count": 0,
                    "patternCount": 0,
                },
                "classification": "HUMAN_ONLY",
                "confidence": "medium",
            },
        )


if __name__ == "__main__":
    unittest.main()
