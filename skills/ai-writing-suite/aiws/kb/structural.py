"""The KB's add-an-entry structural contract (P2.5 KB wiki).

Moved unchanged from `evals/kb_lint.py` (architecture review 2026-07-13, item
5). `evals/kb_lint.py` is now a thin compatibility wrapper over this module —
see that file for the CLI entrypoint and why it still exists.

WHY this exists: the product promise is "a company drops in a markdown page
and edits a table — no retrieval engine to build" (design D5/D11). That
promise only holds if the add-an-entry contract is mechanically enforceable,
because a fork edits the KB by hand with no embeddings/build step to catch
mistakes. A typo in an INDEX row, a `## Related entries` link that points at a
deleted file, or a one-way link silently degrades retrieval with NO runtime
error — the agent just reads a worse index or a dead hop. This module turns
each of those silent failures into a red check, the same way
`aiws.kb.retrieval` guards the retrieval chain.

The four checks (each a function returning `(ok, problems)` so callers —
`tools/kb_validate.py`, `evals/test_kb_wiki.py` — can import and assert them
without shelling out):
  (a) check_index_sync       — INDEX rows <-> *.md files are 1:1, no orphans/rot.
  (b) check_related_entries  — every entry has a `## Related entries` footer with
                               >=2 links, no self-links, every target exists.
  (c) check_bidirectional    — A links B  =>  B links A (report each one-way link).
  (d) check_keywords         — every INDEX row's Keywords cell is non-empty.
"""

import os
import re
import sys

from aiws.kb.entries import DEFAULT_KB, NON_ENTRY_FILES, entry_files as _entry_files


# ── Parse helpers ──────────────────────────────────────────────────────────
def _index_rows(kb):
    """Parse INDEX.md's Entries table into [{file, summary, keywords}].

    Same row shape `aiws.kb.retrieval` keys on: `| `name.md` | summary | keywords |`.
    We read INDEX.md but never write it — retrieval semantics are frozen (the
    HARD CONSTRAINT for this change), so the lint only validates against it."""
    index_path = os.path.join(kb, "INDEX.md")
    rows = []
    if not os.path.isfile(index_path):
        return rows
    with open(index_path, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"\|\s*`([^`]+\.md)`\s*\|(.+?)\|(.+?)\|\s*$", line)
            if m:
                rows.append({
                    "file": m.group(1).strip(),
                    "summary": m.group(2).strip(),
                    "keywords": m.group(3).strip(),
                })
    return rows


def _related_links(kb, entry_file):
    """Return the list of `*.md` targets in an entry's `## Related entries`
    footer (in order), or None if the entry has no such section.

    We read only the section that starts at the `## Related entries` heading and
    runs to the next `##` heading or EOF, then pull every `` `target.md` ``
    inline-code span out of it. Reading just that section (not the whole file)
    means a stray ``backtick.md`` elsewhere in the prose can't be mistaken for a
    link, mirroring the inline-code-span discipline in test_skill_manifests.py."""
    path = os.path.join(kb, entry_file)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"^##\s+Related entries\s*$", text, re.M)
    if not m:
        return None
    section = text[m.end():]
    # Stop at the next heading of equal-or-higher level (start of another section).
    nxt = re.search(r"^#{1,2}\s+\S", section, re.M)
    if nxt:
        section = section[:nxt.start()]
    return re.findall(r"`([A-Za-z0-9_.-]+\.md)`", section)


# ── Checks: each returns (ok: bool, problems: list[str]) ─────────────────────
def check_index_sync(kb):
    """(a) INDEX rows and *.md entry files are exactly 1:1.

    Catches both failure directions: an entry file with no INDEX row (invisible
    to retrieval) and an INDEX row pointing at a missing file (a dead row the
    agent will try to open and fail). A duplicate row is also flagged — two rows
    for one file is an ambiguous index."""
    problems = []
    files = _entry_files(kb)
    rows = _index_rows(kb)
    row_files = [r["file"] for r in rows]

    seen = set()
    for rf in row_files:
        if rf in NON_ENTRY_FILES:
            problems.append(f"INDEX row points at non-entry file: {rf}")
            continue
        if rf in seen:
            problems.append(f"INDEX has duplicate row for: {rf}")
        seen.add(rf)
        if rf not in files:
            problems.append(f"INDEX row points at missing file: {rf}")

    for f in sorted(files):
        if f not in seen:
            problems.append(f"entry file has no INDEX row: {f}")

    return (not problems), problems


def check_related_entries(kb):
    """(b) Every entry has a valid `## Related entries` footer.

    A footer must exist, list >=2 links, never link itself, and every target
    must be a real entry file (no link rot). Each of these is a hop the QA skill
    relies on; a missing or rotten link silently shortens multi-hop retrieval."""
    problems = []
    files = _entry_files(kb)
    for f in sorted(files):
        links = _related_links(kb, f)
        if links is None:
            problems.append(f"{f}: no '## Related entries' section")
            continue
        if len(links) < 2:
            problems.append(
                f"{f}: only {len(links)} related link(s), need >=2")
        for target in links:
            if target == f:
                problems.append(f"{f}: links to itself ({target})")
            elif target not in files:
                problems.append(
                    f"{f}: related link points at non-entry/missing file: "
                    f"{target}")
    return (not problems), problems


def check_bidirectional(kb):
    """(c) Related links are symmetric: A lists B  =>  B lists A.

    A one-way link is a hop that works in one direction only — the reader can go
    clarity -> revision but not back, which makes the graph quietly lopsided.
    We report each offending pair so a fork knows exactly which back-link to add.
    Self-links and dead targets are left to check (b); here we only test symmetry
    among real entry-to-entry links."""
    problems = []
    files = _entry_files(kb)
    graph = {}
    for f in files:
        links = _related_links(kb, f) or []
        graph[f] = {t for t in links if t in files and t != f}

    for src in sorted(graph):
        for dst in sorted(graph[src]):
            if src not in graph.get(dst, set()):
                problems.append(
                    f"one-way link: {src} -> {dst} "
                    f"(but {dst} does not link back to {src})")
    return (not problems), problems


def check_keywords(kb):
    """(d) Every INDEX row's Keywords cell is non-empty.

    The Keywords/aliases column is the primary retrieval signal (the retrieval
    protocol scores keyword overlap first). An empty cell means that entry can
    only be reached by Summary-intent overlap — a silent recall hole a fork
    would not otherwise see."""
    problems = []
    for r in _index_rows(kb):
        if not r["keywords"]:
            problems.append(f"INDEX row for {r['file']} has empty Keywords cell")
    return (not problems), problems


# Ordered registry so main() and callers iterate the same checks identically.
CHECKS = [
    ("INDEX <-> directory sync", check_index_sync),
    ("Related-entries validity", check_related_entries),
    ("Bidirectionality", check_bidirectional),
    ("Keywords non-empty", check_keywords),
]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    kb = os.path.abspath(argv[0]) if argv else DEFAULT_KB

    if not os.path.isdir(kb):
        print(f"FAIL: knowledge dir not found: {kb}", file=sys.stderr)
        return 1

    n_entries = len(_entry_files(kb))
    print(f"KB lint — {kb}")
    print(f"({n_entries} entry file(s), {len(_index_rows(kb))} INDEX row(s))\n")

    failed = 0
    for label, fn in CHECKS:
        ok, problems = fn(kb)
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {label}")
        if not ok:
            failed += 1
            for p in problems:
                print(f"       - {p}")

    print()
    if failed:
        print(f"{failed}/{len(CHECKS)} check(s) FAILED")
        return 1
    print(f"All {len(CHECKS)} checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
