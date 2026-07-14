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
  **Why:** asserts importance the reader can't verify; no concrete change is named.
  **Fix:** "cuts the weekly report from three tools down to one screen"

## Moderate
*Clear tells a careful reader notices, but that don't dominate the piece.*

- **Quote:** "It's important to note that it may, in some cases, help surface insights."
  **Tell:** H2 — Excessive / stacked hedging
  **Why:** three hedges ("may", "in some cases", "help") stack until the sentence claims nothing.
  **Fix:** "It surfaces the three metrics the team checks every morning."
- **Quote:** "fast, clean, and intuitive"
  **Tell:** T1 — Rule of three
  **Why:** a padded three-adjective list where one specific claim would land harder.
  **Fix:** "loads in under a second"

## Minor
*Cosmetic or low-frequency tells only a scan catches.*

- **Quote:** "We built it — from the ground up — to empower everyone."
  **Tell:** F1 — Em / en dashes
  **Why:** a parenthetical em-dash aside in the AI-favored cadence; the interruption adds nothing.
  **Fix:** "We built it for the whole team."

## What already reads well
- "The dashboard is fast" is a plain, checkable claim — keep that register and give the rest of the draft the same concreteness.

**AI-tell score:** 58/100
```
