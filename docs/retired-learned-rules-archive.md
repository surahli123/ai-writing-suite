# Retired learned-rules archive

Rules removed from `_shared/learned-rules.md` when live maintainer state left the
shipped package (T0-1, feat/t0-1-user-state-boundary, 2026-07-22). Preserved here
because docs reference them; this file is historical record, not live rule state.
Consumers must never load rules from this file.

Known references at removal time: `docs/improvement-plan-deslop-landscape-2026-07-11.md`
task #31 (planned to take LR-001 through a Layer-3 eval as the D10 graduation proof —
the rule text below remains usable as that fixture); `reviews/2026-07-13-e2e-product-assets.md`
(cites LR-001 by line number as historical review evidence).

---

### LR-001 (removed 2026-07-22; was `status: proposed`, never active)

- **rule:** When polishing a structured analysis or diagnosis report, delete any opening
  paragraph that describes the section or asserts it is checkable, deterministic, or
  reproducible before the first finding. Open on the first substantive step, not on a
  description of what the section is about to do.
- **rationale:** 2026-06-14, SMA diagnosis-report narrative. The owner flagged a
  methodology-section preamble ("How an analyst reaches this read, with each step checkable
  against the data. The path is deterministic, so the same question lands the same way") as
  throat-clearing meta-commentary. Cutting it raised directness with zero information loss.
  Auto-generated reports recurringly prepend this kind of "here is how to read me" runway, so
  the correction repeats across cases.
- **scope:** comms-polish
- **date:** 2026-06-14
- **status at removal:** proposed
- **next-review at removal:** proposed 2026-06-14; past the 30-day mark — owner should
  promote, retire, or keep waiting. No Layer-3 eval pass and no user "make it active" at
  removal time.
- **source:** SMA_v2 report-narrative de-slop session; owner override of a section preamble,
  cross-checked against stop-slop ("meta-joiners / throat-clearing — delete").
