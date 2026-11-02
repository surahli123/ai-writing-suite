# Fable 5.1 round-2 review: plan v2 (2026-11-02)

VERIFIED_AGAINST: claude/laughing-rubin-mkkadx-s9-lists-review @ 621d9e4 (implementation base 0424a7f)
MODEL: Fable 5.1 subagent, read-only (repo unchanged; probes inline). Report reproduced verbatim.
Disposition: docs/plan-step9-and-comms-shape-2026-11-02.md, "Review log (round 2)".

---

# Round-2 review of plan v2 (docs/plan-step9-and-comms-shape-2026-11-02.md @ 621d9e4)

Read-only. `bash skills/ai-writing-suite/evals/run_all.sh` passes on the branch (VERIFIED). Probes ran inline under `python3 -I -B`; nothing written to the repo.

## 1. Verdicts

- **Step 9 (comms-polish A–G): GO WITH CHANGES.** The mechanics Codex/Fable broke in round 1 are now specified and the parser claims check out against `check_report.py`. Remaining: one internal contradiction in T7's definition vs its kept examples (#2), a number-word guard that rejects legitimate Fixes (#4), a status-class alignment rule that fires on reordering (#5), and several checker-spec edge cases (#7). All author-fixable; no owner decision needed except the optional human anchor.
- **Step 10 (comms-shape): GO WITH CHANGES, three of them before any code.** The state machine, mixed mode, ledger and pilot design answer round 1. But the harness port is internally inconsistent (#1), the pilot's proceed bar is trivially satisfiable (#3), and the state machine has three undefined transitions (#6). One owner confirmation needed on the stops ruling.

## 2. Resolution table

Codex (C) 1–15 + drop list; Fable (F) 1–24 + drop list. Checked against files, not only plan text.

| Id | Status | Reason |
|---|---|---|
| C1 | RESOLVED | PREREG rules used as written (S/W CI, sign test, floor, Inconclusive non-blocking); 5 deviations declared. s8 did change after run 2 (7f230eb→0424a7f contains e7de9e5, 4e3ba85) — claim VERIFIED. |
| C2 | RESOLVED | Fixes rewritten (cut / draft words / `[NEEDS]`); number-word guard added. Guard has FP problem → new #4. |
| C3 | RESOLVED | String-overlap rule dropped; owner ruling 2026-11-02. |
| C4 | RESOLVED | Occurrence unit, sub-bullet form, `×N` at start of Why, no ellipses, distinctness. Casefold chosen over Codex's keep-case (defensible). Edge cases → #7. |
| C5 | RESOLVED | Meaning+container, no count, argument sequences / separately delivered texts / procedures excluded, permissions not obligations, existing heading only. |
| C6 | PARTIAL | "Checkable" tightened, but "specific action on a named target" / "named artifact" still admits the kept positive example "Optimized RandomX performance" (structural-tells.md:119-120) → #2. |
| C7 | RESOLVED | light-edit restriction scoped to list-structure transforms; SKILL.md:107-118 permissions kept; C gets its own section + four `Notes:` classes; comparability precondition added. |
| C8 | RESOLVED (deferred) | Divergence stated with three cases; detector fix is a follow-up PR; green detector not evidence; status class item-aligned (alignment rule flawed → #5). |
| C9 | PARTIAL | 24 items regression-only, oracles, Notes judge, cluster bootstrap. Human anchor depends on owner (open decision 2); Notes-judge gold not specified → #11. |
| C10 | RESOLVED | Class (c): immutable source, full revised document, polish final pass. |
| C11 | RESOLVED | State table, re-confirm rule, ledger over notes/answers/approved sources, provided vs approved, "not a contribution assessment". Gaps remain → #6. |
| C12 | RESOLVED | Pilot only, shared budgets (≤4 author turns), scripted author, probes, K=2, incomplete sessions and chars recorded. Decision bar weak → #3. |
| C13 | RESOLVED | Capability rename with `test_discovery.py:16-35` and `known_human_negatives.py:12`; legacy `comms-draft` scope read-compat limited to fill/mixed; load checks; no mechanical replace. |
| C14 | RESOLVED | Matrix recomputed for 29/20 (→ TP2 FN18 TN26 FP3; "0.50" print still holds: (0.1+0.897)/2=0.498); criteria coupling repointed; MAX_QUESTIONS=3 kept with intake set to 3; quote tests assert mutation. Port coherence → #1. |
| C15 | RESOLVED | Rhythm dimension (final-pass:99), tone.md:18, R4 clauses, anchor corrected to checklist:31, step-9 NOTICE section, tenex rights reserved, Ng second-hand. |
| C-drop a (containment praise rule) | RESOLVED | Dropped. |
| C-drop b (unconditional frame/first-word/prefix) | RESOLVED | Permissions with reasons; "leave alone when it scans". |
| C-drop c (R4 clauses, residual variation) | RESOLVED | R2/R4 detection-only; tone.md, checklist Rhythm, step 8 reworded. |
| C-drop d (unqualified "Never refuse") | RESOLVED | Phrase gone; class (d) never skips fidelity/provenance. |
| C-drop e (notes diff as contribution; green checks / small NOT WORSE as proof) | RESOLVED | Ledger "not a contribution assessment"; 24 items "never used to claim gains". |
| F1 | REJECTED-OK | Owner ruled for Codex; judged in eval. |
| F2 | RESOLVED | Sub-bullet grammar; `_split_tier_bullets` claim VERIFIED by probe (`^-\s+` with MULTILINE does not split `  - `). |
| F3 | RESOLVED | Apostrophes, dashes, `*_\``, whitespace, casefold; ellipses banned rather than split (fine). |
| F4 | RESOLVED | "or doesn't matter" deleted; owner is a fact. |
| F5 | RESOLVED | Meaning+container; count rejected per Codex (defensible); existing heading only. |
| F6 | PARTIAL | Tag→`judge` + regen; consumers checked (only `aiws/catalog.py` and `test_catalog_projection.py` read enforcement — VERIFIED). Definition still ambiguous → #2. |
| F7 | RESOLVED | Oracles for list items, bare = run-1 K=1 reuse, review absolute-only, harm rule. `structure_change` class replaced by count/heading oracles (fine). |
| F8 | PARTIAL | Artifact shape named but checks kept are incompatible with it → #1. |
| F9 | RESOLVED | Criteria in stage 3, N1–N4, negative checklist, self-scan; final = final pass. |
| F10 | RESOLVED | Class (d) collapses stops not stages; "Draft a decision memo…" is not a skip. |
| F11 | RESOLVED (bar weak) | Bare-staged arm added, shared budgets; "≥ on traceability or cost" → #3. |
| F12 | RESOLVED | SYCOPHANTIC+C3 scan, invariance pair, unraised objection, vague answer + contradicting number. |
| F13 | RESOLVED | Boundary sentence in both descriptions, row rename, near-misses both ways, ROUTER_ANCHORS. |
| F14 | RESOLVED | final-pass:99, :25 "four→five", step 8 Verbatim Anchors sentence kept. |
| F15 | RESOLVED | Anchor corrected; four classes enumerated. |
| F16 | RESOLVED | "every sentence carries a flagged pattern". |
| F17 | RESOLVED | H7 sub-section with cluster validity; detector disagreement stated. Q4 stretch → #17. |
| F18 | RESOLVED | Header sentence only; table pinned by `test_catalog_sync.py`. |
| F19 | RESOLVED | R4 detection-only. |
| F20 | RESOLVED | Knife edge acknowledged (probe: 5 bold labels + verb-first = 13 < 14; 6 verb-first items = 0); genre memo; `test_fidelity_classes.py:41-44` + docstring; status tiers. |
| F21 | RESOLVED | Root README:26,97,112; SKILL.md:3/:172; voice-lookup:64; test_discovery; known_human_negatives; both contract tests all listed. |
| F22 | RESOLVED / Ng REJECTED-OK | NOTICE section, `Sources:` tags, no article examples; Ng kept with "second-hand, not verified" (Codex 15's version). Legend rows missing → #14. |
| F23 | RESOLVED | Unsourced-claims check, expected empty, hit = defect. |
| F24 | RESOLVED | One commit per item, B revertible. |
| F-drop (actor clause; contribution diff; R4; bare K=3; stage-6 review) | RESOLVED | All adopted. Ng: see F22. |

## 3. New findings (most severe first)

**#1 [major, Step 10 "Harness port"] The kept checks cannot apply to the artifact as defined. VERIFIED.** `run_draft_cases.py:47-54`: `DRAFT_HEADING="## draft"`, `CRITERIA_DIMENSIONS`, `MAX_QUESTIONS=3`; `count_questions` counts `?` in the pre-draft section; `criteria_labels` needs a criteria heading in that same section. Plan: artifact = "one stage-5 fill turn given a confirmed outline plus notes", while keeping all three checks "since the criteria now live in stage 3". A fill turn has no questions (check vacuous) and no criteria (check fails on every conforming artifact). If instead the artifact is stage-3 + stage-5 concatenated, stage 3 by design carries the sharpen questions (≥1 unraised objection, weakest point, what would change the call, provenance per number, framing alternatives) — more than 3 `?` marks — so `question_count` fails conforming comms-shape output. Also `draft-02-thin-brief`'s good_draft asks ≤3 questions then proceeds to a draft in the same turn = one-shot-from-brief, so the plan's own retirement rule removes the only `question_count` planted positive; `mutants_draft.py:146` and `holdout_adversary.py:119` run that family only when a case declares it, so coverage disappears silently. **Fix:** artifact = `## intake` segment ∥ `## outline` segment ∥ `## draft`; `question_count` on the intake segment only; `criteria_dimensions` on the outline segment; rewrite draft-02 as intake-only (good: ≤3 questions then STOP; bad: 4+ or proceeds past the stop).

**#2 [major, Step 9 Definitions ↔ A/T7] The "checkable" definition classifies the plan's own T7 positive as not-T7. VERIFIED.** Definitions: checkable = "a specific action on a named target" or "a named artifact, person or ticket". T7 keeps "Stable mining efficiency / Reliable pool connectivity / Optimized RandomX performance" as a tell example (structural-tells.md:119-120). "Optimized RandomX performance" is an action on a named target and names an artifact → checkable under the definition, T7 under the example. Codex 6 named exactly this; v2 kept both. `test_parallel_items_contract.py` would pin the contradiction. Also unspecified whether T7's "5+ consecutive bullets" and "≤6-word" survive the reframe; if the tell is emptiness they become unmoored numeric text-property thresholds. **Fix:** "specific action" excludes evaluative verbs (optimized/improved/enhanced/streamlined/unlocked) unless paired with a number or outcome; delete the 5+/≤6-word counts.

**#3 [major, Step 10 eval "Decision"] The proceed bar passes regardless of skill value. JUDGMENT.** "≥ bare-staged on traceability *or* cost": `find_fabrications` traceability will sit at/near 100% for both arms (ties satisfy ≥), so the bar is met even if the skill adds nothing. The five probes (wrong insistence, correct correction, vague answer, contradicting number, invariance) are the only measures that can show value and none feeds the decision. **Fix:** proceed only if strictly better than bare-staged on ≥1 of {planted-gap `[NEEDS]` hit rate, unsupported-claim-insisted kept as `[NEEDS]`, contradicting number flagged} and not worse on traceability; drop cost from the "or" (report it).

**#4 [major, Step 9 §E "Fix fidelity"] The number-word guard rejects legitimate Fixes. VERIFIED probe.** Against the example draft (no numbers), "Pick one.", "no one knows", "one of the metrics", "half the team" all flag. H2's own catalog fix is literally "Pick one." (hedging-filler.md:36). **Fix:** guard digits and two…twenty/hundred/thousand/million/percent/dozen; exclude `one` and `half` (document the gap; semantic invention is the judge's job).

**#5 [major, Step 9 §B "Fidelity check"] Position-first alignment fires on a legitimate reorder, and item order is not an invariant. VERIFIED probe.** before `[Investigating A, Fixed B]` → after `[Fixed B, Investigating A]` fires `status` at item 1. B's invariants cover status, actor and labels but not order, and no permission allows reordering, so the gap is both a spec hole and a checker FP. Also undefined when neither side has ≥2 list items (running-prose fixtures with `fidelity_check: true` would otherwise collide with `strength`). **Fix:** add invariant "item order is preserved"; align by ticket id / content words first, position as fallback; return `[]` when either side has <2 items.

**#6 [major, Step 10 state machine] Three undefined transitions. JUDGMENT.** (i) Class (b) ends "the author decides" with no continuation: when the author says "ok, rewrite it with those fixes", nothing routes into fill/final (v1's "fixes route to comms-polish" was removed, nothing replaced it). (ii) No default for an ambiguous request with a draft attached ("look at this memo before I send it"); the boundary sentence covers "how it reads" vs "whether it holds", not neither; comms-polish has "if unclear, use rewrite" (SKILL.md:82), comms-shape has nothing. (iii) Skip inside mixed: does (d) apply to (c), where do the two printed lines go relative to the whole revised document, does the polish final pass still run? **Fix:** (b) + author asks for changes → stage 5 on the reverse-outline with the ledger → stage 6; ambiguous → one classifying question counted against the 3; (d)∧(c) → mini-outline as two lines above the full document, final pass unchanged.

**#7 [major, Step 9 §D/E checker] Spec edges that will produce false rejections or untested paths. VERIFIED against check_report.py.** (a) `_is_quoted` today accepts any ordered pair anywhere (check_report.py:76-83); "outer quote pair is the first and last character" rejects `**Quote:** "x" (para 2)` — say whether trailing text is allowed. (b) Define: single instance with `×1`; sub-bullets without a leading `×N`; N>5 with 3–5 shown. (c) A "Nothing…" bullet mixed with a quoted strength should be rejected like `- None.` mixing (check_report.py:202-206) — not stated. (d) Per-snippet count can't see two different snippets covering one span — acceptable, state it. (e) The new section needs an *accepted-in-position* artifact, not only the "misplaced" mutant, or the acceptance path is untested; `run_report_contract.py` passes no draft, so verbatim/Fix mutants need the example draft as a fixture file (e.g. `evals/audit_report/draft.md`) — unlisted.

**#8 [minor, Step 9 §B ↔ SKILL.md File Edits] Prefix move into an existing heading contradicts "Preserve ... headings" (SKILL.md:356) in `edit` mode. VERIFIED.** Fix: in `edit`, move a prefix only into a lead-in sentence, or amend File Edits step 2 for this one case.

**#9 [minor, Step 9 §B light-edit] "No list-structure transformations" reads against SKILL.md:127-129 ("A light cleanup of terse text is still welcome when asked for: consistent bullet formatting, typos", which applies to both modes). VERIFIED.** State explicitly that punctuation/capitalization/marker consistency stays allowed; only frame, in-item word order and prefix moves are barred.

**#10 [minor, Step 9 §C] Evidence gaps now have two homes in review. VERIFIED.** SKILL.md:261-262 routes a fact-only repair through Quote/Tell/Why/Fix (needs a catalog id); the new section "needs no catalog id and no Fix". Define: a gap with a catalog match (S2/S4/S8) stays a finding; a missing slot/n/interval with no tell goes to the new section; never both.

**#11 [minor, Step 9 eval] Oracles confounded by sampling noise; Notes-judge gold unspecified; harm rule undefined per run. JUDGMENT.** With fresh K=3, finding sets differ run-to-run without the pressure line, so "finding set and severities must not change" fails on noise; "×5 (+1 set aside)" is a content judgment (which contrast is evidence-answered), not an oracle. Precision/recall for C items needs a gold conflict list from the item author — not stated. Harm rule: define per-run vs per-item (does 1/3 s9 with 0/3 s8 block?) and pre-declare the oracle→commit map (most oracles → B). Fix: compare coarse statistics 3-vs-3 and report; check N-quoted = N-claimed deterministically, leave N=5 to the judge; require the gold list in the item spec.

**#12 [minor, Step 9 fixtures] `fail-lists-recast` has no deterministic catch and no named `fail_dimension`.** `test_fail_dimension_is_weighed_by_the_judge` (test_fixtures.py:850-856) requires it in `rubric_focus`; rubric.md says nothing about list→prose over-editing, so the advisory lane won't catch it either. Name it (`meaning_preserved`, as `fail-restraint-overedit-en` does) and say it is judge-only. "All are detector_blind, expect_baseline: miss" — gold-FAILs carry neither field today (18/18); harmless but imprecise.

**#13 [minor, Step 9 commits] "fixtures/tests" as a separate final commit leaves A (T7 tag + registry regen), D+E (conforming.md + checker) and B (presets + contract tests) possibly red at intermediate commits, which defeats per-commit bisect/revert.** State: every commit keeps `run_all.sh` green; B's contract tests live in commit B.

**#14 [minor, Attribution] `Sources:` tags for fsdatalab/tenex need legend rows.** 00-index.md:168-177 defines the tag legend; NOTICE.md:183 says update it when adding sources. Plan adds tags but no rows ("ideas only, no text copied; tenex rights reserved").

**#15 [minor, Step 10 eval] "arm hidden" is nominal (stops and 2–3 framings reveal the arm); SYCOPHANTIC is 4 regexes (patterns.py:209-214) — weak control.** State both as limits.

**#16 [minor, Step 10 archive] `claude plugin validate .` at repo root may discover `archive/comms-draft/SKILL.md` (`name: comms-draft`); `validate_packaging.py` scans only `skills/*/`.** Add to the load checks.

**#17 [minor, Step 9 §F] Q4 is preset-based ("leave alone" list, rhythm-stylometric.md:155-156); "formal, legal or academic register" is not a preset.** The H7 sub-section must state that reading explicitly.

**Numeric thresholds, classified.** Legit report formatting: quote all when N≤5, 3–5 when N>5; "four→five things". Legit eval budgets: K=3/K=2, 8 packets, ≤4 author turns, 90% CI ±0.10, p<0.10, floor W≥0.85/S≤0.10, ~12 items, ~10 labels. Owner-ruled: ≤3 intake questions (short path "up to 2" is a sub-budget). Fixture-authoring constraint borrowed from the detector: "bold labels ≤3, no tier-3 words" (detector.py:271) — keeps fixtures `miss`, not a skill lever. Pre-existing text-property levers v2 edits around but leaves: T5 "8+ bullets / 200 words", "3 headings / 300 words"; T7 "5+", "≤6-word" (fate unspecified — #2); F2 "one bold per section" (scoped to prose). **v2 introduces no new text-property lever.**

**Pins v2 will break that it lists:** all found (test_fixtures.py:79 `(27,0)`, :1059 `(27,18)`, :1156 `(2,16,24,3)`; test_report_contract.py:152-164; test_fidelity_classes.py:41-44; test_catalog_sync; registry projection; test_untrusted_content_contract.py:26-32; test_fact_interpretation_contract.py:64-67; test_router_routing incl. `routes to \`comms-draft\`` at :86; test_skill_lint count 5 + trigger coverage ≥2 per sub-skill). **Unlisted but affected:** `test_fail_dimension_is_weighed_by_the_judge` (#12); `evals/fixtures/draft_cases.json` `_doc.artifact_shape` text (#1); `mutants_draft.py`/`holdout_adversary.py` docstrings naming comms-draft (cosmetic).

## 4. Remaining owner decisions

1. **Approve v2 with the changes above** (#1, #3, #6 before any step-10 code; #2, #4, #5, #7 before step-9 code).
2. **Human anchor:** blind-label ~10 items (plan already asks).
3. **Stops ruling vs collapsed paths.** The ruling is "required stops after the thesis and after the outline". v2's short path (one combined stop), class (c) (one stop) and class (d) (no stops) collapse them. Confirm that genre-sized and explicit-skip collapses are within the ruling, or the short/mixed paths must keep two stops.
4. **Retired draft cases.** Owner should see the list before step 10 merges (plan promises it in the PR); with #1 it will include draft-02 in its current form.

Everything else (T7 definition tie-break, status vocabulary and alignment, evidence-gap home, guard word list, checker edge rules, legend rows, commit greenness) is author-level and needs no ruling. Step 9 is implementable from v2 once those author-level items are written in.
