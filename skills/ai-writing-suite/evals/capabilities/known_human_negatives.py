"""Capability: provenance-gated known-human-negative false-positive evaluation."""

import sys

SPEC = {
    "id": "known_human_negatives",
    "name": "known human negatives",
    "kind": "batch",
    "needs_model": False,
    "depends_on": [
        "audit_report",
        "comms_draft",
        "false_positives",
        "fixtures",
        "kb_smoke",
        "unit_tests",
        "voice_extraction",
    ],
}


def run(context):
    return context.run(
        [sys.executable, "-m", "known_human.run_known_human"]
    )
