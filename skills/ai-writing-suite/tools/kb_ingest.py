#!/usr/bin/env python3
"""Thin CLI entrypoint over `aiws.kb.ingest` — convert exported pages into
KB-shaped entries (the fork's ingestion step).

All the shaping logic (HTML/markdown parsing, keyword/summary extraction,
related-link proposals, atomic writes, INDEX.md merge) lives in
`aiws.kb.ingest`; see that module's docstring for the full contract. This file
only adds the argv-parsing CLI (architecture review 2026-07-13, item 5 — this
tool used to import the parser/checker logic directly; it is now identical to
the reusable module aiws.kb.ingest, just invoked through argparse here).

Run:  python3 tools/kb_ingest.py <export-dir> --out _shared/knowledge [--force]
"""

import argparse
import os
import sys

# tools/ -> suite root, so `import aiws` resolves to the sibling aiws/ package.
_HERE = os.path.dirname(os.path.abspath(__file__))
_SUITE_ROOT = os.path.normpath(os.path.join(_HERE, ".."))
if _SUITE_ROOT not in sys.path:
    sys.path.insert(0, _SUITE_ROOT)

from aiws.kb.ingest import (  # noqa: E402  (path set above)
    ingest, print_report, NON_ENTRY_FILES, STOPWORDS, BOILERPLATE_HEADINGS,
    MIN_KEYWORDS, MAX_RELATED, slugify, extract_keywords, first_sentence,
    propose_related, render_entry, read_entry_meta, merge_index_text,
    parse_existing_index_rows, parse_html_export, parse_md_export,
    INDEX_HEADER, _atomic_write, _INDEX_ROW_RE, _existing_provenance_source,
    _words, _META_RE, _PROVENANCE_RE,
)

_HELP_EPILOG = """\
INDEX-row precedence on re-runs (a file NOT (re)written this run — because it
already existed and --force was not passed — never gets its INDEX.md row
regenerated from the incoming page): an existing row is preserved verbatim
first; only if no row exists yet is one derived, preferring the on-disk file's
own <!-- kb-entry-meta --> header over the incoming page. This is what keeps a
human's hand edit to an INDEX row, and an untouched file's row, from drifting
out of sync with a later ingest run. See docs/kb-onboarding.md.
"""


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ap = argparse.ArgumentParser(
        description="Ingest exported pages into KB entries.",
        epilog=_HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)
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
