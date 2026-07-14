#!/usr/bin/env python3
"""Convert exported pages into KB-shaped entries (the fork's ingestion step).

WHY this exists: the whole v1 bet is "engine vs fuel" — the OSS repo ships the
engine + a generic KB, and a company fork drops its real DS Comms Playbook into
`_shared/knowledge/` "via a Confluence page — data, not engineering" (design
D11/D12). Today that drop-in step is UNTOOLED: a data person exports pages from
Confluence/Notion/GDocs and must hand-shape each into the markdown + INDEX.md
contract that `comms-qa` retrieval depends on (see `_shared/knowledge/INDEX.md`).
Do it wrong and retrieval silently degrades — the agent answers from a broken KB
or refuses everything, on the company's first day. This tool does the mechanical
shaping so the human only reviews, not hand-crafts.

What it produces, per input page:
  * one `*.md` entry: a `<!-- kb-entry-meta -->` header carrying Keywords +
    Summary (the retrieval fields), the page body as markdown, and a
    `## Related entries` footer.
  * a merged `INDEX.md` row: `| `file.md` | summary | keywords |` — the single
    row that IS the ingestion step (INDEX.md retrieval semantics are FROZEN; this
    tool only appends/updates rows, it never rewrites the protocol).

Honesty contract (the product's whole adoption funnel rides on this):
  * It NEVER silently guesses. Keywords and Summary are EXTRACTED from the page's
    own words (title + headings + first sentence) — extraction, not fabrication.
  * Cross-links between entries are PROPOSED from shared-keyword overlap among the
    ingested batch (deterministic, symmetric) and every proposal is printed in the
    end-of-run report for the human to confirm — surfaced, never silent.
  * When it genuinely cannot infer something (no title, no prose, a duplicate
    topic, too few keywords, too few related neighbours), it writes an explicit
    `TODO:` marker into the file AND lists it at the end. A TODO makes
    kb_validate.py fail — by design — so the human fixes it before first use.

Idempotent: no timestamps, deterministic ordering; re-running on the same input
yields byte-identical output. It NEVER overwrites an existing entry without
`--force`.

Input formats (both supported in one run):
  * Confluence "Export to HTML" pages (`*.html`) — the per-page/space HTML export
    any Confluence user can produce with no admin rights or API token (unlike the
    storage-format XML or the REST API, which need both). Parsed with stdlib
    `html.parser` — zero deps, so it runs identically on every target surface.
  * Generic markdown export (`*.md`, `*.markdown`) — Notion / Google Docs / plain
    markdown. Title = first `# ` heading; body used as-is.

Stdlib only. Run:
  python3 tools/kb_ingest.py <export-dir> --out _shared/knowledge [--force]
"""

import argparse
import os
import re
import sys
from html.parser import HTMLParser

# Files in a knowledge dir that are NOT retrieval entries (kept in sync with
# kb_lint.NON_ENTRY_FILES so ingest and lint agree on what counts as an entry).
NON_ENTRY_FILES = {"INDEX.md", "README.md", "SMOKE-TEST.md"}

# Stopwords for keyword extraction. Deliberately function-words only — the same
# discipline as smoke_test.STOPWORDS: stripping content words is how a keyword
# index loses recall.
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "to", "of", "in", "on", "at", "for",
    "with", "is", "are", "was", "were", "be", "been", "it", "its", "this",
    "that", "these", "those", "how", "what", "when", "why", "your", "you",
    "our", "we", "they", "from", "by", "as", "do", "does", "about", "into",
}

MIN_KEYWORDS = 3   # below this, keyword extraction is too thin -> TODO.
MAX_RELATED = 3    # cap related-entry proposals per entry (matches KB norm 2-3).


# ── Title / slug helpers ────────────────────────────────────────────────────
def slugify(title):
    """Turn a page title into a stable KB filename stem (kebab-case, ascii)."""
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s or "untitled"


def _words(text):
    """Lowercase content tokens with stopwords removed, order preserved."""
    return [w for w in re.findall(r"[a-z][a-z0-9'-]+", text.lower())
            if w not in STOPWORDS and len(w) > 2]


# ── HTML export -> (title, markdown body) ───────────────────────────────────
class _ConfluenceHTML(HTMLParser):
    """Minimal Confluence-HTML -> markdown converter (stdlib only).

    Handles the block/inline tags a Confluence page export actually uses:
    headings, paragraphs, lists, bold/italic, code/pre, links (text kept), line
    breaks. Unknown tags (nav, div wrappers, script/style) are dropped, keeping
    only their text — good enough to preserve the page's words, which is all the
    KB needs (the retrieval signal is words, not layout)."""

    _BLOCK = {"p", "div", "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6",
              "pre", "tr", "br"}

    def __init__(self):
        super().__init__()
        self.title = None
        self._in_title = False
        self._skip_depth = 0          # inside <script>/<style>
        self._list_stack = []         # 'ul' | 'ol' for nesting
        self.parts = []               # emitted markdown fragments

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip_depth += 1
        elif tag == "title":
            self._in_title = True
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.parts.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "p":
            self.parts.append("\n\n")
        elif tag in ("ul", "ol"):
            self._list_stack.append(tag)
            self.parts.append("\n")
        elif tag == "li":
            depth = max(0, len(self._list_stack) - 1)
            marker = "1. " if (self._list_stack or ["ul"])[-1] == "ol" else "- "
            self.parts.append("\n" + "  " * depth + marker)
        elif tag in ("strong", "b"):
            self.parts.append("**")
        elif tag in ("em", "i"):
            self.parts.append("*")
        elif tag in ("code", "pre"):
            self.parts.append("`")
        elif tag == "br":
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip_depth = max(0, self._skip_depth - 1)
        elif tag == "title":
            self._in_title = False
        elif tag in ("ul", "ol") and self._list_stack:
            self._list_stack.pop()
        elif tag in ("strong", "b"):
            self.parts.append("**")
        elif tag in ("em", "i"):
            self.parts.append("*")
        elif tag in ("code", "pre"):
            self.parts.append("`")

    def handle_data(self, data):
        if self._skip_depth:
            return
        if self._in_title:
            self.title = (self.title or "") + data
            return
        self.parts.append(data)

    def body_markdown(self):
        text = "".join(self.parts)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def parse_html_export(path):
    """Return (title, body_markdown). Title from <title>, else first <h1>."""
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    p = _ConfluenceHTML()
    p.feed(raw)
    body = p.body_markdown()
    title = (p.title or "").strip()
    # Confluence titles often read "Page Name : Space" or "Page Name - Confluence".
    title = re.split(r"\s+[:\-]\s+", title)[0].strip() if title else ""
    if not title:
        m = re.search(r"^#\s+(.+)$", body, re.M)
        title = m.group(1).strip() if m else ""
    # Drop a leading duplicated H1 that just repeats the title.
    if title:
        body = re.sub(r"^#\s+" + re.escape(title) + r"\s*\n+", "", body, count=1)
    return title, body.strip()


# ── Markdown export -> (title, body) ────────────────────────────────────────
def parse_md_export(path):
    """Return (title, body). Title = first `# ` heading; body = the rest."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"^#\s+(.+)$", text, re.M)
    if m:
        title = m.group(1).strip()
        body = (text[:m.start()] + text[m.end():]).strip()
    else:
        title, body = "", text.strip()
    return title, body


# ── Retrieval-field extraction (never fabricates) ───────────────────────────
def extract_keywords(title, body):
    """Extract candidate retrieval keywords from the page's OWN words.

    Source = the title plus every heading, in document order, deduped. These are
    terms the page literally uses, so this is extraction (safe), not invention of
    synonyms/aliases (which a human still adds). Returns [] if too thin."""
    seen, out = set(), []
    heads = re.findall(r"^#{1,6}\s+(.+)$", body, re.M)
    for chunk in [title] + heads:
        for w in _words(chunk):
            if w not in seen:
                seen.add(w)
                out.append(w)
    return out


def first_sentence(body):
    """Summary = the first real prose sentence (not a heading/list/code line)."""
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith(("#", "-", "*", "`", "|", ">", "1.")):
            continue
        m = re.match(r"(.+?[.!?])(\s|$)", s)
        return (m.group(1) if m else s).strip()
    return ""


# ── Related-entry proposals (shared-keyword overlap, symmetric) ─────────────
def propose_related(entries):
    """Return {file: [related files]} proposed from shared-keyword overlap.

    Undirected: an edge exists if EITHER endpoint ranks the other in its top-N by
    shared-keyword count, then symmetrised — so every proposed link is
    bidirectional by construction (kb_lint.check_bidirectional passes). Entries
    with fewer than 2 neighbours are left for the caller to TODO."""
    files = sorted(entries)
    kw = {f: set(entries[f]["keywords"]) for f in files}
    picks = {f: set() for f in files}
    for f in files:
        scored = sorted(
            ((len(kw[f] & kw[g]), g) for g in files if g != f),
            key=lambda t: (-t[0], t[1]))
        for shared, g in scored[:MAX_RELATED]:
            if shared >= 1:
                picks[f].add(g)
    # Symmetrise: if A picked B, B lists A too.
    related = {f: set(picks[f]) for f in files}
    for f in files:
        for g in picks[f]:
            related[g].add(f)
    return {f: sorted(related[f]) for f in files}


# ── Rendering ───────────────────────────────────────────────────────────────
def render_entry(entry, related):
    """Render one KB entry file.

    Only GENUINE gaps get an inline `TODO:` marker (which makes kb_validate fail
    by design). A clean page — real title, prose, >=3 keywords, >=2 related
    neighbours — renders with NO `TODO`, so it can validate PASS straight after
    ingest. Auto-proposed related links carry a provenance comment (not a TODO):
    they are surfaced for confirmation in the run report, not blocked."""
    kw = entry["keywords"]
    summary = entry["summary"]
    lines = ["<!-- kb-entry-meta"]
    lines.append("Keywords: " + (", ".join(kw) if kw
                 else "TODO: add retrieval keywords/aliases"))
    lines.append("Summary: " + (summary if summary
                 else "TODO: add a one-line summary"))
    lines.append("-->")
    lines.append("")
    lines.append("# " + (entry["title"] or "TODO: add a title (none found in source)"))
    lines.append("")
    lines.append("> Generated by `kb_ingest.py` from `" + entry["source"] +
                 "`. Confirm the content below before first use.")
    lines.append("")
    # Inline block for every per-entry gap, so the validator points file:line at
    # the exact problem and the operator cannot miss it.
    if entry["per_todos"]:
        lines.append("<!-- kb_ingest flagged gaps:")
        for t in entry["per_todos"]:
            lines.append("TODO: " + t)
        lines.append("-->")
        lines.append("")
    if entry["body"]:
        lines.append(entry["body"])
    else:
        lines.append("TODO: source page had no body content — add the entry text.")
    lines.append("")
    lines.append("## Related entries")
    lines.append("")
    for r in related:
        rslug = r[:-3] if r.endswith(".md") else r
        lines.append("- `" + r + "` — related topic: " + rslug + ".")
    if len(related) < 2:
        lines.append("<!-- TODO: add >=2 bidirectional `related.md` links "
                     "(too few shared-keyword neighbours to propose) -->")
    else:
        lines.append("<!-- related links auto-proposed by kb_ingest from "
                     "shared-keyword overlap; confirm they are accurate -->")
    lines.append("")
    return "\n".join(lines)


INDEX_HEADER = """# Knowledge Base — Navigation Index

> **This file is the retrieval backbone.** Retrieval = an agent reads this index,
> matches the question against the **Summary** and **Keywords / aliases** columns,
> opens the one entry that fits, and quotes the passage. Pure markdown + file
> reads — no embeddings, no vector DB, no host-specific tools (design D5).
>
> Keep this index in sync with the entries. Adding a KB entry = add one file +
> one row here. This table was seeded by `tools/kb_ingest.py`; edit it by hand
> afterwards — the retrieval protocol itself is frozen.

## How an agent uses this index (retrieval protocol)

1. Read the user's question.
2. Scan the **Keywords / aliases** column for term overlap, then the **Summary**
   column for intent overlap. Pick the single best-matching entry.
3. Open that entry file, find the section that answers the question, quote it,
   and cite the entry filename. If two entries tie, open both. If nothing
   matches, say so — do not invent guidance.

## Entries

| Entry file | Summary (one line) | Keywords / aliases |
| --- | --- | --- |
"""


def _index_row(fname, summary, keywords):
    s = summary if summary else "TODO: add a one-line summary"
    k = ", ".join(keywords) if keywords else "TODO: add keywords/aliases"
    return "| `" + fname + "` | " + s + " | " + k + " |"


def parse_existing_index_rows(index_path):
    """Return {file: raw_row_line} for an existing INDEX.md, else {}.

    Lets ingest MERGE into a fork's existing index (preserve untouched rows)
    instead of clobbering hand-written ones."""
    rows = {}
    if not os.path.isfile(index_path):
        return rows
    with open(index_path, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"\|\s*`([^`]+\.md)`\s*\|(.+?)\|(.+?)\|\s*$", line)
            if m:
                rows[m.group(1).strip()] = line.rstrip("\n")
    return rows


# ── Orchestration ───────────────────────────────────────────────────────────
def _discover_inputs(src_dir):
    """Return sorted [(path, kind)] for supported export files under src_dir."""
    out = []
    for name in sorted(os.listdir(src_dir)):
        low = name.lower()
        p = os.path.join(src_dir, name)
        if not os.path.isfile(p):
            continue
        if low.endswith((".html", ".htm")):
            out.append((p, "html"))
        elif low.endswith((".md", ".markdown")):
            out.append((p, "md"))
    return out


def ingest(src_dir, out_dir, force=False):
    """Ingest an export dir into KB-shaped entries + a merged INDEX.md.

    Returns a report dict: {written, skipped, todos, proposals, errors}."""
    report = {"written": [], "skipped": [], "todos": [], "proposals": [],
              "errors": []}
    inputs = _discover_inputs(src_dir)
    if not inputs:
        report["errors"].append("no .html/.md export files found in " + src_dir)
        return report

    os.makedirs(out_dir, exist_ok=True)

    # Pass 1 — parse every page and assign a unique, deterministic filename.
    entries = {}
    used = set(NON_ENTRY_FILES)
    for path, kind in inputs:
        title, body = (parse_html_export(path) if kind == "html"
                       else parse_md_export(path))
        src_name = os.path.basename(path)
        stem = slugify(title) if title else slugify(os.path.splitext(src_name)[0])
        fname = stem + ".md"
        per_todos = []
        if not title:
            per_todos.append("missing title (used source filename)")
        if fname in used:  # duplicate topic
            n = 2
            while stem + "-" + str(n) + ".md" in used:
                n += 1
            fname = stem + "-" + str(n) + ".md"
            per_todos.append("duplicate topic '" + (title or stem) +
                             "' — merge or rename")
        used.add(fname)

        keywords = extract_keywords(title, body)
        if len(keywords) < MIN_KEYWORDS:
            per_todos.append("only " + str(len(keywords)) +
                             " keyword(s) extracted (need >=" +
                             str(MIN_KEYWORDS) + ") — add aliases")
        summary = first_sentence(body)
        if not summary:
            per_todos.append("no summary sentence found in source")

        entries[fname] = {"title": title, "body": body, "keywords": keywords,
                          "summary": summary, "source": src_name,
                          "per_todos": per_todos}

    # Pass 2 — propose related links across the whole batch (needs all keywords).
    related = propose_related(entries)

    # Pass 3 — write entry files (idempotent; never clobber without --force).
    for fname in sorted(entries):
        e = entries[fname]
        dest = os.path.join(out_dir, fname)
        text = render_entry(e, related[fname])
        if os.path.exists(dest) and not force:
            report["skipped"].append(fname + " (exists; use --force to overwrite)")
        else:
            with open(dest, "w", encoding="utf-8") as fh:
                fh.write(text)
            report["written"].append(fname)
        # Record TODOs + proposals for the end-of-run report regardless.
        for t in e["per_todos"]:
            report["todos"].append(fname + ": " + t)
        if len(related[fname]) < 2:
            report["todos"].append(fname + ": fewer than 2 related-entry links")
        for r in related[fname]:
            report["proposals"].append(fname + " <-> " + r +
                                       " (shared-keyword overlap; confirm)")

    # Pass 4 — merge the INDEX.md rows (preserve existing untouched rows).
    index_path = os.path.join(out_dir, "INDEX.md")
    existing_rows = parse_existing_index_rows(index_path)
    all_files = sorted(set(existing_rows) | set(entries))
    body_rows = []
    for f in all_files:
        if f in entries:
            e = entries[f]
            body_rows.append(_index_row(f, e["summary"], e["keywords"]))
        else:
            body_rows.append(existing_rows[f])
    # Preserve any existing non-table prose above/below? For a merge we keep the
    # canonical header + the merged table. A fresh fork gets the full header; a
    # fork with an existing hand-written INDEX keeps its rows but the frozen
    # protocol header is re-asserted (identical semantics), never mutated.
    index_text = INDEX_HEADER + "\n".join(body_rows) + "\n"
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write(index_text)

    return report


def print_report(report):
    """Human-readable end-of-run summary. Proposals and TODOs are surfaced here —
    the tool never guesses silently."""
    print("\n=== kb_ingest report ===")
    print("Wrote " + str(len(report["written"])) + " entr(y/ies): " +
          ", ".join(report["written"]) if report["written"] else "Wrote 0 entries")
    if report["skipped"]:
        print("\nSkipped (already existed, no --force):")
        for s in report["skipped"]:
            print("  - " + s)
    if report["proposals"]:
        print("\nPROPOSED related links (confirm these — not auto-trusted):")
        for p in report["proposals"]:
            print("  - " + p)
    if report["todos"]:
        print("\nTODO — resolve before first use (kb_validate.py will fail on these):")
        for t in report["todos"]:
            print("  - " + t)
    if report["errors"]:
        print("\nERRORS:")
        for e in report["errors"]:
            print("  - " + e)
    print("\nNext: review TODOs, then run  python3 tools/kb_validate.py " +
          "_shared/knowledge")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ap = argparse.ArgumentParser(description="Ingest exported pages into KB entries.")
    ap.add_argument("src", help="directory of exported pages (.html and/or .md)")
    ap.add_argument("--out", required=True, help="target knowledge dir")
    ap.add_argument("--force", action="store_true",
                    help="overwrite existing entry files")
    args = ap.parse_args(argv)

    if not os.path.isdir(args.src):
        print("FAIL: source dir not found: " + args.src, file=sys.stderr)
        return 1
    report = ingest(args.src, args.out, force=args.force)
    print_report(report)
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
