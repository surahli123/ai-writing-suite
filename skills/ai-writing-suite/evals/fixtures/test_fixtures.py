"""Unit tests for the fixtures harness. Run: python3 -m unittest discover.

These tests assert the fixture SUITE is well-formed and stays calibrated:
  - every fixture has the required fields
  - detector scores land in the declared bands (so a fixture can't silently rot)
  - the naive-baseline miss rate stays in the 30-40% calibration band
  - the LLM-judge prompt builds for every fixture (the SKIP path is sound)
"""

import unittest

from detector.detector import analyze
from fixtures import judge
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
            # No template placeholder may leak — including subtle_tell, whose
            # template token was `{subtle_tell or "..."}` and silently leaked.
            for token in ("{before", "{after", "{genre", "{rubric_focus",
                          "{subtle_tell"):
                self.assertNotIn(token, prompt,
                                 f"{f['id']} leaked placeholder {token}")
            self.assertIn(f["before"], prompt)
            self.assertIn(f["after"], prompt)


class JudgePromptAlwaysScoresNoFabrication(unittest.TestCase):
    """no_fabrication must be requested for EVERY fixture, even the 3 whose
    rubric_focus omits it — otherwise the highest-stakes dimension goes
    unscored on those fixtures."""

    def test_every_prompt_requests_no_fabrication(self):
        template = _extract_judge_template()
        for f in load_fixtures()["fixtures"]:
            prompt = build_judge_prompt(f, template)
            self.assertIn("no_fabrication", prompt,
                          f"{f['id']} prompt does not request no_fabrication")


class GoldLabels(unittest.TestCase):
    def test_expected_verdict_is_valid_when_present(self):
        for f in load_fixtures()["fixtures"]:
            gv = f.get("expected_verdict")
            if gv is not None:
                self.assertIn(gv, ("PASS", "FAIL"),
                              f"{f['id']} expected_verdict={gv!r} not PASS/FAIL")


class JudgeParsing(unittest.TestCase):
    """Parse + aggregate the model's verdict from CANNED responses — no network,
    no key, runs in CI. Guards the judge logic the way ScoreBands/Calibration
    guard the deterministic half."""

    def test_clean_all_pass(self):
        text = ("meaning_preserved: PASS — facts kept\n"
                "tells_removed: PASS — vocab cleaned\n"
                "voice_kept: PASS — sounds human\n"
                "no_fabrication: PASS — nothing invented\n"
                "VERDICT: PASS")
        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
                                  ["meaning_preserved", "tells_removed", "voice_kept"])
        self.assertEqual(verdict, "PASS")

    def test_no_fabrication_fail_forces_overall_fail(self):
        # focus does NOT list no_fabrication (mirrors readme-01) yet a fabricated
        # rewrite must still FAIL — the load-bearing asymmetry. Also proves we
        # IGNORE the model's self-reported "VERDICT: PASS" line.
        text = ("meaning_preserved: PASS\n"
                "tells_removed: PASS\n"
                "specificity_added: PASS\n"
                "no_fabrication: FAIL — invented a 2GB figure not in the source\n"
                "VERDICT: PASS")
        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
                                  ["meaning_preserved", "tells_removed",
                                   "specificity_added"])
        self.assertEqual(verdict, "FAIL")

    def test_fabrication_trap_caught(self):
        # A fluent rewrite that invents a metric: every other dim PASS, only
        # no_fabrication FAIL. The single discrimination the judge exists to make.
        text = ("meaning_preserved: PASS\n"
                "voice_kept: PASS\n"
                "genre_fit: PASS\n"
                "no_fabrication: FAIL — '37% faster' appears nowhere in before\n"
                "VERDICT: PASS")
        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
                                  ["voice_kept", "genre_fit"])
        self.assertEqual(verdict, "FAIL")

    def test_focus_dim_fail_forces_fail(self):
        text = ("meaning_preserved: FAIL — dropped the retention number\n"
                "tells_removed: PASS\n"
                "no_fabrication: PASS\n"
                "VERDICT: FAIL")
        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
                                  ["meaning_preserved", "tells_removed"])
        self.assertEqual(verdict, "FAIL")

    def test_unparseable_returns_none(self):
        text = "The rewrite reads well overall and keeps the meaning."
        self.assertEqual(judge.parse_dimension_lines(text), {})
        self.assertIsNone(
            judge.aggregate([judge.parse_dimension_lines(text)], ["voice_kept"]))

    def test_missing_required_dim_returns_none(self):
        # no_fabrication line absent -> can't enforce the load-bearing rule ->
        # SKIP (None), never a fabricated PASS.
        text = ("meaning_preserved: PASS\n"
                "tells_removed: PASS\n"
                "specificity_added: PASS")
        self.assertIsNone(
            judge.aggregate([judge.parse_dimension_lines(text)],
                            ["meaning_preserved", "tells_removed",
                             "specificity_added"]))

    def test_parse_excludes_self_reported_verdict_line(self):
        dims = judge.parse_dimension_lines("voice_kept: PASS\nVERDICT: FAIL")
        self.assertEqual(dims, {"voice_kept": "PASS"})
        self.assertNotIn("verdict", dims)

    def test_majority_vote_across_reps(self):
        reps = [{"meaning_preserved": "PASS", "no_fabrication": "PASS"},
                {"meaning_preserved": "FAIL", "no_fabrication": "PASS"},
                {"meaning_preserved": "PASS", "no_fabrication": "PASS"}]
        self.assertEqual(judge.aggregate(reps, ["meaning_preserved"]), "PASS")

    def test_majority_vote_tie_resolves_fail(self):
        reps = [{"meaning_preserved": "PASS", "no_fabrication": "PASS"},
                {"meaning_preserved": "FAIL", "no_fabrication": "PASS"}]
        self.assertEqual(judge.aggregate(reps, ["meaning_preserved"]), "FAIL")

    def test_parser_tolerates_markdown_formatting(self):
        # Real judges bullet/bold/number their per-dimension lines; all must parse.
        for line in ("- meaning_preserved: PASS",
                     "* meaning_preserved: PASS",
                     "1. meaning_preserved: PASS",
                     "**meaning_preserved**: PASS",
                     "- **meaning_preserved**: PASS — kept all facts"):
            self.assertEqual(judge.parse_dimension_lines(line),
                             {"meaning_preserved": "PASS"}, line)

    def test_required_dim_missing_from_all_reps_returns_none(self):
        # no_fabrication absent from EVERY rep -> no complete verdict -> None,
        # never a fake PASS for the dimension nobody scored.
        reps = [{"meaning_preserved": "PASS"}, {"meaning_preserved": "PASS"}]
        self.assertIsNone(judge.aggregate(reps, ["meaning_preserved"]))

    def test_incomplete_reps_discarded_complete_rep_decides(self):
        # Only rep0 scored every required dim; the incomplete rep is discarded,
        # not silently counted as present for the dimension it skipped.
        reps = [
            {"meaning_preserved": "PASS", "no_fabrication": "PASS"},  # complete
            {"meaning_preserved": "FAIL"},                            # incomplete
        ]
        self.assertEqual(judge.aggregate(reps, ["meaning_preserved"]), "PASS")


class JudgeGate(unittest.TestCase):
    """The 3-state gate, exercised with NO network."""

    def test_not_configured_by_default_returns_none(self):
        import os
        from unittest import mock
        with mock.patch.dict(os.environ, {"AIWS_JUDGE_RUN": "0"}, clear=False):
            self.assertFalse(judge.is_configured())
            self.assertIsNone(judge.score("anything"))

    def test_key_without_optin_does_not_fire(self):
        # Credentials present but AIWS_JUDGE_RUN unset -> still not configured, so
        # a stray key in the environment cannot trigger a billed call.
        import os
        from unittest import mock
        env = {"AIWS_JUDGE_URL": "https://x/v1", "AIWS_JUDGE_MODEL": "m",
               "AIWS_JUDGE_KEY": "sk-test", "AIWS_JUDGE_RUN": "0"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertFalse(judge.is_configured())
            self.assertIsNone(judge.score("anything"))


class CIClean(unittest.TestCase):
    """The 'CI stays stdlib-only / key-free' invariant, enforced as a TEST
    rather than a convention."""

    def test_judge_not_imported_at_module_load(self):
        # judge must be imported lazily INSIDE run_judge, never at run_fixtures
        # module load — so the deterministic path can't pull in the network code.
        import fixtures.run_fixtures as rf
        self.assertFalse(hasattr(rf, "judge"),
                         "run_fixtures imported judge at module load (must be lazy)")

    def test_deterministic_and_offline_judge_make_no_network_call(self):
        import io
        import os
        import contextlib
        import urllib.request
        from unittest import mock
        from fixtures.run_fixtures import run_deterministic, main

        def boom(*a, **k):
            raise AssertionError("network call attempted in a no-key run")

        buf = io.StringIO()
        with mock.patch.dict(os.environ, {"AIWS_JUDGE_RUN": "0"}, clear=False), \
                mock.patch.object(urllib.request, "urlopen", boom), \
                contextlib.redirect_stdout(buf):
            run_deterministic(load_fixtures())   # deterministic path
            rc_plain = main([])                  # CI's exact invocation
            rc_judge = main(["--judge"])         # offline judge -> all SKIP
        self.assertEqual(rc_plain, 0)
        self.assertEqual(rc_judge, 0)

    def test_run_all_and_ci_never_invoke_the_judge(self):
        # The deterministic CI path must never pass --judge or set a judge key —
        # that is what keeps CI key-free. Enforce it on the ACTUAL files, so a
        # future edit that wires the judge into CI fails this test loudly.
        import os
        evals = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(evals, "run_all.sh"), encoding="utf-8") as fh:
            run_all = fh.read()
        self.assertNotIn("--judge", run_all,
                         "run_all.sh must not invoke the judge (keeps CI key-free)")
        self.assertNotIn("AIWS_JUDGE", run_all)
        ci = os.path.join(evals, "..", "..", "..",
                          ".github", "workflows", "ci.yml")
        if os.path.exists(ci):
            with open(ci, encoding="utf-8") as fh:
                ci_txt = fh.read()
            self.assertNotIn("--judge", ci_txt)
            self.assertNotIn("AIWS_JUDGE", ci_txt)


class JudgeIntegration(unittest.TestCase):
    """run_judge end-to-end with a STUBBED model (no network, no key spend):
    proves the configured path scores every fixture, computes judge-vs-gold
    agreement, and that the liveness 0/N gate fires when nothing parses."""

    def _run(self, fake_score):
        import os
        import io
        import contextlib
        from unittest import mock
        from fixtures.run_fixtures import run_judge
        env = {"AIWS_JUDGE_URL": "https://x", "AIWS_JUDGE_MODEL": "m",
               "AIWS_JUDGE_KEY": "k", "AIWS_JUDGE_RUN": "1"}
        buf = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch("fixtures.judge.score", side_effect=fake_score), \
                contextlib.redirect_stdout(buf):
            result = run_judge(load_fixtures())
        return result, buf.getvalue()

    def test_all_pass_scores_full_agreement_no_live_error(self):
        # Emit PASS for every dimension any fixture could ask about (+ the base
        # six), so each fixture's required dims are present and PASS.
        all_dims = {"meaning_preserved", "tells_removed", "no_fabrication",
                    "voice_kept", "specificity_added", "genre_fit"}
        for f in load_fixtures()["fixtures"]:
            all_dims |= set(f["rubric_focus"])
        reply = "\n".join(f"{d}: PASS" for d in all_dims)
        (p, f, s, live), out = self._run(lambda prompt: reply)
        self.assertEqual((p, f, s, live), (8, 0, 0, False))
        self.assertIn("agreement: 8/8", out)  # all gold=PASS, judge=PASS

    def test_all_unparseable_triggers_live_error(self):
        (p, f, s, live), out = self._run(lambda prompt: "no verdict here")
        self.assertEqual((p, f), (0, 0))
        self.assertTrue(live)
        self.assertIn("envelope likely changed", out)

    def test_fabrication_makes_a_fixture_fail(self):
        # Same all-PASS reply but no_fabrication FAIL -> every fixture FAILs
        # overall (no_fabrication is always required), agreement drops to 0/8.
        all_dims = {"meaning_preserved", "tells_removed", "voice_kept",
                    "specificity_added", "genre_fit"}
        for f in load_fixtures()["fixtures"]:
            all_dims |= set(f["rubric_focus"])
        all_dims.discard("no_fabrication")
        reply = "\n".join(f"{d}: PASS" for d in all_dims) + "\nno_fabrication: FAIL"
        (p, f, s, live), out = self._run(lambda prompt: reply)
        self.assertEqual((p, f, s, live), (0, 8, 0, False))
        self.assertIn("agreement: 0/8", out)


if __name__ == "__main__":
    unittest.main()
