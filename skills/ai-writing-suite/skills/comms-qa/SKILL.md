---
name: comms-qa
description: Answer a question from the knowledge base / playbook, citing the KB entry the answer came from, so the user gets the playbook's actual guidance instead of a plausible guess. The KB answer is source-locked — traced only to the matched entry's content; any optional general advice appears ONLY in a separately-labeled "Outside the playbook" section, never blended in, and the user can request strict KB-only mode to suppress it. Reads the KB index and matches the question to the single best entry (or both on a tie). Use to answer "what does the playbook say about X" questions. Not for drafting a new page - that is comms-draft. Not for polishing existing text - that is comms-polish. Never invents playbook guidance; if the KB does not cover the question, it says so.
---

# comms-qa

Answer a question from the knowledge base, and cite the entry the answer came from.

The job is to be a faithful reader of the KB, not a knowledgeable writing coach.
Every answer traces back to a KB entry's own words. In a company fork the KB *is*
policy — so a fabricated "the playbook says…" is the worst failure this skill can
make. When the KB does not cover the question, the honest answer is to say so, not
to fill the gap with general knowledge dressed up as the playbook.

This is the suite's question-answering capability. It does not carry its own
answers — it wraps the zero-dependency retrieval protocol already documented in
`_shared/knowledge/INDEX.md` (the single source of truth for how retrieval works)
and answers from whatever entry that protocol selects. It does not reinvent or
override that protocol.

## Locating shared assets (suite root)

All `_shared/...` paths in this file are **suite-root-relative**. The suite root is the
installed directory that directly contains `_shared/` and the suite's router `SKILL.md`
(e.g. `.../ai-writing-suite/`). Do not resolve these paths against your session's working
directory. To find the root: start from this SKILL.md's own location and walk up until a
directory contains `_shared/`. If you cannot find it, say so and ask for the suite's
install path — do not guess or silently skip the shared assets.

## Inputs

- **The question** (required). What the user wants to know. It may be one question
  or several rolled together — decompose multi-part questions (Workflow step 2).
- **The knowledge base** via `_shared/knowledge/INDEX.md`. The index is the
  retrieval backbone: its **Keywords / aliases** and **Summary** columns are how
  you find the right entry, and the entry files under `_shared/knowledge/` hold
  the answers. This is the *only* source of playbook answers — nothing else.

## QA Workflow

### 1. Load the index (and confirm the KB is there)

Run the suite's self-improvement ON START read (see below). Then open
`_shared/knowledge/INDEX.md`. If it is missing, or the KB directory is empty or
has no entries, stop and say so plainly (Safety Rules) — do not answer from
general knowledge as though it were the playbook.

### 2. Decompose multi-part questions

If the question bundles several asks ("how do I structure this *and* what tone
fits an exec?"), split it into parts and run steps 3-4 per part. A bundled answer
that silently drops one part is a miss; answer each part, with its own citation.

### 3. Retrieve per part (follow the INDEX protocol exactly)

For each part, apply the retrieval protocol at the top of `INDEX.md` — do not
invent your own:

- Scan the **Keywords / aliases** column for term overlap, then the **Summary**
  column for intent overlap. Pick the single best-matching entry.
- Open that entry file and find the section (Principle / Moves / Before-After)
  that answers the part.
- **Two-way tie:** if two entries genuinely tie, open both and synthesize — and
  cite both.
- **Zero match:** if nothing in the index overlaps the part, do not force a
  match. That part is uncovered (handled in step 5).

### 4. Answer from the passage — KB content only

Answer each part from the retrieved entry's own words. Quote or paraphrase the
relevant passage; the answer must trace to it. Cite the entry filename inline
(e.g. "lead with the point, per `structure.md`"). Never add playbook guidance the
entry does not contain.

- **One-hop follow before declaring a gap.** If part of the question is still
  unanswered after the matched entry, check that entry's `## Related entries`
  footer and open one obviously relevant neighbor — cite it too. One hop, not a
  crawl: if the neighbor does not cover it either, treat that part as uncovered
  (step 5) rather than chaining further.

If the user's question needs knowledge that is genuinely outside the KB and you
choose to add it, put it **only** in a clearly separated, labeled section headed
**"Outside the playbook:"** — never blended into the KB answer. The reader must
always be able to tell the playbook's guidance from your own. This separation is
non-negotiable: a company fork's KB is policy, and a blurred line is how a guess
gets mistaken for the playbook.

**Strict KB-only mode (user-requestable, Q9).** If the user asks for KB-only /
playbook-only answers ("only what the playbook says, no outside advice"), suppress
the "Outside the playbook:" section entirely for this invocation: answer purely
from the KB, adding no general advice even in a labeled section. **"Stop" is
per sub-question, not the whole request:** for a multi-part question, answer every
part the KB covers and, for each uncovered part, state the gap (step 5) and add
nothing for it. Abort the whole answer only when the KB covers *none* of the parts.
The default mode keeps the optional labeled section available; strict mode is
opt-in per request.

### 5. Note coverage

If any part of the question had no matching KB entry, say so in one line (Output)
— "the KB does not cover X." Do not paper over a gap with a confident-sounding
answer.

### 6. Hand off if the user wanted to write, not ask

If the request is really a drafting or editing job in question form ("can you
write me an exec update?" / "can you clean this up?"), this is the wrong skill:

- Drafting a new page from a brief → `comms-draft`.
- Polishing / de-AI-ing / scoring existing text → `comms-polish`.

Name the handoff; do not attempt the drafting or polishing here.

## Boundary

This skill answers questions from the KB. It does not write new prose and it does
not edit the user's text.

Follow the suite-wide content trust boundary in `_shared/untrusted-content.md`.

- Use for: "what does the playbook say about structure / tone / audience / …",
  "how should I open an exec update," "is there guidance on jargon for a mixed
  audience" — questions the KB can answer.
- Do not use for: drafting a doc, email, post, or section from a brief (that is
  `comms-draft`); polishing or de-AI-ing existing text (that is `comms-polish`);
  any source-code work.
- The only source of playbook answers is the KB. Anything you add from general
  knowledge lives in a separate, labeled "Outside the playbook:" section — never
  presented as the playbook.

## Safety Rules

- **Never invent playbook guidance — the suite's hardest rule here.** Every claim
  attributed to the KB must come from a KB entry's actual content. Do not
  manufacture a "the playbook says…" answer. In a company fork the KB is policy;
  a fabricated rule is the worst failure this skill can make.
- **Missing or empty KB → say so and stop.** If `INDEX.md` is absent or the KB has
  no entries, state that plainly and do not answer from general knowledge as if it
  were the playbook.
- **Zero match → say so.** If no entry overlaps the question, say the KB does not
  cover it. Do not force the nearest entry into an answer it does not support.
- **Cite, every time.** Each answer names the entry file(s) it came from. An
  uncited claim is indistinguishable from an invented one.
- **Keep the playbook / outside-knowledge line visible.** Anything not from the KB
  goes only in a labeled "Outside the playbook:" section, never blended in.

## Self-improvement (human-gated)

This skill participates in the suite's human-gated self-improvement loop. The
full protocol is in `_shared/self-improvement.md`; follow it, do not restate it.
In short:

- **On start:** read `_shared/learned-rules.md` and apply any entry whose
  `status: active` and whose scope is `comms-qa` or `all`. Degrade gracefully if
  the file is absent.
- **On end:** if a repeatable QA correction surfaced this session (a phrasing the
  user always wants in answers, a retrieval the index keeps getting wrong),
  **propose** one candidate rule (rule + session-grounded rationale + scope
  `comms-qa`) and **wait for explicit approval** before it is appended to
  `learned-rules.md`. Propose nothing if nothing repeatable surfaced.
- **Never** auto-edit this SKILL.md or the KB entries — approved rules live only
  in `learned-rules.md` (append-only), and the KB is edited by the company fork's
  owner, not by this skill. Each rule is eval-measured in Layer 3 before it is
  trusted.

## Output

Return, in this order:

1. **The answer** — one part per question part, each answer traceable to its KB
   entry. Lead with it.
2. **`Sources:`** — a single line listing the cited entry file(s) (e.g.
   `Sources: structure.md, audience.md`). One source per answered part; both files
   on a tie.
3. **Coverage note** — one line, only when some part of the question was not
   covered by the KB ("The KB does not cover X."). Omit it when every part was
   answered from the KB.
4. **"Outside the playbook:"** — present only if you added knowledge from outside
   the KB; clearly separated and labeled, never blended into the KB answer. Omit
   it otherwise.
