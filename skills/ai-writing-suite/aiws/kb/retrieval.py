"""INDEX.md loading + the keyword/summary retrieval protocol.

Moved unchanged from `evals/smoke_test.py` (architecture review 2026-07-13,
item 5), with one signature change: `load_index()` takes an explicit
`index_path` parameter instead of reading a module-level `INDEX_PATH` global.
That global was the seam `tools/kb_validate.py` used to reach a different KB
by temporarily mutating `smoke_test.INDEX_PATH` (save/restore around each
call) — a defect this module removes by construction: callers now just pass
the path they mean.
"""

import os
import re

from aiws.kb.entries import DEFAULT_KB

DEFAULT_INDEX_PATH = os.path.join(DEFAULT_KB, "INDEX.md")

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
def load_index(index_path=None):
    """Return [{file, summary, keywords, summary_kw}] from the Entries table.

    `keywords` = the Keywords/aliases column only. `summary_kw` = the Summary
    column tokens. We keep them separate so retrieve() can implement the
    documented two-step protocol: keyword overlap first, summary-intent overlap
    as the tie-breaker.

    `index_path` defaults to the shipped KB's INDEX.md; pass an explicit path
    to read a different KB (e.g. a fork's KB under validation) — no global
    mutation involved.
    """
    if index_path is None:
        index_path = DEFAULT_INDEX_PATH
    with open(index_path, encoding="utf-8") as fh:
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
    """Replicate the frozen KB retrieval semantics:
      1. Rank by overlap across Keywords/aliases and Summary terms.
      2. Use Summary-column overlap to break total-overlap ties.
    Return every best entry on a full tie, in stable table order.

    See RETRIEVAL-SEMANTICS.md for the canonical algorithm and rationale."""
    q = set(tokens(query))
    # Sort key: (total overlap, summary-intent overlap). Higher = better.
    #   - primary: overlap across BOTH columns
    #   - secondary: summary-only overlap, used to break ties on intent
    # Full ties are all retained in stable table order.
    best_files, best_score = [], (-1, -1)
    for e in entries:
        all_terms = e["keywords"] | e["summary_kw"]
        score = (len(q & all_terms), len(q & e["summary_kw"]))
        if score > best_score:
            best_files, best_score = [e["file"]], score
        elif score == best_score:
            best_files.append(e["file"])
    # Overlap guard (review m2): a query with ZERO term overlap must NOT resolve
    # to the first table row by stable-order fallback — that would let an empty
    # or garbage query vacuously satisfy a case. Zero overlap = no match.
    if best_score[0] <= 0:
        return None, best_score
    return best_files, best_score
