"""Capability: false positives — clean human prose must NOT flag (+ planted control).

Moved verbatim from run_all.sh step 4: `python3 -m fixtures.run_false_positives`.
"""

import sys

SPEC = {
    "id": "false_positives",
    "name": "false positives",
    "kind": "batch",
    "needs_model": False,
    "depends_on": ["unit_tests"],
}


def run(context):
    return context.run([sys.executable, "-m", "fixtures.run_false_positives"])
