#!/usr/bin/env python3
"""Run the audit-report OUTPUT-CONTRACT check: conforming passes, nonconforming fails.

Run from `evals/`:
    python3 -m audit_report.run_report_contract

This is a contract/regression check, NOT behavioral eval coverage of comms-polish
(no skill is invoked; both artifacts are hand-authored). It proves the checker
discriminates a conforming report from one with planted violations, which is what
makes the checker trustworthy as a grader. Exits nonzero if the conforming artifact
fails OR the nonconforming artifact passes. Stdlib only, no model, no key.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from audit_report.check_report import check_report, load_catalog_ids  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CONFORMING = os.path.join(HERE, "conforming.md")
NONCONFORMING = os.path.join(HERE, "nonconforming.md")


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def main():
    print("=== Audit-report output-contract check ===")
    print("(structure only — NOT behavioral coverage; no skill is invoked)\n")
    catalog_ids = load_catalog_ids()
    print(f"Catalog registry: {len(catalog_ids)} tell ids loaded from _shared/patterns/\n")

    fails = 0

    ok, viols = check_report(_read(CONFORMING), catalog_ids)
    if ok:
        print("[PASS] conforming.md    — conforms to the contract")
    else:
        fails += 1
        print("[FAIL] conforming.md    — expected to conform but did not:")
        for v in viols:
            print(f"          - {v}")

    ok, viols = check_report(_read(NONCONFORMING), catalog_ids)
    if not ok:
        print(f"[PASS] nonconforming.md — rejected, {len(viols)} violation(s) caught:")
        for v in viols:
            print(f"          - {v}")
    else:
        fails += 1
        print("[FAIL] nonconforming.md — expected violations but checker passed it "
              "(checker is not discriminating)")

    print()
    if fails:
        print(f"CONTRACT CHECK FAILED ({fails} artifact(s) misclassified).")
        return 1
    print("Contract check passed: checker discriminates conforming vs nonconforming.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
