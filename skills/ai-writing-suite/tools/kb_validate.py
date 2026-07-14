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
  * NO `TODO:` markers left anywhere                 (added here, with file:line)
  * retrieval smoke: each entry's own Keywords must retrieve THAT entry through
    the exact matching logic smoke_test.py uses      (imports smoke_test.retrieve)

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

NON_ENTRY_FILES = kb_lint.NON_ENTRY_FILES


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


def check_retrieval_smoke(kb):
    """Each entry's OWN Keywords must retrieve THAT entry.

    Reuses the exact matching logic smoke_test.py uses (smoke_test.load_index +
    smoke_test.retrieve) — no reimplementation. If an entry's keyword string
    resolves to a different entry (or to nothing), retrieval for that topic is
    broken: the keywords are too weak or collide with a neighbour. This is the
    ingestion-time analogue of the shipped-KB smoke test, run over the fork KB."""
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
            got, overlap = smoke_test.retrieve(", ".join(sorted(e["keywords"])),
                                               entries)
            if got != e["file"]:
                problems.append(
                    os.path.join(kb, e["file"]) +
                    ":0 own keywords retrieve '" + str(got) +
                    "' not '" + e["file"] + "' (overlap=" + str(overlap) + ")")
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
    ("No TODO markers left", check_no_todo_markers),
    ("Retrieval smoke (own keywords -> own entry)", check_retrieval_smoke),
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
