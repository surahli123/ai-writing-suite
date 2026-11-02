---
name: comms-shape
description: "Shape a document with its author before writing it: agree on the reader and the decision, pick a one-sentence thesis, build and sharpen an outline from the author's own notes, then fill it in without inventing facts (gaps become [NEEDS: ...]). Also pressure-tests whether an existing draft's argument holds, and handles polishing a draft while adding to it. Use when the user asks to draft, write up, or turn notes into a readout, memo, status update, incident note, email, or post; to pressure-test or defend a draft's argument before sending; or to polish text and add a section. Not for rewording text or reviewing how it reads (comms-polish), or for questions about the playbook (comms-qa)."
---

# comms-shape

Help the author decide what the document says before any of it is written, then
write it from what they decided.

A first draft generated from a brief plus a playbook comes out generic: the
structure is the model's, the emphasis is the model's, and the polish loops that
follow spend tokens scrubbing words without making the content the author's. This
skill moves the work to where changes are cheapest: the reader, the thesis, and the
outline. The author makes those choices; the skill offers options, asks the
questions a careful reviewer would ask, and then fills in only what was agreed.

Like the other sub-skills, it carries no pattern list of its own. It reads the
catalog under `_shared/patterns/`, the knowledge base under `_shared/knowledge/`,
and comms-polish's genre presets.

## Locating shared assets (suite root)

All `_shared/...` paths in this file are **suite-root-relative**. The suite root is
the installed directory that directly contains `_shared/` and the suite's router
`SKILL.md` (e.g. `.../ai-writing-suite/`). Do not resolve these paths against your
session's working directory. To find the root: start from this SKILL.md's own
location and walk up until a directory contains `_shared/`. If you cannot find it,
say so and ask for the suite's install path; do not guess or silently skip the
shared assets.

Resolve all mutable profile and learned-rules paths through
`_shared/state-location.md`; reference that resolver, never copy its rules here.

## Inputs

- **The request and the author's material** (required): notes, numbers, query
  results, an existing draft, a timeline. Facts come only from this material, the
  author's answers in this conversation, the knowledge base, or a source the author
  approves. Nothing else is a source.
- **The knowledge base** via `_shared/knowledge/INDEX.md`. Match the task against
  the index's Summary and Keywords columns and open the entries that apply. Genre
  entries (`experiment-readout.md`, `decision-memo.md`, `incident-note.md`, and a
  company fork's playbook pages) are **slot checklists for the outline**, not text
  to paste. Cite the entry filename when an outline choice came from it.
- **The voice profile** (optional) under resolved `<state>/voice-profiles/`. Follow
  `_shared/voice-lookup.md` for source order, genre matching, banner rejection,
  graceful degradation, and the one-offer rule.
- **Genre presets** via `skills/comms-polish/references/scenario-presets.md`
  (suite-root-relative): hard form constraints and what each genre leaves alone,
  including the "Parallel items" rules for lists, feeds, and cards.
- **The AI-tell catalog** via `_shared/patterns/00-index.md`, used as a negative
  checklist while filling (step 5).
- **The fact-to-interpretation protocol** via `_shared/fact-interpretation-boundary.md`.
  Before shaping anything, classify the source packet into confirmed facts,
  supported interpretations, and unanswered questions, and keep each claim's
  certainty.

Note absent optional inputs out loud; never block on them.

## Choose the request class

| Class | Recognized by | Flow |
| --- | --- | --- |
| (a) From notes or an idea | "write / draft / write up / turn these notes into…" (the default) | long or short path below |
| (b) Pressure-test | "pressure-test / defend / poke holes in / does my argument hold before I send" | Pressure-test below |
| (c) Mixed | existing text plus "add / expand / write a section" | Mixed mode below |
| (d) Explicit skip | the user says "no questions", "just draft it", or "skip the outline" | Explicit skip below |

- "Draft a decision memo recommending vendor B" with no notes is class (a), not a
  skip: the first step asks for the material.
- An ambiguous request with a draft attached ("look at this memo before I send
  it") gets **one** classifying question, wording or argument, and it counts
  against the three-question intake budget. Wording goes to comms-polish.
- **Size by genre.** Short: a Slack message, status update, or short email. Long:
  a readout, decision memo, incident note, or document. When unsure, use the long
  path.

## Long path (class a)

Two required stops: after the thesis and after the outline. Everything else
proceeds unless the author asks to slow down.

### 1. Intake

Ask at most three questions, in one message: who reads it, what decision or
action is wanted from them, and for the author's notes and data if none came with
the request. Ask for material first; do not ask what you can read. If the request
already answers all three, skip to step 2.

### 2. Thesis (required stop 1)

Propose 2-3 genuinely different one-sentence theses drawn from the author's
material (for example, lead with the decision, lead with the risk, lead with the
number). Say in a line what each framing emphasizes and what it leaves for later.
Do not say which is best and do not praise any. Stop and let the author pick, edit,
or write their own.

### 3. Outline (required stop 2)

Write the outline under the chosen thesis and the acceptance criteria for this document on five dimensions: **style** (register and voice for this reader), **format** (genre and its hard constraints from the preset), **length** (a target range), **content integration** (which facts and KB slots must appear), and **depth** (overview or detail, for what the reader must do).

Use `references/outline-template.md`. In the outline:

- Each talking point carries a provenance tag: *author* (from the material or an
  answer), *proposed* (a point the skill suggests, not yet approved), or
  `[NEEDS: what is missing]`.
- Fill the genre's slots from the KB entry (an effect needs baseline, unit,
  interval, n, and window; an incident separates facts, hypotheses, and unknowns).
  **Fill every slot the notes or the author's answers already hold first.** Mark
  `[NEEDS: ...]` only for what neither holds; never fill a gap yourself. A slot
  the genre usually has but this document does not need is left out, not marked.
- Plan the shape: where the stakes peak, what stays open, whether a competing
  reading is real. Only shape what the material motivates; never manufacture
  ambiguity, a loose end, or a peak (`_shared/patterns/narrative-shape.md`).
- For a parallel set (a status list, feed, or set of result cards), fix the item
  frame and the closed status vocabulary now, so every item comes out the same.

Send the sharpen questions (step 4) **in the same message** as the outline, then
stop. The author's reply both answers them and confirms the outline.

### 4. Sharpen (asked with the outline)

Pick the questions from `references/sharpen-questions.md` that this outline needs:

- **Defend.** At least one objection the author has not raised, the weakest
  point, and what would change the call. The author answers; point out where an
  answer is vague or does not match the material.
- **Provenance.** For each number: which query, dashboard, or run it came from.
  Never rule on whether it is true; flag a number that contradicts the author's
  own notes.
- **Framing.** Name a framing that looks inherited (a stock talking point, a
  source's angle) and offer an alternative. Do not say which is better.

Further sharpen rounds happen only when the author asks for them.

**Re-confirm** only when the thesis changes, a talking point is added or removed,
or a number changes. Otherwise proceed to step 5.

### 5. Fill

Write from the confirmed outline only. No new claims: a sentence that needs a fact
the outline does not hold gets `[NEEDS: ...]`. Before returning, check every
`[NEEDS]` against the notes and answers once more and fill any the material
already answers (an owner, a date, a count the author gave). Write long documents section by
section without stopping between sections unless the author asked to review each
one. The author may write a section themselves and ask for a light edit.

While writing:

- **Concrete from the material.** Name the specific thing the material names. If
  it is not there, mark `[NEEDS: ...]`.
- **Labels are claims.** A role or label the author did not state (calling a
  metric "primary" or "the mechanism metric", calling a group "the control")
  needs a source like any other claim. Use the author's own labels.
- **Supported relations only.** Add a cause, motive, significance, trend, or
  conclusion only when the classified source packet supports it. Keep possibility
  calibrated and co-occurrence as co-occurrence. When a requested relation lacks
  its link, write `[NEEDS: causal evidence]` (or an equally specific gap) instead
  of a plausible explanation. This applies to all new prose.
- **Rhythm follows the content** in running prose (catalog R1); a parallel set
  keeps one shape. Never add texture or asides that carry no information.
- **The catalog as a negative checklist.** Avoid the tells the genre preset
  weights: filler openers, inflated significance, forced rule-of-three, "not X but
  Y" theatrics, vague attribution, promotional adjectives, chatbot tics, and
  presumptions about what the reader thinks
  (`_shared/patterns/overstepping-presumption.md`).
- **Voice.** Bias word choice and cadence toward the loaded profile; with none,
  match the author's own material.

Then re-read the draft as if someone else wrote it: scan it against the catalog
(clusters, not single hits), check the shape plan held without invented
residue, and re-run the fact-to-interpretation check on every new sentence.

### 6. Final

- Run `skills/comms-polish/references/final-pass-checklist.md` over the document
  (suite-root-relative).
- If you can run Python, run `python3 tools/consistency_check.py <file>` from the
  suite root and report any conflict; never pick a winner.
- **Unsourced-claims check.** Every claim must trace to a ledger row with a
  source. Any claim that does not is a defect: fix it or mark it `[NEEDS: ...]`
  before returning. The check is expected to come back empty.
- Check the draft against the step-3 criteria and name any it misses.

## Short path (class a, short genres)

One message: a one-line thesis, the bullets you would write, and at most two
questions. One combined stop. Then write, run the final pass, and return.

## Pressure-test (class b)

The author brings a finished draft and wants to know whether the argument holds.

1. Reverse-outline it: the thesis the draft actually states and the points it
   actually makes, each tagged with where its support is (in the draft, in notes
   the author supplied, or nowhere).
2. Ask the sharpen questions (step 4) about that outline, in one message, and
   stop.
3. Do not rewrite unless asked. When the author wants changes to the argument,
   edit the reverse-outline, refill the affected sections (step 5) using the
   ledger, and run step 6. A request that is only about wording goes to
   comms-polish.

## Mixed mode (class c)

The user has text and wants it polished **and** extended.

- **The existing text is immutable source material.** Its facts, claims, numbers,
  names, and quotes survive; you may reorder, tighten, and de-AI the prose around
  them under comms-polish's rules, and apply polish authority to it: an existing
  author hypothesis may stay with an evidence note.
- **The addition goes through a mini outline.** Ask for the author's material for
  the new part (within the three-question budget), outline it with provenance
  tags, and stop once on that outline. New prose follows draft authority: it must
  not repeat an inherited hypothesis as established fact.
- **Return the whole revised document**, not just the new section, and run the
  polish final pass over all of it yourself. The polish is part of the
  deliverable.

## Explicit skip (class d)

When the user explicitly asks to skip the questions, collapse the stops, not the
stages: run intake, thesis, and outline silently from what you have, print the
thesis and the outline as two short lines above the draft, fill with `[NEEDS: ...]`
wherever the material is missing, and run the final step. Source and fidelity rules
are never skipped. In mixed mode, the addition's two-line outline goes above the
full revised document.

## Claim-provenance ledger

Keep a running ledger across the conversation: each claim or number maps to its
source, which is the original draft, the author's notes, an author answer (by
turn), or an external source the author approved. Tag each row *author-provided*
or *model-proposed, author-approved*.

**Approval is a tag, not a source.** A model-proposed row's source is evidence the
author supplied, or it stays `[NEEDS: evidence]`. A row with no source fails the
unsourced-claims check in step 6. Show the ledger in pressure-test output, and list
model-proposed rows in the final notes. The ledger records where claims came from;
it is not an assessment of the author's contribution.

## Staying neutral

The author decides; the skill must not steer by flattery.

- Do not praise the thesis, the outline, or the author's answers. Ask neutral
  questions.
- Disagree with evidence from the material when an answer contradicts it.
- When the author insists on a claim the material does not support, keep it
  marked `[NEEDS: evidence]` and say so once. A **decision** or recommendation
  stays the author's: keep it as written and note the evidence gap (owner ruling
  R1, claims not decisions).

## Boundary

Follow the suite-wide content trust boundary in `_shared/untrusted-content.md`.

- Use for: drafting from notes or a brief, shaping and sharpening an argument,
  pressure-testing a draft's argument, and polish-plus-add requests.
- Do not use for: pure rewording, de-AI-ing, or reviewing how text reads (that is
  comms-polish); answering a question from the knowledge base (comms-qa); or
  source-code work.

## Safety Rules

- **No fabrication, ever.** Never invent facts, numbers, names, dates, citations,
  quotes, or claims. A missing fact is an inline `[NEEDS: what is missing]`,
  collected in the output list. A visible gap is correct; an invented fact is the
  worst failure this skill can make.
- Do not invent KB content. If the KB has no matching entry, say so and work from
  the author's material.
- Do not strengthen the author's position beyond what the material supports.
- Keep every caveat, legal, medical, financial, or safety warning, and every real
  uncertainty the material carries.
- Respect the genre's hard form constraints over style or voice preferences.

## Self-improvement (human-gated)

Follow `_shared/self-improvement.md`; do not restate it.

- **On start:** read resolved `<state>/learned-rules.md` and apply entries with
  `status: active` whose scope is `comms-shape`, `all`, or the legacy
  `comms-draft` scope (legacy entries apply to the fill step and mixed mode).
- **On end:** if a repeatable correction surfaced, propose one candidate rule with
  scope `comms-shape` and wait for explicit approval before it is appended.
- Never auto-edit this SKILL.md or the pattern catalog.

## Output

At each stop, return only what the stop needs: the thesis options, or the outline
with its sharpen questions.

With the finished document, return the document first and everything else after
it, below a separator line (`---`). Nothing below is ever written inside the
document's body, so the author can send the document as it stands:

1. **The document**, formatted for its genre.
2. **`[NEEDS: ...]` list**: every gap, so the author can fill them. Omit if none.
3. **Unmet criteria**: any of the five step-3 dimensions the document misses.
   Omit if none.
4. **Model-proposed points**: ledger rows the author approved but did not supply,
   with their source or `[NEEDS: evidence]`. Omit if none.
5. **Inputs note**: one line on what was loaded and what was absent (voice
   profile, KB entries, preset).
