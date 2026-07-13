#!/usr/bin/env python3
"""Run the adversarial false-positive suite.

Run from `evals/`:
    python3 -m fixtures.run_false_positives

WHY this is a SEPARATE runner from run_fixtures.py: the before/after fixtures
measure that GOOD REWRITES score low and that a naive baseline misses ~30-40% of
AI drafts (the calibration band). This suite measures the opposite failure — that
CLEAN HUMAN prose is NOT flagged as AI. Keeping them apart means neither can
mask the other, and this one never touches the calibration denominator.

Two roles (see false_positives.json `_doc`):
  - clean   : genuine-human-style prose the detector must NOT flag. A clean
              sample that scores >= flag_threshold FAILS the run (a false
              positive == a real detector regression).
  - control : deliberate AI slop planted so the harness can prove it detects at
              all. A control that scores < flag_threshold FAILS the run (a
              suite where nothing can trip is vacuous).

Stdlib only, no model, no key — pure detector scoring, safe for CI.
"""

import json
import os
import sys

# Allow running both as a module (-m fixtures.run_false_positives) and as a script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detector.detector import analyze  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FP_PATH = os.path.join(HERE, "false_positives.json")


def load_false_positives():
    with open(FP_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def run(data):
    """Score every sample; enforce clean<threshold and control>=threshold.

    Returns (passes, fails). A nonzero `fails` is meant to abort the run so a
    detector regression can't slip through CI green.
    """
    threshold = data["flag_threshold"]
    samples = data["samples"]
    clean = [s for s in samples if s["role"] == "clean"]
    control = [s for s in samples if s["role"] == "control"]

    passes = fails = 0
    print(f"=== False-positive suite (flag_threshold={threshold}) ===\n")

    print("-- clean (must score < threshold: a flag here is a false positive) --")
    for s in clean:
        score = analyze(s["text"])["score"]
        ok = score < threshold
        passes += ok
        fails += not ok
        print(f"[{'PASS' if ok else 'FAIL'}] {s['id']:22} score={score:3} "
              f"({s.get('flavor', '-')})"
              + ("" if ok else f"  <-- FALSE POSITIVE: >= {threshold}"))

    print("\n-- control (must score >= threshold: the planted positive) --")
    for s in control:
        score = analyze(s["text"])["score"]
        ok = score >= threshold
        passes += ok
        fails += not ok
        print(f"[{'PASS' if ok else 'FAIL'}] {s['id']:22} score={score:3}"
              + ("" if ok else f"  <-- MISSED PLANTED POSITIVE: < {threshold}"))

    # Should-not-trigger pass rate: of the clean (should-not-trigger) samples,
    # how many correctly stayed below threshold. This is the headline number.
    clean_ok = sum(1 for s in clean if analyze(s["text"])["score"] < threshold)
    rate = 100 * clean_ok / len(clean) if clean else 0
    print(f"\nShould-not-trigger pass rate: {clean_ok}/{len(clean)} = {rate:.0f}% "
          f"(clean human-style samples correctly NOT flagged)")
    print(f"Planted-positive control: {sum(1 for s in control if analyze(s['text'])['score'] >= threshold)}"
          f"/{len(control)} tripped as required")
    return passes, fails


def main(argv=None):
    data = load_false_positives()
    passes, fails = run(data)
    print(f"\nFalse-positive suite: {passes} passed, {fails} failed.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
