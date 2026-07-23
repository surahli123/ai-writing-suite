#!/usr/bin/env python3
"""White-box mutant FAMILIES for the voice-onboard checkers (cheap smoke).

WHY THIS EXISTS (the root cause it removes)

Before this module, every failure mode had exactly ONE positive exemplar (the shipped
bad profile) and ONE negative (the good profile), both authored in the same pass as
the checker. With N=1 the separating boundary is underdetermined, so an author
optimizing for "the planted positive trips" converges on the cheapest discriminator
that separates that one pair: a substring lookup, a presence/absence test, a
polarity-blind mention count. Every BLOCKER and MAJOR found in review was an instance
of that shape. A FAMILY removes the class, because a checker that memorized one
exemplar fails on the very next draw.

These families are WHITE-BOX — they reuse the checker's section-surgery helpers and
know the blended figure the checker computes — so they can only probe the checker's
stated design, not its blind spots. That is why they are "cheap smoke" here; the
adversarial claim lives in the BLACK-BOX holdout (fixtures/holdout_adversary.py),
which shares nothing with the checker.

FIX-3 SEMANTICS (per the 2026-07-13 audit):
  * Every member is tagged `must_catch` or `expected_escape`.
  * must_catch families have a 100% floor — ONE escape fails the run. No floor is set
    "just under the observed rate"; a tolerated gap is where uncovered behavior hid.
  * expected_escape members are documented known gaps, reported separately and NOT in
    the catch-rate denominator.
  * Unique mutation TEMPLATES are reported separately from per-genre instantiations.

KNOWN GAP (expected_escape, declared not hidden):
  * invented/hard-unquoted-vocabulary — an unquoted, non-feature vocabulary claim
    ("leans on synergy framing"). Catching it needs a free content-word scan, which
    false-positives the good profile's own descriptive prose ("reaches",
    "abstractions", "reframe" have zero corpus support and are not claims about the
    author's words).

DETERMINISM: enumerated, not sampled. No RNG, no seed, no clock — byte-reproducible.

Stdlib only. No model, no key, no network.
"""

import re

from fixtures import run_voice_extraction as rve

MUST_CATCH_FLOOR = 1.0


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


def set_subsection(md, section, subsection, body):
    """Replace one H3 body inside an H2 section while preserving all other content."""
    out = []
    target = rve.normalize(subsection)
    for header, lines in _split_sections(md):
        if not _header_is(header, section):
            out.append((header, lines))
            continue
        start = next((i for i, line in enumerate(lines)
                      if re.match(r"^###\s+", line)
                      and rve.normalize(line[3:].strip()) == target), None)
        if start is None:
            lines = lines + [f"### {subsection}"] + body.splitlines()
        else:
            end = next((i for i in range(start + 1, len(lines))
                        if re.match(r"^###\s+", lines[i])), len(lines))
            lines = lines[:start + 1] + body.splitlines() + lines[end:]
        out.append((header, lines))
    return _rebuild(out)


def edit_claim_lines(md, fn):
    """Apply fn(line) to every non-blockquote line of every POSITIVE section."""
    absent = {rve.normalize(h) for h in rve.ABSENCE_SECTIONS}
    out = []
    for header, lines in _split_sections(md):
        if header is not None and rve.normalize(header[2:].strip()) not in absent:
            lines = [ln if ln.lstrip().startswith(">") else fn(ln) for ln in lines]
        out.append((header, lines))
    return _rebuild(out)


# --------------------------------------------------------------------------
# The families. Each returns [(template, mutated_md, klass)] with klass "must"/"escape".
# --------------------------------------------------------------------------

def family_scope_declared(good, spec, corpus, genre):
    other = [g for g in rve.genres_of(corpus) if g != genre][0]
    return [
        ("pooled-both-genres", set_section(good, "Scope & Calibration", (
            f"\n- **Applies to:** all of her writing, {genre}s and {other}s alike.\n"
            f"- **Re-calibrate for:** nothing — the profile generalizes.\n")), "must"),
        ("unscoped-everything", set_section(good, "Scope & Calibration", (
            "\n- **Applies to:** everything she writes, whatever the channel.\n"
            "- **Re-calibrate for:** nothing.\n")), "must"),
        ("silent", set_section(good, "Scope & Calibration",
                               "\n- Recalibrate when her style drifts.\n"), "must"),
    ]


def family_learns_habit_word(good, spec, corpus, genre):
    habit = spec["habit_word"]["word"]
    absent = spec["absent_words"][0]["word"]
    swapped = re.sub(rf"\b{re.escape(habit)}\b", absent, good, flags=re.IGNORECASE)

    def strip_habit(line):
        return re.sub(rf'"?\b{re.escape(habit)}\b"?', "the artifact", line,
                      flags=re.IGNORECASE)

    stripped = edit_claim_lines(good, strip_habit)
    return [
        ("swapped-for-absent-word", swapped, "must"),
        ("dropped-from-claims", stripped, "must"),
        ("inverse-never-writes", append_to_section(
            stripped, "Vocabulary Don't", f"\n- {habit} — she never writes this word.\n"),
         "must"),
        ("inverse-avoid-section", append_to_section(
            stripped, "Things To Avoid",
            f"\n- {habit} — a word she pointedly avoids; do not put it in her mouth.\n"),
         "must"),
        ("inverse-quoted-absence", append_to_section(
            stripped, "Vocabulary Don't", f'\n- "{habit}" — 0 occurrences.\n'), "must"),
    ]


def family_omits_noise_word(good, spec, corpus, genre):
    noise = spec["noise_word"]["word"]
    return [
        ("quoted-signature-word", append_to_section(
            good, "Vocabulary", f'\n- **More signature words:** "{noise}"\n'), "must"),
        ("unquoted-vocabulary-do", append_to_section(
            good, "Vocabulary Do",
            f"\n- Reaches for the {noise} image whenever charts pile up.\n"), "must"),
        ("pooled-justification", append_to_section(
            good, "Vocabulary",
            f"\n- **Habit word:** {noise} — 4 occurrences across all her writing.\n"), "must"),
        ("in-tone", append_to_section(
            good, "Tone",
            f"\n- Reaches for the {noise} metaphor when she is annoyed.\n"), "must"),
    ]


def family_no_subthreshold_claims(good, spec, corpus, genre):
    decoy = spec["subthreshold_decoy"]["word"]
    return [
        ("quoted-signature", append_to_section(
            good, "Vocabulary", f'\n- **More signature words:** "{decoy}"\n'), "must"),
        ("vocabulary-do", append_to_section(
            good, "Vocabulary Do", f'\n- Reaches for "{decoy}" to frame the point.\n'), "must"),
        ("signature-move", append_to_section(
            good, "Signature Moves", f'\n- Lands the paragraph on "{decoy}".\n'), "must"),
    ]


def family_genre_scoped_rhythm(good, spec, corpus, genre):
    blended = rve.mean_sentence_words(rve.corpus_text(corpus))
    b = round(blended)
    other = [g for g in rve.genres_of(corpus) if g != genre][0]
    return [
        ("flat-average", set_section(good, "Sentence Length", (
            f"\n- **Average words/sentence:** {b}\n"
            f"- **Rhythm habit:** steady, even pacing.\n")), "must"),
        ("both-genres-alike", set_section(good, "Sentence Length", (
            f"Both genres share one rhythm, so a single figure is enough.\n"
            f"- **Average words/sentence ({genre} and {other} alike):** {b}\n"
            f"- Range: 3 to 31 words. Pacing is even; no genre-specific habit found.\n")),
         "must"),
        # HARD: no "average", no "both", no genre name — nothing lexical to key on.
        ("hard-no-keywords", set_section(good, "Sentence Length", (
            f"\n- **Typical line:** about {b} words.\n"
            f"- She writes at one speed and the speed does not shift.\n")), "must"),
        ("hard-decimal-prose", set_section(good, "Sentence Length", (
            f"\nOne number covers the whole sample set: {blended:.1f} words a sentence, "
            f"start to finish.\n")), "must"),
        ("correct-plus-blended", append_to_section(
            good, "Sentence Length",
            f"\n- **Across all her writing:** {b} words/sentence — use this when in doubt.\n"),
         "must"),
    ]


def family_no_invented_traits(good, spec, corpus, genre):
    foreign = spec["foreign_habit_word"]["word"]
    return [
        ("quoted-word", append_to_section(
            good, "Vocabulary Do",
            '\n- Frames team work as "synergy" between functions.\n'), "must"),
        ("unquoted-features", append_to_section(
            good, "Signature Moves", (
                "\n- Habitually opens with a rhetorical question and closes with a rocket emoji.\n"
                "- Frequent exclamation marks; heavy em-dash use.\n")), "must"),
        ("paraphrased-feature", append_to_section(
            good, "Punctuation & Formatting",
            "\n- Ends a launch post with a rocket, every time.\n"), "must"),
        ("cross-genre-import", append_to_section(
            good, "Vocabulary", f'\n- **More signature words:** "{foreign}"\n'), "must"),
        # Declared known gap (expected_escape): see module _doc.
        ("hard-unquoted-vocabulary", append_to_section(
            good, "Vocabulary Do",
            "\n- Leans on synergy framing when two teams disagree.\n"), "escape"),
    ]


def family_honest_gap(good, spec, corpus, genre):
    out = []
    for section in spec["expected_unknown_sections"]:
        out.append((f"{section}/confident", set_section(good, section, (
            "\n- Blunt: never hedges, always commits to the number.\n")), "must"))
        out.append((f"{section}/parked-elsewhere", append_to_section(
            set_section(good, section, "\n- Quantified: she always states a confidence.\n"),
            "Tone", f"\n- Emoji habit: {rve.HONEST_GAP} in samples.\n"), "must"))
    return out


def family_self_report_divergence(good, spec, corpus, genre):
    report = corpus["ground_truth"]["self_report"]
    feature = report["feature"]
    actual = report["genre_counts"][genre]
    generic_only = set_subsection(
        good, "Things To Avoid", rve.SELF_REPORT_SUBSECTION,
        "\n- Self-report divergence.\n")
    return [
        ("omitted", set_subsection(
            good, "Things To Avoid", rve.SELF_REPORT_SUBSECTION,
            "\n- No self-report mismatches recorded.\n"), "must"),
        ("generic-substring-only", generic_only, "must"),
        ("wrong-measured-count", set_subsection(
            good, "Things To Avoid", rve.SELF_REPORT_SUBSECTION, (
                f"\n- **Stated:** the author reported frequent {feature}.\n"
                f"- **Measured:** {actual + 1} {feature} in the {genre} corpus; "
                "this contradicts the self-report.\n")), "must"),
        ("substring-only-plus-adoption", append_to_section(
            generic_only, "Punctuation & Formatting",
            f"\n- Frequent {feature} are a learned habit.\n"), "must"),
        ("surfaced-plus-adoption", append_to_section(
            good, "Punctuation & Formatting",
            f"\n- Frequent {feature} are a learned habit.\n"), "must"),
    ]


FAMILIES = {
    "scope_declared": family_scope_declared,
    "learns_habit_word": family_learns_habit_word,
    "omits_noise_word": family_omits_noise_word,
    "no_subthreshold_claims": family_no_subthreshold_claims,
    "no_invented_traits": family_no_invented_traits,
    "genre_scoped_rhythm": family_genre_scoped_rhythm,
    "honest_gap": family_honest_gap,
    "self_report_divergence": family_self_report_divergence,
}


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------

def _caught(mode, md, corpus, genre):
    ok, _ = rve.CHECKS[mode](md, corpus, genre)
    return not ok            # a CAUGHT mutant is one the check FAILS


def catch_rates(corpus, pairs):
    """{mode: (caught, total)} over must_catch instantiations only. Deterministic."""
    rates = {}
    for genre, good_path, _bad in pairs:
        good = rve.load_profile(good_path)
        spec = corpus["ground_truth"]["genres"][genre]
        for mode, build in FAMILIES.items():
            caught, total = rates.get(mode, (0, 0))
            for _tmpl, md, klass in build(good, spec, corpus, genre):
                if klass != "must":
                    continue
                caught += _caught(mode, md, corpus, genre)
                total += 1
            rates[mode] = (caught, total)
    return rates


def template_counts(corpus, pairs):
    """{mode: (unique_must_templates, must_instantiations)}."""
    counts = {}
    for genre, good_path, _bad in pairs:
        good = rve.load_profile(good_path)
        spec = corpus["ground_truth"]["genres"][genre]
        for mode, build in FAMILIES.items():
            tmpls, insts = counts.get(mode, (set(), 0))
            for tmpl, _md, klass in build(good, spec, corpus, genre):
                if klass != "must":
                    continue
                tmpls = tmpls | {tmpl}
                insts += 1
            counts[mode] = (tmpls, insts)
    return {k: (len(t), n) for k, (t, n) in counts.items()}


def expected_escapes(corpus, pairs):
    """[(mode, genre, template)] for every declared known gap — honesty ledger."""
    out = []
    for genre, good_path, _bad in pairs:
        good = rve.load_profile(good_path)
        spec = corpus["ground_truth"]["genres"][genre]
        for mode, build in FAMILIES.items():
            for tmpl, _md, klass in build(good, spec, corpus, genre):
                if klass == "escape":
                    out.append((mode, genre, tmpl))
    return out


def run_mutant_families(corpus, pairs):
    """Print must_catch rates (100% floor) + declared gaps. Returns (passes, fails)."""
    passes = fails = 0
    print("-- white-box mutant families (cheap smoke; must_catch floor 100%) --")

    rates = catch_rates(corpus, pairs)
    tmpl = template_counts(corpus, pairs)
    for mode in sorted(rates):
        caught, total = rates[mode]
        rate = caught / total if total else 0.0
        ok = rate >= MUST_CATCH_FLOOR
        passes += ok
        fails += not ok
        uniq, insts = tmpl[mode]
        print(f"[{'PASS' if ok else 'FAIL'}] {mode:24} must_catch {caught}/{total} = {rate:.0%}"
              f"  ({uniq} templates x genres = {insts}; floor 100%)"
              + ("" if ok else "  <-- ESCAPE: a must_catch mutant slipped the checker"))

    escapes = expected_escapes(corpus, pairs)
    if escapes:
        print("    expected_escape (declared gaps, NOT in denominator): "
              + ", ".join(f"{m}:{g}/{t}" for m, g, t in escapes))
    print()
    return passes, fails
