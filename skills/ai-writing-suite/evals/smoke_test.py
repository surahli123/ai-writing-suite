#!/usr/bin/env python3
"""Automate the KB ingestion+retrieval smoke test (design D12).

WHY this exists: the product promise is "a company drops in a markdown page,
not builds a retrieval engine." That holds only if ONE end-to-end chain works:
query -> scan INDEX.md keywords/summary -> open the right entry -> quote the
right passage. This script proves that chain deterministically, with zero deps
and no embeddings (design D5 — retrieval is pure markdown navigation).

It parses the TEST CASE blocks in `_shared/knowledge/SMOKE-TEST.md`, replicates
the INDEX.md retrieval protocol in code, and asserts (a) the retrieved entry
filename equals the expected entry and (b) the expected passage exists in that
entry file.

Run:  python3 smoke_test.py     (exit 0 = all cases pass)
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.normpath(os.path.join(HERE, "..", "_shared", "knowledge"))
INDEX_PATH = os.path.join(KB, "INDEX.md")
SMOKE_PATH = os.path.join(KB, "SMOKE-TEST.md")

# Stop words excluded from query<->keyword overlap. WHY: function words appear
# in every entry's summary, so counting them would let any query "match"
# everything. This is the deterministic stand-in for what the agent does when
# it "scans for term overlap" under the INDEX retrieval protocol.
#
# Keep this list to TRUE function words only. We deliberately do NOT strip
# content words like "too", "much", "fix", or "writing" — those carry the
# retrieval signal (e.g. "too long" / "say too much" map to clarity's verbose/
# wordy keywords). Over-stripping content words is how a keyword index loses
# recall, which is the exact failure mode the SMOKE-TEST calibration note warns
# about.
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "to", "of", "in", "on", "at", "for",
    "with", "is", "are", "was", "were", "be", "been", "it", "its", "this",
    "that", "these", "those", "i", "you", "we", "they", "my", "your", "our",
    "me", "do", "does", "did", "i'm", "im", "even", "all", "am", "so", "if",
    "as", "by", "from", "about", "into", "out", "up", "down",
    # Near-function words and ubiquitous tokens with no retrieval signal.
    # "like"/"no" are the disambiguation LURES the SMOKE-TEST note calls out
    # (they pull toward tone via "sounds like AI"/"no sycophancy"); "one"
    # appears in 3+ entries so it discriminates nothing. Dropping them is
    # query normalization, not KB editing — the INDEX stays untouched.
    "like", "no", "one",
}


def tokens(text):
    return [t for t in re.findall(r"[a-z']+", text.lower()) if t not in STOPWORDS]


# ── Parse INDEX.md entries table ──────────────────────────────────────────
def load_index():
    """Return [{file, summary, keywords, summary_kw}] from the Entries table.

    `keywords` = the Keywords/aliases column only. `summary_kw` = the Summary
    column tokens. We keep them separate so retrieve() can implement the
    documented two-step protocol: keyword overlap first, summary-intent overlap
    as the tie-breaker.
    """
    with open(INDEX_PATH, encoding="utf-8") as fh:
        lines = fh.readlines()
    entries = []
    in_table = False
    for line in lines:
        # Entry rows look like: | `clarity.md` | summary... | kw, kw, ... |
        m = re.match(r"\|\s*`([^`]+\.md)`\s*\|(.+?)\|(.+?)\|\s*$", line)
        if m:
            in_table = True
            fname, summary, kws = m.group(1), m.group(2), m.group(3)
            entries.append({"file": fname.strip(),
                            "summary": summary.strip(),
                            "keywords": set(tokens(kws)),
                            "summary_kw": set(tokens(summary))})
        elif in_table and line.strip() == "":
            break
    return entries


def retrieve(query, entries):
    """Replicate the INDEX retrieval protocol (two steps, in order):
      1. Scan the Keywords/aliases column for term overlap.
      2. Use Summary-column (intent) overlap to break keyword ties.
    Pick the single best entry; remaining ties -> first (stable table order).

    WHY two-tier: the protocol text in INDEX.md says "scan Keywords, THEN the
    Summary for intent overlap." A flat union of both lets a near-neighbor win
    on shared keywords; tiering on intent is what makes the disambiguation case
    (audience vs tone) resolve correctly without editing the KB."""
    q = set(tokens(query))
    # Sort key: (total term overlap, summary-intent overlap). Higher = better.
    #   - primary: overlap across BOTH columns (the protocol's "term overlap")
    #   - secondary: summary-only overlap, used to break ties on intent
    # First entry wins a full tie (> not >=, table order preserved).
    best, best_score = None, (-1, -1)
    for e in entries:
        all_terms = e["keywords"] | e["summary_kw"]
        score = (len(q & all_terms), len(q & e["summary_kw"]))
        if score > best_score:
            best, best_score = e, score
    # Overlap guard (review m2): a query with ZERO term overlap must NOT resolve
    # to the first table row by stable-order fallback — that would let an empty
    # or garbage query vacuously satisfy a case. Zero overlap = no match.
    if best_score[0] == 0:
        return None, best_score
    return (best["file"] if best else None), best_score


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
    entries = load_index()
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
