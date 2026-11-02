"""Capability: comms-shape — good vs bad pre-authored intake/outline/draft artifacts told apart.

Renamed from comms_draft when comms-draft was archived (2026-11-02, owner ruling R4).

Moved verbatim from run_all.sh step 5: `python3 -m fixtures.run_draft_cases`.
"""

import sys

SPEC = {
    "id": "comms_shape",
    "name": "comms-shape behavioral cases",
    "kind": "batch",
    "needs_model": False,
    "depends_on": ["unit_tests"],
}


def run(context):
    return context.run([sys.executable, "-m", "fixtures.run_draft_cases"])
