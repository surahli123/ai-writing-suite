"""Document-level numeric consistency check (stdlib only).

WHY: a DS document can be clean sentence by sentence and still contradict
itself. The summary says retention rose 12% while the table says 11.6%, or a
breakdown's shares add up to 104%. No sentence-level tell catches that, and a
one-line "polish this" prompt does not look for it. Round-2 research
(notes/research-best-practices-round2-2026-11-01.md, R2-1) found no external
writing skill doing it well.

The check reports conflicts with their locations. It NEVER reconciles them:
which number is right is the author's call.

Two deterministic checks, deliberately narrow so false positives stay rare:

* near-miss: a number in the lead (the first paragraph) has the same unit as a
  different number in the body, the two are within 10% of each other, and the
  lead's exact value never appears in the body. This is the classic
  summary/body drift (12% vs 11.6%, 1.2M vs 1.25M).
* share-sum: one block (a paragraph or a run of list or table lines) has three
  or more percentages that look like shares of a whole (each 0-100, followed by
  a share word or in a list/table), and they total between 90 and 110 but not
  within 1.5 of 100.

Defined-term drift and promises in the title or lead are judgment calls. They
live in the comms-polish final-pass checklist, not here.
"""
import re

_NUM = re.compile(
    r"(?<![\w.])(?P<num>\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*(?P<unit>%|pp\b|percentage points?\b|[kKmMbB]\b|ms\b|x\b)?")
_SHARE_WORDS = re.compile(r"\b(?:of (?:users|customers|respondents|traffic|revenue|sessions|orders|the total)|share)\b", re.I)


def _blocks(text):
    """Split into blocks: paragraphs, but a run of list/table lines is one block."""
    return [b for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]


def _numbers(block):
    out = []
    for m in _NUM.finditer(block):
        raw = m.group("num").replace(",", "")
        unit = (m.group("unit") or "").lower()
        unit = {"percentage point": "pp", "percentage points": "pp"}.get(unit, unit)
        try:
            out.append((float(raw), unit, m.group(0).strip()))
        except ValueError:
            continue
    return out


def near_miss_conflicts(text, rel_tol=0.10):
    blocks = _blocks(text)
    if len(blocks) < 2:
        return []
    lead = _numbers(blocks[0])
    body_text = "\n\n".join(blocks[1:])
    body = _numbers(body_text)
    body_values = {(v, u) for v, u, _ in body}
    found = []
    for v, u, shown in lead:
        if not u or v == 0 or (v, u) in body_values:
            continue  # unitless numbers (years, counts) are too ambiguous; exact match = consistent
        for bv, bu, bshown in body:
            if bu == u and bv != v and abs(bv - v) / max(abs(v), abs(bv)) <= rel_tol:
                found.append(("near-miss", f"lead says {shown}, body says {bshown}"))
                break
    return found


def share_sum_conflicts(text):
    found = []
    for block in _blocks(text):
        lines = block.splitlines()
        listy = sum(1 for ln in lines if re.match(r"\s*(?:[-*•]|\d+[.)]|\|)", ln)) >= 2
        if not listy and not _SHARE_WORDS.search(block):
            continue
        pcts = [v for v, u, _ in _numbers(block) if u == "%" and 0 <= v <= 100]
        if len(pcts) < 3:
            continue
        total = sum(pcts)
        if 90 <= total <= 110 and abs(total - 100) > 1.5:
            found.append(("share-sum", f"shares in one block total {total:g}% (expected about 100%)"))
    return found


def check(text):
    """Return a list of (kind, detail) conflicts. Empty list = nothing found."""
    return near_miss_conflicts(text) + share_sum_conflicts(text)
