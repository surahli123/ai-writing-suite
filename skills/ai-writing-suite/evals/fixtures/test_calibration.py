"""Tests for the miss-target calibration table (fixtures/calibration.py).

Two jobs:
  - the pure arithmetic is correct (known sizes, the n=8 knife-edge, the
    uncalibratable sizes, inclusive band edges), and
  - the table AGREES with the live fixtures.json — so the table's notion of "in
    band" can't drift from what run_fixtures actually asserts.
"""

import unittest

from detector.detector import analyze
from fixtures.calibration import (
    BAND_LO, BAND_HI, valid_miss_counts, miss_target)
from fixtures.run_fixtures import load_fixtures


class MissCountArithmetic(unittest.TestCase):
    def test_n8_knife_edge(self):
        # Current suite size: only 3 misses (37.5%) is in band; 2 and 4 fail.
        self.assertEqual(valid_miss_counts(8), [3])
        self.assertEqual(miss_target(8), 3)

    def test_band_edges_are_inclusive(self):
        # 30% and 40% are both IN band (the live assert uses <= on both ends).
        # n=10 is the clean case where both edges land on integers.
        self.assertEqual(valid_miss_counts(10), [3, 4])  # 30% and 40%

    def test_uncalibratable_sizes_return_empty(self):
        # No integer miss count lands in [0.3n, 0.4n] for these sizes.
        self.assertEqual(valid_miss_counts(4), [])   # band [1.2, 1.6]
        self.assertIsNone(miss_target(4))

    def test_target_for_planned_2b_size(self):
        # The planned ~24-item 2b set: 8 (33.3%) and 9 (37.5%) are valid.
        # target = 8 — 33.3% is closer to the 35% midpoint than 37.5%.
        self.assertEqual(valid_miss_counts(24), [8, 9])
        self.assertEqual(miss_target(24), 8)

    def test_target_maximizes_edge_margin(self):
        # n=20 band is [6, 8] -> 30/35/40%; the exact-midpoint option (7) wins.
        self.assertEqual(miss_target(20), 7)


class AgreesWithLiveFixtures(unittest.TestCase):
    def test_live_suite_miss_count_is_in_table_band(self):
        # Compute (miss, total) EXACTLY as run_fixtures.run_deterministic does,
        # then assert the table calls that miss count valid. Fails if the live
        # fixtures drift out of band, OR if BAND_LO/HI here stop matching the
        # live 30-40 assert — catching drift from either side. `detector_blind`
        # (judge-only) fixtures are excluded from the denominator here too, to
        # match run_deterministic and the Calibration unit test.
        data = load_fixtures()
        thr = data["baseline_threshold"]
        targeted = [f for f in data["fixtures"] if not f.get("detector_blind")]
        total = len(targeted)
        miss = sum(1 for f in targeted
                   if analyze(f["before"])["score"] < thr)
        self.assertIn(miss, valid_miss_counts(total),
                      f"live suite {miss}/{total} not in band per table")

    def test_band_constants_are_the_documented_30_40(self):
        self.assertEqual((BAND_LO, BAND_HI), (30, 40))


if __name__ == "__main__":
    unittest.main()
