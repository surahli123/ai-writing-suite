"""Tests for the voice-onboard extraction eval (fixtures/run_voice_extraction.py).

Four things are under test, in rising order of importance:

  1. The counting primitives — word boundaries and case. The whole fixture rests on
     "ledger appears exactly 4x IN TWEETS, delve exactly 0x". If counting is loose,
     the 3+ rule and the absence signal are both fiction.
  2. The fixture's own ground truth — declared counts must equal counts recomputed
     WITHIN each genre, and the cross-genre trap must still hold.
  3. The GATE: each genre's bad profile must trip every declared failure mode, and a
     run where a bad profile is swapped for a copy of the good one must EXIT 1.
  4. The MUTANT FAMILIES: the checkers must catch artifacts they have never seen,
     drawn programmatically from the same failure mode, at or above a declared floor.
     This is what stops a checker from passing by memorizing one exemplar — the
     failure class behind every finding in review.

Genre scoping is not a detail here. voice-onboard/SKILL.md Step 2 says "Don't average
across genres", so the fixture ships one profile PER GENRE and every count is
recomputed within a genre. The previous corpus pooled genres to reach its declared
"ledger 4x" (tweet=3 + memo=1) — the very error the eval exists to detect.
"""

import io
import json
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

from fixtures import mutants_voice as mv
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

    def test_names_genre_accepts_the_plural(self):
        # A profile writes "applies to her tweets", never "her tweet".
        self.assertTrue(rve.names_genre("Applies to: her tweets.", "tweet"))
        self.assertFalse(rve.names_genre("Applies to: her tweets.", "memo"))


class GroundTruth(unittest.TestCase):
    """Declared counts must survive recomputation WITHIN their genre."""

    def setUp(self):
        self.corpus = rve.load_corpus()

    def test_declared_equals_recomputed_per_genre(self):
        recomputed, errors = rve.verify_ground_truth(self.corpus)
        self.assertEqual(errors, [], f"fixture ground truth has drifted: {errors}")
        tweet, memo = recomputed["genres"]["tweet"], recomputed["genres"]["memo"]
        self.assertEqual(tweet["ledger"], 4)        # habit: clears 3+ WITHIN tweets
        self.assertEqual(tweet["kaleidoscope"], 2)  # noise: fails 3+ WITHIN tweets
        self.assertEqual(tweet["forecast"], 1)      # sub-threshold decoy
        self.assertEqual(tweet["queue"], 0)         # the memo genre's habit word
        self.assertEqual(tweet["ledgers"], 1)       # boundary decoy
        self.assertEqual(memo["queue"], 4)          # habit: clears 3+ WITHIN memos
        self.assertEqual(memo["kaleidoscope"], 2)   # noise WITHIN memos too
        self.assertEqual(memo["boring"], 2)         # sub-threshold decoy
        self.assertEqual(memo["ledger"], 0)         # the tweet genre's habit word
        for genre in ("tweet", "memo"):
            self.assertEqual(recomputed["genres"][genre]["delve"], 0)
            self.assertEqual(recomputed["genres"][genre]["leverage"], 0)

    def test_the_cross_genre_trap_holds(self):
        # Noise in EACH genre, habit-shaped when POOLED. That is what makes cross-genre
        # aggregation detectably wrong rather than merely untidy.
        recomputed, _ = rve.verify_ground_truth(self.corpus)
        bar = self.corpus["ground_truth"]["min_habit_occurrences"]
        word = self.corpus["ground_truth"]["cross_genre_trap"]["word"]
        self.assertGreaterEqual(recomputed["_pooled_trap"], bar)
        for genre in rve.genres_of(self.corpus):
            self.assertLess(
                rve.count_word(word, rve.corpus_text(self.corpus, genre)), bar,
                f"'{word}' is a real habit in {genre} — the trap is void")

    def test_habit_word_does_not_clear_the_bar_by_luck_of_aggregation(self):
        # The defect that started this rewrite: the old fixture declared 'ledger' 4x,
        # which was tweet=3 + memo=1 — a pooled count. Each habit word must now clear
        # the bar INSIDE its own genre, with nothing borrowed from the other.
        gt = self.corpus["ground_truth"]
        for genre, spec in gt["genres"].items():
            within = rve.count_word(spec["habit_word"]["word"],
                                    rve.corpus_text(self.corpus, genre))
            self.assertGreaterEqual(within, gt["min_habit_occurrences"])

    def test_genres_have_genuinely_different_rhythm(self):
        recomputed, _ = rve.verify_ground_truth(self.corpus)
        means = {g: recomputed["genres"][g]["_mean"] for g in ("tweet", "memo")}
        self.assertLess(means["tweet"], means["memo"])
        self.assertGreaterEqual(
            recomputed["_genre_gap"],
            self.corpus["ground_truth"]["min_genre_mean_gap_words"],
            "genres too similar — 'don't average across genres' becomes untestable")

    def test_drifted_ground_truth_is_caught(self):
        # Planted positive for the drift guard itself: lie about the habit count.
        corpus = json.loads(json.dumps(self.corpus))
        corpus["ground_truth"]["genres"]["tweet"]["habit_word"]["count"] = 9
        _, errors = rve.verify_ground_truth(corpus)
        self.assertTrue(any("GROUND TRUTH DRIFT" in e for e in errors))

    def test_undeclared_expected_unknown_sections_is_a_fixture_error(self):
        corpus = json.loads(json.dumps(self.corpus))
        corpus["ground_truth"]["genres"]["tweet"]["expected_unknown_sections"] = []
        _, errors = rve.verify_ground_truth(corpus)
        self.assertTrue(any("expected_unknown_sections" in e for e in errors))


class GoodProfilesPass(unittest.TestCase):
    def setUp(self):
        self.corpus = rve.load_corpus()

    def test_every_check_passes_for_every_genre(self):
        for genre, good, _bad in rve.profile_pairs(self.corpus):
            md = rve.load_profile(good)
            for name, (ok, detail) in rve.run_checks(md, self.corpus, genre).items():
                self.assertTrue(ok, f"[{genre}] good profile failed {name}: {detail}")

    def test_good_profiles_are_genre_scoped_not_blended(self):
        # The construct under test: the GOLD artifact must not itself be the failure
        # mode. SKILL.md Step 1 — "Mixed genres → offer to extract two profiles rather
        # than averaging them into a blur." The previous gold profile was one blended
        # profile over a mixed corpus, which is that failure.
        pairs = rve.profile_pairs(self.corpus)
        self.assertEqual(len(pairs), len(rve.genres_of(self.corpus)))
        for genre, good, _bad in pairs:
            ok, detail = rve.CHECKS["scope_declared"](
                rve.load_profile(good), self.corpus, genre)
            self.assertTrue(ok, detail)

    def test_good_profiles_claim_nothing_under_the_3x_bar(self):
        # The other half of that defect: the old gold profile claimed "forecast" (2x)
        # and "boring" (1x) as positive traits, under a spec whose 3+ rule is absolute.
        for genre, good, _bad in rve.profile_pairs(self.corpus):
            md = rve.load_profile(good)
            text = rve.corpus_text(self.corpus, genre)
            for term in rve.quoted_terms(md):
                self.assertGreaterEqual(
                    rve.count_word(term, text), 3,
                    f"[{genre}] good profile claims '{term}' with "
                    f"{rve.count_word(term, text)} occurrences — under the 3+ bar")


class BadProfilesFailEachDeclaredMode(unittest.TestCase):
    """One assertion per failure mode per genre, so a broken check names itself."""

    def setUp(self):
        self.corpus = rve.load_corpus()

    def _assert_trips(self, name):
        for genre, _good, bad in rve.profile_pairs(self.corpus):
            ok, detail = rve.CHECKS[name](rve.load_profile(bad), self.corpus, genre)
            self.assertFalse(ok, f"[{genre}] bad profile did NOT trip {name} — checker "
                                 f"is broken ({detail})")

    def test_misses_the_habit_word(self):
        self._assert_trips("learns_habit_word")

    def test_learns_the_noise_word(self):
        self._assert_trips("omits_noise_word")

    def test_claims_a_subthreshold_word(self):
        self._assert_trips("no_subthreshold_claims")

    def test_fails_to_mine_the_absences(self):
        self._assert_trips("lists_absence")

    def test_reports_the_blended_rhythm(self):
        self._assert_trips("genre_scoped_rhythm")

    def test_invents_an_unsupported_trait(self):
        self._assert_trips("no_invented_traits")

    def test_fills_every_gap_confidently(self):
        self._assert_trips("honest_gap")

    def test_claims_to_cover_every_genre(self):
        self._assert_trips("scope_declared")

    def test_still_satisfies_the_header_contract(self):
        # It must be wrong on CONTENT only. If it broke a header, test_voice_contract.py
        # would already catch it and this suite would add nothing.
        for genre, _good, bad in rve.profile_pairs(self.corpus):
            ok, detail = rve.CHECKS["headers_present"](
                rve.load_profile(bad), self.corpus, genre)
            self.assertTrue(ok, f"[{genre}] bad profile broke the header contract: {detail}")


class ReviewerEvasions(unittest.TestCase):
    """Regression tests for the evasions a reviewer constructed against v1 of these
    checkers — profiles wrong in the exact way the check names that still sailed
    through, plus the mirror false positives where a CORRECT profile was flagged.
    Deleting a test here re-opens the hole it names.
    """

    def setUp(self):
        self.corpus = rve.load_corpus()
        self.pairs = rve.profile_pairs(self.corpus)

    def _each_genre(self):
        for genre, good, _bad in self.pairs:
            yield (genre, rve.load_profile(good),
                   self.corpus["ground_truth"]["genres"][genre])

    # --- MAJOR 1: the genre-averaging check was a string hack ------------------

    def test_averaged_profile_is_caught(self):
        # v1 passed if the genre NAMES appeared and >= 2 numerals appeared anywhere in
        # the section. A profile that says outright "one figure is enough" satisfied both.
        for genre, good, spec in self._each_genre():
            mid, md = mv.family_genre_scoped_rhythm(good, spec, self.corpus, genre)[1]
            self.assertEqual(mid, "rhythm/both-genres-alike")
            body = rve.parse_sections(md)["Sentence Length"]
            self.assertTrue(all(rve.count_word(g, body)
                                for g in rve.genres_of(self.corpus)),
                            "the evasion must still NAME both genres — that is why v1 passed it")
            self.assertGreaterEqual(len({float(n) for n in re.findall(r"\d+", body)}), 2)
            ok, detail = rve.CHECKS["genre_scoped_rhythm"](md, self.corpus, genre)
            self.assertFalse(ok, f"[{genre}] an explicitly AVERAGED profile passed")
            self.assertIn("BLENDED", detail)

    def test_genre_collapse_without_the_telltale_words_is_caught(self):
        # The hard mutant: no "average", no "both", no genre name — nothing lexical to
        # key on. Only comparing the figure against the recomputed means catches it.
        for genre, good, spec in self._each_genre():
            mid, md = mv.family_genre_scoped_rhythm(good, spec, self.corpus, genre)[2]
            self.assertEqual(mid, "rhythm/hard-no-keywords")
            body = rve.parse_sections(md)["Sentence Length"].lower()
            self.assertNotIn("average", body)
            self.assertNotIn("both", body)
            ok, _ = rve.CHECKS["genre_scoped_rhythm"](md, self.corpus, genre)
            self.assertFalse(ok, f"[{genre}] keyword-free genre collapse escaped")

    # --- MAJOR 2: habit / noise checks were direction-blind --------------------

    def test_inverted_habit_claim_is_caught(self):
        # v1 asked "does this string appear anywhere in the file", so a profile could
        # assert the INVERSE of the corpus and score as having learned the habit.
        for genre, good, spec in self._each_genre():
            mid, md = mv.family_learns_habit_word(good, spec, self.corpus, genre)[2]
            self.assertEqual(mid, "habit/inverse-never-writes")
            habit = spec["habit_word"]["word"]
            self.assertTrue(rve.profile_mentions(habit, md),
                            "the word must still be IN the file — that is the trick")
            ok, detail = rve.CHECKS["learns_habit_word"](md, self.corpus, genre)
            self.assertFalse(ok, f"[{genre}] a profile claiming the INVERSE scored as "
                                 f"having learned the habit")
            self.assertIn("INVERSE", detail)

    def test_correct_profile_noting_noise_word_in_avoid_section_is_not_flagged(self):
        # The mirror false positive: naming the 2x accident under Things To Avoid, in
        # order to dismiss it, is correct extraction — not learning it.
        for genre, good, spec in self._each_genre():
            noise = spec["noise_word"]["word"]
            md = mv.append_to_section(good, "Things To Avoid",
                                      f"\n- {noise} — 2x, do not treat as a habit.\n")
            self.assertTrue(rve.profile_mentions(noise, md))
            ok, detail = rve.CHECKS["omits_noise_word"](md, self.corpus, genre)
            self.assertTrue(ok, f"[{genre}] a CORRECT profile was flagged: {detail}")

    def test_noise_word_claimed_in_a_positive_section_still_trips(self):
        for genre, good, spec in self._each_genre():
            for _mid, md in mv.family_omits_noise_word(good, spec, self.corpus, genre):
                ok, _ = rve.CHECKS["omits_noise_word"](md, self.corpus, genre)
                self.assertFalse(ok)

    # --- MAJOR 3: no_invented_traits only saw QUOTED single tokens -------------

    def test_unquoted_invented_trait_is_caught(self):
        for genre, good, spec in self._each_genre():
            mid, md = mv.family_no_invented_traits(good, spec, self.corpus, genre)[1]
            self.assertEqual(mid, "invented/unquoted-features")
            ok, detail = rve.CHECKS["no_invented_traits"](md, self.corpus, genre)
            self.assertFalse(ok, f"[{genre}] unquoted invented traits were invisible")
            self.assertIn("INVENTED features", detail)
            text = rve.corpus_text(self.corpus, genre)
            for ch in ("!", "?", "—"):   # the premise of the check: the corpus has none
                self.assertEqual(text.count(ch), 0)

    def test_cross_genre_import_is_an_invented_trait(self):
        # Pooling the genres puts the OTHER genre's habit word into this profile. Within
        # this genre it has zero support, so it is exactly what it looks like: invented.
        for genre, good, spec in self._each_genre():
            foreign = spec["foreign_habit_word"]["word"]
            md = mv.append_to_section(good, "Vocabulary",
                                      f'\n- **More signature words:** "{foreign}"\n')
            ok, detail = rve.CHECKS["no_invented_traits"](md, self.corpus, genre)
            self.assertFalse(ok, f"[{genre}] importing '{foreign}' was not caught")
            self.assertIn(foreign, detail)

    def test_denied_feature_is_not_an_invented_trait(self):
        # The mirror direction: the good profile writes "Em-dash density: never — 0
        # em-dashes across all 5 samples". Mining an absence must not read as asserting it.
        for genre, good, _spec in self._each_genre():
            ok, detail = rve.CHECKS["no_invented_traits"](good, self.corpus, genre)
            self.assertTrue(ok, detail)
            self.assertIn("em-dash", good.lower())

    # --- MINOR: honest_gap was a literal substring search anywhere in the file --

    def test_honest_gap_must_land_in_the_evidence_free_section(self):
        for genre, good, spec in self._each_genre():
            mid, md = mv.family_honest_gap(good, spec, self.corpus, genre)[1]
            self.assertIn("parked-elsewhere", mid)
            self.assertIn(rve.HONEST_GAP.lower(), md.lower(),
                          "the phrase must still be in the file — that is the evasion")
            ok, _ = rve.CHECKS["honest_gap"](md, self.corpus, genre)
            self.assertFalse(ok, f"[{genre}] the phrase parked in a convenient section "
                                 f"satisfied the check")


class MutantFamilies(unittest.TestCase):
    """The families are the point: a checker must catch artifacts it has never seen."""

    def setUp(self):
        self.corpus = rve.load_corpus()
        self.pairs = rve.profile_pairs(self.corpus)

    def test_every_family_meets_its_declared_floor(self):
        for mode, (caught, total) in mv.catch_rates(self.corpus, self.pairs).items():
            self.assertGreater(total, 0, f"{mode}: an empty family proves nothing")
            rate = caught / total
            self.assertGreaterEqual(
                rate, mv.MUTANT_FLOORS[mode],
                f"{mode}: catch rate {caught}/{total} = {rate:.0%} is below the declared "
                f"floor {mv.MUTANT_FLOORS[mode]:.0%} — the checker is memorizing exemplars")

    def test_families_are_deterministic(self):
        # No RNG, no clock: CI must be byte-reproducible or the catch rate is noise.
        self.assertEqual(mv.catch_rates(self.corpus, self.pairs),
                         mv.catch_rates(self.corpus, self.pairs))

    def test_every_family_has_more_than_one_member(self):
        # A family of one is the N=1 boundary that produced every finding in review.
        for genre, good, _bad in self.pairs:
            spec = self.corpus["ground_truth"]["genres"][genre]
            for mode, build in mv.FAMILIES.items():
                self.assertGreater(len(build(rve.load_profile(good), spec,
                                             self.corpus, genre)), 1,
                                   f"{mode} family has <2 members for {genre}")

    def test_mutants_are_wrong_only_in_the_dimension_they_name(self):
        # If a mutant broke the header contract it would be caught for the wrong reason
        # and the catch rate would be a lie.
        for genre, good, _bad in self.pairs:
            md = rve.load_profile(good)
            spec = self.corpus["ground_truth"]["genres"][genre]
            for mode, build in mv.FAMILIES.items():
                for mid, mutant in build(md, spec, self.corpus, genre):
                    ok, _ = rve.CHECKS["headers_present"](mutant, self.corpus, genre)
                    self.assertTrue(ok, f"{mid}: mutant broke the header contract")

    def test_the_known_miss_is_still_a_miss_and_still_declared(self):
        # Honesty guard. If this starts passing, the checker got better and the floor
        # should rise — but it must never pass SILENTLY while the docs declare a gap.
        for genre, good, _bad in self.pairs:
            spec = self.corpus["ground_truth"]["genres"][genre]
            family = dict(mv.family_no_invented_traits(rve.load_profile(good), spec,
                                                       self.corpus, genre))
            md = family["invented/hard-unquoted-vocabulary"]
            ok, _ = rve.CHECKS["no_invented_traits"](md, self.corpus, genre)
            self.assertTrue(ok, "the declared KNOWN MISS is now caught — raise the "
                                "no_invented_traits floor and update the module _doc")
        self.assertLess(mv.MUTANT_FLOORS["no_invented_traits"], 1.0,
                        "a family with a declared known miss cannot have a 100% floor")

    def test_hard_tail_controls_are_not_flagged(self):
        for genre, good, _bad in self.pairs:
            spec = self.corpus["ground_truth"]["genres"][genre]
            for hid, md, mode, must_catch in mv.hard_tail(rve.load_profile(good), spec,
                                                          self.corpus, genre):
                if must_catch or mode is None:
                    continue
                ok, detail = rve.CHECKS[mode](md, self.corpus, genre)
                self.assertTrue(ok, f"[{genre}] {hid} is correct behavior but was "
                                    f"flagged: {detail}")


class MainGate(unittest.TestCase):
    """The gate: main() must exit nonzero when the suite can no longer discriminate."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.corpus = rve.load_corpus()

    def _run_main(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = rve.main([])
        return rc, buf.getvalue()

    def test_shipped_fixtures_pass(self):
        rc, _ = self._run_main()
        self.assertEqual(rc, 0)

    def test_doctored_run_with_two_good_profiles_fails(self):
        # Replace a bad profile with a copy of the good one. Nothing trips, so the
        # suite proves nothing — and must go red rather than green.
        pairs = rve.profile_pairs(self.corpus)
        genre, good, _bad = pairs[0]
        fake_bad = os.path.join(self.tmp, "fake_bad.md")
        shutil.copyfile(good, fake_bad)
        doctored = [(genre, good, fake_bad)] + pairs[1:]
        with mock.patch.object(rve, "profile_pairs", lambda _c: doctored):
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
        pairs = rve.profile_pairs(self.corpus)
        genre, good, _bad = pairs[0]
        missing = [(genre, good, os.path.join(self.tmp, "does-not-exist.md"))] + pairs[1:]
        with mock.patch.object(rve, "profile_pairs", lambda _c: missing):
            rc, out = self._run_main()
        self.assertEqual(rc, 1)
        self.assertIn("missing fixture artifact", out)

    def test_a_pooled_ground_truth_cannot_go_green(self):
        # The defect that started this rewrite, as a gate: declare a habit count that
        # only holds when the genres are POOLED ('kaleidoscope' is 2x per genre, 4x
        # pooled). The runner must refuse to be green.
        corpus_path = os.path.join(self.tmp, "pooled.json")
        corpus = rve.load_corpus()
        corpus["ground_truth"]["genres"]["tweet"]["habit_word"] = {
            "word": "kaleidoscope", "count": 4, "rule": "pooled count — WRONG"}
        with open(corpus_path, "w", encoding="utf-8") as fh:
            json.dump(corpus, fh)
        with mock.patch.object(rve, "CORPUS_PATH", corpus_path):
            rc, out = self._run_main()
        self.assertEqual(rc, 1)
        self.assertIn("GROUND TRUTH DRIFT", out)


if __name__ == "__main__":
    unittest.main()
