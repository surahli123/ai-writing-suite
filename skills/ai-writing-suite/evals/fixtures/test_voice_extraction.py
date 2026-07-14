"""Tests for the voice-onboard extraction eval (fixtures/run_voice_extraction.py).

Three things are under test, in rising order of importance:

  1. The counting primitives — word boundaries and case. The whole fixture rests on
     "ledger appears exactly 4x, delve exactly 0x". If counting is loose, the 3+ rule
     and the absence signal are both fiction.
  2. The fixture's own ground truth — declared counts must equal recomputed counts.
  3. The GATE: the bad profile must trip every declared failure mode, and a run where
     the bad profile is swapped for a copy of the good one must EXIT 1. That last test
     is the point of the suite — it proves the checks can actually fail, so a green run
     means something.
"""

import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

from fixtures import run_voice_extraction as rve


class WordCounting(unittest.TestCase):
    def test_respects_word_boundaries(self):
        # The plural must not inflate the habit count — this is why the fixture
        # plants "ledgers" once.
        self.assertEqual(rve.count_word("ledger", "the ledger and two ledgers"), 1)

    def test_inflection_does_not_resurrect_an_absent_word(self):
        # "delved" must NOT count as "delve", or the strongest signal (a 0x word)
        # silently becomes a 1x word.
        self.assertEqual(rve.count_word("delve", "she delved into the data"), 0)
        self.assertEqual(rve.count_word("delve", "we delve into the data"), 1)

    def test_case_insensitive(self):
        self.assertEqual(rve.count_word("ledger", "Ledger. LEDGER? ledger!"), 3)

    def test_absent_word_counts_zero(self):
        self.assertEqual(rve.count_word("leverage", "no hype here"), 0)


class GroundTruth(unittest.TestCase):
    """Declared counts must survive recomputation from the sample text."""

    def setUp(self):
        self.corpus = rve.load_corpus()

    def test_declared_equals_recomputed(self):
        recomputed, errors = rve.verify_ground_truth(self.corpus)
        self.assertEqual(errors, [], f"fixture ground truth has drifted: {errors}")
        self.assertEqual(recomputed["ledger"], 4)        # habit: clears 3+
        self.assertEqual(recomputed["kaleidoscope"], 2)  # noise: fails 3+
        self.assertEqual(recomputed["delve"], 0)         # absence
        self.assertEqual(recomputed["leverage"], 0)      # absence
        self.assertEqual(recomputed["ledgers"], 1)       # boundary decoy

    def test_genres_have_genuinely_different_rhythm(self):
        recomputed, _ = rve.verify_ground_truth(self.corpus)
        means = recomputed["_genre_means"]
        self.assertLess(means["tweet"], means["memo"])
        self.assertGreaterEqual(
            recomputed["_genre_gap"],
            self.corpus["ground_truth"]["min_genre_mean_gap_words"],
            "genres too similar — 'don't average across genres' becomes untestable")

    def test_drifted_ground_truth_is_caught(self):
        # Planted positive for the drift guard itself: lie about the habit count.
        corpus = json.loads(json.dumps(self.corpus))
        corpus["ground_truth"]["habit_word"]["count"] = 9
        _, errors = rve.verify_ground_truth(corpus)
        self.assertTrue(any("GROUND TRUTH DRIFT" in e for e in errors))


class GoodProfilePasses(unittest.TestCase):
    def setUp(self):
        self.corpus = rve.load_corpus()
        self.md = rve.load_profile(rve.GOOD_PATH)

    def test_every_check_passes(self):
        for name, (ok, detail) in rve.run_checks(self.md, self.corpus).items():
            self.assertTrue(ok, f"good profile failed {name}: {detail}")


class BadProfileFailsEachDeclaredMode(unittest.TestCase):
    """One test per failure mode, so a broken check names itself."""

    def setUp(self):
        self.corpus = rve.load_corpus()
        self.md = rve.load_profile(rve.BAD_PATH)

    def _assert_trips(self, name):
        ok, detail = rve.CHECKS[name](self.md, self.corpus)
        self.assertFalse(ok, f"bad profile did NOT trip {name} — checker is broken "
                             f"({detail})")

    def test_misses_the_4x_habit_word(self):
        self._assert_trips("learns_habit_word")

    def test_learns_the_2x_noise_word(self):
        self._assert_trips("omits_noise_word")

    def test_fails_to_mine_the_absences(self):
        self._assert_trips("lists_absence")

    def test_averages_across_genres(self):
        self._assert_trips("splits_genres")

    def test_invents_an_unsupported_trait(self):
        self._assert_trips("no_invented_traits")

    def test_fills_every_gap_confidently(self):
        self._assert_trips("honest_gap")

    def test_still_satisfies_the_header_contract(self):
        # It must be wrong on CONTENT only. If it broke a header,
        # test_voice_contract.py would already catch it and this suite would add
        # nothing.
        ok, detail = rve.CHECKS["headers_present"](self.md, self.corpus)
        self.assertTrue(ok, f"bad profile broke the header contract: {detail}")


class MainGate(unittest.TestCase):
    """The gate: main() must exit nonzero when the suite can no longer discriminate."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def _run_main(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = rve.main([])
        return rc, buf.getvalue()

    def test_shipped_fixtures_pass(self):
        rc, _ = self._run_main()
        self.assertEqual(rc, 0)

    def test_doctored_run_with_two_good_profiles_fails(self):
        # Replace the bad profile with a copy of the good one. Nothing trips, so the
        # suite proves nothing — and must go red rather than green.
        fake_bad = os.path.join(self.tmp, "voice_profile_bad.md")
        shutil.copyfile(rve.GOOD_PATH, fake_bad)
        with mock.patch.object(rve, "BAD_PATH", fake_bad):
            rc, out = self._run_main()
        self.assertEqual(rc, 1, "a non-discriminating run must FAIL")
        self.assertIn("DID NOT TRIP", out)

    def test_empty_corpus_fails(self):
        empty = os.path.join(self.tmp, "empty.json")
        corpus = rve.load_corpus()
        corpus["samples"] = []
        with open(empty, "w", encoding="utf-8") as fh:
            json.dump(corpus, fh)
        with mock.patch.object(rve, "CORPUS_PATH", empty):
            rc, out = self._run_main()
        self.assertEqual(rc, 1)
        self.assertIn("empty corpus", out)

    def test_missing_artifact_fails(self):
        with mock.patch.object(rve, "BAD_PATH",
                               os.path.join(self.tmp, "does-not-exist.md")):
            rc, out = self._run_main()
        self.assertEqual(rc, 1)
        self.assertIn("missing fixture artifact", out)


if __name__ == "__main__":
    unittest.main()
