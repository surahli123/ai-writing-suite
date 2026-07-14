<!--
================================================================================
  learned-rules.md  —  HUMAN-GATED, APPEND-ONLY SELF-IMPROVEMENT LOG
================================================================================

  WHAT THIS IS
  ------------
  The single place approved self-improvement rules live. The suite's sub-skills
  (`comms-polish`, `voice-onboard`) READ this file on start and apply matching
  active rules. The self-improvement hook APPENDS to it — but ONLY after the user
  explicitly approves a proposed rule. See `_shared/self-improvement.md` for the
  full protocol. Anti-drift design: plan §6 (D6), risk R3.

  THE RULES OF THIS FILE
  ----------------------
  1. APPEND-ONLY. Never rewrite or delete an existing entry's rule text. To
     change a rule, append a NEW entry and set the old one's `status:` to
     `retired` (a one-line status flip is the only permitted edit to a past
     entry — its rule/rationale text stays as written, for audit).
  2. HUMAN-GATED. Nothing lands here without an explicit user "yes". The hook
     proposes; the user approves; only then does an entry appear.
  3. CORE LOGIC IS NEVER TOUCHED. Rules live here, not in any SKILL.md or in the
     pattern catalog. This file is the *only* mutable surface of the loop.

  ENTRY FORMAT (stable schema — keep every field)
  -----------------------------------------------
  Each entry is one `### LR-NNN` block with these fields, in this order:
    - id        : LR-001, LR-002, ... (zero-padded, never reused)
    - rule      : the imperative the skill should follow (one or two sentences)
    - rationale : why — grounded in a real session correction, not theory
    - scope     : comms-polish | comms-draft | comms-qa | voice-onboard | all
    - date      : YYYY-MM-DD it was approved
    - status    : proposed | active | retired | graduated
                  (proposed  = approved by user, not yet eval-measured in Layer 3;
                   active    = trusted/eval-passed, applied on every run;
                   retired   = superseded — see the entry that replaced it;
                   graduated = folded into the pattern catalog by a maintainer;
                               the log entry is a tombstone, applied from the
                               catalog, NOT re-applied from here on start.)
    - source    : short note on the session that produced it (auditable trail)

  STATUS LIFECYCLE
  ----------------
  proposed --(Layer 3 eval passes, or user says "make it active")--> active
  active   --(a later entry supersedes it)--> retired
  active   --(maintainer folds it into the catalog by hand)--> graduated

  PROMOTION PROCEDURE (proposed -> active; owner-gated)
  -----------------------------------------------------
  A `proposed` rule advances to `active` only through this procedure, so no rule
  sits in `proposed` forever unowned:
  - WHO INITIATES: the owner, at review time OR when a sub-skill's ON START read
    finds a `proposed` rule whose `date:` is more than 30 days old. In that case
    the skill PAUSES and asks, one line — "LR-NNN proposed since <date>: promote,
    retire, or keep waiting?" — and waits for the answer before touching the rule.
  - EVIDENCE THAT QUALIFIES: exactly one of (a) a Layer-3 eval pass, with the pass
    output pasted into the entry as evidence, or (b) an explicit user "make it
    active." Nothing else promotes a rule.
  - WHO EDITS STATUS: the agent, only after the user confirms — a one-line flip of
    `status: proposed` to `status: active`, never a rewrite of the rule text.
  See `_shared/self-improvement.md` (PROMOTION) for the full protocol.

  HOW SUB-SKILLS USE IT
  ---------------------
  On start, read this file and apply every entry whose status is `active` and
  whose scope matches the running skill (`all` matches both). Ignore `proposed`,
  `retired`, and `graduated` entries when deciding behavior — `proposed` rules are
  not yet trusted; `retired` rules have been superseded; `graduated` rules now
  live in the pattern catalog and are applied from there, so re-applying them here
  would double-count.
================================================================================
-->

# Learned Rules (append-only)

Approved, human-gated self-improvement rules for the AI Writing Suite. Read on
start by the sub-skills; appended to only on explicit user approval. See
`_shared/self-improvement.md` for the protocol.

<!-- ──────────────────────────────────────────────────────────────────────────
     EXAMPLE ENTRY (illustration only — NOT an active rule)
     This block shows the exact shape a real entry takes. It is intentionally
     marked status: retired and id LR-000 so no skill ever applies it. Delete
     it once real rules exist, or leave it as the format reference.
─────────────────────────────────────────────────────────────────────────── -->

### LR-000  (EXAMPLE — do not apply)

- **rule:** When polishing LinkedIn posts, do not flag a single leading rhetorical
  question as an AI tell; this author opens that way on purpose.
- **rationale:** Example only. In a real entry this cites a session where the user
  overrode the catalog's "engagement hook" flag because the opener was genuinely
  theirs, and the correction would recur on every LinkedIn post.
- **scope:** comms-polish
- **date:** 2026-06-06
- **status:** retired
- **source:** Example seed entry showing the schema. Not produced by a real
  session; kept as the format reference.

<!-- ──────────────────────────────────────────────────────────────────────────
     REAL ENTRIES START BELOW. The hook appends new `### LR-NNN` blocks here,
     one per approved rule, newest at the bottom.
─────────────────────────────────────────────────────────────────────────── -->

### LR-001

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
- **status:** proposed
- **next-review:** proposed 2026-06-14; now past the 30-day mark, so a sub-skill's
  ON START read surfaces it under the PROMOTION PROCEDURE — the owner should
  promote, retire, or keep waiting. No Layer-3 eval pass and no user "make it
  active" yet, so it stays `proposed` until one of those qualifies it.
- **source:** SMA_v2 report-narrative de-slop session; owner override of a section preamble,
  cross-checked against stop-slop ("meta-joiners / throat-clearing — delete").
