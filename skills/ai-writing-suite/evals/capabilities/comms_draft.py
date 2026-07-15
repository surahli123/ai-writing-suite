"""Capability: comms-draft — good vs bad pre-authored draft artifacts told apart.

Moved verbatim from run_all.sh step 5: `python3 -m fixtures.run_draft_cases`.
"""

import sys

SPEC = {
    "id": "comms_draft",
    "name": "comms-draft behavioral cases",
    "kind": "batch",
    "needs_model": False,
    "depends_on": ["unit_tests"],
}


def run(context):
    return context.run([sys.executable, "-m", "fixtures.run_draft_cases"])
