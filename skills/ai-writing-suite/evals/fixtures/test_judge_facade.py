"""Characterization tests for the judge.evaluate() façade.

Pins the façade to the EXACT pre-refactor lifecycle the runners used to inline:
score() -> parse_dimensions() -> verify_evidence() -> aggregate(). A JudgeResult
must carry byte-identical parsed / verified / verdict / warnings structures to what
the four module-level functions produce on the same raw text — that equality is the
whole safety net for moving run_fixtures / run_draft_cases behind one call. It
catches drift in the CALL SEQUENCE (a dropped step, a wrong argument to aggregate,
a stale rubric_focus) and in raw/parsed/verdict wiring.

Scope note: it does NOT and CANNOT catch a before/after argument swap inside
evaluate()'s call to verify_evidence — verify_evidence is provably symmetric in
its two text arguments (`needle in nb or needle in na`), so swapping before/after
is both undetectable by an equality check AND harmless by design, not a gap in
this test.

Also pins the two load-bearing invariants the review calls out:
  - the AIWS_JUDGE_RUN=1 spend gate is checked BEFORE any network touch, so a stray
    key alone can never bill through the façade;
  - a transport/auth failure stays LOUD (JudgeError propagates), never a silent SKIP.

Fully offline, stdlib-only, canned strings (mock urlopen) — same style as
test_judge_protocol.py, runs in CI via run_all.sh step 1.
"""

import io
import json
import os
import unittest
from unittest import mock

from fixtures import judge


# A multi-dimension verdict exercising every evidence branch: one verbatim-ok quote,
# one well-formed-but-fabricated quote (not_verbatim), one graded dim with no quote
# (a warning), and one N/A. no_fabrication is graded so aggregate() has a load-bearing
# dim to weigh. Quotes are chosen so BEFORE/AFTER below decide verbatim vs not.
_MODEL_TEXT = (
    'meaning_preserved: PASS — kept | EVIDENCE: "the API migration slipped"\n'
    'no_fabrication: PASS — clean | EVIDENCE: "cut latency by 37%"\n'
    "tells_removed: PASS — human\n"
    "payoff_clear: N/A — nothing removed\n"
    "VERDICT: PASS"
)
_BEFORE = "We're behind on Q3 by 14% because the API migration slipped."
_AFTER = "We're behind on Q3; the API migration slipped three weeks."
_FOCUS = ["meaning_preserved", "tells_removed"]


def _canned_response(text):
    payload = {"choices": [{"message": {"content": text}}]}
    resp = mock.MagicMock()
    resp.read.return_value = json.dumps(payload).encode("utf-8")
    resp.__enter__.return_value = resp
    resp.__exit__.return_value = False
    return resp


_CONFIGURED_ENV = {
    "AIWS_JUDGE_URL": "https://x/v1/chat/completions",
    "AIWS_JUDGE_MODEL": "gpt-4o",
    "AIWS_JUDGE_KEY": "k",
    "AIWS_JUDGE_RUN": "1",
}


class FacadeMatchesInlinedLifecycle(unittest.TestCase):
    """result fields == the four functions run by hand on the same raw text."""

    def test_result_is_byte_identical_to_manual_pipeline(self):
        req = judge.JudgeRequest(prompt="p", before=_BEFORE, after=_AFTER,
                                 rubric_focus=_FOCUS)
        with mock.patch.dict(os.environ, _CONFIGURED_ENV, clear=True), \
                mock.patch("urllib.request.urlopen",
                           return_value=_canned_response(_MODEL_TEXT)):
            result = judge.evaluate(req)

        # The pre-refactor path, reproduced verbatim from the model text.
        raw = _MODEL_TEXT
        parsed = judge.parse_dimensions(raw)
        verified = judge.verify_evidence(parsed, _BEFORE, _AFTER)
        verdict = judge.aggregate([judge.parse_dimension_lines(raw)], _FOCUS)
        warnings = judge.evidence_warnings(raw)

        self.assertTrue(result.configured)
        self.assertEqual(result.raw, raw)
        self.assertEqual(result.parsed, parsed)
        self.assertEqual(result.verified, verified)
        self.assertEqual(result.verdict, verdict)
        self.assertEqual(result.warnings, warnings)

    def test_verified_and_warnings_have_real_content(self):
        # Guard the guard: prove the byte-compare above isn't trivially over empty
        # structures. This canned verdict must actually surface a not_verbatim quote
        # and an uncited graded dim.
        req = judge.JudgeRequest(prompt="p", before=_BEFORE, after=_AFTER,
                                 rubric_focus=_FOCUS)
        with mock.patch.dict(os.environ, _CONFIGURED_ENV, clear=True), \
                mock.patch("urllib.request.urlopen",
                           return_value=_canned_response(_MODEL_TEXT)):
            result = judge.evaluate(req)
        self.assertEqual(result.verified["meaning_preserved"], "ok")
        self.assertEqual(result.verified["no_fabrication"], "not_verbatim")
        self.assertIn("tells_removed", result.warnings)  # graded, no quote
        self.assertEqual(result.verdict, "PASS")


class SpendGateCheckedBeforeNetwork(unittest.TestCase):
    """AIWS_JUDGE_RUN != "1" (or missing credentials) -> SKIP result, NO POST."""

    def test_run_flag_off_returns_skip_without_network(self):
        env = dict(_CONFIGURED_ENV)
        env.pop("AIWS_JUDGE_RUN")  # key present, but not opted in to spend
        boom = mock.Mock(side_effect=AssertionError("network touched while gated"))
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch("urllib.request.urlopen", boom):
            result = judge.evaluate(judge.JudgeRequest(prompt="p"))
        self.assertFalse(result.configured)
        self.assertIsNone(result.raw)
        self.assertIsNone(result.verdict)
        self.assertEqual(result.parsed, {})
        self.assertEqual(result.verified, {})
        self.assertEqual(result.warnings, [])
        boom.assert_not_called()

    def test_no_env_at_all_returns_skip_without_network(self):
        boom = mock.Mock(side_effect=AssertionError("network touched offline"))
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch("urllib.request.urlopen", boom):
            result = judge.evaluate(judge.JudgeRequest(prompt="p"))
        self.assertFalse(result.configured)
        self.assertIsNone(result.verdict)
        boom.assert_not_called()


class TransportFailureStaysLoud(unittest.TestCase):
    """A provider error must propagate as JudgeError, never a quiet SKIP result."""

    def test_http_error_raises_through_evaluate(self):
        import urllib.error
        err = urllib.error.HTTPError("https://x", 401, "unauth", {}, None)
        with mock.patch.dict(os.environ, _CONFIGURED_ENV, clear=True), \
                mock.patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaises(judge.JudgeError):
                judge.evaluate(judge.JudgeRequest(prompt="p"))


class ConfiguredButNoTextIsSkip(unittest.TestCase):
    """A 200 whose envelope carries no extractable text -> raw None, verdict None
    (the caller treats it as unparseable; run_judge's liveness check turns an all-None
    run loud). parsed/verified/warnings stay empty."""

    def test_empty_envelope_gives_skip_result(self):
        empty = mock.MagicMock()
        empty.read.return_value = json.dumps({"choices": []}).encode("utf-8")
        empty.__enter__.return_value = empty
        empty.__exit__.return_value = False
        with mock.patch.dict(os.environ, _CONFIGURED_ENV, clear=True), \
                mock.patch("urllib.request.urlopen", return_value=empty):
            result = judge.evaluate(judge.JudgeRequest(prompt="p", rubric_focus=_FOCUS))
        self.assertTrue(result.configured)
        self.assertIsNone(result.raw)
        self.assertIsNone(result.verdict)
        self.assertEqual(result.parsed, {})


if __name__ == "__main__":
    unittest.main()
