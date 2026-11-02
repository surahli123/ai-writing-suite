# Research round 2: writing-skill best practices beyond the owner's stars (2026-11-01)

**Status: RESEARCH + PROPOSAL ONLY. Nothing implemented.**

This round follows `research-landscape-2026-11-01.md` (round 1) and the skill-lift eval `eval-lift-2026-11-01/` (v0). The owner asked for sources beyond their stars and named two exemplars: [cursor/plugins pstack unslop](https://github.com/cursor/plugins/blob/main/pstack/skills/unslop/SKILL.md) and [theclaymethod/unslop](https://github.com/theclaymethod/unslop).

## Method

A 5-agent Sonnet workflow (`wf_1c5bb38a-79d`, about 1.5M subagent tokens). It produced 48 practices, which merged into 30 clusters, and each cluster was checked against the suite files with `file:line` evidence.

| Lane | Scope | Sources |
|---|---|---|
| authoring | Official skill-authoring guidance (agentskills.io spec and guides, Anthropic platform and Claude Code docs, anthropics/skills skill-creator, OpenAI Codex skill-creator) and the two named exemplars in depth | 15 |
| registries | Most-*used* writing skills by install counts (skills.sh, claudemarketplaces, claudeskills.info, awesome lists) | 15 |
| ds-comms | BLUF/Minto, decision memos, 6-pagers, experiment readouts, postmortems, communicating uncertainty, plain-language standards, and skills that encode them | 30 |
| product-hci | AI writing products (Word Copilot, Claude for Word, Docs Gemini, Grammarly, Lex, Spiral, Writer, Type) and 2024–26 HCI research on co-writing | 45 |

The orchestrator verified these directly:

- theclaymethod/unslop's published NO-SHIP result: `evals/CORE-RESULTS.md:142-171`, recall 83.87% vs 32.26% and damage rate 11.11% vs 0%;
- its lack of a LICENSE file;
- the detector false positive on DS terms: "robust regression … high leverage … loss landscape" scores 15 ("robust", "landscape", "leverage" flagged);
- telegraphic status text scoring 0.

Registry install counts are search snippets from aggregators that disagree by up to 2×, and bundle installs inflate them. They show demand, not effectiveness. All HCI paper findings are abstracts or snippets, many from student samples.

## What round 2 adds

1. **Demand sits with process and format skills, not tell catalogs.** The top writing skills by installs:
   - Anthropic's own `doc-coauthoring` (about 61–77K) and `internal-comms` (about 61–67K; 3P updates, newsletters, FAQs);
   - coreyhaines31/marketingskills `copywriting` (about 82–180K);
   - Matt Pocock's beta `writing-shape` / `writing-fragments`.

   De-slop skills rank far lower in the same listings (stop-slop about 11K, humanizer about 4K). **None of the popular ones measures its own effect.** One sample output in content-research-writer even contains invented citations.
2. **Official authoring guidance converges** (Anthropic, agentskills.io, OpenAI):
   - **The description does all the triggering.** Write it from user intent with a "Use when" clause and near-miss exclusions, and verify it with a labeled should-trigger / should-not set (about 20 queries, 3 runs).
   - **Context is a budget.** SKILL.md stays under 500 lines and about 5k tokens, references sit one level deep with a Contents block on any file over 100 lines, and the skill says exactly when to read each file.
   - **Freedom matches fragility.** Give defaults, not menus.
   - **Iterate with and without the skill** in clean contexts, and drop assertions that pass in both arms.
   - **Start from real team material.** SkillsBench (snippet) reports curated skills at +16 points and self-generated ones at −1.3. That supports the owner's real-writer stance.
3. **theclaymethod/unslop v2.3.0 is now an audit-first, no-op-default skill with honest evals.**
   - One 644-word core contract that presets and commands cannot override.
   - "Prefer a no-op to an uncertain edit", "a scanner match alone never authorizes an edit", and "copy every other sentence byte-for-byte".
   - Its frozen holdout ships as **NO-SHIP**: higher recall and repair than the raw model, but one damaging edit (a literal "harnessed energy" weakened).
   - Its three recurring failures: a correct report of someone else's claim treated as the author's error; literal technical language treated as metaphor; missed semantic risks.
   - Same lesson as our v0: **damage on clean or literal text is the metric that decides shipping.**
4. **pstack unslop is a cited catalog, not a workflow.**
   - Stable rule ids, where a removed rule leaves a gap.
   - #27: the portability test. #32: mannered prose. #33: over-compression.
   - It is `disable-model-invocation` (a manual command).
   - Its sibling `technical-writing` picks the Diataxis mode first and has a good escape hatch: *"A sentence that follows every rule and sounds like a machine wrote it has failed."*
   - In our v0 eval this style over-edited terse DS text: 31% would-send on fresh drafts.
5. **DS-comms practice:**
   - **Answer-first fits only documents that ask the reader to accept a judgment.** Timelines, runbooks, tutorials and thanks are left alone. millwright's 8-case eval found over-firing and acting unasked were the real failures, and a prohibition only worked once it was rewritten as a positive output-shape contract.
   - **Genre = slot list with obligations:**
     - decision memo: rejected options, the trade-off, a change trigger;
     - status update: the call, the ask, dated and owned items;
     - postmortem: cause, not symptom, plus owned actions;
     - readout: verdict and validity before effects.
   - **Effect statements** need an estimate, an interval, n and window, and an implication.
   - **Nulls have three distinct phrasings:** precise null, underpowered, negative.
6. **Products converged on proposals anchored to spans until the writer approves them:** tracked changes in Word Copilot and Claude for Word, private Gemini edits, accept/dismiss in Grammarly. Voice and facts live in separate slots (Lex style guides vs knowledge bases; Spiral styles vs knowledge), which our voice-profile / `_shared/knowledge` split already matches. Grammarly concedes its own AI detector agent is hit or miss and points enforcers to *process* provenance (Authorship), which supports the A4 score stance.
   - Research (snippets): AI help cuts effort and felt ownership with little change in rated quality.
   - Influence is invisible.
   - A small, specific friction reduces uptake of flawed suggestions (a written justification moved it from 65% to 41%, one preprint).

## Corrections to round 1

- theclaymethod/unslop *does* ship a quantitative voice score with impostor calibration. Round 1 said no external skill did.
- anthropics/skills *does* ship writing skills (doc-coauthoring, internal-comms). It shipped no *new* tell-editing skill since July.

Both corrections are applied in the round-1 note.

## New clusters, with suite status (verified)

| # | Practice | Verdict | Value / effort | Delta for us |
|---|---|---|---|---|
| R2-1 | **Document-level consistency pass.** Each number with its label, unit and denominator; same-label disagreements; parts that don't sum; defined-term drift; title/lead promises vs body. Report all locations and never reconcile. | gap | high / M | Most DS-specific gap. The number half fits the stdlib mutant harness; the term and promise halves stay judge-only. Mutant: change one repeated number and require a flag. |
| R2-2 | **DS-literal false-positive fixtures + damage metric** ("robust SE", "leverage" as hat value, "loss landscape", kernel, ensemble). A protected class for quoted claims. | partial (FP gate has "term of art"; no DS fixtures; detector flags them) | high / M | Collocation-gated detector rows: a "protects" row plus a "recall" row per word. Track a damage rate for protected spans. |
| R2-3 | **DS fidelity classes** beyond A1's scope words: % vs pp, relative vs absolute, "roughly 60%" → "60%", date precision, "not significant" → "no effect". | partial (A1 / T1-5 unbuilt) | high / S | One mutant per class, as gold-FAIL items outside the calibration denominator. |
| R2-4 | **Experiment-readout preset + effect-statement slots + three null phrasings** | gap | medium / S | Ship as generic KB entries ("fuel") that a company playbook overrides. Never compute or guess a CI; use `[NEEDS: interval]` instead. |
| R2-5 | **More DS genre slot lists:** decision memo, exec/status update (3P), postmortem, analysis write-up | partial (B8 named some, no content) | medium / S | KB entries, each with one missing-slot fixture that must produce `[NEEDS: …]`. Drop numeric caps and emoji/quota rules (owner-rejected). |
| R2-6 | **Structure gate:** answer-first only for documents that ask for a judgment, plus decline fixtures (timeline, thank-you, tutorial, notes). If the user only shared a draft for feedback, return feedback, not a rewrite. | partial | medium / M | Fold into A2/B8. Fixtures across model tiers. |
| R2-7 | **Intent-first descriptions + labeled trigger set** (about 20 queries per skill, near-misses) | gap | medium / M | Our descriptions are led by modes and mechanics (325–768 chars). A checked-in trigger fixture plus a lint on the first 300 characters; the live run stays opt-in. Real phrasings should come from the DS team. |
| R2-8 | **Static skill lint:** portable frontmatter allowlist, body ≤500 lines, Contents blocks on long references, no ruling IDs and dates in runtime text, plus B9's read-instruction lint | partial | medium / S | Extend `test_skill_manifests.py`, one mutant per rule. Runtime text currently carries "C3 ruling, 2026-07-15" and similar (`comms-polish/SKILL.md:106,225`). Move those to the CHANGELOG. |
| R2-9 | **Claim-strength ladder** (direct / supported / inferred / speculative / unknown), checked both ways, plus a "closest supportable claim + what evidence would unlock it" rule | partial | medium / M | A generic KB entry plus one Safety Rule line. **It must agree with the PR #67 fix** (a user-supplied source authorizes alignment). |
| R2-10 | **Apply / ask / report lanes:** local meaning-preserving fixes are applied; claim-strength decisions are asked; global issues are reported with locations | partial | medium / M | A `lane:` field in the audit report (S). Must not turn into "never apply claim changes"; v0 shows readers want the source-aligned cut. |
| R2-11 | **Over-compression counterweight** (dropped articles, arrows, verbless fragments introduced by a rewrite) | gap | medium / S | Judge-only entry with a Slack/terse-genre validity condition. Also a counterweight to R1's push toward fragments (A6). |
| R2-12 | **Planted-defect prioritization fixture:** the audit report's "Biggest problem" must name the planted major defect, not minor tells | gap | medium / S | Deterministic string-match fixture family; fits `run_all.sh`. |
| R2-13 | **Persona/stance drift** as a judge dimension (a cautious analyst stays cautious after "make it professional") | partial | medium / M | `no_persona_shift` rubric dimension plus a gold-FAIL item. |
| R2-14 | **Contract-first reorder of comms-polish/comms-draft SKILL.md** (decision rule, protected classes, output contract and two contrastive pairs in the first ~600 words) | gap | medium / M | v0 shows no failure from the current order, so test it with a leave-one-out run before reordering. Conflicts with PR #67's edits. |
| R2-15 | **First-party `claude plugin eval`** as the live arm (with/without plugin, regex / tool_used / llm graders) | partial | medium / M | Could replace the bespoke `lift_eval.js`. Verify the command exists (`claude plugin eval --help`) before planning. Claude-only, never required. |
| R2-16 | **Holdout discipline:** composition floor, burn ledger, sealed holdback, exact sign-flip test for ≤12 items | partial | medium / M | Small additions to B10. Little to protect until real DS drafts exist (P3). |

Low value, recorded only:

- durable anchors (relative time words → dates in archived documents);
- assertion headings, for argument documents only;
- define-before-use grounding ledger;
- relationship-message ceiling plus a receipt line;
- a team-exemplars KB slot;
- a model-tier matrix;
- opt-in friction (justify-to-accept);
- a post-draft trigger for agent-written prose;
- extra Vercel tells (fold into mannered prose);
- a scaffold-label and example-leakage guard.

## Merged priority list (round 1 + v0 eval + round 2)

The v0 eval changes the ranking. On Sonnet, the suite's only measured difference from no skill is **restraint**: it edits less. A one-liner ties it. *(Correction after adversarial review: the "fidelity lift, p=0.04" did not replicate, and the PR #67 result was set by the judge rubric. See `eval-lift-2026-11-01/review/`.)* The external evidence (unslop's NO-SHIP, millwright, quiron) says shipping should be decided by **damage on clean or literal text**. So the build order puts the measured value first, then the things a one-liner *cannot* do (DS genre knowledge, document-level checks).

| Order | Item | Why now |
|---|---|---|
| 0 | **Fix PR #67 before merging.** A source the user supplies in the same request counts as authorization to align claims (cut or qualify, then say so). Keep preserve-and-flag for standalone drafts. Then re-run its 3 factbridge items in the v0 harness. | Measured regression: 2/6 vs 6/6 would-send. The PR also contradicts its own gold answers. |
| 1 | **A2 + R2-6: edit restraint.** Light-edit switch, named-failure rule, no-change fixtures, decline fixtures; revisit the overstepping validity condition for evidence-answered setups. | v0's suite losses were over-edits (overstep-05, memo-01). unslop and millwright say the same. |
| 2 | **A1 + R2-3: fidelity classes.** Scope words, % vs pp, approximators, hope→fact, "not significant"→"no effect". | The only measured lift; gold-FAIL lane T1-5 is still unbuilt. |
| 3 | **R2-2: DS-literal false-positive fixtures** plus a collocation-gated detector | Reproduced: a DS methods sentence scores 15. Cheap and stdlib. |
| 4 | **A3: add-side hedge guard** plus **A4: score epistemics** (owner ruling) | Small. Grammarly's own concession strengthens A4. |
| 5 | **R2-1: document consistency pass** (number half in stdlib) | The DS gap no external skill fills well; a one-liner can't do it. |
| 6 | **R2-4 + R2-5: DS genre slot lists as KB fuel** (readout first) | Where the popular skills' demand is (format and process); the playbook can override them. |
| 7 | **A5 + A6 + R2-11: catalog updates** (mannered prose, portability, pending no-ai-slop items, soften R1, over-compression) | Normal catalog lane. |
| 8 | **R2-7 + R2-8 + B9: descriptions, trigger set, static lint** | Cheap hygiene. |
| 9 | **Re-run the lift eval** on fixes 0–3, adding a Haiku arm and K≥3 fresh contexts, then a comms-draft-from-KB arm and long DS documents. Consider `claude plugin eval` (R2-15). | Turns these proposals into measured results. |
| Later | B7/E2 versioning, B8/E3 register, C12 judge protocol, C13 recipient proxy, C14 learned-rule hardening, R2-9/R2-10/R2-13/R2-14/R2-16 | Depend on the items above or on real DS drafts (P3). |

## Rejected re-proposals seen this round (not recommended)

- **Em-dash bans:** pstack unslop #13, technical-writing, Vercel.
- **Numeric levers:**
  - 20/25-word caps (STE, plain-language, pstack);
  - Amazon's 70%-under-20-words;
  - unslop's 32/40 strict gate and 8–25 word rhythm rubric;
  - 3P one-to-three sentences;
  - FAQ quotas.
- **Manufactured personality:** unslop rubric's "has voice, opinion, lived experience".
- **Writing for AI readers:** K-Dense claim-ID and hash registries.
- **Public corpus as evidence.**

## License notes

- **Usable (MIT/Apache), with NOTICE credit if text is absorbed:**
  - pstack (MIT, Lauren Tan);
  - marketingskills, millwright, Pocock skills, Vercel writing-guidelines, K-Dense, copyeditor-skill (all MIT);
  - anthropics/skills internal-comms and discernment-nudge, tyroneross, pm-skills, MADR (Apache/MIT/CC0);
  - GSA plainlanguage (CC0).
- **Ideas only:**
  - **theclaymethod/unslop has no LICENSE file** (MIT is claimed only in its README and frontmatter), so absorb no text;
  - anthropics/skills doc-coauthoring has no per-skill license;
  - humanities-writing-companion is CC BY-NC;
  - TavoloPerUno and SantaJordan declare no license.
