# Research — petergyang/no-ai-slop vs the suite catalog (2026-07-22)

Sources: https://github.com/petergyang/no-ai-slop (MIT, Copyright 2026 Peter Yang; 3 files:
SKILL.md 93 lines, eval.md 42, README 64) and the companion essay
"Use My /No-AI-Slop Skill to Remove 20+ Patterns of AI Slop" (creatoreconomy.so, 2026-07-22).
Compared against the suite's 72-entry `_shared/patterns/` catalog at main @ `3ba8fad`.

## Shape of the skill

One flat SKILL.md: two jobs (edit = minimum effective edit + "What changed" section;
detect = name pattern, quote line, give the fix — explicitly no rewrite, no score, no
AI-authorship claim), 15 editing principles, a banned-word list with keep-when-voice
carve-outs, ~17 named patterns, and a same-agent self-check against `eval.md` (39
pass/fail questions). No references/ tree, no code, no fixtures — the eval is a
checklist the editing agent runs on itself.

## Delta against the 72-entry catalog

Roughly 16 of its ~20 patterns are already covered, several with stronger machinery
on our side (tiered L1 vocabulary + deterministic swap table; R1/R2 stylometric
enforcement; S7's exact -ing rule; T2's exact binary-contrast before/after). The
genuine deltas:

| # | no-ai-slop item | Catalog state | Delta |
|---|---|---|---|
| 1 | **Faux-insight setup** — "what nobody tells you," "the part everyone misses," "what most people get wrong" (lone-expert flattery framing) | Zero hits in catalog; O1/O2 cover presumed cognition/strawman, a different mechanism | NEW candidate entry (judge enforcement; regex-able trigger list) |
| 2 | **Colon-reveal statement form** — "The best part: it learns." (noun phrase + colon + dramatic lowercase reveal) | C7 covers the QUESTION-form hooks ("The best part?", "But here's the kicker:") | Extension of C7 to the statement form + the sentence-case-after-colon micro-rule |
| 3 | **Fake-profound kicker ending + delete-don't-rewrite remediation** — cut the final aphorism/mic-drop; never rewrite it into a better metaphor; end on the clearest concrete sentence already in the draft | H3/H4 cover generic and future-narrative closers; the aphorism-ending form and, more importantly, the remediation discipline are absent | The remediation rule is the gem: it guards the FIXER against fix-erosion (replacing slop with prettier slop). Candidate addition to the H-family fix prose and/or final-pass-checklist |

## Process-level findings (not pattern entries)

1. **Detect-mode epistemics.** no-ai-slop refuses to score or claim AI authorship:
   "AI detectors guess. Named patterns are evidence the user can check." Our
   comms-polish exposes a 0-100 AI-tell score in detect mode. Suite doctrine already
   says detector = regression signal, never a quality KPI — but the user-facing score
   sits in tension with that doctrine in exactly the way Yang's rule names. Worth an
   owner ruling: keep the score (useful relative signal), reframe its presentation
   (named-pattern evidence first, score as footnote), or drop it from detect output.
2. **Internal voice-signal note.** Workflow step 2: before editing, note 3-5 voice
   signals to preserve (vocabulary, cadence, bluntness, humor, uncertainty,
   digressions) — kept internal. Convergent with our Verbatim Anchors (Wave-2), but
   the cheap internal-note step is adoptable in comms-polish's rewrite workflow
   without schema changes.
3. **Same-agent self-check.** eval.md is explicitly run by the same agent ("without
   requiring separate editor and evaluator agents") — the opposite of our
   separate-lane review discipline. Simpler, weaker; nothing to adopt, but a useful
   contrast when documenting why the suite splits producer and grader.
4. **25/50/25 rule** (essay, not skill): human-only first 25% (draft from taste),
   AI-assisted middle 50%, human-only last 25% (line-by-line pass). Candidate for the
   suite README's usage guidance; matches the suite's human-gated philosophy.

## Recommendation (owner decision, not implemented)

Small backlog lane (~S, three catalog candidates + one checklist line), through the
normal catalog process: (a) new entry for faux-insight setups; (b) C7 extension for
statement-form colon reveals; (c) delete-don't-rewrite remediation line in the
H-family fix prose / final-pass checklist. Attribution: MIT, credit petergyang/no-ai-slop
in NOTICE.md per repo convention. Separately, the detect-score epistemics question
(#1 above) deserves its own explicit ruling before any change.
