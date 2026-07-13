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


class PairedQuoteParsing(unittest.TestCase):
    """The FIX-1 paired-quote parser: a contraction inside the quote must survive
    (the old non-greedy regex closed on the apostrophe, truncating 'We're' to 'We'),
    and status distinguishes ok / missing / malformed."""

    def test_contraction_inside_quote_parses_whole(self):
        line = ('meaning_preserved: FAIL — dropped the number | '
                'EVIDENCE: "We\'re behind by 14%"')
        rec = judge.parse_dimensions(line)["meaning_preserved"]
        self.assertEqual(rec["evidence"], "We're behind by 14%")
        self.assertEqual(rec["evidence_status"], "ok")
        self.assertFalse(rec["evidence_missing"])

    def test_smart_quotes_with_apostrophe_inside(self):
        line = 'voice_kept: PASS — human | EVIDENCE: “don’t ship on a Friday”'
        rec = judge.parse_dimensions(line)["voice_kept"]
        self.assertEqual(rec["evidence"], "don’t ship on a Friday")
        self.assertEqual(rec["evidence_status"], "ok")

    def test_unpaired_quote_is_malformed(self):
        rec = judge.parse_dimensions('genre_fit: PASS — fits | EVIDENCE: "unclosed')
        rec = rec["genre_fit"]
        self.assertIsNone(rec["evidence"])
        self.assertEqual(rec["evidence_status"], "malformed")
        self.assertTrue(rec["evidence_missing"])

    def test_empty_quote_is_malformed(self):
        rec = judge.parse_dimensions('genre_fit: PASS — fits | EVIDENCE: ""')["genre_fit"]
        self.assertEqual(rec["evidence_status"], "malformed")
        self.assertTrue(rec["evidence_missing"])

    def test_graded_line_without_evidence_is_missing(self):
        rec = judge.parse_dimensions("tells_removed: FAIL — still robotic")["tells_removed"]
        self.assertEqual(rec["evidence_status"], "missing")
        self.assertTrue(rec["evidence_missing"])

    def test_na_line_status_ok_never_flagged(self):
        rec = judge.parse_dimensions("payoff_clear: N/A — nothing removed")["payoff_clear"]
        self.assertEqual(rec["evidence_status"], "ok")
        self.assertFalse(rec["evidence_missing"])

    def test_multiline_model_text_parses_each_line(self):
        text = ('meaning_preserved: PASS — kept | EVIDENCE: "shipped 3 fixes"\n'
                'no_fabrication: FAIL — invented | EVIDENCE: "cut load by 37%"\n'
                'VERDICT: FAIL')
        dims = judge.parse_dimensions(text)
        self.assertEqual(dims["meaning_preserved"]["evidence"], "shipped 3 fixes")
        self.assertEqual(dims["no_fabrication"]["evidence"], "cut load by 37%")
        self.assertNotIn("verdict", dims)  # self-reported line ignored


class VerifyEvidence(unittest.TestCase):
    """judge.verify_evidence: a well-formed quote that appears nowhere in the
    before/after is 'not_verbatim' — the fabrication the parser alone can't catch."""

    BEFORE = "We're behind on Q3 by 14% because the API migration slipped."
    AFTER = "We're behind on Q3; the API migration slipped three weeks."

    def test_verbatim_quote_from_before_is_ok(self):
        line = 'meaning_preserved: PASS — kept | EVIDENCE: "the API migration slipped"'
        parsed = judge.parse_dimensions(line)
        self.assertEqual(judge.verify_evidence(parsed, self.BEFORE, self.AFTER),
                         {"meaning_preserved": "ok"})

    def test_hallucinated_quote_is_not_verbatim(self):
        line = 'no_fabrication: PASS — clean | EVIDENCE: "cut latency by 37%"'
        parsed = judge.parse_dimensions(line)
        self.assertEqual(judge.verify_evidence(parsed, self.BEFORE, self.AFTER),
                         {"no_fabrication": "not_verbatim"})

    def test_whitespace_normalized_match(self):
        # A quote whose internal whitespace differs from the source (newline/extra
        # spaces) still matches — the check is whitespace-normalized, not byte-exact.
        before = "We shipped   three\n   fixes on Tuesday."
        line = 'x_dim: PASS — kept | EVIDENCE: "We shipped three fixes on Tuesday"'
        parsed = judge.parse_dimensions(line)
        self.assertEqual(judge.verify_evidence(parsed, before, ""),
                         {"x_dim": "ok"})

    def test_missing_and_na_dims_omitted(self):
        # Only dims with a usable (status ok) quote are verified; missing/malformed/
        # N/A dims are absent from the result (nothing to check).
        text = ("tells_removed: FAIL — robotic\n"           # missing quote
                "payoff_clear: N/A — nothing removed\n"       # N/A
                'meaning_preserved: PASS — kept | EVIDENCE: "the API migration slipped"')
        parsed = judge.parse_dimensions(text)
        self.assertEqual(judge.verify_evidence(parsed, self.BEFORE, self.AFTER),
                         {"meaning_preserved": "ok"})


class EvidenceWarningsEdgeCases(unittest.TestCase):
    """FIX-8: evidence_warnings must not crash on degenerate model_text and must
    stay silent when there is nothing gradeable to warn about."""

    def test_empty_string_warns_nothing(self):
        self.assertEqual(judge.evidence_warnings(""), [])

    def test_none_ish_input_warns_nothing(self):
        self.assertEqual(judge.evidence_warnings(None), [])
        self.assertEqual(judge.evidence_warnings(12345), [])

    def test_all_na_text_warns_nothing(self):
        text = ("overstepping_removed: N/A — nothing removed\n"
                "payoff_clear: N/A — nothing removed")
        self.assertEqual(judge.evidence_warnings(text), [])


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
