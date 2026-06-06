"""Unit tests for the fixtures harness. Run: python3 -m unittest discover.

These tests assert the fixture SUITE is well-formed and stays calibrated:
  - every fixture has the required fields
  - detector scores land in the declared bands (so a fixture can't silently rot)
  - the naive-baseline miss rate stays in the 30-40% calibration band
  - the LLM-judge prompt builds for every fixture (the SKIP path is sound)
"""

import unittest

from detector.detector import analyze
from fixtures.run_fixtures import (
    load_fixtures, build_judge_prompt, _extract_judge_template)

REQUIRED = {"id", "genre", "difficulty", "before", "after",
            "rubric_focus", "expect_baseline"}


class FixtureShape(unittest.TestCase):
    def test_all_fixtures_have_required_fields(self):
        for f in load_fixtures()["fixtures"]:
            missing = REQUIRED - set(f)
            self.assertFalse(missing, f"{f.get('id')} missing {missing}")

    def test_four_genres_present(self):
        genres = {f["genre"] for f in load_fixtures()["fixtures"]}
        self.assertEqual(genres, {"tweet", "linkedin", "readme", "memo"})


class ScoreBands(unittest.TestCase):
    def test_before_after_scores_in_band(self):
        for f in load_fixtures()["fixtures"]:
            before = analyze(f["before"])["score"]
            after = analyze(f["after"])["score"]
            if "before_band_min" in f:
                self.assertGreaterEqual(before, f["before_band_min"],
                                        f"{f['id']} before={before}")
            if "before_band_max" in f:
                self.assertLessEqual(before, f["before_band_max"],
                                     f"{f['id']} before={before}")
            self.assertLessEqual(after, f["after_band_max"],
                                 f"{f['id']} after={after}")


class Calibration(unittest.TestCase):
    def test_naive_baseline_misses_30_to_40_percent(self):
        data = load_fixtures()
        thr = data["baseline_threshold"]
        miss = sum(1 for f in data["fixtures"]
                   if analyze(f["before"])["score"] < thr)
        total = len(data["fixtures"])
        pct = 100 * miss / total
        self.assertTrue(30 <= pct <= 40,
                        f"miss rate {pct:.0f}% outside 30-40% target")

    def test_expect_baseline_matches_actual(self):
        # The declared expect_baseline must match what the detector actually does.
        data = load_fixtures()
        thr = data["baseline_threshold"]
        for f in data["fixtures"]:
            caught = analyze(f["before"])["score"] >= thr
            expected = "catch" if caught else "miss"
            self.assertEqual(f["expect_baseline"], expected,
                             f"{f['id']}: declared {f['expect_baseline']} "
                             f"but detector would {expected}")


class JudgePrompt(unittest.TestCase):
    def test_prompt_builds_for_every_fixture(self):
        template = _extract_judge_template()
        self.assertIn("{before}", template)  # template has the slots
        for f in load_fixtures()["fixtures"]:
            prompt = build_judge_prompt(f, template)
            # All slots filled — no stray placeholders left.
            for slot in ("{before}", "{after}", "{genre}", "{rubric_focus}"):
                self.assertNotIn(slot, prompt, f"{f['id']} left {slot} unfilled")
            self.assertIn(f["before"], prompt)
            self.assertIn(f["after"], prompt)


if __name__ == "__main__":
    unittest.main()
