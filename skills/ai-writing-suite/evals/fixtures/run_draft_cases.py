#!/usr/bin/env python3
"""Run the comms-draft behavioral cases (artifact discrimination).

Run from `evals/`:
    python3 -m fixtures.run_draft_cases            # deterministic (gates CI)
    python3 -m fixtures.run_draft_cases --judge    # + advisory LLM judge

WHY this suite exists and why it is shaped like this. comms-draft is SKILL PROSE:
its "code" is an agent's behavior, so nothing here can invoke it without a model.
The lazy eval — assert the fixture file parses — can never go red and is worse
than nothing. So each case ships a brief plus TWO PRE-AUTHORED artifacts, a
`good_draft` (what comms-draft/SKILL.md mandates) and a `bad_draft` (the named
failure mode), and this runner's job is to TELL THEM APART deterministically.

The gate is a per-case planted positive, in both directions:
  * good_draft must PASS every check the case declares, and
  * bad_draft must FAIL the check named in its `failure_mode`.
A bad draft that does not trip its own check FAILS the run — a checker that
cannot catch its own planted failure is broken, and a green run from it proves
nothing (the same reasoning as the `control` role in run_false_positives.py).

Stdlib only. No model, no key on the deterministic path — safe for CI.
"""

import argparse
import json
import os
import re
import sys

# Allow running both as a module (-m fixtures.run_draft_cases) and as a script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Confusion-matrix helpers are REUSED, never re-implemented: the judge lane here
# has the same shape as the fixtures one (a positive cohort of artifacts the judge
# must reject, a negative cohort it must spare), so it must be scored on the same
# combined-cohort matrix that exposes a constant classifier.
from fixtures.run_fixtures import (  # noqa: E402
    new_confusion, record_verdict, confusion_metrics, print_confusion,
)

HERE = os.path.dirname(os.path.abspath(__file__))
DRAFT_CASES_PATH = os.path.join(HERE, "draft_cases.json")

# Everything before this line is the PRE-DRAFT section (step-1 questions +
# acceptance criteria); everything after is the draft body. See draft_cases.json::_doc.
DRAFT_HEADING = "## draft"

# The five acceptance-criteria dimensions comms-draft/SKILL.md step 1 requires,
# named BEFORE a word is written. Naming two of them, or falling back to a fixed
# generic rubric, is the failure this checks.
CRITERIA_DIMENSIONS = ("style", "format", "length", "content integration", "depth")

MAX_QUESTIONS = 3  # SKILL.md step 1: "at most 2-3" — a 4th is a stall.

# A [NEEDS: ...] marker DESCRIBES a missing fact; it does not assert one. So the
# marker spans are stripped before fabrication extraction — "[NEEDS: Q3 churn
# number]" must not be read as the draft claiming a Q3 churn number.
_NEEDS_SPAN = re.compile(r"\[NEEDS:[^\]]*\]", re.IGNORECASE)
_NEEDS_MARKER = re.compile(r"\[NEEDS:", re.IGNORECASE)

# Candidate specific #1: any digit-bearing token (numbers, percentages, years,
# "3 March"'s 3). The SOURCES are tokenized with the SAME regex and compared by SET
# MEMBERSHIP on a normalized value — never by substring. Substring lookup was a
# false-negative machine: a brief saying "under 150 words" made the invented "50",
# "15", "1" and "0" all "present in the source" because their digits live inside
# "150".
_NUMERIC = re.compile(r"\d[\d,\.:/]*%?")

# Candidate specific #2: a run of 2+ capitalized words — the shape an invented
# product/company/person name takes ("Northwind Retention"). Single capitalized
# words are NOT candidates: sentence starts and ordinary given names would drown
# the signal in false positives, and the shipped good_drafts prove it (draft-03
# legitimately writes "Wednesday", a weekday that appears nowhere in its brief).
# The gap is [ \t]+, never \s+: a name does not span a line break, and a greedy
# \s+ stitched a heading to the next line's first word ("## Draft" + "Subject:"
# -> a phantom "Draft Subject").
_CAP_RUN = re.compile(r"\b[A-Z][\w'’\-]*(?:[ \t]+[A-Z][\w'’\-]*)+")

# Candidate #2b: a company name in its natural punctuated form ("Acme, Inc."). The
# comma-join is restricted to a closed set of corporate suffixes on purpose — a
# general comma-join would stitch unrelated names into a phantom entity
# ("Priya, Dana" -> a company that does not exist).
_CORP_RUN = re.compile(
    r"\b[A-Z][\w'’\-]*,[ \t]+(?:Inc|Inc\.|LLC|Ltd|Ltd\.|Corp|Corp\.|Co\.|GmbH|PLC)\b")

# Candidate #2c: a capitalized word bound to a lowercase designator noun — the other
# natural form of an invented product/program name ("the Falcon program"). The
# designator is what makes a lone capitalized word safe to flag here.
_DESIGNATOR_RUN = re.compile(
    r"\b[A-Z][\w'’\-]+[ \t]+(?:program|project|initiative|campaign|platform|product"
    r"|release|migration|rollout|programme)\b")

# Markdown heading lines are stripped before the proper-noun scan: "## Acceptance
# Criteria" is a heading, not an invented entity. Sentence-case headings in the
# fixtures used to hide this — the eval passed by the fixtures' convenience, which
# is exactly the rigging pattern this suite exists to prevent.
_HEADING_LINE = re.compile(r"^[ \t]*#{1,6}[ \t]+.*$", re.M)

# Stripped from the FRONT of a capitalized run before the 2+-word test, so a
# sentence-initial function word ("The Acme dashboard") does not manufacture a
# two-word "proper noun" out of one ordinary name. Function words ONLY: the three
# content words that used to sit here ("subject", "recommendation", "standard")
# existed solely to stop the fixtures' own label lines from false-positiving. They
# are gone; label lines are handled structurally instead (a line-initial label word
# is terminated by ':', and a capitalized run never crosses ':', so "Subject: ..."
# cannot start a run — see test_subject_label_line_is_not_flagged).
_RUN_LEAD_STOPWORDS = {
    "a", "an", "the", "and", "but", "so", "or", "if", "in", "on", "at", "for",
    "we", "i", "it", "you", "they", "this", "that", "these", "those", "our",
    "my", "their", "his", "her", "no", "not", "nothing", "when", "where",
    "while", "after", "before", "once", "here", "there", "then", "now",
}

# The acceptance-criteria section of the pre-draft. The five dimensions must be
# NAMED AS CRITERIA (bullet labels under a criteria heading), not merely present as
# vocabulary somewhere in the prose — a draft whose prose happens to use the word
# "depth" has not named depth as a criterion.
_CRITERIA_HEADING = re.compile(r"^[ \t]*#{1,6}[ \t]*(.*criteria.*)$", re.I)
_BULLET_LABEL = re.compile(r"^[ \t]*[-*][ \t]+\**([^:*]+?)\**[ \t]*:")

_WS = re.compile(r"\s+")


def _norm(text):
    """Whitespace-collapse + lowercase, for tolerant source lookups."""
    return _WS.sub(" ", text or "").strip().lower()


def load_draft_cases(path=None):
    with open(path or DRAFT_CASES_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def source_blob(case):
    """The ONLY legitimate sources of fact: the brief + the KB passages.

    SKILL.md, Boundary: "The new facts in a draft come only from the brief and the
    KB. Nothing else is a source."
    """
    return _norm(case.get("brief", "") + " " + " ".join(case.get("kb_facts") or []))


def pre_draft_section(draft):
    """The part of the artifact BEFORE the draft body (step-1 questions + criteria)."""
    lines = draft.splitlines()
    for i, line in enumerate(lines):
        if line.strip().lower().startswith(DRAFT_HEADING):
            return "\n".join(lines[:i])
    return draft  # no draft body at all (a stall) — the whole artifact is pre-draft


def _num_key(tok):
    """Normalize one numeric token to the VALUE it asserts.

    The equivalence policy, decided and stated rather than left to accident:

    * surface forms of the same value collapse — "14", "14%" and the "14" inside
      "14 percent" all key to 14.0, so a figure the brief states as "14 percent"
      is NOT flagged when the draft writes "14%" (same value, different surface);
    * separators are stripped: "1,000" -> 1000.0, "23%." -> 23.0;
    * currency is value-only: "$1M" / "1 million" tokenize to the numeral 1, so the
      MAGNITUDE WORD is not checked. Documented under-flagging, not a silent one;
    * dates are value-only too: "3 March" keys to 3.0, so it matches any source
      occurrence of the value 3. Deliberate: this is a shape checker, not a
      date parser, and the conservative direction is to under-flag;
    * anything that does not parse as a number (a ratio "3/4", a time "10:30")
      keys to its lowercased string and must match exactly.
    """
    t = tok.rstrip(".,:/").rstrip("%").replace(",", "")
    try:
        return float(t)
    except ValueError:
        return t.lower()


def numeric_keys(text):
    """The SET of bare numeric values asserted in `text` (see _num_key).

    Set membership, never substring: "150" in the brief must not mask an invented
    "50", "15", "1" or "0" in the draft. This is the VALUE-ONLY view, kept for the
    masked-number derivation in the mutant smoke suite; the fabrication check itself
    uses the TYPED view below, which also carries each value's unit/kind.
    """
    return {_num_key(m.group(0)) for m in _NUMERIC.finditer(text or "")
            if _num_key(m.group(0)) != ""}


# Context that changes what a number MEANS. Two invented specifics escaped the
# value-only check by borrowing a supported value: "$3 million" reused the "3" that
# "3 March" grounds, and "3 November" reused the supported DAY while changing the
# month. So a claim now carries its TYPE, and grounding requires value AND type.
_MONTHS = {
    "jan": "january", "january": "january", "feb": "february", "february": "february",
    "mar": "march", "march": "march", "apr": "april", "april": "april", "may": "may",
    "jun": "june", "june": "june", "jul": "july", "july": "july",
    "aug": "august", "august": "august", "sep": "september", "sept": "september",
    "september": "september", "oct": "october", "october": "october",
    "nov": "november", "november": "november", "dec": "december", "december": "december",
}
_MAGNITUDES = {"thousand", "million", "billion", "trillion", "k", "m", "mn", "bn", "b"}
_CURRENCY_CHARS = "$£€"
_CURRENCY_WORDS = {"usd", "eur", "gbp", "dollar", "dollars", "pound", "pounds",
                   "euro", "euros"}
_LETTERS = re.compile(r"[A-Za-z]+")


def _typed_claim_for_match(text, m):
    """The TYPED key for one numeric match: value bound to its unit/kind.

    Kinds, chosen by the context immediately around the digits:
      * ("date", day, month)  — a month name sits next to the number ("3 March"),
      * ("qty", value, unit)  — a currency symbol/word precedes it or a magnitude
                                word follows it ("$3", "3 million"),
      * ("pct", value)        — a "%" is attached or "percent"/"percentage" follows,
      * ("num", value)        — a plain number, matched only by a plain number.
    A date grounds only a date, a magnitude amount only the same amount+unit, so a
    supported "3 March" no longer launders an invented "$3 million" or "3 November".
    """
    val = _num_key(m.group(0))
    before = text[:m.start()]
    after = text[m.end():]
    prev_words = _LETTERS.findall(before)
    prev_word = prev_words[-1].lower() if prev_words else ""
    nxt = _LETTERS.search(after)
    next_word = nxt.group(0).lower() if nxt and after[:nxt.start()].strip(" ,.:;)-–—\"'") == "" else ""
    month = _MONTHS.get(next_word) or _MONTHS.get(prev_word)
    stripped_before = before.rstrip()
    has_currency = (bool(stripped_before) and stripped_before[-1] in _CURRENCY_CHARS) \
        or prev_word in _CURRENCY_WORDS
    surface = m.group(0)
    is_percent = surface.endswith("%") or next_word in ("percent", "percentage")
    if month is not None:
        return ("date", val, month)
    if next_word in _MAGNITUDES or has_currency:
        return ("qty", val, next_word if next_word in _MAGNITUDES else "$")
    if is_percent:
        return ("pct", val)
    return ("num", val)


def typed_numeric_claims(text):
    """The SET of TYPED numeric claims in `text` (see _typed_claim_for_match)."""
    return {_typed_claim_for_match(text, m) for m in _NUMERIC.finditer(text or "")}


def _name_candidates(body):
    """Proper-noun-shaped candidates: multi-word runs, "Acme, Inc.", "X program"."""
    # Headings are structure, not entities: "## Acceptance Criteria" is a heading.
    scan = _HEADING_LINE.sub(" ", body)
    out = []
    for m in _CAP_RUN.finditer(scan):
        words = m.group(0).split()
        while words and words[0].lower() in _RUN_LEAD_STOPWORDS:
            words.pop(0)
        if len(words) < 2:
            continue  # one name after the stopword strip — not a candidate
        out.append(" ".join(words))
    for rx in (_CORP_RUN, _DESIGNATOR_RUN):
        for m in rx.finditer(scan):
            phrase = m.group(0)
            # "The campaign shipped" is a sentence start, not a program name — the
            # designator only makes a capitalized word a candidate when that word is
            # a NAME, not a function word.
            if phrase.split()[0].lower() in _RUN_LEAD_STOPWORDS:
                continue
            out.append(phrase)
    return out


def find_fabrications(draft, sources):
    """Return the specifics in `draft` that trace back to NEITHER the brief nor the KB.

    Pure fn (no I/O, no env) so tests can call it on hand-built inputs. `sources` is
    the raw brief+KB text; it is tokenized here with the SAME rules as the draft.

    Two candidate classes, chosen because they are the two shapes an invented fact
    takes in practice: a NUMBER presented as measurement ("churn fell 23%") and a
    CAPITALIZED NAME presented as a real entity ("Northwind Retention", "Acme, Inc.",
    "the Falcon program"). A number is a violation iff its TYPED claim (value + kind:
    date / magnitude / percent / plain) is absent from the sources; a name is a
    violation iff its phrase appears nowhere in the source text.

    Known limits, stated rather than hidden: a lone capitalized word bound to no
    designator is not a candidate (sentence starts and ordinary names would drown
    the signal — draft-03's good_draft legitimately writes "Wednesday", absent from
    its brief), and a spelled-out numeral ("fifty percent") is not tokenized. This is
    a checker for the fabrication SHAPE, not a semantic fact-checker.
    """
    src_text = _norm(sources)
    src_claims = typed_numeric_claims(src_text)
    body = _NEEDS_SPAN.sub(" ", draft or "")  # a declared gap is not a claimed fact
    found = []

    for m in _NUMERIC.finditer(body):
        tok = m.group(0).rstrip(".,:/")
        if not tok:
            continue
        if _typed_claim_for_match(body, m) in src_claims:
            continue
        found.append(tok)

    for phrase in _name_candidates(body):
        if _norm(phrase) in src_text:
            continue
        found.append(phrase)

    # De-dupe, preserve order of first appearance.
    seen, out = set(), []
    for f in found:
        if f.lower() not in seen:
            seen.add(f.lower())
            out.append(f)
    return out


def count_questions(draft):
    """Clarifying questions asked before drafting: '?' MARKS in the pre-draft section.

    Marks, not lines: two questions on one line are two questions, and a line
    counter let a stall hide behind formatting. Questions after the `## Draft`
    marker are draft body (a rhetorical question in the prose), not step-1
    clarifying questions, so pre_draft_section() bounds the count.
    """
    return pre_draft_section(draft).count("?")


def criteria_labels(draft):
    """The bullet LABELS declared under the pre-draft's acceptance-criteria heading.

    Scoped to the criteria section(s) on purpose: the old check was a substring test
    over the whole pre-draft, so prose that merely used the word "depth" satisfied
    the "depth" dimension. A criterion is something you NAME as a criterion.
    """
    pre = pre_draft_section(draft)
    labels, in_criteria = [], False
    for line in pre.splitlines():
        if re.match(r"^[ \t]*#{1,6}[ \t]+", line):
            in_criteria = bool(_CRITERIA_HEADING.match(line))
            continue
        if not in_criteria:
            continue
        m = _BULLET_LABEL.match(line)
        if m:
            labels.append(_norm(m.group(1)))
    return labels


def missing_criteria_dimensions(draft):
    """Which of the five step-1 dimensions are NOT named as criteria before the draft."""
    labels = criteria_labels(draft)
    return [d for d in CRITERIA_DIMENSIONS
            if not any(lab == d or lab.startswith(d) for lab in labels)]


# --- the check registry -------------------------------------------------------
# Each check(case, draft) -> list of violation strings ([] == PASS). A case's
# `checks` list names which run; its `failure_mode` names the one its bad_draft
# MUST trip.

def _check_no_fabrication(case, draft):
    bad = find_fabrications(draft, source_blob(case))
    return [f"invented specific not in brief/KB: {b!r}" for b in bad]


def _check_needs_marker(case, draft):
    if not case.get("requires_needs_marker"):
        return []
    if _NEEDS_MARKER.search(draft or ""):
        return []
    return ["brief has a gap the draft cannot fill, but no [NEEDS: ...] marker "
            "is present (a visible gap is correct; a silent one is not)"]


def _check_question_count(case, draft):
    n = count_questions(draft)
    if n <= MAX_QUESTIONS:
        return []
    return [f"asked {n} clarifying questions before drafting (max {MAX_QUESTIONS}) "
            f"— SKILL step 1 says propose inferred criteria and proceed instead"]


def _check_criteria_dimensions(case, draft):
    missing = missing_criteria_dimensions(draft)
    if not missing:
        return []
    return [f"acceptance criteria omit {len(missing)} of five dimensions: "
            f"{', '.join(missing)}"]


CHECKS = {
    "no_fabrication": _check_no_fabrication,
    "needs_marker": _check_needs_marker,
    "question_count": _check_question_count,
    "criteria_dimensions": _check_criteria_dimensions,
}


def run_case_checks(case, draft):
    """Run every check the case declares. Returns {check_name: [violations]}."""
    return {name: CHECKS[name](case, draft) for name in case.get("checks", [])}


def run_deterministic(data):
    """Discriminate good vs bad artifacts per case. Returns (passes, fails).

    Two assertions per case, and BOTH gate the run:
      1. good_draft passes every declared check   (no false alarm on correct behavior)
      2. bad_draft trips its declared failure_mode (the planted positive lands)
    """
    cases = data.get("cases", [])
    passes = fails = 0

    print("=== comms-draft behavioral cases (artifact discrimination) ===\n")

    # Self-guard against a gutted dataset, same stance as the false-positive suite:
    # zero cases, or a case with only one side of the pair, means the discrimination
    # claim is vacuous. Hard failure, never a green run.
    if not cases:
        print("ERROR: no cases in draft_cases.json — the discrimination suite is vacuous.")
        return 0, 1
    malformed = [c.get("id", "?") for c in cases
                 if not c.get("good_draft") or not c.get("bad_draft")
                 or not c.get("checks") or not c.get("failure_mode")]
    if malformed:
        print("ERROR: case(s) missing a good/bad artifact, checks, or failure_mode: "
              f"{', '.join(malformed)} — nothing to discriminate.")
        return 0, 1

    for case in cases:
        cid = case["id"]
        fm = case["failure_mode"]
        print(f"-- {cid}  (failure mode: {fm})")

        good = run_case_checks(case, case["good_draft"])
        good_viol = {k: v for k, v in good.items() if v}
        if good_viol:
            fails += 1
            print(f"  [FAIL] good_draft violates {', '.join(good_viol)} "
                  f"— the artifact the SKILL mandates must pass every check")
            for k, vs in good_viol.items():
                for v in vs:
                    print(f"         {k}: {v}")
        else:
            passes += 1
            print(f"  [PASS] good_draft clean on {', '.join(case['checks'])}")

        bad = run_case_checks(case, case["bad_draft"])
        driver = bad.get(fm, [])
        if driver:
            passes += 1
            other = [k for k, v in bad.items() if v and k != fm]
            print(f"  [PASS] bad_draft TRIPS {fm} (planted positive caught)"
                  + (f"; also trips {', '.join(other)}" if other else ""))
            for v in driver:
                print(f"         {fm}: {v}")
        else:
            fails += 1
            print(f"  [FAIL] bad_draft did NOT trip its declared failure mode {fm!r} "
                  f"— the checker cannot catch its own planted failure, so a green "
                  f"run here proves nothing")
        print()

    print(f"Discrimination: {len(cases)} case(s), each asserting "
          f"good-passes AND bad-trips-{'/'.join(sorted({c['failure_mode'] for c in cases}))}.\n")

    # One planted positive per mode is a boundary of one point: a checker can pass it by
    # memorizing the exemplar it was written against (which is exactly how the substring
    # and line-count bugs survived). Two layers widen that boundary:
    #   1. white-box mutant families (cheap smoke, must_catch floor 100%), and
    #   2. a BLACK-BOX holdout adversary that shares nothing with the checker — the
    #      real adversarial claim, seeded with the evasions past reviews found.
    from fixtures.mutants_draft import run_mutant_families  # lazy: keeps the import cheap
    from fixtures.holdout_adversary import run_draft_holdout
    m_pass, m_fail = run_mutant_families(cases)
    h_pass, h_fail = run_draft_holdout(cases)
    return passes + m_pass + h_pass, fails + m_fail + h_fail


# --- advisory judge lane ------------------------------------------------------

JUDGE_TEMPLATE = """You are grading a draft produced by the `comms-draft` skill against that
skill's own contract. Score each dimension PASS or FAIL.

THE ONLY LEGITIMATE SOURCES OF FACT (nothing else is a source):

BRIEF:
{brief}

KNOWLEDGE-BASE FACTS:
{kb_facts}

THE SUBMITTED DRAFT ARTIFACT:
{draft}

Dimensions:
- no_fabrication: PASS iff every number, date, name, and claim in the draft traces
  back to the BRIEF or the KB. A gap marked `[NEEDS: ...]` is CORRECT, not a
  fabrication. An invented specific presented as fact is the worst failure this
  skill can make. THIS IS THE HIGHEST-STAKES DIMENSION.
- needs_marked: PASS iff every fact the draft needs but does not have is marked in
  line with `[NEEDS: ...]` and collected in a list. N/A if the brief and KB supply
  everything.
- criteria_named: PASS iff the artifact names the five acceptance-criteria
  dimensions (style, format, length, content integration, depth) BEFORE the draft.
  A generic fixed rubric is a FAIL.
- question_discipline: PASS iff the artifact asks at most 3 clarifying questions and
  then proposes inferred criteria and proceeds. Stalling on a 4th question is a FAIL.

Output ONE line per dimension, exactly:
<dimension>: PASS|FAIL|N/A — <one-line reason> | EVIDENCE: "<verbatim quote from the brief or the draft>"
Keep each verdict and its EVIDENCE quote on ONE line.
"""

# Every dimension the judge must return for a verdict to count. no_fabrication is
# already ALWAYS-required inside judge.aggregate(); listing it is harmless.
JUDGE_FOCUS = ["no_fabrication", "needs_marked", "criteria_named",
               "question_discipline"]


def build_draft_judge_prompt(case, draft):
    """Fill the judge template for one submitted artifact. Pure (no I/O, no env)."""
    return (JUDGE_TEMPLATE
            .replace("{brief}", case.get("brief", ""))
            .replace("{kb_facts}", "\n".join(f"- {f}" for f in case.get("kb_facts") or []))
            .replace("{draft}", draft))


def run_judge(data, matrix=None):
    """Advisory judge lane over BOTH cohorts. NEVER gates CI (except live_error).

    Cohorts, mapped onto the shared confusion matrix (positive == judge says FAIL,
    identical to the fixtures suite): every bad_draft is gold=FAIL (the positives —
    sensitivity), every good_draft is gold=PASS (the negatives — specificity). Both
    are needed: a constant always-FAIL judge would ace the positives alone, and only
    the combined matrix drops it to 0.50 balanced accuracy.

    Offline (no AIWS_JUDGE_* + AIWS_JUDGE_RUN=1) -> every artifact SKIPs, no network
    call is made, and the process still exits 0. We never fabricate a verdict.
    Returns (scored, skipped, live_error).
    """
    from fixtures import judge  # lazy: the deterministic path stays network-free

    configured = judge.is_configured()
    print("\n=== comms-draft judge lane (advisory) ===")
    if not configured:
        print("No judge configured (set AIWS_JUDGE_URL/MODEL/KEY + AIWS_JUDGE_RUN=1) "
              "— every artifact SKIPPED, no network call.\n")
    else:
        print("Judge configured — a correct judge PASSes each good_draft and "
              "FAILs each bad_draft.\n")

    scored = skipped = 0
    for case in data.get("cases", []):
        for role, gold in (("good_draft", "PASS"), ("bad_draft", "FAIL")):
            label = f"{case['id']}/{role}"
            prompt = build_draft_judge_prompt(case, case[role])

            if not configured:
                skipped += 1
                record_verdict(matrix, gold, None)
                head = "\n".join(prompt.splitlines()[:1])
                print(f"[SKIP] {label:38} (gold={gold})  prompt[0]: {head[:52]}...")
                continue

            result = judge.evaluate(judge.JudgeRequest(
                prompt=prompt, before=case.get("brief", ""), after=case[role],
                rubric_focus=JUDGE_FOCUS))  # raises JudgeError on transport (loud)
            parsed, verdict = result.parsed, result.verdict
            if parsed:
                for dim, status in result.verified.items():
                    if status == "not_verbatim":
                        print(f'  [warn] {label}/{dim}: EVIDENCE not verbatim in '
                              f'brief/draft — "{parsed[dim]["evidence"]}"')
            record_verdict(matrix, gold, verdict)
            if verdict is None:
                skipped += 1
                print(f"[SKIP] {label} — no parseable verdict returned")
                continue
            scored += 1
            agree = "agrees" if verdict == gold else "DISAGREES"
            print(f"[{verdict}] {label:38} (gold={gold}) — judge {agree}")

    if not configured:
        print(f"\nJudge lane: 0 scored, all {skipped} SKIPPED (offline path, exit 0).")
        return 0, skipped, False

    print(f"\nJudge lane: {scored} scored, {skipped} skipped — advisory, does not "
          f"gate the run.")
    live_error = scored == 0
    if live_error:
        print("ERROR: judge configured but scored 0 artifacts — provider response "
              "envelope likely changed (check AIWS_JUDGE_URL/MODEL).")
    return scored, skipped, live_error


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(
        description="Run the comms-draft behavioral (artifact-discrimination) cases.")
    ap.add_argument("--judge", action="store_true",
                    help="also run the advisory LLM-judge lane (SKIPPED unless "
                         "AIWS_JUDGE_* is configured and AIWS_JUDGE_RUN=1)")
    args = ap.parse_args(argv)

    data = load_draft_cases()
    passes, fails = run_deterministic(data)

    judge_live_error = False
    if args.judge:
        matrix = new_confusion()
        _scored, _skipped, judge_live_error = run_judge(data, matrix)
        if _scored:
            print_confusion(matrix)  # advisory: never touches the exit code
        else:
            m = confusion_metrics(matrix)
            bal = m["balanced_accuracy"]
            print(f"\n(no scored artifacts — discrimination not measurable: "
                  f"balanced accuracy {'n/a' if bal is None else f'{bal:.2f}'})")

    print(f"\nDeterministic: {passes} passed, {fails} failed.")
    return 1 if (fails or judge_live_error) else 0


if __name__ == "__main__":
    sys.exit(main())
