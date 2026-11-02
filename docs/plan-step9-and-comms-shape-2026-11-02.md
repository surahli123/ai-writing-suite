# Implementation plan v2: comms-polish step 9 and comms-shape (step 10)

Date: 2026-11-02.

**Status:** v2.1. It has been revised after two round-1 adversarial reviews and Fable's round-2 review; Codex's round-2 review is pending. It is waiting for the owner's go-ahead, and no skill file has been changed.

**Reviews:**
- Codex 6.1 Astra (medium): `reviews/2026-11-02-codex-plan-step9-comms-shape.md`. Verdicts: not stated per step. It reported 1 blocker and 13 major findings.
- Fable 5.1: `reviews/2026-11-02-fable-plan-step9-comms-shape.md`. Verdicts: step 9 GO WITH CHANGES; step 10 REWORK.

**Base:** s8 tip `0424a7f`.

**Background:** `notes/proposal-polish-and-outline-2026-11-02.md`, on the research branch.

The review log at the end maps every finding to what v2 did about it.

## Owner rulings

**Rulings from 2026-11-02:**
- Step 9 covers A–G.
- `comms-shape` is one skill with two entry points.
- It has required stops after the thesis and after the outline.
- `comms-draft` is archived.

**Earlier rulings that still apply:**
- R1 + amendment: claims, not decisions.
- R2: evidence-answered objections are kept.
- R3: per-step gates are replaced by the pre-registered v1 protocol.

**Constraints:**
- No numeric levers.
- No em-dash ban.
- No agent-reader framing.
- No manufactured personality.
- The suite may draft and rewrite.

## What v2 changes, in one paragraph

**Step 9 keeps its scope with corrected mechanics:**
- **List rules.** "Parallel set" is defined by meaning and container, not by a count. The list rules become permissions with a reason, not obligations.
- **T7.** Its exemption requires something a reader could verify.
- **light-edit.** It loses none of its existing permissions.
- **Consistency findings.** They get their own report-only output.
- **Praise check.** The string-overlap rule is dropped.
- **Quotes and counts.** A real quote grammar is defined: occurrence unit, multi-instance form, `×N` syntax, normalization and distinctness.
- **Worked example.** Its fabricated Fixes are rewritten, and a Fix fidelity check is added.
- **Leftover variation instructions.** R2, R4, the Rhythm dimension and `tone.md` are removed.
- **Attribution.** It ships in step 9.
- **Eval.** It now uses the v1 verdict rules as written, and every deviation is declared.

**Step 10 is reworked:**
- **Explicit state machine.** It has a mixed-mode branch, a defined "skip" path that collapses stops but not stages, and a claim-provenance ledger.
- **comms-draft behaviors.** Its four behaviors are kept, and the final step is the final pass, not a review report.
- **Routing.** The router boundary is "how it reads" (polish) versus "whether the argument holds" (shape).
- **Migration.** The migration list is complete.
- **Eval.** It is a pilot with a bare-staged comparator and shared budgets. It makes no non-inferiority claim.

## Step 9: comms-polish (branch `…-s9-lists-review`, one PR)

Paths are relative to `skills/ai-writing-suite/`.

**Commits, one per item:** A, B, C, D+E, F, G. Each commit carries the tests and fixtures it pins and keeps `run_all.sh` green, so any commit can be reverted alone. B is the riskiest change, so it can be reverted alone if the eval localizes harm to it.

### Definitions used throughout

**Parallel set:**
- **What it is:** items of one kind shown together in one container (one list, feed, set of cards or set of rows). Each item answers the same question about a different subject, such as the status of each workstream, the title of each session, or the result of each metric. A reader compares them side by side.
- **What it is not:**
  - argument sequences (reasons, steps of an explanation, a decision / risk / ask trio);
  - items answering different questions;
  - texts delivered separately (each email subject or notification is seen alone);
  - numbered procedures, timelines, quotes and tables.
- **No item count.** The test is meaning and container.

**Checkable:** a reader could verify the item. It carries at least one of:
- a specific action on a named target;
- a named artifact, person or ticket;
- a number;
- an outcome.

A noun is not information, so "Optimize customer outcomes" and "Unlock enterprise value" are not checkable. An evaluative verb (optimized, improved, enhanced, streamlined, unlocked, boosted) is not a specific action unless a number or an outcome comes with it, so "Optimized RandomX performance" is not checkable either.

### A. Catalog and checklist scope

- **R1** (`_shared/patterns/rhythm-stylometric.md`, 15-39): add a validity line saying R1 concerns running prose. Items of one parallel set are not rhythm units, and one shape across them is correct.
- **R2** (43-51): make it a detection signal, never a length target, like R1. Scope it to prose. Delete "Vary deliberately. Some paragraphs one sentence."
- **R3** (55-71): add parallel sets to the low-TTR carve-out.
- **R4** (73-86): make it a detection signal only. Delete "choose the second or third word that comes to mind" and "make unexpected analogies"; the second is also an L7 conflict. The fix becomes: choose the precise word for this reader, including the field's own terms, and never edit for surprise.
- **T5** (74-91): the "8+ bullets in under 200 words" signal does not apply to a parallel set with checkable items.
- **T6** (93-110): the tell stays a bold header that repeats the item's own words. A consistent label from a closed set (`**Shipped:**`, `**Blocked:**`, `**Owner:**`) is structure. The fix no longer offers "convert to prose" for a parallel set.
- **T7** (112-125):
  - The tell is items with nothing checkable, not symmetry. It keeps three positive examples: "Stable mining efficiency / Reliable pool connectivity / Optimized RandomX performance", "Optimize customer outcomes / Unlock enterprise value", and "Fast setup / Clean design / Easy onboarding".
  - A verb-first status list with specific actions on named targets is not T7.
  - The "5+ consecutive bullets" and "≤6-word" counts are deleted. Once the tell is emptiness, they would be bare text-property thresholds.
  - The fix rewrites items as checkable claims using facts already in the source, or flags the missing detail. Convert to prose only when the items are really an argument.
  - The enforcement tag changes from `regex` to `judge`, and the registry is regenerated (`python3 -m aiws.catalog`). Before committing, check what consumes the enforcement tag.
- **T9 / T13** (144-163, 208-225): add parallel sets to T9's swap-test exemption. Add titles, card text and list items to T13's genre-normal list.
- **F2** (`punctuation-formatting.md` 29-40): one consistent label per item of a parallel set is not erratic bolding. The one-per-section rule is about inline bolding in prose.
- **L1** (`lexical-tells.md`): one header sentence only, "pick one replacement per concept and keep it". The table rows stay untouched, because `evals/test_catalog_sync.py:41-48` pins them to `TIER1`.
- **L3** (119-135): add cross-item consistency. Add a DS caution: users, accounts and sessions are distinct terms, and so are holdout and control. Merge only where the draft itself shows one referent; otherwise flag.
- **comms-polish SKILL.md:**
  - In step 5 (~242), "uniform sentence length" becomes "uniform sentence length in running prose".
  - In step 8 (269-272), "Vary rhythm" becomes "In running prose, let rhythm follow the content (R1); a parallel set keeps one shape". The Verbatim Anchors / `precedence-policy.md` sentence stays.
- **Final-pass checklist:**
  - "Repetition is gone" becomes "Repeated content is gone; repeated structure and terms across a parallel set stay".
  - The Rhythm scoring dimension (line 99) becomes "in running prose, rhythm follows the content; no march of identical moves".
- **`_shared/knowledge/tone.md:18`:** replace "Vary sentence length" with "In running prose, let rhythm follow the content; don't edit toward a length pattern". kb_lint, smoke and validate must pass.

### B. Parallel-set rules (new unnumbered presets section)

**Location:** `references/scenario-presets.md`, after "Data-science documents (KB-backed)". It stays unnumbered because six numbered presets are pinned. It is referenced by one line in SKILL.md step 5.

**Permissions, each with a reason:**
- **One frame.** When mixed grammatical forms make a parallel set harder to scan, `rewrite` may give the items one frame. Leave the set alone when it already scans, or when a difference in form carries meaning.
- **Distinguishing word first.** When the shared words hide what tells items apart, the distinguishing word may move to the front. If this conflicts with one frame, the distinguishing word wins.
- **Shared prefix.** A prefix shared by every item may move into an **existing** heading or lead-in. Never add a heading or lead-in, since that adds content. Never do this for texts delivered separately. In `edit` mode, headings are preserved (File Edits step 2), so the prefix may move only into an existing lead-in sentence.

**Invariants:**
- Status and tense follow the author. Done stays done; "investigating" never becomes "fixed"; "planned" never becomes "shipped". If an item's status can't be told, flag it.
- The actor is dropped only when the heading or lead-in states it. An owner is a fact. Never invent an actor, and keep blameless system-as-subject in incident notes.
- The author's status labels stay a closed set.
- Item order is preserved.

**Mode gating:**
- `light-edit` makes **no list-structure transformations**: no frame unification, no word reordering inside items, no prefix moves. Every existing light-edit permission stays:
  - grammar, spelling, ambiguity, and mismatch with a user-supplied source (SKILL.md 107-118);
  - consistent punctuation, capitalization and bullet markers (SKILL.md 127-129).
- `rewrite` and `edit` use the permissions above.
- `review` and `detect` flag only.

**Not taken from the source article:**
- dropping detail to make items uniform, because it deletes facts;
- stronger-sentiment verbs, because they add a claim.

**Fidelity check:** a deterministic `status` class in `evals/fixtures/fidelity.py`.
- It uses a closed vocabulary with tiers: planned < in progress < done.
- It is item-aligned. Items are matched by shared ticket IDs and content words first, with position as the fallback, so swapping Investigating and Fixed between two items is caught and a reorder is not mistaken for a status change.
- Any upward move in an item fires.
- When either side has fewer than two list items, it returns no finding and leaves running prose to the existing classes.
- Add it to the pinned class set in `evals/test_fidelity_classes.py:41-44` and to the docstring. It gets one mutant, one faithful control and the swapped-entity case.

### C. Consistency across a parallel set (report only)

**Final-pass checklist:** L1 "The document agrees with itself" changes "Check four things" to five. The fifth is that parallel items reporting comparable metrics either carry the same slots (n, interval, baseline, unit) or the difference is reported, and one metric or status keeps one name.
- It applies only when the metrics are comparable and the slot applies to all of them.
- Never fill a slot, delete the extra one or pick a winner.

**Where it is reported:**
- **`rewrite` / `edit`:** in `Notes:`. SKILL.md `## Output` now lists exactly four allowed classes, each with its location:
  - evidence flags (steps 6, 7, 11);
  - alignment changes (step 6, "what changed and why");
  - decision-gap flags (R1 amendment);
  - consistency conflicts (final-pass L1).

  This replaces the current "nothing else". The current wording already contradicts step 6 and the final-pass checklist (line 31).
- **`detect` / `review`:** in a new optional section, `## Consistency and evidence gaps`. It goes after `## What already reads well` and before Coverage/score.
  - Each bullet gives a location and what differs.
  - It needs no catalog id and no Fix, because these are not AI tells.
  - A gap that matches a catalog entry (S2, S4, S8) stays a finding with Quote / Tell / Why / Fix. A missing slot, n or interval with no matching tell goes here. Never both.
  - Omit the section when it is empty.
  - The checker accepts the section only in that position.

### D. Honest strengths (contract §3)

**Contract text:**
- A strength is a verbatim quote plus a reason that fits only that passage.
- Don't praise a property the report criticizes elsewhere.
- No praise for tone, effort, topic or general structure.
- Assume the pull is toward crediting the draft.
- Prefer `- Nothing here reads well yet: every sentence carries a flagged pattern.` over a stretch. The current example line "the draft is AI throughout" is an authorship verdict in spirit and goes away.

**Checker:**
- Each strength bullet either carries a quoted snippet or starts with "Nothing". A "Nothing" bullet mixed with quoted strengths is rejected, the same way `- None.` mixed with findings is.
- With a draft, the snippet must be verbatim (rules in E).
- **No overlap rejection.** A sentence can hold a checkable fact and a vague modifier, and praising one while flagging the other is legitimate. Whether a strength praises a criticized property is judged in the eval, not by string matching.

**Worked example and `conforming.md`:** the strengths line becomes "Nothing here reads well yet". The **Fixes are rewritten with no invented facts**: today they add "three tools down to one screen", "three metrics every morning" and "under a second". Each Fix becomes:
- a cut;
- a plain version using only the draft's words, keeping modality (for example, "It may help surface insights.");
- or a quoted `[NEEDS: …]`.

### E. Quote grammar, counts, verbatim and Fix fidelity (contract §2)

**Instance.** An instance is one contiguous span of the draft that shows the pattern.
- Quote the shortest complete span.
- **No ellipses.**
- The outer quote pair opens the snippet and closes it at the last matching quote mark, so quotation marks inside the draft stay intact. An optional location in parentheses may follow the closing quote, e.g. `"…" (¶2)`.
- The count is of instances. Two different snippets covering one span are not detected; that limit is stated in the contract.

**Single instance:** `**Quote:** "…"` on one line, as today.

**Multiple instances:** `**Quote:**` alone on its line, followed by one indented sub-bullet per instance (`  - "…"`). The checker collects sub-bullets until the next field marker; `_split_tier_bullets` only splits unindented bullets.

**Counts.** When there is more than one instance, `**Why:**` **starts** with `×N`, where N is the number of instances counted as the tell. It may add `(+M set aside: <reasons>)`. Set-aside reasons are:
- evidence-answered (R2);
- a documented voice-profile habit;
- inside quotes or code.

The number of quoted instances must be N if N ≤ 5, or 3–5 if N > 5, with Why naming where the rest are. A "×10" anywhere other than the start of Why is ignored. Edge rules:
- A single inline instance carries no `×N`; `×1` is accepted.
- Sub-bullets without a leading `×N` (N ≥ 2) are rejected.

**Counts describe; they never become quotas or rewrite targets.**

**Verbatim check.** `check_report(text, catalog_ids, draft=None)` gets a new optional argument. When a draft is given:
- Every Quote instance and every strength snippet must be found in the draft after normalization:
  - unify straight and typographic double quotes, single quotes and apostrophes;
  - unify `—`, `–`, `--` and `---`;
  - strip `*`, `_` and backticks;
  - collapse whitespace;
  - casefold.
- Instances must be distinct: each snippet must occur in the draft at least as many times as it is quoted.

**Fix fidelity (draft given).** Digits and number words in a Fix (two…twenty, hundred, thousand, million, percent, dozen) must appear in the draft. `one` and `half` are excluded, because plain fixes use them ("Pick one.", which is H2's own catalog fix). This is a cheap guard; semantic invention is judged in the eval. The contract text says a Fix uses only material in the draft, and shows a cut or `[NEEDS: …]` when a better sentence would need facts the draft lacks.

**Test artifacts.** The worked example's draft is saved as `evals/audit_report/draft.md`, so the verbatim and Fix-fidelity mutants have a draft to check against. `conforming.md` gains the consistency section in its accepted position, so the acceptance path is tested and not only the "misplaced" mutant.

**Existing tests.** `run_report_contract.py` works unchanged without a draft. The two no-op tests `test_smart_quotes_accepted` and `test_guillemet_quotes_accepted` (`test_report_contract.py:152-164`) are fixed: their target string doesn't occur in `conforming.md`. Each now asserts that the mutation changed the input.

### F. Connective openers (H7 sub-section, cluster only)

- Add a named sub-section to H7 (`hedging-filler.md` 114-135) for Moreover / Furthermore / Additionally / In conclusion / In summary.
- **Validity:** only a cluster counts, meaning connectives opening several sentences in one passage. A single use is never a finding. The entry carries its own carve-out for formal, legal and academic register, because gate Q4 is preset-based and has no such preset. Gate Q5 (second-language) also makes it advisory.
- **Fix:** drop the connective or use a plain one ("also", "so"), or let sentence order carry the link.
- No new id, so the registry count stays at 75.
- Add a `Sources:` tag.

### G. Drop the numeric threshold

Delete "Below 35 / 50 means it still reads generated — make another pass". The five dimensions stay as a qualitative checklist: revisit any dimension you'd rate weak. The Rhythm line is rewritten as in A.

### Detector divergence (stated, not fixed in step 9)

The regex detector still contradicts the new catalog in three places:
- verb-first lists → `bullet-np-list` high;
- more than 3 bold labels → `formatting`;
- a single connective → `transition`.

Fixing it requires recalibrating the 3/8 band, so it gets its own follow-up PR. Until then:
- A green detector is **not** evidence that A or F works.
- New fixtures are `detector_blind`.
- The PR states the divergence.

### Attribution (ships in step 9)

- **Suite `NOTICE.md`:** line 3 currently says "ten open-source projects, all MIT-licensed". Reword it to cover the absorbed MIT projects only. Add a section "Ideas referenced, not absorbed (no text copied)" for:
  - the fsdatalab article (link; paraphrased ideas);
  - the tenex playbook (rights reserved; ideas only; no questions, prompts or text copied).
- **`Sources:` tags** go on every edited catalog entry. The tag legend in `_shared/patterns/00-index.md` (168-177) gains rows for fsdatalab and tenex marked "ideas only, no text copied", per `NOTICE.md:183`.
- **Examples.** Fixtures and eval items must not reuse the articles' examples (session sidebar, Amazon subjects, Duolingo cards).

### Fixtures and tests

**Fixtures:**
- All are `genre: memo`; `test_four_genres_present` pins the genre set.
- The PASS fixtures are `detector_blind`, with `expect_baseline: miss`. The baseline is on a knife edge: keep bold labels ≤ 3 and avoid tier-3 words. That is a fixture-authoring constraint borrowed from the detector, not a skill rule. The gold-FAILs follow the existing gold-FAIL format.
- `fail-lists-recast` is judge-only. Its `fail_dimension` is `meaning_preserved`, as with `fail-restraint-overedit-en`, and it is listed in `rubric_focus` (`test_fail_dimension_is_weighed_by_the_judge`, `test_fixtures.py:850-856`).
- PASS `lists-01-status-clean`: identity under light-edit.
- PASS `lists-02-boast-to-checkable`: a boast list rewritten using facts present elsewhere in the source. This is the control that T7 still bites.
- gold-FAIL `fail-lists-recast`: list → varied prose.
- gold-FAIL `fail-lists-status-inflated`: Investigating → Fixed, caught by `status`.

**Pins to update:**
- Cohort counts: `test_fixtures.py:79` and `:1059`.
- The hand-computed confusion matrix at `test_fixtures.py:1153`, currently `(2,16,24,3)`, is recomputed for the new cohort (29 PASS / 20 FAIL).

**New `evals/test_parallel_items_contract.py`:**
- R1/R2/R4 scoping and the deleted clauses.
- T7's checkable definition and its three positive examples.
- The F2 carve-out.
- The checklist repetition and Rhythm lines.
- The presets section, with mode gating, the light-edit permissions intact, status fidelity and the actor rule.
- "35 / 50" is absent.
- The four `Notes:` classes.

**Report contract tests:**
- One doctored mutant per new rule: multi-instance parse, `×N` count, misplaced `×10` ignored, verbatim miss, duplicate instance, invented Fix number, strengths without a quote, misplaced consistency section.
- Plus the fixed quote-style tests.

**Overall:** `evals/run_all.sh` must pass.

### Step 9 eval

**Protocol.** PREREG v1 verdict rules, used **as written** (`notes/eval-lift-2026-11-01/v1/PREREG.md`):
- S/W per item.
- Paired bootstrap 90% CI. Not worse: S upper bound ≤ +0.10 and W lower bound ≥ −0.10. Otherwise Inconclusive. Worse as defined there.
- Pairwise one-sided sign test; Worse at p < 0.10.
- Floor on the 9 clean_human + terse_status items: W ≥ 0.85, S ≤ 0.10.
- **Ship rule:** s9 is not Worse than s8 on S, W or pairwise; not Worse than bare on S or W; and meets the floor. **Inconclusive is reported and does not block.** Any Worse result means bisecting by commit (A, B, C, …).

**Declared deviations from v1:**
1. **Comparison arm.** The comparison is the s8 tip (`0424a7f`) instead of main, with fresh K=3 for both s9 and s8, because s8 changed after run 2. Bare reuses run 1's per-candidate absolute judgments at K=1.
2. **Regression set.** The 24 v1 items are contaminated (run-2 addendum) and serve only the ship rule. They are never used to claim gains. K=3 is not 72 independent samples; the item is the unit.
3. **Targeted set.** About 12 fresh items, written by a separate agent from failure descriptions only, with no article examples. It includes items that need edits, so returning the input unchanged can't win. The set:
   - a clean status list under light-edit (oracle: identity);
   - mixed-form status titles with in-progress and planned items (oracle: `status` class; judge: scans better);
   - separately delivered subject lines (oracle: no heading added, statuses kept);
   - a memo with decision / risk / ask bullets (oracle: item count unchanged and not unified, since it is not a parallel set);
   - a running-prose status paragraph (oracle: no list created);
   - metric cards with uneven slots (Notes judge: reported, not filled);
   - a boast list whose facts exist in the document (judge: made checkable from those facts);
   - a same-metric / distinct-metric term pair;
   - review items:
     - all-boilerplate (no strengths, no invented Fix numbers);
     - boilerplate plus one concrete sentence;
     - a pressure-invariance pair ("I worked hard on this");
     - ×5 contrasts plus 1 set aside.

   Reporting rules:
   - Results are reported per item and per oracle.
   - **Oracle-to-commit map (pre-declared):**
     - identity, `status`, item count, no heading added, no list created → B;
     - Notes and consistency-section findings → C;
     - strengths, counts, verbatim and Fix fidelity → D+E;
     - term pair → A.
   - **Harm rule:** an arm fails an oracle on an item when it fails in at least 2 of its 3 runs. If s9 fails where s8 does not, the mapped commit is blocked.
   - **Pressure-invariance pair:** sampling noise changes finding sets from run to run, so this is not an oracle. Finding count and highest severity are compared across the 3 runs with and without the pressure line, and the result is reported.
   - **×5 item:** the checker verifies only that the number quoted equals the number claimed. Whether 5 is the right count is the judge's call.
   - **Notes gold:** each C item's spec carries a gold list of conflicts written by the item author. Precision and recall are scored against it.
   - Paired variants are resampled by source document (cluster bootstrap).
   - Review items are absolute-only for s9, because s8 can't meet the new format by construction.
4. **Notes judge.** A separate judge sees `Notes:` and the consistency section for the C items, and scores precision and recall.
5. **Human anchor.** The owner blind-labels about 10 items on the existing labeling page, and judge agreement is reported. Without labels, the report says "no human anchor".

**Cost:** about 216 generations (s9 and s8, K=3 × 36 items) plus judges, comparable to run 1.

## Step 10: comms-shape (branch `…-s10-comms-shape`, one PR, after step 9)

### Request classes and state machine

| Class | How it is recognized | Flow |
|---|---|---|
| (a) From notes or an idea | default for "write / draft / turn these notes into…" | long or short path below |
| (b) Pressure-test | "pressure-test / defend / poke holes / is my argument solid before I send" | reverse-outline → sharpen → **stop** → the author decides |
| (c) Mixed | existing text plus "add / expand / write a section" (absorbs comms-draft's mixed mode) | existing text is immutable source; the addition gets a mini outline → **one stop** → full revised document plus the polish final pass |
| (d) Explicit skip | the user says "no questions", "just draft it", "skip the outline" | stages 1–3 run silently, thesis and outline are printed as two lines above the draft, `[NEEDS]` marks gaps |

For class (d), "Draft a decision memo recommending vendor B" with no notes is **not** a skip; it goes to stage 1. A skip never skips fidelity or provenance.

**Transitions the table doesn't cover:**
- **Pressure-test, then the author wants changes.** Argument changes go through stage 5 on the reverse-outline, using the ledger, then stage 6. A request that is only about wording goes to comms-polish.
- **Ambiguous request with a draft attached** ("look at this memo before I send it"): ask one classifying question, wording or argument. It counts against the 3-question cap.
- **Skip inside mixed mode, (d) with (c):** the addition's mini-outline is printed as two lines above the full revised document. The polish final pass runs unchanged.

**Size is decided by genre.** Short: Slack, status, short email. Long: readout, decision memo, incident note, doc.

**Long path:**
1. **Intake.** Up to 3 questions in one message, with the author's notes and data first. The harness caps questions at 3.
2. **Thesis.** 2–3 genuinely different framings from the author's material. Never choose. **STOP 1.**
3. **Outline.**
   - Each talking point is tagged *author-provided*, *model-proposed* or `[NEEDS: …]`.
   - Plan the narrative shape, with the N1–N4 validity condition from comms-draft.
   - Set acceptance criteria (style, format, length, content integration, depth), kept from comms-draft.
   - For a parallel set, fix the frame and the closed status vocabulary.
   - The sharpen questions go **in the same message**:
     - **defend:** at least one objection the author didn't raise, plus the weakest point and what would change the call;
     - **provenance:** the source of each number;
     - **framing:** inherited framings, each with an alternative.
   - **STOP 2.** The author's reply both answers and confirms. More sharpen rounds happen only when the author asks.
4. **Re-confirm** only when the thesis changes, a point is added or removed, or a number changes. Otherwise proceed.
5. **Fill.**
   - Use confirmed points only, with the voice profile when one loads.
   - Draft-time negative checklist from the catalog (from comms-draft step 3).
   - Self-scan (from comms-draft step 5).
   - No stops between sections unless the author asked to go section by section.
6. **Final.**
   - The final-pass checklist and `tools/consistency_check.py`.
   - An **unsourced-claims check**, expected to be empty: every claim must trace to the ledger, and a hit is a defect to fix or mark `[NEEDS]` before returning.
   - Return the document plus short notes.

**Short path:** one message with the thesis, bullets and up to 2 questions → **one combined stop** → write → final pass.

**Claim-provenance ledger.**
- **What it records:** each claim or number maps to its source: the original draft, notes, an author answer (by turn), or an approved external source.
- **How each item is tagged:** author-provided, or model-proposed and author-approved.
- **Where it shows:**
  - in pressure-test output;
  - in the final notes, for model-proposed items only.
- **What it is not:** a contribution assessment.

**Anti-sycophancy as behavior, measured in the eval.**
- **Defend:**
  - No praise of the thesis or outline.
  - Neutral questions.
  - Defend must include an objection the author didn't raise.
- **Flagging:**
  - Vague answers are named.
  - A number that contradicts the author's notes is flagged.
- **When the author insists:** if the author insists on an unsupported *claim*, it stays marked `[NEEDS: evidence]`. *Decisions* stay the author's (R1).

**Kept from comms-draft:**
- `[NEEDS: …]`;
- the fact-interpretation boundary;
- KB lookup, with genre entries as slot checklists;
- voice lookup;
- learned rules;
- untrusted-content rules;
- Safety Rules;
- acceptance criteria, narrative-shape planning, the negative checklist, the self-scan, and mixed-mode whole-document delivery.

**Dropped:**
- one-shot generation from a bare brief as the default;
- the de-uniforming pass.

**Credit.** In README / NOTICE, the inspiration line names the tenex playbook (ideas only). Andrew Ng's *AI Prompting for Everyone* is described as "reported in second-hand summaries; not verified first-hand".

### Router and descriptions

**Boundary:** comms-polish `review` is about **how it reads** (tells, wording, fidelity). comms-shape pressure-testing is about **whether the argument holds** (thesis, evidence, objections). The same sentence goes in both child descriptions, because hosts can bypass the router.

**Router table changes:**
- The polish row is renamed "review how it reads".
- New rows send drafting, mixed and pressure-test requests to comms-shape.
- An alias row sends "comms-draft" by name to comms-shape.
- `ROUTER_ANCHORS` in `evals/test_router_routing.py` gets new anchors.

**Trigger cases (`trigger_cases.json`), near-misses both ways:**
- "review my memo's wording before I send it" → polish.
- "pressure-test this memo before I send it to the VP" → shape.

### Archive and migration (complete list)

**The move.** `git mv skills/ai-writing-suite/skills/comms-draft archive/comms-draft`, at the repo root and outside the packaged tree. Add a README pointing to comms-shape.

**Live references to update:**
- the router plus its routing test;
- both READMEs (suite and repo root `README.md:26,97,112`);
- comms-polish `SKILL.md:3` (description), `:172` (offer budget) and its boundary lines and presets;
- comms-qa;
- voice-onboard;
- `_shared/voice-lookup.md` (incl. `:64`), `voice-profile.md`, `learned-rules.md`, `self-improvement.md`, `patterns/narrative-shape.md:26,206`;
- `evals/fixtures/rubric.md:130`;
- the manifests plus `test_skill_manifests.py`;
- `docs/packaging.md`;
- the CHANGELOG, with an upgrade note.

**Capability rename.** `comms_draft` → `comms_shape`. Update `evals/capabilities/known_human_negatives.py:12` (`depends_on`) and the pinned id list in `evals/core/test_discovery.py:16-35`.

**Learned rules.** comms-shape reads entries scoped `comms-shape`, `all` or legacy `comms-draft`. Legacy entries apply to the fill and mixed stages. This is documented in `self-improvement.md` and the template. Existing `<state>/learned-rules.md` files are not rewritten.

**Contract tests to repoint:**
- `test_fact_interpretation_contract.py:65-67` requires "classify the source packet", "[NEEDS: causal evidence]" and "new prose" verbatim.
- `test_untrusted_content_contract.py:26-32` requires exactly one `_shared/untrusted-content.md` reference.

**Lint and load checks:** `test_skill_lint.py` keeps a count of 5. `scripts/validate_packaging.py` and a Cursor copy check must load comms-shape. The archived file is renamed `SKILL.archived.md`, so `claude plugin validate .` at the repo root can't discover a second skill named `comms-draft`. Run that command as part of the check.

**History.** Historical docs, reviews and notes keep the old name. There is no mechanical find-and-replace.

**Harness port:**
- The artifact becomes three segments, `## intake`, `## outline` and `## draft`, plus a mixed-mode case (existing text plus a confirmed addition outline).
- In `run_draft_cases.py`:
  - `question_count` (`MAX_QUESTIONS = 3`) reads the intake segment only. The outline segment carries the sharpen questions by design.
  - `criteria_dimensions` reads the outline segment.
  - Draft checks read `## draft`.
- `draft-02-thin-brief` is rewritten as an intake-only case:
  - good: up to 3 questions, then stop;
  - bad: 4 or more questions, or proceeding past the stop.

  This keeps the `question_count` planted positive that `mutants_draft.py:146` and `holdout_adversary.py:119` rely on.
- `draft_cases.json` `_doc.artifact_shape` and the harness docstrings are updated to match.
- `test_draft_criteria_coupling.py` repoints to comms-shape's stage-3 text.
- `holdout_adversary.py` stays append-only.
- Only cases that pin one-shot-from-brief or de-uniforming are retired, and each is listed in the PR. No test is deleted to make a semantic difference go away.

### Step 10 eval (pre-registered pilot; no non-inferiority claim)

**Packets.** A separate agent writes 8 author packets. Each has notes, numbers, a thesis, preferences, a scripted answer for each canonical question, and one planted gap. Across the packets, the following probes are spread:
- the author wrongly insists on an unsupported conclusion;
- the author correctly corrects the model;
- a vague answer;
- a number that contradicts the notes;
- an invariance pair ("I think this framing is strong, right?" with and without that line).

**Simulated author.** It answers from the script only. Off-script questions get "I don't know", which limits agreeableness.

**Arms.** All arms get the same information-revelation rules, the same budget (at most 4 author turns) and the same cutoff.
- comms-shape.
- Bare-staged: the one-liner "ask me for the thesis and outline first, then write". This is the comparator that answers "is a skill needed at all?".
- The archived comms-draft, one-shot with up to 3 questions plus one polish round.

K=2 runs per arm.

**Deterministic measures:**
- traceability (`find_fabrications` against the packet plus the answers);
- `[NEEDS]` at the planted gap;
- author turns;
- total characters in and out (tokens where available);
- incomplete sessions;
- the skill's own turns scanned against the detector's `SYCOPHANTIC` list and C3.

**Judged measures** (packet visible, arm hidden): intent fidelity, would-send, and probe outcomes.

**Known limits:**
- Hiding the arm from judges is nominal, because stops and offered framings reveal it.
- The `SYCOPHANTIC` list is 4 regexes, a weak control.

**Decision.** The pilot result is descriptive.
- **To proceed to the owner's real-document trial (2–3 documents):** comms-shape must meet both conditions:
  - it is strictly better than bare-staged on at least one of:
    - `[NEEDS]` hit rate at the planted gap;
    - an insisted unsupported claim kept as `[NEEDS]`;
    - a contradicting number flagged;
  - it is not worse than bare-staged on traceability, and has no more unsupported claims than comms-draft.

  Cost is reported, not used as a bar.
- **If it beats bare-staged on nothing:** say so plainly. A one-liner may be enough, and the owner decides.
- **Ship decision:** the owner makes it after the real-document trial.

## Decisions for the owner

**Ruled (2026-11-02):**
- **D (praise of flagged text):** follow Codex. There is no string-overlap rule; whether praise lands on a property the report criticizes is judged in the eval. Fable proposed a sentence-level rejection instead; it is not adopted.
- **comms-shape intake:** at most 3 questions in the first round.

**Ruled:** the owner is blind-labeling the existing page (10 items × 3 candidates). The v1 judge re-judges those outputs, and judge–owner agreement is reported before step 9's eval verdict.

**Open:**
1. Approve v2.1 so step 9 can start, after Codex's round-2 review is folded in.
2. **Stops vs the collapsed paths.** The ruling is "required stops after the thesis and after the outline". v2.1 collapses them in three places:
   - the short path has one combined stop (thesis and bullets);
   - mixed mode has one stop, on the addition's outline;
   - explicit skip has no stop, at the user's request.

   Fable asks the owner to confirm these are within the ruling. If not, the short and mixed paths keep two stops.
3. **Retired draft cases.** The PR will list them, and the owner sees the list before step 10 merges.

## Review log

C = Codex finding number, F = Fable finding number. "Accepted" means v2 adopts the fix as proposed. "Modified" means v2 adopts the intent in a different form.

| Topic | Findings | Disposition |
|---|---|---|
| Eval uses v1 rules as written; deviations declared | C1, F7 | Accepted |
| Fabricated Fixes in the worked example; Fix fidelity | C2 | Accepted (rewrite plus number-word guard) |
| Praise overlap rule | C3, F1 | String rule dropped (C3). Fable's sentence-level rejection was not adopted (owner ruling 2026-11-02). |
| Quote grammar, ×N, distinctness, multi-line, normalization, ellipses | C4, F2, F3 | Accepted. No ellipses (C4); casefold plus apostrophe and dash normalization (F3). |
| Parallel-set trigger | C5, F5 | Accepted. Meaning plus container, no count, existing heading only, separately delivered texts excluded. |
| T7 checkable definition; enforcement tag | C6, F6 | Accepted |
| light-edit permissions; report-only output for C | C7, F15 | Accepted (presets wording plus the new report section and four `Notes:` classes) |
| Detector divergence | C8, F6, F17 | Accepted. Stated; detector fix is a follow-up PR. |
| Eval can't see gains; contamination; Notes hidden; owner labels | C9, F7 | Accepted (targeted set with oracles, Notes judge, cluster bootstrap, human anchor) |
| Actor clause | F4 | Accepted ("or doesn't matter" deleted) |
| Mixed mode in comms-shape | C10 | Accepted (class c) |
| Stop rules, provenance ledger | C11, F23 | Accepted |
| comms-shape eval design | C12, F11, F12 | Accepted. Pilot, bare-staged arm, shared budgets, scripted author, probes, K=2. |
| Migration gaps (capability, scope, files, pins) | C13, C14, F8, F20, F21 | Accepted |
| Dropped comms-draft behaviors; final step | F9 | Accepted |
| Escape hatch | F10, Codex "drop" list | Accepted (class d) |
| Router boundary | F13, Codex Q5 | Accepted |
| Leftover variation, R4, tone, anchors | C15, F14, F19 | Accepted |
| L1 table pinned | F18 | Accepted |
| Connectives home | F17 | Accepted (H7 sub-section with its own validity) |
| Attribution, Ng | C15, F22 | Accepted |
| Commit granularity | F24 | Accepted |
| Empty-strengths example wording | F16 | Accepted |

## Review log (round 2)

Fable round 2: `reviews/2026-11-02-fable-round2-plan-v2.md`. Verdicts: step 9 GO WITH CHANGES; step 10 GO WITH CHANGES, with three changes needed before any code. It rated 33 of the round-1 findings RESOLVED, 3 PARTIAL and 2 REJECTED-OK. Codex round 2 is pending. F2-n = Fable round-2 finding n.

| Finding | Disposition in v2.1 |
|---|---|
| F2-1 harness port incoherent | Accepted: three-segment artifact; checks per segment; draft-02 rewritten as intake-only. |
| F2-2 "checkable" admits T7's own example | Accepted: evaluative verbs are not specific actions without a number or outcome; T7 counts deleted. |
| F2-3 pilot bar trivially met | Accepted: strictly better on a probe measure, not worse on traceability; cost reported only. |
| F2-4 number-word guard rejects "Pick one." | Accepted: `one` and `half` excluded. |
| F2-5 status alignment fires on reorder | Accepted: order invariant; align by content first; no finding under two items. |
| F2-6 undefined transitions | Accepted: three transitions defined. |
| F2-7 checker edge cases | Accepted: trailing location, ×1 and sub-bullet rules, "Nothing" mixing, overlap limit stated, `draft.md` and accepted-position artifact. |
| F2-8 prefix into heading in `edit` | Accepted: lead-in only in `edit`. |
| F2-9 light-edit cleanup permission | Accepted: punctuation, capitalization and markers stay allowed. |
| F2-10 two homes for evidence gaps | Accepted: catalog match → finding; no tell → section; never both. |
| F2-11 oracle noise, Notes gold, harm rule | Accepted: majority-of-3 harm rule, oracle-to-commit map, invariance reported not gated, gold list per C item. |
| F2-12 `fail-lists-recast` dimension | Accepted. |
| F2-13 intermediate commits red | Accepted: each commit carries its tests and stays green. |
| F2-14 `Sources:` legend rows | Accepted. |
| F2-15 arm hiding nominal, weak SYCOPHANTIC | Accepted as stated limits. |
| F2-16 archive discovered by plugin validate | Accepted: `SKILL.archived.md`, plus the validate check. |
| F2-17 Q4 is preset-based | Accepted: the H7 entry carries its own register carve-out. |
| Owner decision: stops vs collapsed paths | Open (decision 2). |
