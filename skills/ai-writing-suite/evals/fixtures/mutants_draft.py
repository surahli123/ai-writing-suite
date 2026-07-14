#!/usr/bin/env python3
"""Programmatic mutant FAMILIES for the comms-draft checkers.

WHY THIS EXISTS (the root cause it removes)

Each failure mode used to have exactly ONE positive exemplar (the case's bad_draft)
and ONE negative (its good_draft), both authored in the same pass as the checker.
With N=1 per class the separating boundary is underdetermined, so an author
optimizing for "the planted positive trips" converges on the cheapest discriminator
that separates that one pair — a raw substring lookup for numbers, a line count for
questions, a bag-of-words test for criteria. Every finding in review was an instance
of that shape. A reviewer's evasion frozen as a static test patches the instance; a
FAMILY drawn from the same generator removes the class, because a checker that
memorized one exemplar fails on the next draw.

Every mutant is derived programmatically from the case's GOOD draft — never
hand-authored to be caught.

DETERMINISM: families are ENUMERATED, not sampled. No RNG, no seed, no clock. The
same mutants in the same order on every run, so CI is byte-reproducible.

DECLARED FLOORS (justified, not decorative):

  needs_marker         1.00 — the marker is present or it is not. Binary.
  question_count       1.00 — '?' marks in the pre-draft are countable exactly.
  criteria_dimensions  1.00 — a dimension is named as a criterion or it is not.
  no_fabrication       0.80 — deliberately below the family's true rate, because the
                             family carries TWO KNOWN MISSES, declared rather than
                             hidden:
                               * a SPELLED-OUT number ("fifty percent") — the checker
                                 tokenizes digits, so a written-out numeral is invisible
                                 to it. Catching it needs a number-word lexicon, which
                                 buys false positives on ordinary prose ("one read",
                                 "three Friday deploys" — both live in the shipped good
                                 drafts and both come from the brief).
                               * a BARE single-word invented name ("Falcon") with no
                                 designator and no capitalized neighbour. A lone
                                 capitalized word is not a candidate on purpose: the
                                 shipped good draft-03 legitimately writes "Wednesday",
                                 a weekday absent from its brief, and flagging it would
                                 be a false positive on correct behavior.
                             The MASKED-NUMBER member (a value that is a digit substring
                             of a legitimate source number — the "50 inside 150" bug) is
                             the hard member that makes the rest of the rate meaningful.

A 100% catch rate across EVERY family is SUSPICIOUS, not reassuring: it means the
mutants are too easy and the next reviewer will walk through the boundary they never
probed. Same instinct as the repo's 30-40% baseline-calibration rule — an eval nothing
can fail is not an eval. When a family hits 100%, add a harder member.

Stdlib only. No model, no key, no network.
"""

from fixtures import run_draft_cases as rdc

MUTANT_FLOORS = {
    "no_fabrication": 0.80,
    "needs_marker": 1.00,
    "question_count": 1.00,
    "criteria_dimensions": 1.00,
}

DRAFT_MARKER = "## Draft"


def _body_insert(draft, sentence):
    """Insert a sentence into the DRAFT BODY (after the '## Draft' line).

    Injecting into the body, not the criteria, is what makes these mutants realistic:
    a fabricated fact arrives inside the prose the reader will believe.
    """
    lines = draft.splitlines()
    for i, line in enumerate(lines):
        if line.strip().lower().startswith(rdc.DRAFT_HEADING):
            lines.insert(i + 1, sentence)
            return "\n".join(lines) + "\n"
    return draft + "\n" + sentence + "\n"


def _masked_value(src_keys):
    """A number whose DIGITS hide inside a legitimate source number.

    "under 150 words" in the brief -> 50. This is the BLOCKER the reviewer found: a
    raw substring lookup clears it, because "50" really is inside "150". Derived from
    the case, never hardcoded.
    """
    for key in sorted(k for k in src_keys if isinstance(k, float)):
        digits = str(int(key)) if key == int(key) else str(key)
        for cut in range(1, len(digits)):
            tail = digits[cut:]
            if not tail or tail.startswith("."):
                continue
            try:
                value = float(tail)
            except ValueError:
                continue
            if value not in src_keys:
                return tail, value
    return None, None


def family_no_fabrication(case):
    """Invented specifics the brief and KB do not support, in many surface forms."""
    src = rdc.source_blob(case)
    keys = rdc.numeric_keys(src)
    out = []

    # Numeric surfaces. Each candidate is checked against the source value set first,
    # so a mutant can never accidentally inject a fact the brief actually supports.
    candidates = [
        ("bare-int", "Churn fell 77 points last quarter.", 77.0),
        ("decimal", "Churn fell 4.7 points last quarter.", 4.7),
        ("percent", "Churn fell 23% last quarter.", 23.0),
        ("currency", "The campaign cost $2M to run.", 2.0),
    ]
    for name, sentence, value in candidates:
        if value in keys:
            continue  # the brief supplies it — not a fabrication, so not a mutant
        out.append((f"fabrication/number-{name}", _body_insert(case["good_draft"], sentence)))

    surface, value = _masked_value(keys)
    if surface is not None:
        # HARD: the digits of this number live inside a legitimate source number.
        out.append((f"fabrication/number-masked-by-source-{surface}",
                    _body_insert(case["good_draft"],
                                 f"Churn fell {surface}% last quarter.")))

    # KNOWN MISS (declared in the module _doc): a spelled-out numeral.
    out.append(("fabrication/number-spelled-out-KNOWN-MISS",
                _body_insert(case["good_draft"],
                             "Churn fell fifty percent last quarter.")))

    # Invented entity names, in the forms they take in natural prose.
    names = [
        ("title-case-run", "The work runs on Northwind Retention."),
        ("corp-suffix", "The rollout was built by Acme, Inc. under contract."),
        ("possessive", "Northwind Retention's dashboard tracks the campaign."),
        ("designator", "This shipped under the Falcon program."),
        # KNOWN MISS: a lone capitalized word with no designator and no neighbour.
        ("bare-single-word-KNOWN-MISS", "Falcon covers the rest."),
    ]
    for name, sentence in names:
        if rdc._norm(sentence) in rdc._norm(rdc.source_blob(case)):
            continue
        out.append((f"fabrication/name-{name}", _body_insert(case["good_draft"], sentence)))
    return out


def family_needs_marker(case):
    """Strip the declared gaps. A silent gap is the failure; a visible one is correct."""
    if not case.get("requires_needs_marker"):
        return []
    good = case["good_draft"]
    stripped = rdc._NEEDS_SPAN.sub("something", good)
    return [
        ("needs/markers-removed", stripped),
        # the marker section deleted but inline gaps rewritten as confident prose
        ("needs/gaps-filled-confidently",
         "\n".join(ln for ln in stripped.splitlines()
                   if not ln.strip().lower().startswith("## [needs"))),
    ]


def family_question_count(case):
    """Blow the step-1 question budget, in formats a line counter could not see."""
    good = case["good_draft"]
    pre = rdc.pre_draft_section(good)
    rest = good[len(pre):]
    stall = ("I cannot start until I know these.")
    return [
        ("questions/four-on-separate-lines", "\n".join([
            "## Clarifying questions",
            "- Who is the reader?",
            "- What changed in the flow?",
            "- Is there a launch date?",
            "- What tone do you want?",
            stall]) + rest),
        # HARD: a line counter saw ONE line here and passed it.
        ("questions/four-on-one-line", "\n".join([
            "## Clarifying questions",
            "- Who is the reader? What changed? Is there a date? What tone?",
            stall]) + rest),
        ("questions/mixed-with-prose", "\n".join([
            "## Clarifying questions",
            "Before I start: who is the reader?",
            "And what changed, exactly? Is there a launch date I should name?",
            "Also, how long should this be? What tone?",
            stall]) + rest),
    ]


def family_criteria_dimensions(case):
    """Drop each acceptance-criteria dimension in turn — five mutants, one per dimension."""
    good = case["good_draft"]
    out = []
    for dim in rdc.CRITERIA_DIMENSIONS:
        kept = []
        for line in good.splitlines():
            m = rdc._BULLET_LABEL.match(line)
            if m and rdc._norm(m.group(1)).startswith(dim):
                continue  # this dimension is no longer named as a criterion
            kept.append(line)
        out.append((f"criteria/dropped-{dim.replace(' ', '-')}", "\n".join(kept)))
    # The whole criteria section replaced by a fixed generic rubric — SKILL.md step 1
    # calls this out by name ("a generic fixed rubric is a FAIL").
    out.append(("criteria/generic-rubric",
                "## Acceptance criteria\n"
                "(Standard rubric applied: is it clear, is it concise, is it correct.)\n"
                + good[len(rdc.pre_draft_section(good)):]))
    return out


FAMILIES = {
    "no_fabrication": family_no_fabrication,
    "needs_marker": family_needs_marker,
    "question_count": family_question_count,
    "criteria_dimensions": family_criteria_dimensions,
}


# --------------------------------------------------------------------------
# The APPEND-ONLY hard tail: evasions a reviewer constructed against a live checker,
# plus the false-positive controls. Never delete an entry.
# --------------------------------------------------------------------------

def hard_tail(case):
    """[(id, draft, check, must_catch)]."""
    good = case["good_draft"]
    items = []
    # The reviewer's artifacts are literal text written against ONE brief (they assert
    # "We shipped on 3 March", which only draft-01 supplies). Running them under another
    # case's brief would make that date a genuine fabrication and the "control" would
    # correctly flag it — a fixture bug, not a checker bug. So they are bound to the
    # brief they were constructed against.
    grounded = "3 march" in rdc.source_blob(case)
    if "no_fabrication" in case["checks"] and grounded:
        items += [
            # The BLOCKER: every one of these was masked by "150" in draft-01's brief.
            ("reviewer/masked-numbers",
             "## Draft\nChurn fell 50% in Q3, our 15th straight quarter of decline, "
             "costing 1 million.\nWe shipped on 3 March.\n", "no_fabrication", True),
            # FALSE-POSITIVE CONTROL: SKILL.md never mandates sentence-case headings.
            ("control/title-case-heading",
             "## Acceptance Criteria\n## Draft\nWe shipped on 3 March.\n",
             "no_fabrication", False),
            # FALSE-POSITIVE CONTROL: label lines are structure, not invented entities.
            ("control/label-lines",
             "## Draft\nSubject: win-back campaign is live\nRecommendation: ship it.\n"
             "(Standard rubric applied.)\n", "no_fabrication", False),
        ]
    if "no_fabrication" in case["checks"]:
        # Runs for EVERY case: the artifact the SKILL mandates must never be flagged.
        items.append(("control/good-draft-untouched", good, "no_fabrication", False))
    if "question_count" in case["checks"]:
        # FALSE-POSITIVE CONTROL: a rhetorical question in the DRAFT BODY is prose, not
        # a step-1 clarifying question. The budget applies to the pre-draft only.
        items.append(("control/questions-in-draft-body",
                      good + "\n## Draft\nWhy does this matter? Because churn is up. "
                             "Right? Right. And then? We ship.\n",
                      "question_count", False))
    return items


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------

def catch_rates(cases):
    """{check: (caught, total)} over the generated families. Pure, deterministic."""
    rates = {}
    for case in cases:
        for check, build in FAMILIES.items():
            if check not in case["checks"]:
                continue
            caught, total = rates.get(check, (0, 0))
            for _mid, draft in build(case):
                caught += bool(rdc.CHECKS[check](case, draft))  # violations == caught
                total += 1
            rates[check] = (caught, total)
    return rates


def run_mutant_families(cases):
    """Print per-check catch rates + the hard tail. Returns (passes, fails)."""
    passes = fails = 0
    print("-- mutant families (generated from each good_draft; catch rate vs declared floor) --")

    rates = catch_rates(cases)
    misses = []
    for case in cases:
        for check, build in FAMILIES.items():
            if check not in case["checks"]:
                continue
            for mid, draft in build(case):
                if not rdc.CHECKS[check](case, draft):
                    misses.append(f"{case['id']}/{mid}")

    for check in sorted(rates):
        caught, total = rates[check]
        rate = caught / total if total else 0.0
        floor = MUTANT_FLOORS[check]
        ok = rate >= floor
        passes += ok
        fails += not ok
        print(f"[{'PASS' if ok else 'FAIL'}] {check:20} catch rate {caught}/{total} = {rate:.0%}"
              f"  (floor {floor:.0%})"
              + ("" if ok else "  <-- BELOW FLOOR: the checker is memorizing exemplars"))
    if misses:
        print("    known misses (declared, not hidden): " + ", ".join(misses))
    if all(rates[c][0] == rates[c][1] for c in rates):
        print("    NOTE: 100% across every family is SUSPICIOUS, not reassuring — the mutants "
              "are too easy. Add a harder member before trusting this number.")

    print("\n-- hard tail (append-only reviewer evasions + false-positive controls) --")
    for case in cases:
        for hid, draft, check, must_catch in hard_tail(case):
            violations = rdc.CHECKS[check](case, draft)
            caught = bool(violations)
            hit = caught if must_catch else not caught
            passes += hit
            fails += not hit
            verdict = ("CAUGHT: " + "; ".join(violations) if caught else "ESCAPED") \
                if must_catch else \
                ("clean (correct behavior, not flagged)" if not caught
                 else f"FALSE POSITIVE — {violations}")
            print(f"[{'PASS' if hit else 'FAIL'}] [{case['id']}] {hid:34} {check}: {verdict}")
    print()
    return passes, fails
