"""Capability: KB smoke — end-to-end ingestion/retrieval over the seed KB.

Moved verbatim from run_all.sh step 2: `python3 smoke_test.py`.
"""

import sys

SPEC = {
    "id": "kb_smoke",
    "name": "KB smoke",
    "kind": "batch",
    "needs_model": False,
    "depends_on": ["unit_tests"],
}


def run(context):
    return context.run([sys.executable, "smoke_test.py"])
