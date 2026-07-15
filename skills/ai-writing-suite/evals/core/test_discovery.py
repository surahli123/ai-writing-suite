"""Discovery premise guard (plan item 1, Risk 3).

The whole capability-runner refactor is motivated by renumbering collisions: if
discovery silently DROPS a capability, a whole regression suite stops running with
no failure. This test freezes the expected set of capability ids and asserts
discovery finds EXACTLY them — no more (stray module), no fewer (dropped file).

Proof-gate method: temporarily delete one descriptor module in the worktree and
confirm this test goes red before cutting run_all.sh over to run.py.
"""

import unittest

from core import discover_capabilities, order_capabilities

EXPECTED_IDS = {
    "unit_tests",
    "kb_smoke",
    "fixtures",
    "false_positives",
    "comms_draft",
    "voice_extraction",
    "audit_report",
}


class DiscoveryFindsExactlyKnownCapabilities(unittest.TestCase):
    def test_discovers_exactly_the_seven_known_ids(self):
        caps = discover_capabilities()
        found = {c.id for c in caps}
        self.assertEqual(
            found,
            EXPECTED_IDS,
            f"discovery drift: missing={EXPECTED_IDS - found} unexpected={found - EXPECTED_IDS}",
        )

    def test_exactly_seven_capabilities(self):
        self.assertEqual(len(discover_capabilities()), 7)

    def test_ordering_is_deterministic_and_total(self):
        caps = discover_capabilities()
        ordered = order_capabilities(caps)
        self.assertEqual({c.id for c in ordered}, {c.id for c in caps})
        self.assertEqual(ordered, order_capabilities(caps))


if __name__ == "__main__":
    unittest.main()
