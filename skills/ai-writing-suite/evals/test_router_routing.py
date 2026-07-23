"""Static routing-decision fixtures for the AI Writing Suite router."""

import os
import re
import unittest


SKILL = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "SKILL.md",
))

ROUTING_FIXTURES = (
    ("polish this without adding content", "comms-polish"),
    ("draft a new page from this brief", "comms-draft"),
    ("add a new section", "comms-draft"),
    ("polish this and add a risks section", "comms-draft"),
    ("answer this question from the knowledge base", "comms-qa"),
    ("learn my voice", "voice-onboard"),
)

ROUTER_ANCHORS = {
    "polish this without adding content":
        "edit existing text, with no new content added",
    "draft a new page from this brief": "a new page from a brief",
    "add a new section": "a new section",
    "polish this and add a risks section":
        "a mix of polishing existing text and adding to it",
    "answer this question from the knowledge base":
        "ask a question the knowledge base answers",
    "learn my voice": "teach the tool their writing style",
}


class RouterRoutingDecision(unittest.TestCase):
    def _skill_text(self):
        with open(SKILL, encoding="utf-8") as fh:
            return fh.read()

    def _routing_rows(self):
        text = self._skill_text()
        route_section = text.split("## How to route (executable)", 1)[1]
        decision_table = route_section.split(
            "**Precedence rule for mixed requests.**", 1)[0]
        rows = re.findall(
            r"^\|\s*(.*?)\s*\|\s*`([^`]+)`\s*\|\s*$",
            decision_table,
            re.M,
        )
        return [(re.sub(r"\*\*", "", intent), route)
                for intent, route in rows]

    def test_decision_table_encodes_routing_fixtures(self):
        rows = self._routing_rows()
        for request_phrase, expected_route in ROUTING_FIXTURES:
            with self.subTest(request=request_phrase):
                row_anchor = ROUTER_ANCHORS[request_phrase]
                matching_routes = [
                    route for intent, route in rows
                    if row_anchor in intent
                ]
                self.assertEqual(
                    matching_routes,
                    [expected_route],
                    f"router decision table does not map {request_phrase!r} "
                    f"exactly to {expected_route!r}",
                )

    def test_mixed_precedence_example_routes_to_draft(self):
        text = self._skill_text()
        match = re.search(
            r"\*\*Precedence rule for mixed requests\.\*\*(?P<body>.*?)(?:\n\n|\Z)",
            text,
            re.S,
        )
        self.assertIsNotNone(
            match,
            "router is missing the mixed-request precedence paragraph",
        )
        paragraph = " ".join(match.group("body").split())
        self.assertIn(
            '"polish this and add a risks section"',
            paragraph,
        )
        self.assertIn("routes to `comms-draft`", paragraph)
        self.assertIn("pure rewording with no new material", paragraph)
        self.assertIn("Route to `comms-polish` only", paragraph)


if __name__ == "__main__":
    unittest.main()
