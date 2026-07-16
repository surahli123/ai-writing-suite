"""Freshness check for the checked-in catalog projections (Q5 lockfile model).

The inventory-counts and registry tables in `_shared/patterns/00-index.md` are
GENERATED, marker-bounded blocks committed like a lockfile
(`docs/decisions-2026-07-13.md:13`). This test regenerates them from the live
catalog via `aiws.catalog` and asserts the committed blocks match byte-for-byte —
so a new/edited/removed tell, or a changed severity/enforcement value, that wasn't
followed by `python3 -m aiws.catalog` turns CI red instead of silently drifting.
No build step at use time; this is the only thing that keeps the projection honest.

Stdlib-only, no network. Runs under `run_all.sh` via `unittest discover`.
"""

import os
import sys
import unittest

# evals/ -> <suite-root>, so `import aiws` resolves to the sibling aiws/ package.
_SUITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SUITE_ROOT not in sys.path:
    sys.path.insert(0, _SUITE_ROOT)

from aiws import catalog  # noqa: E402  (path set above)

INDEX = os.path.join(_SUITE_ROOT, "_shared", "patterns", "00-index.md")
COMMS_POLISH = os.path.join(_SUITE_ROOT, "skills", "comms-polish", "SKILL.md")
_STALE = ("00-index.md projection is STALE — regenerate with "
          "`python3 -m aiws.catalog` and commit the result.")


def _block(text, begin, end):
    """Return the content strictly between the begin/end marker lines."""
    b = text.index(begin) + len(begin)
    e = text.index(end)
    return text[b:e].strip("\n")


class CatalogProjectionFreshness(unittest.TestCase):
    def setUp(self):
        with open(INDEX, encoding="utf-8") as fh:
            self.text = fh.read()

    def test_inventory_block_matches_catalog(self):
        committed = _block(self.text, catalog.INVENTORY_BEGIN, catalog.INVENTORY_END)
        self.assertEqual(committed, catalog.render_inventory(), _STALE)

    def test_registry_block_matches_catalog(self):
        committed = _block(self.text, catalog.REGISTRY_BEGIN, catalog.REGISTRY_END)
        self.assertEqual(committed, catalog.render_registry(), _STALE)

    def test_render_index_is_idempotent(self):
        # Regenerating an already-fresh index changes nothing — the freshness
        # check and the regenerator agree on the canonical rendering.
        self.assertEqual(catalog.render_index(self.text), self.text, _STALE)

    def test_registry_covers_every_id_and_all_rated(self):
        # The projection must list exactly the catalog ids, each with a real
        # (non-unrated) severity + enforcement — so an entry that ships without a
        # metadata table is caught here, not silently rendered blank.
        entries = catalog.load_catalog()
        ids = catalog.load_catalog_ids()
        self.assertEqual(len(entries), len(ids))
        self.assertEqual({e.id for e in entries}, set(ids))
        unrated = [e.id for e in entries
                   if catalog.UNRATED in (e.severity, e.enforcement)]
        self.assertEqual(unrated, [], f"entries missing metadata: {unrated}")


class CatalogConsumerContract(unittest.TestCase):
    """comms-polish discovers catalog files from the generated inventory.

    A second filename list in SKILL.md goes stale whenever a category is added;
    the generated inventory is already freshness-gated against the live catalog.
    """

    def test_comms_polish_does_not_duplicate_the_catalog_file_list(self):
        with open(COMMS_POLISH, encoding="utf-8") as fh:
            text = fh.read()
        start = text.index("## Pattern catalog")
        end = text.index("## Boundary", start)
        section = text[start:end]

        self.assertIn("_shared/patterns/00-index.md", section)
        self.assertIn("generated inventory", section.lower())
        self.assertIn("every category file", section.lower())

        manual_entries = [
            line for line in section.splitlines()
            if line.startswith("- `_shared/patterns/")
            and "00-index.md" not in line
        ]
        self.assertEqual(
            manual_entries,
            [],
            "comms-polish must not maintain a second catalog filename list; "
            "discover category files from 00-index.md's generated inventory",
        )


class MetadataValidation(unittest.TestCase):
    """The metadata table's Severity/Enforcement values are closed vocabularies
    (VALID_SEVERITY / VALID_ENFORCEMENT). A typo must break the loader loudly —
    the same way a malformed heading or duplicate id does — not pass through
    silently into the projection as a bogus rating."""

    def test_unknown_severity_raises(self):
        text = ("### S1 — Significance inflation\n"
                "| Severity | Enforcement |\n"
                "| --- | --- |\n"
                "| bogussev | regex |\n")
        with self.assertRaises(ValueError) as ctx:
            catalog._parse_entries("fake.md", text)
        self.assertIn("unknown severity", str(ctx.exception))
        self.assertIn("bogussev", str(ctx.exception))

    def test_unknown_enforcement_raises(self):
        text = ("### S1 — Significance inflation\n"
                "| Severity | Enforcement |\n"
                "| --- | --- |\n"
                "| high | nonsense |\n")
        with self.assertRaises(ValueError) as ctx:
            catalog._parse_entries("fake.md", text)
        self.assertIn("unknown enforcement", str(ctx.exception))
        self.assertIn("nonsense", str(ctx.exception))

    def test_valid_values_pass(self):
        for sev in sorted(catalog.VALID_SEVERITY):
            for enf in sorted(catalog.VALID_ENFORCEMENT):
                text = (f"### S1 — Significance inflation\n"
                        f"| Severity | Enforcement |\n"
                        f"| --- | --- |\n"
                        f"| {sev} | {enf} |\n")
                entries = catalog._parse_entries("fake.md", text)
                self.assertEqual((entries[0].severity, entries[0].enforcement),
                                 (sev, enf))


if __name__ == "__main__":
    unittest.main()
