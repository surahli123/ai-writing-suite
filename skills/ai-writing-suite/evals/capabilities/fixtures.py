"""Capability: fixtures — deterministic detector bands + 30-40% baseline calibration.

Moved verbatim from run_all.sh step 3: `python3 -m fixtures.run_fixtures`.
Emits the load-bearing calibration line (`Naive-baseline miss rate: 3/8 = 38% ...`).
"""

import sys

SPEC = {
    "id": "fixtures",
    "name": "fixtures (deterministic + calibration)",
    "kind": "batch",
    "needs_model": False,
    "depends_on": ["unit_tests"],
}


def run(context):
    return context.run([sys.executable, "-m", "fixtures.run_fixtures"])
