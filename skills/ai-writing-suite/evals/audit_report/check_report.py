#!/usr/bin/env python3
"""Deterministic OUTPUT-CONTRACT checker for comms-polish detect/review reports.

WHAT THIS IS (and is not). This is an output-contract check, NOT behavioral
coverage: it verifies that a report's STRUCTURE matches the Audit Report Contract
in `skills/comms-polish/SKILL.md` — sections present, in order; each finding
carries a quoted snippet, a catalog tell-id, a why, and a shown fix; every tell-id
resolves against the live `_shared/patterns/` registry. It never judges whether the
prose is *right* (was this really S1? is the fix good?) — claim polarity and
semantic quality in free prose are not decidable by stdlib regex, and pretending
otherwise is the rigged-checker trap (see reviews/2026-07-13-advisor-eval-method.md
Q1-Q2). Structure is honestly checkable; semantics is not. So we check structure.

The point of the contract is diffability: two detect runs on one draft should
produce reports a reader can line up. This checker enforces exactly the skeleton
that makes that possible, and nothing it cannot honestly verify.

Stdlib only. No network, no key. Importable and runnable
(`python3 -m audit_report.run_report_contract`).
"""

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
# evals/audit_report/ -> evals/ -> <suite-root>/_shared/patterns
PATTERNS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(HERE)), "_shared", "patterns")

TIERS = ("Critical", "Moderate", "Minor")

# `### S1 — Significance inflation` -> id "S1". The em-dash separator matches the
# catalog's own header shape (00-index.md documents `### <id> — <name>`).
_CATALOG_HEADER = re.compile(r"^###\s+([A-Za-z]+\d+)\s+[—-]\s+(.+)$")
# A finding's `**Tell:**` line: capture the leading id token before the em-dash.
_TELL_ID = re.compile(r"^\*\*Tell:\*\*\s*([A-Za-z]+\d+)\s+[—-]\s+")
_LEAD = re.compile(r"^\*\*Biggest problem:\*\*\s*(.+)$")
_SCORE = re.compile(r"^\*\*AI-tell score:\*\*\s*(\d{1,3})\s*/\s*100\b")
_H2 = re.compile(r"^##\s+(.+?)\s*$")


def load_catalog_ids(patterns_dir=PATTERNS_DIR):
    """Return the set of tell ids declared in _shared/patterns/*.md.

    This is the live registry a finding's tell-id must resolve against, so the
    checker can never drift from the catalog: rename a tell in the catalog and a
    report citing the old id fails here.
    """
    ids = set()
    for name in sorted(os.listdir(patterns_dir)):
        if not name.endswith(".md") or name.startswith("00-"):
            continue
        with open(os.path.join(patterns_dir, name), encoding="utf-8") as fh:
            for line in fh:
                m = _CATALOG_HEADER.match(line.rstrip("\n"))
                if m:
                    ids.add(m.group(1))
    return ids


def _is_italic_clause(line):
    """True for a one-clause italic definition line: *...* but not **bold**."""
    s = line.strip()
    return (len(s) >= 3 and s.startswith("*") and s.endswith("*")
            and not s.startswith("**") and not s.endswith("**"))


def _sections(lines):
    """Map each `## Heading` to (start_index, list_of_body_lines_until_next_h2)."""
    out = {}
    order = []
    cur = None
    for i, line in enumerate(lines):
        m = _H2.match(line)
        if m:
            cur = m.group(1).strip()
            out[cur] = (i, [])
            order.append(cur)
        elif cur is not None:
            out[cur][1].append(line)
    return out, order


def _check_findings(tier, body, catalog_ids, violations):
    """Validate every finding block under one tier's body lines.

    A finding starts at a `- **Quote:**` bullet and runs until the next bullet.
    `- None.` is the sanctioned empty-tier marker and is skipped.
    """
    text = "\n".join(body)
    if re.search(r"^-\s*None\.?\s*$", text, re.MULTILINE):
        return
    # Split on top-level `- ` bullets. blocks[0] is the preamble BEFORE the first
    # bullet (the tier's italic definition line) — not a finding; drop it.
    blocks = re.split(r"^-\s+", text, flags=re.MULTILINE)
    findings = [b for b in blocks[1:] if b.strip()]
    if not findings:
        violations.append(f"{tier}: tier has neither a finding nor '- None.'")
        return
    for n, block in enumerate(findings, 1):
        tag = f"{tier} finding #{n}"
        qm = re.search(r"\*\*Quote:\*\*\s*(.+)", block)
        if not qm:
            violations.append(f"{tag}: missing **Quote:** line")
        elif '"' not in qm.group(1):
            violations.append(f"{tag}: **Quote:** is not a quoted snippet")
        tm = None
        for bl in block.splitlines():
            tm = _TELL_ID.match(bl.strip())
            if tm:
                break
        if not tm:
            violations.append(f"{tag}: missing/malformed **Tell:** id (want `X9 — name`)")
        elif tm.group(1) not in catalog_ids:
            violations.append(
                f"{tag}: tell id '{tm.group(1)}' not in _shared/patterns/ catalog")
        if not re.search(r"\*\*Why:\*\*\s*\S", block):
            violations.append(f"{tag}: missing **Why:** line")
        if not re.search(r"\*\*Fix:\*\*\s*\S", block):
            violations.append(f"{tag}: missing **Fix:** line")


def check_report(text, catalog_ids):
    """Return (ok, violations). ok == (violations == []).

    Enforces, in order: a plain-language (non-numeric) lead line; the three tiers
    Critical/Moderate/Minor present in order, each with an italic one-clause
    definition and well-formed findings; a non-empty 'What already reads well'
    section; and — only if a score line is present — that it sits after that
    section and is 0-100.
    """
    violations = []
    lines = text.splitlines()

    # 1. Lead line: first non-blank line, plain words (not purely a number).
    first = next((ln for ln in lines if ln.strip()), "")
    lead = _LEAD.match(first.strip())
    if not lead:
        violations.append("lead: first line is not `**Biggest problem:** <sentence>`")
    elif not re.search(r"[A-Za-z]{3,}", lead.group(1)):
        violations.append("lead: biggest-problem line has no plain-language content")

    sections, order = _sections(lines)

    # 2. Tiers present, in order, each defined, findings well-formed.
    present_tiers = [t for t in TIERS if t in sections]
    if present_tiers != list(TIERS):
        violations.append(
            f"tiers: expected headings {list(TIERS)} in order, got {present_tiers}")
    else:
        seen_order = [h for h in order if h in TIERS]
        if seen_order != list(TIERS):
            violations.append(f"tiers: out of order — got {seen_order}")
        for tier in TIERS:
            _idx, body = sections[tier]
            defn = next((b for b in body if b.strip()), "")
            if not _is_italic_clause(defn):
                violations.append(
                    f"{tier}: missing italic one-clause tier definition under heading")
            _check_findings(tier, body, catalog_ids, violations)

    # 3. 'What already reads well' present and non-empty.
    well = next((h for h in sections if h.lower().startswith("what already reads well")), None)
    if not well:
        violations.append("missing '## What already reads well' section")
    elif not any(b.strip() for b in sections[well][1]):
        violations.append("'What already reads well' section is empty")

    # 4. Score optional; if present, valid range and placed after 'reads well'.
    score_idx = next((i for i, ln in enumerate(lines) if _SCORE.match(ln.strip())), None)
    if score_idx is not None:
        val = int(_SCORE.match(lines[score_idx].strip()).group(1))
        if not 0 <= val <= 100:
            violations.append(f"score: {val} outside 0-100")
        if well and score_idx < sections[well][0]:
            violations.append("score: must be the closing line, after 'What already reads well'")

    return (not violations), violations
