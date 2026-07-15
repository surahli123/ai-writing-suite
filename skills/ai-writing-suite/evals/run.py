#!/usr/bin/env python3
"""run.py — discover every capability descriptor and run them fail-fast.

Replaces run_all.sh's hardcoded ordinal step list. Discovery (not a central list)
computes `[n/N]`; each capability shells out to the same command its old numbered
step ran, so load-bearing child output passes through byte-for-byte.

Run from `evals/`:
    python3 run.py

Exits nonzero on the first failing capability (matching the old `set -euo pipefail`).
"""

import sys

from core import Context, discover_capabilities, order_capabilities


def main():
    caps = order_capabilities(discover_capabilities())
    total = len(caps)
    context = Context()

    for i, cap in enumerate(caps, 1):
        print(f"== [{i}/{total}] {cap.name} ==")
        result = cap.run(context)
        if not result.ok:
            return result.returncode or 1

    print()
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
