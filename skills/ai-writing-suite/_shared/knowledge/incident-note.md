# Incident notes and postmortems: timeline, cause vs hypothesis, owned actions

> **Generic best-practice entry.** Compiled from public postmortem practice (SRE
> postmortem-culture writing, ideas only) and the round-2 research note
> `notes/research-best-practices-round2-2026-11-01.md`. Open-source KB; a
> company fork replaces it with its own incident template via the same slot
> (`README.md`).

## Principle

An incident note serves two readers. The on-call reader needs current status and
the next update time. The later reader needs what happened and what changes.
Keep confirmed facts, hypotheses and unknowns visibly separate. A cause stays a
hypothesis until something confirmed it.

## Moves

- **Live update slots:**
  - status (investigating / mitigated / resolved);
  - impact;
  - what we know;
  - what we don't know;
  - the next action and when the next update comes.
- **Postmortem slots:**
  - a summary;
  - impact, with numbers and window;
  - a timeline in a single time zone, in chronological order;
  - the cause (a cause, not a symptom), labeled confirmed or leading hypothesis;
  - contributing factors;
  - action items, each with an owner and a date.
- **Keep timelines as timelines.** Don't restructure a timestamped list into
  prose or answer-first order.
- **Blameless wording.** Name the system or process step that failed, not the
  person.

## Before / After

- **Before:** The latency spike was caused by the deploy, and we fixed it with a
  rollback.
- **After:** p95 rose from 340ms to 910ms at 14:12 UTC, 14 minutes after the
  13:58 deploy. Traffic was also up 22% that hour. Leading hypothesis (not
  confirmed): the cache eviction change in that deploy. Rolled back at 16:00;
  p95 was back to 360ms by 16:10, which supports but does not prove the
  hypothesis.

## When this matters most

Incident channel updates, postmortems, data-quality incident notices, and any
message read under time pressure by people deciding what to do next.

## Sources

- SRE postmortem-culture practice (Google SRE workbook; ideas only, wording our
  own).
- Round-2 research synthesis (`notes/research-best-practices-round2-2026-11-01.md`,
  R2-5: postmortem slots; cause vs symptom; blameless wording).

## Related entries

- `decision-memo.md` — action items follow the same owned-and-dated rule as decision and status slots.
- `structure.md` — an incident note is the case where answer-first does *not* apply to the timeline: keep chronological order there.
