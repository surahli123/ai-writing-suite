#!/usr/bin/env python3
"""stylometry.py — quantitative voice fingerprint (stdlib-only, per-genre).

WHAT THIS IS
------------
A deterministic measurement pass for `voice-onboard`. Given >=3 writing samples
of a SINGLE genre, it computes a numeric fingerprint of the author's style:
sentence-length rhythm (variance is the signal), function-word deltas vs a
shipped generic baseline, a character 3-gram profile, punctuation density,
testable-number density, and AI-register absences. Every number it emits is
recomputable from the samples + the constants in this file, which is the whole
point: it lets `evals/test_voice_contract.py` assert on NUMBERS instead of
parsing prose for polarity (see reviews/2026-07-13-advisor-eval-method.md Q3c).

WHY PER GENRE (HARD CONSTRAINT)
-------------------------------
voice-onboard forbids averaging across genres ("Don't average across genres —
mixed samples -> split, don't flatten"). A tweet and a report have different
sentence rhythm; pooling them yields a blended mean/variance that describes
NEITHER genre. So this module computes ONE fingerprint per genre. The public
entry `compute_per_genre({genre: [samples]})` never pools; `compute_fingerprint`
operates on one genre's list. Pooling two genres deliberately produces a
different (wrong) answer — that is demonstrated by `--demo`.

WHY THESE SIGNALS
-----------------
- sentence-length VARIANCE / burstiness: human rhythm is irregular; the mean
  alone is a weak, easily-faked signal. Coefficient of variation (stdev/mean)
  captures "short punchy line, then a long qualifier".
- function-word deltas: the classic authorship-attribution signal (function
  words are topic-independent and unconsciously used). See BASELINE_RATES below
  for the baseline's origin and limits.
- character 3-grams: robust, cheap, lexicon-free fingerprint (Kešelj et al.,
  2003). Captures sub-word habits (morphology, spacing, punctuation runs) that a
  word list misses. 3 is the standard sweet spot for English.
- punctuation density (em-dash / semicolon / ellipsis / exclamation per 1k
  words): rossmann/unslop both treat punctuation rhythm as voice, not noise.
- testable-number density (concrete figures per 100 words): rossmann's core
  signal — "testable-number density ... not adjectives".
- AI-register absences: per voice-onboard, a word someone NEVER writes is the
  strongest signal. We count AI-register words (delve, leverage, tapestry, ...);
  ZERO occurrences is the fingerprint, a nonzero count is a red flag.

CJK / NON-WHITESPACE SCRIPTS  (honest limitation, not garbage)
--------------------------------------------------------------
Word counting here assumes WHITESPACE-DELIMITED scripts (same limitation the
detector documents, review note m4). Chinese/Japanese/Thai have no inter-word
spaces and different sentence terminators, so whitespace tokenization collapses
to a tiny word count and every per-word / per-sentence rate becomes garbage.
Rather than emit authoritative-looking wrong numbers, this module DETECTS a
predominantly-CJK genre (>=20% CJK letters) and returns an explicit unsupported
marker (`supported=False, script="CJK"`) with NO numeric fingerprint. Bilingual/CJK
stylometry is v2 (consistent with voice-onboard + the detector, which both scope
bilingual to v2). Callers must surface that marker; they must never present CJK
numbers as if measured.

Below that 20% refuse threshold the module still runs, but a SUB-threshold CJK
share (say 12%) is not free of the problem: `_WORD_RE` never matches CJK
codepoints and `.`/`!`/`?` are not how CJK sentences end, so the CJK fraction of
the text is silently excluded from tokenization — the fingerprint measures only
the English-script remainder, with an undercounted `total_words`. To avoid
*silent* partial measurement, any fingerprint computed over text with CJK share
in (0, 0.20) carries a `partial_scripts` field (e.g. `"CJK 12% excluded from
tokenization"`) stating exactly what was left out, in both the returned dict and
`format_fingerprint`'s rendering. Pure-English text has no such field.

NO-CONTENT INPUT
-----------------
Samples that are empty, whitespace-only, or tokenize to zero words (e.g. bare
punctuation) return an explicit `supported=False, reason="no_content"` marker,
the same shape as the CJK refusal — never a silent all-zeros fingerprint that
only a thin-N warning would hint at.

USAGE
-----
    from stylometry import compute_fingerprint, compute_per_genre
    fp = compute_fingerprint(samples_list, genre="blog")   # one genre
    fps = compute_per_genre({"blog": [...], "tweet": [...]})  # never pools

    # CLI (what voice-onboard runs during extraction):
    python3 stylometry.py --demo                      # two-genre proof
    python3 stylometry.py --genre blog a.md b.md c.md  # print one fingerprint

Stdlib only. No pip installs, no host-specific deps: loads on every host.
"""

import math
import re
import sys

# The 3-sample floor from voice-onboard: a trait counts only if it appears 3+
# times; below 3 samples nothing is a habit. Enforced in confidence labeling.
MIN_SAMPLES = 3

# ---------------------------------------------------------------------------
# Function-word baseline.
#
# ORIGIN & LIMITS (be honest — this is a register-(c) anchor, not a corpus
# recomputation): these are APPROXIMATE per-1000-word rates for generic modern
# English prose, rounded to order-of-magnitude from published English
# word-frequency norms (the familiar ranked function-word frequencies reported
# by large reference corpora such as Brown / COCA). They are ANCHORS: the SIGN
# and rough magnitude of a delta is the signal ("this author under-uses 'the'"),
# not 3-significant-figure precision. Because the table is a shipped constant,
# every delta is fully recomputable from (text, this table) — which is what the
# eval's recomputable-number property relies on.
#
# Known limits: single register (generic prose, not tuned to tweets vs reports),
# English-only, and NOT recomputed live from a corpus. Swap this table for a
# genre-matched corpus baseline if you need calibrated magnitudes.
# ---------------------------------------------------------------------------
BASELINE_RATES = {
    "the": 50.0, "of": 30.0, "and": 28.0, "to": 26.0, "a": 22.0,
    "in": 19.0, "is": 10.0, "it": 9.0, "for": 9.0, "that": 8.0,
    "as": 7.0, "with": 7.0, "but": 6.0, "on": 6.0, "be": 6.0,
    "by": 5.0, "at": 4.0, "this": 4.0, "not": 4.0, "we": 4.0,
    "i": 4.0, "you": 3.0, "or": 3.0, "so": 3.0, "if": 3.0,
}

# AI-register words: their ABSENCE (0 occurrences) is the strong voice signal.
# Kept lowercase; matched as whole words. Multi-word phrases handled separately.
AI_REGISTER_WORDS = frozenset({
    "delve", "leverage", "tapestry", "testament", "realm", "foster",
    "robust", "seamless", "seamlessly", "underscore", "underscores",
    "showcase", "showcases", "pivotal", "intricate", "myriad", "nuanced",
    "elevate", "elevates", "embark", "navigate", "navigating", "landscape",
    "bustling", "notably", "moreover", "furthermore", "unlock", "unlocks",
    "harness", "harnessing", "spearhead", "boasts", "boast", "resonate",
    "resonates", "vibrant", "crucial", "vital", "utilize", "utilizes",
    "endeavor", "plethora", "profound", "meticulous", "meticulously",
})
AI_REGISTER_PHRASES = (
    "treasure trove", "cutting-edge", "game-changer", "game changer",
    "in today's fast-paced world", "at the end of the day",
    "it's worth noting", "it is worth noting", "a testament to",
)

# Sentence splitter for whitespace-delimited scripts. Splits on . ! ? runs.
_SENT_SPLIT = re.compile(r"[.!?]+(?:\s+|$)")
# A "word" for counting: run of word-ish chars incl. internal ' and -.
_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['\-][A-Za-z0-9]+)*")
# A "testable number": integers, decimals, percents, currency, ratios, ranges,
# and figures with magnitude/units (2x, 3.5M, $40, 12%). We require a digit so
# spelled-out "two" is not counted (rossmann means concrete figures).
#
# Version strings ("v1.1", "2.3.4") are identifiers, not testable metrics, and
# are stripped from the text BEFORE this regex runs (_VERSION_RE below) so they
# never inflate the count.
#
# Bare 4-digit years (1900-2099, e.g. "2025") are, BY DESIGN, EXCLUDED from the
# count: a year reads as a date/label, not a concrete claim about magnitude. A
# 4-digit figure that carries a currency prefix, decimal, comma, or magnitude
# suffix (e.g. "$2025", "2,025", "2025%", "2025x") is NOT a bare year and DOES
# count — see `_is_bare_year` for the exact boundary. Code and this docstring
# must agree: if you change one, change the other.
_NUMBER_RE = re.compile(
    r"""(?<![\w])            # not mid-word
        [\$€£]?              # optional currency
        \d[\d,]*             # integer part
        (?:\.\d+)?           # optional decimal
        (?:\s?%|x|k|m|b|bn)? # optional unit/magnitude
    """,
    re.IGNORECASE | re.VERBOSE,
)
# Version-string patterns to strip before counting: "v1", "v1.1", "v2.3.4", and
# bare semver "1.2.3" (no leading v). Removed wholesale so no fragment of them
# leaks into _NUMBER_RE's matches.
_VERSION_RE = re.compile(
    r"""\bv\d+(?:\.\d+){0,2}\b   # v1, v1.1, v2.3.4
      | \b\d+\.\d+\.\d+\b        # bare semver 1.2.3
    """,
    re.IGNORECASE | re.VERBOSE,
)
# CJK / Hangul / Hiragana / Katakana codepoint ranges (predominance -> CJK path).
_CJK_RE = re.compile(
    "[぀-ヿ㐀-䶿一-鿿가-힯ｦ-ﾟ]"
)


def _round(x, n=1):
    return round(float(x), n)


def _cjk_share(text):
    """Fraction of alphabetic characters that are CJK-script. 0.0 if no letters."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    cjk = sum(1 for c in letters if _CJK_RE.match(c))
    return cjk / len(letters)


def is_cjk_dominant(text, threshold=0.20):
    """True if CJK-script codepoints are a large share of the letters.

    Threshold is low (0.20) on purpose: even a fifth CJK means whitespace word
    counting is already unreliable, so we refuse rather than emit garbage.
    """
    return _cjk_share(text) >= threshold


def _is_bare_year(raw_match):
    """True if a raw _NUMBER_RE match is a plain 1900-2099 year, nothing else.

    A "bare" year has no currency, decimal point, comma, or magnitude/percent
    suffix — those all mean "this 4-digit figure is doing more than dating
    something" and must still count. Must stay consistent with the _NUMBER_RE
    docstring above.
    """
    s = raw_match.strip()
    if not s.isdigit() or len(s) != 4:
        return False
    return 1900 <= int(s) <= 2099


def confidence_label(n_samples):
    """Confidence tied to sample count, with a HARD floor at the 3-sample rule."""
    if n_samples < MIN_SAMPLES:
        return "Insufficient (N<%d)" % MIN_SAMPLES
    if n_samples <= 4:
        return "Low"
    if n_samples <= 10:
        return "Medium"
    return "High"


def _sentences(text):
    parts = [s.strip() for s in _SENT_SPLIT.split(text)]
    return [s for s in parts if s]


def _words(text):
    return _WORD_RE.findall(text)


def sentence_length_stats(text):
    """Mean, variance, stdev, burstiness (CV) of words-per-sentence.

    Variance/burstiness is the signal, not the mean. Returns zeros for <2
    sentences (variance undefined) so callers can flag thin rhythm data.
    """
    lengths = [len(_words(s)) for s in _sentences(text)]
    lengths = [n for n in lengths if n > 0]
    n = len(lengths)
    if n == 0:
        return {"n_sentences": 0, "mean": 0.0, "variance": 0.0,
                "stdev": 0.0, "burstiness_cv": 0.0}
    mean = sum(lengths) / n
    if n < 2:
        var = 0.0
    else:
        # population variance: deterministic, no sampling assumption.
        var = sum((x - mean) ** 2 for x in lengths) / n
    stdev = math.sqrt(var)
    cv = (stdev / mean) if mean else 0.0
    return {
        "n_sentences": n,
        "mean": _round(mean),
        "variance": _round(var),
        "stdev": _round(stdev),
        "burstiness_cv": _round(cv, 2),
    }


def function_word_deltas(text, baseline=BASELINE_RATES):
    """Per-1000-word rate of each baseline function word, minus baseline rate.

    Positive delta = author over-uses vs generic prose; negative = under-uses.
    Fully recomputable from (text, baseline).
    """
    words = [w.lower() for w in _words(text)]
    total = len(words)
    counts = {}
    for w in words:
        if w in baseline:
            counts[w] = counts.get(w, 0) + 1
    out = {}
    for word, base_rate in baseline.items():
        rate = (counts.get(word, 0) / total * 1000.0) if total else 0.0
        out[word] = {
            "text_rate": _round(rate),
            "baseline_rate": base_rate,
            "delta": _round(rate - base_rate),
        }
    return out


def char_ngram_profile(text, n=3, top=10):
    """Top character n-grams by normalized frequency (lexicon-free fingerprint).

    Whitespace is collapsed to single spaces so layout doesn't dominate; case is
    lowered. Returns the top-`top` [(gram, freq)] plus the distinct-gram count.
    """
    norm = re.sub(r"\s+", " ", text.strip().lower())
    grams = {}
    if len(norm) >= n:
        for i in range(len(norm) - n + 1):
            g = norm[i:i + n]
            grams[g] = grams.get(g, 0) + 1
    total = sum(grams.values())
    ranked = sorted(grams.items(), key=lambda kv: (-kv[1], kv[0]))[:top]
    profile = [[g, _round(c / total, 4)] for g, c in ranked] if total else []
    return {"distinct": len(grams), "top": profile}


def punctuation_density(text):
    """em-dash / semicolon / ellipsis / exclamation per 1000 words."""
    words = len(_words(text))
    scale = (1000.0 / words) if words else 0.0
    em = len(re.findall(r"—|--", text))
    semi = text.count(";")
    # ellipsis: unicode … or three-or-more dots.
    ell = len(re.findall(r"…|\.{3,}", text))
    excl = text.count("!")
    return {
        "per": "1000 words",
        "em_dash": _round(em * scale),
        "semicolon": _round(semi * scale),
        "ellipsis": _round(ell * scale),
        "exclamation": _round(excl * scale),
    }


def testable_number_density(text):
    """Concrete figures per 100 words (rossmann's testable-number signal).

    Version strings (v1.1, 1.2.3) are stripped before counting — identifiers,
    not metrics. Bare 4-digit years (1900-2099) are excluded by design — dates,
    not testable claims (see _NUMBER_RE / _is_bare_year docstrings).
    """
    words = len(_words(text))
    cleaned = _VERSION_RE.sub(" ", text)
    raw = _NUMBER_RE.findall(cleaned)
    nums = len([m for m in raw if not _is_bare_year(m)])
    per100 = (nums / words * 100.0) if words else 0.0
    return {"count": nums, "per_100_words": _round(per100)}


def ai_register_absences(text):
    """Count AI-register words/phrases. ZERO is the strong voice signal.

    Returns total hits, the offending terms with counts (empty = clean), and the
    list length checked, so a profile can assert '0 AI-register words across N
    samples'.
    """
    lowered = text.lower()
    words = [w.lower() for w in _words(lowered)]
    hits = {}
    for w in words:
        if w in AI_REGISTER_WORDS:
            hits[w] = hits.get(w, 0) + 1
    for ph in AI_REGISTER_PHRASES:
        c = lowered.count(ph)
        if c:
            hits[ph] = hits.get(ph, 0) + c
    return {
        "terms_checked": len(AI_REGISTER_WORDS) + len(AI_REGISTER_PHRASES),
        "total_hits": sum(hits.values()),
        "offenders": dict(sorted(hits.items())),
    }


def compute_fingerprint(samples, genre=None):
    """Full numeric fingerprint for ONE genre's samples (list of strings).

    Never pool genres here — pass one genre's samples. Returns a dict carrying
    provenance (genre, sample_count, total_words, confidence) so every number in
    a written profile is traceable to what it rests on. CJK-dominant input
    returns an explicit unsupported marker instead of garbage numbers.
    """
    if isinstance(samples, str):
        samples = [samples]
    samples = [s for s in samples if s and s.strip()]
    n = len(samples)
    joined = "\n\n".join(samples)

    cjk_share = _cjk_share(joined)
    if cjk_share >= 0.20:
        return {
            "genre": genre,
            "sample_count": n,
            "supported": False,
            "script": "CJK",
            "note": ("CJK / non-whitespace script detected (%.0f%% of letters): "
                      "stylometry assumes whitespace-delimited words, so "
                      "per-word/per-sentence rates would be garbage. No numbers "
                      "emitted. Bilingual/CJK stylometry is v2."
                      % (cjk_share * 100)),
        }

    total_words = len(_words(joined))
    if n == 0 or total_words == 0:
        return {
            "genre": genre,
            "sample_count": n,
            "supported": False,
            "reason": "no_content",
            "note": ("No measurable content: samples are empty, whitespace-only, "
                     "or tokenize to zero words. No numbers emitted."),
        }

    result = {
        "genre": genre,
        "sample_count": n,
        "total_words": total_words,
        "confidence": confidence_label(n),
        "supported": True,
        "sentence_length": sentence_length_stats(joined),
        "function_word_deltas": function_word_deltas(joined),
        "char_3gram": char_ngram_profile(joined, n=3, top=10),
        "punctuation_density": punctuation_density(joined),
        "testable_number_density": testable_number_density(joined),
        "ai_register": ai_register_absences(joined),
    }
    if n < MIN_SAMPLES:
        result["warning"] = (
            "N=%d is below the %d-sample floor; treat every number as "
            "indicative only, not an established habit." % (n, MIN_SAMPLES))
    # Sub-threshold CJK (0 < share < 0.20): the CJK fraction never matches
    # _WORD_RE and its sentences aren't split on . ! ? — it is silently excluded
    # from tokenization, not measured. Never let that be silent.
    if 0.0 < cjk_share < 0.20:
        result["partial_scripts"] = (
            "CJK %.0f%% excluded from tokenization" % (cjk_share * 100))
    return result


def compute_per_genre(genre_samples):
    """Map {genre: [samples]} -> {genre: fingerprint}. Never pools genres."""
    return {g: compute_fingerprint(s, genre=g) for g, s in genre_samples.items()}


# ---------------------------------------------------------------------------
# Human-readable rendering (what voice-onboard shows the user for confirmation).
# ---------------------------------------------------------------------------
def format_fingerprint(fp):
    g = fp.get("genre") or "(unlabelled)"
    if not fp.get("supported", True):
        reason = fp.get("script") or fp.get("reason") or "unsupported"
        return ("### Measured Fingerprint — %s\n- UNSUPPORTED (%s): %s (N=%d)"
                % (g, reason, fp.get("note", ""), fp.get("sample_count", 0)))
    sl = fp["sentence_length"]
    pd = fp["punctuation_density"]
    tn = fp["testable_number_density"]
    ai = fp["ai_register"]
    over = sorted(fp["function_word_deltas"].items(),
                  key=lambda kv: kv[1]["delta"])
    under = over[:3]
    overused = list(reversed(over))[:3]
    lines = [
        "### Measured Fingerprint — %s" % g,
        "- Provenance: genre=%s, N=%d samples, %d words, confidence=%s"
        % (g, fp["sample_count"], fp["total_words"], fp["confidence"]),
    ]
    if fp.get("warning"):
        lines.append("- CONFIDENCE NOTE: %s" % fp["warning"])
    if fp.get("partial_scripts"):
        lines.append("- CAVEAT: partial_scripts: %s" % fp["partial_scripts"])
    lines += [
        "- Sentence length: mean=%.1f, variance=%.1f, burstiness(CV)=%.2f "
        "over %d sentences (variance is the rhythm signal)"
        % (sl["mean"], sl["variance"], sl["burstiness_cv"], sl["n_sentences"]),
        "- Punctuation /1k words: em-dash=%.1f, semicolon=%.1f, ellipsis=%.1f, "
        "exclamation=%.1f" % (pd["em_dash"], pd["semicolon"], pd["ellipsis"],
                              pd["exclamation"]),
        "- Testable numbers: %.1f per 100 words (%d figures)"
        % (tn["per_100_words"], tn["count"]),
        "- AI-register words: %d hits across %d terms checked%s"
        % (ai["total_hits"], ai["terms_checked"],
           "" if not ai["offenders"] else " -> " + ", ".join(
               "%s x%d" % (k, v) for k, v in ai["offenders"].items())),
        "- Function-word deltas /1k (vs generic baseline): "
        "over-uses %s; under-uses %s"
        % (", ".join("%s +%.1f" % (w, d["delta"]) for w, d in overused),
           ", ".join("%s %.1f" % (w, d["delta"]) for w, d in under)),
        "- Char 3-gram top: %s"
        % ", ".join("'%s' %.4f" % (g_, f_) for g_, f_ in fp["char_3gram"]["top"][:5]),
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Demo: the proof that per-genre discipline is real, not decorative.
# ---------------------------------------------------------------------------
_DEMO_TWEETS = [
    "Shipped it. 3 lines. Nobody noticed the 40% latency drop.",
    "Hot take: your dashboard has 12 metrics and 0 decisions attached.",
    "Rewrote the ranker today. NDCG up 2 points. Ship it.",
]
_DEMO_REPORTS = [
    ("In this analysis we examine the reranking model across the full query "
     "distribution, and we find that the observed 2-point NDCG improvement is "
     "concentrated in the head, while the long tail, which accounts for roughly "
     "38 percent of traffic, shows no statistically meaningful movement over the "
     "measured window."),
    ("The latency regression, which reached 120 milliseconds at the 99th "
     "percentile, was traced to an unbatched feature lookup, and after we "
     "restored batching the regression fell to 15 milliseconds, a level the "
     "team considered acceptable for the current release."),
    ("We recommend that the model be promoted to the primary ranking path only "
     "after the tail evaluation is repeated on a cleaner sample, because the "
     "current holdout, drawn from a single unusually clean quarter, likely "
     "overstates the improvement that production traffic would realize."),
]


def _demo():
    tweets = _DEMO_TWEETS
    reports = _DEMO_REPORTS
    per = compute_per_genre({"tweet": tweets, "report": reports})
    pooled = compute_fingerprint(tweets + reports, genre="POOLED (WRONG)")

    print("=" * 72)
    print("PER-GENRE (correct — voice-onboard discipline):")
    print("=" * 72)
    for g in ("tweet", "report"):
        print(format_fingerprint(per[g]))
        print()
    print("=" * 72)
    print("POOLED (wrong — flattens two genres into a blur):")
    print("=" * 72)
    print(format_fingerprint(pooled))
    print()

    tm = per["tweet"]["sentence_length"]["mean"]
    rm = per["report"]["sentence_length"]["mean"]
    pm = pooled["sentence_length"]["mean"]
    tv = per["tweet"]["sentence_length"]["variance"]
    rv = per["report"]["sentence_length"]["variance"]
    pv = pooled["sentence_length"]["variance"]
    print("-" * 72)
    print("PROOF pooling is materially different (describes neither genre):")
    print("  sentence-length mean : tweet=%.1f  report=%.1f  POOLED=%.1f"
          % (tm, rm, pm))
    print("  sentence-length var  : tweet=%.1f  report=%.1f  POOLED=%.1f"
          % (tv, rv, pv))
    print("  -> pooled mean sits between the two genres, matching neither;")
    print("     pooled variance is inflated by the cross-genre gap, inventing a")
    print("     'burstiness' that exists in no single genre. Averaging lies.")
    return per, pooled


def _cli(argv):
    if "--demo" in argv:
        _demo()
        return 0
    if "--genre" in argv:
        i = argv.index("--genre")
        genre = argv[i + 1]
        files = argv[i + 2:]
        samples = []
        for path in files:
            with open(path, encoding="utf-8") as fh:
                samples.append(fh.read())
        fp = compute_fingerprint(samples, genre=genre)
        print(format_fingerprint(fp))
        return 0
    print(__doc__.strip().splitlines()[0])
    print("usage: python3 stylometry.py --demo")
    print("       python3 stylometry.py --genre <name> <file> [<file> ...]")
    return 1


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
