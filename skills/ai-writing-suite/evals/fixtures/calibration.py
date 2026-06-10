#!/usr/bin/env python3
"""Miss-target calibration table — which naive-baseline miss counts keep an eval
set inside the 30-40% fail band, for each set size n.

WHY this exists: `run_fixtures.run_deterministic` hard-asserts
`30 <= miss_pct <= 40`, where `miss_pct = 100 * miss / total` and a "miss" is an
AI `before` draft the flat baseline scores BELOW `baseline_threshold`. At the
current n=8 that band admits EXACTLY ONE miss count — 3 (37.5%); 2 (25%) and
4 (50%) both fail. So adding or removing even one fixture can silently flip CI
red. This module turns "is my set still calibrated?" from a knife-edge into a
lookup: given a target set size n, it returns the miss count(s) that satisfy the
band — and flags the sizes that CANNOT satisfy it at all.

Pure arithmetic, stdlib only — no fixtures or model needed to compute the table.
A separate cross-check (`test_calibration.py`) ties this table to the live
`fixtures.json`, so the table's notion of "in band" can't drift from what
`run_fixtures` actually asserts.

Run as a script to print the table:
    python3 -m fixtures.calibration            # default range (n=5..30)
    python3 -m fixtures.calibration 6 24       # n from 6 to 24
"""

import sys

# These MUST match the live assert in run_fixtures.run_deterministic (the
# `30 <= miss_pct <= 40` line) and test_fixtures.Calibration. They live here as
# named constants so the table and the live assert share ONE definition of "in
# band"; test_calibration cross-checks against the live fixtures so changing one
# side without the other is caught.
BAND_LO = 30  # inclusive, percent
BAND_HI = 40  # inclusive, percent


def valid_miss_counts(n, lo=BAND_LO, hi=BAND_HI):
    """Integer miss counts m in [0, n] with lo <= 100*m/n <= hi.

    Returns a sorted list. EMPTY when no integer miss count lands in the band —
    i.e. a set of size n cannot be calibrated. Example: n=4 -> band [1.2, 1.6],
    which contains no integer, so a 4-item set can never satisfy the assert.
    """
    if n <= 0:
        return []
    return [m for m in range(n + 1) if lo <= 100 * m / n <= hi]


def miss_target(n, lo=BAND_LO, hi=BAND_HI):
    """The single recommended miss count for size n, or None if uncalibratable.

    Picks the valid count whose fail-rate is closest to the band MIDPOINT
    ((lo+hi)/2 = 35%) — i.e. the choice with the most margin to either edge, so a
    single fixture's score drifting is least likely to push the set out of band.
    Ties (two counts equidistant from the midpoint) resolve to the lower count.
    """
    counts = valid_miss_counts(n, lo, hi)
    if not counts:
        return None
    mid = (lo + hi) / 2
    return min(counts, key=lambda m: (abs(100 * m / n - mid), m))


def table(n_min, n_max, lo=BAND_LO, hi=BAND_HI):
    """Rows of (n, valid_counts, pcts, target) for n in [n_min, n_max]."""
    rows = []
    for n in range(n_min, n_max + 1):
        counts = valid_miss_counts(n, lo, hi)
        pcts = [round(100 * m / n, 1) for m in counts]
        rows.append((n, counts, pcts, miss_target(n, lo, hi)))
    return rows


def format_table(rows, lo=BAND_LO, hi=BAND_HI):
    """Render the table as text for a human to eyeball before building a set."""
    out = [f"Miss-target calibration table (band: {lo}-{hi}% inclusive)",
           f"{'n':>3}  {'valid miss counts':<24}  {'fail %':<18}  target",
           "-" * 64]
    for n, counts, pcts, target in rows:
        if counts:
            counts_s = ", ".join(str(c) for c in counts)
            pcts_s = ", ".join(f"{p:g}%" for p in pcts)
            target_s = f"{target} ({100 * target / n:.0f}%)"
        else:
            counts_s = "(none - uncalibratable)"
            pcts_s = "-"
            target_s = "-"
        out.append(f"{n:>3}  {counts_s:<24}  {pcts_s:<18}  {target_s}")
    return "\n".join(out)


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    n_min = int(argv[0]) if len(argv) > 0 else 5
    n_max = int(argv[1]) if len(argv) > 1 else 30
    print(format_table(table(n_min, n_max)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
