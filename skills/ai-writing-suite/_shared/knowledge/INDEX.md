# Knowledge Base — Navigation Index

> **This file is the retrieval backbone.** There is no embedding store, no vector
> DB, no MCP dependency (design decision **D5**). "Retrieval" = an agent reads
> this index, matches the user's question against the **Summary** and **Keywords
> / aliases** columns, then opens the one entry that fits and quotes the relevant
> passage. This works identically on Claude, Codex, Cursor, and RovoDev because
> it is pure markdown + file reads — nothing host-specific.
>
> Keep this index in sync with the entries. Adding a KB entry = add one file +
> one row here (the "ingestion" step — see `SMOKE-TEST.md`).

## How an agent uses this index (retrieval protocol)

1. Read the user's question.
2. Scan the **Keywords / aliases** column for term overlap, then the **Summary**
   column for intent overlap. Pick the single best-matching entry.
3. Open that entry file. Find the section (Principle / Moves / Before-After) that
   answers the question.
4. Answer from that passage; cite the entry filename. If two entries tie, open
   both and synthesize. If nothing matches, say so — do not invent guidance.

## Entries

| Entry file | Summary (one line) | Keywords / aliases |
| --- | --- | --- |
| `clarity.md` | Say one idea per sentence in plain, concrete words; cut filler. | clarity, clear, concise, plain language, wordy, verbose, filler, jargon, simplify, hard to read, confusing, cut words, concrete, vague |
| `structure.md` | Lead with the point (BLUF), one idea per paragraph, shape to channel. | structure, organization, order, BLUF, bottom line up front, flow, outline, headings, rambling, where to start, lead with, top-down, paragraph |
| `audience.md` | Write for one specific reader and their job, not "everyone." | audience, reader, who is this for, target reader, stakeholder, exec vs engineer, jargon level, too technical, condescending, tailor |
| `tone.md` | Sound like a competent colleague: direct, no sycophancy, no hype, varied rhythm. | tone, voice, formal, casual, sounds robotic, sounds like AI, stiff, corporate, hype, salesy, sycophantic, cheesy, register, how it sounds |
| `revision.md` | Treat the first draft as raw; fix it in editing passes; final tell-sweep. | revision, editing, revise, edit, second draft, polish, proofread, rewrite, read aloud, cut length, final pass, self-edit, improve a draft |
| `experiment-readout.md` | Readouts open with the verdict and validity; every effect carries baseline, unit, interval, n, window; three distinct nulls. | experiment readout, A/B test, ab test, readout, results write-up, effect size, confidence interval, statistical significance, not significant, null result, underpowered, lift, holdout analysis, launch review |
| `decision-memo.md` | Decision memos owe the call, rejected options, trade-off and change trigger; status updates owe the call, the ask, owned and dated items. | decision memo, recommendation, proposal, go/no-go, options, trade-off, reversible, ADR, status update, weekly update, 3P, progress report, blocked, ask |
| `incident-note.md` | Incident notes separate facts, hypotheses and unknowns; postmortems need a single-timezone timeline, cause vs symptom, owned actions. | incident, incident update, postmortem, post-mortem, outage, root cause, hypothesis, timeline, on-call, data quality incident, blameless, action items |

## Categories (for browsing, not required for retrieval)

- **Sentence-level:** `clarity.md`, `tone.md`
- **Document-level:** `structure.md`, `audience.md`
- **Process:** `revision.md`
- **Data-science genres:** `experiment-readout.md`, `decision-memo.md`, `incident-note.md`

## Provenance

All entries are generic professional-writing best practices distilled from four
MIT-licensed reference repos (`anti-vibe-writing`, `avoid-ai-writing`,
`AI-Vibe-Writing-Skills`, `nature-skills`). Per-entry `Sources` sections carry
the lineage; full attribution lives in the skill `NOTICE.md`. This is the
**open-source** KB. A company fork drops its proprietary playbook into this same
slot and updates this index — see `README.md` ("Swapping in a company playbook").
