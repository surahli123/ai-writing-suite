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
RUBRIC_PATH = os.path.join(HERE, "rubric.md")


def load_fixtures():
    with open(FIXTURES_PATH, encoding="utf-8") as fh:
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
        total += 1
        caught = before >= threshold
        if not caught:
            miss += 1

        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {f['id']:22} before={before:3} after={after:3} "
              f"baseline={'CATCH' if caught else 'MISS '}")
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


def build_judge_prompt(fixture, rubric_template):
    """Fill the rubric.md judge template for one fixture."""
    return (rubric_template
            .replace("{genre}", fixture["genre"])
            .replace("{subtle_tell}", fixture.get("subtle_tell",
                     "obvious AI vocabulary and formatting"))
            .replace("{rubric_focus}", ", ".join(fixture["rubric_focus"]))
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
    """Emit the filled judge prompts and mark them SKIPPED (no model wired in).

    A host integration would replace the `verdict = None` line with a real model
    call and aggregate per rubric.md. We never fabricate a verdict offline."""
    template = _extract_judge_template()
    print("\n=== LLM-judge check ===")
    print("No model is configured in this offline harness — emitting the prompts "
          "that WOULD be sent, marked SKIPPED.\n")
    for f in data["fixtures"]:
        prompt = build_judge_prompt(f, template)
        verdict = None  # offline: never invent a verdict
        print(f"[SKIP] {f['id']} (focus: {', '.join(f['rubric_focus'])})")
        # Show the first 2 lines of the filled prompt as proof it built.
        head = "\n".join(prompt.splitlines()[:2])
        print(f"        prompt[0:2]: {head[:90]}...")
    print("\nLLM-judge: 0 scored, all SKIPPED (wire a model to run).")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description="Run before/after eval fixtures.")
    ap.add_argument("--judge", action="store_true",
                    help="also emit LLM-judge prompts (skipped offline)")
    args = ap.parse_args(argv)

    data = load_fixtures()
    passes, fails = run_deterministic(data)
    if args.judge:
        run_judge(data)

    print(f"\nDeterministic: {passes} passed, {fails} failed.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
