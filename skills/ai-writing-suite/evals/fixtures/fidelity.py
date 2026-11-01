"""Deterministic fidelity-class checker: catches strength and scope changes that
a literal `must_preserve` substring check cannot see.

WHY: the skill-lift v0 eval (notes/eval-lift-2026-11-01) found that the suite's
only measured lift over no skill is fewer meaning changes, and that bare models
drift on exactly these classes. Examples: "no evidence" softened to "no clear
evidence", "won't be ready until" turned into "expected by". Plan item T1-5
(2026-07-21) proposed this lane and it was never built. This checker covers the
cheap, regex-visible part of it. Judges still own everything subtler.

Scope is deliberately narrow. It compares one before/after pair and reports
`(class, detail)` tuples. It is used only on fixtures that opt in with
`fidelity_check: true` (PASS) or `fidelity_class` (gold-FAIL), because curated
legacy `after`s legitimately rewrite whole sentences.

Classes:
  scope         a scope word in `before` is missing from `after`
  approximator  "about/roughly/~ N" in `before`, but `after` states N bare
  units         "N pp / percentage points" in `before`, but `after` says "N%"
  significance  `before` says not significant / no detectable effect; `after`
                claims no effect and drops the significance wording
  interval      `before` carries a confidence interval; `after` drops it
  strength      a hedged or intent verb in `before` hardens in `after`
                (suggests->shows, may->will, hope/plan to->will, expect->will)
  added_qualification
                `after` adds a defensive qualification `before` never had
                ("does not by itself establish", "interpreted with caution",
                "further research is needed", "not necessarily"); the add-side
                twin of `strength` (Liao et al. 2026: review-flavored prompts
                make models add these, and AI judges reward them)
"""
import re

SCOPE_WORDS = ("only", "all", "most", "every", "never", "first", "at least", "up to")
_APPROX = r"(?:about|roughly|approximately|around|nearly|almost|~)\s*(?:an?\s+)?"
_NUM = r"\d[\d,]*(?:\.\d+)?"
_PP = re.compile(r"(" + _NUM + r")\s*(?:pp\b|percentage points?\b)", re.I)
_PCT = r"\s*%"
_NOT_SIG = re.compile(r"\b(?:not (?:statistically )?significant|no (?:statistically )?significant|no detectable|not detectable)\b", re.I)
_NO_EFFECT = re.compile(r"\b(?:no effect|no impact|had no effect|has no effect|didn't work|did not work|does not work|made no difference|unaffected)\b", re.I)
_INTERVAL = re.compile(r"\b(?:CI|confidence interval|credible interval|interval)\b|±|\+/-", re.I)
_STRENGTH = (
    (re.compile(r"\b(?:suggests?|indicates?|points? to)\b", re.I), re.compile(r"\b(?:shows?|proves?|demonstrates?|confirms?)\b", re.I), "suggests->shows"),
    (re.compile(r"\b(?:may|might|could)\b", re.I), re.compile(r"\bwill\b|\b\w+'ll\b", re.I), "may->will"),
    (re.compile(r"\b(?:hope|plan|aim|intend)s? to\b", re.I), re.compile(r"\bwill\b|\b\w+'ll\b", re.I), "hope/plan to->will"),
    (re.compile(r"\bexpects?\b|\bexpected to\b", re.I), re.compile(r"\bwill\b|\b\w+'ll\b", re.I), "expect->will"),
)


_ADDED_QUAL = re.compile(
    r"\b(?:do(?:es)? not (?:by (?:itself|themselves) |on (?:its|their) own )?(?:establish|prove|imply|guarantee)"
    r"|(?:should|must) be interpreted with caution|interpret(?:ed)? with caution"
    r"|further (?:research|work|analysis|study) (?:is|would be) (?:needed|required|warranted)"
    r"|not necessarily|correlation (?:is not|does not imply) causation"
    r"|(?:by|on) (?:itself|themselves|its own|their own),? (?:this|these|it|they) (?:do|does) not)\b", re.I)


def _has_word(text, w):
    return re.search(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])", text, re.I) is not None


def fidelity_violations(before, after):
    """Return a list of (class, detail) for strength/scope changes from before to after."""
    out = []
    for w in SCOPE_WORDS:
        if _has_word(before, w) and not _has_word(after, w):
            out.append(("scope", f"'{w}' dropped"))
    for m in re.finditer(_APPROX + "(" + _NUM + ")", before, re.I):
        n = m.group(1)
        if re.search(r"(?<![\d.])" + re.escape(n) + r"(?![\d])", after) and not re.search(_APPROX + re.escape(n), after, re.I):
            out.append(("approximator", f"approximate {n} stated as exact"))
    for m in _PP.finditer(before):
        n = m.group(1)
        if re.search(re.escape(n) + _PCT, after) and not re.search(re.escape(n) + r"\s*(?:pp\b|percentage points?\b)", after, re.I):
            out.append(("units", f"{n} percentage points became {n}%"))
    if _NOT_SIG.search(before) and _NO_EFFECT.search(after) and not _NOT_SIG.search(after):
        out.append(("significance", "not significant / not detectable became no effect"))
    if _INTERVAL.search(before) and not _INTERVAL.search(after):
        out.append(("interval", "confidence interval dropped"))
    for weak, strong, label in _STRENGTH:
        if weak.search(before) and not weak.search(after) and strong.search(after) and not strong.search(before):
            out.append(("strength", label))
    added = {m.group(0).lower() for m in _ADDED_QUAL.finditer(after)} - {m.group(0).lower() for m in _ADDED_QUAL.finditer(before)}
    for q in sorted(added):
        out.append(("added_qualification", f"added '{q}'"))
    return out
