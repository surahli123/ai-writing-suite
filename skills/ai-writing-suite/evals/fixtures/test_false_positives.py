"""Unit tests for the adversarial false-positive suite.
Run: python3 -m unittest fixtures.test_false_positives

These tests assert the FP suite is well-formed, that it flags clean prose with
the SAME threshold the calibration suite uses (no silent drift), and — the
load-bearing one — that the checker can actually FAIL: a clean sample doctored
with obvious slop must be caught, and run() must return a nonzero fail count.
A guard that can never go red proves nothing.
"""

import copy
import io
import contextlib
import unittest

from detector.detector import analyze
from fixtures.run_false_positives import load_false_positives, run
from fixtures.run_fixtures import load_fixtures

REQUIRED = {"id", "role", "genre", "text"}
REQUIRED_CLEAN_FLAVORS = {"non-native", "terse-parataxis", "formal-academic",
                          "ordinary-professional"}
SUITE_GENRES = {"tweet", "linkedin", "readme", "memo"}


class Wellformed(unittest.TestCase):
    def test_required_fields_and_roles(self):
        for s in load_false_positives()["samples"]:
            missing = REQUIRED - set(s)
            self.assertFalse(missing, f"{s.get('id')} missing {missing}")
            self.assertIn(s["role"], ("clean", "control"),
                          f"{s['id']} bad role {s['role']!r}")

    def test_ids_unique(self):
        ids = [s["id"] for s in load_false_positives()["samples"]]
        self.assertEqual(len(ids), len(set(ids)), "duplicate sample id")

    def test_clean_and_control_counts_in_range(self):
        samples = load_false_positives()["samples"]
        clean = [s for s in samples if s["role"] == "clean"]
        control = [s for s in samples if s["role"] == "control"]
        self.assertTrue(8 <= len(clean) <= 12,
                        f"expected 8-12 clean samples, got {len(clean)}")
        self.assertTrue(1 <= len(control) <= 2,
                        f"expected 1-2 control samples, got {len(control)}")

    def test_clean_covers_required_flavors(self):
        # The motivating FP cases must all be present: non-native, the two
        # stylistically-unusual kinds, and ordinary professional prose.
        flavors = {s.get("flavor") for s in load_false_positives()["samples"]
                   if s["role"] == "clean"}
        missing = REQUIRED_CLEAN_FLAVORS - flavors
        self.assertFalse(missing, f"clean set missing flavors: {missing}")

    def test_clean_spans_all_suite_genres(self):
        genres = {s["genre"] for s in load_false_positives()["samples"]
                  if s["role"] == "clean"}
        self.assertTrue(SUITE_GENRES <= genres,
                        f"clean genres {genres} do not cover {SUITE_GENRES}")

    def test_multiple_non_native_samples(self):
        # The 60-70% FP stat is specifically about non-native writers, so the
        # suite must over-weight that flavor, not carry a token single sample.
        n = sum(1 for s in load_false_positives()["samples"]
                if s.get("flavor") == "non-native")
        self.assertGreaterEqual(n, 2, "need >= 2 non-native-flavored samples")


class ThresholdSourceConsistency(unittest.TestCase):
    def test_flag_threshold_matches_baseline_threshold(self):
        # The FP flag threshold and the calibration baseline threshold must be the
        # SAME notion of 'flagged'. If someone retunes baseline_threshold in
        # fixtures.json, this test forces false_positives.json to move with it
        # (or to consciously justify a divergence) instead of drifting silently.
        fp_thr = load_false_positives()["flag_threshold"]
        base_thr = load_fixtures()["baseline_threshold"]
        self.assertEqual(fp_thr, base_thr,
                         "false_positives.flag_threshold "
                         f"({fp_thr}) != fixtures.baseline_threshold ({base_thr})")


class LiveScoring(unittest.TestCase):
    """The same assertions run() makes, as first-class tests so a bad sample
    fails `unittest discover` too, not only the standalone runner."""

    def test_all_clean_below_threshold(self):
        data = load_false_positives()
        thr = data["flag_threshold"]
        for s in data["samples"]:
            if s["role"] == "clean":
                score = analyze(s["text"])["score"]
                self.assertLess(score, thr,
                                f"{s['id']} FALSE POSITIVE: score {score} >= {thr}")

    def test_all_controls_at_or_above_threshold(self):
        data = load_false_positives()
        thr = data["flag_threshold"]
        for s in data["samples"]:
            if s["role"] == "control":
                score = analyze(s["text"])["score"]
                self.assertGreaterEqual(
                    score, thr,
                    f"{s['id']} MISSED planted positive: score {score} < {thr}")

    def test_runner_passes_on_real_data(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            passes, fails = run(load_false_positives())
        self.assertEqual(fails, 0, f"live suite has {fails} failure(s)")
        self.assertGreater(passes, 0)


class CheckerCanFail(unittest.TestCase):
    """Regression-proof: prove the checker goes RED on a real false positive.
    Per the eval-calibration rule, a method that reports 'no false positives'
    is only trustworthy if it can detect a planted one."""

    SLOP = (" In today's ever-evolving landscape, we must leverage a robust, "
            "seamless, cutting-edge paradigm to delve into game-changing synergy.")

    def _first_clean(self, data):
        return next(s for s in data["samples"] if s["role"] == "clean")

    def test_doctored_clean_sample_now_trips_detector(self):
        # Append obvious AI vocabulary to a clean sample and confirm the detector
        # now scores it AT OR ABOVE threshold — i.e. a genuine false-positive
        # condition is detectable, not silently below the bar.
        data = load_false_positives()
        thr = data["flag_threshold"]
        clean = self._first_clean(data)
        self.assertLess(analyze(clean["text"])["score"], thr)  # clean as-is
        doctored = analyze(clean["text"] + self.SLOP)["score"]
        self.assertGreaterEqual(
            doctored, thr,
            "doctored clean+slop sample did NOT trip — checker cannot detect a "
            "false positive, so a green run proves nothing")

    def test_run_returns_nonzero_fails_when_a_clean_sample_is_poisoned(self):
        # Feed run() a dataset whose first clean sample has been poisoned with
        # slop; run() must count it as a failure (the nonzero exit CI relies on).
        data = copy.deepcopy(load_false_positives())
        clean = self._first_clean(data)
        clean["text"] = clean["text"] + self.SLOP
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _passes, fails = run(data)
        self.assertGreaterEqual(fails, 1,
                                "run() did not fail on a poisoned clean sample")

    def test_run_returns_nonzero_fails_when_a_control_is_declawed(self):
        # The mirror direction: if a control stops looking like slop (replaced by
        # plain prose), run() must fail because the planted positive was missed.
        data = copy.deepcopy(load_false_positives())
        control = next(s for s in data["samples"] if s["role"] == "control")
        control["text"] = ("We moved the standup to Thursday and updated the "
                            "shared calendar so everyone can plan around it.")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _passes, fails = run(data)
        self.assertGreaterEqual(fails, 1,
                                "run() did not fail when a control stopped tripping")


if __name__ == "__main__":
    unittest.main()
