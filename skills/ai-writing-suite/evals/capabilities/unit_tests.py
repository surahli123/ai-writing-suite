"""Capability: unit tests — detector logic + fixture/judge/false-positive/draft suites.

Moved verbatim from run_all.sh step 1: `python3 -m unittest discover -p 'test_*.py'`.
"""

import sys

SPEC = {
    "id": "unit_tests",
    "name": "unit tests",
    "kind": "batch",
    "needs_model": False,
    "depends_on": [],
}


def run(context):
    return context.run([sys.executable, "-m", "unittest", "discover", "-p", "test_*.py"])
