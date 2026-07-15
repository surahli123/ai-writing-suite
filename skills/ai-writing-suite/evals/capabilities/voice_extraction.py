"""Capability: voice-onboard extraction — engineered corpus + good/bad profiles.

Moved verbatim from run_all.sh step 6: `python3 -m fixtures.run_voice_extraction`.
"""

import sys

SPEC = {
    "id": "voice_extraction",
    "name": "voice-onboard extraction",
    "kind": "batch",
    "needs_model": False,
    "depends_on": [],
}


def run(context):
    return context.run([sys.executable, "-m", "fixtures.run_voice_extraction"])
