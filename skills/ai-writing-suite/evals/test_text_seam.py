"""Parity and contract tests for the item-3 text-analysis seam.

The parity oracles below locally recompile the original consumer regexes.  They
must not import those patterns from ``aiws.text``: a seam test that compares a
primitive with itself would pass after a behavior-changing edit.
"""

import importlib
import json
import os
import re
import sys
import unittest


# evals/ -> <suite-root>, so ``import aiws`` resolves to the sibling package.
_SUITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SUITE_ROOT not in sys.path:
    sys.path.insert(0, _SUITE_ROOT)

from aiws.text import (  # noqa: E402  (path set above)
    CLAUSE_SPLIT,
    SENT_SPLIT,
    TOKEN_RE,
    VOICE_TOKEN,
    WORD_RE,
    count_words,
    segment,
    split_paragraphs,
    split_sentences,
    tokenize,
)


FIXTURES = os.path.join(_SUITE_ROOT, "evals", "fixtures", "fixtures.json")
CJK_SAMPLE = "这是一个中文测试。它没有用空格分词。"

# Original detector.py patterns and splitters.
ORIGINAL_WORD_RE = re.compile(r"\S+")
ORIGINAL_TOKEN_RE = re.compile(r"[\w'-]+")

# Original run_voice_extraction.py patterns.
ORIGINAL_VOICE_TOKEN = re.compile(r"[a-z0-9'’]+")
ORIGINAL_CLAUSE_SPLIT = re.compile(r"[.;]|—|–|\s-\s")

# Original _shared/stylometry.py sentence splitter.
ORIGINAL_SENT_SPLIT = re.compile(r"[.!?]+(?:\s+|$)")


def _original_tokenize(text):
    return ORIGINAL_TOKEN_RE.findall(text.lower())


def _original_count_words(text):
    return len(ORIGINAL_WORD_RE.findall(text))


def _original_split_paragraphs(text):
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


def _original_split_sentences(text):
    return [s for s in re.split(r"[.!?]+", text) if len(s.strip()) > 5]


class TextPrimitiveParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(FIXTURES, encoding="utf-8") as fh:
            fixture_data = json.load(fh)["fixtures"]
        # Four repo fixtures provide eight before/after samples across tweet and
        # LinkedIn prose; the explicit CJK case exercises Unicode behavior too.
        cls.corpus = [
            text
            for fixture in fixture_data[:4]
            for text in (fixture["before"], fixture["after"])
        ] + [CJK_SAMPLE]

    def test_detector_primitives_match_originals(self):
        for text in self.corpus:
            with self.subTest(text=text[:50]):
                self.assertEqual(WORD_RE.findall(text),
                                 ORIGINAL_WORD_RE.findall(text))
                self.assertEqual(TOKEN_RE.findall(text),
                                 ORIGINAL_TOKEN_RE.findall(text))
                self.assertEqual(tokenize(text), _original_tokenize(text))
                self.assertEqual(count_words(text),
                                 _original_count_words(text))
                self.assertEqual(split_paragraphs(text),
                                 _original_split_paragraphs(text))
                self.assertEqual(split_sentences(text),
                                 _original_split_sentences(text))

    def test_voice_extraction_primitives_match_originals(self):
        for text in self.corpus:
            with self.subTest(text=text[:50]):
                self.assertEqual(VOICE_TOKEN.findall(text),
                                 ORIGINAL_VOICE_TOKEN.findall(text))
                self.assertEqual(CLAUSE_SPLIT.split(text),
                                 ORIGINAL_CLAUSE_SPLIT.split(text))

    def test_stylometry_sentence_splitter_matches_original(self):
        for text in self.corpus:
            with self.subTest(text=text[:50]):
                self.assertEqual(SENT_SPLIT.split(text),
                                 ORIGINAL_SENT_SPLIT.split(text))

    def test_compiled_primitives_identical_to_originals(self):
        primitives = (
            ("WORD_RE", WORD_RE, ORIGINAL_WORD_RE),
            ("TOKEN_RE", TOKEN_RE, ORIGINAL_TOKEN_RE),
            ("VOICE_TOKEN", VOICE_TOKEN, ORIGINAL_VOICE_TOKEN),
            ("CLAUSE_SPLIT", CLAUSE_SPLIT, ORIGINAL_CLAUSE_SPLIT),
            ("SENT_SPLIT", SENT_SPLIT, ORIGINAL_SENT_SPLIT),
        )
        for name, compiled, original in primitives:
            with self.subTest(primitive=name):
                self.assertEqual(
                    (compiled.pattern, compiled.flags),
                    (original.pattern, original.flags),
                )


class SegmentContract(unittest.TestCase):
    def test_segment_uses_detector_counts(self):
        text = ("One short line. Another longer line!\n\n"
                "Third paragraph here?")
        document = segment(text)

        self.assertEqual(document.script_class, "Latin")
        self.assertEqual(document.support_status, "supported")
        self.assertEqual(document.tokens, _original_tokenize(text))
        self.assertEqual(document.words, 9)
        self.assertEqual(len(document.sentences), 3)
        self.assertEqual(len(document.paragraphs), 2)

    def test_cjk_dominant_text_is_explicitly_unsupported(self):
        document = segment(CJK_SAMPLE)

        self.assertEqual(document.script_class, "CJK")
        self.assertEqual(document.support_status, "unsupported script")
        self.assertEqual(document.tokens, [])
        self.assertEqual(document.sentences, [])
        self.assertEqual(document.words, 0)
        self.assertEqual(document.paragraphs, [])

    def test_cjk_refusal_boundary_matches_stylometry(self):
        # One CJK letter among five alphabetic characters is exactly 20% and
        # must refuse; one among six remains the explicit partial-script path.
        self.assertEqual(segment("界abcd").support_status,
                         "unsupported script")
        partial = segment("界abcde")
        self.assertEqual(partial.script_class, "mixed Latin/CJK")
        self.assertEqual(partial.support_status, "partial script")


class StylometrySyncPin(unittest.TestCase):
    """stylometry.py stays self-contained for portability (it ships inside
    _shared/ to end users, stdlib-only, zero intra-repo imports), so it keeps
    its own copy of the sentence splitter instead of importing the seam.
    This pin makes silent drift impossible: if either copy changes, the other
    must change with it (or this test goes red and forces the conversation)."""

    def test_sent_split_pattern_and_flags_identical_to_stylometry(self):
        import os, sys
        shared = os.path.join(os.path.dirname(__file__), "..", "_shared")
        sys.path.insert(0, os.path.abspath(shared))
        try:
            import stylometry
        finally:
            sys.path.pop(0)
        from aiws.text import SENT_SPLIT
        self.assertEqual(
            (SENT_SPLIT.pattern, SENT_SPLIT.flags),
            (stylometry._SENT_SPLIT.pattern, stylometry._SENT_SPLIT.flags),
        )

    def test_cjk_pattern_and_flags_identical_to_stylometry(self):
        import os, sys
        shared = os.path.join(os.path.dirname(__file__), "..", "_shared")
        sys.path.insert(0, os.path.abspath(shared))
        try:
            import stylometry
        finally:
            sys.path.pop(0)
        from aiws.text import _CJK_RE
        self.assertEqual(
            (_CJK_RE.pattern, _CJK_RE.flags),
            (stylometry._CJK_RE.pattern, stylometry._CJK_RE.flags),
        )


class DetectorImportSmoke(unittest.TestCase):
    def test_run_all_supported_import_paths(self):
        evals_root = os.path.join(_SUITE_ROOT, "evals")
        added_evals_root = evals_root not in sys.path
        if added_evals_root:
            # run_all.sh changes into evals/, which makes this import spelling
            # available through the working-directory entry on sys.path.
            sys.path.insert(0, evals_root)
        try:
            direct = importlib.import_module("detector.detector")
        finally:
            if added_evals_root:
                sys.path.pop(0)

        # evals/ has no __init__.py, but it is a supported implicit namespace
        # package because _SUITE_ROOT is on sys.path.
        packaged = importlib.import_module("evals.detector.detector")

        self.assertTrue(callable(direct.analyze))
        self.assertTrue(callable(packaged.analyze))
        self.assertEqual(direct.__file__, packaged.__file__)


if __name__ == "__main__":
    unittest.main()
