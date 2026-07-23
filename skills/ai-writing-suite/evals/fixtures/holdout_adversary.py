#!/usr/bin/env python3
"""BLACK-BOX held-out adversary for the comms-draft and voice-onboard checkers.

WHY THIS IS SEPARATE FROM THE MUTANT FAMILIES (the 2026-07-13 audit's BLOCKER)

The white-box families in mutants_draft.py / mutants_voice.py reuse the checkers' own
regexes, constants, and parsing helpers, and compute the very blended figure the
checker computes. A probe built from the checker's own template can only confirm the
checker's stated design; it cannot find the checker's blind spots. All four novel
evasions a reviewer hand-built escaped the families for exactly that reason.

This module is the adversarial claim. Its ONE discipline: it imports NOTHING from the
checkers except their PUBLIC scoring entry points and PUBLIC data loaders —

    run_draft_cases.find_fabrications, run_draft_cases.CHECKS, run_draft_cases.load_draft_cases
    run_voice_extraction.CHECKS, run_voice_extraction.run_checks,
    run_voice_extraction.load_corpus / load_profile / profile_pairs

— and no regexes, no constants (_NEEDS_SPAN, CRITERIA_DIMENSIONS, _BULLET_LABEL,
TRAIT_FEATURES, _DENIAL, _NUMERIC, _MONTHS, …), no parse helpers (parse_sections,
mean_sentence_words, numeric_keys, _num_key, _typed_claim_for_match, …). The payloads
are hand-authored verbatim strings, assembled onto the public good artifacts with the
naive string ops in this file. test_*_extraction / test_draft_cases enforce that
discipline by scanning this module's source for forbidden identifiers.

APPEND-ONLY. Every entry below slipped through a checker that was green at the time
(the four the audit found) or is a fresh probe added here. Never delete an entry; a
deleted evasion is a reopened hole. The two false-positive controls per side stay as
must-NOT-flag assertions.

If the whole holdout is caught 100% on the first try, that is a signal the holdout is
too soft — add a harder verbatim probe, do not celebrate (the same instinct as the
repo's 30-40% baseline-calibration rule). It is not a floor that can be gamed: these
are fixed adversarial artifacts, not a generated rate.

Stdlib only. No model, no key, no network.
"""

from fixtures import run_draft_cases as rdc
from fixtures import run_voice_extraction as rve


# --------------------------------------------------------------------------
# Naive assembly helpers — local, no checker imports.
# --------------------------------------------------------------------------

def _add_to_draft_body(draft, sentence):
    """Insert a sentence just after the '## Draft' line, by plain string search."""
    low = draft.lower()
    idx = low.find("## draft")
    if idx == -1:
        return draft + "\n" + sentence + "\n"
    eol = draft.find("\n", idx)
    eol = len(draft) if eol == -1 else eol
    return draft[:eol + 1] + sentence + "\n" + draft[eol + 1:]


def _add_bullet(md, header, bullet):
    """Append a bullet right under a '## <header>' line, by plain string search."""
    marker = "## " + header
    idx = md.find(marker)
    if idx == -1:
        return md + f"\n{marker}\n{bullet}\n"
    eol = md.find("\n", idx)
    eol = len(md) if eol == -1 else eol
    return md[:eol + 1] + bullet + "\n" + md[eol + 1:]


# --------------------------------------------------------------------------
# DRAFT holdout — bound to the case whose brief supplies "3 March".
# entry: (id, artifact, check, must_catch)
# --------------------------------------------------------------------------

def build_draft_holdout(case):
    good = case["good_draft"]
    # Bind the "3 March"-based evasions to a brief that actually supplies that date,
    # computed locally (plain string search) so this module touches no checker helper.
    source = (case.get("brief", "") + " " + " ".join(case.get("kb_facts") or [])).lower()
    grounded = "3 march" in source
    entries = []
    if "no_fabrication" in case["checks"] and grounded:
        entries += [
            # AUDIT EVASION 1: "$3 million" reused the supported value 3 (from "3 March")
            # while adding a magnitude the source never states.
            ("audit/currency-magnitude-reuses-supported-value",
             _add_to_draft_body(good, "The campaign cost $3 million to run."),
             "no_fabrication", True),
            # AUDIT EVASION 2: "3 November" reused the supported DAY while changing month.
            ("audit/supported-day-wrong-month",
             _add_to_draft_body(good, "We shipped it on 3 November, not before."),
             "no_fabrication", True),
            # FRESH: an invented percentage the brief never states.
            ("fresh/invented-percentage",
             _add_to_draft_body(good, "Retention grew 250% year over year."),
             "no_fabrication", True),
            # FRESH: an invented programme name in natural designator form.
            ("fresh/designator-name",
             _add_to_draft_body(good, "This ran under the Meridian initiative."),
             "no_fabrication", True),
            # FRESH: an invented four-digit year (plain number absent from the brief).
            ("fresh/invented-year",
             _add_to_draft_body(good, "The pilot began back in 2019."),
             "no_fabrication", True),
            # HARDER: an invented multiword name without an entity designator.
            ("harder/bare-multiword-name",
             _add_to_draft_body(good, "The rollout moved forward under Quiet Harbor."),
             "no_fabrication", True),
            # CONTROL: SKILL.md never mandates sentence-case headings.
            ("control/title-case-heading",
             "## Acceptance Criteria\n## Draft\nWe shipped on 3 March.\n",
             "no_fabrication", False),
            # CONTROL: label lines are structure, not invented entities.
            ("control/label-lines",
             "## Draft\nSubject: win-back campaign is live\nRecommendation: ship it.\n"
             "(Standard rubric applied.)\n", "no_fabrication", False),
        ]
    if "no_fabrication" in case["checks"]:
        entries.append(("control/good-draft-untouched", good, "no_fabrication", False))
    if "question_count" in case["checks"]:
        # CONTROL: rhetorical questions in the DRAFT BODY are prose, not step-1 questions.
        entries.append(("control/questions-in-draft-body",
                        good + "\n## Draft\nWhy does this matter? Because churn is up. "
                               "Right? Right. And then? We ship.\n",
                        "question_count", False))
    return entries


# --------------------------------------------------------------------------
# VOICE holdout — per genre, built on the genre's good profile.
# entry: (id, md, check, must_catch)  (check None -> the untouched-good control)
# --------------------------------------------------------------------------

def build_voice_holdout(corpus, good_md, genre):
    noise = corpus["ground_truth"]["genres"][genre]["noise_word"]["word"]
    return [
        # AUDIT EVASION 3: an invented SEMICOLON habit — a punctuation feature the old
        # closed lexicon did not carry, so it was invisible.
        ("audit/invented-semicolon-habit",
         _add_bullet(good_md, "Signature Moves",
                     "- Leans on semicolons to string her clauses together."),
         "no_invented_traits", True),
        # AUDIT EVASION 4: a POSITIVE emoji claim phrased as a double negative. The old
        # code skipped any line holding a denial token, so "not rare" suppressed it.
        ("audit/double-negative-emoji",
         _add_bullet(good_md, "Signature Moves",
                     "- Emoji use is not rare in her posts."),
         "no_invented_traits", True),
        # FRESH: a positive ellipsis habit the corpus does not carry.
        ("fresh/invented-ellipsis-habit",
         _add_bullet(good_md, "Signature Moves",
                     "- Often trails a thought off with ellipses."),
         "no_invented_traits", True),
        # FRESH: a positive rhetorical-question habit (corpus has zero '?').
        ("fresh/invented-question-habit",
         _add_bullet(good_md, "Openings & Closings",
                     "- Loves to open on a rhetorical question."),
         "no_invented_traits", True),
        # CONTROL: the untouched good profile — nothing may flag it.
        ("control/good-profile-untouched", good_md, None, False),
        # CONTROL: naming the 2x accident under an AVOID section is correct extraction.
        ("control/noise-word-noted-in-avoid-section",
         _add_bullet(good_md, "Things To Avoid",
                     f"- {noise} — 2x, do not treat as a habit."),
         "omits_noise_word", False),
        # CONTROL: a DENIED feature ("never — 0 question marks") is mining an absence.
        ("control/absence-denial-not-an-invented-trait",
         _add_bullet(good_md, "Punctuation & Formatting",
                     "- **Question marks:** never — 0 across the samples."),
         "no_invented_traits", False),
    ]


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------

def _draft_caught(check, case, artifact):
    return bool(rdc.CHECKS[check](case, artifact))


def _voice_caught(check, md, corpus, genre):
    ok, _ = rve.CHECKS[check](md, corpus, genre)
    return not ok


def draft_results(cases):
    """[(id, check, must_catch, caught)] for the draft holdout."""
    out = []
    for case in cases:
        for hid, art, check, must in build_draft_holdout(case):
            out.append((f"{case['id']}/{hid}", check, must, _draft_caught(check, case, art)))
    return out


def voice_results(corpus, pairs):
    """[(id, check, must_catch, caught)] for the voice holdout."""
    out = []
    for genre, good_path, _bad in pairs:
        good = rve.load_profile(good_path)
        for hid, md, check, must in build_voice_holdout(corpus, good, genre):
            if check is None:      # untouched-good control: nothing may flag it
                flagged = [n for n, (ok, _) in rve.run_checks(md, corpus, genre).items()
                           if not ok]
                out.append((f"{genre}/{hid}", "any_check", False, bool(flagged)))
            else:
                out.append((f"{genre}/{hid}", check, must,
                            _voice_caught(check, md, corpus, genre)))
    return out


def _report(label, results):
    """Print one holdout cohort's rows. Returns (passes, fails, must_caught, must_total)."""
    passes = fails = must_caught = must_total = 0
    for hid, check, must, caught in results:
        hit = caught if must else not caught
        passes += hit
        fails += not hit
        if must:
            must_total += 1
            must_caught += caught
            verdict = "CAUGHT" if caught else "ESCAPED — a closed gap reopened"
        else:
            verdict = "clean (correct behavior, not flagged)" if not caught \
                else "FALSE POSITIVE"
        print(f"[{'PASS' if hit else 'FAIL'}] [{label}] {hid:52} {check}: {verdict}")
    return passes, fails, must_caught, must_total


def _footer(must_caught, must_total):
    rate = must_caught / must_total if must_total else 0.0
    print(f"    Holdout adversary: must_catch {must_caught}/{must_total} = {rate:.0%} "
          f"(black-box; floor 100%)")
    if must_total and must_caught == must_total:
        print("    NOTE: 100% on the black-box holdout means the current probes are all "
              "closed — add a HARDER verbatim probe rather than trusting the number.")
    print()


def run_draft_holdout(cases):
    """Print the DRAFT black-box holdout report. Returns (passes, fails)."""
    print("-- BLACK-BOX holdout adversary (append-only; shares nothing with the checkers) --")
    passes, fails, mc, mt = _report("draft", draft_results(cases))
    _footer(mc, mt)
    return passes, fails


def run_voice_holdout(corpus, pairs):
    """Print the VOICE black-box holdout report. Returns (passes, fails)."""
    print("-- BLACK-BOX holdout adversary (append-only; shares nothing with the checkers) --")
    passes, fails, mc, mt = _report("voice", voice_results(corpus, pairs))
    _footer(mc, mt)
    return passes, fails
