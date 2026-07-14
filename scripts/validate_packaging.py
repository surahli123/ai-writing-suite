#!/usr/bin/env python3
"""Packaging-surface validator (CI B1 guard) — stdlib-only, no network.

CI previously ran only the evals; the *packaging body* (JSON manifests + skill
frontmatter) had no red check, so a manifest could go stale or a SKILL.md could
load with empty metadata and every test would still pass. This script closes
that gap. It runs in CI (.github/workflows/ci.yml) and locally:

    python3 scripts/validate_packaging.py

Checks:
  1. Every packaging *.json manifest parses as JSON.
  2. The `name` field agrees across all manifests (marketplace root, marketplace
     plugin entry, Claude plugin.json, Codex plugin.json).
  3. The `version` field agrees across the versioned manifests (Claude + Codex).
  4. Every skills/*/SKILL.md frontmatter passes the frontmatter contract:
     a well-formed `---` block with non-empty `name:` and single-line
     `description:`, and no unquoted YAML flow-indicator at the start of a value.

The frontmatter predicate is imported from the canonical test
(skills/ai-writing-suite/evals/test_skill_manifests.py) rather than duplicated,
so both checks stay in lock-step.
"""

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUITE = os.path.join(ROOT, "skills", "ai-writing-suite")
EVALS = os.path.join(SUITE, "evals")

# Reuse the canonical frontmatter predicate (do not duplicate its logic).
sys.path.insert(0, EVALS)
import test_skill_manifests as tsm  # noqa: E402  (path set above)

# YAML flow-indicator / special chars that break an unquoted plain scalar when
# they appear as its first character (the class of bug that silently drops
# SKILL.md metadata on host parsers).
_UNSAFE_LEAD = set("[]{}&*!|>%@`,#?")


def _fail(errors, msg):
    errors.append(msg)


def check_manifests(errors):
    manifests = {
        "marketplace": os.path.join(ROOT, ".claude-plugin", "marketplace.json"),
        "claude-plugin": os.path.join(SUITE, ".claude-plugin", "plugin.json"),
        "codex-plugin": os.path.join(SUITE, ".codex-plugin", "plugin.json"),
    }
    parsed = {}
    for label, path in manifests.items():
        if not os.path.isfile(path):
            _fail(errors, f"missing manifest: {os.path.relpath(path, ROOT)}")
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                parsed[label] = json.load(fh)
        except json.JSONDecodeError as exc:
            _fail(errors, f"{os.path.relpath(path, ROOT)}: invalid JSON: {exc}")

    # name agreement across every name-bearing field
    names = {}
    if "marketplace" in parsed:
        m = parsed["marketplace"]
        names["marketplace.name"] = m.get("name")
        plugins = m.get("plugins") or []
        if plugins:
            names["marketplace.plugins[0].name"] = plugins[0].get("name")
    if "claude-plugin" in parsed:
        names["claude-plugin.name"] = parsed["claude-plugin"].get("name")
    if "codex-plugin" in parsed:
        names["codex-plugin.name"] = parsed["codex-plugin"].get("name")
    distinct_names = set(v for v in names.values() if v)
    if len(names) < 4:
        _fail(errors, f"expected >=4 name fields, found {sorted(names)}")
    if len(distinct_names) > 1:
        _fail(errors, f"manifest name mismatch: {names}")

    # version agreement across versioned manifests
    versions = {}
    for label in ("claude-plugin", "codex-plugin"):
        if label in parsed:
            versions[f"{label}.version"] = parsed[label].get("version")
    distinct_versions = set(v for v in versions.values() if v)
    if len(versions) < 2:
        _fail(errors, f"expected 2 versioned manifests, found {sorted(versions)}")
    if len(distinct_versions) > 1:
        _fail(errors, f"manifest version mismatch: {versions}")


def check_frontmatter(errors):
    skills_glob = os.path.join(SUITE, "skills", "*", "SKILL.md")
    paths = sorted(glob.glob(skills_glob))
    if len(paths) < 4:
        _fail(errors, f"expected >=4 SKILL.md, found {len(paths)}")
    for path in paths:
        rel = os.path.relpath(path, ROOT)
        fm = tsm._frontmatter(path)  # canonical predicate
        if not fm:
            _fail(errors, f"{rel}: no frontmatter '---' block")
            continue
        name = tsm._field(fm, "name")
        desc = tsm._field(fm, "description")
        if not name:
            _fail(errors, f"{rel}: missing/empty 'name:'")
        if not desc:
            _fail(errors, f"{rel}: missing/empty 'description:'")
        # YAML-safe scalar guard: an unquoted value must not start with a flow
        # indicator (e.g. a description that begins with '[NEEDS: ...]').
        for field, value in (("name", name), ("description", desc)):
            if value and value[0] not in "\"'" and value[0] in _UNSAFE_LEAD:
                _fail(errors, f"{rel}: '{field}:' starts with unquoted YAML "
                              f"indicator {value[0]!r} (quote the value)")


def main():
    errors = []
    check_manifests(errors)
    check_frontmatter(errors)
    if errors:
        print("PACKAGING VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("packaging validation OK: manifests parse, name/version agree, "
          "all SKILL.md frontmatter valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
