"""Unit tests for the comms-draft behavioral (artifact-discrimination) suite.
Run: python3 -m unittest fixtures.test_draft_cases

The load-bearing tests here are NOT "the JSON parses". They are:
  * the fabrication fn catches an invented number/name on hand-built inputs, and
    does NOT flag a specific that legitimately came from the brief or the KB;
  * every case's good_draft passes and bad_draft trips its declared failure_mode
    (the planted positive, per case);
  * main() goes RED when a bad_draft is replaced by a clean one — i.e. the
    planted-positive gate itself can fail. A gate that can't go red proves nothing.
"""

import contextlib
import copy
import io
import json
import os
import tempfile
import unittest
from unittest import mock

import ast
import pathlib

import fixtures.holdout_adversary as ha
import fixtures.mutants_draft as md
import fixtures.run_draft_cases as rdc
from fixtures.run_draft_cases import (
    CHECKS, CRITERIA_DIMENSIONS, build_draft_judge_prompt, count_questions,
    find_fabrications, load_draft_cases, main, run_case_checks, run_deterministic,
    run_judge, source_blob,
)

REQUIRED = {"id", "brief", "kb_facts", "good_draft", "bad_draft",
            "failure_mode", "checks"}


class Wellformed(unittest.TestCase):
    def test_required_fields(self):
        for c in load_draft_cases()["cases"]:
            missing = REQUIRED - set(c)
            self.assertFalse(missing, f"{c.get('id')} missing {missing}")

    def test_at_least_three_cases_unique_ids(self):
        cases = load_draft_cases()["cases"]
        self.assertGreaterEqual(len(cases), 3)
        ids = [c["id"] for c in cases]
        self.assertEqual(len(ids), len(set(ids)), "duplicate case id")

    def test_failure_mode_is_a_declared_check(self):
        # A failure_mode the case does not actually run is unfalsifiable.
        for c in load_draft_cases()["cases"]:
            self.assertIn(c["failure_mode"], c["checks"],
                          f"{c['id']}: failure_mode not in its own checks list")
            self.assertIn(c["failure_mode"], CHECKS,
                          f"{c['id']}: unknown failure_mode {c['failure_mode']!r}")

    def test_every_check_name_is_implemented(self):
        for c in load_draft_cases()["cases"]:
            for name in c["checks"]:
                self.assertIn(name, CHECKS, f"{c['id']}: unknown check {name!r}")


class Fabrication(unittest.TestCase):
    """A bounded regression signal for numeric, capitalized-name, and closed
    claim-verb shapes, tested independently of the shipped artifacts. Claims outside
    those shapes remain declared misses, not evidence that the draft is factual."""

    SOURCES = ("We shipped the win-back campaign on 3 March; Priya owns the "
               "follow-up. Q3 churn was 4.1%.")

    EXPECTED_FABRICATION_ESCAPES = (
        {
            "id": "emotion-claim-outside-closed-verbs",
            "klass": "expected_escape",
            "draft": "The team was thrilled with the outcome.",
        },
        {
            "id": "reaction-claim-outside-closed-verbs",
            "klass": "expected_escape",
            "draft": "The launch delighted everyone involved.",
        },
    )

    def test_clean_draft_flags_nothing(self):
        draft = ("We shipped on 3 March. Priya owns the follow-up, and Q3 churn "
                 "was 4.1%.")
        self.assertEqual(find_fabrications(draft, self.SOURCES), [])

    def test_invented_number_is_flagged(self):
        draft = "Churn fell 23% last quarter."
        self.assertIn("23%", find_fabrications(draft, self.SOURCES))

    def test_number_present_in_sources_is_not_flagged(self):
        # The false-alarm direction: a real figure from the brief/KB must survive.
        draft = "Q3 churn was 4.1%, which is why this matters."
        self.assertEqual(find_fabrications(draft, self.SOURCES), [])

    def test_invented_proper_noun_is_flagged(self):
        draft = "The campaign runs on Northwind Retention."
        self.assertIn("Northwind Retention", find_fabrications(draft, self.SOURCES))

    def test_completed_claim_is_flagged(self):
        claim = "The migration completed yesterday and customers were unaffected"
        self.assertIn(claim, find_fabrications(claim + ".", self.SOURCES))

    def test_caused_claim_is_flagged(self):
        claim = "The rollout caused an outage and support handled every complaint"
        self.assertIn(claim, find_fabrications(claim + ".", self.SOURCES))

    def test_approved_claim_is_flagged(self):
        claim = "Legal approved the policy"
        self.assertIn(claim, find_fabrications(claim + ".", self.SOURCES))

    def test_claim_phrase_present_in_sources_is_not_flagged(self):
        claim = "Legal approves the policy."
        self.assertEqual(find_fabrications(claim, claim), [])

    def test_residual_claim_escapes_are_declared_and_still_escape(self):
        # Honesty guard: these fabricated claims lack every candidate shape. If the
        # detector grows to catch one, promote it instead of leaving stale ledger data.
        for entry in self.EXPECTED_FABRICATION_ESCAPES:
            with self.subTest(entry=entry["id"]):
                self.assertEqual(entry["klass"], "expected_escape")
                self.assertEqual(find_fabrications(entry["draft"], self.SOURCES), [])

    def test_needs_marker_content_is_not_treated_as_a_claim(self):
        # A declared gap DESCRIBES a missing fact; it must not be read as asserting
        # one, or marking a gap correctly would itself trip the fabrication check.
        draft = "Churn was [NEEDS: the Q3 churn number, e.g. 23% — unknown] last quarter."
        self.assertEqual(find_fabrications(draft, self.SOURCES), [])

    def test_sentence_initial_capital_is_not_a_proper_noun(self):
        # "The campaign" must not manufacture a two-word name out of one word.
        draft = "The campaign shipped. Our team is ready."
        self.assertEqual(find_fabrications(draft, self.SOURCES), [])

    def test_is_pure(self):
        # No I/O, no env: same inputs -> same outputs, callable from anywhere.
        a = find_fabrications("Acme Dynamics raised 9%.", "")
        b = find_fabrications("Acme Dynamics raised 9%.", "")
        self.assertEqual(a, b)
        self.assertEqual(sorted(a), ["9%", "Acme Dynamics"])


class PreDraftHelpers(unittest.TestCase):
    CRITERIA_HEAD = "## Acceptance criteria\n"

    def test_question_count_only_counts_pre_draft_lines(self):
        draft = ("## Clarifying questions\n- Who is the reader?\n- What changed?\n"
                 "## Draft\nIs this counted? No — it is in the body.\n")
        self.assertEqual(count_questions(draft), 2)

    def test_missing_criteria_dimensions_needs_all_five(self):
        # The five must be NAMED AS CRITERIA — bullet labels under a criteria
        # heading. (The heading is required now; the old check accepted the five
        # words appearing anywhere in the pre-draft, which prose satisfied by
        # accident. See test_criteria_named_only_in_prose_do_not_count.)
        pre = self.CRITERIA_HEAD + "\n".join(f"- {d}: something"
                                             for d in CRITERIA_DIMENSIONS)
        self.assertEqual(rdc.missing_criteria_dimensions(pre + "\n## Draft\nx"), [])
        self.assertIn("depth", rdc.missing_criteria_dimensions(
            self.CRITERIA_HEAD + "- style: x\n- format: x\n- length: x\n"
            "- content integration: x\n## Draft\nx"))

    def test_source_blob_includes_brief_and_kb(self):
        case = {"brief": "Ship on 3 March.", "kb_facts": ["structure.md: lead with the point."]}
        blob = source_blob(case)
        self.assertIn("3 march", blob)
        self.assertIn("lead with the point", blob)


class ReviewerEvasions(unittest.TestCase):
    """Regression tests for the evasions a reviewer constructed against v1 of these
    checkers. Each one slipped through; each one is now a permanent gate. Deleting a
    test here re-opens the hole it names.
    """

    # --- BLOCKER: substring lookup made the fabrication check miss its own case ---

    def test_masked_number_evasion_is_caught(self):
        # v1 did `tok in src` on RAW TEXT. draft-01's brief says "under 150 words",
        # so "50", "15", "1" and "0" all substring-matched inside "150" and were
        # silently cleared. Three invented specifics, zero flags.
        case = load_draft_cases()["cases"][0]
        self.assertIn("150", case["brief"], "the masking substring must still be here")
        draft = ("## Draft\nChurn fell 50% in Q3, our 15th straight quarter of "
                 "decline, costing 1 million.\nWe shipped on 3 March.\n")
        flagged = find_fabrications(draft, source_blob(case))
        for invented in ("50%", "15", "1"):
            self.assertIn(invented, flagged,
                          f"{invented!r} is masked by '150' in the brief again")
        # ...and the two specifics that DO come from the brief still survive.
        self.assertNotIn("3", flagged)

    def test_equivalent_percent_surface_is_not_flagged(self):
        # Same value, different surface: the policy is value equality, so a brief
        # that writes "14 percent" must not make a draft's "14%" a fabrication.
        self.assertEqual(
            find_fabrications("Churn was 14%.", "Q3 churn was 14 percent."), [])
        self.assertEqual(find_fabrications("Churn was 14 percent.", "Churn: 14%."), [])

    def test_comma_separated_thousands_are_the_same_value(self):
        self.assertEqual(find_fabrications("We saw 1,000 signups.",
                                           "There were 1000 signups."), [])

    # --- MINOR: Title Case headings false-positived as invented proper nouns ---

    def test_title_case_heading_is_not_flagged(self):
        # SKILL.md never mandates sentence-case headings; the fixtures merely
        # happened to use them. The checker must strip heading lines instead.
        case = load_draft_cases()["cases"][0]
        self.assertEqual(
            find_fabrications("## Acceptance Criteria\n## Draft\nWe shipped on 3 March.",
                              source_blob(case)), [])

    def test_subject_label_line_is_not_flagged(self):
        # The three content words ("subject", "recommendation", "standard") that used
        # to sit in _RUN_LEAD_STOPWORDS existed only to protect the fixtures' own
        # label lines. They are gone — a label word is terminated by ':', so it
        # cannot start a capitalized run.
        case = load_draft_cases()["cases"][0]
        draft = ("## Draft\nSubject: win-back campaign is live\n"
                 "Recommendation: ship it.\n(Standard rubric applied.)\n")
        self.assertEqual(find_fabrications(draft, source_blob(case)), [])

    # --- MINOR: invented names in natural punctuated / designator form escaped ---

    def test_corporate_suffix_name_is_caught(self):
        self.assertIn("Acme, Inc",
                      find_fabrications("Built by Acme, Inc. under contract.", ""))

    def test_designator_name_is_caught(self):
        self.assertIn("Falcon program",
                      find_fabrications("Shipped under the Falcon program.", ""))

    def test_designator_name_present_in_sources_is_not_flagged(self):
        self.assertEqual(
            find_fabrications("Shipped under the Falcon program.",
                              "The Falcon program ships in March."), [])

    # --- MINOR: question count was a LINE count, blind to the draft body ---

    def test_question_count_counts_marks_not_lines(self):
        # Two questions on one line are two questions — a line counter let a stall
        # hide behind formatting.
        self.assertEqual(count_questions("- Who is the reader? What changed?\n"
                                         "## Draft\nx"), 2)

    def test_questions_in_the_draft_body_are_not_counted(self):
        draft = ("- Who is the reader?\n## Draft\nWhy does this matter? Because "
                 "churn is up. Right? Right.\n")
        self.assertEqual(count_questions(draft), 1)

    # --- MINOR: criteria check was a substring test over the whole pre-draft ---

    def test_criteria_named_only_in_prose_do_not_count(self):
        # Prose that merely USES the five words has not named them as criteria.
        pre = ("## Notes\nI thought about style, format, length, content integration "
               "and depth before writing.\n## Draft\nx")
        self.assertEqual(sorted(rdc.missing_criteria_dimensions(pre)),
                         sorted(CRITERIA_DIMENSIONS))


class Discrimination(unittest.TestCase):
    """The planted positive, per case: good passes, bad trips its declared mode."""

    def test_good_draft_passes_every_declared_check(self):
        for c in load_draft_cases()["cases"]:
            viol = {k: v for k, v in run_case_checks(c, c["good_draft"]).items() if v}
            self.assertFalse(viol, f"{c['id']}: good_draft violated {viol}")

    def test_bad_draft_trips_its_declared_failure_mode(self):
        for c in load_draft_cases()["cases"]:
            res = run_case_checks(c, c["bad_draft"])
            self.assertTrue(res[c["failure_mode"]],
                            f"{c['id']}: bad_draft did NOT trip {c['failure_mode']} "
                            f"— the checker cannot catch its own planted failure")

    def test_runner_passes_on_real_data(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            passes, fails = run_deterministic(load_draft_cases())
        self.assertEqual(fails, 0)
        self.assertGreater(passes, 0)


class MainExitCodes(unittest.TestCase):
    """main() must exit 0 on real data and NONZERO on a dataset that has been
    gutted — the proof that the gate can actually go red."""

    def _run_main_on(self, data):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                         encoding="utf-8") as fh:
            json.dump(data, fh)
            path = fh.name
        try:
            buf = io.StringIO()
            with mock.patch.object(rdc, "DRAFT_CASES_PATH", path), \
                    contextlib.redirect_stdout(buf):
                return rdc.main([])
        finally:
            os.unlink(path)

    def test_real_data_exits_zero(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main([])
        self.assertEqual(rc, 0)

    def test_declawed_bad_draft_exits_nonzero(self):
        # Replace a bad_draft with a CLEAN artifact (its good twin). The planted
        # positive no longer trips -> the run must FAIL. This is the test that
        # proves the whole suite is not vacuous.
        data = copy.deepcopy(load_draft_cases())
        data["cases"][0]["bad_draft"] = data["cases"][0]["good_draft"]
        self.assertEqual(self._run_main_on(data), 1)

    def test_poisoned_good_draft_exits_nonzero(self):
        # The mirror direction: a good_draft that invents a fact must fail the run.
        data = copy.deepcopy(load_draft_cases())
        data["cases"][0]["good_draft"] += "\nRevenue grew 47% after the Acme Migration."
        self.assertEqual(self._run_main_on(data), 1)

    def test_empty_cohort_exits_nonzero(self):
        self.assertEqual(self._run_main_on({"cases": []}), 1)

    def test_case_missing_one_side_exits_nonzero(self):
        data = copy.deepcopy(load_draft_cases())
        del data["cases"][1]["bad_draft"]
        self.assertEqual(self._run_main_on(data), 1)


class TypedNumericFabrication(unittest.TestCase):
    """FIX 2 (audit): a number is grounded only when its VALUE and its TYPE both appear
    in the source. Bare-value matching let a supported "3 March" launder an invented
    "$3 million" or "3 November"."""

    SRC = ("We shipped the win-back campaign on 3 March; Priya owns the follow-up. "
           "Q3 churn was 4.1%.")

    def test_currency_magnitude_reusing_a_supported_value_is_flagged(self):
        # "$3 million" reuses the "3" that "3 March" grounds, but the source states no
        # magnitude. AUDIT EVASION 1.
        self.assertIn("3", find_fabrications("The campaign cost $3 million to run.", self.SRC))

    def test_supported_day_with_a_wrong_month_is_flagged(self):
        # "3 November" reuses the supported DAY while changing the month. AUDIT EVASION 2.
        self.assertIn("3", find_fabrications("We shipped it on 3 November.", self.SRC))

    def test_the_supported_date_itself_is_not_flagged(self):
        self.assertEqual(find_fabrications("We shipped on 3 March.", self.SRC), [])

    def test_percent_surface_equivalence_still_holds(self):
        # The typed view must not regress the value-equality policy.
        self.assertEqual(find_fabrications("Churn was 14%.", "Q3 churn was 14 percent."), [])
        self.assertEqual(find_fabrications("Saw 1,000 signups.", "There were 1000 signups."), [])

    def test_typed_claims_expose_kind(self):
        claims = rdc.typed_numeric_claims("on 3 March we spent $3 million, up 4.1%")
        self.assertIn(("date", 3.0, "march"), claims)
        self.assertIn(("qty", 3.0, "million"), claims)
        self.assertIn(("pct", 4.1), claims)


class MutantFamilies(unittest.TestCase):
    """White-box families are cheap smoke. FIX 3: must_catch floor is 100% (no escape
    tolerated); declared gaps are expected_escape, reported out of the denominator."""

    def setUp(self):
        self.cases = load_draft_cases()["cases"]

    def test_must_catch_families_are_all_at_100_percent(self):
        for check, (caught, total) in md.catch_rates(self.cases).items():
            self.assertGreater(total, 0, f"{check}: an empty must_catch family proves nothing")
            self.assertEqual(caught, total,
                             f"{check}: {caught}/{total} must_catch mutants caught — a "
                             f"must_catch escape is a checker gap, not a tolerable rate")

    def test_declared_floor_is_100_percent(self):
        self.assertEqual(md.MUST_CATCH_FLOOR, 1.0)

    def test_families_are_deterministic(self):
        # No RNG, no clock: CI must be byte-reproducible or the catch rate is noise.
        self.assertEqual(md.catch_rates(self.cases), md.catch_rates(self.cases))

    def test_templates_reported_apart_from_instantiations(self):
        # FIX 3: the same template applied to three briefs is one idea, three instances.
        counts = md.template_counts(self.cases)
        uniq, insts = counts["no_fabrication"]
        self.assertGreater(insts, uniq, "instantiations should exceed unique templates "
                                        "when a template runs across multiple cases")

    def test_the_masked_number_mutant_is_derived_from_the_brief(self):
        # The hard member: a value whose digits hide inside a legitimate source number
        # ("50" inside the brief's "150"). It must be DERIVED, not hardcoded.
        case = self.cases[0]
        surface, value = md._masked_value(rdc.numeric_keys(source_blob(case)))
        self.assertIsNotNone(surface)
        self.assertIn(surface, case["brief"])                        # digits hide in the brief
        self.assertNotIn(value, rdc.numeric_keys(source_blob(case)))  # the VALUE does not
        family = {t: art for t, art, _k in md.family_no_fabrication(case)}
        self.assertTrue(CHECKS["no_fabrication"](case, family["number-masked-by-source"]),
                        "the masked-number mutant escaped — the substring bug is back")

    def test_expected_escapes_are_declared_and_still_escape(self):
        # Honesty guard: every declared gap must be tagged expected_escape AND actually
        # escape. If one starts being caught, the checker improved — promote it.
        escapes = md.expected_escapes(self.cases)
        self.assertTrue(escapes, "no declared gaps — the honesty ledger is empty")
        for check, cid, tmpl in escapes:
            case = next(c for c in self.cases if c["id"] == cid)
            family = {t: art for t, art, _k in md.FAMILIES[check](case)}
            self.assertFalse(CHECKS[check](case, family[tmpl]),
                             f"{cid}/{tmpl} is now CAUGHT — move it to must_catch")


class BlackBoxHoldout(unittest.TestCase):
    """FIX 1: the adversarial claim is the black-box holdout, which shares NOTHING with
    the checker. The four audit evasions live here as permanent must-catch entries."""

    def setUp(self):
        self.cases = load_draft_cases()["cases"]

    def test_the_two_draft_audit_evasions_are_caught(self):
        ids = {hid for hid, _c, must, caught in ha.draft_results(self.cases)
               if must and caught}
        for needle in ("currency-magnitude-reuses-supported-value",
                       "supported-day-wrong-month"):
            self.assertTrue(any(needle in i for i in ids),
                            f"audit evasion {needle} not caught by the holdout")

    def test_every_must_catch_holdout_entry_is_caught(self):
        for hid, check, must, caught in ha.draft_results(self.cases):
            if must:
                self.assertTrue(caught, f"holdout {hid} ESCAPED — a closed gap reopened")

    def test_holdout_controls_are_not_flagged(self):
        for hid, check, must, caught in ha.draft_results(self.cases):
            if not must:
                self.assertFalse(caught, f"holdout control {hid} was FALSE-flagged")

    def test_holdout_is_black_box_uses_no_checker_internals(self):
        # The discipline that makes the holdout adversarial: it may touch only public
        # entry points, never the checker's regexes/constants/parse helpers. AST-level,
        # so the module's docstring may NAME the symbols it avoids without tripping this.
        tree = ast.parse(pathlib.Path(ha.__file__).read_text(encoding="utf-8"))
        used = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                used.add(node.attr)
            elif isinstance(node, ast.Name):
                used.add(node.id)
        forbidden = {"_NEEDS_SPAN", "CRITERIA_DIMENSIONS", "_BULLET_LABEL", "_NUMERIC",
                     "_MONTHS", "_MAGNITUDES", "_num_key", "_typed_claim_for_match",
                     "typed_numeric_claims", "numeric_keys", "TRAIT_FEATURES", "_DENIAL",
                     "_CLAUSE_SPLIT", "parse_sections", "mean_sentence_words",
                     "asserted_features", "_CAP_RUN"}
        self.assertEqual(used & forbidden, set(),
                         f"holdout reaches into checker internals: {used & forbidden}")


class JudgeLane(unittest.TestCase):
    """Offline the judge lane SKIPs everything, makes no network call, exits 0."""

    def test_prompt_carries_brief_kb_and_draft(self):
        c = load_draft_cases()["cases"][0]
        p = build_draft_judge_prompt(c, c["bad_draft"])
        self.assertIn(c["brief"], p)
        self.assertIn(c["kb_facts"][0], p)
        self.assertIn("Northwind Retention", p)  # the artifact under judgment
        self.assertIn("no_fabrication", p)

    def test_offline_judge_skips_all_and_makes_no_network_call(self):
        data = load_draft_cases()
        env = {k: v for k, v in os.environ.items() if not k.startswith("AIWS_JUDGE_")}
        buf = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch("urllib.request.urlopen",
                           side_effect=AssertionError("judge lane hit the network")), \
                contextlib.redirect_stdout(buf):
            scored, skipped, live_error = run_judge(data, rdc.new_confusion())
        self.assertEqual(scored, 0)
        self.assertEqual(skipped, 2 * len(data["cases"]))  # good + bad per case
        self.assertFalse(live_error)

    def test_main_with_judge_offline_exits_zero(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith("AIWS_JUDGE_")}
        buf = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch("urllib.request.urlopen",
                           side_effect=AssertionError("judge lane hit the network")), \
                contextlib.redirect_stdout(buf):
            rc = main(["--judge"])
        self.assertEqual(rc, 0)
        self.assertIn("SKIPPED", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
