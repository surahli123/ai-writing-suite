#!/usr/bin/env python3
"""Run the voice-onboard extraction eval.

Run from `evals/`:
    python3 -m fixtures.run_voice_extraction

WHAT THIS MEASURES (and why it is not the header contract test)

test_voice_contract.py asserts the 10 `## H2` headers exist. That is shape, not
quality: a profile can carry every header and still have learned the wrong voice.
This suite grades CONTENT against a corpus whose ground truth is countable by hand.

voice-onboard is skill prose — an agent reads samples and writes a profile — so
there is no extraction function to unit-test. Testing it would be vacuous ("assert
the corpus parses"). Instead:

  1. voice_corpus.json is SYNTHETIC and engineered: a habit word at exactly 4x, a
     noise word at exactly 2x, two absent words at 0x, and two genres with genuinely
     different rhythm.
  2. Two pre-authored PROFILE ARTIFACTS stand in for voice-onboard's output — one
     correct, one wrong in named, specific ways.
  3. Deterministic checks must tell them apart. The good profile must pass every
     check; the bad profile must FAIL each of its declared failure modes. If the bad
     profile ever stops tripping a check, the checker itself is broken and the run
     fails — that is the planted-positive gate.

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
GOOD_PATH = os.path.join(HERE, "voice_profile_good.md")
BAD_PATH = os.path.join(HERE, "voice_profile_bad.md")

# The 10 headers comms-polish reads (same contract test_voice_contract.py guards on
# the template). Both artifacts must satisfy it — which is exactly why passing it
# proves nothing about voice quality.
REQUIRED_HEADERS = [
    "Tone", "Sentence Length", "Vocabulary Do", "Vocabulary Don't",
    "Signature Moves", "Punctuation & Formatting", "Openings & Closings",
    "Uncertainty Style", "Things To Avoid", "Scope & Calibration",
]

# Sections that describe what the author does NOT do. A word named here is expected
# to have zero corpus occurrences, so the invented-trait scan must skip them —
# otherwise correctly mining an absence would read as inventing a trait.
ABSENCE_SECTIONS = {"Vocabulary Don't", "Things To Avoid"}

HONEST_GAP = "Unknown — not enough signal"


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
    return " ".join(s["text"] for s in corpus["samples"]
                    if genre is None or s["genre"] == genre)


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
    return s.replace("’", "'").strip()


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


def profile_mentions(word, md):
    """Does the profile claim this word anywhere (comments excluded)?"""
    return count_word(word, strip_comments(md)) > 0


def quoted_terms(sections):
    """Single-word terms the profile puts in quotes inside CLAIM sections.

    A profile asserts traits by quoting them ("signature words: 'ledger'"). Evidence
    lines quote whole sentences, which is why only single tokens are collected — a
    pasted sentence is proof, not a claim. Absence sections are excluded (see above).
    """
    terms = set()
    for header, body in sections.items():
        if normalize(header) in {normalize(h) for h in ABSENCE_SECTIONS}:
            continue
        for m in re.finditer(r"[\"“]([A-Za-z][A-Za-z'’-]*)[\"”]", body):
            terms.add(m.group(1).lower())
    return terms


# --------------------------------------------------------------------------
# Ground truth: declared vs recomputed
# --------------------------------------------------------------------------

def verify_ground_truth(corpus):
    """Recompute every declared count from the samples. Any drift is fatal.

    Returns (recomputed: dict, errors: list[str]).
    """
    gt = corpus["ground_truth"]
    text = corpus_text(corpus)
    errors = []
    recomputed = {}

    for key in ("habit_word", "noise_word", "boundary_decoy"):
        spec = gt[key]
        actual = count_word(spec["word"], text)
        recomputed[spec["word"]] = actual
        if actual != spec["count"]:
            errors.append(
                f"GROUND TRUTH DRIFT: '{spec['word']}' declared {spec['count']}x, "
                f"recomputed {actual}x. Fix the SAMPLES, not the declared count.")

    for spec in gt["absent_words"]:
        actual = count_word(spec["word"], text)
        recomputed[spec["word"]] = actual
        if actual != spec["count"]:
            errors.append(
                f"GROUND TRUTH DRIFT: '{spec['word']}' declared {spec['count']}x, "
                f"recomputed {actual}x. The absence signal is void.")

    # The 3+ rule only has teeth if the two words really do straddle it.
    if recomputed.get(gt["habit_word"]["word"], 0) < 3:
        errors.append("habit_word does not clear the SKILL's 3+ rule — the fixture "
                      "cannot test 'learn the habit'.")
    if recomputed.get(gt["noise_word"]["word"], 0) >= 3:
        errors.append("noise_word clears the 3+ rule — it is no longer noise, so the "
                      "fixture cannot test 'don't learn an accident'.")

    # Genre rhythm must actually differ, or "don't average across genres" is untestable.
    means = {g: mean_sentence_words(corpus_text(corpus, g))
             for g in gt["genres"]}
    recomputed["_genre_means"] = means
    tw, mo = gt["genres"]["tweet"], gt["genres"]["memo"]
    if means["tweet"] > tw["max_mean_sentence_words"]:
        errors.append(f"tweet mean {means['tweet']:.1f} exceeds declared max "
                      f"{tw['max_mean_sentence_words']}")
    if means["memo"] < mo["min_mean_sentence_words"]:
        errors.append(f"memo mean {means['memo']:.1f} below declared min "
                      f"{mo['min_mean_sentence_words']}")
    gap = abs(means["memo"] - means["tweet"])
    recomputed["_genre_gap"] = gap
    if gap < gt["min_genre_mean_gap_words"]:
        errors.append(f"genre rhythm gap {gap:.1f} words < declared minimum "
                      f"{gt['min_genre_mean_gap_words']} — averaging the genres would "
                      f"not be detectably wrong.")
    return recomputed, errors


# --------------------------------------------------------------------------
# The checks. Each returns (ok: bool, detail: str).
# --------------------------------------------------------------------------

def check_headers_present(md, corpus):
    sections = {normalize(h) for h in parse_sections(md)}
    missing = [h for h in REQUIRED_HEADERS if normalize(h) not in sections]
    return (not missing,
            "all 10 consumer headers present" if not missing
            else f"missing headers: {missing}")


def check_learns_habit_word(md, corpus):
    word = corpus["ground_truth"]["habit_word"]["word"]
    n = count_word(word, corpus_text(corpus))
    ok = profile_mentions(word, md)
    return ok, (f"'{word}' ({n}x, clears 3+) "
                + ("is learned" if ok else "is MISSING from the profile"))


def check_omits_noise_word(md, corpus):
    word = corpus["ground_truth"]["noise_word"]["word"]
    n = count_word(word, corpus_text(corpus))
    ok = not profile_mentions(word, md)
    return ok, (f"'{word}' ({n}x, fails 3+) "
                + ("correctly not learned" if ok
                   else "was LEARNED AS A HABIT — an accident promoted to a trait"))


def check_lists_absence(md, corpus):
    sections = parse_sections(md)
    dont = sections.get("Vocabulary Don't", "")
    missing = [spec["word"] for spec in corpus["ground_truth"]["absent_words"]
               if count_word(spec["word"], dont) == 0]
    return (not missing,
            "0x words mined into Vocabulary Don't" if not missing
            else f"absences not mined (0x in corpus, absent from Vocabulary Don't): {missing}")


def check_splits_genres(md, corpus):
    """The corpus is mixed-genre, so one flat sentence-length figure is wrong.

    A correct profile names the genres in Sentence Length and reports a figure per
    genre. Detection: the section must name every corpus genre AND carry >= 2
    distinct numbers.
    """
    body = parse_sections(md).get("Sentence Length", "")
    genres = sorted({s["genre"] for s in corpus["samples"]})
    named = [g for g in genres if count_word(g, body) > 0]
    numbers = {float(n) for n in re.findall(r"\d+(?:\.\d+)?", body)}
    ok = len(named) == len(genres) and len(numbers) >= 2
    if ok:
        return True, f"sentence length split by genre {genres} ({len(numbers)} figures)"
    if len(named) < len(genres):
        return False, (f"AVERAGED ACROSS GENRES: Sentence Length names {named or 'no'} "
                       f"genre(s), corpus has {genres} — one flat figure describes neither")
    return False, f"Sentence Length names the genres but reports only {len(numbers)} figure(s)"


def check_no_invented_traits(md, corpus):
    """A trait word claimed in a claim section with ZERO corpus support is invented."""
    text = corpus_text(corpus)
    invented = sorted(t for t in quoted_terms(parse_sections(md))
                      if count_word(t, text) == 0)
    return (not invented,
            "every claimed trait word has corpus support" if not invented
            else f"INVENTED (0 occurrences in corpus): {invented}")


def check_honest_gap(md, corpus):
    """The SKILL: no evidence -> 'Unknown — not enough signal', never invent."""
    ok = HONEST_GAP.lower() in strip_comments(md).lower()
    return ok, ("marks at least one gap Unknown rather than guessing" if ok
                else f"no '{HONEST_GAP}' anywhere — every field filled confidently")


CHECKS = {
    "headers_present": check_headers_present,
    "learns_habit_word": check_learns_habit_word,
    "omits_noise_word": check_omits_noise_word,
    "lists_absence": check_lists_absence,
    "splits_genres": check_splits_genres,
    "no_invented_traits": check_no_invented_traits,
    "honest_gap": check_honest_gap,
}

# The bad profile's declared failure modes. Every one MUST trip; a bad profile that
# sails through a check means the check is broken, and a broken check is a green run
# that proves nothing.
BAD_MUST_FAIL = [
    "learns_habit_word", "omits_noise_word", "lists_absence",
    "splits_genres", "no_invented_traits", "honest_gap",
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


def run_checks(md, corpus):
    return {name: fn(md, corpus) for name, fn in CHECKS.items()}


def run(corpus, good_md, bad_md):
    """Grade both artifacts. Returns (passes, fails)."""
    passes = fails = 0

    print("=== voice-onboard extraction eval ===\n")

    if not corpus.get("samples"):
        print("ERROR: empty corpus — nothing to extract from, every check is vacuous.")
        return 0, 1

    recomputed, gt_errors = verify_ground_truth(corpus)
    print("-- ground truth (declared in fixture, RECOMPUTED from sample text) --")
    for word, n in recomputed.items():
        if word.startswith("_"):
            continue
        print(f"    {word:14} {n}x")
    means = recomputed["_genre_means"]
    print("    genre mean words/sentence: "
          + ", ".join(f"{g}={m:.1f}" for g, m in sorted(means.items()))
          + f"  (gap {recomputed['_genre_gap']:.1f})")
    if gt_errors:
        for e in gt_errors:
            print(f"[FAIL] {e}")
        return 0, len(gt_errors)
    print("[PASS] declared ground truth == recomputed\n")

    print("-- GOOD profile (must pass every check) --")
    for name, (ok, detail) in run_checks(good_md, corpus).items():
        passes += ok
        fails += not ok
        print(f"[{'PASS' if ok else 'FAIL'}] {name:20} {detail}")

    print("\n-- BAD profile (the planted positive: each declared mode MUST trip) --")
    bad_results = run_checks(bad_md, corpus)
    for name in BAD_MUST_FAIL:
        ok, detail = bad_results[name]
        tripped = not ok           # we WANT the check to fail on the bad profile
        passes += tripped
        fails += not tripped
        print(f"[{'PASS' if tripped else 'FAIL'}] {name:20} "
              + (f"tripped as declared — {detail}" if tripped
                 else f"DID NOT TRIP — checker is broken, not the profile ({detail})"))

    # Sanity: the bad profile must still satisfy the header contract. If it did not,
    # the header test alone would catch it and this suite would prove nothing new.
    header_ok, _ = bad_results["headers_present"]
    if not header_ok:
        print("\n[FAIL] the bad profile breaks the header contract — it must be wrong on "
              "CONTENT only, or this suite adds nothing over test_voice_contract.py")
        fails += 1
    else:
        print("\n[PASS] bad profile satisfies the 10-header contract and is still wrong — "
              "shape is not quality")
        passes += 1

    return passes, fails


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    for path in (CORPUS_PATH, GOOD_PATH, BAD_PATH):
        if not os.path.exists(path):
            print(f"ERROR: missing fixture artifact: {path}")
            return 1
    corpus = load_corpus()
    passes, fails = run(corpus, load_profile(GOOD_PATH), load_profile(BAD_PATH))
    print(f"\nVoice extraction eval: {passes} passed, {fails} failed.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
