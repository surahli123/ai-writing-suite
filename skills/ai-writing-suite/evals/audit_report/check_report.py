#!/usr/bin/env python3
"""Deterministic OUTPUT-CONTRACT checker for comms-polish detect/review reports.

WHAT THIS IS (and is not). This is an output-contract check, NOT behavioral
coverage: it verifies that a report's STRUCTURE matches the Audit Report Contract
in `skills/comms-polish/SKILL.md` — sections present, in order; each finding
carries a quoted snippet, a catalog tell-id, a why, and a shown fix, in that exact
field order; every tell-id resolves against the live `_shared/patterns/` registry.
It never judges whether the prose is *right* (was this really S1? is the fix
good?) — claim polarity and semantic quality in free prose are not decidable by
stdlib regex, and pretending otherwise is the rigged-checker trap (see
reviews/2026-07-13-advisor-eval-method.md Q1-Q2). Structure is honestly
checkable; semantics is not. So we check structure.

CONFORMANCE MODEL (byte-literal structure, normalized punctuation) — see the
matching note in SKILL.md's Audit Report Contract. Section headings, the four
field markers, their order, and the tier names are byte-literal: that rigidity is
what makes two reports diffable. The ONE normalization is punctuation style for
quoted snippets (straight / typographic / guillemet quotes all count, a leading
BOM is stripped) because paste-from-Word and model output both carry typographic
quotes routinely, and rejecting those would be a false positive, not a caught
violation.

Stdlib only. No network, no key. Importable and runnable
(`python3 -m audit_report.run_report_contract`).
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# evals/audit_report/ -> evals/ -> <suite-root>, so `import aiws` resolves to
# the sibling aiws/ package (same convention as evals/kb_lint.py, smoke_test.py).
SUITE_ROOT = os.path.dirname(os.path.dirname(HERE))
if SUITE_ROOT not in sys.path:
    sys.path.insert(0, SUITE_ROOT)

# The catalog registry is parsed in ONE place — aiws.catalog. This module's own
# `_CATALOG_HEADER`/`load_catalog_ids` were folded into it (architecture review
# 2026-07-13, item 2); re-exported here so importers of check_report still work.
from aiws.catalog import load_catalog_ids  # noqa: E402  (path set above)

TIERS = ("Critical", "Moderate", "Minor")
FIELD_ORDER = ("Quote", "Tell", "Why", "Fix")

# One finding's required field line: `**Quote:** ...`, `**Tell:** ...`, etc.
# Only the four contract fields are captured — any other bold line (extra
# commentary) is invisible to this regex and doesn't perturb the ordering check.
_FIELD_LINE = re.compile(r"^\*\*(Quote|Tell|Why|Fix):\*\*\s*(.*)$")
_TELL_ID = re.compile(r"^([A-Za-z]+\d+)\s+[—-]\s+")
_LEAD = re.compile(r"^\*\*Biggest problem:\*\*\s*(.+)$")
_SCORE = re.compile(r"^\*\*AI-tell score:\*\*\s*(\d{1,3})\s*/\s*100\b")
_H2 = re.compile(r"^##\s+(.+?)\s*$")
_BULLET = re.compile(r"^-\s+", re.MULTILINE)
_FENCE = re.compile(r"`[^`]+`")

# Quote delimiter pairs accepted for a "quoted snippet" wherever the contract
# requires one (**Quote:** value, or the shown replacement inside **Fix:**).
# Field MARKERS themselves stay byte-literal (see module docstring) — this is
# the one normalized dimension: typographic-quote style, not structure.
_QUOTE_PAIRS = [('"', '"'), ("“", "”"), ("\xab", "\xbb")]


def _normalize(text):
    """Strip a leading byte-order-mark. The only input normalization step."""
    return text.lstrip("﻿")


def _contains_quote_pair(value):
    """True if `value` contains a properly ordered open/close quote pair
    (straight, typographic, or guillemet) — i.e. an actual quoted snippet is
    present, not merely a bare quote character or none at all."""
    for lo, hi in _QUOTE_PAIRS:
        if lo in value and hi in value and value.index(lo) < value.rindex(hi):
            return True
    return False


def _is_quoted(value):
    return _contains_quote_pair(value.strip())


def _has_shown_replacement(value):
    """A Fix value is 'shown' when it carries a quoted snippet or a fenced
    code span — not merely a prose description of what to do."""
    v = value.strip()
    return bool(_FENCE.search(v)) or _contains_quote_pair(v)


def extract_fenced_report(text):
    """Return the content of the first ``` fenced code block in `text`, or
    None if there is none.

    Shared helper so a worked example embedded in prose documentation (e.g.
    comms-polish/references/audit-report-format.md) can fence its canonical
    report — keeping it out of the doc's own rendered heading structure —
    while an eval extracts exactly that text and checks it against the same
    contract a live report must satisfy.
    """
    m = re.search(r"```[^\n]*\n(.*?)```", text, re.DOTALL)
    return m.group(1) if m else None


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


def _split_tier_bullets(body_lines):
    """Split a tier's body into top-level `- ` bullet blocks.

    Each block is the text between one `- ` bullet marker and the next (or
    end of tier). The tier's italic definition line (before the first bullet)
    is not a bullet and is not returned here — it's checked separately.
    """
    text = "\n".join(body_lines)
    matches = list(_BULLET.finditer(text))
    blocks = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        blocks.append(text[start:end])
    return blocks


def _check_one_finding(tag, block, catalog_ids, violations):
    """Ordered state-machine check: Quote -> Tell -> Why -> Fix, exactly once
    each, in that order. Any reordering, duplication, or omission is a single
    'fields must appear in order' violation — the shape itself is wrong, so
    per-field content isn't evaluated in that case."""
    field_lines = []
    for raw in block.splitlines():
        m = _FIELD_LINE.match(raw.strip())
        if m:
            field_lines.append((m.group(1), m.group(2)))

    names = [n for n, _ in field_lines]
    if names != list(FIELD_ORDER):
        violations.append(
            f"{tag}: fields must appear in order {list(FIELD_ORDER)} exactly "
            f"once each, got {names}")
        return

    values = dict(field_lines)

    if not _is_quoted(values["Quote"]):
        violations.append(f"{tag}: **Quote:** is not a quoted snippet")

    tm = _TELL_ID.match(values["Tell"])
    if not tm:
        violations.append(f"{tag}: missing/malformed **Tell:** id (want `X9 — name`)")
    elif tm.group(1) not in catalog_ids:
        violations.append(
            f"{tag}: tell id '{tm.group(1)}' not in _shared/patterns/ catalog")

    if not values["Why"].strip():
        violations.append(f"{tag}: **Why:** is empty")

    if not _has_shown_replacement(values["Fix"]):
        violations.append(
            f"{tag}: **Fix:** must show the replacement (quoted or fenced), "
            f"not just describe it")


def _check_findings(tier, body, catalog_ids, violations):
    """Validate every finding in one tier's body lines.

    `- None.` is the sanctioned empty-tier marker, but ONLY when it is the
    tier's single bullet — mixed with real findings it's a contract violation
    (a reader can't tell if the tier is empty or not), not a shortcut that
    skips checking the rest of the tier.
    """
    blocks = _split_tier_bullets(body)
    none_blocks = [b for b in blocks if b.strip().rstrip(".") == "None"]
    real_blocks = [b for b in blocks if b.strip().rstrip(".") != "None"]

    if none_blocks and real_blocks:
        violations.append(
            f"{tier}: '- None.' bullet mixed with {len(real_blocks)} actual "
            f"finding(s) in the same tier")
        return
    if none_blocks:
        if len(none_blocks) > 1:
            violations.append(f"{tier}: multiple '- None.' bullets")
        return
    if not real_blocks:
        violations.append(f"{tier}: tier has neither a finding nor '- None.'")
        return

    for n, block in enumerate(real_blocks, 1):
        _check_one_finding(f"{tier} finding #{n}", block, catalog_ids, violations)


def check_report(text, catalog_ids):
    """Return (ok, violations). ok == (violations == []).

    Enforces, in order: a plain-language (non-numeric) lead line; the three
    tiers Critical/Moderate/Minor present in order, each with an italic
    one-clause definition and well-formed findings (ordered Quote->Tell->Why->
    Fix, `- None.` never mixed with real findings); a non-empty 'What already
    reads well' section; and — only if a score line is present — that it is
    the single, final non-blank line of the whole report and 0-100.
    """
    text = _normalize(text)
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

    # 4. Score optional; if present it must be the ONLY score line, valid
    #    0-100, come after 'reads well', and be the FINAL non-blank line of
    #    the whole report — no trailing commentary after it.
    score_idxs = [i for i, ln in enumerate(lines) if _SCORE.match(ln.strip())]
    if len(score_idxs) > 1:
        violations.append("score: more than one **AI-tell score:** line found")
    elif score_idxs:
        score_idx = score_idxs[0]
        val = int(_SCORE.match(lines[score_idx].strip()).group(1))
        if not 0 <= val <= 100:
            violations.append(f"score: {val} outside 0-100")
        if well and score_idx < sections[well][0]:
            violations.append("score: must come after 'What already reads well'")
        last_nonblank = next(
            (i for i in range(len(lines) - 1, -1, -1) if lines[i].strip()), None)
        if last_nonblank != score_idx:
            violations.append(
                "score: must be the final non-blank line of the report "
                "(trailing content found after it)")

    return (not violations), violations
