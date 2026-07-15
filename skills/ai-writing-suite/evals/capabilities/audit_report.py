"""Capability: audit-report output contract — conforming passes, nonconforming fails.

Moved verbatim from run_all.sh step 7: `python3 -m audit_report.run_report_contract`.
Emits the load-bearing catalog line (`Catalog registry: 72 tell ids loaded ...`).
"""

import sys

SPEC = {
    "id": "audit_report",
    "name": "audit-report output contract",
    "kind": "batch",
    "needs_model": False,
    "depends_on": ["unit_tests"],
}


def run(context):
    return context.run([sys.executable, "-m", "audit_report.run_report_contract"])
