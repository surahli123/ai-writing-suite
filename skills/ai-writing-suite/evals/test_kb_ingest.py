"""Unit tests for the fork KB ingestion tooling (`tools/kb_ingest.py` +
`tools/kb_validate.py`).

WHY this exists: the drop-in step — a company exports its playbook and shapes it
into the KB contract — is the product's whole adoption funnel. These tests pin
the tooling's guarantees so a regression there (a non-idempotent ingest, a
silent clobber, a validator that stops catching a broken KB) turns red under
`run_all.sh`, not on the company's first day.

All fixtures are synthetic and live in tempdirs; the shipped `_shared/knowledge/`
KB is never touched. Stdlib-only (unittest, tempfile). Collected automatically by
`python3 -m unittest discover -p 'test_*.py'`.
"""

import os
import sys
import tempfile
import unittest

# evals/ -> suite root -> tools/. Put tools/ on the path so we can import the
# ingestion tooling the same way test_kb_wiki.py imports kb_lint from evals/.
_HERE = os.path.dirname(os.path.abspath(__file__))
_TOOLS = os.path.normpath(os.path.join(_HERE, "..", "tools"))
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

import kb_ingest      # noqa: E402
import kb_validate    # noqa: E402


# ── Fixture builders ────────────────────────────────────────────────────────
def _write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _clean_export(src):
    """3 well-formed pages that share the token 'writing' (so each gets >=2
    bidirectional related links) — a mixed markdown + Confluence-HTML batch."""
    _write(os.path.join(src, "clear-emails.md"),
           "# Writing Clear Emails\n\n"
           "Keep each email focused on one decision the reader must make.\n\n"
           "## Subject lines\nState the ask in the subject.\n\n"
           "## Length\nShort emails get answered faster.\n")
    _write(os.path.join(src, "status-updates.md"),
           "# Writing Status Updates\n\n"
           "Lead a status update with the headline before the detail.\n\n"
           "## Structure\nPut the decision or blocker first.\n\n"
           "## Cadence\nSend updates on a predictable schedule.\n")
    _write(os.path.join(src, "exec-writing.html"),
           "<html><head><title>Writing for Executives : DS Space</title></head>"
           "<body><h1>Writing for Executives</h1>"
           "<p>An executive reader wants the recommendation and the risk.</p>"
           "<h2>Audience</h2><ul><li>Assume no context</li>"
           "<li>Lead with the decision</li></ul></body></html>")


def _broken_export(src):
    """A page with no title, an empty page, and two pages with the same title
    (duplicate topic)."""
    _write(os.path.join(src, "a-notitle.md"),
           "Just some body text with no heading at all here.\n")
    _write(os.path.join(src, "b-empty.md"), "")
    _write(os.path.join(src, "tone1.md"), "# Tone Guide\n\nUse a plain register.\n")
    _write(os.path.join(src, "tone2.md"), "# Tone Guide\n\nAvoid hype words.\n")


def _entry_files(kb):
    return sorted(f for f in os.listdir(kb)
                  if f.endswith(".md") and f not in kb_ingest.NON_ENTRY_FILES)


def _snapshot(kb):
    """path -> bytes for every file in a KB dir (for idempotency comparison)."""
    out = {}
    for name in sorted(os.listdir(kb)):
        p = os.path.join(kb, name)
        if os.path.isfile(p):
            with open(p, encoding="utf-8") as fh:
                out[name] = fh.read()
    return out


# ── Ingest: clean path ──────────────────────────────────────────────────────
class CleanIngest(unittest.TestCase):
    def test_ingests_and_validates_pass(self):
        with tempfile.TemporaryDirectory() as d:
            src, kb = os.path.join(d, "exp"), os.path.join(d, "kb")
            os.makedirs(src)
            _clean_export(src)
            report = kb_ingest.ingest(src, kb)

            self.assertEqual(len(report["written"]), 3, report)
            self.assertEqual(report["errors"], [])
            self.assertEqual(_entry_files(kb),
                             ["writing-clear-emails.md",
                              "writing-for-executives.md",
                              "writing-status-updates.md"])
            self.assertTrue(os.path.isfile(os.path.join(kb, "INDEX.md")))

            # A clean export leaves NO in-file TODO markers.
            for f in _entry_files(kb):
                with open(os.path.join(kb, f), encoding="utf-8") as fh:
                    self.assertNotIn("TODO", fh.read(), f + " should be TODO-free")

            # And the freshly ingested KB validates PASS end-to-end.
            all_ok, results = kb_validate.validate(kb)
            self.assertTrue(all_ok,
                            "clean ingest should validate PASS:\n" +
                            "\n".join(f"{lbl}: {probs}"
                                      for lbl, ok, probs in results if not ok))


# ── Ingest: broken path ─────────────────────────────────────────────────────
class BrokenIngest(unittest.TestCase):
    def test_produces_todos_and_fails_validation(self):
        with tempfile.TemporaryDirectory() as d:
            src, kb = os.path.join(d, "exp"), os.path.join(d, "kb")
            os.makedirs(src)
            _broken_export(src)
            report = kb_ingest.ingest(src, kb)

            # Duplicate topic did not clobber: two distinct tone files exist.
            self.assertIn("tone-guide.md", _entry_files(kb))
            self.assertIn("tone-guide-2.md", _entry_files(kb))

            # The run report surfaces the gaps (missing title, empty, duplicate).
            joined = "\n".join(report["todos"])
            self.assertIn("missing title", joined)
            self.assertIn("no summary", joined)
            self.assertIn("duplicate topic", joined)

            # In-file TODO markers were written for each gap.
            todo_files = [f for f in _entry_files(kb)
                          if "TODO" in _read(os.path.join(kb, f))]
            self.assertTrue(todo_files, "expected TODO markers in broken entries")

            # Validation FAILS on the unreviewed KB.
            all_ok, _ = kb_validate.validate(kb)
            self.assertFalse(all_ok, "broken ingest must fail validation")


# ── Ingest: idempotency + no-clobber ────────────────────────────────────────
class IngestSafety(unittest.TestCase):
    def test_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            src, kb = os.path.join(d, "exp"), os.path.join(d, "kb")
            os.makedirs(src)
            _clean_export(src)
            kb_ingest.ingest(src, kb)
            first = _snapshot(kb)
            kb_ingest.ingest(src, kb)        # re-run onto the same output
            self.assertEqual(first, _snapshot(kb),
                             "re-ingesting the same input must be byte-identical")

    def test_no_clobber_without_force(self):
        with tempfile.TemporaryDirectory() as d:
            src, kb = os.path.join(d, "exp"), os.path.join(d, "kb")
            os.makedirs(src)
            _clean_export(src)
            kb_ingest.ingest(src, kb)
            target = os.path.join(kb, "writing-clear-emails.md")
            _write(target, "# HAND EDITED\n\nlocal change\n")

            # Without --force the hand edit survives.
            kb_ingest.ingest(src, kb, force=False)
            with open(target, encoding="utf-8") as fh:
                self.assertIn("HAND EDITED", fh.read())

            # With --force it is regenerated.
            kb_ingest.ingest(src, kb, force=True)
            with open(target, encoding="utf-8") as fh:
                self.assertNotIn("HAND EDITED", fh.read())


# ── Validator: each check can fail on a planted defect ──────────────────────
class ValidatorCatchesDefects(unittest.TestCase):
    def _valid_kb(self, d):
        """Ingest the clean export into a tempdir -> a KB that validates PASS,
        then hand it back for a test to plant one defect."""
        src, kb = os.path.join(d, "exp"), os.path.join(d, "kb")
        os.makedirs(src)
        _clean_export(src)
        kb_ingest.ingest(src, kb)
        ok, _ = kb_validate.validate(kb)
        self.assertTrue(ok, "baseline KB should be clean before planting a defect")
        return kb

    def test_orphan_index_row_fails_sync(self):
        with tempfile.TemporaryDirectory() as d:
            kb = self._valid_kb(d)
            with open(os.path.join(kb, "INDEX.md"), "a", encoding="utf-8") as fh:
                fh.write("| `ghost.md` | orphan row | ghost, missing |\n")
            ok, problems = kb_validate.kb_lint.check_index_sync(kb)
            self.assertFalse(ok)
            self.assertTrue(any("ghost.md" in p for p in problems), problems)

    def test_entry_missing_keywords_fails(self):
        with tempfile.TemporaryDirectory() as d:
            kb = self._valid_kb(d)
            idx = os.path.join(kb, "INDEX.md")
            # Blank out the keywords cell of the first entry row.
            lines = []
            for ln in _read(idx).splitlines():
                if ln.startswith("| `writing-clear-emails.md` |"):
                    parts = ln.split("|")
                    parts[3] = "  "            # keywords column -> empty
                    ln = "|".join(parts)
                lines.append(ln)
            _write(idx, "\n".join(lines) + "\n")
            ok, problems = kb_validate.kb_lint.check_keywords(kb)
            self.assertFalse(ok)
            self.assertTrue(any("writing-clear-emails.md" in p for p in problems),
                            problems)

    def test_one_way_related_link_fails_bidirectional(self):
        with tempfile.TemporaryDirectory() as d:
            kb = self._valid_kb(d)
            # Remove the back-link: strip status-updates from clear-emails' footer.
            target = os.path.join(kb, "writing-clear-emails.md")
            kept = [ln for ln in _read(target).splitlines()
                    if "writing-status-updates.md" not in ln]
            _write(target, "\n".join(kept) + "\n")
            ok, problems = kb_validate.kb_lint.check_bidirectional(kb)
            self.assertFalse(ok)
            self.assertTrue(
                any("writing-status-updates.md" in p and "writing-clear-emails.md" in p
                    for p in problems), problems)


if __name__ == "__main__":
    unittest.main()
