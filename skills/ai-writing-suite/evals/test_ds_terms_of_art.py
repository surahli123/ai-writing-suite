"""DS terms of art must not trip the vocabulary tiers; marketing uses still must.

Each row is a pair. The `protect` sentence uses the word as a literal technical
term and must NOT report it. The `recall` sentence uses it as slop and MUST
report it. A mutant check proves the masking is load-bearing: with masking
disabled, every protect sentence flags again.
"""
import unittest
from unittest import mock

from detector import patterns as P
from detector.detector import analyze

ROWS = [
    # (word as reported, protect sentence, recall sentence)
    ("robust",
     "We report heteroskedasticity-robust standard errors and a robust regression as a sensitivity check for the main estimate.",
     "Our robust platform gives every team a smooth way to work together on the projects that matter most."),
    ("robust",
     "The median is robust to outliers, so we kept it as the headline metric for the weekly report to finance.",
     "We built a robust solution that brings your data, people and plans together in one simple place."),
    ("leverage",
     "Four observations had high leverage, and dropping them moved the coefficient from 0.42 to 0.39 overall.",
     "Teams can leverage our new dashboard to make faster decisions about pricing, staffing and inventory."),
    ("leverage",
     "Leverage scores flagged twelve rows from one merchant, so we checked those rows by hand before refitting.",
     "We will leverage these insights to drive growth across every region in the coming quarter and beyond."),
    ("landscape",
     "The loss landscape was flat near the optimum, so we report the cross-validated estimate rather than one run.",
     "The data landscape is changing fast, and every team needs to keep up with new tools and new rules."),
]


def reported(text):
    return {i["text"].lower() for i in analyze(text)["issues"] if i["type"] in ("tier1", "tier2", "tier3")}


class TermsOfArt(unittest.TestCase):
    def test_literal_technical_use_is_not_flagged(self):
        for word, protect, _ in ROWS:
            with self.subTest(word=word, sentence=protect):
                self.assertNotIn(word, reported(protect))

    def test_marketing_use_is_still_flagged(self):
        for word, _, recall in ROWS:
            with self.subTest(word=word, sentence=recall):
                self.assertIn(word, reported(recall))

    def test_masking_is_load_bearing(self):
        # Mutant: disable masking; every protect row must flag again, or the
        # protect rows were never testing the mechanism.
        with mock.patch.object(P, "mask_terms_of_art", lambda t: t):
            for word, protect, _ in ROWS:
                with self.subTest(word=word):
                    self.assertIn(word, reported(protect))

    def test_masking_preserves_word_count(self):
        for _, protect, recall in ROWS:
            for s in (protect, recall):
                self.assertEqual(len(P.mask_terms_of_art(s).split()), len(s.split()))


if __name__ == "__main__":
    unittest.main()
