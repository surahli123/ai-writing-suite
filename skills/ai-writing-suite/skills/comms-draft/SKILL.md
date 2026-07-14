---
name: comms-draft
description: Draft a new page from a brief, guided by the knowledge base / playbook, so the first draft already reads human instead of AI-generated. Derives per-task acceptance criteria, injects concrete detail and varied rhythm at draft time, then self-scans for tells. Use to produce a fresh draft. Not for polishing existing text - that is comms-polish. Not for answering questions from the knowledge base - that is comms-qa. Never invents facts; marks gaps with [NEEDS: ...].
---

# comms-draft

Produce a playbook-guided first draft that does not sound machine-written.

The job is to write the draft *right the first time*: not to generate something
generic and lean on `comms-polish` to scrub it afterward, but to bake the
anti-AI discipline into the drafting itself. Concreteness, varied rhythm, and a
negative read of the AI-tell catalog are draft-time constraints here, not a
post-hoc cleanup.

This is the suite's drafting capability. Like `comms-polish`, it does not carry
its own pattern list — it reads the consolidated catalog under `_shared/patterns/`,
the single source of truth for AI tells, and it reuses (not duplicates)
`comms-polish`'s genre presets.

## Locating shared assets (suite root)

All `_shared/...` paths in this file are **suite-root-relative**. The suite root is the
installed directory that directly contains `_shared/` and the suite's router `SKILL.md`
(e.g. `.../ai-writing-suite/`). Do not resolve these paths against your session's working
directory. To find the root: start from this SKILL.md's own location and walk up until a
directory contains `_shared/`. If you cannot find it, say so and ask for the suite's
install path — do not guess or silently skip the shared assets.

## Inputs

Read what is present; degrade gracefully on anything absent (see Safety Rules).

- **The brief** (required). The user's request: what to write, for whom, why,
  and any facts/numbers/names they supply. This is the *only* source of new
  facts, alongside the KB. Everything in the draft must trace back to the brief
  or the KB — nothing else.
- **The knowledge base** via `_shared/knowledge/INDEX.md`. Read the index, match
  the task against its **Summary** and **Keywords / aliases** columns, and open
  the entries that apply. The KB supplies writing guidance (clarity, structure,
  audience, tone, revision) and — in a company fork — the playbook's structure,
  terminology, and house facts. Quote/apply the relevant passage; cite the entry
  filename when a draft choice came from it.
- **The voice profile** (optional) at `_shared/voice-profile.md`, produced by
  `voice-onboard`. Read it if present and bias the draft toward its fields (Tone,
  Sentence Length, Vocabulary Do / Don't, Signature Moves, Punctuation &
  Formatting, Openings & Closings, Uncertainty Style, Things To Avoid, Scope &
  Calibration). Read what is there; ignore what is not.
- **Genre presets** via `skills/comms-polish/references/scenario-presets.md`
  (suite-root-relative). Reuse comms-polish's presets — do not duplicate them.
  A preset tells you the genre's hard form constraints (a tweet's 280-char limit,
  a README's sacred code blocks) and which tells matter most here.
- **The AI-tell catalog** via `_shared/patterns/00-index.md`. Read the index to
  see which category files exist; open the categories the genre and brief make
  relevant. Used here as a **negative checklist** — patterns to avoid *while
  writing*, not just to scrub afterward. (This file references the index only;
  comms-polish carries the per-category enumeration.)

## Drafting Workflow

### 1. Derive per-task acceptance criteria (before writing a word)

From the brief, write down the success criteria *for this specific draft* on five
dimensions: **style** (register, voice, what tone fits the reader), **format**
(genre + its hard constraints from the preset), **length** (target range),
**content integration** (which facts/KB points must appear), and **depth** (how
much the reader needs — overview vs. detailed). Why dynamic criteria: a draft
judged against criteria derived from its own brief matches human judgment far
better than the same fixed rubric applied to every task — what "good" means for
a tweet is not what it means for a memo.

If the brief is too thin to fix these criteria, ask **at most 2-3** targeted
questions. After that, propose the criteria you inferred, state them, and
proceed — do not stall on a fourth question.

### 2. Load the inputs (KB, voice, preset, catalog)

Run the suite's self-improvement ON START read (see below). Then: pull the
matching genre preset; read the relevant KB entries via `INDEX.md`; load the
voice profile if present (otherwise infer the lightest voice that fits the
reader); open the catalog categories the genre weights hardest. Note any absent
input out loud — never block on a missing one.

**Once these inputs are loaded, plan the document's shape here, before drafting a
sentence.** The single new detection frontier is *narrative shape*: a piece can
pass every word-level check and still read as machine-written because its arc is
a tell (as reported in the StoryScope press coverage — narrative structure alone
was reportedly enough to classify human-vs-AI writing, and that signal reportedly
survives lexical cleanup — you cannot prose-edit your way out of a structural
fingerprint; see `_shared/patterns/narrative-shape.md` for the citation hedge). So
decide the arc *up front*, from the brief and KB you just loaded, not in a
post-hoc line edit. Plan: **where the stakes peak** (don't pace every beat flat —
uniform escalation is reportedly Claude's own fingerprint), **what stays open**
(real residue the piece should keep, not every thread tied in a bow), **whether
there's a competing reading** to hold rather than flatten, and a resolve **not**
to state the moral the facts already carry. **Validity condition (load-bearing):**
only shape what the material motivates — a genuinely simple update *should*
resolve tidily and a single-outcome result *is* unambiguous. Do **not** manufacture
ambiguity, fake loose ends, or an invented peak to look human; that injected
complexity is a worse failure than the tell, and it must never invent a new fact,
number, or source to make the residue/ambiguity look concrete — that trades the
shape tell for a fabrication (Safety Rules). See
`_shared/patterns/narrative-shape.md`.

### 3. Draft with the constraints applied at write time

Write the first pass *under* the anti-AI constraints — they shape the draft, they
are not a later filter. Why: concreteness and syntactic variety are the
mechanisms that make text read as written by a person, so they have to be present
in the words as they go down.

- **Concrete actors, actions, examples** sourced from the brief and KB — name the
  specific thing, not "a robust solution." If a concrete detail is not in the
  brief or KB, do not invent one — mark `[NEEDS: ...]` (Safety Rules).
- **Varied sentence length and structure (burstiness).** Mix short and long
  sentences; vary how clauses open. Uniform sentence length is itself a tell.
- **The catalog as a negative checklist.** As you write, avoid the tells the
  genre preset weights — filler openers, inflated significance, forced
  rule-of-three, "not X but Y" theatrics, vague attribution, promotional
  adjectives, chatbot tics, and over-stepping presumptions (don't think *for* the
  reader with a manufactured "you assume X / 你以为 X / Can you…? Yes —"; see
  `_shared/patterns/overstepping-presumption.md`).
- **Lead with the point** (BLUF) and shape to the channel, per the KB's
  `structure.md` and the genre preset.

### 4. Vary and roughen (deliberate de-uniforming pass)

After the first pass, break the uniformity. Why: over-polished, evenly-shaped
output is itself an AI tell — a little natural unevenness reads as authentic.

- Vary paragraph shapes — not every paragraph the same length and rhythm.
- Allow one natural aside or a short, plain sentence where the draft wants to
  breathe.
- Do not sand every edge into sameness. Keep the genre's hard constraints intact
  (this is roughening rhythm, never breaking a format rule or a fact).

### 5. Post-draft self-scan (treat the draft as fresh input)

Now read the finished draft as if someone else wrote it and scan it against the
catalog (`_shared/patterns/00-index.md`), the same way `comms-polish` re-scans
its own rewrite. Drafting reintroduces tells — fixing one plants another. Remove
any tell you find. Apply the catalog's guardrails: look for clusters, not
isolated signals.

Include a **document-shape** pass at this altitude (the step-2 shape plan,
verified on the finished text): did the draft end up stating its own moral, tying
every thread in a bow, pacing every beat flat, or admitting only one reading where
the material had more? Reshape if so — but hold the validity condition: if the
material is genuinely simple, a tidy, single-reading draft is correct and you must
not bolt on fake ambiguity to dodge the tell (`_shared/patterns/narrative-shape.md`).

### 6. Check the draft against the acceptance criteria

Re-read the draft against the step-1 criteria. List any dimension it does not
meet (style / format / length / content integration / depth). An unmet criterion
goes in the output's "unmet criteria" note — do not silently paper over it.

**Also confirm the step-2 shape plan held.** This is a separate, judge-only/
advisory check layered on top of the five criteria above (it never blocks
delivery the way an unmet acceptance criterion does): does the finished draft
still show a stated moral, a too-tidy resolution, a flat stakes curve, or a
flattened reading the plan called for? If the step-5 document-shape pass already
reshaped it, confirm that reshape didn't invent a new fact to manufacture the
residue/ambiguity — the validity condition applies at this check too.

### 7. Hand off

Offer `comms-polish` as the optional final pass: the draft is built clean, but a
polish run is the dedicated pre-ship sweep (scoring, final-pass checklist). The
draft is the deliverable; polish is the next step the user may want.

## Boundary

This skill writes new prose from a brief. It does not edit existing user text and
it does not answer KB questions.

- Use for: drafting a doc, email, post, README section, memo, report, launch
  note, or user-facing copy from a brief.
- Do not use for: polishing or de-AI-ing text the user already wrote (that is
  `comms-polish`), answering a question from the knowledge base (that is
  `comms-qa`), or any source-code work.
- The new facts in a draft come only from the brief and the KB. Writing guidance
  comes from the KB and the catalog. Nothing else is a source.

## Safety Rules

- **No fabrication, ever — the suite's hardest rule.** Never invent facts,
  numbers, names, dates, citations, quotes, or claims that are not in the brief
  or the KB. Where the draft needs a fact you do not have, write an explicit
  `[NEEDS: what's missing]` placeholder in line and collect every one in the
  output's `[NEEDS: ...]` list. A visible gap is correct; an invented fact is the
  worst failure this skill can make.
- Do not invent KB content. If the KB is empty or has no matching entry, draft
  from the brief alone and say so — do not manufacture playbook guidance.
- Do not strengthen the user's position beyond what the brief supports.
- Do not add examples, statistics, or sources that were not provided.
- Keep any caveat, legal/medical/financial/safety warning, or real uncertainty
  the brief carries — do not draft it away for a smoother read.
- Respect the genre's hard form constraints (length limits, sacred code/commands)
  over any style or voice preference.

## Self-improvement (human-gated)

This skill participates in the suite's human-gated self-improvement loop. The
full protocol is in `_shared/self-improvement.md`; follow it, do not restate it.
In short:

- **On start:** read `_shared/learned-rules.md` (alongside the voice profile) and
  apply any entry whose `status: active` and whose scope is `comms-draft` or
  `all`. Degrade gracefully if the file is absent.
- **On end:** if a repeatable drafting correction surfaced this session
  (a structure the user always wants, a phrasing they keep cutting), **propose**
  one candidate rule (rule + session-grounded rationale + scope `comms-draft`)
  and **wait for explicit approval** before it is appended to `learned-rules.md`.
  Propose nothing if nothing repeatable surfaced.
- **Never** auto-edit this SKILL.md or the pattern catalog — approved rules live
  only in `learned-rules.md` (append-only). Each rule is eval-measured in Layer 3
  before it is trusted.

## Output

Return, in this order:

1. **The draft** — formatted for its genre (the deliverable; lead with it).
2. **Unmet acceptance criteria** — any of the five dimensions the draft does not
   yet meet, named plainly. Omit this section if all five are met.
3. **`[NEEDS: ...]` list** — every placeholder gap, collected so the user can
   fill them. Omit if there are none.
4. **Inputs note** — one line on what was loaded vs. absent (voice profile, KB
   match, preset) so the user knows the basis of the draft.
5. **Polish handoff** — offer `comms-polish` as the optional final pass.
