#!/usr/bin/env python3
"""Run the voice-onboard extraction eval.

Run from `evals/`:
    python3 -m fixtures.run_voice_extraction

WHAT THIS MEASURES (and why it is not the header contract test)

test_voice_contract.py asserts the 10 `## H2` headers exist. That is shape, not
quality: a profile can carry every header and still have learned the wrong voice.
This suite grades CONTENT against a corpus whose ground truth is countable by hand.

voice-onboard is skill prose — an agent reads samples and writes a profile — so
there is no extraction function to unit-test. Instead:

  1. voice_corpus.json is SYNTHETIC and engineered PER GENRE: a habit word at 4x
     within its genre, a noise word at 2x within EACH genre (4x pooled — the
     cross-genre trap), sub-threshold decoys at 1-2x, absences at 0x, and two genres
     with genuinely different rhythm.
  2. The corpus is mixed-genre, so per voice-onboard/SKILL.md Step 1 ("Mixed genres
     -> offer to extract two profiles rather than averaging them into a blur") the
     gold artifact is a PAIR OF GENRE-SCOPED PROFILES, not one blended profile. Each
     genre ships a good profile and a bad one.
  3. Deterministic checks must tell them apart, and every count is recomputed WITHIN
     the profile's genre. Pooling genres is itself a failure mode here, not a
     measurement convenience.
  4. Beyond the shipped bad profiles, each failure mode is probed with a FAMILY of
     programmatically generated mutants (mutants_voice.py) plus the append-only hard
     tail of evasions a reviewer constructed by hand. The suite reports a CATCH RATE
     per mode against a declared floor — a checker that can only catch the one
     exemplar it was written against fails on the next draw.

Ground truth is DECLARED in the fixture and RECOMPUTED here from the sample text.
Disagreement is a hard failure: a fixture whose own ground truth has drifted is
worse than no fixture. Fix the samples, never the declared number.

Stdlib only, no model, no key — pure counting, safe for CI.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS_PATH = os.path.join(HERE, "voice_corpus.json")

# evals/fixtures/ -> evals/ -> <suite-root>, so `import aiws` resolves to
# the sibling aiws/ package (same convention as evals/audit_report/check_report.py).
SUITE_ROOT = os.path.dirname(os.path.dirname(HERE))
if SUITE_ROOT not in sys.path:
    sys.path.insert(0, SUITE_ROOT)

from aiws.text import (  # noqa: E402  (path set above)
    VOICE_TOKEN as _TOKEN,
    CLAUSE_SPLIT as _CLAUSE_SPLIT,
)

# The 10 headers comms-polish reads (same contract test_voice_contract.py guards on
# the template). Every artifact must satisfy it — which is exactly why passing it
# proves nothing about voice quality.
REQUIRED_HEADERS = [
    "Tone", "Sentence Length", "Vocabulary Do", "Vocabulary Don't",
    "Signature Moves", "Punctuation & Formatting", "Openings & Closings",
    "Uncertainty Style", "Things To Avoid", "Scope & Calibration",
]

# Sections that describe what the author does NOT do. A word named here is an
# assertion of ABSENCE, so the claim scans must skip them — otherwise correctly
# mining an absence reads as inventing a trait, and a profile asserting the exact
# INVERSE of the corpus ("ledger — she never writes this word") scores as having
# learned the habit.
ABSENCE_SECTIONS = {"Vocabulary Don't", "Things To Avoid"}
EVIDENCE_SECTIONS = {"Verbatim Anchors"}

HONEST_GAP = "Unknown — not enough signal"
SELF_REPORT_SUBSECTION = "Self-report Divergence"

# Observable style features whose truth is COUNTABLE in the corpus. This is how an
# UNQUOTED trait claim ("Frequent exclamation marks; heavy em-dash use") is checked.
# A free content-word scan cannot do this job: it flags the profile's own descriptive
# prose ("reaches", "abstractions", "reframe" have zero corpus support and are not
# claims about the author's words), which is a false-positive machine.
_EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")

TRAIT_FEATURES = {
    "exclamation": ("exclamation marks", lambda t: t.count("!")),
    "exclamation mark": ("exclamation marks", lambda t: t.count("!")),
    "exclamation marks": ("exclamation marks", lambda t: t.count("!")),
    "em-dash": ("em-dashes", lambda t: t.count("—") + t.count("--")),
    "em dash": ("em-dashes", lambda t: t.count("—") + t.count("--")),
    "em-dashes": ("em-dashes", lambda t: t.count("—") + t.count("--")),
    "ellipsis": ("ellipses", lambda t: t.count("…") + t.count("...")),
    "ellipses": ("ellipses", lambda t: t.count("…") + t.count("...")),
    "emoji": ("emoji", lambda t: len(_EMOJI.findall(t))),
    "emojis": ("emoji", lambda t: len(_EMOJI.findall(t))),
    "rocket": ("emoji", lambda t: len(_EMOJI.findall(t))),
    "rhetorical question": ("question marks", lambda t: t.count("?")),
    "question mark": ("question marks", lambda t: t.count("?")),
    "question marks": ("question marks", lambda t: t.count("?")),
    "semicolon": ("semicolons", lambda t: t.count(";")),
    "semicolons": ("semicolons", lambda t: t.count(";")),
    "semi-colon": ("semicolons", lambda t: t.count(";")),
}

# Tokens that flip a feature claim's polarity. A CLAUSE is negated when it holds an
# ODD number of these (double negatives cancel: "not rare" is a POSITIVE claim). The
# old code skipped a whole line if any denial token appeared anywhere on it, so an
# emoji habit asserted as "not rare" — the denial token belonging to "rare", not to
# a suppression of emoji — escaped. Polarity is now scoped to the clause, with parity.
_NEGATIONS = {
    "never", "none", "no", "not", "zero", "absent", "unknown", "avoid", "avoids",
    "without", "neither", "nor", "rarely", "rare", "uncommon", "seldom",
    "scarcely", "hardly", "lacks", "lack", "0",
}
# Clause boundaries: sentence stops, semicolons, and dash separators. NOT the hyphen
# inside "em-dash" — only a SPACED hyphen or a real en/em dash separates clauses.


# --------------------------------------------------------------------------
# Pure helpers (each independently testable; see test_voice_extraction.py)
# --------------------------------------------------------------------------

def count_word(word, text):
    """Case-insensitive, word-boundary occurrence count.

    Word-boundary matters: "ledgers" must not inflate the count of "ledger", and
    "delved" must not resurrect an absent "delve". The absence signal is only as
    trustworthy as the boundary.
    """
    return len(re.findall(r"\b" + re.escape(word) + r"\b", text, re.IGNORECASE))


def corpus_text(corpus, genre=None):
    """Sample text, scoped to ONE genre unless genre is None.

    genre=None (the pooled text) exists only for the cross-genre TRAP assertion and
    the blended-mean computation. No trait check may count on it: pooling genres is
    the failure this eval detects, not a shortcut it may take.
    """
    return " ".join(s["text"] for s in corpus["samples"]
                    if genre is None or s["genre"] == genre)


def genres_of(corpus):
    return sorted({s["genre"] for s in corpus["samples"]})


def sentence_lengths(text):
    """Words per sentence, splitting on terminal punctuation."""
    return [len(part.split())
            for part in re.split(r"[.!?]+", text) if part.strip()]


def mean_sentence_words(text):
    lens = sentence_lengths(text)
    return sum(lens) / len(lens) if lens else 0.0


def strip_comments(md):
    return re.sub(r"<!--.*?-->", "", md, flags=re.S)


def normalize(s):
    return re.sub(r"\s+", " ", s.replace("’", "'")).strip()


def parse_sections(md):
    """Split a profile into {H2 header: body text}. HTML comments are dropped."""
    body = strip_comments(md)
    sections = {}
    current = None
    for line in body.splitlines():
        m = re.match(r"^##\s+(.+)$", line)
        if m:
            current = normalize(m.group(1))
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {k: "\n".join(v) for k, v in sections.items()}


def parse_subsection(md, section, subsection):
    """Return one H3 body inside an H2 section, without changing the H2 contract."""
    body = parse_sections(md).get(section, "")
    lines = []
    active = False
    for line in body.splitlines():
        match = re.match(r"^###\s+(.+)$", line)
        if match:
            active = normalize(match.group(1)) == normalize(subsection)
            continue
        if active:
            lines.append(line)
    return "\n".join(lines)


def claim_sections(md):
    """The POSITIVE sections — where the profile asserts what the author DOES."""
    non_claim = {normalize(h) for h in ABSENCE_SECTIONS | EVIDENCE_SECTIONS}
    return {h: b for h, b in parse_sections(md).items()
            if normalize(h) not in non_claim}


def claim_text(md):
    """Positive-section prose with blockquote EVIDENCE lines dropped.

    A pasted sample sentence is proof, not a claim: quoting "Shipped the pricing
    ledger today." does not by itself claim "ledger" as a habit, and quoting a
    sentence that happens to contain the noise word is not learning it.
    """
    lines = []
    for body in claim_sections(md).values():
        lines += [ln for ln in body.splitlines() if not ln.lstrip().startswith(">")]
    return "\n".join(lines)


def profile_claims(word, md):
    """Does the profile CLAIM this word as the author's, in a positive section?"""
    return count_word(word, claim_text(md)) > 0


def profile_mentions(word, md):
    """Does the profile name this word anywhere at all (comments excluded)?

    Direction-blind on purpose — used only for REPORTING how a word was used, never
    as a check. See claim_sections() for why.
    """
    return count_word(word, strip_comments(md)) > 0


def quoted_terms(md):
    """Single-word terms the profile puts in quotes inside CLAIM sections.

    A profile asserts a vocabulary trait by quoting it ("signature words: 'ledger'").
    Evidence lines quote whole sentences, which is why only single tokens are
    collected — a pasted sentence is proof, not a claim — and blockquote lines are
    dropped outright.
    """
    terms = set()
    for line in claim_text(md).splitlines():
        for m in re.finditer(r"[\"“]([A-Za-z][A-Za-z'’-]*)[\"”]", line):
            terms.add(m.group(1).lower())
    return terms


def _clause_is_negated(clause):
    """True when the clause carries an ODD number of negation tokens.

    Parity, not presence: "never — 0 em-dashes" is a denial (two negations, but they
    sit in different clauses after the split), while "not rare" inside one clause is
    two negations that cancel to a POSITIVE claim.
    """
    return sum(1 for t in _TOKEN.findall(clause.lower()) if t in _NEGATIONS) % 2 == 1


def asserted_features(md, text):
    """Style features the profile ASSERTS in a claim section but `text` does not carry.

    Returns a sorted list of feature names. Polarity is scoped to the CLAUSE the
    feature is named in: a feature is invented only when the corpus has zero of it
    AND the clause naming it is not negated. Mining an absence ("Em-dash density:
    never — 0 em-dashes") stays correct; a positive double-negative claim ("emoji use
    is not rare") is caught.
    """
    invented = set()
    for body in claim_sections(md).values():
        for line in body.splitlines():
            if line.lstrip().startswith(">"):
                continue
            for clause in _CLAUSE_SPLIT.split(line):
                if _clause_is_negated(clause):
                    continue
                low = clause.lower()
                for alias, (feature, evidence) in TRAIT_FEATURES.items():
                    if re.search(r"\b" + re.escape(alias) + r"\b", low) \
                            and evidence(text) == 0:
                        invented.add(feature)
    return sorted(invented)


def feature_aliases(feature):
    """Known lexical aliases for one canonical countable style feature."""
    return sorted(alias for alias, (canonical, _counter) in TRAIT_FEATURES.items()
                  if canonical == feature)


def feature_count(feature, text):
    """Count a canonical style feature with the same machinery as trait checks."""
    counters = {canonical: counter
                for _alias, (canonical, counter) in TRAIT_FEATURES.items()}
    if feature not in counters:
        raise KeyError(feature)
    return counters[feature](text)


# --------------------------------------------------------------------------
# Ground truth: declared vs recomputed, PER GENRE
# --------------------------------------------------------------------------

def verify_ground_truth(corpus):
    """Recompute every declared count WITHIN its genre. Any drift is fatal.

    Returns (recomputed: dict, errors: list[str]).

    Per-genre is not a refinement, it is the spec (SKILL.md Step 2: "Don't average
    across genres"). A pooled count can clear the 3+ bar by aggregation — the old
    fixture's "ledger 4x" was tweet=3 + memo=1 — which is the very extraction error
    this eval exists to punish.
    """
    gt = corpus["ground_truth"]
    min_habit = gt["min_habit_occurrences"]
    errors = []
    recomputed = {"genres": {}}

    for genre, spec in gt["genres"].items():
        text = corpus_text(corpus, genre)
        counts = {}

        for key in ("habit_word", "noise_word", "subthreshold_decoy",
                    "foreign_habit_word", "boundary_decoy"):
            declared = spec[key]
            actual = count_word(declared["word"], text)
            counts[declared["word"]] = actual
            if actual != declared["count"]:
                errors.append(
                    f"GROUND TRUTH DRIFT [{genre}.{key}]: '{declared['word']}' declared "
                    f"{declared['count']}x, recomputed {actual}x WITHIN {genre}. "
                    f"Fix the SAMPLES, not the declared count.")

        for declared in spec["absent_words"]:
            actual = count_word(declared["word"], text)
            counts[declared["word"]] = actual
            if actual != declared["count"]:
                errors.append(
                    f"GROUND TRUTH DRIFT [{genre}.absent]: '{declared['word']}' declared "
                    f"{declared['count']}x, recomputed {actual}x. The absence signal is void.")

        # The engineered contrasts only have teeth if they straddle the 3+ bar.
        habit, noise = spec["habit_word"]["word"], spec["noise_word"]["word"]
        decoy = spec["subthreshold_decoy"]["word"]
        foreign = spec["foreign_habit_word"]["word"]
        if counts.get(habit, 0) < min_habit:
            errors.append(f"[{genre}] habit_word '{habit}' does not clear the {min_habit}+ "
                          f"rule WITHIN its genre — the fixture cannot test 'learn the habit'.")
        if counts.get(noise, 0) >= min_habit:
            errors.append(f"[{genre}] noise_word '{noise}' clears the {min_habit}+ rule — it "
                          f"is no longer noise, so 'don't learn an accident' is untestable.")
        if not 0 < counts.get(decoy, 0) < min_habit:
            errors.append(f"[{genre}] subthreshold_decoy '{decoy}' must occur 1..{min_habit - 1} "
                          f"times (non-zero, under the bar) — recomputed {counts.get(decoy)}x. "
                          f"A 0x decoy would be caught by the invented-trait check instead and "
                          f"the 3+ rule would go untested.")
        if counts.get(foreign, 0) != 0:
            errors.append(f"[{genre}] foreign_habit_word '{foreign}' must be 0x here — it is the "
                          f"other genre's habit, and cross-genre import must stay detectable.")

        mean = mean_sentence_words(text)
        counts["_mean"] = mean
        if "max_mean_sentence_words" in spec and mean > spec["max_mean_sentence_words"]:
            errors.append(f"[{genre}] mean {mean:.1f} exceeds declared max "
                          f"{spec['max_mean_sentence_words']}")
        if "min_mean_sentence_words" in spec and mean < spec["min_mean_sentence_words"]:
            errors.append(f"[{genre}] mean {mean:.1f} below declared min "
                          f"{spec['min_mean_sentence_words']}")

        unknown = spec.get("expected_unknown_sections") or []
        if not unknown:
            errors.append(f"[{genre}] no expected_unknown_sections declared — the honest-gap "
                          f"check has nothing to bind to and would pass on any profile.")
        bad = [h for h in unknown if h not in REQUIRED_HEADERS]
        if bad:
            errors.append(f"[{genre}] expected_unknown_sections names header(s) the profile "
                          f"contract does not have: {bad}")

        recomputed["genres"][genre] = counts

    # The planted self-report is useful only while it deterministically contradicts
    # the measured feature in every declared genre. Recompute the evidence here so a
    # changed sample cannot silently turn the false report true.
    report = gt.get("self_report") or {}
    feature = report.get("feature")
    declared_counts = report.get("genre_counts") or {}
    if not feature:
        errors.append("no ground_truth.self_report.feature declared")
    else:
        for genre in gt["genres"]:
            try:
                actual = feature_count(feature, corpus_text(corpus, genre))
            except KeyError:
                errors.append(f"self_report feature '{feature}' is not deterministically "
                              "countable by TRAIT_FEATURES")
                break
            recomputed["genres"][genre][f"self-report {feature}"] = actual
            declared = declared_counts.get(genre)
            if declared != actual:
                errors.append(
                    f"GROUND TRUTH DRIFT [{genre}.self_report]: '{feature}' declared "
                    f"{declared}x, recomputed {actual}x WITHIN {genre}. Fix the SAMPLES, "
                    "not the declared count.")
            if report.get("asserted_present") is not True or actual != 0:
                errors.append(
                    f"[{genre}] planted self-report no longer contradicts the corpus: "
                    f"asserted_present={report.get('asserted_present')!r}, "
                    f"measured '{feature}'={actual}x")

    # The cross-genre trap: noise WITHIN each genre, habit-shaped when POOLED. This is
    # what makes aggregation detectably wrong rather than merely inelegant.
    trap = gt["cross_genre_trap"]
    pooled = count_word(trap["word"], corpus_text(corpus))
    recomputed["_pooled_trap"] = pooled
    if pooled != trap["pooled_count"]:
        errors.append(f"GROUND TRUTH DRIFT [cross_genre_trap]: '{trap['word']}' declared "
                      f"{trap['pooled_count']}x pooled, recomputed {pooled}x.")
    if pooled < min_habit:
        errors.append(f"cross_genre_trap '{trap['word']}' no longer clears {min_habit}+ when "
                      f"pooled — a profile that aggregates genres would not be detectably wrong.")
    for genre in gt["genres"]:
        if count_word(trap["word"], corpus_text(corpus, genre)) >= min_habit:
            errors.append(f"cross_genre_trap '{trap['word']}' clears {min_habit}+ WITHIN {genre} "
                          f"— it is a real habit there, so the trap is void.")

    means = {g: recomputed["genres"][g]["_mean"] for g in gt["genres"]}
    gap = max(means.values()) - min(means.values())
    recomputed["_genre_gap"] = gap
    recomputed["_blended_mean"] = mean_sentence_words(corpus_text(corpus))
    if gap < gt["min_genre_mean_gap_words"]:
        errors.append(f"genre rhythm gap {gap:.1f} words < declared minimum "
                      f"{gt['min_genre_mean_gap_words']} — reporting the blended mean would "
                      f"not be detectably wrong.")
    return recomputed, errors


# --------------------------------------------------------------------------
# The checks. Each is fn(md, corpus, genre) -> (ok: bool, detail: str).
# Every count inside them is scoped to `genre`.
# --------------------------------------------------------------------------

# A claimed rhythm figure must TRACK its own genre's mean. Tolerance is proportional
# (a memo mean of ~32 words tolerates more slack than a tweet mean of ~3.5) with a
# floor for the short genre.
_RHYTHM_TOL_FRACTION = 0.30
_RHYTHM_TOL_FLOOR = 2.0


def _genre_spec(corpus, genre):
    return corpus["ground_truth"]["genres"][genre]


def check_headers_present(md, corpus, genre):
    sections = {normalize(h) for h in parse_sections(md)}
    missing = [h for h in REQUIRED_HEADERS if normalize(h) not in sections]
    return (not missing,
            "all 10 consumer headers present" if not missing
            else f"missing headers: {missing}")


def names_genre(text, genre):
    """Does `text` name this genre? Singular or plural — "her tweets" names 'tweet'.

    Word-boundary counting is right for corpus traits ("ledgers" must not inflate
    "ledger") and wrong here: a profile writes "applies to her tweets", never "applies
    to her tweet". The plural form is the natural one, so the scope check must see it.
    """
    return count_word(genre, text) > 0 or count_word(genre + "s", text) > 0


def check_scope_declared(md, corpus, genre):
    """The profile must declare the ONE genre it covers.

    SKILL.md Step 1: mixed genres -> two profiles. A profile that claims to apply to
    "all of her writing" is the blur the SKILL forbids, whatever its contents say.
    """
    body = parse_sections(md).get("Scope & Calibration", "")
    applies = [ln for ln in body.splitlines() if "applies to" in ln.lower()]
    if not applies:
        return False, "Scope & Calibration does not say what the profile applies to"
    line = " ".join(applies)
    others = [g for g in genres_of(corpus)
              if g != genre and names_genre(line, g)]
    if not names_genre(line, genre):
        return False, f"'Applies to' does not name this profile's genre ({genre})"
    if others:
        return False, (f"profile is scoped to '{genre}' but claims to apply to {others} "
                       f"as well — that is the cross-genre blur the SKILL forbids")
    return True, f"scoped to one genre ({genre}) and says so"


def check_learns_habit_word(md, corpus, genre):
    """The genre's habit word must be CLAIMED in a positive section."""
    word = _genre_spec(corpus, genre)["habit_word"]["word"]
    n = count_word(word, corpus_text(corpus, genre))
    if profile_claims(word, md):
        return True, f"'{word}' ({n}x in {genre}, clears 3+) is learned"
    inverted = profile_mentions(word, md)
    return False, (
        f"'{word}' ({n}x in {genre}, clears 3+) is MISSING from the profile's claim "
        f"sections" + (" — it appears ONLY in an absence section, which asserts the "
                       "INVERSE of the corpus" if inverted else ""))


def check_omits_noise_word(md, corpus, genre):
    """The genre's noise word must not be claimed as a habit.

    Absence sections are exempt: a correct profile MAY note "kaleidoscope — 2x, do not
    treat as a habit" under Things To Avoid. Naming an accident in order to dismiss it
    is the discipline the SKILL asks for; flagging that was a false positive.
    """
    word = _genre_spec(corpus, genre)["noise_word"]["word"]
    n = count_word(word, corpus_text(corpus, genre))
    pooled = count_word(word, corpus_text(corpus))
    ok = not profile_claims(word, md)
    return ok, (f"'{word}' ({n}x in {genre}, fails 3+; {pooled}x pooled) "
                + ("correctly not learned as a habit" if ok
                   else "was LEARNED AS A HABIT — an accident promoted to a trait. It "
                        "only clears the bar if you POOL the genres, which is exactly "
                        "what the SKILL forbids"))


def check_no_subthreshold_claims(md, corpus, genre):
    """Every claimed word must clear the 3+ bar WITHIN this genre.

    SKILL.md Step 2: "A trait counts only if it appears 3+ times. One occurrence is
    noise. This is the single most common extraction mistake." A word with 1-2
    occurrences has non-zero support, so the invented-trait check (0 occurrences)
    waves it through — this check is what makes the 3+ rule enforceable.
    """
    text = corpus_text(corpus, genre)
    bar = corpus["ground_truth"]["min_habit_occurrences"]
    weak = sorted((t, count_word(t, text)) for t in quoted_terms(md)
                  if 0 < count_word(t, text) < bar)
    return (not weak,
            f"every claimed word clears the {bar}+ bar in {genre}" if not weak
            else f"SUB-THRESHOLD claims (under the {bar}+ bar in {genre}): "
                 + ", ".join(f"'{w}' ({n}x)" for w, n in weak))


def check_no_invented_traits(md, corpus, genre):
    """A trait asserted in a claim section with ZERO support IN THIS GENRE is invented.

    Two candidate classes, because a profile asserts traits two ways:
      * a QUOTED single token — "signature words: 'synergy'" (quoted_terms);
      * an UNQUOTED feature claim — "Frequent exclamation marks; heavy em-dash use"
        (asserted_features). Quoting was the whole detection surface before, so an
        invented trait was one paraphrase away from invisible.

    Genre-scoped: the OTHER genre's habit word has zero support here, so importing it
    ("ledger" into a memo profile) lands as what it is — an invented trait.
    """
    text = corpus_text(corpus, genre)
    invented = sorted(t for t in quoted_terms(md) if count_word(t, text) == 0)
    features = asserted_features(md, text)
    if not invented and not features:
        return True, f"every claimed word and feature has support in the {genre} corpus"
    parts = []
    if invented:
        parts.append(f"INVENTED words (0 occurrences in {genre}): {invented}")
    if features:
        parts.append(f"INVENTED features (0 occurrences in {genre}): {features}")
    return False, "; ".join(parts)


def check_lists_absence(md, corpus, genre):
    dont = parse_sections(md).get("Vocabulary Don't", "")
    missing = [spec["word"] for spec in _genre_spec(corpus, genre)["absent_words"]
               if count_word(spec["word"], dont) == 0]
    return (not missing,
            "0x words mined into Vocabulary Don't" if not missing
            else f"absences not mined (0x in {genre}, absent from Vocabulary Don't): {missing}")


def check_genre_scoped_rhythm(md, corpus, genre):
    """Sentence Length must report THIS genre's rhythm, not the blended mean.

    SKILL.md Step 2: "Don't average across genres." Two conditions:
      1. some figure in the section TRACKS this genre's recomputed mean (within 30%,
         floor 2 words) — a number that does not track the genre is not a measurement;
      2. no figure that tracks the BLENDED cross-genre mean is offered as the genre's
         rhythm. The blended mean is what averaging produces, and it describes neither
         genre.
    """
    body = parse_sections(md).get("Sentence Length", "")
    mean = mean_sentence_words(corpus_text(corpus, genre))
    blended = mean_sentence_words(corpus_text(corpus))
    tol = max(_RHYTHM_TOL_FLOOR, _RHYTHM_TOL_FRACTION * mean)
    blended_tol = max(_RHYTHM_TOL_FLOOR, _RHYTHM_TOL_FRACTION * blended)

    numbers = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", body)]
    if not numbers:
        return False, f"Sentence Length reports no figure at all for {genre}"

    tracking = [n for n in numbers if abs(n - mean) <= tol]
    blended_claims = [n for n in numbers if abs(n - blended) <= blended_tol
                      and abs(n - mean) > tol]
    if not tracking:
        return False, (
            f"AVERAGED / UNTRACKED: no figure in Sentence Length tracks the {genre} mean "
            f"{mean:.1f} words/sentence (tolerance {tol:.1f}); figures offered: {numbers}"
            + (f" — {blended_claims} is the BLENDED cross-genre mean ({blended:.1f}), which "
               f"describes neither genre" if blended_claims else ""))
    if blended_claims:
        return False, (
            f"Sentence Length offers the BLENDED cross-genre mean {blended_claims} "
            f"({blended:.1f}) alongside the {genre} figure — averaging the genres is the "
            f"failure, even when a correct figure is also present")
    return True, (f"reports the {genre} rhythm {tracking} against a recomputed mean of "
                  f"{mean:.1f} (blended mean {blended:.1f} correctly not used)")


def check_honest_gap(md, corpus, genre):
    """The SKILL: no evidence -> 'Unknown — not enough signal', never invent.

    Bound to the genre's declared `expected_unknown_sections` — the sections where the
    corpus GENUINELY carries no evidence. A literal substring search anywhere in the
    file let the phrase be parked in whatever section was convenient while the section
    that actually lacks evidence was filled confidently.
    """
    expected = _genre_spec(corpus, genre)["expected_unknown_sections"]
    sections = parse_sections(strip_comments(md))
    missing = [h for h in expected
               if HONEST_GAP.lower() not in sections.get(h, "").lower()]
    return (not missing,
            f"marks the evidence-free section(s) {expected} '{HONEST_GAP}'" if not missing
            else f"no '{HONEST_GAP}' in {missing} — the {genre} corpus carries no evidence "
                 f"there, and the profile filled it confidently anyway")


def check_anchor_provenance(md, corpus, genre):
    """Every verbatim anchor must be copied from a declared sample for this genre."""
    body = parse_sections(md).get("Verbatim Anchors", "")
    bullets = [line.strip() for line in body.splitlines() if line.strip().startswith("-")]
    parsed = []
    malformed = []
    for line in bullets:
        match = re.fullmatch(r'-\s+"(.+)"\s+—\s+([^—]+)', line)
        if match:
            parsed.append((match.group(1), match.group(2).strip()))
        else:
            malformed.append(line)

    if len(parsed) != 3 or malformed:
        return False, ("Verbatim Anchors must contain exactly 3 bullets shaped as "
                       "'- \"<verbatim line>\" — <one habit>'"
                       + (f"; malformed: {malformed}" if malformed else ""))

    declared = [normalize(sample["text"]) for sample in corpus["samples"]
                if sample["genre"] == genre]
    fabricated = [anchor for anchor, _habit in parsed
                  if not any(normalize(anchor) in sample for sample in declared)]
    if fabricated:
        return False, (f"anchors not found verbatim in any declared {genre} sample "
                       f"after whitespace normalization: {fabricated}")
    return True, f"all 3 anchors have verbatim provenance in the {genre} corpus"


def _line_names_feature(line, feature):
    return any(count_word(alias, line) for alias in feature_aliases(feature))


def _line_reports_count(line, count):
    numeric = re.search(rf"(?<![\d.]){count}(?:\.0)?(?![\d.])", line)
    word = count == 0 and count_word("zero", line)
    return bool(numeric or word)


def check_self_report_divergence(md, corpus, genre):
    """Surface the specific measured contradiction without learning the false trait.

    This is intentionally not a phrase check. The divergence note must bind the
    declared feature to its recomputed genre count and identify it as a conflict with
    the author's stated voice. Separately, asserted_features verifies that the same
    unsupported feature was not adopted in any positive profile section.
    """
    report = corpus["ground_truth"]["self_report"]
    feature = report["feature"]
    actual = feature_count(feature, corpus_text(corpus, genre))
    body = parse_subsection(md, "Things To Avoid", SELF_REPORT_SUBSECTION)
    low = body.lower()
    feature_lines = [line for line in body.splitlines()
                     if _line_names_feature(line, feature)]
    states_report = any(re.search(r"\b(self-report|stated|described|reported)\b",
                                  line, re.IGNORECASE)
                        for line in feature_lines)
    gives_measurement = any(_line_reports_count(line, actual)
                            and re.search(r"\b(measured|corpus|evidence|occurrences?|samples?)\b",
                                          line, re.IGNORECASE)
                            for line in feature_lines)
    names_conflict = bool(re.search(r"\b(contradict(?:s|ed|ion)?|diverg(?:e|es|ed|ence)|"
                                    r"conflict(?:s|ed)?|mismatch(?:es|ed)?)\b", low))
    adopted = feature in asserted_features(md, corpus_text(corpus, genre))

    if adopted:
        return False, (f"false self-report ADOPTED as a learned trait: '{feature}' is "
                       f"asserted present despite a recomputed {actual}x in {genre}")
    missing = []
    if not feature_lines:
        missing.append(f"the specific feature '{feature}'")
    if not states_report:
        missing.append("the author's stated claim")
    if not gives_measurement:
        missing.append(f"the recomputed {genre} count ({actual}x)")
    if not names_conflict:
        missing.append("the contradiction")
    if missing:
        return False, (f"self-report divergence not semantically surfaced: missing "
                       + ", ".join(missing))
    return True, (f"surfaces stated '{feature}' claim against measured {actual}x in "
                  f"{genre} and does not learn the false trait")


CHECKS = {
    "headers_present": check_headers_present,
    "scope_declared": check_scope_declared,
    "learns_habit_word": check_learns_habit_word,
    "omits_noise_word": check_omits_noise_word,
    "no_subthreshold_claims": check_no_subthreshold_claims,
    "no_invented_traits": check_no_invented_traits,
    "lists_absence": check_lists_absence,
    "genre_scoped_rhythm": check_genre_scoped_rhythm,
    "honest_gap": check_honest_gap,
    "anchor_provenance": check_anchor_provenance,
    "self_report_divergence": check_self_report_divergence,
}

# The bad profiles' declared failure modes. Every one MUST trip; a bad profile that
# sails through a check means the check is broken, and a broken check is a green run
# that proves nothing.
BAD_MUST_FAIL = [
    "scope_declared", "learns_habit_word", "omits_noise_word",
    "no_subthreshold_claims", "no_invented_traits", "lists_absence",
    "genre_scoped_rhythm", "honest_gap", "anchor_provenance",
    "genre_scoped_rhythm", "honest_gap", "self_report_divergence",
]


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------

def load_corpus(path=None):
    # Resolved at call time, not def time, so a test can point the runner at a
    # doctored fixture (e.g. an empty corpus) by patching CORPUS_PATH.
    with open(path or CORPUS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def load_profile(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def profile_pairs(corpus):
    """[(genre, good_path, bad_path)] — declared in the fixture, one pair per genre."""
    return [(p["genre"], os.path.join(HERE, p["good"]), os.path.join(HERE, p["bad"]))
            for p in corpus["profiles"]]


def run_checks(md, corpus, genre):
    return {name: fn(md, corpus, genre) for name, fn in CHECKS.items()}


def run(corpus, pairs):
    """Grade every genre's good/bad pair, then the mutant families. (passes, fails)."""
    passes = fails = 0

    print("=== voice-onboard extraction eval (genre-scoped) ===\n")

    if not corpus.get("samples"):
        print("ERROR: empty corpus — nothing to extract from, every check is vacuous.")
        return 0, 1
    if not pairs:
        print("ERROR: no profile pairs declared — nothing to discriminate.")
        return 0, 1

    recomputed, gt_errors = verify_ground_truth(corpus)
    print("-- ground truth (declared in fixture, RECOMPUTED from sample text, PER GENRE) --")
    for genre, counts in recomputed["genres"].items():
        words = ", ".join(f"{w}={n}x" for w, n in counts.items() if not w.startswith("_"))
        print(f"    [{genre}] {words}")
        print(f"    [{genre}] mean words/sentence: {counts['_mean']:.1f}")
    trap = corpus["ground_truth"]["cross_genre_trap"]
    print(f"    cross-genre trap: '{trap['word']}' = {trap['per_genre_count']}x per genre "
          f"(noise) but {recomputed['_pooled_trap']}x POOLED (habit-shaped) — pooling the "
          f"genres is detectably wrong")
    print(f"    genre mean gap {recomputed['_genre_gap']:.1f} words; blended mean "
          f"{recomputed['_blended_mean']:.1f} (what averaging would produce)")
    if gt_errors:
        for e in gt_errors:
            print(f"[FAIL] {e}")
        return 0, len(gt_errors)
    print("[PASS] declared ground truth == recomputed, WITHIN every genre\n")

    for genre, good_path, bad_path in pairs:
        good_md, bad_md = load_profile(good_path), load_profile(bad_path)

        print(f"-- [{genre}] GOOD profile (must pass every check) --")
        for name, (ok, detail) in run_checks(good_md, corpus, genre).items():
            passes += ok
            fails += not ok
            print(f"[{'PASS' if ok else 'FAIL'}] {name:24} {detail}")

        print(f"\n-- [{genre}] BAD profile (the planted positive: each mode MUST trip) --")
        bad_results = run_checks(bad_md, corpus, genre)
        for name in BAD_MUST_FAIL:
            ok, detail = bad_results[name]
            tripped = not ok           # we WANT the check to fail on the bad profile
            passes += tripped
            fails += not tripped
            print(f"[{'PASS' if tripped else 'FAIL'}] {name:24} "
                  + (f"tripped — {detail}" if tripped
                     else f"DID NOT TRIP — checker is broken, not the profile ({detail})"))

        # The bad profile must still satisfy the header contract, or test_voice_contract.py
        # would already catch it and this suite would prove nothing new.
        header_ok, _ = bad_results["headers_present"]
        if header_ok:
            passes += 1
            print(f"\n[PASS] [{genre}] bad profile satisfies the 10-header contract and is "
                  f"still wrong — shape is not quality\n")
        else:
            fails += 1
            print(f"\n[FAIL] [{genre}] bad profile breaks the header contract — it must be "
                  f"wrong on CONTENT only\n")

    from fixtures.mutants_voice import run_mutant_families  # lazy: keeps the import cheap
    from fixtures.holdout_adversary import run_voice_holdout
    m_pass, m_fail = run_mutant_families(corpus, pairs)
    h_pass, h_fail = run_voice_holdout(corpus, pairs)
    return passes + m_pass + h_pass, fails + m_fail + h_fail


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not os.path.exists(CORPUS_PATH):
        print(f"ERROR: missing fixture artifact: {CORPUS_PATH}")
        return 1
    corpus = load_corpus()
    pairs = profile_pairs(corpus)
    for _genre, good, bad in pairs:
        for path in (good, bad):
            if not os.path.exists(path):
                print(f"ERROR: missing fixture artifact: {path}")
                return 1
    passes, fails = run(corpus, pairs)
    print(f"\nVoice extraction eval: {passes} passed, {fails} failed.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
