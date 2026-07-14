"""Unit tests for _shared/stylometry.py — the quantitative voice fingerprint.

Stdlib-only (unittest). Discovered by run_all.sh step 1 and by
`python3 -m unittest discover -p 'test_*.py'` from the evals/ dir.

Coverage:
  - known-input -> known-output (hand-derived, not self-referential)
  - per-genre isolation: pooling two genres yields a detectably WRONG answer
  - thin-N confidence behavior (the 3-sample floor)
  - the CJK path (unsupported marker, never garbage numbers)

The module lives in _shared/ (suite root), so we add that dir to sys.path the
same way voice-onboard resolves _shared/ by suite-root-relative path.
"""

import math
import os
import sys
import unittest

_SHARED = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "_shared")
sys.path.insert(0, _SHARED)

import stylometry as S  # noqa: E402


class KnownInputKnownOutput(unittest.TestCase):
    """Each expected value is derived by hand, not read back from the module."""

    def test_sentence_length_stats(self):
        # "One two three." = 3 words; "Four five." = 2 words. n=2.
        # mean = 2.5; pop variance = ((3-2.5)^2 + (2-2.5)^2)/2 = 0.25, which the
        # module rounds to 1 decimal -> 0.2 (round-half-to-even); stdev = 0.5;
        # cv = 0.5/2.5 = 0.2.
        st = S.sentence_length_stats("One two three. Four five.")
        self.assertEqual(st["n_sentences"], 2)
        self.assertEqual(st["mean"], 2.5)
        self.assertEqual(st["variance"], 0.2)
        self.assertEqual(st["stdev"], 0.5)
        self.assertEqual(st["burstiness_cv"], 0.2)

    def test_single_sentence_has_zero_variance(self):
        st = S.sentence_length_stats("Just one sentence here now.")
        self.assertEqual(st["n_sentences"], 1)
        self.assertEqual(st["variance"], 0.0)

    def test_testable_number_density(self):
        # 7 words, 2 figures (3, 2) -> 2/7*100 = 28.57 -> 28.6
        tn = S.testable_number_density("I have 3 cats and 2 dogs")
        self.assertEqual(tn["count"], 2)
        self.assertEqual(tn["per_100_words"], 28.6)

    def test_testable_number_ignores_spelled_out(self):
        # "two" is a word, not a testable figure; only "12%" and "40" count.
        tn = S.testable_number_density("two teams shipped 12% faster over 40 days")
        self.assertEqual(tn["count"], 2)

    def test_ai_register_absence_and_hits(self):
        clean = S.ai_register_absences("We shipped it. It was fast. Nobody noticed.")
        self.assertEqual(clean["total_hits"], 0)
        self.assertEqual(clean["offenders"], {})
        dirty = S.ai_register_absences(
            "We must delve into this and leverage a treasure trove.")
        self.assertEqual(dirty["offenders"].get("delve"), 1)
        self.assertEqual(dirty["offenders"].get("leverage"), 1)
        self.assertEqual(dirty["offenders"].get("treasure trove"), 1)
        self.assertEqual(dirty["total_hits"], 3)

    def test_punctuation_density(self):
        # 4 words -> scale = 1000/4 = 250 per hit.
        pd = S.punctuation_density("a — b; c! d...")
        self.assertEqual(pd["em_dash"], 250.0)
        self.assertEqual(pd["semicolon"], 250.0)
        self.assertEqual(pd["exclamation"], 250.0)
        self.assertEqual(pd["ellipsis"], 250.0)

    def test_function_word_delta(self):
        # "the the the" -> 3/3*1000 = 1000/1k; baseline the=50 -> delta 950.
        fw = S.function_word_deltas("the the the")
        self.assertEqual(fw["the"]["text_rate"], 1000.0)
        self.assertEqual(fw["the"]["baseline_rate"], 50.0)
        self.assertEqual(fw["the"]["delta"], 950.0)


class PerGenreIsolation(unittest.TestCase):
    """The HARD constraint: pooling two genres must yield a wrong answer."""

    TWEETS = [
        "Shipped it. 3 lines. Done.",
        "Hot take: fewer metrics, more decisions.",
        "Rewrote the ranker. NDCG up 2 points. Ship.",
    ]
    REPORTS = [
        ("In this analysis we examine the reranking model across the full query "
         "distribution and we find that the observed improvement is concentrated "
         "in the head while the long tail shows no meaningful movement over the "
         "window we measured for this particular release cycle."),
        ("The latency regression which reached the ninety ninth percentile was "
         "traced to an unbatched feature lookup and after we restored batching "
         "the regression fell to a level the team considered acceptable for the "
         "current production release under review."),
        ("We recommend that the model be promoted to the primary ranking path "
         "only after the tail evaluation is repeated on a cleaner sample because "
         "the current holdout likely overstates the improvement that real "
         "production traffic would actually realize in steady state."),
    ]

    def test_pooling_changes_the_answer(self):
        per = S.compute_per_genre({"tweet": self.TWEETS, "report": self.REPORTS})
        tweet_v = per["tweet"]["sentence_length"]["variance"]
        report_v = per["report"]["sentence_length"]["variance"]
        tweet_m = per["tweet"]["sentence_length"]["mean"]
        report_m = per["report"]["sentence_length"]["mean"]

        pooled = S.compute_fingerprint(self.TWEETS + self.REPORTS, genre="pooled")
        pooled_v = pooled["sentence_length"]["variance"]
        pooled_m = pooled["sentence_length"]["mean"]

        # The two genres have very different means (short tweets vs long reports).
        self.assertGreater(report_m, tweet_m * 3)

        # Pooled mean describes NEITHER genre: it lands strictly between them.
        self.assertGreater(pooled_m, tweet_m)
        self.assertLess(pooled_m, report_m)

        # Pooled variance is inflated by the cross-genre gap far beyond either
        # genre's own variance — a "burstiness" that exists in no single genre.
        self.assertGreater(pooled_v, 2 * max(tweet_v, report_v))

    def test_compute_per_genre_never_pools(self):
        # Two genres in -> two independent fingerprints out, each with its own N.
        out = S.compute_per_genre({"a": self.TWEETS, "b": self.REPORTS})
        self.assertEqual(set(out), {"a", "b"})
        self.assertEqual(out["a"]["sample_count"], 3)
        self.assertEqual(out["b"]["sample_count"], 3)
        # A pooled run would report N=6; per-genre must never do that.
        self.assertNotEqual(out["a"]["sample_count"], 6)


class ThinNConfidence(unittest.TestCase):
    def test_below_floor_is_insufficient_and_warns(self):
        fp = S.compute_fingerprint(["One line.", "Two line."], genre="x")
        self.assertEqual(fp["sample_count"], 2)
        self.assertTrue(fp["confidence"].startswith("Insufficient"))
        self.assertIn("warning", fp)
        self.assertIn("below", fp["warning"])

    def test_at_floor_is_low_no_warning(self):
        fp = S.compute_fingerprint(["a b c.", "d e f.", "g h i."], genre="x")
        self.assertEqual(fp["confidence"], "Low")
        self.assertNotIn("warning", fp)

    def test_confidence_bands(self):
        self.assertEqual(S.confidence_label(2), "Insufficient (N<3)")
        self.assertEqual(S.confidence_label(3), "Low")
        self.assertEqual(S.confidence_label(7), "Medium")
        self.assertEqual(S.confidence_label(15), "High")


class CJKPath(unittest.TestCase):
    ZH = [
        "这是一个中文写作样本用来测试系统能否诚实处理中文",
        "数据科学团队每天都在写报告和沟通",
        "我们需要一个真正好用的写作助手工具",
    ]

    def test_cjk_returns_unsupported_not_garbage(self):
        fp = S.compute_fingerprint(self.ZH, genre="blog-zh")
        self.assertFalse(fp["supported"])
        self.assertEqual(fp["script"], "CJK")
        # Crucially: NO numeric fingerprint keys are present (no garbage numbers).
        self.assertNotIn("sentence_length", fp)
        self.assertNotIn("testable_number_density", fp)
        self.assertIn("note", fp)

    def test_detector_flags_cjk_dominant(self):
        self.assertTrue(S.is_cjk_dominant("".join(self.ZH)))
        self.assertFalse(S.is_cjk_dominant("plain english only, no cjk here"))

    def test_format_renders_unsupported_line(self):
        fp = S.compute_fingerprint(self.ZH, genre="blog-zh")
        rendered = S.format_fingerprint(fp)
        self.assertIn("UNSUPPORTED", rendered)


if __name__ == "__main__":
    unittest.main()
