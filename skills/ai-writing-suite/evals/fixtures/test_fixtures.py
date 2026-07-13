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
    load_fixtures, load_fail_fixtures, build_judge_prompt, _extract_judge_template)

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
        # The 30-40% band measures the DETECTOR-TARGETED set only. `detector_blind`
        # fixtures (judge-only over-stepping cases) are misses by construction and
        # are excluded from the denominator — mirrors run_fixtures.run_deterministic.
        data = load_fixtures()
        thr = data["baseline_threshold"]
        targeted = [f for f in data["fixtures"] if not f.get("detector_blind")]
        miss = sum(1 for f in targeted
                   if analyze(f["before"])["score"] < thr)
        total = len(targeted)
        pct = 100 * miss / total
        self.assertTrue(30 <= pct <= 40,
                        f"miss rate {pct:.0f}% outside 30-40% target")

    def test_detector_blind_fixtures_are_declared_miss(self):
        # Invariant: every judge-only (detector_blind) fixture must also declare
        # expect_baseline='miss'. Guards the calibration exclusion — a future
        # judge-only fixture that forgets the marker (or mislabels its baseline)
        # would silently re-pollute the denominator.
        for f in load_fixtures()["fixtures"]:
            if f.get("detector_blind"):
                self.assertEqual(f.get("expect_baseline"), "miss",
                                 f"{f['id']} is detector_blind but not expect_baseline='miss'")

    def test_calibration_denominator_is_targeted_fixture_count(self):
        # The naive-baseline miss-rate denominator must equal exactly the count of
        # non-detector_blind fixtures in fixtures.json (currently 8). If a future
        # refactor folds the gold-FAIL fixtures (fixtures_fail.json) into the
        # runtime denominator, the printed total jumps above this count and the
        # test fails loudly — the calibration band must never be diluted at runtime.
        import io
        import re
        import contextlib
        from fixtures.run_fixtures import run_deterministic
        data = load_fixtures()
        expected_total = sum(1 for f in data["fixtures"]
                             if not f.get("detector_blind"))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            run_deterministic(data)
        m = re.search(r"miss rate:\s*\d+/(\d+)\s*=", buf.getvalue())
        self.assertIsNotNone(m, "miss-rate line not found in run_deterministic output")
        self.assertEqual(int(m.group(1)), expected_total,
                         f"calibration denominator {m.group(1)} != "
                         f"{expected_total} non-detector_blind fixtures")

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


class OversteppingHardNegatives(unittest.TestCase):
    """The over-correction trap for the `overstepping_removed` dimension.

    These are real-mined FAIL exemplars: the `before` is NOT over-stepping — it
    flips a GENUINELY common prior ('love = a feeling', 'transformation = how
    much you spend') or uses a concrete teaching device ('imagine you...'). The
    'rewrite' stripped that legitimate contrast/pedagogy, losing real information.
    A naive judge that rewards removing ANY 'you assume / 不是X而是Y / imagine you'
    would wrongly PASS these; the validity condition (over-stepping is real ONLY
    when the prior is a manufactured strawman) must drive `meaning_preserved` to
    FAIL, forcing the overall verdict FAIL. Same canned-reply shape as JudgeParsing:
    feed the per-dimension verdict a correct judge WOULD emit and assert FAIL.
    Live before/after strings + provenance: docs/overstepping-fixtures-DRAFT-2026-06-24.json
    (_fail_exemplars_for_test_fixtures). FAIL is driven by meaning_preserved in every case.
    """

    def test_hardneg_apple_en_legit_pedagogy(self):
        # before: "Imagine that you are holding an apple ... cut it in half with a knife."
        # after:  "Consider an apple that is cut in half with a knife."
        # 'imagine you' is a concrete teaching device, not a judgment about the
        # reader's thoughts; stripping it is colder with no gain.
        text = ("overstepping_removed: PASS — dropped an 'imagine you' frame\n"
                "meaning_preserved: FAIL — removed a legitimate teaching device "
                "for no gain (the prior was not a manufactured strawman)\n"
                "voice_kept: FAIL — traded a concrete image for a colder register\n"
                "no_fabrication: PASS")
        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
                                  ["overstepping_removed", "meaning_preserved",
                                   "voice_kept"])
        self.assertEqual(verdict, "FAIL")

    def test_hardneg_love_zh_valid_flip(self):
        # before: 爱并不是一种感觉，而是一种行为。   after: 爱是一种行为。
        # 「爱=感觉」是真实普遍旧认知 -> 「不是感觉，而是行为」是有信息量的合法对比；
        # 改写删掉对比丢了真实信息 -> meaning_preserved FAIL.
        text = ("overstepping_removed: PASS — a 不是X而是Y contrast was removed\n"
                "meaning_preserved: FAIL — '爱=感觉' is a real widespread prior, so "
                "the flip carried information; removing it loses meaning\n"
                "no_fabrication: PASS")
        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
                                  ["overstepping_removed", "meaning_preserved"])
        self.assertEqual(verdict, "FAIL")

    def test_hardneg_transform_zh_earned_contrast(self):
        # before: 真正的转型不是看投入绝对值，而是看投入是否匹配到能产生实际改变的最小单元。
        # after:  真正的转型要看投入是否匹配到能产生实际改变的最小单元。
        # 「转型=砸钱（投入绝对值）」是真实常见认知 -> 对比是 earned；改写丢了「不是砸钱」
        # 这层纠正 -> meaning_preserved FAIL.
        text = ("overstepping_removed: PASS — a 不是X而是Y contrast was removed\n"
                "meaning_preserved: FAIL — '转型=砸钱' is a real common prior; the "
                "contrast was earned, so dropping it loses information\n"
                "no_fabrication: PASS")
        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
                                  ["overstepping_removed", "meaning_preserved"])
        self.assertEqual(verdict, "FAIL")


class PayoffClearAggregateSemantics(unittest.TestCase):
    """payoff_clear exercised through aggregate() with canned judge replies.

    HONESTY NOTE: aggregate() has NO per-dimension hard/advisory distinction —
    every dim in rubric_focus is always-required. So these assert the GENERIC
    aggregate contract using payoff_clear as the focus dim (the FAIL + PASS halves
    of the overstep-05 minimal pair). They do NOT, by themselves, guard the diff —
    the payoff_clear-SPECIFIC guards live in PayoffClearGuards, and the N/A contract
    this feature ships is guarded by NaAwareAggregate below.
    """

    def test_stub_after_fails_when_payoff_clear_fails(self):
        text = ("overstepping_removed: PASS\n"
                "payoff_clear: FAIL — 'It reduces them' lost its subject\n"
                "meaning_preserved: PASS\n"
                "no_fabrication: PASS")
        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
                                  ["overstepping_removed", "payoff_clear",
                                   "meaning_preserved"])
        self.assertEqual(verdict, "FAIL")

    def test_clean_after_passes(self):
        text = ("overstepping_removed: PASS\n"
                "payoff_clear: PASS — 'Merging reduces outages' names the subject\n"
                "meaning_preserved: PASS\n"
                "no_fabrication: PASS")
        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
                                  ["overstepping_removed", "payoff_clear",
                                   "meaning_preserved"])
        self.assertEqual(verdict, "PASS")


class NaAwareAggregate(unittest.TestCase):
    """The N/A contract, enforced end-to-end. rubric.md tells the judge to output
    `payoff_clear: N/A` when no presumption was removed. aggregate() must treat an
    explicit N/A as VACUOUSLY SATISFIED (dropped from the verdict), not as an
    incomplete rep — so a genuine FAIL is never silently swallowed as a SKIP when
    payoff_clear is N/A (the review's reproduced landmine)."""

    def test_parse_recognizes_na(self):
        self.assertEqual(judge.parse_dimension_lines("payoff_clear: N/A"),
                         {"payoff_clear": "N/A"})
        self.assertEqual(judge.parse_dimension_lines("- **payoff_clear**: NA"),
                         {"payoff_clear": "N/A"})

    def test_na_dim_vacuously_satisfied_real_fail_surfaces(self):
        # The reviewer's repro: a genuine defect (overstepping_removed +
        # meaning_preserved FAIL) with payoff_clear correctly N/A must FAIL —
        # NOT return None (silent SKIP that swallows the real FAIL).
        text = ("overstepping_removed: FAIL\n"
                "meaning_preserved: FAIL\n"
                "payoff_clear: N/A\n"
                "no_fabrication: PASS")
        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
                                  ["overstepping_removed", "payoff_clear",
                                   "meaning_preserved"])
        self.assertEqual(verdict, "FAIL")

    def test_na_dim_dropped_all_else_pass_is_pass(self):
        text = ("overstepping_removed: PASS\n"
                "meaning_preserved: PASS\n"
                "payoff_clear: N/A\n"
                "no_fabrication: PASS")
        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
                                  ["overstepping_removed", "payoff_clear",
                                   "meaning_preserved"])
        self.assertEqual(verdict, "PASS")

    def test_no_fabrication_na_is_incomplete_never_pass(self):
        # no_fabrication is the load-bearing dim; it can never be N/A. An N/A there
        # -> incomplete rep -> None (SKIP), never a fabricated PASS.
        text = ("meaning_preserved: PASS\n"
                "no_fabrication: N/A")
        self.assertIsNone(
            judge.aggregate([judge.parse_dimension_lines(text)],
                            ["meaning_preserved"]))


class PayoffClearGuards(unittest.TestCase):
    """Guards that actually go RED if the payoff_clear diff is reverted (unlike the
    generic aggregate tests above, which pass with any dimension label)."""

    # The over-stripped FAIL half of the overstep-05 minimal pair — materialized
    # from docstring prose into an executable check.
    FAIL_PARTNER = ("It actually reduces them: one config to keep in sync instead "
                    "of two, and we traced 3 of the last 5 incidents to drift "
                    "between them.")

    def test_judge_template_documents_payoff_clear(self):
        # The fenced prompt block a LIVE judge actually reads must define the
        # dimension. Goes RED if the PAYOFF-CLEAR CHECK block is removed from
        # rubric.md while payoff_clear stays in fixtures' rubric_focus.
        template = _extract_judge_template()
        self.assertIn("PAYOFF-CLEAR CHECK", template)
        self.assertIn("payoff_clear", template)
        self.assertIn("N/A", template)

    def test_judge_template_demands_verbatim_evidence(self):
        # The fenced prompt a LIVE judge reads must instruct it to cite a verbatim
        # EVIDENCE quote. Goes RED if the EVIDENCE instruction is dropped from
        # rubric.md while judge.parse_dimensions still expects/audits it. Mirrors
        # test_judge_template_documents_payoff_clear.
        template = _extract_judge_template()
        self.assertIn("EVIDENCE", template)
        self.assertIn("verbatim", template.lower())

    def test_payoff_clear_only_paired_with_overstepping_removed(self):
        # Invariant lock (rubric.md): payoff_clear is scored ONLY alongside a
        # removal, so it must never appear in rubric_focus without
        # overstepping_removed. Prevents a future fixture from tripping the N/A path.
        for f in load_fixtures()["fixtures"]:
            if "payoff_clear" in f["rubric_focus"]:
                self.assertIn("overstepping_removed", f["rubric_focus"],
                              f"{f['id']}: payoff_clear without overstepping_removed")

    def test_overstep05_failpartner_detector_blind_and_isolated(self):
        # Tie the minimal-pair claim to executable checks: the FAIL partner must be
        # detector-blind (score 0, matching overstep-05's declared judge-only band)
        # and must have DROPPED the presumption — isolating payoff_clear as the sole
        # differentiator vs the live PASS `after`. Goes RED if overstep-05 is reverted.
        fixture = next(f for f in load_fixtures()["fixtures"]
                       if f["id"] == "overstep-05-payoff-en")
        self.assertEqual(analyze(self.FAIL_PARTNER)["score"], 0)
        self.assertNotIn("you might think", self.FAIL_PARTNER.lower())
        self.assertNotIn("you might think", fixture["after"].lower())


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
        n = len(load_fixtures()["fixtures"])  # all gold=PASS, judge=PASS
        (p, f, s, live), out = self._run(lambda prompt: reply)
        self.assertEqual((p, f, s, live), (n, 0, 0, False))
        self.assertIn(f"agreement: {n}/{n}", out)

    def test_all_unparseable_triggers_live_error(self):
        (p, f, s, live), out = self._run(lambda prompt: "no verdict here")
        self.assertEqual((p, f), (0, 0))
        self.assertTrue(live)
        self.assertIn("envelope likely changed", out)

    def test_fabrication_makes_a_fixture_fail(self):
        # Same all-PASS reply but no_fabrication FAIL -> every fixture FAILs
        # overall (no_fabrication is always required), agreement drops to 0/N.
        all_dims = {"meaning_preserved", "tells_removed", "voice_kept",
                    "specificity_added", "genre_fit"}
        for f in load_fixtures()["fixtures"]:
            all_dims |= set(f["rubric_focus"])
        all_dims.discard("no_fabrication")
        reply = "\n".join(f"{d}: PASS" for d in all_dims) + "\nno_fabrication: FAIL"
        n = len(load_fixtures()["fixtures"])  # all gold=PASS, judge=FAIL
        (p, f, s, live), out = self._run(lambda prompt: reply)
        self.assertEqual((p, f, s, live), (0, n, 0, False))
        self.assertIn(f"agreement: 0/{n}", out)


class GoldFailSuiteShape(unittest.TestCase):
    """The separate gold-FAIL file (fixtures_fail.json) is well-formed, covers the
    required archetypes, and cannot leak into the calibration denominator."""

    FAIL_REQUIRED = {"id", "genre", "difficulty", "before", "after",
                     "rubric_focus", "expected_verdict", "fail_dimension"}

    def test_all_fail_fixtures_have_required_fields(self):
        for f in load_fail_fixtures()["fixtures"]:
            missing = self.FAIL_REQUIRED - set(f)
            self.assertFalse(missing, f"{f.get('id')} missing {missing}")

    def test_every_expected_verdict_is_fail(self):
        for f in load_fail_fixtures()["fixtures"]:
            self.assertEqual(f["expected_verdict"], "FAIL",
                             f"{f['id']} expected_verdict must be FAIL")

    def test_fail_dimension_is_weighed_by_the_judge(self):
        # The FAIL driver must be in rubric_focus (so the judge actually scores it)
        # unless it is no_fabrication, which the rubric requires on every verdict.
        for f in load_fail_fixtures()["fixtures"]:
            fd = f["fail_dimension"]
            self.assertTrue(fd in f["rubric_focus"] or fd == "no_fabrication",
                            f"{f['id']}: fail_dimension {fd!r} not weighed")

    def test_required_archetypes_present(self):
        # The hardening plan mandates at minimum: fabricated fact (no_fabrication),
        # over-corrected over-stepping + dropped claim (meaning_preserved), and a
        # payoff_clear stub. Guard that the suite keeps covering all three drivers.
        dims = {f["fail_dimension"] for f in load_fail_fixtures()["fixtures"]}
        for required in ("no_fabrication", "meaning_preserved", "payoff_clear"):
            self.assertIn(required, dims,
                          f"gold-FAIL suite missing a {required}-driven archetype")

    def test_fail_ids_never_appear_in_calibration_suite(self):
        # Structural exclusion: the FAIL fixtures live in their OWN file and must
        # never appear in fixtures.json, so they cannot pollute the 30-40% band.
        pass_ids = {f["id"] for f in load_fixtures()["fixtures"]}
        fail_ids = {f["id"] for f in load_fail_fixtures()["fixtures"]}
        self.assertEqual(pass_ids & fail_ids, set(),
                         "a gold-FAIL id leaked into fixtures.json (calibration set)")

    def test_declared_score_bands_hold(self):
        for f in load_fail_fixtures()["fixtures"]:
            if "before_band_max" in f:
                self.assertLessEqual(analyze(f["before"])["score"],
                                     f["before_band_max"], f["id"])
            if "after_band_max" in f:
                self.assertLessEqual(analyze(f["after"])["score"],
                                     f["after_band_max"], f["id"])


class GoldFailDiscrimination(unittest.TestCase):
    """Canned-judge-response DISCRIMINATION over gold-FAIL fixtures. gold=FAIL, so
    judge-says-FAIL == agreement (the judge discriminated); judge-says-PASS ==
    DISAGREEMENT — the signal this suite exists to surface. Same no-network canned
    shape as JudgeParsing, but keyed to expected_verdict='FAIL'."""

    def _fixture(self, fid):
        return next(f for f in load_fail_fixtures()["fixtures"] if f["id"] == fid)

    def test_fabricated_number_judge_fail_is_agreement(self):
        f = self._fixture("fail-fabricated-number-en")
        reply = ("meaning_preserved: PASS\n"
                 "specificity_added: PASS — added figures\n"
                 "no_fabrication: FAIL — 37% / 2.1s->1.3s appear nowhere in before")
        verdict = judge.aggregate([judge.parse_dimension_lines(reply)],
                                  f["rubric_focus"])
        self.assertEqual(verdict, "FAIL")
        self.assertEqual(verdict, f["expected_verdict"])  # agreement

    def test_fabricated_number_judge_pass_is_disagreement(self):
        # The judge is FOOLED by the fluent, specific rewrite and marks it PASS.
        # gold=FAIL -> a DISAGREEMENT the runner must surface, not a silent pass.
        f = self._fixture("fail-fabricated-number-en")
        reply = ("meaning_preserved: PASS\n"
                 "specificity_added: PASS\n"
                 "no_fabrication: PASS")  # wrongly accepts the invented stats
        verdict = judge.aggregate([judge.parse_dimension_lines(reply)],
                                  f["rubric_focus"])
        self.assertEqual(verdict, "PASS")
        self.assertNotEqual(verdict, f["expected_verdict"])  # DISAGREEMENT

    def test_payoff_stub_judge_fail_is_agreement(self):
        f = self._fixture("fail-payoff-stub-en")
        reply = ("overstepping_removed: PASS\n"
                 "payoff_clear: FAIL — 'It reduces them' lost its subject\n"
                 "meaning_preserved: PASS\n"
                 "no_fabrication: PASS")
        verdict = judge.aggregate([judge.parse_dimension_lines(reply)],
                                  f["rubric_focus"])
        self.assertEqual(verdict, "FAIL")

    def test_overcorrected_overstep_judge_fail_is_agreement(self):
        f = self._fixture("fail-overcorrected-overstep-en")
        reply = ("overstepping_removed: PASS — a 'X isn't Y' frame was removed\n"
                 "meaning_preserved: FAIL — 'love=feeling' is a real prior; the "
                 "contrast was legitimate, removing it loses information\n"
                 "no_fabrication: PASS")
        verdict = judge.aggregate([judge.parse_dimension_lines(reply)],
                                  f["rubric_focus"])
        self.assertEqual(verdict, "FAIL")


class GoldFailJudgeIntegration(unittest.TestCase):
    """run_fail_judge end-to-end with a STUBBED model (no network, no key): prove
    the discrimination tally separates a judge that catches every bad rewrite from
    one that misses them all, and that the 0/N liveness gate fires."""

    def _run(self, fake_score):
        import os
        import io
        import contextlib
        from unittest import mock
        from fixtures.run_fixtures import run_fail_judge
        env = {"AIWS_JUDGE_URL": "https://x", "AIWS_JUDGE_MODEL": "m",
               "AIWS_JUDGE_KEY": "k", "AIWS_JUDGE_RUN": "1"}
        buf = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch("fixtures.judge.score", side_effect=fake_score), \
                contextlib.redirect_stdout(buf):
            result = run_fail_judge(load_fail_fixtures())
        return result, buf.getvalue()

    def test_judge_that_fails_everything_discriminates_all(self):
        n = len(load_fail_fixtures()["fixtures"])
        # A TRUE all-FAIL judge fails every dimension, so it also fails each
        # fixture's declared DRIVER dim -> discrimination, not wrong-reason.
        reply = "\n".join(f"{d}: FAIL" for d in
                          ("overstepping_removed", "payoff_clear", "meaning_preserved",
                           "specificity_added", "no_fabrication"))
        (d, m, w, s, live), out = self._run(lambda p: reply)
        self.assertEqual((d, m, w, s, live), (n, 0, 0, 0, False))
        self.assertIn(f"{n}/{n} caught", out)

    def test_overall_fail_wrong_driver_is_wrong_reason_not_discrimination(self):
        # The FIX-2 refinement: a judge that FAILs only no_fabrication marks every
        # fixture overall-FAIL, but only the ONE no_fabrication-driven fixture is
        # truly discriminated. The other three fail for the WRONG reason (their
        # driver dim passed) -> wrong_reason, not discrimination. The pre-fix code
        # would have counted all four as caught.
        n = len(load_fail_fixtures()["fixtures"])
        drivers = {f["fail_dimension"] for f in load_fail_fixtures()["fixtures"]}
        n_nofab = sum(1 for f in load_fail_fixtures()["fixtures"]
                      if f["fail_dimension"] == "no_fabrication")
        reply = "\n".join(f"{d}: PASS" for d in
                          ("overstepping_removed", "payoff_clear",
                           "meaning_preserved", "specificity_added")
                          ) + "\nno_fabrication: FAIL"
        (d, m, w, s, live), out = self._run(lambda p: reply)
        self.assertEqual(d, n_nofab)          # only the no_fabrication-driven one
        self.assertEqual(w, n - n_nofab)      # rest are right-verdict/wrong-reason
        self.assertEqual((m, s, live), (0, 0, False))
        self.assertIn("right verdict, wrong reason", out)
        # Guard the premise: the suite really does mix driver dims (else this test
        # would be vacuous).
        self.assertGreater(len(drivers), 1)

    def test_judge_that_passes_everything_misses_all(self):
        n = len(load_fail_fixtures()["fixtures"])
        # All-PASS (incl no_fabrication + payoff_clear) -> judge PASS on every bad
        # rewrite -> gold=FAIL -> all MISSED (disagreement).
        reply = "\n".join(f"{d}: PASS" for d in
                          ("overstepping_removed", "payoff_clear", "meaning_preserved",
                           "specificity_added", "no_fabrication"))
        (d, m, w, s, live), out = self._run(lambda p: reply)
        self.assertEqual((d, m, w, s, live), (0, n, 0, 0, False))
        self.assertIn("DISAGREEMENT", out)

    def test_unparseable_triggers_live_error(self):
        (d, m, w, s, live), out = self._run(lambda p: "no verdict here")
        self.assertEqual((d, m, w), (0, 0, 0))
        self.assertTrue(live)
        self.assertIn("envelope likely changed", out)

    def test_offline_all_skip_no_live_error(self):
        # Not configured -> every fixture SKIPPED, no discrimination attempted, and
        # crucially no live_error (mirrors run_judge's keyless all-SKIP exiting 0).
        import os
        import io
        import contextlib
        from unittest import mock
        from fixtures.run_fixtures import run_fail_judge
        n = len(load_fail_fixtures()["fixtures"])
        buf = io.StringIO()
        with mock.patch.dict(os.environ, {"AIWS_JUDGE_RUN": "0"}, clear=False), \
                contextlib.redirect_stdout(buf):
            d, m, w, s, live = run_fail_judge(load_fail_fixtures())
        self.assertEqual((d, m, w, s, live), (0, 0, 0, n, False))


if __name__ == "__main__":
    unittest.main()
