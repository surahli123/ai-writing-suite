#!/usr/bin/env python3
"""Programmatic mutant FAMILIES for the voice-onboard checkers.

WHY THIS EXISTS (the root cause it removes)

Before this module, every failure mode had exactly ONE positive exemplar (the shipped
bad profile) and ONE negative (the good profile), both authored in the same pass as
the checker. With N=1 per class the separating boundary is wildly underdetermined, so
an author optimizing for "the planted positive trips" converges on the cheapest
discriminator that separates that one pair: a substring lookup, a presence/absence
test, a polarity-blind mention count. Every BLOCKER and MAJOR found in review was an
instance of that shape. Freezing a reviewer's evasion as a static test patches the
instance; it does not remove the class.

A FAMILY removes the class. Each mutant is derived programmatically from the GOOD
artifact, so a checker that memorized one exemplar fails on the very next draw, and
the suite reports a CATCH RATE per mode rather than a binary "the planted positive
tripped".

DETERMINISM: the families are ENUMERATED, not sampled. No RNG, no seed, no clock —
the same mutants in the same order on every run, so CI is byte-reproducible.

DECLARED FLOORS (the `_doc` the fixture asks for; justified, not decorative):

  scope_declared          1.00  — a scope claim is structural text; nothing about it
                                  is ambiguous, so anything under 100% is a bug.
  learns_habit_word       1.00  — the habit word is either claimed in a positive
                                  section or it is not. Binary, so 100% or broken.
  omits_noise_word        1.00  — same shape, opposite direction.
  no_subthreshold_claims  1.00  — a claimed word's genre count is countable exactly.
  genre_scoped_rhythm     1.00  — the claimed figure either tracks the genre mean or
                                  tracks the blended mean; both are computed, not
                                  guessed. The HARD members of this family (a collapse
                                  phrased without the words "average", "both", or a
                                  genre name) are what make the 100% meaningful.
  honest_gap              1.00  — bound to declared sections; countable.
  no_invented_traits      0.75  — the ONE floor below 100%, and it is set below the
                                  family's true rate on purpose. The family contains a
                                  KNOWN MISS: an unquoted, non-feature vocabulary claim
                                  ("leans on synergy framing"). Catching that needs a
                                  free content-word scan, which false-positives the
                                  good profile's own descriptive prose ("reaches",
                                  "abstractions", "reframe" all have zero corpus
                                  support and are not claims about the author's words).
                                  The miss is declared here rather than hidden, and the
                                  floor keeps the rest of the family honest.

A 100% catch rate across EVERY family is a warning, not a celebration: it means the
mutants are too easy and the next reviewer will walk straight through the boundary
they failed to probe. Same instinct as the repo's 30-40% baseline-calibration rule —
an eval nothing can fail is not an eval. When a family hits 100%, add a harder member.

Stdlib only. No model, no key, no network.
"""

import re

from fixtures import run_voice_extraction as rve

# floor = the minimum fraction of a family's mutants the checker must CATCH.
MUTANT_FLOORS = {
    "scope_declared": 1.0,
    "learns_habit_word": 1.0,
    "omits_noise_word": 1.0,
    "no_subthreshold_claims": 1.0,
    "genre_scoped_rhythm": 1.0,
    "honest_gap": 1.0,
    "no_invented_traits": 0.75,
}


# --------------------------------------------------------------------------
# Section surgery (mutants are derived from the good artifact, never hand-authored)
# --------------------------------------------------------------------------

def _split_sections(md):
    """[(header_or_None, [lines])] preserving order, so a section can be rewritten."""
    blocks, current, lines = [], None, []
    for line in md.splitlines():
        if re.match(r"^##\s+", line):
            blocks.append((current, lines))
            current, lines = line, []
        else:
            lines.append(line)
    blocks.append((current, lines))
    return blocks


def _rebuild(blocks):
    out = []
    for header, lines in blocks:
        if header is not None:
            out.append(header)
        out.extend(lines)
    return "\n".join(out) + "\n"


def _header_is(header, name):
    return header is not None and rve.normalize(header[2:].strip()) == rve.normalize(name)


def set_section(md, name, body):
    """Replace a section's body wholesale."""
    blocks = [(h, body.splitlines() if _header_is(h, name) else ls)
              for h, ls in _split_sections(md)]
    return _rebuild(blocks)


def append_to_section(md, name, body):
    """Append lines to a section, leaving the rest of the profile intact."""
    blocks = [(h, (ls + body.splitlines()) if _header_is(h, name) else ls)
              for h, ls in _split_sections(md)]
    return _rebuild(blocks)


def edit_claim_lines(md, fn):
    """Apply fn(line) to every non-blockquote line of every POSITIVE section.

    This is how the inverse-claim mutant strips a habit word from the claims while
    leaving it in the file — the exact trick that beat the direction-blind checker.
    """
    absent = {rve.normalize(h) for h in rve.ABSENCE_SECTIONS}
    out = []
    for header, lines in _split_sections(md):
        if header is not None and rve.normalize(header[2:].strip()) not in absent:
            lines = [ln if ln.lstrip().startswith(">") else fn(ln) for ln in lines]
        out.append((header, lines))
    return _rebuild(out)


# --------------------------------------------------------------------------
# The families. Each returns [(mutant_id, mutated_md)].
# --------------------------------------------------------------------------

def family_scope_declared(good, spec, corpus, genre):
    other = [g for g in rve.genres_of(corpus) if g != genre][0]
    return [
        ("scope/pooled-both-genres", set_section(good, "Scope & Calibration", (
            f"\n- **Applies to:** all of her writing, {genre}s and {other}s alike.\n"
            f"- **Re-calibrate for:** nothing — the profile generalizes.\n"))),
        ("scope/unscoped-everything", set_section(good, "Scope & Calibration", (
            "\n- **Applies to:** everything she writes, whatever the channel.\n"
            "- **Re-calibrate for:** nothing.\n"))),
        ("scope/silent", set_section(good, "Scope & Calibration", (
            "\n- Recalibrate when her style drifts.\n"))),
    ]


def family_learns_habit_word(good, spec, corpus, genre):
    habit = spec["habit_word"]["word"]
    absent = spec["absent_words"][0]["word"]
    swapped = re.sub(rf"\b{re.escape(habit)}\b", absent, good, flags=re.IGNORECASE)

    def strip_habit(line):
        return re.sub(rf'"?\b{re.escape(habit)}\b"?', "the artifact", line,
                      flags=re.IGNORECASE)

    stripped = edit_claim_lines(good, strip_habit)
    inverted = [
        ("habit/inverse-never-writes", append_to_section(
            stripped, "Vocabulary Don't", f"\n- {habit} — she never writes this word.\n")),
        ("habit/inverse-avoid-section", append_to_section(
            stripped, "Things To Avoid",
            f"\n- {habit} — a word she pointedly avoids; do not put it in her mouth.\n")),
        ("habit/inverse-quoted-absence", append_to_section(
            stripped, "Vocabulary Don't", f'\n- "{habit}" — 0 occurrences.\n')),
    ]
    return [
        # the habit word swapped for a word that is 0x in this genre
        ("habit/swapped-for-absent-word", swapped),
        # the habit word simply dropped from every claim
        ("habit/dropped-from-claims", stripped),
    ] + inverted


def family_omits_noise_word(good, spec, corpus, genre):
    noise = spec["noise_word"]["word"]
    return [
        ("noise/quoted-signature-word", append_to_section(
            good, "Vocabulary", f'\n- **More signature words:** "{noise}"\n')),
        ("noise/unquoted-vocabulary-do", append_to_section(
            good, "Vocabulary Do", f"\n- Reaches for the {noise} image whenever charts pile up.\n")),
        ("noise/pooled-justification", append_to_section(
            good, "Vocabulary",
            f"\n- **Habit word:** {noise} — 4 occurrences across all her writing.\n")),
        ("noise/in-tone", append_to_section(
            good, "Tone", f"\n- Reaches for the {noise} metaphor when she is annoyed.\n")),
    ]


def family_no_subthreshold_claims(good, spec, corpus, genre):
    decoy = spec["subthreshold_decoy"]["word"]
    return [
        ("subthreshold/quoted-signature", append_to_section(
            good, "Vocabulary", f'\n- **More signature words:** "{decoy}"\n')),
        ("subthreshold/vocabulary-do", append_to_section(
            good, "Vocabulary Do", f'\n- Reaches for "{decoy}" to frame the point.\n')),
        ("subthreshold/signature-move", append_to_section(
            good, "Signature Moves", f'\n- Lands the paragraph on "{decoy}".\n')),
    ]


def family_genre_scoped_rhythm(good, spec, corpus, genre):
    blended = rve.mean_sentence_words(rve.corpus_text(corpus))
    b = round(blended)
    other = [g for g in rve.genres_of(corpus) if g != genre][0]
    return [
        # the plain collapse: one figure, no genre named
        ("rhythm/flat-average", set_section(good, "Sentence Length", (
            f"\n- **Average words/sentence:** {b}\n"
            f"- **Rhythm habit:** steady, even pacing.\n"))),
        # the reviewer's evasion: names BOTH genres in one breath (v1 read that as a split)
        ("rhythm/both-genres-alike", set_section(good, "Sentence Length", (
            f"Both genres share one rhythm, so a single figure is enough.\n"
            f"- **Average words/sentence ({genre} and {other} alike):** {b}\n"
            f"- Range: 3 to 31 words. Pacing is even; no genre-specific habit found.\n"))),
        # HARD: no "average", no "both", no genre name — nothing lexical to key on
        ("rhythm/hard-no-keywords", set_section(good, "Sentence Length", (
            f"\n- **Typical line:** about {b} words.\n"
            f"- She writes at one speed and the speed does not shift.\n"))),
        # HARD: decimal surface, prose framing, figure still the blended mean
        ("rhythm/hard-decimal-prose", set_section(good, "Sentence Length", (
            f"\nOne number covers the whole sample set: {blended:.1f} words a sentence, "
            f"start to finish.\n"))),
        # the blended figure smuggled in ALONGSIDE the correct one
        ("rhythm/correct-plus-blended", append_to_section(
            good, "Sentence Length",
            f"\n- **Across all her writing:** {b} words/sentence — use this when in doubt.\n")),
    ]


def family_no_invented_traits(good, spec, corpus, genre):
    foreign = spec["foreign_habit_word"]["word"]
    return [
        ("invented/quoted-word", append_to_section(
            good, "Vocabulary Do", '\n- Frames team work as "synergy" between functions.\n')),
        # the reviewer's evasion: unquoted feature assertions, nothing to key on lexically
        ("invented/unquoted-features", append_to_section(
            good, "Signature Moves", (
                "\n- Habitually opens with a rhetorical question and closes with a rocket emoji.\n"
                "- Frequent exclamation marks; heavy em-dash use; leans on synergy framing.\n"))),
        ("invented/paraphrased-feature", append_to_section(
            good, "Punctuation & Formatting",
            "\n- Ends a launch post with a rocket, every time.\n")),
        # cross-genre import: the OTHER genre's habit word, 0x here. Pooling puts it here.
        ("invented/cross-genre-import", append_to_section(
            good, "Vocabulary", f'\n- **More signature words:** "{foreign}"\n')),
        # KNOWN MISS (declared in the module _doc): unquoted, non-feature vocabulary claim.
        # Catching it needs a free content-word scan, which false-positives the good
        # profile's own meta-prose. Kept in the family so the rate tells the truth.
        ("invented/hard-unquoted-vocabulary", append_to_section(
            good, "Vocabulary Do", "\n- Leans on synergy framing when two teams disagree.\n")),
    ]


def family_honest_gap(good, spec, corpus, genre):
    out = []
    for section in spec["expected_unknown_sections"]:
        out.append((f"gap/{section}/confident", set_section(good, section, (
            "\n- Blunt: never hedges, always commits to the number.\n"))))
        # the phrase still appears elsewhere in the file — the "park it somewhere" evasion
        out.append((f"gap/{section}/parked-elsewhere", append_to_section(
            set_section(good, section, "\n- Quantified: she always states a confidence.\n"),
            "Tone", f"\n- Emoji habit: {rve.HONEST_GAP} in samples.\n")))
    return out


FAMILIES = {
    "scope_declared": family_scope_declared,
    "learns_habit_word": family_learns_habit_word,
    "omits_noise_word": family_omits_noise_word,
    "no_subthreshold_claims": family_no_subthreshold_claims,
    "no_invented_traits": family_no_invented_traits,
    "genre_scoped_rhythm": family_genre_scoped_rhythm,
    "honest_gap": family_honest_gap,
}


# --------------------------------------------------------------------------
# The APPEND-ONLY hard tail: evasions constructed by hand against a live checker.
# Never delete an entry. Each one slipped through a checker that was green at the time.
# --------------------------------------------------------------------------

def hard_tail(good, spec, corpus, genre):
    """[(id, md, mode, must_catch)] — reviewer artifacts, plus false-positive controls."""
    noise = spec["noise_word"]["word"]
    items = [
        ("reviewer/averaged-profile", family_genre_scoped_rhythm(good, spec, corpus, genre)[1][1],
         "genre_scoped_rhythm", True),
        ("reviewer/inverted-habit-claim", family_learns_habit_word(good, spec, corpus, genre)[2][1],
         "learns_habit_word", True),
        ("reviewer/unquoted-invented-trait", family_no_invented_traits(good, spec, corpus, genre)[1][1],
         "no_invented_traits", True),
        # FALSE-POSITIVE CONTROLS: correct behavior that a rigged checker punished.
        ("control/good-profile-untouched", good, None, False),
        ("control/noise-word-noted-in-avoid-section", append_to_section(
            good, "Things To Avoid",
            f"\n- {noise} — 2x, do not treat as a habit.\n"), "omits_noise_word", False),
        ("control/absence-denial-not-an-invented-trait", append_to_section(
            good, "Punctuation & Formatting",
            "\n- **Question marks:** never — 0 across the samples.\n"),
         "no_invented_traits", False),
    ]
    return items


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------

def catch_rates(corpus, pairs):
    """{mode: (caught, total)} over every genre's generated family. Pure, deterministic."""
    rates = {}
    for genre, good_path, _bad in pairs:
        good = rve.load_profile(good_path)
        spec = corpus["ground_truth"]["genres"][genre]
        for mode, build in FAMILIES.items():
            caught, total = rates.get(mode, (0, 0))
            for _mid, md in build(good, spec, corpus, genre):
                ok, _detail = rve.CHECKS[mode](md, corpus, genre)
                caught += (not ok)      # a CAUGHT mutant is one the check FAILS
                total += 1
            rates[mode] = (caught, total)
    return rates


def run_mutant_families(corpus, pairs):
    """Print per-mode catch rates + the hard tail. Returns (passes, fails)."""
    passes = fails = 0
    print("-- mutant families (generated from the GOOD artifact; catch rate vs declared floor) --")

    rates = catch_rates(corpus, pairs)
    misses = []
    for genre, good_path, _bad in pairs:
        good = rve.load_profile(good_path)
        spec = corpus["ground_truth"]["genres"][genre]
        for mode, build in FAMILIES.items():
            for mid, md in build(good, spec, corpus, genre):
                ok, _ = rve.CHECKS[mode](md, corpus, genre)
                if ok:
                    misses.append(f"{genre}/{mid} ({mode})")

    for mode in sorted(rates):
        caught, total = rates[mode]
        rate = caught / total if total else 0.0
        floor = MUTANT_FLOORS[mode]
        ok = rate >= floor
        passes += ok
        fails += not ok
        print(f"[{'PASS' if ok else 'FAIL'}] {mode:24} catch rate {caught}/{total} = "
              f"{rate:.0%}  (floor {floor:.0%})"
              + ("" if ok else "  <-- BELOW FLOOR: the checker is memorizing exemplars"))
    if misses:
        print("    known misses (declared, not hidden): " + ", ".join(misses))
    if all(rates[m][0] == rates[m][1] for m in rates):
        print("    NOTE: 100% across every family is SUSPICIOUS, not reassuring — the mutants "
              "are too easy. Add a harder member before trusting this number.")

    print("\n-- hard tail (append-only reviewer evasions + false-positive controls) --")
    for genre, good_path, _bad in pairs:
        good = rve.load_profile(good_path)
        spec = corpus["ground_truth"]["genres"][genre]
        for hid, md, mode, must_catch in hard_tail(good, spec, corpus, genre):
            if mode is None:   # the untouched good profile: nothing may flag it
                bad = [n for n, (ok, _) in rve.run_checks(md, corpus, genre).items() if not ok]
                good_run = not bad
                passes += good_run
                fails += not good_run
                print(f"[{'PASS' if good_run else 'FAIL'}] [{genre}] {hid:44} "
                      + ("clean on every check" if good_run else f"FALSE POSITIVE on {bad}"))
                continue
            ok, detail = rve.CHECKS[mode](md, corpus, genre)
            caught = not ok
            hit = caught if must_catch else not caught
            passes += hit
            fails += not hit
            verdict = ("CAUGHT" if caught else "ESCAPED") if must_catch \
                else ("clean (correct behavior, not flagged)" if not caught
                      else f"FALSE POSITIVE — {detail}")
            print(f"[{'PASS' if hit else 'FAIL'}] [{genre}] {hid:44} {mode}: {verdict}")
    print()
    return passes, fails
