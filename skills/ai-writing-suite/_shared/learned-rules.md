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
    - scope     : comms-polish | voice-onboard | all
    - date      : YYYY-MM-DD it was approved
    - status    : proposed | active | retired
                  (proposed = approved by user, not yet eval-measured in Layer 3;
                   active   = trusted/eval-passed, applied on every run;
                   retired  = superseded — see the entry that replaced it)
    - source    : short note on the session that produced it (auditable trail)

  STATUS LIFECYCLE
  ----------------
  proposed --(Layer 3 eval passes, or user says "make it active")--> active
  active   --(a later entry supersedes it)--> retired

  HOW SUB-SKILLS USE IT
  ---------------------
  On start, read this file and apply every entry whose status is `active` and
  whose scope matches the running skill (`all` matches both). Ignore `proposed`
  and `retired` entries when deciding behavior — `proposed` rules are not yet
  trusted; `retired` rules have been superseded.
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
