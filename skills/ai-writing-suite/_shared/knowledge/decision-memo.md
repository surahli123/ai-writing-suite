# Decision memos and status updates: the call, the options, the ask

> **Generic best-practice entry.** Compiled from public practice on decision
> memos and architecture decision records (MADR, MIT/CC0), status-update
> formats, and the round-2 research note
> `notes/research-best-practices-round2-2026-11-01.md`. Open-source KB; a company
> fork replaces it with its own templates via the same slot (`README.md`).

## Principle

A decision memo asks the reader to accept a judgment, so it owes the reader the
judgment itself, the options it beat, the trade-off it accepts, and what would
change it. A status update is shorter but similar. It owes the reader the call
(on track or not), the ask, and items that are dated and owned. Both report
position, not effort.

## Moves

- **Decision memo slots:**
  - the recommendation, in one line;
  - whether the decision is reversible, and how;
  - the options considered and why each lost;
  - the trade-off accepted;
  - what would change the decision (a metric, a date, an event);
  - the owner and the decision date.

  A missing slot gets `[NEEDS: …]`; never invent a rejected option or a
  threshold.
- **Status update slots:**
  - the call first (on track / at risk / blocked);
  - any ask or FYI up front;
  - then items, each with an owner and a date.

  Say "blocked on X, ETA unknown" rather than inventing a date.
- **Position, not effort.** "Forecast v4 shipped to supply Tuesday" beats
  "worked hard on the forecast this week".
- **Answer-first only where a judgment is asked.** Timelines, runbooks, logs and
  thank-you notes keep their own order; see `structure.md`.

## Before / After

- **Before:** After extensive analysis of several options, we believe it may be
  worth considering moving forward with vendor B.
- **After:** Recommendation: move to vendor B (reversible until the March
  renewal). Vendor A lost on latency (p95 420ms vs 180ms) and in-house lost on
  cost. We accept 15% higher list price for the latency. We would revisit if A
  closes the latency gap before renewal. Owner: Dana, decide by Nov 15.

## When this matters most

Investment and tooling decisions, launch go/no-go calls, weekly status posts,
and any message where the reader must approve, block, or act.

## Sources

- MADR (Markdown Architectural Decision Records, MIT/CC0): options, decision
  drivers, consequences. Ideas only.
- Round-2 research synthesis (`notes/research-best-practices-round2-2026-11-01.md`,
  R2-5: decision memo and status update slot lists). Numeric caps from the
  sources were deliberately dropped.

## Related entries

- `structure.md` — the recommendation-first order is BLUF; this entry adds the slots a decision owes.
- `experiment-readout.md` — a readout often supplies the evidence a decision memo cites.
- `incident-note.md` — a postmortem's action items follow the same owned-and-dated rule.
