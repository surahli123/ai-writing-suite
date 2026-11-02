# Fable 5.1 round-3 targeted check: plan diff 621d9e4 → 0db4071 (2026-11-02)

VERIFIED_AGAINST: claude/laughing-rubin-mkkadx-s9-lists-review @ 0db4071
MODEL: Fable 5.1 subagent, read-only. Report reproduced verbatim; line numbers refer to the plan at 0db4071.
Disposition: docs/plan-step9-and-comms-shape-2026-11-02.md, "Review log (round 3, targeted)".

---

## Round-3 re-check: plan diff 621d9e4 → 0db4071 (docs/plan-step9-and-comms-shape-2026-11-02.md)

Read-only. Line numbers below are the plan at 0db4071 unless a file path is given. Probe: /tmp/claude-0/-home-user-ai-writing-suite/330ac9e5-004d-5681-a680-86276d534b6f/scratchpad/fable-review3/probe_fixfid.py (simulates §E Fix-fidelity as written).

### (a) Verdicts
- **Step 9: READY AFTER MINOR EDITS** — one internal contradiction (195 vs 219), one definition hole (T7 prong 2), one deterministic-guard asymmetry (`one`/`half`), two precedence/API ambiguities in the `status` class. All author-level, each a one-sentence edit.
- **Step 10: READY AFTER MINOR EDITS** — the harness port as written turns `run_draft_cases` red on draft-01/-02/-03; the ledger does not say what the "source" of an author-approved model proposal is, so the skill's stage-6 check and the eval judge can disagree. Owner decision 2 (stops vs collapsed paths) remains open and is already tracked.

### (b) Disposition table

| Finding | Status | One line |
|---|---|---|
| F2-1 harness port | **PARTIAL** | Segments + draft-02 intake-only are in (463-474), but: draft-01/draft-03 artifacts are still one-shot `criteria + ## Draft` transcripts and must be rewritten into `## outline`/`## draft` or `criteria_dimensions` (now outline-scoped) fails draft-03; draft-02 keeps `checks: [question_count, no_fabrication, needs_marker]` + `requires_needs_marker: true` (draft_cases.json:43-44) — an intake-only good_draft has no `[NEEDS]`, so `needs_marker` fails it; and if "Draft checks read `## draft`" (468) scopes `no_fabrication`, `_body_insert`'s no-`## draft` fallback (mutants_draft.py:55-64) drops the must-catch mutant into the intake segment → escape → run fails. |
| F2-2 "checkable" admits T7 example | **PARTIAL** | Evaluative-verb clause and 5+/≤6-word deletion are in (81, 94), but prong 2 of Checkable (77, "a named artifact, person or ticket") still makes "Optimized RandomX performance" checkable — RandomX is a named artifact. Fable named both prongs; only prong 1 was closed. `test_parallel_items_contract.py` (282) would pin the contradiction. |
| F2-3 pilot bar | APPLIED | 516-524. |
| F2-4 number-word guard | APPLIED | 223 (see new issue 3 for the asymmetry it creates). |
| F2-5 alignment / order / <2 | APPLIED | 122, 137-142; superseded by R1 as the log says. |
| F2-6 transitions | APPLIED | 354-357. |
| F2-7 checker edges | **PARTIAL** | (a)(b)(c)(e) in at 194, 207-208, 180, 229; (d) at 195 now contradicts R4's rule at 219 (new issue 1). |
| F2-8 prefix in `edit` | APPLIED | 116; SKILL.md:356 verified. |
| F2-9 light-edit cleanup | APPLIED | 127; SKILL.md:127-129 verified. |
| F2-10 two homes | APPLIED | 166; S2/S4/S8 exist. |
| F2-11 oracle noise / gold / map | APPLIED | 324-333 (map omits the boast-list judge item; minor). |
| F2-12 `fail-lists-recast` dimension | APPLIED | 270; test is at test_fixtures.py:852-858 (plan says 850-856, harmless). |
| F2-13 green commits | APPLIED | 62. |
| F2-14 legend rows | APPLIED | 262; NOTICE.md:183 verified. |
| F2-15 limits | APPLIED | 512-514. |
| F2-16 archive discovery | APPLIED | 459 (note: the step-10 eval's comms-draft arm must then be run from file content; no host loads `SKILL.archived.md`). |
| F2-17 Q4 preset-based | APPLIED | 236. |
| C2-R1 entity alignment | APPLIED | 137-147; residual ambiguity: "position is used only after the entity is confirmed" has no defined role once entities match; "unambiguous entity" is not operationalized (ticket-ID regex, then content-word key). |
| C2-R2 claim→source list | APPLIED | 497-503; see new issue 5 for the ledger/approval gap. |
| C2-R3 review-only pass rule | APPLIED | 330; the Ship rule sentence (302) still states only the PREREG rule, so the oracle blocks are an unreferenced extra ship condition (335 also duplicates 330). |
| C2-R4 span assignment | APPLIED | 219, but contradicted by 195 (new issue 1). |
| C2-R5 normalized number compare | **PARTIAL** | Value+unit, NEEDS strip, coverage limit, controls are in (221-225); but excluding `one`/`half` symmetrically creates the inverse false rejection, and number-word composition is undefined (new issue 3). |
| C2-R6 cost direction | APPLIED | Resolved by F2-3; cost reported only (524). |
| C2-R7 light-edit word order | APPLIED | 125. |

### (c) New issues introduced or exposed by the diff

**Major**
1. **195 vs 219 contradict.** 195: "Two different snippets covering one span are not detected; that limit is stated in the contract." 219: "two snippets of different length taken from one spot are rejected." The contract would state a limit the checker no longer has. *Fix:* delete the 195 sentence, or reword it to the limit that actually remains: "The same span quoted by two different findings is not detected."
2. **T7 prong 2 still admits the kept example** (77 vs 81/92). *Fix:* reword prong 2 to "a named artifact, person or ticket **together with what was done to it or what state it is in**" (a name alone is a noun, per 81).
3. **Fix-fidelity `one`/`half` exclusion is applied on both sides**, so draft "one dashboard" + Fix "1 dashboard", draft "half the team" + Fix "50%", draft "one in five" + Fix "1 in 5" are rejected (probe output: three REJECTs), while the plan says numeral↔word equivalence passes; "3 thousand"/"three thousand" vs "3,000" also rejects because composition of number words is undefined. *Fix:* parse `one`/`half` (and compose "N thousand/million/hundred") on the **draft** side, skip them only on the **Fix** side, and say so at 223.
4. **`status` class: the <2 rule and the unscored rule conflict** for before ≥2 / after <2 items (142 says "no finding"; 141 says unalignable items are coverage gaps that "never count as a pass"). A rewrite that merges two status items into one and inflates a status is silent. *Fix:* apply the <2 rule to `before` only; when `before` has ≥2 and `after` has <2, report every `before` item as unaligned.
5. **Ledger has no "source" for a model-proposed, author-approved claim** (387-389 lists sources: draft, notes, author answer by turn, approved external source; tag: "model-proposed and author-approved"). Stage 6 says "every claim must trace to the ledger" (382); the new judge rule says approval "is not evidence" (499). The skill can pass its own check on a claim the eval counts unsupported. *Fix:* state that approval is a tag, not a source; a model-proposed row's source is the author-supplied evidence or `[NEEDS: evidence]`, and stage 6 fails any row with an empty source.
6. **Harness port goes red as written** (F2-1 PARTIAL above). *Fix:* add to 469-474: draft-01/-03 artifacts are rewritten into the three-segment shape; draft-02 drops `needs_marker`/`requires_needs_marker` (and `no_fabrication`, or `no_fabrication` keeps scanning the whole artifact); `JUDGE_TEMPLATE` `question_discipline` (run_draft_cases.py:541-543, "then proposes inferred criteria and proceeds") is updated to the stop semantics along with `_doc.artifact_shape`.

**Minor**
7. `status` "unscored" has no return channel: `fidelity_violations` returns violations only and `test_faithful_rewrites_pass` / fixture test assert `== []` (test_fidelity_classes.py:54, 67). *Fix:* name the channel (e.g. a second return value or a `("status_unscored", …)` tuple the `== []` tests filter out).
8. 194 quote rule "closes at the last matching quote mark" + optional parenthetical location: `"…" (see "Overview")` swallows the location into the snippet and fails verbatim. *Fix:* "the location may contain no quote marks."
9. Oracle-to-commit map (324-328) omits the boast-list judge item and the "scans better"/Notes-judge items; no rule says judge-only items are report-only. *Fix:* add "judge items are reported, never block."
10. Ship rule (302) does not reference the oracle Harm/Pass blocks (329-330); 335 duplicates 330. *Fix:* append "plus no oracle block under the targeted-set rules" to 302 and delete 335.
11. F2-16: the step-10 eval's third arm (493) loads "the archived comms-draft"; after the rename no host can load it as a skill. *Fix:* say the arm is run from the file's content as a system prompt.

### Nothing else blocks
Verified against files: run_draft_cases.py:47-54/293-348/351-387, check_report.py:76-87/134-148/198-216, mutants_draft.py:55-64/146-168, holdout_adversary.py:47-56/119-124, test_fixtures.py:852-858, SKILL.md:107-129/356, test_report_contract.py:152-164 (no-op confirmed: target string absent from conforming.md:6), 00-index.md:168-177, NOTICE.md:183, hedging-filler.md:36 ("Pick one."), structural-tells.md:112-125, rhythm-stylometric.md:155-156, test_fidelity_classes.py:41-44, test_skill_lint.py:15/57 (count 5 = router + 4 sub-skills; archive outside `skills/*/`), validate_packaging.py:142 (scans `skills/*/SKILL.md` only), audit-report-format.md:15-20 (the worked example does carry a draft to save as `draft.md`).
