#!/usr/bin/env python3
"""Run the before/after fixtures. Deterministic half always; LLM half on demand.

Run from `evals/`:
    python3 -m fixtures.run_fixtures            # deterministic + calibration
    python3 -m fixtures.run_fixtures --judge    # also emit LLM-judge prompts

WHY a model is NOT required: the deterministic half (detector score bands +
naive-baseline miss rate) is the part that gates CI. The LLM half needs a model;
when none is wired in we print the judge prompts and mark them SKIPPED so a
reader can see exactly what *would* run, instead of a green check that proved
nothing. There is intentionally no API call here — this repo ships zero deps and
no key. A host integration calls `build_judge_prompt()` and sends it to whatever
model the surface provides.
"""

import argparse
import json
import os
import re
import sys

# Allow running both as a module (-m fixtures.run_fixtures) and as a script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detector.detector import analyze  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES_PATH = os.path.join(HERE, "fixtures.json")
FIXTURES_FAIL_PATH = os.path.join(HERE, "fixtures_fail.json")
RUBRIC_PATH = os.path.join(HERE, "rubric.md")

# Candidate fact surfaces for must_preserve declarations. The numeric pattern
# mirrors run_draft_cases.py's _NUMERIC: digit-bearing tokens, including
# percentages and date-shaped punctuation. Dates add named calendar forms; URLs
# cover explicit links; labels cover short ALLCAPS identifiers and TitleCase
# names such as API, Q3, CSV, and Stripe.
_NUMERIC = re.compile(r"\d[\d,\.:/]*%?")
_DATE = re.compile(
    r"\b(?:"
    r"\d{4}-\d{1,2}-\d{1,2}|"
    r"\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?|"
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
    r"Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?(?:,\s*\d{4})?|"
    r"\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|"
    r"Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
    r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)(?:\s+\d{4})?|"
    r"Q[1-4]|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|"
    r"January|February|March|April|May|June|July|August|September|October|"
    r"November|December)\b",
    re.IGNORECASE,
)
_URL = re.compile(r"\b(?:https?://|www\.)[^\s<>()]+", re.IGNORECASE)
_LABEL = re.compile(r"\b(?:[A-Z][A-Z0-9_-]{1,15}|[A-Z][a-z][A-Za-z0-9_-]{0,14})\b")
_PRESERVABLE_EXTRACTORS = (
    ("number", _NUMERIC),
    ("date", _DATE),
    ("url", _URL),
    ("label", _LABEL),
)

# Required fields for a gold-FAIL fixture (see fixtures_fail.json::_doc). Distinct
# from the PASS-suite shape: no expect_baseline (these are NOT calibration items),
# but a mandatory expected_verdict='FAIL' + a fail_dimension naming the driver.
FAIL_REQUIRED = {"id", "genre", "difficulty", "before", "after",
                 "rubric_focus", "expected_verdict", "fail_dimension"}


def load_fixtures():
    with open(FIXTURES_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def load_fail_fixtures():
    with open(FIXTURES_FAIL_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def _in_band(score, lo=None, hi=None):
    if lo is not None and score < lo:
        return False
    if hi is not None and score > hi:
        return False
    return True


def _normalize_whitespace(text):
    return " ".join(text.split())


def _extract_preservable_literals(text):
    """Return typed number/date/URL/label atoms found in text."""
    return {
        (kind, _normalize_whitespace(match.group(0)).rstrip(".,;:!?"))
        for kind, pattern in _PRESERVABLE_EXTRACTORS
        for match in pattern.finditer(text)
    }


def run_deterministic(data):
    """Assert detector scores land in the declared bands. Returns (passes, fails)."""
    threshold = data["baseline_threshold"]
    passes = fails = 0
    miss = total = 0

    print("=== Deterministic check (detector score bands) ===\n")
    for f in data["fixtures"]:
        before = analyze(f["before"])["score"]
        after = analyze(f["after"])["score"]
        normalized_after = _normalize_whitespace(f["after"])
        after_literals = _extract_preservable_literals(f["after"])

        ok = True
        reasons = []
        dropped = []
        if not _in_band(before, f.get("before_band_min"), f.get("before_band_max")):
            ok = False
            reasons.append(
                f"before={before} outside "
                f"[{f.get('before_band_min', '-')}, {f.get('before_band_max', '-')}]")
        if not _in_band(after, hi=f.get("after_band_max")):
            ok = False
            reasons.append(f"after={after} > {f.get('after_band_max')}")
        for literal in f.get("must_preserve", []):
            normalized_literal = _normalize_whitespace(literal)
            literal_atoms = _extract_preservable_literals(literal)
            if (normalized_literal not in normalized_after
                    or not literal_atoms.issubset(after_literals)):
                ok = False
                dropped.append(literal)

        if ok:
            passes += 1
        else:
            fails += 1

        # Naive-baseline accounting: a flat threshold flags `before` as AI iff
        # score >= threshold. A "miss" is an AI draft that scores below it.
        # `detector_blind` fixtures (judge-only over-stepping cases) are MISSES
        # by construction — the tell is in stance, not vocabulary — so they are
        # excluded from the calibration denominator. Their score bands above are
        # still checked; only the 30-40% rate measures the detector-targeted set.
        caught = before >= threshold
        if not f.get("detector_blind"):
            total += 1
            if not caught:
                miss += 1

        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {f['id']:22} before={before:3} after={after:3} "
              f"baseline={'CATCH' if caught else 'MISS '}"
              + ("  (judge-only)" if f.get("detector_blind") else ""))
        for r in reasons:
            print(f"        {r}")
        for literal in dropped:
            print(f"[FAIL] {f['id']} dropped '{literal}'")

    miss_pct = 100 * miss / total if total else 0
    print(f"\nNaive-baseline miss rate: {miss}/{total} = {miss_pct:.0f}% "
          f"(threshold={threshold}; calibration target 30-40%)")
    calib_ok = 30 <= miss_pct <= 40
    print(f"Calibration in target band: {'YES' if calib_ok else 'NO'}")
    if not calib_ok:
        fails += 1  # treat out-of-band calibration as a suite failure
    return passes, fails


def run_fail_deterministic(data):
    """Validate the gold-FAIL fixtures: well-formedness + loose detector bands.

    These are JUDGE-DISCRIMINATION fixtures (every `after` is a bad rewrite the
    judge must reject), NOT calibration items. They are NEVER added to the
    naive-baseline miss-rate denominator — that computation lives entirely in
    run_deterministic over fixtures.json and is untouched here. The deterministic
    path cannot compute a FAIL verdict without a judge, so all it asserts is that
    each fixture is shaped correctly and its declared score bands still hold.
    Returns (passes, fails).
    """
    passes = fails = 0
    print("\n=== Gold-FAIL fixtures (well-formedness + bands; judge-discrimination set) ===\n")
    for f in data["fixtures"]:
        ok = True
        reasons = []

        missing = FAIL_REQUIRED - set(f)
        if missing:
            ok = False
            reasons.append(f"missing fields {sorted(missing)}")
        if f.get("expected_verdict") != "FAIL":
            ok = False
            reasons.append(f"expected_verdict={f.get('expected_verdict')!r} (must be 'FAIL')")
        fd = f.get("fail_dimension")
        focus = f.get("rubric_focus", [])
        # The FAIL driver must be a dimension the judge is actually told to weigh,
        # i.e. present in rubric_focus — except no_fabrication, which the rubric
        # requires on every verdict even when unlisted.
        if fd is not None and fd not in focus and fd != "no_fabrication":
            ok = False
            reasons.append(f"fail_dimension {fd!r} not in rubric_focus and != no_fabrication")

        before = analyze(f["before"])["score"] if "before" in f else None
        after = analyze(f["after"])["score"] if "after" in f else None
        if before is not None and not _in_band(
                before, f.get("before_band_min"), f.get("before_band_max")):
            ok = False
            reasons.append(
                f"before={before} outside "
                f"[{f.get('before_band_min', '-')}, {f.get('before_band_max', '-')}]")
        if after is not None and not _in_band(after, hi=f.get("after_band_max")):
            ok = False
            reasons.append(f"after={after} > {f.get('after_band_max')}")

        if ok:
            passes += 1
        else:
            fails += 1
        mark = "PASS" if ok else "FAIL"
        loc = (f"before={before:3} after={after:3}"
               if before is not None and after is not None else "")
        print(f"[{mark}] {f.get('id', '?'):28} gold=FAIL via "
              f"{f.get('fail_dimension', '?'):20} {loc}")
        for r in reasons:
            print(f"        {r}")

    print(f"\nGold-FAIL well-formedness: {passes} ok, {fails} malformed "
          f"(judge-discrimination set — excluded from calibration denominator).")
    return passes, fails


def new_confusion():
    """Empty combined-cohort confusion accumulator (positive == judge says FAIL).

    Cells (gold x judge), filled from BOTH cohorts so discrimination is measurable:
      tp  gold FAIL & judge FAIL   (fixtures_fail.json — sensitivity lane)
      fn  gold FAIL & judge PASS
      tn  gold PASS & judge PASS   (fixtures.json     — specificity lane)
      fp  gold PASS & judge FAIL
    Plus:
      skipped        fixtures with no parseable verdict — NEVER folded into a cell
      ungraded       fixtures carrying no gold verdict at all (nothing to score against)
      driver_right   gold-FAIL caught with its DECLARED fail_dimension == FAIL
      driver_wrong   gold-FAIL caught for the wrong reason (driver dim not FAIL)
    driver_* is an ATTRIBUTION metric ("right reason"), NOT discrimination — it is
    computed over the positives only and cannot distinguish a constant classifier.
    """
    return {"tp": 0, "fn": 0, "tn": 0, "fp": 0,
            "skipped": 0, "ungraded": 0,
            "driver_right": 0, "driver_wrong": 0}


def record_verdict(matrix, gold, verdict):
    """Fold one fixture's (gold, judge) outcome into `matrix`. No-op when matrix is None.

    verdict None (unparseable / not configured) -> `skipped`, never a cell: an
    unscored fixture is missing data, not evidence for or against the judge.
    A fixture with no gold verdict is `ungraded` and likewise never lands in a cell.
    """
    if matrix is None:
        return
    if gold not in ("PASS", "FAIL"):
        matrix["ungraded"] += 1
        return
    if verdict is None:
        matrix["skipped"] += 1
        return
    if gold == "FAIL":
        matrix["tp" if verdict == "FAIL" else "fn"] += 1
    else:
        matrix["fp" if verdict == "FAIL" else "tn"] += 1


def confusion_metrics(matrix):
    """Derive sensitivity / specificity / balanced accuracy / driver attribution.

    Each is None when its denominator is empty (an empty cohort prints "n/a" rather
    than crashing or implying a score). Balanced accuracy needs BOTH cohorts — that
    is the whole point: a constant always-FAIL judge scores sensitivity 1.0 but
    specificity 0.0, so its balanced accuracy is 0.5 (chance), which is exactly what
    a single-cohort recall number hid.
    """
    tp, fn, tn, fp = matrix["tp"], matrix["fn"], matrix["tn"], matrix["fp"]
    sens = tp / (tp + fn) if (tp + fn) else None
    spec = tn / (tn + fp) if (tn + fp) else None
    bal = (sens + spec) / 2 if (sens is not None and spec is not None) else None
    dr, dw = matrix["driver_right"], matrix["driver_wrong"]
    attribution = dr / (dr + dw) if (dr + dw) else None
    return {"sensitivity": sens, "specificity": spec,
            "balanced_accuracy": bal, "attribution": attribution}


def _fmt(x):
    return "n/a" if x is None else f"{x:.2f}"


def print_confusion(matrix):
    """Print the ONE combined-cohort confusion block (advisory; never gates CI)."""
    m = confusion_metrics(matrix)
    print("\n=== Judge discrimination (BOTH cohorts, advisory) ===")
    print("positive = judge says FAIL (i.e. detects a bad rewrite)\n")
    print(f"                 judge FAIL   judge PASS")
    print(f"  gold FAIL      TP {matrix['tp']:<9} FN {matrix['fn']}")
    print(f"  gold PASS      FP {matrix['fp']:<9} TN {matrix['tn']}")
    print(f"\nsensitivity       = {_fmt(m['sensitivity'])}  (TP/(TP+FN) — catches bad rewrites)")
    print(f"specificity       = {_fmt(m['specificity'])}  (TN/(TN+FP) — spares good rewrites)")
    print(f"balanced accuracy = {_fmt(m['balanced_accuracy'])}  "
          f"((sens+spec)/2 — 0.50 == chance/constant classifier)")
    print(f"skipped (excluded from matrix) = {matrix['skipped']}"
          + (f", ungraded = {matrix['ungraded']}" if matrix["ungraded"] else ""))
    print(f"\ndriver attribution = {_fmt(m['attribution'])}  "
          f"({matrix['driver_right']} right-reason / "
          f"{matrix['driver_right'] + matrix['driver_wrong']} caught) — ATTRIBUTION "
          f"only,\n  i.e. 'was it caught for the declared reason'. NOT discrimination: "
          f"a constant\n  always-FAIL judge scores 1.00 here and 0.50 balanced accuracy.")


def run_fail_judge(data, matrix=None):
    """Judge sensitivity + reason-ATTRIBUTION over the gold-FAIL fixtures (opt-in).

    This is the POSITIVES lane only. For each bad rewrite a correct judge returns
    overall FAIL; overall FAIL AND fail_dimension==FAIL means it was caught for the
    RIGHT REASON (discriminated / driver_right). Overall FAIL with the driver dim
    passing is "right verdict, wrong reason" (wrong_reason / driver_wrong) — still a
    true positive for the confusion matrix, but not proof the judge saw the planted
    defect. judge-says-PASS overall == DISAGREEMENT (a false negative, missed).

    DISCRIMINATION IS NOT MEASURABLE HERE. Negatives alone cannot expose a constant
    classifier: an always-FAIL judge fails every dimension, so it also fails every
    declared driver and would score a perfect "caught for the right reason" tally on
    this lane. Discrimination is measured ONLY by the combined-cohort confusion
    matrix (new_confusion / confusion_metrics / print_confusion), which pairs these
    positives with the gold-PASS negatives from run_judge: the same always-FAIL judge
    lands sensitivity 1.00 / specificity 0.00 / balanced accuracy 0.50. Pass the
    shared `matrix` accumulator (main does) to feed that computation.

    Advisory, like run_judge: none of these counts drive the exit code; only a
    configured-but-broken judge (scored 0/N => provider envelope changed) does.
    Returns (discriminated, missed, wrong_reason, skipped, live_error).
    """
    from fixtures import judge  # lazy: keep the deterministic path network-free
    template = _extract_judge_template()
    configured = judge.is_configured()

    print("\n=== Gold-FAIL judge sensitivity + reason attribution ===")
    if not configured:
        print("No judge configured — SKIPPING this lane (needs a model).\n")
        for f in data["fixtures"]:
            record_verdict(matrix, f.get("expected_verdict"), None)
            print(f"[SKIP] {f['id']} (gold=FAIL via {f['fail_dimension']})")
        return 0, 0, 0, len(data["fixtures"]), False

    print("Judge configured — a correct judge marks every one FAIL on its "
          "declared driver dimension.\n"
          "(This lane measures SENSITIVITY only; specificity comes from the "
          "gold-PASS cohort.)\n")
    discriminated = missed = wrong_reason = skipped = 0
    for f in data["fixtures"]:
        prompt = build_judge_prompt(f, template)
        result = judge.evaluate(judge.JudgeRequest(
            prompt=prompt, before=f["before"], after=f["after"],
            rubric_focus=f["rubric_focus"]))  # raises JudgeError on transport (loud)
        raw, parsed, verdict = result.raw, result.parsed, result.verdict
        if raw is not None:
            _report_evidence(f, result)
        record_verdict(matrix, f.get("expected_verdict"), verdict)
        if verdict is None:
            skipped += 1
            print(f"[SKIP] {f['id']} — no parseable verdict returned")
            continue
        if verdict != "FAIL":
            missed += 1
            print(f"[MISS] {f['id']} — judge PASS but gold=FAIL (DISAGREEMENT)")
            continue
        # Overall FAIL == a true positive either way; the driver check only decides
        # WHY it was caught (attribution). A FAIL driven by an unrelated dim is
        # right-verdict/wrong-reason, not proof the judge saw the planted defect.
        driver = f["fail_dimension"]
        driver_verdict = parsed.get(driver, {}).get("verdict")
        if driver_verdict == "FAIL":
            discriminated += 1
            if matrix is not None:
                matrix["driver_right"] += 1
            print(f"[OK  ] {f['id']} — judge FAIL on {driver} == gold (right reason)")
        else:
            wrong_reason += 1
            if matrix is not None:
                matrix["driver_wrong"] += 1
            print(f"[WARN] {f['id']} — right verdict, wrong reason "
                  f"({driver} was {driver_verdict or 'absent'})")

    scored = discriminated + wrong_reason + missed
    print(f"\nGold-FAIL sensitivity lane: {discriminated + wrong_reason}/{scored} "
          f"caught ({discriminated} for the right reason, {wrong_reason} "
          f"right-verdict/wrong-reason, {missed} missed, {skipped} skipped) — "
          f"advisory. Discrimination requires BOTH cohorts: see the confusion matrix.")
    # Liveness mirror of run_judge: configured but nothing scored => envelope changed.
    live_error = scored == 0
    if live_error:
        print(f"ERROR: judge configured but scored 0/{len(data['fixtures'])} "
              f"FAIL fixtures — provider response envelope likely changed "
              f"(check AIWS_JUDGE_URL/MODEL).")
    return discriminated, missed, wrong_reason, skipped, live_error


def _report_evidence(fixture, result):
    """Advisory per-dimension evidence audit for one scored fixture.

    Prints the accepted EVIDENCE quote for every graded dim (so an operator can
    read what the judge cited), plus a [warn] line when a quote is missing,
    malformed, or well-formed-but-not-verbatim (appears nowhere in before/after —
    a fabricated quote the parser alone can't catch). Purely advisory: it never
    changes the verdict or the exit code. Reads the parsed dims, the verbatim check,
    and the missing/malformed dim list the façade already computed on this fixture
    (JudgeResult.parsed/verified/warnings) — the missing/malformed test is NOT
    re-derived here, it consults result.warnings (== evidence_warnings(raw)).
    """
    parsed = result.parsed
    verified = result.verified
    fid = fixture["id"]
    for dim, rec in parsed.items():
        ev = rec.get("evidence")
        if dim in result.warnings:
            why = ("malformed EVIDENCE quote (unpaired/empty)"
                   if rec.get("evidence_status") == "malformed"
                   else "verdict missing EVIDENCE quote")
            print(f"  [warn] {fid}/{dim}: {why}")
        elif ev and rec.get("evidence_status") == "ok":
            if verified.get(dim) == "not_verbatim":
                print(f'  [warn] {fid}/{dim}: EVIDENCE not verbatim in '
                      f'before/after — "{ev}"')
            else:
                print(f'  evidence[{dim}]: "{ev}"')


def build_judge_prompt(fixture, rubric_template):
    """Fill the rubric.md judge template for one fixture.

    no_fabrication is appended to the focus list when the fixture omits it, so the
    judge is ALWAYS told to score it. rubric.md requires no_fabrication for every
    verdict, but 3/8 fixtures don't list it in rubric_focus — without this the
    highest-stakes dimension would go unscored on those fixtures.
    """
    focus = list(fixture["rubric_focus"])
    if "no_fabrication" not in focus:
        focus.append("no_fabrication")
    return (rubric_template
            .replace("{genre}", fixture["genre"])
            .replace("{subtle_tell}", fixture.get("subtle_tell",
                     "obvious AI vocabulary and formatting"))
            .replace("{rubric_focus}", ", ".join(focus))
            .replace("{before}", fixture["before"])
            .replace("{after}", fixture["after"]))


def _extract_judge_template():
    """Pull the fenced judge-prompt template out of rubric.md."""
    with open(RUBRIC_PATH, encoding="utf-8") as fh:
        text = fh.read()
    start = text.find("```", text.find("Judge prompt template"))
    end = text.find("```", start + 3)
    return text[start + 3:end].strip()


def run_judge(data, matrix=None):
    """Score fixtures with the optional LLM judge, or SKIP when unconfigured.

    These fixtures are all gold-PASS: this is the NEGATIVES / SPECIFICITY lane. Pass
    the shared `matrix` accumulator (main does) so its TN/FP land in the combined
    confusion matrix alongside run_fail_judge's positives — that pairing is the only
    thing that can expose a constant classifier.

    Honesty stance: when no judge is configured (no key, or not opted in via
    AIWS_JUDGE_RUN=1) we print the filled prompt heads and mark every fixture
    SKIPPED — we never fabricate a verdict offline. When a judge IS configured we
    POST each prompt, parse the per-dimension PASS/FAIL lines, and RE-COMPUTE the
    verdict in Python (no_fabrication-overrides-FAIL, per rubric.md) instead of
    trusting the model's self-reported VERDICT line. A transport/auth error raises
    loudly (caller exits nonzero) — never a silent SKIP.

    Returns (passes, fails, skipped, live_error). The judge is ADVISORY in v1:
    its PASS/FAIL counts do NOT drive the process exit code. The ONE judge
    condition that does is `live_error` — configured but 0/N scored, meaning the
    provider response envelope likely changed (a broken harness, surfaced loudly).
    """
    from fixtures import judge  # lazy: never imported on the deterministic path
    template = _extract_judge_template()
    configured = judge.is_configured()

    print("\n=== LLM-judge check ===")
    if not configured:
        print("No judge configured (set AIWS_JUDGE_URL/MODEL/KEY + AIWS_JUDGE_RUN=1) "
              "— emitting the prompts that WOULD be sent, marked SKIPPED.\n")
    else:
        print("Judge configured — scoring each fixture against the rubric.\n")

    passes = fails = skipped = 0
    agree = gold_total = 0
    for f in data["fixtures"]:
        prompt = build_judge_prompt(f, template)

        if not configured:
            skipped += 1
            record_verdict(matrix, f.get("expected_verdict"), None)
            print(f"[SKIP] {f['id']} (focus: {', '.join(f['rubric_focus'])})")
            # Show the first 2 lines of the filled prompt as proof it built.
            head = "\n".join(prompt.splitlines()[:2])
            print(f"        prompt[0:2]: {head[:90]}...")
            continue

        result = judge.evaluate(judge.JudgeRequest(
            prompt=prompt, before=f["before"], after=f["after"],
            rubric_focus=f["rubric_focus"]))  # raises JudgeError on transport (loud)
        raw, verdict = result.raw, result.verdict
        if raw is not None:
            _report_evidence(f, result)
        record_verdict(matrix, f.get("expected_verdict"), verdict)
        if verdict is None:
            skipped += 1
            print(f"[SKIP] {f['id']} — no parseable verdict returned")
            continue

        if verdict == "PASS":
            passes += 1
        else:
            fails += 1
        gold = f.get("expected_verdict")
        if gold is not None:
            gold_total += 1
            agree += int(gold == verdict)
        print(f"[{verdict}] {f['id']}" + (f"  (gold={gold})" if gold else ""))

    scored = passes + fails
    if not configured:
        print(f"\nLLM-judge: 0 scored, all {skipped} SKIPPED "
              f"(configure a judge to run).")
        return passes, fails, skipped, False

    print(f"\nLLM-judge: {scored} scored ({passes} PASS / {fails} FAIL), "
          f"{skipped} skipped.")
    if gold_total:
        print(f"Judge-vs-gold agreement: {agree}/{gold_total} "
              f"(advisory — directional only at this n; NOT kappa).")

    # Liveness: configured but nothing scored => provider envelope likely changed.
    # This is the one judge condition that fails the run (a broken harness, loud),
    # distinct from the keyless all-SKIP path above which exits 0.
    live_error = scored == 0
    if live_error:
        print(f"ERROR: judge configured but scored 0/{len(data['fixtures'])} — "
              f"provider response envelope likely changed "
              f"(check AIWS_JUDGE_URL/MODEL).")
    return passes, fails, skipped, live_error


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description="Run before/after eval fixtures.")
    ap.add_argument("--judge", action="store_true",
                    help="also run the LLM-judge half (SKIPPED unless a judge is "
                         "configured via AIWS_JUDGE_* env vars)")
    args = ap.parse_args(argv)

    data = load_fixtures()
    passes, fails = run_deterministic(data)

    # Gold-FAIL suite (separate file, judge-discrimination). Its deterministic half
    # only validates well-formedness + bands and is NOT part of the calibration
    # denominator; its malformed-count DOES gate the run (a rotted FAIL fixture is
    # a real regression). See fixtures_fail.json::_doc.
    fail_data = load_fail_fixtures()
    fp, ff = run_fail_deterministic(fail_data)
    passes += fp
    fails += ff

    # The judge is ADVISORY: its PASS/FAIL counts do NOT change the exit code, so
    # CI (which never passes --judge and sets no key) stays deterministic and
    # key-free. The only judge condition that fails the run is a configured-but-
    # broken judge (live_error: scored 0/N) — a harness error, surfaced loudly.
    judge_live_error = False
    if args.judge:
        # ONE shared accumulator across BOTH cohorts: gold-PASS (negatives ->
        # specificity) and gold-FAIL (positives -> sensitivity). Discrimination is
        # only meaningful over both — a constant always-FAIL judge scores perfect
        # recall on the positives alone, and the matrix is what exposes it.
        matrix = new_confusion()
        _jp, _jf, _js, judge_live_error = run_judge(data, matrix)
        _d, _m, _w, _s, fail_live_error = run_fail_judge(fail_data, matrix)
        judge_live_error = judge_live_error or fail_live_error
        print_confusion(matrix)  # advisory: never touches the exit code

    print(f"\nDeterministic: {passes} passed, {fails} failed.")
    return 1 if (fails or judge_live_error) else 0


if __name__ == "__main__":
    sys.exit(main())
