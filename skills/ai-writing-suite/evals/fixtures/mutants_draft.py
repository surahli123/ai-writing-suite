#!/usr/bin/env python3
"""White-box mutant FAMILIES for the comms-draft checkers (cheap smoke).

WHY THIS EXISTS (the root cause it removes)

Each failure mode used to have exactly ONE positive exemplar (the case's bad_draft)
and ONE negative (its good_draft), both authored in the same pass as the checker.
With N=1 per class the separating boundary is underdetermined, so an author
optimizing for "the planted positive trips" converges on the cheapest discriminator
that separates that one pair — a raw substring lookup for numbers, a line count for
questions, a bag-of-words test for criteria. Every finding in review was an instance
of that shape. A FAMILY drawn from a generator removes the class, because a checker
that memorized one exemplar fails on the next draw.

These families are WHITE-BOX: they may reuse the checker's own parsing helpers, and
so they can only probe the checker's stated design, not its blind spots. That is why
they are demoted to "cheap smoke" here — the adversarial claim lives in the BLACK-BOX
holdout (fixtures/holdout_adversary.py), which shares nothing with the checker.

FIX-3 SEMANTICS (per the 2026-07-13 audit):
  * Every member is tagged `must_catch` or `expected_escape`.
  * must_catch families have a 100% floor — ONE escape fails the run. There is no
    "floor set just under the observed rate" any more; a tolerated gap is where real
    uncovered behavior hid.
  * expected_escape members are documented known gaps. They are reported separately
    and are NOT in the catch-rate denominator, so the must_catch rate is not diluted
    by deliberately-uncatchable probes.
  * Unique mutation TEMPLATES are reported separately from per-case instantiations
    (the same template applied to three briefs is three instantiations of one idea).

KNOWN GAPS (expected_escape, declared not hidden):
  * number-spelled-out — a written-out numeral ("fifty percent") is not tokenized;
    catching it needs a number-word lexicon that false-positives ordinary prose
    ("three Friday deploys", which the good drafts use and the brief supplies).
  * name-bare-single-word — a lone capitalized word ("Falcon") with no designator is
    not a candidate; the good draft-03 legitimately writes "Wednesday", absent from
    its brief, and flagging lone caps would false-positive correct behavior.

DETERMINISM: families are ENUMERATED, not sampled. No RNG, no seed, no clock — the
same mutants in the same order on every run, so CI is byte-reproducible.

Stdlib only. No model, no key, no network.
"""

from fixtures import run_draft_cases as rdc

MUST_CATCH_FLOOR = 1.0

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

    "under 150 words" in the brief -> 50. This is the BLOCKER an earlier review found:
    a raw substring lookup clears it, because "50" really is inside "150". Derived
    from the case, never hardcoded.
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


# Each family returns [(template, artifact, klass)] with klass in {"must", "escape"}.

def family_no_fabrication(case):
    keys = rdc.numeric_keys(rdc.source_blob(case))
    out = []

    # Numeric surfaces. Each candidate is checked against the source value set first,
    # so a mutant can never accidentally inject a fact the brief actually supports.
    candidates = [
        ("number-bare-int", "Churn fell 77 points last quarter.", 77.0),
        ("number-decimal", "Churn fell 4.7 points last quarter.", 4.7),
        ("number-percent", "Churn fell 23% last quarter.", 23.0),
        ("number-currency", "The campaign cost $2M to run.", 2.0),
    ]
    for name, sentence, value in candidates:
        if value in keys:
            continue  # the brief supplies it — not a fabrication, so not a mutant
        out.append((name, _body_insert(case["good_draft"], sentence), "must"))

    surface, _value = _masked_value(keys)
    if surface is not None:
        out.append(("number-masked-by-source",
                    _body_insert(case["good_draft"], f"Churn fell {surface}% last quarter."),
                    "must"))

    names = [
        ("name-title-case-run", "The work runs on Northwind Retention."),
        ("name-corp-suffix", "The rollout was built by Acme, Inc. under contract."),
        ("name-possessive", "Northwind Retention's dashboard tracks the campaign."),
        ("name-designator", "This shipped under the Falcon program."),
    ]
    for name, sentence in names:
        if rdc._norm(sentence) in rdc.source_blob(case):
            continue
        out.append((name, _body_insert(case["good_draft"], sentence), "must"))

    # Declared known gaps (expected_escape): see module _doc.
    out.append(("number-spelled-out",
                _body_insert(case["good_draft"], "Churn fell fifty percent last quarter."),
                "escape"))
    out.append(("name-bare-single-word",
                _body_insert(case["good_draft"], "Falcon covers the rest."),
                "escape"))
    return out


def family_needs_marker(case):
    if not case.get("requires_needs_marker"):
        return []
    stripped = rdc._NEEDS_SPAN.sub("something", case["good_draft"])
    return [
        ("markers-removed", stripped, "must"),
        ("gaps-filled-confidently",
         "\n".join(ln for ln in stripped.splitlines()
                   if not ln.strip().lower().startswith("## [needs")), "must"),
    ]


def family_question_count(case):
    good = case["good_draft"]
    rest = good[len(rdc.pre_draft_section(good)):]
    stall = "I cannot start until I know these."
    return [
        ("four-on-separate-lines", "\n".join([
            "## Clarifying questions",
            "- Who is the reader?",
            "- What changed in the flow?",
            "- Is there a launch date?",
            "- What tone do you want?",
            stall]) + rest, "must"),
        # HARD: a line counter saw ONE line here and passed it.
        ("four-on-one-line", "\n".join([
            "## Clarifying questions",
            "- Who is the reader? What changed? Is there a date? What tone?",
            stall]) + rest, "must"),
        ("mixed-with-prose", "\n".join([
            "## Clarifying questions",
            "Before I start: who is the reader?",
            "And what changed, exactly? Is there a launch date I should name?",
            "Also, how long should this be? What tone?",
            stall]) + rest, "must"),
    ]


def family_criteria_dimensions(case):
    good = case["good_draft"]
    out = []
    for dim in rdc.CRITERIA_DIMENSIONS:
        kept = [line for line in good.splitlines()
                if not (rdc._BULLET_LABEL.match(line)
                        and rdc._norm(rdc._BULLET_LABEL.match(line).group(1)).startswith(dim))]
        out.append((f"dropped-{dim.replace(' ', '-')}", "\n".join(kept), "must"))
    out.append(("generic-rubric",
                "## Acceptance criteria\n"
                "(Standard rubric applied: is it clear, is it concise, is it correct.)\n"
                + good[len(rdc.pre_draft_section(good)):], "must"))
    return out


FAMILIES = {
    "no_fabrication": family_no_fabrication,
    "needs_marker": family_needs_marker,
    "question_count": family_question_count,
    "criteria_dimensions": family_criteria_dimensions,
}


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------

def _caught(check, case, draft):
    return bool(rdc.CHECKS[check](case, draft))


def catch_rates(cases):
    """{check: (caught, total)} over must_catch instantiations only. Deterministic.

    expected_escape members are excluded from the denominator on purpose (FIX 3): a
    tolerated gap must not dilute the must_catch rate.
    """
    rates = {}
    for case in cases:
        for check, build in FAMILIES.items():
            if check not in case["checks"]:
                continue
            caught, total = rates.get(check, (0, 0))
            for _tmpl, draft, klass in build(case):
                if klass != "must":
                    continue
                caught += _caught(check, case, draft)
                total += 1
            rates[check] = (caught, total)
    return rates


def template_counts(cases):
    """{check: (unique_must_templates, must_instantiations)} — FIX 3 reporting."""
    counts = {}
    for case in cases:
        for check, build in FAMILIES.items():
            if check not in case["checks"]:
                continue
            tmpls, insts = counts.get(check, (set(), 0))
            for tmpl, _draft, klass in build(case):
                if klass != "must":
                    continue
                tmpls = tmpls | {tmpl}
                insts += 1
            counts[check] = (tmpls, insts)
    return {k: (len(t), n) for k, (t, n) in counts.items()}


def expected_escapes(cases):
    """[(check, case_id, template)] for every declared known gap — honesty ledger."""
    out = []
    for case in cases:
        for check, build in FAMILIES.items():
            if check not in case["checks"]:
                continue
            for tmpl, _draft, klass in build(case):
                if klass == "escape":
                    out.append((check, case["id"], tmpl))
    return out


def run_mutant_families(cases):
    """Print must_catch rates (100% floor) + declared gaps. Returns (passes, fails)."""
    passes = fails = 0
    print("-- white-box mutant families (cheap smoke; must_catch floor 100%) --")

    rates = catch_rates(cases)
    tmpl = template_counts(cases)
    for check in sorted(rates):
        caught, total = rates[check]
        rate = caught / total if total else 0.0
        ok = rate >= MUST_CATCH_FLOOR
        passes += ok
        fails += not ok
        uniq, insts = tmpl[check]
        print(f"[{'PASS' if ok else 'FAIL'}] {check:20} must_catch {caught}/{total} = {rate:.0%}"
              f"  ({uniq} templates x cases = {insts} instantiations; floor 100%)"
              + ("" if ok else "  <-- ESCAPE: a must_catch mutant slipped the checker"))

    escapes = expected_escapes(cases)
    if escapes:
        print(f"    expected_escape (declared gaps, NOT in denominator): "
              + ", ".join(f"{c}:{cid}/{t}" for c, cid, t in escapes))
    print()
    return passes, fails
