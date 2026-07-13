"""Unit tests for the quoted-evidence judge protocol + cross-family warning.

Fully offline, stdlib-only, canned strings — no network, no key, runs in CI via
`run_all.sh` step 1 (`unittest discover -p 'test_*.py'`). Guards the additions in
judge.py:
  - parse_dimensions(): the EVIDENCE quote is extracted; a graded verdict with no
    quote is flagged (evidence_missing) but stays VALID, never fatal;
  - parse_dimension_lines(): still returns the plain {dim: verdict} shape after the
    rich-parser refactor (old-format lines unchanged) — the compat gate;
  - model_family() prefix mapping and same_family_warning() same/cross detection.

test_fixtures.py owns the aggregate()/verdict semantics; this file owns evidence
+ family only, so the two suites don't overlap.
"""

import io
import os
import unittest
from unittest import mock

from fixtures import judge


class EvidenceParsing(unittest.TestCase):
    def test_evidence_quote_extracted(self):
        line = ('meaning_preserved: PASS — every fact kept | '
                'EVIDENCE: "we shipped 3 fixes on Tuesday"')
        rec = judge.parse_dimensions(line)["meaning_preserved"]
        self.assertEqual(rec["verdict"], "PASS")
        self.assertEqual(rec["evidence"], "we shipped 3 fixes on Tuesday")
        self.assertFalse(rec["evidence_missing"])

    def test_smart_quotes_extracted(self):
        line = 'tells_removed: FAIL — still robotic | EVIDENCE: “leverage synergies”'
        rec = judge.parse_dimensions(line)["tells_removed"]
        self.assertEqual(rec["evidence"], "leverage synergies")
        self.assertFalse(rec["evidence_missing"])

    def test_evidence_keeps_own_punctuation_despite_bold(self):
        # Bold/bullets are cleaned off the VERDICT half, but evidence is read from
        # the raw line so an asterisk inside the quote survives.
        line = '- **voice_kept**: PASS — human | EVIDENCE: "ship it *now*"'
        rec = judge.parse_dimensions(line)["voice_kept"]
        self.assertEqual(rec["verdict"], "PASS")
        self.assertEqual(rec["evidence"], "ship it *now*")


class EvidenceMissingIsAdvisory(unittest.TestCase):
    def test_graded_line_without_evidence_flagged_not_fatal(self):
        text = ("meaning_preserved: PASS — facts kept\n"
                "no_fabrication: PASS — nothing invented")
        dims = judge.parse_dimensions(text)
        self.assertTrue(dims["meaning_preserved"]["evidence_missing"])
        self.assertTrue(dims["no_fabrication"]["evidence_missing"])
        # Advisory: the verdict still computes normally, no crash, no auto-FAIL.
        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
                                  ["meaning_preserved"])
        self.assertEqual(verdict, "PASS")

    def test_evidence_warnings_lists_only_uncited_graded_dims(self):
        text = ('meaning_preserved: PASS — kept | EVIDENCE: "the 3 fixes"\n'
                "tells_removed: FAIL — robotic\n"
                "payoff_clear: N/A — nothing removed\n"
                "no_fabrication: PASS — clean")
        self.assertEqual(sorted(judge.evidence_warnings(text)),
                         ["no_fabrication", "tells_removed"])

    def test_na_line_never_flagged_missing(self):
        rec = judge.parse_dimensions("payoff_clear: N/A — no presumption removed")
        self.assertEqual(rec["payoff_clear"]["verdict"], "N/A")
        self.assertIsNone(rec["payoff_clear"]["evidence"])
        self.assertFalse(rec["payoff_clear"]["evidence_missing"])

    def test_empty_quote_counts_as_missing(self):
        rec = judge.parse_dimensions('genre_fit: PASS — fits | EVIDENCE: ""')
        self.assertIsNone(rec["genre_fit"]["evidence"])
        self.assertTrue(rec["genre_fit"]["evidence_missing"])


class BackwardCompatibleProjection(unittest.TestCase):
    """parse_dimension_lines must keep returning the plain {dim: verdict} shape
    test_fixtures.py depends on — for both old (no-evidence) and new lines."""

    def test_old_format_unchanged(self):
        text = ("meaning_preserved: PASS — facts kept\n"
                "no_fabrication: FAIL — invented a 2GB figure\n"
                "VERDICT: PASS")
        self.assertEqual(judge.parse_dimension_lines(text),
                         {"meaning_preserved": "PASS", "no_fabrication": "FAIL"})

    def test_new_evidence_line_projects_to_verdict_only(self):
        line = 'voice_kept: PASS — human | EVIDENCE: "ship it"'
        self.assertEqual(judge.parse_dimension_lines(line), {"voice_kept": "PASS"})

    def test_na_and_markdown_still_normalize(self):
        self.assertEqual(judge.parse_dimension_lines("- **payoff_clear**: NA"),
                         {"payoff_clear": "N/A"})


class ModelFamilyMapping(unittest.TestCase):
    def test_known_prefixes(self):
        cases = {
            "claude-opus-4-8": "anthropic",
            "gpt-4o-mini": "openai",
            "gpt-5.5": "openai",
            "o3-mini": "openai",
            "o1-preview": "openai",
            "gemini-2.0-flash": "google",
            "gemma-2-9b": "google",
            "llama-3.1-70b": "meta",
            "mistral-large": "mistral",
            "mixtral-8x7b": "mistral",
            "deepseek-chat": "deepseek",
            "qwen2.5-72b": "qwen",
            "grok-2": "xai",
        }
        for model, family in cases.items():
            self.assertEqual(judge.model_family(model), family, model)

    def test_provider_prefix_stripped(self):
        self.assertEqual(judge.model_family("anthropic/claude-3-5-sonnet"),
                         "anthropic")
        self.assertEqual(judge.model_family("openai/gpt-4o"), "openai")

    def test_unknown_and_empty(self):
        self.assertEqual(judge.model_family("some-random-model"), "unknown")
        self.assertEqual(judge.model_family(""), "unknown")
        self.assertEqual(judge.model_family(None), "unknown")


class SameFamilyDetection(unittest.TestCase):
    def test_same_family_warns(self):
        msg = judge.same_family_warning("claude-opus-4-8", "claude-3-5-sonnet")
        self.assertIsNotNone(msg)
        self.assertIn("same family (anthropic)", msg)

    def test_openai_variants_share_family(self):
        # gpt judging o-series output is still same-vendor self-preference.
        self.assertIsNotNone(judge.same_family_warning("gpt-4o", "o3-mini"))

    def test_cross_family_no_warning(self):
        self.assertIsNone(judge.same_family_warning("claude-opus-4-8", "gpt-4o"))

    def test_missing_rewriter_disables_check(self):
        self.assertIsNone(judge.same_family_warning("claude-opus-4-8", None))
        self.assertIsNone(judge.same_family_warning("claude-opus-4-8", ""))

    def test_unknown_family_never_warns(self):
        # Two unrecognized ids must not warn — "unknown == unknown" is not evidence
        # of a shared family, just of a classifier miss.
        self.assertIsNone(judge.same_family_warning("mystery-a", "mystery-b"))


class ScoreEmitsWarningOnce(unittest.TestCase):
    """The once-per-process stderr warning, exercised offline (mock urlopen)."""

    def setUp(self):
        judge._FAMILY_WARNING_EMITTED = False
        self.addCleanup(setattr, judge, "_FAMILY_WARNING_EMITTED", False)

    def _fake_response(self):
        payload = {"choices": [{"message": {"content": "voice_kept: PASS"}}]}
        resp = mock.MagicMock()
        resp.read.return_value = __import__("json").dumps(payload).encode()
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = False
        return resp

    def test_same_family_warns_once_across_two_score_calls(self):
        env = {"AIWS_JUDGE_URL": "https://x/v1", "AIWS_JUDGE_MODEL": "claude-opus-4-8",
               "AIWS_JUDGE_KEY": "k", "AIWS_JUDGE_RUN": "1",
               "AIWS_REWRITER_MODEL": "claude-3-5-sonnet"}
        buf = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch("urllib.request.urlopen",
                           return_value=self._fake_response()), \
                mock.patch("sys.stderr", buf):
            judge.score("p1")
            judge.score("p2")
        self.assertEqual(buf.getvalue().count("same family"), 1)

    def test_cross_family_emits_nothing(self):
        env = {"AIWS_JUDGE_URL": "https://x/v1", "AIWS_JUDGE_MODEL": "claude-opus-4-8",
               "AIWS_JUDGE_KEY": "k", "AIWS_JUDGE_RUN": "1",
               "AIWS_REWRITER_MODEL": "gpt-4o"}
        buf = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch("urllib.request.urlopen",
                           return_value=self._fake_response()), \
                mock.patch("sys.stderr", buf):
            judge.score("p1")
        self.assertEqual(buf.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
