# Audit Report Format — worked example

This is a complete `detect`/`review` report that satisfies the **Audit Report
Contract** in `SKILL.md` (`## Output`). It shows the required sections, order, and
the four-part finding shape on a real draft. Copy the *shape*, not the wording —
the prose is genre-appropriate and yours to vary; the structure is the contract.

The tell ids used below (`S1`, `H2`, `T1`, `F1`) are real entries in
`_shared/patterns/`. Every `**Tell:**` line must name an id that exists there — an
invented id is a contract violation the eval checker (`evals/audit_report/`) will
reject.

---

## Example draft under audit

> Our new dashboard represents a truly transformative leap forward for the team.
> It's important to note that it may, in some cases, help surface insights. The
> dashboard is fast, clean, and intuitive. We built it — from the ground up — to
> empower everyone.

## The report

Fenced below (not rendered as headings) so the eval
(`evals/audit_report/test_report_contract.py`) can extract this exact text with
`extract_fenced_report()` and check it against the same contract a live report
must satisfy — the canonical example has to pass its own checker, or it's
teaching the wrong shape.

```
**Biggest problem:** the draft claims importance ("transformative leap forward")
instead of showing what the dashboard actually does, so it reads as promotional AI
filler rather than a real update.

## Critical
*Tells that make the whole piece read as machine-written at a glance, or that distort meaning or trust.*

- **Quote:** "represents a truly transformative leap forward"
  **Tell:** S1 — Significance inflation
  **Why:** asserts importance the reader can't verify; the draft names no concrete change, so the fix asks for one instead of inventing it.
  **Fix:** "[NEEDS: what the dashboard changes for the team]"

## Moderate
*Clear tells a careful reader notices, but that don't dominate the piece.*

- **Quote:** "It's important to note that it may, in some cases, help surface insights."
  **Tell:** H2 — Excessive / stacked hedging
  **Why:** three hedges ("may", "in some cases", "help") stack until the sentence claims nothing; one hedge keeps the author's real uncertainty.
  **Fix:** "It may help surface insights."
- **Quote:** "fast, clean, and intuitive"
  **Tell:** T1 — Rule of three
  **Why:** a padded three-adjective list; "fast" is the one claim a reader could check.
  **Fix:** "The dashboard is fast."

## Minor
*Cosmetic or low-frequency tells only a scan catches.*

- **Quote:** "We built it — from the ground up — to empower everyone."
  **Tell:** F1 — Em / en dashes
  **Why:** a parenthetical em-dash aside in the AI-favored cadence; the interruption adds nothing.
  **Fix:** "We built it for everyone."

## What already reads well
- Nothing here reads well yet: every sentence carries a flagged pattern.

**Coverage:** checked by rule: vocabulary, punctuation, structure patterns; by judgment: overstepping, narrative shape; not checked: voice profile (none loaded).

**AI-tell score:** 58/100 (surface patterns only, not authorship)
```
