"""Static skill lint (round-2 research R2-8): portable frontmatter, size budgets,
intent-first descriptions, and a labeled trigger set.

Each rule is a pure function, so a mutant can prove the rule fails when it
should. The live trigger run is host-specific and opt-in; here we only check
that the trigger fixture covers every sub-skill and has near-miss negatives.
"""
import glob
import json
import os
import re
import unittest

SUITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_FILES = [os.path.join(SUITE, "SKILL.md")] + sorted(glob.glob(os.path.join(SUITE, "skills", "*", "SKILL.md")))
PORTABLE_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
MAX_DESC = 1024      # Agent Skills spec limit
MAX_BODY_LINES = 500  # Anthropic / agentskills.io authoring guidance


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    out = {}
    for ln in m.group(1).splitlines():
        if ln and not ln.startswith((" ", "\t")) and ":" in ln:
            k, _, v = ln.partition(":")
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def lint(path, text):
    """Return a list of rule violations for one SKILL.md."""
    fm = frontmatter(text)
    errs = []
    extra = set(fm) - PORTABLE_KEYS
    if extra:
        errs.append(f"non-portable frontmatter keys: {sorted(extra)}")
    expected_name = os.path.basename(os.path.dirname(path))
    if fm.get("name") != expected_name:
        errs.append(f"name {fm.get('name')!r} != directory {expected_name!r}")
    desc = fm.get("description", "")
    if len(desc) > MAX_DESC:
        errs.append(f"description is {len(desc)} chars (> {MAX_DESC})")
    if not re.search(r"\bUse (?:when|for)\b", desc[:400]):
        errs.append("description lacks an early 'Use when/for' intent clause")
    if "Not for" not in desc:
        errs.append("description names no near-miss ('Not for ...')")
    if text.count("\n") > MAX_BODY_LINES:
        errs.append(f"SKILL.md is {text.count(chr(10))} lines (> {MAX_BODY_LINES})")
    return errs


class SkillLint(unittest.TestCase):
    def test_shipped_skills_pass(self):
        self.assertEqual(len(SKILL_FILES), 5)
        for p in SKILL_FILES:
            with self.subTest(skill=os.path.relpath(p, SUITE)):
                self.assertEqual(lint(p, open(p, encoding="utf-8").read()), [])

    def test_each_rule_trips_on_a_mutant(self):
        p = os.path.join(SUITE, "skills", "comms-polish", "SKILL.md")
        good = open(p, encoding="utf-8").read()
        mutants = {
            "non-portable": good.replace("---\nname:", "---\nuser-invocable: true\nname:", 1),
            "!= directory": good.replace("name: comms-polish", "name: polish", 1),
            "chars (>": re.sub(r'description: "', 'description: "' + "x" * 1100, good, count=1),
            "intent clause": good.replace("Use when", "Handy if", 1),
            "near-miss": good.replace("Not for", "Also handles", 1),
            "lines (>": good + "\n" * 600,
        }
        for needle, text in mutants.items():
            with self.subTest(rule=needle):
                self.assertTrue(any(needle in e for e in lint(p, text)), f"rule '{needle}' did not fire")


class TriggerFixture(unittest.TestCase):
    def test_every_sub_skill_and_negatives_are_covered(self):
        cases = json.load(open(os.path.join(SUITE, "evals", "fixtures", "trigger_cases.json"), encoding="utf-8"))["cases"]
        names = {os.path.basename(os.path.dirname(p)) for p in SKILL_FILES[1:]}
        counts = {n: 0 for n in names | {"none"}}
        for c in cases:
            self.assertIn(c["expect"], counts, c)
            counts[c["expect"]] += 1
        for n in names:
            self.assertGreaterEqual(counts[n], 2, f"{n} needs >= 2 should-trigger queries")
        self.assertGreaterEqual(counts["none"], 5, "need >= 5 near-miss negatives")
        self.assertEqual(len({c["query"] for c in cases}), len(cases), "duplicate query")


if __name__ == "__main__":
    unittest.main()
