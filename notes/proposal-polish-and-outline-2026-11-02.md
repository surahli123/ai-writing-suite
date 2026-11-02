# Proposal: comms-polish step 9 and an outline-first replacement for comms-draft

Date: 2026-11-02. Status: **proposal for owner approval; nothing here is implemented.**

## Inputs

- **fsdatalab:** Shreya Shankar, "Five Principles for Generating Readable AI Text in Bulk" (2026-10-29). The owner pasted the text because the host is blocked here.
- **tenex:** "Stay Slop-Free: say yes to these 8 questions", from the `slop-free-check` SKILL.md in the owner's zip. It has no license, so this proposal borrows ideas only and copies no wording.
- **Andrew Ng:** *AI Prompting for Everyone* (DeepLearning.AI / Coursera, 2026), "Thought Partner" module. I know it only from second-hand summaries, because both hosts are blocked here. Per those summaries, the course teaches staged writing (outline, then bullets, then text), says changes at the outline stage matter most, and covers guarding against sycophancy.
- **Gap reviews:** two read-only reviews by subagents compared the s8 tip (`0424a7f`) with each source. I re-checked every claim this proposal rests on; those are marked ✔.

## 1. What the sources show about comms-polish

### 1a. The catalog treats a well-formed list as an AI tell (fsdatalab)

The article's main value to us is a scope correction. In parallel items (status lists, feeds, card sets, titles), using the same structure and the same words in every item is what makes a list quick to read. The suite pushes the other way in four places:

- **T7 ✔** says "the tell is the *symmetry*", and its first fix is "convert to prose". The detector's `_detect_bullet_np` counts any item without an auxiliary verb as a noun phrase. In a probe, six verb-first status bullets ("Fixing login redirect loop", "Debugging flaky checkout test", ...) were flagged `bullet-np-list` at **high** severity.
- **Bold labels ✔.** Five consistent bold status labels (`**Shipped:**`, `**Blocked:**`, ...) were flagged as a formatting tell. F2 and T6 point the same way.
- **Rhythm and repetition.** The workflow and the final pass treat uniform rhythm as something to fix ("Vary rhythm", "sentence lengths vary", "Repetition is gone"). Those lines are written for running prose but don't say so. R1 already says rhythm is never a rewrite target, so the suite is also inconsistent with itself here.
- **Synonym swaps.** R4 ("choose the second or third word") and the L1 swap table (2–3 replacements per word) can give the same concept a different word in each item. L3 says to do the opposite.

DS status updates are mostly lists. Light-edit is safe because it keeps every sentence. Rewrite and review can "fix" a list that was already good.

### 1b. The review report has a flattery hole (tenex)

- **Self-contradicting example ✔.** The canonical example report praises "The dashboard is fast" under *What already reads well*, while the same report flags "fast, clean, and intuitive" as T1.
- **Pressure to praise.** The checker only requires that section to be non-empty, which pushes the reviewer to find something to praise.
- **No counts.** Each finding carries one quote and says nothing about how often the pattern recurs, although the catalog says frequency is what matters.
- **No quote check.** Nothing verifies that a quote actually appears in the draft.
- **Catalog gap ✔.** Moreover, Furthermore, Additionally and In conclusion are detector patterns but are missing from the model-facing catalog.

### 1c. What polish should not take from tenex

The process questions (did you understand it, check it, decide it, contribute something?) only work if the author answers them. They don't belong in an editor. They are the core of the drafting replacement in section 3.

## 2. comms-polish step 9 (one PR)

| # | Change | Source | Modes | Risk to rewrite |
|---|---|---|---|---|
| A | Scope carve-outs for parallel items | fsdatalab | all | low |
| B | Rules for parallel lists (unnumbered preset section) | fsdatalab | rewrite full; light-edit mechanical only; review flags | medium |
| C | Sibling-consistency findings, report only | fsdatalab | `Notes:` and review | low |
| D | Honest strengths section, plus a checker rule | tenex | detect / review | none |
| E | Count and quote repeated patterns; quotes must be verbatim | tenex | detect / review | none |
| F | Connective adverbs in the catalog, cluster-only | tenex | all, advisory | low–medium |
| G | Drop the "below 35/50, make another pass" threshold | pre-existing | final pass | low |

**A. Scope carve-outs.**
- **Rhythm.** In R1/R2 and the SKILL rhythm lines, add "in running prose". Items of one parallel list are not rhythm units.
- **Final-pass checklist.** Repeated *content* is still cut. Repeated *structure and terms* across parallel items stay. The "Rhythm" scoring dimension applies to prose only.
- **T7.** The tell becomes emptiness (nothing checkable in the item), not symmetry. Status lists, feeds and card sets with checkable content are exempt, and "convert to prose" is no longer their default fix.
- **Formatting entries.** In T6 and F2, a consistent bold label on each item of a scan list is structure, not erratic bolding. The genre-normal lists in T9 and T13 gain feeds, titles and list items.
- **Word choice.** The L1 table and R4 move to one replacement per concept, and recurring terms are exempt. `tone.md`'s "vary sentence length" is scoped to prose.

**B. Parallel lists** (three or more siblings that a reader skims as a set).
- **Structure.**
  - Use one frame for every item.
  - Put the differentiating word first.
  - Move a shared prefix into the heading.
- **Meaning.**
  - Tense and status follow the author: done stays done, and "investigating" never becomes "fixed". If an item's status can't be told, flag it.
  - Verb-first or active voice beats "X done by Y" only when the actor is already stated or doesn't matter. Never invent an actor, and keep blameless system-as-subject phrasing.
  - The author's status vocabulary stays closed and consistent.
- **Leave alone:** mixed lists, numbered procedures, timelines, quotes and tables.
- **Mode gating.**
  - light-edit fixes punctuation and typos only. It may unify a term only when the draft itself shows one thing called by two names.
  - rewrite applies the full set.
  - review and detect flag only.
- **Not taken from the article.**
  - Dropping detail to make cards uniform: that deletes facts.
  - Swapping in strongly emotional verbs ("love", "complain"): that adds a claim.

**C. Sibling consistency (report only).** This extends step 5's "the document agrees with itself" check.
- **What it reports.** When parallel items carry metrics, it reports which items have n, an interval, a baseline or a unit and which don't. It also flags one metric or status that goes by two names.
- **What it never does.** It never fills a missing slot and never deletes the extra one.
- **When it fires.** At least two siblings share a slot pattern and at least one lacks it.

**D. Honest strengths.**
- **What counts as a strength.** It is a quoted passage plus a reason that fits only that passage. Praise for tone, effort, topic or general structure is not allowed.
- **No double-dipping.** A sentence quoted in any finding cannot also be praised.
- **Empty is allowed.** "Nothing reads well yet" is better than a stretch.
- **Fix the examples.** Correct the canonical example and `conforming.md`. `check_report.py` rejects any overlap between strength quotes and finding quotes.

**E. Counting.**
- **Instances.** When a pattern repeats, the Quote line carries each instance: up to about five, then the clearest few plus their locations.
- **Count and set-asides.** Why gives "×N" and how many instances were set aside: evidence-answered contrasts (ruling R2), documented author habits, and text inside quotes or code.
- **Counts describe.** They never become quotas or rewrite targets.
- **Verbatim check.** `check_report.py` gains an optional draft argument and rejects any quote that is not a verbatim substring of the draft. That also catches hallucinated quotes.

**F. Connectives.** Add them to H7 as cluster-only: several sentence openers within one passage, never a single occurrence. Carve out formal register and second-language writers. The known-human negatives must stay clean.

**G. Threshold.** The final pass's optional scoring ends with "Below 35 / 50 means it still reads generated — make another pass". That is a numeric gate of the kind the owner has rejected. Keep the five dimensions as a qualitative checklist and drop the threshold.

### Deferred

- **New catalog ids for list defects (T14/T15).** First the owner has to decide whether readability defects count toward the AI-pattern score; I'd say no. This can follow once B proves useful.
- **Detector fix** (`_detect_bullet_np` skipping verb-first items). This needs the 3/8 calibration band redone, so it gets its own PR. Until then the new fixtures are `detector_blind`.
- **"Could be X% shorter".** It can be computed from the quoted sentences, and nothing would branch on it, but it is still a number in the report. Deferred unless the owner wants it.
- **Voice-fit finding against the loaded profile.** This belongs first in the replacement skill's pre-send check.
- **Lead-vs-body sentiment alignment** (fsdatalab principle 5). It risks adding sentiment, and flag-only coverage already exists through the lead-promise line.

### Eval for step 9 (pre-registered v1 protocol)

**Arms:** s9 vs the s8 tip vs main vs bare.

**Held-out items**, written by a separate agent from failure descriptions only:
- *List items:*
  - a clean verb-first status list under light-edit, which must come back unchanged;
  - mixed-form titles with "investigating" and "planned" statuses, where the frame is unified and the statuses are kept;
  - subject lines with a shared prefix;
  - a running-prose control, which must not be made parallel;
  - metric cards with uneven slots, reported and not filled;
  - a same-metric term pair next to a distinct-metric pair.
- *Review items:*
  - an all-boilerplate draft (no strengths);
  - boilerplate plus one concrete sentence (that sentence is the only strength);
  - the same draft with an "I worked hard on this" line, where findings must not change;
  - five evidence-free contrasts plus one evidence-answered contrast (count 5, 1 set aside).
- *Regression:* the existing 24 v1 items.

**Gate:** NOT WORSE than the s8 tip and bare on severe changes and would-send. Review items are scored by `check_report.py` (deterministic) and by the judges. `run_all.sh` must pass.

## 3. Replacing comms-draft: outline first

### Why

- **Generic first drafts.** A first draft built from a playbook plus a prompt comes out generic. Polish then removes surface tells but cannot make the content the author's. Rounds 1–2 of the research and eval v0 both point this way.
- **Token cost.** Each polish loop re-reads the whole draft. Iterating on the outline costs a few dozen lines per round.
- **Ng (second-hand).** Outline, then bullets, then text. The cheapest and most effective changes happen at the outline.
- **tenex.** Slop is AI substituting for work the reader expects from the author. The process questions are best asked *while* the piece is built, not after it is finished.

### Proposed skill (working name `comms-outline`)

| Stage | What happens | Borrowed from |
|---|---|---|
| 0. Size the job | Short pieces (Slack update, status, short email): thesis plus bullets in one turn, the author confirms, then write. Long pieces (readout, decision memo, incident note): the full flow. | — |
| 1. Intake | Who reads it, and what decision or action is wanted. Ask for the author's notes and data first. Up to 5 questions, in one message. | Ng: context |
| 2. Thesis | One sentence. Offer 2–3 genuinely different framings drawn from the author's material. Never pick one. | tenex Q3 |
| 3. Outline and talking points | Each point ties to a piece of the author's material or is marked `[NEEDS: ...]`. KB and playbook genre entries are slot checklists here (baseline, unit, interval, n, window...), not text generators. For list artifacts, fix the item frame and the status vocabulary now. | Ng; fsdatalab |
| 4. Sharpen (outline only, repeat) | **Defend:** weakest point, strongest objection, what would change the call. The author answers; the skill points out vagueness. **Provenance:** for each number, which query, dashboard or run it came from. The skill never rules on truth. **Framing:** name inherited or stock framings and give an alternative. **Anti-sycophancy:** neutral questions, no praise of the outline, push back with evidence. Stop when the author says so. | tenex Q1–Q3; Ng: sycophancy |
| 5. Fill | Section by section for long pieces, all at once for short ones. Use only confirmed points and add no new claims. Use the voice profile if one is loaded. The author may write a section and ask for light-edit. | Ng |
| 6. Pre-send | **Contribution diff:** list claims in the final that trace to nothing in the author's notes, for the author to account for. Then comms-polish review and the consistency check. | tenex Q8 (notes diff) |

- **Second entry point: "pressure-test my draft".** The author brings a finished draft. The skill reverse-outlines it into the thesis and points it actually makes, then runs stages 4 and 6. This covers tenex's pre-ship use without adding a sixth skill.
- **Escape hatch.** For "just write it", the skill writes it, then ends with a short list of the skipped steps and the `[NEEDS]` gaps. It never refuses.
- **Required stops:** after the thesis and after the outline. Other stages proceed unless the author asks to slow down.
- **Carries over from comms-draft:** `[NEEDS: ...]` markers, the fact-interpretation boundary, KB lookup, voice lookup and the untrusted-content rules.
- **Dropped from comms-draft:** one-shot full-draft generation as the default, and the "deliberate de-uniforming pass", which conflicts with R1 and with item A above.

### Archive and touch points

Move `skills/comms-draft/` to `archive/comms-draft/`, outside the packaged tree, with a README pointing to the replacement. About 25 live files name comms-draft:

- **Router and skills:**
  - the router plus `test_router_routing`;
  - comms-polish (boundary lines and presets);
  - comms-qa;
  - voice-onboard.
- **`_shared` files:**
  - `voice-lookup`, `voice-profile`;
  - `learned-rules`, `self-improvement`;
  - `narrative-shape`.
- **Docs and tests:**
  - README;
  - the manifests plus `test_skill_manifests`;
  - `trigger_cases.json` and the skill lint;
  - the fact-interpretation and untrusted-content contract tests.
- **Draft eval harness:**
  - `capabilities/comms_draft.py`;
  - `draft_cases.json`, `mutants_draft.py`, `run_draft_cases.py`, `test_draft_cases.py`;
  - the criteria-coupling test, `rubric.md` and `holdout_adversary.py`.

  These test fill-stage behavior (`[NEEDS]`, no fabrication) and get ported to stage 5.

The router's "polish this and add a risks section" case moves to the new skill, which asks for the author's risks instead of writing some.

### Eval for the new skill

The question differs from polish: is the result more the author's, and is it cheaper to get there?

- **Author packets.** A separate agent writes about 10 packets with hidden intent: the real thesis, notes and numbers, two preferences, and one point only the author knows. A simulated-author agent answers the skill's questions from its packet only.
- **Arms:**
  - the new skill;
  - comms-draft one-shot followed by up to N polish rounds;
  - bare.
- **Measures,** scored by judges who see the packet but not the arm:
  - **Intent:** does the final make the author's thesis and points?
  - **Traceability:** what share of claims trace to the packet, and which trace to nothing?
  - **Gaps and fabrication:** count unsupported claims, and check that `[NEEDS]` is used where material is missing.
  - **Would-send.**
  - **Cost:** total tokens, and author turns to reach the final.
- **Known bias.** A simulated author tends to agree. To check that the skill doesn't steamroll the author, each packet plants one disagreement: the author rejects the first framing.
- **Human anchor.** The owner runs the skill on 2–3 real documents.

## 4. Decisions for the owner

1. Which of A–G go into step 9.
2. One skill with two entry points (recommended), or a separate ship-check skill.
3. The new skill's name.
4. Required stops: after the thesis and the outline only (recommended), or after every stage.
5. Attribution:
   - tenex has no license, so credit it as inspiration with no text copied;
   - credit Ng's course as inspiration;
   - fsdatalab's ideas are paraphrased with a link.
