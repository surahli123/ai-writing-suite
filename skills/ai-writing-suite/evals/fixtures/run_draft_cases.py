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
# "3 March"'s 3). Punctuation is trimmed; the "%" is kept AND a bare-number form is
# also checked against the sources, which is the conservative direction (a number
# present in the brief is never flagged just because the draft added a % sign).
_NUMERIC = re.compile(r"\d[\d,\.:/]*%?")

# Candidate specific #2: a run of 2+ capitalized words — the shape an invented
# product/company/person name takes ("Northwind Retention"). Single capitalized
# words are NOT candidates: sentence starts and ordinary given names would drown
# the signal in false positives. The gap is [ \t]+, never \s+: a name does not span
# a line break, and a greedy \s+ stitched a heading to the next line's first word
# ("## Draft" + "Subject:" -> a phantom "Draft Subject").
_CAP_RUN = re.compile(r"\b[A-Z][\w'’\-]*(?:[ \t]+[A-Z][\w'’\-]*)+")

# Stripped from the FRONT of a capitalized run before the 2+-word test, so a
# sentence-initial function word ("The Acme dashboard") does not manufacture a
# two-word "proper noun" out of one ordinary name.
_RUN_LEAD_STOPWORDS = {
    "a", "an", "the", "and", "but", "so", "or", "if", "in", "on", "at", "for",
    "we", "i", "it", "you", "they", "this", "that", "these", "those", "our",
    "my", "their", "his", "her", "no", "not", "nothing", "when", "where",
    "while", "after", "before", "once", "here", "there", "then", "now",
    "subject", "recommendation", "standard",
}

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


def find_fabrications(draft, sources):
    """Return the specifics in `draft` that trace back to NEITHER the brief nor the KB.

    Pure fn (no I/O, no env) so tests can call it on hand-built inputs. `sources` is
    the raw brief+KB text; it is normalized here.

    Two candidate classes, chosen because they are the two shapes an invented fact
    takes in practice: a NUMBER presented as measurement ("churn fell 23%") and a
    multi-word CAPITALIZED NAME presented as a real entity ("Northwind Retention").
    A candidate is a violation iff it appears nowhere in the sources.

    Known limits, stated rather than hidden: single-word proper nouns are not
    candidates (too many false positives from sentence starts), and Title Case
    Headings would read as a proper-noun run — the artifacts use sentence-case
    headings on purpose. This is a checker for the fabrication SHAPE, not a
    semantic fact-checker.
    """
    src = _norm(sources)
    body = _NEEDS_SPAN.sub(" ", draft or "")  # a declared gap is not a claimed fact
    found = []

    for m in _NUMERIC.finditer(body):
        tok = m.group(0).rstrip(".,:/")
        if not tok:
            continue
        bare = tok.rstrip("%")
        if tok.lower() in src or bare.lower() in src:
            continue
        found.append(tok)

    for m in _CAP_RUN.finditer(body):
        words = m.group(0).split()
        while words and words[0].lower() in _RUN_LEAD_STOPWORDS:
            words.pop(0)
        if len(words) < 2:
            continue  # one name after the stopword strip — not a candidate
        phrase = " ".join(words)
        if _norm(phrase) in src:
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
    """Clarifying questions asked before drafting: '?'-bearing lines in the pre-draft."""
    return sum(1 for line in pre_draft_section(draft).splitlines() if "?" in line)


def missing_criteria_dimensions(draft):
    """Which of the five step-1 dimensions are NOT named before the draft body."""
    pre = _norm(pre_draft_section(draft))
    return [d for d in CRITERIA_DIMENSIONS if d not in pre]


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
          f"good-passes AND bad-trips-{'/'.join(sorted({c['failure_mode'] for c in cases}))}.")
    return passes, fails


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

            raw = judge.score(prompt)  # raises JudgeError on transport/auth (loud)
            parsed = judge.parse_dimensions(raw) if raw is not None else {}
            if parsed:
                verified = judge.verify_evidence(parsed, case.get("brief", ""),
                                                 case[role])
                for dim, status in verified.items():
                    if status == "not_verbatim":
                        print(f'  [warn] {label}/{dim}: EVIDENCE not verbatim in '
                              f'brief/draft — "{parsed[dim]["evidence"]}"')
            verdict = (judge.aggregate([judge.parse_dimension_lines(raw)], JUDGE_FOCUS)
                       if raw is not None else None)
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
