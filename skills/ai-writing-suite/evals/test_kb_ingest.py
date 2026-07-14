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
import re
import sys
import tempfile
import unittest
from unittest import mock

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


# ── Review round: title collision with an EXISTING entry (Finding 1) ────────
class TitleCollisionWithExistingEntry(unittest.TestCase):
    """A new page's slug collides with an EXISTING file that was NOT produced
    by ingesting this same source (e.g. a shipped/hand-authored entry). Must
    never merge: the existing file + its INDEX row stay untouched; the new
    page is written under an auto-renamed filename with a duplicate TODO."""

    def test_collision_does_not_desync_existing_entry(self):
        with tempfile.TemporaryDirectory() as d:
            src, kb = os.path.join(d, "exp"), os.path.join(d, "kb")
            os.makedirs(src)
            os.makedirs(kb)

            # Simulate a SHIPPED / hand-authored entry already in the KB — no
            # kb-entry-meta header, no provenance line (the shipped generic-KB
            # shape, e.g. clarity.md/tone.md).
            existing_file = os.path.join(kb, "tone-and-voice.md")
            _write(existing_file,
                   "# Tone and Voice\n\nHouse tone: warm but precise.\n")
            existing_row = ("| `tone-and-voice.md` | House tone guidance. "
                            "| tone, voice, house style |")
            _write(os.path.join(kb, "INDEX.md"),
                   "# Knowledge Base — Navigation Index\n\n"
                   "## Entries\n\n"
                   "| Entry file | Summary (one line) | Keywords / aliases |\n"
                   "| --- | --- | --- |\n" + existing_row + "\n")

            # A brand-new, UNRELATED page whose title slugs to the same name.
            _write(os.path.join(src, "kubernetes.md"),
                   "# Tone And Voice\n\n"
                   "Kubernetes autoscaling notes for the platform team.\n\n"
                   "## Scaling\nSet resource requests before enabling HPA.\n")

            before_existing = _read(existing_file)
            report = kb_ingest.ingest(src, kb)

            # The shipped file is byte-for-byte untouched.
            self.assertEqual(_read(existing_file), before_existing)
            # Its INDEX row is byte-for-byte untouched — no desync.
            self.assertIn(existing_row, _read(os.path.join(kb, "INDEX.md")))

            # The new page landed under a RENAMED file, not the collided name.
            self.assertIn("tone-and-voice-2.md", report["written"])
            self.assertTrue(os.path.isfile(os.path.join(kb, "tone-and-voice-2.md")))
            self.assertIn("kubernetes",
                          _read(os.path.join(kb, "tone-and-voice-2.md")).lower())
            self.assertIn("kubernetes",
                          _read(os.path.join(kb, "INDEX.md")).lower())

            # A duplicate-topic TODO was raised for the human to review.
            self.assertTrue(
                any("collided" in t for t in report["todos"]), report["todos"])

    def test_index_matches_entry_meta_catches_planted_desync(self):
        """Finding 1c positive control: if a row DOES drift from its entry's
        own kb-entry-meta header (simulating the pre-fix bug directly), the
        new validator check must catch it."""
        with tempfile.TemporaryDirectory() as d:
            src, kb = os.path.join(d, "exp"), os.path.join(d, "kb")
            os.makedirs(src)
            _clean_export(src)
            kb_ingest.ingest(src, kb)
            ok, _ = kb_validate.validate(kb)
            self.assertTrue(ok, "baseline should be clean before planting a desync")

            # Plant the exact desync class Finding 1 describes: rewrite the
            # INDEX row for one entry to a DIFFERENT page's content, leaving
            # the entry file (and its kb-entry-meta header) untouched.
            idx = os.path.join(kb, "INDEX.md")
            lines = []
            for ln in _read(idx).splitlines():
                if ln.startswith("| `writing-clear-emails.md` |"):
                    ln = ("| `writing-clear-emails.md` | Kubernetes autoscaling "
                          "notes. | kubernetes, autoscaling, hpa |")
                lines.append(ln)
            _write(idx, "\n".join(lines) + "\n")

            ok, results = kb_validate.validate(kb)
            self.assertFalse(ok)
            by_label = {lbl: probs for lbl, ok2, probs in results}
            mismatch = by_label["INDEX matches entry metadata"]
            self.assertTrue(
                any("writing-clear-emails.md" in p for p in mismatch), mismatch)


# ── Finding 2, bullet 1: no-force re-ingest split-brain ─────────────────────
class ReingestPreservesIndexRow(unittest.TestCase):
    def test_no_force_reingest_does_not_split_brain(self):
        with tempfile.TemporaryDirectory() as d:
            src, kb = os.path.join(d, "exp"), os.path.join(d, "kb")
            os.makedirs(src)
            _clean_export(src)
            kb_ingest.ingest(src, kb)

            file_path = os.path.join(kb, "writing-clear-emails.md")
            idx_path = os.path.join(kb, "INDEX.md")
            before_file = _read(file_path)
            before_index = _read(idx_path)

            # Modify the SOURCE page (same title -> same filename) so a fresh
            # parse would produce DIFFERENT keywords/summary than what's on
            # disk — simulating a stale/edited export re-run without --force.
            _write(os.path.join(src, "clear-emails.md"),
                   "# Writing Clear Emails\n\n"
                   "Kubernetes autoscaling notes for the platform team.\n\n"
                   "## Scaling\nSet resource requests before enabling HPA.\n")

            kb_ingest.ingest(src, kb, force=False)

            # The on-disk file is untouched (Pass 3 skip).
            self.assertEqual(_read(file_path), before_file)
            # The INDEX row must ALSO be untouched — this is the split-brain
            # class Finding 2 flags: previously the row silently regenerated
            # from the modified source even though the file was skipped.
            self.assertEqual(_read(idx_path), before_index)
            self.assertNotIn("kubernetes", _read(idx_path).lower())


# ── Finding 2, bullet 2: a human's hand-edited INDEX row survives re-ingest ─
class HandEditedIndexRowPreserved(unittest.TestCase):
    def test_hand_edit_survives_reingest(self):
        with tempfile.TemporaryDirectory() as d:
            src, kb = os.path.join(d, "exp"), os.path.join(d, "kb")
            os.makedirs(src)
            _clean_export(src)
            kb_ingest.ingest(src, kb)

            idx_path = os.path.join(kb, "INDEX.md")
            lines = []
            for ln in _read(idx_path).splitlines():
                if ln.startswith("| `writing-clear-emails.md` |"):
                    ln = re.sub(r"\s*\|\s*$", ", email etiquette |", ln)
                lines.append(ln)
            _write(idx_path, "\n".join(lines) + "\n")

            # Re-ingest the SAME unmodified source, without --force.
            kb_ingest.ingest(src, kb, force=False)

            self.assertIn("email etiquette", _read(idx_path))

            # A hand-added ALIAS keyword is legitimate enrichment (the KB's own
            # README documents hand-editing an INDEX row), not a desync — it
            # must not trip "INDEX matches entry metadata" (that check uses a
            # subset relation for exactly this reason: the file's own declared
            # keywords must still all be present in the row, but the row is
            # allowed extra words).
            ok, results = kb_validate.validate(kb)
            by_label = {lbl: (ok2, probs) for lbl, ok2, probs in results}
            meta_ok, meta_problems = by_label["INDEX matches entry metadata"]
            self.assertTrue(meta_ok, meta_problems)


# ── Finding 2, bullet 3: retrieval-smoke false-pass on shared keywords ──────
class RetrievalSmokeTieDetection(unittest.TestCase):
    def test_shared_keyword_tie_is_flagged_for_both_entries(self):
        with tempfile.TemporaryDirectory() as d:
            kb = os.path.join(d, "kb")
            os.makedirs(kb)
            _write(os.path.join(kb, "INDEX.md"),
                   "# Knowledge Base — Navigation Index\n\n"
                   "## Entries\n\n"
                   "| Entry file | Summary (one line) | Keywords / aliases |\n"
                   "| --- | --- | --- |\n"
                   "| `alpha.md` | Shared common topic guidance. "
                   "| shared, common, topic, guidance |\n"
                   "| `beta.md` | Shared common topic guidance. "
                   "| shared, common, topic, guidance |\n")
            _write(os.path.join(kb, "alpha.md"),
                   "# Alpha\n\nAlpha body.\n\n## Related entries\n\n"
                   "- `beta.md`\n- `beta.md`\n")
            _write(os.path.join(kb, "beta.md"),
                   "# Beta\n\nBeta body.\n\n## Related entries\n\n"
                   "- `alpha.md`\n- `alpha.md`\n")

            ok, problems = kb_validate.check_retrieval_smoke(kb)
            self.assertFalse(ok, "identical keyword sets must not silently pass")
            joined = "\n".join(problems)
            self.assertIn("alpha.md", joined)
            self.assertIn("beta.md", joined)
            self.assertIn("shadowed", joined)


# ── Finding 2, bullet 4: HTML table cells must not fuse ─────────────────────
class HTMLTableCellSeparation(unittest.TestCase):
    def test_table_cells_do_not_fuse(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "page.html")
            _write(path,
                   "<html><head><title>Table Page</title></head><body>"
                   "<h1>Table Page</h1>"
                   "<table><tr><td>Foo</td><td>Bar</td></tr></table>"
                   "</body></html>")
            title, body = kb_ingest.parse_html_export(path)
            self.assertEqual(title, "Table Page")
            self.assertNotIn("FooBar", body)
            self.assertIn("Foo", body)
            self.assertIn("Bar", body)


# ── Finding 2, bullet 5: non-ASCII titles get a deterministic fallback slug ─
class UnicodeTitleFallbackSlug(unittest.TestCase):
    def test_distinct_cjk_titles_do_not_collide(self):
        with tempfile.TemporaryDirectory() as d:
            src, kb = os.path.join(d, "exp"), os.path.join(d, "kb")
            os.makedirs(src)
            _write(os.path.join(src, "p1.md"), "# 中文标题一\n\n这是第一页的内容说明。\n")
            _write(os.path.join(src, "p2.md"), "# 中文标题二\n\n这是第二页的内容说明。\n")

            report = kb_ingest.ingest(src, kb)
            files = _entry_files(kb)
            self.assertEqual(len(files), 2, files)
            self.assertNotEqual(files[0], files[1])
            self.assertTrue(all(f.startswith("untitled-") for f in files), files)
            self.assertTrue(
                any("could not derive an ASCII filename" in t
                    for t in report["todos"]), report["todos"])

    def test_fallback_slug_is_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "exp")
            kb1, kb2 = os.path.join(d, "kb1"), os.path.join(d, "kb2")
            os.makedirs(src)
            _write(os.path.join(src, "p1.md"), "# 中文标题一\n\n这是内容。\n")
            kb_ingest.ingest(src, kb1)
            kb_ingest.ingest(src, kb2)
            self.assertEqual(_entry_files(kb1), _entry_files(kb2))


# ── Finding 2, bullet 6: blank entry metadata must fail validation ──────────
class BlankEntryMetadataDetection(unittest.TestCase):
    def test_blank_file_level_keywords_fails(self):
        with tempfile.TemporaryDirectory() as d:
            src, kb = os.path.join(d, "exp"), os.path.join(d, "kb")
            os.makedirs(src)
            _clean_export(src)
            kb_ingest.ingest(src, kb)
            ok, _ = kb_validate.validate(kb)
            self.assertTrue(ok)

            target = os.path.join(kb, "writing-clear-emails.md")
            # Blank the file's OWN Keywords line; the INDEX row is left as-is
            # (still valid) — exactly the gap Finding 6 describes: a check
            # that only reads INDEX.md would miss this entirely.
            lines = [("Keywords: " if ln.startswith("Keywords:") else ln)
                    for ln in _read(target).splitlines()]
            _write(target, "\n".join(lines) + "\n")

            ok, problems = kb_validate.check_entry_meta_non_empty(kb)
            self.assertFalse(ok)
            self.assertTrue(
                any("writing-clear-emails.md" in p and "Keywords" in p
                    for p in problems), problems)


# ── Finding 2, bullet 7: atomic writes — no partial state on a mid-run crash ─
class AtomicWriteSafety(unittest.TestCase):
    def test_failed_write_does_not_corrupt_existing_file(self):
        with tempfile.TemporaryDirectory() as d:
            dest = os.path.join(d, "x.md")
            kb_ingest._atomic_write(dest, "version1")
            with mock.patch("kb_ingest.os.replace", side_effect=OSError("boom")):
                with self.assertRaises(OSError):
                    kb_ingest._atomic_write(dest, "version2-CORRUPT")
            # The prior file must be untouched — write-then-replace never
            # exposes a half-written destination.
            self.assertEqual(_read(dest), "version1")

    def test_ingest_leaves_no_temp_files_behind(self):
        with tempfile.TemporaryDirectory() as d:
            src, kb = os.path.join(d, "exp"), os.path.join(d, "kb")
            os.makedirs(src)
            _clean_export(src)
            kb_ingest.ingest(src, kb)
            leftovers = [f for f in os.listdir(kb) if ".tmp-" in f]
            self.assertEqual(leftovers, [], leftovers)


# ── Finding 3 (minor): boilerplate headings excluded from keyword extraction ─
class BoilerplateHeadingExcluded(unittest.TestCase):
    def test_related_entries_heading_not_extracted_as_keyword(self):
        title = "Some Topic"
        body = ("Some prose about the topic.\n\n"
                "## Related entries\n\n- `other.md`\n")
        keywords = kb_ingest.extract_keywords(title, body)
        self.assertNotIn("related", keywords)
        self.assertNotIn("entries", keywords)


if __name__ == "__main__":
    unittest.main()
