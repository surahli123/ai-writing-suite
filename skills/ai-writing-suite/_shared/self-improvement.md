<!--
================================================================================
  self-improvement.md  —  HUMAN-GATED SELF-IMPROVEMENT PROTOCOL (Layer 2)
================================================================================

  WHAT THIS IS
  ------------
  The suite-wide lifecycle hook that lets the skills get *better over time*
  WITHOUT silently rewriting themselves. It is referenced (not copied) by every
  sub-skill that opts in — in v1 that is `comms-polish` and `voice-onboard`.

  THE ONE RULE (read this before anything else)
  ---------------------------------------------
  This hook may only ever do TWO things autonomously:
    1. READ side files at the start of a session (voice-profile + learned-rules).
    2. PROPOSE candidate rules at the end of a session.
  It MUST NOT write anything until the user explicitly approves. Approved rules
  go to ONE place: `learned-rules.md` (append-only). Core SKILL.md logic is NEVER
  auto-edited. This is the anti-drift guarantee — see plan §6 (D6) and risk R3.

  WHY (product-owner framing)
  ---------------------------
  Treat learned rules like a feature flag rollout, not a model that retrains
  itself on its own outputs. An ungated self-improving system feeds on its own
  predictions and drifts — the writing equivalent of a recommender that keeps
  recommending what it already recommended. The human gate is the holdout check:
  no rule ships to the "production" rule set until a person signs off, and (in
  Layer 3) until an eval measures it.
================================================================================
-->

# Self-Improvement Protocol (human-gated, append-only)

This is the shared spec for the suite's self-improvement hook. Sub-skills point
here instead of restating it, so the gate behaves identically everywhere.

## The contract in one line

Read learned rules on start. Propose new ones on end. Append only what the
user explicitly approves. Never auto-edit core skill logic.

## Lifecycle

### ON START — read the side files (no writes)

Before doing the sub-skill's actual work, read these two files if they exist:

1. `_shared/voice-profile.md` — the learned voice (owned by `voice-onboard`).
2. `_shared/learned-rules.md` — approved, human-gated improvements (this file's
   sibling). Apply any rule whose `status: active` and whose scope matches the
   current task (e.g. a rule scoped to `comms-polish` is ignored by
   `voice-onboard`).

Degrade gracefully: if either file is missing, do not error and do not block.
Note briefly that it was absent and continue with defaults. These are bias
signals, never hard dependencies (same posture as comms-polish voice matching).

### ON END — propose candidate rule(s), then STOP

After completing the session's work, look back at what happened and ask: *did a
repeatable correction surface that the catalog / profile / checklist does not
already cover?* Good candidates come from:

- A correction the user made that would recur ("I always cut that opener").
- A pattern the existing catalog missed or over-flagged.
- A voice-extraction judgment the user overrode.

If nothing repeatable surfaced, say so and propose nothing. Do not manufacture a
rule to look productive — a noisy rule log is worse than a short one.

If a candidate exists, **present it to the user** in the proposed-rule shape
(see `learned-rules.md` for the field schema) with:

- the proposed rule text,
- a one-line rationale grounded in *this* session (cite what happened),
- the scope it would apply to (`comms-polish`, `comms-draft`, `comms-qa`,
  `voice-onboard`, or `all`),
- a note that in Layer 3 this rule will be eval-measured before it counts as
  trusted (do not build or run that eval here — just reference it).

Then **stop and wait.** This is the gate.

### ON APPROVAL — append, nothing else

Only on an explicit "yes" / "approve" / "add it" from the user:

- Append ONE entry to `_shared/learned-rules.md` using the documented format
  (id, rule, rationale, scope, date, status, source).
- Set `status: proposed` until Layer 3's eval has measured it; the user may say
  "make it active" to promote a rule they trust without waiting.
- Stamp the date and a short source-session note so the log stays auditable.
- Do NOT touch any SKILL.md, the pattern catalog, or the voice profile schema.
  Approved rules live ONLY in `learned-rules.md`.

If the user says no, or edits the wording, follow their version exactly. Never
append a rule they did not approve. Never append more than they approved.

### PROMOTION — advance a `proposed` rule to `active` (owner-gated)

`proposed` means the user approved the rule but it is not yet trusted for
every-run application. Promotion is the step that makes it `active`, and it
follows a fixed procedure so no rule sits in `proposed` forever with no one
responsible for it:

- **Who initiates:** the product owner — either at a review, or when a sub-skill's
  ON START read surfaces a `proposed` rule whose `date:` is more than 30 days old.
  In that second case the skill must PAUSE and ask the user, in one line: "LR-NNN
  has been proposed since <date> — promote, retire, or keep waiting?" It does
  nothing to the rule until the user answers.
- **What evidence qualifies:** exactly one of (a) a Layer-3 eval pass, with the
  pass output pasted into the rule's entry as its evidence, or (b) an explicit
  user "make it active." Nothing else promotes a rule.
- **Who edits status:** the agent, and only after the user confirms. The edit is a
  single-line change of `status: proposed` to `status: active` on that entry — no
  rewrite of the rule text, consistent with the append-only rule.

### GRADUATION — fold stable rules into the catalog (human-gated, maintainer-run)

`learned-rules.md` is append-only, so its on-start read cost grows with every approved
rule. Graduation keeps the log small WITHOUT weakening the anti-drift gate:

- **Who:** the maintainer (a human), never this hook autonomously. The hook proposes and
  appends; it does NOT graduate.
- **When:** a rule is `status: active`, has proven stable across sessions, and (Layer 3) has
  passed its eval.
- **What:** the maintainer folds the rule's substance into the right catalog file
  (`_shared/patterns/...`) or sub-skill reference by hand — the same way any catalog edit is
  made — then sets the `learned-rules.md` entry to `status: graduated` (a status edit on its
  own line, noting where it landed). The rule now lives in the catalog; the log entry is a
  tombstone, not an active rule the hook re-applies on start.
- **Why it's safe:** the "never auto-edit the catalog" rule (below) is untouched. Graduation
  is a deliberate human edit, identical in trust to writing the catalog in the first place.
  The hook gains no new power — it still only reads on start and proposes on end.

## What this hook must NEVER do

- Auto-edit core logic (any `SKILL.md`, `_shared/patterns/`, the voice-profile
  schema headers). Out of bounds, always.
- Append a rule without explicit approval.
- Silently overwrite or rewrite existing learned rules — the log is append-only.
  Superseding a rule = append a new entry that references the old id and set the
  old one's `status: retired` (a status edit on its own line, not a rewrite of
  its rule text).

## Degradation on RovoDev (and other constrained hosts) — R2

RovoDev has no skill auto-triggering and a reduced toolset (Read/Write/Edit/
Bash/Grep, no Skill tool). This protocol is built to survive that:

- **No auto-trigger needed.** The hook is plain instructions inside a SKILL.md,
  not an event listener. ON START / ON END run whenever the sub-skill runs,
  however the sub-skill was invoked (explicit invocation on RovoDev).
- **File-read only on start.** Reading `voice-profile.md` + `learned-rules.md`
  uses Read/Grep — available everywhere. No MCP, no special tooling.
- **Append uses Edit/Write.** Adding one entry to `learned-rules.md` needs only
  Edit (or Write) — both present on RovoDev.
- **The gate is conversational, not tool-based.** "Propose → user says yes →
  append" works in any chat loop and needs no Skill/Task/Agent machinery.
- If even file writes are unavailable, degrade to: print the proposed rule entry
  and ask the user to paste it into `learned-rules.md` themselves. The gate and
  the append-only discipline still hold.
