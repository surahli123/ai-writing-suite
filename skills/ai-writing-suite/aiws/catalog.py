"""aiws.catalog — the SOLE parser for the `_shared/patterns/` tell catalog.

The pattern markdown IS the machine-readable registry. Everything that needs to
read the catalog reads it through here, so there is exactly one place that knows
the on-disk shape:

  - `load_catalog_ids()` — {id: source_filename} from the `### <id> — <name>`
    headings (was `audit_report/check_report.py`'s `_CATALOG_HEADER` +
    `load_catalog_ids`; that module now imports this one).
  - `parse_replace_table()` — the L1 replace-on-sight table -> {word: swap} (was
    `evals/test_catalog_sync.py`'s private `_ROW`/`_parse_replace_table`; that
    test now imports this one).
  - `load_catalog()` — full CatalogEntry records (id, name, severity,
    enforcement, source_file), reading the per-entry metadata table.
  - `render_inventory()` / `render_registry()` — the checked-in projections that
    live inside marker-bounded GENERATED blocks in `00-index.md` (Q5 lockfile
    model, `docs/decisions-2026-07-13.md:13`), verified fresh by
    `evals/test_catalog_projection.py`.

Stdlib only, no network. `aiws` imports from neither `evals/` nor `tools/`
(architecture review 2026-07-13, item 2).
"""

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
# aiws/ -> suite-root -> _shared/patterns. Resolve relative to THIS file so the
# default works from any cwd (same convention as aiws/kb/entries.py).
DEFAULT_PATTERNS_DIR = os.path.normpath(
    os.path.join(HERE, "..", "_shared", "patterns"))

# The index file documents the `### <id> — <name>` schema rather than
# instantiating catalog entries, so it is skipped by the id/entry loaders.
INDEX_FILENAME = "00-index.md"

# Canonical category order — the order the catalog's own tables present files in
# (NOT alphabetical). Projections render in this order so a regenerated block is
# byte-identical to the human-authored ordering reviewers expect.
FILE_ORDER = (
    "lexical-tells.md",
    "significance-attribution.md",
    "structural-tells.md",
    "hedging-filler.md",
    "punctuation-formatting.md",
    "communication-artifacts.md",
    "rhythm-stylometric.md",
    "overstepping-presumption.md",
    "narrative-shape.md",
)

# `### S1 — Significance inflation` -> ("S1", "Significance inflation"). The
# em-dash separator matches the schema 00-index.md documents.
_CATALOG_HEADER = re.compile(r"^###\s+([A-Za-z]+\d+)\s+[—-]\s+(.+)$")
_H3 = re.compile(r"^###\s+(.*)$")

# A per-entry metadata table: `| Severity | Enforcement |` header, `| v | v |`
# data row. Two SEPARATE fields per owner ruling Q1 (severity = editorial harm,
# enforcement = mechanism; detection confidence stays in the detector tiers).
_META_HEADER = re.compile(r"^\|\s*Severity\s*\|\s*Enforcement\s*\|\s*$", re.I)
_META_ROW = re.compile(r"^\|\s*([\w-]+)\s*\|\s*([\w-]+)\s*\|\s*$")

UNRATED = "unrated"

# Q1: severity = editorial harm, enforcement = mechanism. Closed vocabularies —
# an entry's metadata table value must be one of these or the loader raises
# (see _parse_entries) rather than silently accepting a typo like "hgih".
VALID_SEVERITY = {"high", "medium", "low", UNRATED}
VALID_ENFORCEMENT = {"regex", "judge", "advisory", UNRATED}

# The L1 replace-on-sight table header (lexical-tells.md). The table is parsed
# into {word: swap} and pinned against detector `TIER1` by test_catalog_sync.
_REPLACE_HEADER = "| AI word | Plain swap |"
# A data row: "| word | swap |". Word is lowercase letters/hyphens (matches every
# TIER1 key); the header ("| AI word |") and separator ("| --- |") rows do not.
_REPLACE_ROW = re.compile(r"^\|\s*([a-z][a-z-]+)\s*\|\s*(.+?)\s*\|\s*$", re.M)


class CatalogEntry:
    """One catalog tell: id, name, severity, enforcement, source_file.

    `severity` (editorial harm) and `enforcement` (mechanism) are the two Q1
    fields; either is UNRATED when the entry carries no metadata table yet.
    """

    __slots__ = ("id", "name", "severity", "enforcement", "source_file")

    def __init__(self, id, name, severity, enforcement, source_file):
        self.id = id
        self.name = name
        self.severity = severity
        self.enforcement = enforcement
        self.source_file = source_file

    def __repr__(self):
        return (f"CatalogEntry(id={self.id!r}, severity={self.severity!r}, "
                f"enforcement={self.enforcement!r})")

    def __eq__(self, other):
        return isinstance(other, CatalogEntry) and self._key() == other._key()

    def _key(self):
        return (self.id, self.name, self.severity, self.enforcement,
                self.source_file)


def _catalog_files(patterns_dir):
    """*.md catalog files in the dir, excluding the schema index."""
    return [n for n in sorted(os.listdir(patterns_dir))
            if n.endswith(".md") and n != INDEX_FILENAME]


def load_catalog_ids(patterns_dir=DEFAULT_PATTERNS_DIR):
    """Return {id: source_filename} for every tell declared in
    _shared/patterns/*.md.

    Raises ValueError if:
      - any H3 heading in a catalog file (other than 00-index.md, which
        documents the schema rather than instantiating it) fails the
        `### <id> — <name>` schema — a malformed heading is a broken entry, not
        a silently-skipped one;
      - a tell id is declared more than once, anywhere in the catalog.

    This makes catalog drift LOUD: a bad heading edit or duplicate id breaks the
    loader itself instead of silently shrinking a set() behind a low floor.
    """
    ids = {}
    for name in sorted(os.listdir(patterns_dir)):
        if not name.endswith(".md"):
            continue
        if name == INDEX_FILENAME:
            continue  # documents the schema; not itself a catalog entry
        path = os.path.join(patterns_dir, name)
        with open(path, encoding="utf-8") as fh:
            for lineno, raw in enumerate(fh, 1):
                line = raw.rstrip("\n")
                if not _H3.match(line):
                    continue
                m = _CATALOG_HEADER.match(line)
                if not m:
                    raise ValueError(
                        f"{name}:{lineno}: H3 heading does not match the "
                        f"'### <id> — <name>' catalog schema: {line!r}")
                tid = m.group(1)
                if tid in ids:
                    raise ValueError(
                        f"{name}:{lineno}: duplicate tell id {tid!r} "
                        f"(already declared in {ids[tid]!r})")
                ids[tid] = name
    return ids


def _parse_entries(name, text):
    """Parse one catalog file's text into CatalogEntry records.

    An entry runs from its `### <id> — <name>` heading to the next H3 (or EOF).
    Its metadata is the first `| Severity | Enforcement |` table inside that
    span; absent -> both fields UNRATED. Scoping to the entry's own span keeps
    an entry's table from being read as a neighbour's (and keeps the L1
    replace-on-sight table, which is NOT a metadata table, invisible here).

    Raises ValueError if a metadata value falls outside VALID_SEVERITY /
    VALID_ENFORCEMENT — a typo (e.g. 'hgih') must break the loader loudly, the
    same way a malformed heading or duplicate id does, not silently pass
    through into the projection as a bogus rating.
    """
    lines = text.splitlines()
    heads = [(i, m) for i, ln in enumerate(lines)
             for m in (_CATALOG_HEADER.match(ln),) if m]
    entries = []
    for idx, (start, m) in enumerate(heads):
        end = heads[idx + 1][0] if idx + 1 < len(heads) else len(lines)
        tid = m.group(1)
        severity, enforcement = UNRATED, UNRATED
        j = start + 1
        while j < end:
            if _META_HEADER.match(lines[j].strip()):
                # data row is the line after the `| --- | --- |` separator
                row = lines[j + 2].strip() if j + 2 < end else ""
                rm = _META_ROW.match(row)
                if rm:
                    severity, enforcement = rm.group(1).lower(), rm.group(2).lower()
                    if severity not in VALID_SEVERITY:
                        raise ValueError(
                            f"{tid}: unknown severity {severity!r} "
                            f"(want one of {sorted(VALID_SEVERITY)})")
                    if enforcement not in VALID_ENFORCEMENT:
                        raise ValueError(
                            f"{tid}: unknown enforcement {enforcement!r} "
                            f"(want one of {sorted(VALID_ENFORCEMENT)})")
                break
            j += 1
        entries.append(CatalogEntry(tid, m.group(2).strip(),
                                    severity, enforcement, name))
    return entries


def load_catalog(patterns_dir=DEFAULT_PATTERNS_DIR):
    """Return the full list of CatalogEntry records across all catalog files,
    ordered by FILE_ORDER then id number. Raises the same ValueErrors as
    load_catalog_ids (malformed heading / duplicate id) so the two never
    disagree on the id set."""
    load_catalog_ids(patterns_dir)  # reuse the loud drift guard
    by_file = {}
    for name in _catalog_files(patterns_dir):
        with open(os.path.join(patterns_dir, name), encoding="utf-8") as fh:
            by_file[name] = _parse_entries(name, fh.read())
    ordered = []
    for name in FILE_ORDER:
        ordered.extend(_by_id_number(by_file.get(name, [])))
    # Any file not in FILE_ORDER (e.g. a fork adds one) still gets included.
    for name in _catalog_files(patterns_dir):
        if name not in FILE_ORDER:
            ordered.extend(_by_id_number(by_file[name]))
    return ordered


def _by_id_number(entries):
    return sorted(entries, key=lambda e: (re.sub(r"\d", "", e.id),
                                          int(re.sub(r"\D", "", e.id) or 0)))


def parse_replace_table(text):
    """Parse the L1 'replace-on-sight' markdown table into {word: swap}.

    Scoped to the table block (header through the next blank line) so unrelated
    pipe characters elsewhere in the doc cannot leak in. Returns {} if the
    table is absent."""
    start = text.find(_REPLACE_HEADER)
    if start == -1:
        return {}
    block = text[start:]
    end = block.find("\n\n")  # table ends at the first blank line
    if end != -1:
        block = block[:end]
    return {m.group(1).strip(): m.group(2).strip()
            for m in _REPLACE_ROW.finditer(block)}


def load_replace_table(patterns_dir=DEFAULT_PATTERNS_DIR):
    """Read lexical-tells.md and return its replace-on-sight table {word: swap}."""
    path = os.path.join(patterns_dir, "lexical-tells.md")
    with open(path, encoding="utf-8") as fh:
        return parse_replace_table(fh.read())


# --- Checked-in projections (Q5 lockfile model) ---------------------------
# Rendered from the registry above and committed inside these marker pairs in
# 00-index.md; test_catalog_projection.py regenerates and diffs them.

INVENTORY_BEGIN = "<!-- BEGIN GENERATED: inventory (aiws/catalog.py) -->"
INVENTORY_END = "<!-- END GENERATED: inventory -->"
REGISTRY_BEGIN = "<!-- BEGIN GENERATED: registry (aiws/catalog.py) -->"
REGISTRY_END = "<!-- END GENERATED: registry -->"

_EN_DASH = "–"  # – : matches the existing "L1–L6" ranges


def _file_order(patterns_dir):
    """FILE_ORDER, then any catalog file not in it (e.g. a fork-added pattern
    file) appended in directory-listing order. This is the SAME file set/order
    load_catalog() and render_registry() use, so a fork-added file shows up in
    both projections consistently instead of undercounting the inventory Total
    while still appearing in the registry."""
    extra = [n for n in _catalog_files(patterns_dir) if n not in FILE_ORDER]
    return list(FILE_ORDER) + extra


def render_inventory(patterns_dir=DEFAULT_PATTERNS_DIR):
    """Per-file entry-count table + total, derived from the live catalog."""
    entries = load_catalog(patterns_dir)
    rows = ["| File | Entries |", "| --- | --- |"]
    total = 0
    for name in _file_order(patterns_dir):
        file_entries = _by_id_number([e for e in entries if e.source_file == name])
        if not file_entries:
            continue
        ids = [e.id for e in file_entries]
        rng = f"{ids[0]}{_EN_DASH}{ids[-1]}" if len(ids) > 1 else ids[0]
        rows.append(f"| [`{name}`]({name}) | {len(ids)} ({rng}) |")
        total += len(ids)
    rows.append(f"| **Total** | **{total}** |")
    return "\n".join(rows)


def render_registry(patterns_dir=DEFAULT_PATTERNS_DIR):
    """The machine-readable registry projected to a human-readable table:
    id, name, severity, enforcement — one row per tell, in catalog order."""
    entries = load_catalog(patterns_dir)
    rows = ["| ID | Name | Severity | Enforcement |",
            "| --- | --- | --- | --- |"]
    for e in entries:
        rows.append(f"| {e.id} | {e.name} | {e.severity} | {e.enforcement} |")
    return "\n".join(rows)


def _replace_block(text, begin, end, body):
    """Replace the content between `begin` and `end` markers with `body`."""
    b = text.index(begin)
    e = text.index(end)
    return text[:b] + begin + "\n" + body + "\n" + text[e:]


def render_index(text, patterns_dir=DEFAULT_PATTERNS_DIR):
    """Return `text` (00-index.md content) with both generated blocks refreshed."""
    text = _replace_block(text, INVENTORY_BEGIN, INVENTORY_END,
                          render_inventory(patterns_dir))
    text = _replace_block(text, REGISTRY_BEGIN, REGISTRY_END,
                          render_registry(patterns_dir))
    return text


def _index_path(patterns_dir):
    return os.path.join(patterns_dir, INDEX_FILENAME)


def main():
    """Regenerate the marker-bounded blocks in 00-index.md in place."""
    path = _index_path(DEFAULT_PATTERNS_DIR)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    updated = render_index(text)
    if updated != text:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(updated)
        print(f"regenerated projections in {path}")
    else:
        print(f"projections already fresh in {path}")


if __name__ == "__main__":
    main()
