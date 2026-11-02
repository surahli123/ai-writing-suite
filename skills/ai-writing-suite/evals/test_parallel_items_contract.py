"""Contract tests for parallel sets (step 9 of the 2026-11-02 plan).

Why: the fsdatalab article on readable AI text in bulk showed that in a list,
feed or card set, one structure and one word per concept are what make the set
quick to read. The catalog treated that symmetry as an AI tell (T7), and the
rhythm rules (R1, R2, R4), the final pass and tone.md pushed toward variation
everywhere. Plan: docs/plan-step9-and-comms-shape-2026-11-02.md (v2.3, owner
ruling R4). These tests pin the instruction text. They do not prove behavior;
the step-9 eval measures that.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "_shared" / "patterns"
POLISH = ROOT / "skills" / "comms-polish" / "SKILL.md"
FINAL = ROOT / "skills" / "comms-polish" / "references" / "final-pass-checklist.md"
TONE = ROOT / "_shared" / "knowledge" / "tone.md"
NOTICE = ROOT / "NOTICE.md"
PRESETS = ROOT / "skills" / "comms-polish" / "references" / "scenario-presets.md"
FIX = ROOT / "evals" / "fixtures"


def text(p):
    return p.read_text(encoding="utf-8")


def entry(file, tell_id):
    """Return one catalog entry's text, from its heading to the next `### `."""
    body = text(PATTERNS / file)
    m = re.search(rf"^### {tell_id} — .*?(?=^### |\Z)", body, re.M | re.S)
    if not m:
        raise AssertionError(f"{tell_id} not found in {file}")
    return m.group(0)


class RhythmScopedToProse(unittest.TestCase):
    def test_r1_exempts_parallel_sets(self):
        r1 = entry("rhythm-stylometric.md", "R1")
        self.assertIn("R1 concerns running prose", r1)
        self.assertIn("are not rhythm units", r1)

    def test_r2_is_a_signal_not_a_target(self):
        r2 = entry("rhythm-stylometric.md", "R2")
        self.assertNotIn("Vary deliberately", r2)
        self.assertIn("never a length target", r2)
        self.assertIn("running prose only", r2)

    def test_r3_calibration_names_parallel_sets(self):
        self.assertIn("parallel sets", entry("rhythm-stylometric.md", "R3"))

    def test_r4_manufactured_surprise_removed(self):
        r4 = entry("rhythm-stylometric.md", "R4")
        self.assertNotIn("second or third word", r4)
        self.assertNotIn("unexpected analogies from real", r4)
        self.assertIn("never a rewrite target", r4)
        self.assertIn("one word for one concept", r4)

    def test_tone_kb_no_longer_mandates_variation(self):
        tone = text(TONE)
        self.assertNotIn("Vary sentence length", tone)
        self.assertIn("Let rhythm follow the content", tone)


class ListTellsRequireEmptiness(unittest.TestCase):
    def test_t7_is_about_checkability_not_symmetry(self):
        t7 = entry("structural-tells.md", "T7")
        self.assertIn("| low | judge |", t7)
        self.assertIn("*checkable*", t7)
        self.assertIn("evaluative verb", t7)
        self.assertIn("together with what was done to it", t7)
        self.assertIn("**Not the tell:** symmetry alone", t7)
        self.assertNotIn("The tell is the *symmetry*", t7)
        # Numeric text-property thresholds are gone once the tell is emptiness.
        self.assertNotIn("5+ consecutive", t7)
        self.assertNotIn("≤6-word", t7)

    def test_t7_keeps_its_positive_examples(self):
        t7 = entry("structural-tells.md", "T7")
        for ex in ("Optimized RandomX", "Unlock enterprise value",
                   "Fast setup / Clean design / Easy onboarding"):
            self.assertIn(ex, t7)

    def test_t5_t6_t9_t13_and_f2_exempt_parallel_sets(self):
        self.assertIn("parallel\n  set whose items carry checkable content",
                      entry("structural-tells.md", "T5"))
        t6 = entry("structural-tells.md", "T6")
        self.assertIn("closed set", t6)
        self.assertIn("never convert such a list to prose", t6)
        self.assertIn("So are parallel sets", entry("structural-tells.md", "T9"))
        self.assertIn("titles, card text, and list items",
                      entry("structural-tells.md", "T13"))
        self.assertIn("One consistent bold label on each item of a parallel set",
                      entry("punctuation-formatting.md", "F2"))

    def test_one_word_per_concept(self):
        self.assertIn("Pick one\n  replacement per concept",
                      entry("lexical-tells.md", "L1"))
        l3 = entry("lexical-tells.md", "L3")
        self.assertIn("Data-science caution", l3)
        self.assertIn("holdout vs control", l3)


class PolishWorkflowScoped(unittest.TestCase):
    def test_skill_steps_scope_rhythm_to_prose(self):
        body = text(POLISH)
        self.assertIn("uniform sentence length in running prose", body)
        self.assertIn("parallel set keep one shape", body)
        self.assertNotIn("8. Vary rhythm", body)

    def test_final_pass_keeps_parallel_structure(self):
        fp = text(FINAL)
        self.assertNotIn("- Repetition is gone.", fp)
        self.assertIn("Repeated content is gone", fp)
        self.assertNotIn("sentence lengths vary", fp)


def presets_section():
    body = text(PRESETS)
    m = re.search(r"^## Parallel items \(lists, feeds, cards, titles\)\n(.*?)(?=^## )",
                  body, re.M | re.S)
    if not m:
        raise AssertionError("Parallel items section missing from scenario-presets.md")
    return m.group(1)


class ParallelSetRules(unittest.TestCase):
    def test_definition_is_meaning_and_container_not_a_count(self):
        sec = presets_section()
        self.assertIn("each item answers\nthe same question", sec)
        self.assertIn("texts\ndelivered separately", sec)
        self.assertIn("decision / risk / ask", sec)
        self.assertNotRegex(sec, r"\b(?:three|3) or more\b")

    def test_permissions_not_obligations(self):
        sec = presets_section()
        self.assertIn("each only when it helps the reader scan", sec)
        self.assertIn("Leave a set alone when it already scans", sec)
        self.assertIn("the distinguishing word wins", sec)
        self.assertIn("Never add a heading or lead-in", sec)
        self.assertIn("In `edit` mode headings are preserved", sec)

    def test_invariants(self):
        sec = presets_section()
        self.assertIn('"investigating" never\n  becomes "fixed"', sec)
        self.assertIn("The actor is dropped only when the heading or lead-in states it", sec)
        self.assertNotIn("or doesn't matter", sec)
        self.assertIn("- Item order.", sec)
        self.assertIn("do not swap in stronger-sentiment verbs", sec)

    def test_light_edit_keeps_its_permissions(self):
        sec = presets_section()
        self.assertIn("`light-edit`: no list-structure changes", sec)
        self.assertIn("Everything light-edit already allows\n  stays allowed", sec)
        self.assertIn("We fixed the login bug", sec)
        self.assertIn("bullet markers", sec)

    def test_skill_points_to_the_section(self):
        self.assertIn('"Parallel items"', text(POLISH))

    def test_fixture_pairing(self):
        import json
        passes = {f["id"]: f for f in json.loads((FIX / "fixtures.json").read_text(encoding="utf-8"))["fixtures"]}
        fails = {f["id"]: f for f in json.loads((FIX / "fixtures_fail.json").read_text(encoding="utf-8"))["fixtures"]}
        clean = passes["lists-01-status-clean-en"]
        self.assertEqual(clean["before"], clean["after"])
        for fid in ("fail-lists-recast-en", "fail-lists-status-inflated-en"):
            self.assertEqual(fails[fid]["before"], clean["before"])
            self.assertEqual(fails[fid]["fail_dimension"], "meaning_preserved")
        self.assertEqual(fails["fail-lists-status-inflated-en"]["fidelity_class"], "status")


CONTRACT = ROOT / "skills" / "comms-polish" / "references" / "audit-report-contract.md"


class ConsistencyIsReportOnly(unittest.TestCase):
    def test_final_pass_checks_parallel_slots(self):
        fp = text(FINAL)
        self.assertIn("Check five things", fp)
        self.assertIn("carry\n    the same slots (n, interval, baseline, unit)", fp)
        self.assertIn("only when the metrics are comparable", fp)
        self.assertIn("Never fill a missing slot, delete the extra one, or pick a winner", fp)

    def test_notes_block_has_exactly_four_classes(self):
        body = text(POLISH)
        self.assertIn("exactly four classes of item", body)
        for cls in ("evidence flags", "alignment changes", "decision-gap flags",
                    "consistency conflicts"):
            self.assertIn(cls, body)
        self.assertNotIn("missing-evidence / unsupported-claim flags — nothing else", body)

    def test_review_reports_gaps_in_their_own_section(self):
        c = text(CONTRACT)
        self.assertIn("`## Consistency and evidence gaps` — optional, report-only", c)
        self.assertIn("carry no catalog id and no Fix", c)
        self.assertIn("never report it in both places", c)


class ConnectivesAreClusterOnly(unittest.TestCase):
    def test_h7_connective_subsection(self):
        h7 = entry("hedging-filler.md", "H7")
        self.assertIn("**Connective openers (cluster only).**", h7)
        self.assertIn("A single use is never a finding.", h7)
        self.assertIn("formal, legal, and academic register", h7)
        self.assertIn("gate\n    question 5", h7)
        self.assertIn("tenex", h7)

    def test_registry_count_unchanged(self):
        # A sub-section, not a new id: the 75-entry registry stays as it was.
        idx = text(PATTERNS / "00-index.md")
        self.assertNotIn("| H7b |", idx)


class Attribution(unittest.TestCase):
    def test_ideas_only_sources_are_credited_without_claiming_a_license(self):
        notice = text(NOTICE)
        self.assertIn("### Ideas referenced, not absorbed (no text copied)", notice)
        self.assertIn("fsdatalab.github.io/blog/agent-text-at-scale", notice)
        self.assertIn("Rights reserved", notice)
        legend = text(PATTERNS / "00-index.md")
        self.assertIn("| `fsdatalab` |", legend)
        self.assertIn("| `tenex` |", legend)


if __name__ == "__main__":
    unittest.main()
