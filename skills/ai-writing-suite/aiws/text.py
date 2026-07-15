"""aiws.text — the shared text-analysis seam.

The seam deliberately preserves the three consumers' existing measurement
policies.  Their regexes look similar, but they are not interchangeable:
detector scoring, voice extraction, and stylometry each have calibrated behavior
behind their current splitter.  Keep the primitives separate until a policy
change explicitly recalibrates those consumers.

``segment()`` is the v1 whitespace/Latin implementation.  It uses only the
detector-family token, word, sentence, and paragraph primitives below.  Text
whose alphabetic characters are at least 20% CJK follows an explicit
unsupported-script path; a real CJK implementation belongs to the later
multilingual stage, not an adapter hierarchy here.

Stdlib only.  ``aiws`` imports from neither ``evals/`` nor ``tools/``
(architecture review 2026-07-13, item 3).
"""

import re


# Detector semantics.  These are the detector's calibrated regexes/splitters;
# do not replace them with either of the consumer-specific patterns below.
WORD_RE = re.compile(r"\S+")
TOKEN_RE = re.compile(r"[\w'-]+")


def tokenize(text):
    """Return the detector's lowercased token stream."""
    return TOKEN_RE.findall(text.lower())


def count_words(text):
    """Return the detector's whitespace-delimited word count."""
    return len(WORD_RE.findall(text))


def split_paragraphs(text):
    """Return the detector's nonblank paragraphs."""
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


def split_sentences(text):
    """Return the detector's score-bearing sentence spans."""
    return [s for s in re.split(r"[.!?]+", text) if len(s.strip()) > 5]


# Voice-extraction semantics.  Clause boundaries include sentence stops,
# semicolons, and dash separators.  A hyphen inside "em-dash" is NOT a clause
# boundary: only a SPACED hyphen or a real en/em dash separates clauses.
VOICE_TOKEN = re.compile(r"[a-z0-9'’]+")
CLAUSE_SPLIT = re.compile(r"[.;]|—|–|\s-\s")

# Stylometry semantics: whitespace-script sentence stops consume the following
# whitespace (or the end of the string).  This is intentionally not the
# detector sentence splitter above.
SENT_SPLIT = re.compile(r"[.!?]+(?:\s+|$)")

# CJK / Hangul / Hiragana / Katakana codepoint ranges and refusal threshold,
# ported from _shared/stylometry.py.  Do not change the threshold without an
# explicit measurement-policy version change.
_CJK_RE = re.compile("[぀-ヿ㐀-䶿一-鿿가-힯ｦ-ﾟ]")
_CJK_THRESHOLD = 0.20


class TextDocument:
    """One segmented text and its script-support status.

    ``tokens``, ``sentences``, and ``paragraphs`` preserve detector list
    semantics.  ``words`` is the detector's whitespace-delimited word count.
    Unsupported CJK-dominant input carries empty measurements rather than
    authoritative-looking values from an unsuitable tokenizer.
    """

    __slots__ = ("script_class", "support_status", "tokens", "sentences",
                 "words", "paragraphs")

    def __init__(self, script_class, support_status, tokens, sentences, words,
                 paragraphs):
        self.script_class = script_class
        self.support_status = support_status
        self.tokens = tokens
        self.sentences = sentences
        self.words = words
        self.paragraphs = paragraphs

    def __repr__(self):
        return (f"TextDocument(script_class={self.script_class!r}, "
                f"support_status={self.support_status!r}, "
                f"tokens={self.tokens!r}, sentences={self.sentences!r}, "
                f"words={self.words!r}, paragraphs={self.paragraphs!r})")

    def __eq__(self, other):
        return isinstance(other, TextDocument) and self._key() == other._key()

    def _key(self):
        return (self.script_class, self.support_status, self.tokens,
                self.sentences, self.words, self.paragraphs)


def _cjk_share(text):
    """Fraction of alphabetic characters that are CJK-script; 0 with none."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    cjk = sum(1 for c in letters if _CJK_RE.match(c))
    return cjk / len(letters)


def segment(text, language="auto"):
    """Return a v1 detector-semantics ``TextDocument`` for ``text``.

    ``language`` reserves the stable seam argument for the multilingual stage;
    v1 intentionally has one implementation and no language plugin dispatch.
    """
    del language  # v1 has exactly one implementation; no plugin dispatch.

    cjk_share = _cjk_share(text)
    if cjk_share >= _CJK_THRESHOLD:
        return TextDocument("CJK", "unsupported script", [], [], 0, [])

    script_class = "mixed Latin/CJK" if cjk_share else "Latin"
    support_status = "partial script" if cjk_share else "supported"
    return TextDocument(
        script_class,
        support_status,
        tokenize(text),
        split_sentences(text),
        count_words(text),
        split_paragraphs(text),
    )
