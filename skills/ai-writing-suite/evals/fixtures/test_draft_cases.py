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
    """The highest-stakes check in the suite, tested on hand-built inputs so it is
    exercised independently of the shipped artifacts."""

    SOURCES = ("We shipped the win-back campaign on 3 March; Priya owns the "
               "follow-up. Q3 churn was 4.1%.")

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
    def test_question_count_only_counts_pre_draft_lines(self):
        draft = ("## Clarifying questions\n- Who is the reader?\n- What changed?\n"
                 "## Draft\nIs this counted? No — it is in the body.\n")
        self.assertEqual(count_questions(draft), 2)

    def test_missing_criteria_dimensions_needs_all_five(self):
        pre = "\n".join(f"- {d}: something" for d in CRITERIA_DIMENSIONS)
        self.assertEqual(rdc.missing_criteria_dimensions(pre + "\n## Draft\nx"), [])
        self.assertIn("depth", rdc.missing_criteria_dimensions(
            "- style: x\n- format: x\n- length: x\n- content integration: x\n## Draft\nx"))

    def test_source_blob_includes_brief_and_kb(self):
        case = {"brief": "Ship on 3 March.", "kb_facts": ["structure.md: lead with the point."]}
        blob = source_blob(case)
        self.assertIn("3 march", blob)
        self.assertIn("lead with the point", blob)


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
