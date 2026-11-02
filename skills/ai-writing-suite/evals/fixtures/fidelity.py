"""Deterministic fidelity-class checker: catches strength and scope changes that
a literal `must_preserve` substring check cannot see.

WHY: the skill-lift v0 eval (notes/eval-lift-2026-11-01) found that the suite's
only measured lift over no skill is fewer meaning changes, and that bare models
drift on exactly these classes. Examples: "no evidence" softened to "no clear
evidence", "won't be ready until" turned into "expected by". Plan item T1-5
(2026-07-21) proposed this lane and it was never built. This checker covers the
cheap, regex-visible part of it. Judges still own everything subtler.

Scope is deliberately narrow. It compares one before/after pair and reports
`(class, detail)` tuples. It is used only on fixtures that opt in with
`fidelity_check: true` (PASS) or `fidelity_class` (gold-FAIL), because curated
legacy `after`s legitimately rewrite whole sentences.

Classes:
  scope         a scope word in `before` is missing from `after`
  approximator  "about/roughly/~ N" in `before`, but `after` states N bare
  units         "N pp / percentage points" in `before`, but `after` says "N%"
  significance  `before` says not significant / no detectable effect; `after`
                claims no effect and drops the significance wording
  interval      `before` carries a confidence interval; `after` drops it
  strength      a hedged or intent verb in `before` hardens in `after`
                (suggests->shows, may->will, hope/plan to->will, expect->will)
  added_qualification
                `after` adds a defensive qualification `before` never had
                ("does not by itself establish", "interpreted with caution",
                "further research is needed", "not necessarily"); the add-side
                twin of `strength` (Liao et al. 2026: review-flavored prompts
                make models add these, and AI judges reward them)
  status        a list item's status moves up the closed ladder
                planned < in progress < done ("Investigating" -> "Fixed").
                Items are aligned by entity (ticket ID, then a content-word key
                unique within the list), never by position, so a status swapped
                between two items is caught and a faithful reorder is not. Only
                runs when `before` has two or more list items. Items that can't
                be aligned are reported by `status_coverage()`, never as a pass.
"""
import re

SCOPE_WORDS = ("only", "all", "most", "every", "never", "first", "at least", "up to")
_APPROX = r"(?:about|roughly|approximately|around|nearly|almost|~)\s*(?:an?\s+)?"
_NUM = r"\d[\d,]*(?:\.\d+)?"
_PP = re.compile(r"(" + _NUM + r")\s*(?:pp\b|percentage points?\b)", re.I)
_PCT = r"\s*%"
_NOT_SIG = re.compile(r"\b(?:not (?:statistically )?significant|no (?:statistically )?significant|no detectable|not detectable)\b", re.I)
_NO_EFFECT = re.compile(r"\b(?:no effect|no impact|had no effect|has no effect|didn't work|did not work|does not work|made no difference|unaffected)\b", re.I)
_INTERVAL = re.compile(r"\b(?:CI|confidence interval|credible interval|interval)\b|±|\+/-", re.I)
_STRENGTH = (
    (re.compile(r"\b(?:suggests?|indicates?|points? to)\b", re.I), re.compile(r"\b(?:shows?|proves?|demonstrates?|confirms?)\b", re.I), "suggests->shows"),
    (re.compile(r"\b(?:may|might|could)\b", re.I), re.compile(r"\bwill\b|\b\w+'ll\b", re.I), "may->will"),
    (re.compile(r"\b(?:hope|plan|aim|intend)s? to\b", re.I), re.compile(r"\bwill\b|\b\w+'ll\b", re.I), "hope/plan to->will"),
    (re.compile(r"\bexpects?\b|\bexpected to\b", re.I), re.compile(r"\bwill\b|\b\w+'ll\b", re.I), "expect->will"),
)


_ADDED_QUAL = re.compile(
    r"\b(?:do(?:es)? not (?:by (?:itself|themselves) |on (?:its|their) own )?(?:establish|prove|imply|guarantee)"
    r"|(?:should|must) be interpreted with caution|interpret(?:ed)? with caution"
    r"|further (?:research|work|analysis|study) (?:is|would be) (?:needed|required|warranted)"
    r"|not necessarily|correlation (?:is not|does not imply) causation"
    r"|(?:by|on) (?:itself|themselves|its own|their own),? (?:this|these|it|they) (?:do|does) not)\b", re.I)


_STATUS_LADDER = (
    (0, "planned", re.compile(r"\b(?:planned|planning|next up|to ?do|not started|backlog|scheduled|proposed|queued|upcoming)\b", re.I)),
    (1, "in progress", re.compile(r"\b(?:in progress|investigating|working on|ongoing|underway|in review|blocked|debugging|testing|fixing|migrating|drafting|reviewing|rolling out|mitigat(?:ing|ed))\b", re.I)),
    (2, "done", re.compile(r"\b(?:done|fixed|resolved|shipped|completed?|merged|launched|released|closed|deployed|finished)\b", re.I)),
)
_LIST_ITEM = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+(.+?)\s*$", re.M)
_TICKET = re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b")
_STOP = {"the", "and", "for", "with", "from", "into", "that", "this", "then",
         "than", "about", "after", "before", "over", "under"}


def _items(text):
    return [m.group(1) for m in _LIST_ITEM.finditer(text)]


def _status(item):
    """(tier, label) of the earliest status word in the item, or None."""
    best = None
    for tier, label, rx in _STATUS_LADDER:
        m = rx.search(item)
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), tier, label)
    return None if best is None else (best[1], best[2])


def _content_key(item):
    words = set(re.findall(r"[a-z][a-z0-9]{3,}", item.lower())) - _STOP
    return {w for w in words if not any(rx.fullmatch(w) for _, _, rx in _STATUS_LADDER)}


def _unique_best(keys_from, keys_to, i, skip):
    """Index in keys_to sharing the most content words with keys_from[i], if unique."""
    scores = [(len(keys_from[i] & k), j) for j, k in enumerate(keys_to) if j not in skip]
    if not scores:
        return None
    top = max(s for s, _ in scores)
    winners = [j for s, j in scores if s == top]
    return winners[0] if top > 0 and len(winners) == 1 else None


def _align(before_items, after_items):
    """Map before index -> after index by entity, never by position.

    First a ticket ID that is unique in both lists; then a content-word key,
    accepted only when the best match is unique and mutual. Anything else stays
    unaligned (see status_coverage)."""
    pairs, used = {}, set()
    b_ids = [_TICKET.findall(i) for i in before_items]
    a_ids = [_TICKET.findall(i) for i in after_items]
    for bi, ids in enumerate(b_ids):
        if len(ids) == 1 and sum(ids[0] in b for b in b_ids) == 1:
            hits = [ai for ai, a in enumerate(a_ids) if ids[0] in a]
            if len(hits) == 1:
                pairs[bi] = hits[0]
                used.add(hits[0])
    b_keys = [_content_key(i) for i in before_items]
    a_keys = [_content_key(i) for i in after_items]
    for bi in range(len(before_items)):
        if bi in pairs or b_ids[bi]:
            continue
        ai = _unique_best(b_keys, a_keys, bi, used)
        if ai is not None and _unique_best(a_keys, b_keys, ai, set(pairs)) == bi:
            pairs[bi] = ai
            used.add(ai)
    return pairs


def _status_violations(before, after):
    b, a = _items(before), _items(after)
    if len(b) < 2 or len(a) < 2:
        return []
    out = []
    for bi, ai in sorted(_align(b, a).items()):
        sb, sa = _status(b[bi]), _status(a[ai])
        if sb and sa and sa[0] > sb[0]:
            out.append(("status", f"'{b[bi][:40]}': {sb[1]} -> {sa[1]}"))
    return out


def status_coverage(before, after):
    """`before` list items the status class could not align (never a pass).

    Empty when `before` has fewer than two list items (the class does not run).
    When `after` collapses to fewer than two items, every `before` item is
    unaligned, so a merge that also inflates a status can't pass silently."""
    b, a = _items(before), _items(after)
    if len(b) < 2:
        return []
    if len(a) < 2:
        return list(b)
    pairs = _align(b, a)
    return [item for i, item in enumerate(b) if i not in pairs]


def _has_word(text, w):
    return re.search(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])", text, re.I) is not None


def fidelity_violations(before, after):
    """Return a list of (class, detail) for strength/scope changes from before to after."""
    out = []
    for w in SCOPE_WORDS:
        if _has_word(before, w) and not _has_word(after, w):
            out.append(("scope", f"'{w}' dropped"))
    for m in re.finditer(_APPROX + "(" + _NUM + ")", before, re.I):
        n = m.group(1)
        if re.search(r"(?<![\d.])" + re.escape(n) + r"(?![\d])", after) and not re.search(_APPROX + re.escape(n), after, re.I):
            out.append(("approximator", f"approximate {n} stated as exact"))
    for m in _PP.finditer(before):
        n = m.group(1)
        if re.search(re.escape(n) + _PCT, after) and not re.search(re.escape(n) + r"\s*(?:pp\b|percentage points?\b)", after, re.I):
            out.append(("units", f"{n} percentage points became {n}%"))
    if _NOT_SIG.search(before) and _NO_EFFECT.search(after) and not _NOT_SIG.search(after):
        out.append(("significance", "not significant / not detectable became no effect"))
    if _INTERVAL.search(before) and not _INTERVAL.search(after):
        out.append(("interval", "confidence interval dropped"))
    for weak, strong, label in _STRENGTH:
        if weak.search(before) and not weak.search(after) and strong.search(after) and not strong.search(before):
            out.append(("strength", label))
    added = {m.group(0).lower() for m in _ADDED_QUAL.finditer(after)} - {m.group(0).lower() for m in _ADDED_QUAL.finditer(before)}
    for q in sorted(added):
        out.append(("added_qualification", f"added '{q}'"))
    out.extend(_status_violations(before, after))
    return out
