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
import sys

# Allow running both as a module (-m fixtures.run_fixtures) and as a script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detector.detector import analyze  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES_PATH = os.path.join(HERE, "fixtures.json")
FIXTURES_FAIL_PATH = os.path.join(HERE, "fixtures_fail.json")
RUBRIC_PATH = os.path.join(HERE, "rubric.md")

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


def run_deterministic(data):
    """Assert detector scores land in the declared bands. Returns (passes, fails)."""
    threshold = data["baseline_threshold"]
    passes = fails = 0
    miss = total = 0

    print("=== Deterministic check (detector score bands) ===\n")
    for f in data["fixtures"]:
        before = analyze(f["before"])["score"]
        after = analyze(f["after"])["score"]

        ok = True
        reasons = []
        if not _in_band(before, f.get("before_band_min"), f.get("before_band_max")):
            ok = False
            reasons.append(
                f"before={before} outside "
                f"[{f.get('before_band_min', '-')}, {f.get('before_band_max', '-')}]")
        if not _in_band(after, hi=f.get("after_band_max")):
            ok = False
            reasons.append(f"after={after} > {f.get('after_band_max')}")

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


def run_fail_judge(data):
    """Judge-DISCRIMINATION over the gold-FAIL fixtures (opt-in judge path).

    For each bad rewrite a correct judge returns FAIL: judge-says-FAIL == agreement
    (the judge discriminated); judge-says-PASS == DISAGREEMENT (the judge missed a
    bad rewrite — the failure signal this suite exists to surface). Advisory, like
    run_judge: the discrimination counts do NOT drive the exit code; only a
    configured-but-broken judge (scored 0/N => provider envelope changed) does.
    Returns (discriminated, missed, skipped, live_error).
    """
    from fixtures import judge  # lazy: keep the deterministic path network-free
    template = _extract_judge_template()
    configured = judge.is_configured()

    print("\n=== Gold-FAIL judge discrimination ===")
    if not configured:
        print("No judge configured — SKIPPING discrimination (needs a model).\n")
        for f in data["fixtures"]:
            print(f"[SKIP] {f['id']} (gold=FAIL via {f['fail_dimension']})")
        return 0, 0, len(data["fixtures"]), False

    print("Judge configured — a correct judge marks every one FAIL.\n")
    discriminated = missed = skipped = 0
    for f in data["fixtures"]:
        prompt = build_judge_prompt(f, template)
        raw = judge.score(prompt)  # raises JudgeError on transport/auth (loud)
        if raw is not None:
            for dim in judge.evidence_warnings(raw):
                print(f"  [warn] {f['id']}/{dim}: verdict missing EVIDENCE quote")
        verdict = (judge.aggregate([judge.parse_dimension_lines(raw)],
                                   f["rubric_focus"]) if raw is not None else None)
        if verdict is None:
            skipped += 1
            print(f"[SKIP] {f['id']} — no parseable verdict returned")
            continue
        if verdict == "FAIL":
            discriminated += 1
            print(f"[OK  ] {f['id']} — judge FAIL == gold (discriminated)")
        else:
            missed += 1
            print(f"[MISS] {f['id']} — judge PASS but gold=FAIL (DISAGREEMENT)")

    scored = discriminated + missed
    print(f"\nGold-FAIL discrimination: {discriminated}/{scored} caught "
          f"({missed} missed, {skipped} skipped) — advisory.")
    # Liveness mirror of run_judge: configured but nothing scored => envelope changed.
    live_error = scored == 0
    if live_error:
        print(f"ERROR: judge configured but scored 0/{len(data['fixtures'])} "
              f"FAIL fixtures — provider response envelope likely changed "
              f"(check AIWS_JUDGE_URL/MODEL).")
    return discriminated, missed, skipped, live_error


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


def run_judge(data):
    """Score fixtures with the optional LLM judge, or SKIP when unconfigured.

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
            print(f"[SKIP] {f['id']} (focus: {', '.join(f['rubric_focus'])})")
            # Show the first 2 lines of the filled prompt as proof it built.
            head = "\n".join(prompt.splitlines()[:2])
            print(f"        prompt[0:2]: {head[:90]}...")
            continue

        raw = judge.score(prompt)  # raises JudgeError on transport/auth (loud)
        if raw is not None:
            for dim in judge.evidence_warnings(raw):
                print(f"  [warn] {f['id']}/{dim}: verdict missing EVIDENCE quote")
        verdict = (judge.aggregate([judge.parse_dimension_lines(raw)],
                                   f["rubric_focus"]) if raw is not None else None)
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
        _jp, _jf, _js, judge_live_error = run_judge(data)
        _d, _m, _s, fail_live_error = run_fail_judge(fail_data)
        judge_live_error = judge_live_error or fail_live_error

    print(f"\nDeterministic: {passes} passed, {fails} failed.")
    return 1 if (fails or judge_live_error) else 0


if __name__ == "__main__":
    sys.exit(main())
