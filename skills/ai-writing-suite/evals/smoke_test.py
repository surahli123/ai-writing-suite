#!/usr/bin/env python3
"""Automate the KB ingestion+retrieval smoke test (design D12).

WHY this exists: the product promise is "a company drops in a markdown page,
not builds a retrieval engine." That holds only if ONE end-to-end chain works:
query -> scan INDEX.md keywords/summary -> open the right entry -> quote the
right passage. This script proves that chain deterministically, with zero deps
and no embeddings (design D5 — retrieval is pure markdown navigation).

The retrieval protocol itself (`load_index`, `retrieve`, `tokens`) moved to
`aiws.kb.retrieval` (architecture review 2026-07-13, item 5) — it is reusable
product logic, not test-only scaffolding, and `aiws.kb.validate` reuses it too.
This file keeps the eval-specific part: parsing the TEST CASE blocks in
`_shared/knowledge/SMOKE-TEST.md` and asserting (a) the retrieved entry
filename equals the expected entry and (b) the expected passage exists in that
entry file.

Run:  python3 smoke_test.py     (exit 0 = all cases pass)
"""

import os
import re
import sys

# evals/ -> suite root, so `import aiws` resolves to the sibling aiws/ package.
_HERE = os.path.dirname(os.path.abspath(__file__))
HERE = _HERE  # drop-in compat: this module's own dir, as before the move
_SUITE_ROOT = os.path.normpath(os.path.join(_HERE, ".."))
if _SUITE_ROOT not in sys.path:
    sys.path.insert(0, _SUITE_ROOT)

from aiws.kb.retrieval import (  # noqa: E402
    tokens, load_index, retrieve, STOPWORDS,
)

KB = os.path.normpath(os.path.join(_HERE, "..", "_shared", "knowledge"))
INDEX_PATH = os.path.join(KB, "INDEX.md")
SMOKE_PATH = os.path.join(KB, "SMOKE-TEST.md")


# ── Parse SMOKE-TEST.md TEST CASE blocks ──────────────────────────────────
def load_cases():
    """Extract (query, expected_entry, expected_passage) from the smoke doc.

    The doc has two case shapes: the labelled 'TEST CASE' block and the
    'second case' block. Both carry a Query blockquote, an 'Expected entry'
    line, and an 'Expected passage' blockquote. We parse on those anchors
    rather than on heading text so a reworded heading doesn't silently drop
    a case.
    """
    with open(SMOKE_PATH, encoding="utf-8") as fh:
        text = fh.read()

    cases = []
    # Find every "Expected entry" anchor; walk backward for the query and
    # forward for the passage around each one.
    for m in re.finditer(r"\*\*Expected entry(?:\s+retrieved)?:\*\*\s*`([^`]+)`", text):
        entry = m.group(1).strip()
        before = text[:m.start()]
        after = text[m.start():]

        # Query = the last "Query" blockquote before this anchor.
        q_matches = list(re.finditer(
            r"\*\*Query[^*]*:\*\*\s*\n>\s*\"?(.+?)\"?\s*\n", before, re.S))
        query = q_matches[-1].group(1).strip() if q_matches else None

        # Passage = the first "Expected passage" blockquote after this anchor.
        p_match = re.search(
            r"\*\*Expected passage[^*]*:\*\*\s*\n((?:>\s?.*\n?)+)", after)
        passage = None
        if p_match:
            # Strip leading "> " from each quoted line, join, collapse spaces.
            raw = p_match.group(1)
            passage = " ".join(
                re.sub(r"^>\s?", "", ln).strip()
                for ln in raw.splitlines() if ln.strip())
            passage = re.sub(r"\s+", " ", passage).strip()

        if query and entry and passage:
            cases.append({"query": query, "entry": entry, "passage": passage})
    return cases


def normalize(s):
    """Collapse whitespace + drop markdown bold so passage containment is
    robust to formatting differences between SMOKE-TEST and the entry file."""
    s = s.replace("**", "")
    return re.sub(r"\s+", " ", s).strip().lower()


def run():
    entries = load_index(index_path=INDEX_PATH)
    cases = load_cases()
    if not cases:
        print("FAIL: no TEST CASE blocks parsed from SMOKE-TEST.md", file=sys.stderr)
        return 1
    if not entries:
        print("FAIL: no entries parsed from INDEX.md", file=sys.stderr)
        return 1

    failures = 0
    print(f"KB smoke test — {len(cases)} case(s), {len(entries)} index entries\n")
    for i, c in enumerate(cases, 1):
        got, overlap = retrieve(c["query"], entries)
        entry_ok = (got == c["entry"])

        # Passage check: the expected passage must appear in the retrieved file.
        passage_ok = False
        entry_path = os.path.join(KB, got) if got else None
        if entry_path and os.path.exists(entry_path):
            with open(entry_path, encoding="utf-8") as fh:
                body = normalize(fh.read())
            # Match on the first sentence of the expected passage so trailing
            # editorial parentheticals in the smoke doc don't break the assert.
            needle = normalize(c["passage"].split(".")[0])
            passage_ok = needle in body

        ok = entry_ok and passage_ok
        if not ok:
            failures += 1
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] Case {i}: query -> {got} "
              f"(expected {c['entry']}, overlap={overlap})")
        if not entry_ok:
            print(f"       entry mismatch: got {got}, expected {c['entry']}")
        if entry_ok and not passage_ok:
            print(f"       passage not found in {got}: "
                  f"\"{c['passage'][:60]}...\"")

    print()
    if failures:
        print(f"{failures}/{len(cases)} case(s) FAILED")
        return 1
    print(f"All {len(cases)} case(s) passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
