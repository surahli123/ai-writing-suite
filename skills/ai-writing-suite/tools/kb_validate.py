#!/usr/bin/env python3
"""Pre-flight validator a company fork runs AFTER dropping in its playbook and
BEFORE first use.

WHY this exists: `kb_ingest.py` shapes an export into KB entries but deliberately
leaves `TODO:` markers wherever it could not infer safely (keywords, summaries,
cross-links). If a fork ships that KB unreviewed, `comms-qa` retrieval degrades
silently — a dead INDEX row, an entry with no keywords, a one-way related link,
or a leftover TODO all break retrieval with NO runtime error. This validator
turns every one of those into a red check with a `file:line`, so the failure
surfaces on the operator's screen, not in a wrong answer on day one.

It is the ingestion-time companion to `evals/kb_lint.py`: kb_lint enforces the
add-an-entry structural contract; this tool IMPORTS and reuses kb_lint's four
checks (never copies them) and ADDS the ingestion-specific ones:

  * INDEX rows resolve to files and vice versa      (via kb_lint.check_index_sync)
  * `## Related entries` validity + bidirectionality (via kb_lint.check_related_*)
  * every entry has non-empty Keywords               (via kb_lint.check_keywords)
  * every entry has a non-empty Summary              (added here, with file:line)
  * every entry's OWN kb-entry-meta header is non-blank (added here — catches a
    blank file-level Keywords/Summary that an INDEX-only check can't see)
  * INDEX.md agrees with each entry's own kb-entry-meta header (added here —
    this is the check that catches a stale/desynced INDEX row: one regenerated
    from a DIFFERENT page than the one that actually produced the on-disk file)
  * NO `TODO:` markers left anywhere                 (added here, with file:line)
  * retrieval smoke: each entry's own Keywords must retrieve THAT entry, and
    must do so UNIQUELY (not merely tie-and-win-by-table-order against another
    entry) through the exact matching logic smoke_test.py uses (imports
    smoke_test.retrieve)

Output: a human-readable PASS/FAIL report; exit nonzero on any failure.
Stdlib only. Run:  python3 tools/kb_validate.py <knowledge-dir>
"""

import os
import re
import sys

# tools/ -> suite root -> evals/. Put evals/ on the path so we can import the
# real kb_lint + smoke_test and REUSE their logic rather than reimplement it.
_HERE = os.path.dirname(os.path.abspath(__file__))
_EVALS = os.path.normpath(os.path.join(_HERE, "..", "evals"))
if _EVALS not in sys.path:
    sys.path.insert(0, _EVALS)

import kb_lint      # noqa: E402  (path set above)
import smoke_test   # noqa: E402
import kb_ingest     # noqa: E402  (same tools/ dir as this file)

NON_ENTRY_FILES = kb_lint.NON_ENTRY_FILES


def _norm_ws(s):
    """Collapse whitespace + strip, for tolerant text comparison."""
    return re.sub(r"\s+", " ", s).strip()


def _kw_set(s):
    """A comma-separated keyword string -> a lowercased set of terms, so
    comparisons are robust to ordering/whitespace differences."""
    return {t.strip().lower() for t in s.split(",") if t.strip()}


# ── Row parsing with line numbers (for file:line reporting) ─────────────────
def _index_rows_with_lines(kb):
    """Return [{file, summary, keywords, line}] parsed from INDEX.md."""
    rows = []
    path = os.path.join(kb, "INDEX.md")
    if not os.path.isfile(path):
        return rows
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            m = re.match(r"\|\s*`([^`]+\.md)`\s*\|(.+?)\|(.+?)\|\s*$", line)
            if m:
                rows.append({"file": m.group(1).strip(),
                             "summary": m.group(2).strip(),
                             "keywords": m.group(3).strip(),
                             "line": n})
    return rows


# ── Added checks (each returns (ok, problems) like kb_lint) ─────────────────
def check_summary_non_empty(kb):
    """Every INDEX row has a non-empty Summary cell (and it is not a TODO stub).

    kb_lint already guards the Keywords column; Summary is the other retrieval
    signal (intent overlap / tie-break), so an empty or placeholder Summary is a
    silent recall hole the same way."""
    problems = []
    idx = os.path.join(kb, "INDEX.md")
    for r in _index_rows_with_lines(kb):
        if not r["summary"] or r["summary"].upper().startswith("TODO"):
            problems.append(idx + ":" + str(r["line"]) +
                            " INDEX row for " + r["file"] +
                            " has empty/TODO Summary")
    return (not problems), problems


def check_no_todo_markers(kb):
    """No `TODO` markers left anywhere in the KB (entries or INDEX).

    kb_ingest writes `TODO:` wherever it could not infer safely; shipping one
    means an unreviewed gap. Reported with file:line so the operator jumps
    straight to it."""
    problems = []
    for name in sorted(os.listdir(kb)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(kb, name)
        with open(path, encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                if "TODO" in line:
                    problems.append(path + ":" + str(n) + " " + line.strip())
    return (not problems), problems


def check_entry_meta_non_empty(kb):
    """Every entry's OWN `kb-entry-meta` header (if present) has non-blank
    Keywords and Summary fields.

    kb_lint.check_keywords and check_summary_non_empty above both read
    INDEX.md's cells — neither looks at the file's own declared metadata. A
    hand edit (or a bug) that blanks a file's `Keywords:`/`Summary:` line while
    the INDEX row still shows old, unrelated text would pass every check above
    (Finding 6 — "blank entry metadata passes validation"). This one reads the
    file directly, so a blank header fails here regardless of what INDEX
    says."""
    problems = []
    for name in sorted(kb_lint._entry_files(kb)):
        path = os.path.join(kb, name)
        meta = kb_ingest.read_entry_meta(path)
        if meta is None:
            continue  # no kb-entry-meta header - not a kb_ingest-produced entry
        if not meta["keywords_raw"]:
            problems.append(path + ":0 kb-entry-meta Keywords is blank")
        if not meta["summary"]:
            problems.append(path + ":0 kb-entry-meta Summary is blank")
    return (not problems), problems


def check_index_matches_entry_meta(kb):
    """Every entry's own `kb-entry-meta` header agrees with its INDEX.md row.

    This is the check that catches the Finding-1 collision class directly: a
    stale/mismatched INDEX row (regenerated from a DIFFERENT incoming page than
    the one that produced the on-disk file) is otherwise invisible to every
    other check here — they all compare existence/shape, never row-fields vs.
    the entry's own declared content. Only entries that carry a kb-entry-meta
    header are checked; hand-authored entries with no such header (e.g. the
    shipped generic KB) have nothing to compare against and are skipped.

    Summary must match EXACTLY (normalized whitespace) — a desync always swaps
    in a wholly different one-line summary, so exact match alone catches it.
    Keywords use a SUBSET relation instead (every word the file's own header
    declares must appear in the INDEX row, but the row may carry EXTRA words):
    the KB's own onboarding docs (README.md "Wiki conventions") explicitly
    support a human hand-adding alias keywords straight into an INDEX row
    without touching the entry file — exact-set equality would wrongly flag
    that legitimate enrichment as a desync. A genuine desync (the row replaced
    with an unrelated page's keywords) still fails: the file's real keywords
    are then absent from the row entirely, violating the subset relation."""
    problems = []
    rows = {r["file"]: r for r in _index_rows_with_lines(kb)}
    idx_path = os.path.join(kb, "INDEX.md")
    for name in sorted(kb_lint._entry_files(kb)):
        path = os.path.join(kb, name)
        meta = kb_ingest.read_entry_meta(path)
        if meta is None:
            continue
        row = rows.get(name)
        if row is None:
            continue  # INDEX<->directory sync check already reports this
        if _norm_ws(row["summary"]) != _norm_ws(meta["summary"]):
            problems.append(
                idx_path + ":" + str(row["line"]) + " INDEX Summary for " +
                name + " does not match its kb-entry-meta Summary "
                "('" + row["summary"] + "' vs '" + meta["summary"] + "')")
        meta_kw = _kw_set(meta["keywords_raw"])
        row_kw = _kw_set(row["keywords"])
        if not meta_kw <= row_kw:
            problems.append(
                idx_path + ":" + str(row["line"]) + " INDEX Keywords for " +
                name + " is missing word(s) its kb-entry-meta declares "
                "(missing: " + ", ".join(sorted(meta_kw - row_kw)) + ")")
    return (not problems), problems


def check_retrieval_smoke(kb):
    """Each entry's OWN Keywords must retrieve THAT entry, UNIQUELY.

    Reuses the exact matching logic smoke_test.py uses (smoke_test.load_index +
    smoke_test.retrieve) — no reimplementation. Two failure modes are checked:

    (a) an entry's keyword string resolves to a DIFFERENT entry (or nothing) —
        retrieval for that topic is broken.
    (b) an entry's keyword string TIES another entry's score and only "wins"
        because of INDEX table order (Finding 2 — retrieval-smoke false-pass on
        shared keywords). A tie means the entry is not uniquely identified by
        its own keywords; smoke_test.retrieve()'s strict `>` comparison would
        silently pick whichever entry comes first in the table, which can mask
        the fact that a query for THIS entry would just as validly resolve to
        the other one. Both members of a tie are flagged, not just whichever
        one loses the position-dependent tie-break.

    This is the ingestion-time analogue of the shipped-KB smoke test, run over
    the fork KB."""
    problems = []
    # smoke_test.load_index() reads its module-level INDEX_PATH. Point it at the
    # target KB for the duration of this check, then restore it — genuine reuse
    # of the shipped retrieval code over an arbitrary KB dir.
    saved = smoke_test.INDEX_PATH
    smoke_test.INDEX_PATH = os.path.join(kb, "INDEX.md")
    try:
        entries = smoke_test.load_index()
        if not entries:
            return False, [os.path.join(kb, "INDEX.md") +
                           ":0 no entries parsed from INDEX.md"]
        for e in entries:
            q = set(e["keywords"])
            path = os.path.join(kb, e["file"])
            got, overlap = smoke_test.retrieve(", ".join(sorted(q)), entries)
            if got != e["file"]:
                problems.append(
                    path + ":0 own keywords retrieve '" + str(got) +
                    "' not '" + e["file"] + "' (overlap=" + str(overlap) + ")")
                continue
            # e "won" the retrieval — now check whether it won UNIQUELY, or
            # only by table-order privilege over a genuine tie.
            e_terms = e["keywords"] | e["summary_kw"]
            e_score = (len(q & e_terms), len(q & e["summary_kw"]))
            for g in entries:
                if g is e:
                    continue
                g_terms = g["keywords"] | g["summary_kw"]
                g_score = (len(q & g_terms), len(q & g["summary_kw"]))
                if g_score >= e_score:
                    problems.append(
                        path + ":0 own keywords are shadowed by '" +
                        g["file"] + "' (self=" + str(e_score) + ", shadow=" +
                        str(g_score) + ") — not uniquely retrievable")
                    break
    finally:
        smoke_test.INDEX_PATH = saved
    return (not problems), problems


# Ordered registry: kb_lint's four checks first (reused), then the ingestion
# checks. Each entry: (label, fn(kb) -> (ok, problems)).
CHECKS = [
    ("INDEX <-> directory sync (kb_lint)", kb_lint.check_index_sync),
    ("Related-entries validity (kb_lint)", kb_lint.check_related_entries),
    ("Bidirectionality (kb_lint)", kb_lint.check_bidirectional),
    ("Keywords non-empty (kb_lint)", kb_lint.check_keywords),
    ("Summary non-empty", check_summary_non_empty),
    ("Entry metadata non-empty (file-level)", check_entry_meta_non_empty),
    ("INDEX matches entry metadata", check_index_matches_entry_meta),
    ("No TODO markers left", check_no_todo_markers),
    ("Retrieval smoke (own keywords -> own entry, unique)", check_retrieval_smoke),
]


def validate(kb):
    """Run every check. Return (all_ok, results) where results is
    [(label, ok, problems)]."""
    results = []
    for label, fn in CHECKS:
        ok, problems = fn(kb)
        results.append((label, ok, problems))
    return all(ok for _, ok, _ in results), results


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    kb = os.path.abspath(argv[0]) if argv else kb_lint.DEFAULT_KB
    if not os.path.isdir(kb):
        print("FAIL: knowledge dir not found: " + kb, file=sys.stderr)
        return 1

    n_entries = len(kb_lint._entry_files(kb))
    print("KB validate — " + kb)
    print("(" + str(n_entries) + " entry file(s))\n")

    all_ok, results = validate(kb)
    failed = 0
    for label, ok, problems in results:
        print("[" + ("PASS" if ok else "FAIL") + "] " + label)
        if not ok:
            failed += 1
            for p in problems:
                print("       - " + p)

    print()
    if all_ok:
        print("PASS — KB is ready for first use (" + str(len(CHECKS)) +
              " checks).")
        return 0
    print("FAIL — " + str(failed) + "/" + str(len(CHECKS)) +
          " check(s) failed. Fix the items above before first use.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
