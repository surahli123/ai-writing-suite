# Implementation plan: comms-polish step 9 and comms-shape (step 10)

Date: 2026-11-02. Status: **plan, under external review; no skill file changed yet.**
Base: s8 tip `0424a7f` (branch `claude/laughing-rubin-mkkadx-s8-descriptions-lint`).
Background and evidence: `notes/proposal-polish-and-outline-2026-11-02.md`, on the
research branch `claude/laughing-rubin-mkkadx`.

## Owner rulings (2026-11-02)

- **Step 9 scope:** all of A–G.
- **The drafting replacement:**
  - one skill, `comms-shape`, with two entry points: start from notes, or pressure-test an existing draft;
  - required stops only after the thesis and after the outline;
  - `comms-draft` is archived.
- **Earlier rulings still bind:**
  - claims, not decisions (R1 amendment);
  - evidence-answered objections are kept (R2);
  - per-step gates are replaced by the pre-registered v1 protocol (R3);
  - no numeric levers, no em-dash ban, no agent-reader framing, no manufactured personality;
  - this suite may draft and rewrite.

## Step 9: comms-polish (branch `…-s9-lists-review`, one PR)

All paths are relative to `skills/ai-writing-suite/`. Line numbers refer to the s8 tip.

### A. Parallel-item carve-outs

**Definition.** A *parallel item set* is three or more sibling items that a reader skims as a set:
- status bullets
- feed or card text
- titles and subject lines
- action items
- metric rows

Running prose is everything else.

| File | Change |
|---|---|
| `_shared/patterns/rhythm-stylometric.md` R1 (15-39) | Add a validity line: R1 concerns running prose. Items of one parallel set are not rhythm units, and one shape across them is correct. |
| same, R2 (43-51) | Replace "Vary deliberately. Some paragraphs one sentence." with prose-scoped wording that matches R1: a detection signal, never a length target. Exempt parallel sets. |
| same, R3 (55-71) | Add parallel sets to the low-TTR carve-out. A 20-item list repeats words by design. |
| same, R4 (73-86) | Recurring terms are exempt from "second or third word": one concept keeps one word. **Open:** R4 also says "make unexpected analogies", which conflicts with L7 (mannered prose, s7). Delete that clause? |
| `_shared/patterns/structural-tells.md` T5 (74-91) | The "8+ bullets in under 200 words" signal does not apply to status lists, feeds or card sets whose items carry checkable content. |
| same, T6 (93-110) | The tell stays a bold header that *repeats* the item's own words. A consistent label-first lead-in from a closed set (`**Shipped:**`, `**Blocked:**`, `**Owner:**`) is structure, not a tell. The fix no longer offers "convert to prose" for such lists. |
| same, T7 (112-125) | Reframe the tell from *symmetry* to *emptiness*: short items with nothing checkable (no action, object, number or name). Verb-first items that name a concrete action are checkable. Exempt feeds, status lists and card sets with checkable content. "Convert to prose" is no longer the first fix. |
| same, T9 (144-163) and T13 (208-225) | Add feeds, status lists and card sets to T9's swap-test exemption. Add titles, card text and list items to T13's genre-normal list ("Fixed login bug" is not over-compression). |
| `_shared/patterns/punctuation-formatting.md` F2 (29-40) | One consistent bold label per item of a parallel set is not erratic bolding. The one-per-section rule is about inline bolding in prose. |
| `_shared/patterns/lexical-tells.md` L1 table (~45-60) and L3 (119-135) | L1 table header: pick one replacement per concept and use it everywhere. L3: name cross-item consistency explicitly, and add a DS caution (users vs accounts vs sessions, holdout vs control are distinct terms). Merge only where the draft shows one referent; otherwise flag. |
| `skills/comms-polish/SKILL.md` step 5 (~242) and step 8 (~269) | "uniform sentence length" becomes "uniform sentence length in running prose". Step 8 becomes "In running prose, let rhythm follow content (R1); a parallel item set keeps one shape (see presets)". |
| `skills/comms-polish/references/final-pass-checklist.md` L2 "Repetition is gone" | Becomes "Repeated content is gone; repeated structure and terms across parallel items stay." |
| `_shared/knowledge/tone.md:18` | Scope "Vary sentence length" to running prose. Check that kb_lint, smoke and validate still pass. |

`skills/comms-draft/SKILL.md` §4 ("deliberate de-uniforming pass") also conflicts with this. It is left alone because step 10 archives the file.

### B. Parallel-list rules (rewrite)

**Where.** A new unnumbered section, "Parallel items (lists, feeds, cards, titles)", goes in `skills/comms-polish/references/scenario-presets.md` after "Data-science documents (KB-backed)". It stays unnumbered because `evals/test_scenario_presets.py` pins exactly six numbered presets. One pointer line goes in SKILL.md step 5.

**Content.**
- **Scope test:** the parallel-set definition above.
- **Rules:**
  - Every item uses one frame.
  - The word that tells an item apart from its siblings comes first.
  - A prefix shared by every item moves into the heading or lead-in.
- **Status fidelity:**
  - Tense and status follow the author. Done stays done. "Investigating" never becomes "fixed", and "planned" never becomes "shipped".
  - If an item's status can't be told, flag it.
- **Actor:**
  - Prefer verb-first or active voice over "X done by Y" only when the actor is already stated or doesn't matter.
  - Never invent an actor.
  - Keep blameless system-as-subject phrasing in incident notes.
- **Vocabulary:** the author's status labels stay a closed set, used consistently.
- **Leave alone:**
  - mixed lists
  - numbered procedures
  - chronological timelines
  - quoted text
  - tables
- **Mode gating:**
  - `light-edit`: punctuation and typos only. A term may be unified only where the draft shows one referent with two names.
  - `rewrite` and `edit`: the full set.
  - `review` and `detect`: flag only.
- **Not taken from the source article:**
  - Dropping detail to make items uniform, because it deletes facts.
  - Swapping in stronger-sentiment verbs ("love", "complain"), because it adds a claim.

**Open question:** should status fidelity also become a deterministic class in `evals/fixtures/fidelity.py` (`status`: progressive or planned in the source, completed in the output)? Proposed: yes, with one mutant and one faithful control.

### C. Sibling consistency (report only)

**Final-pass checklist.** L1 "The document agrees with itself" gains a fifth check. When parallel items carry metrics, report:
- which items carry n, interval, baseline or unit, and which lack them;
- any metric or status that goes by two names.

**Firing threshold:** at least 2 siblings share a slot pattern and at least 1 lacks it.

**Limits:** never fill a slot, never delete the extra one, never pick a winner.

**Bug fix.** SKILL.md `## Output` says the `Notes:` block holds missing-evidence flags "nothing else". Step 5 already tells the editor to report consistency conflicts "in notes". So the scope gets widened to evidence flags plus consistency conflicts. That fixes an existing contradiction.

### D. Honest strengths

**Contract** (`references/audit-report-contract.md` §3) is rewritten:
- A strength is a quoted passage plus a reason that fits only that passage.
- No praise of tone, effort, topic or general structure.
- A sentence quoted in any finding cannot be praised.
- Prefer "Nothing here reads well yet" over a stretch.
- Assume the pull is toward crediting the draft.

**Canonical example** (`references/audit-report-format.md`) and `evals/audit_report/conforming.md`:
- Today both praise "The dashboard is fast" while flagging "fast, clean, and intuitive".
- Every sentence of that example draft carries a flagged pattern, so the honest strengths line is "Nothing here reads well yet".

**Checker** (`evals/audit_report/check_report.py`):
- Every bullet under `## What already reads well` either carries a quoted snippet or starts with "Nothing".
- No strength snippet may overlap a finding's Quote snippet. Overlap means one contains the other after normalization (case, whitespace, quote style).
- Doctored-artifact tests cover both rules, and `nonconforming.md` plants the overlap.

### E. Counted findings and verbatim quotes

**Contract** (§2 of the contract file):
- When a pattern repeats, the `**Quote:**` line carries each instance as a separate quoted snippet: all of them when N ≤ 5, the clearest 3–5 when N > 5.
- `**Why:**` starts with `×N` and gives the number set aside:
  - evidence-answered contrasts (R2);
  - documented voice-profile habits;
  - text inside quotes or code.
- One `**Fix:**` shows one representative replacement.
- **Counts describe; they never become quotas or rewrite targets.**

**Checker:**
- If `**Why:**` carries `×N` (or `xN`), the Quote line must carry exactly N snippets when N ≤ 5, and 3–5 when N > 5.
- New optional argument `check_report(text, catalog_ids, draft=None)`. When `draft` is given, every Quote snippet and every strength snippet must be a substring of the draft after normalization (whitespace, quote style, case kept). Fix snippets are exempt.
- `run_report_contract.py` keeps working without a draft.
- **Open:** how should an ellipsis inside a quote be handled (split it and check each part)?

### F. Connectives (cluster-only)

- Add to H7 (`_shared/patterns/hedging-filler.md` 114-135): Moreover, Furthermore, Additionally, In conclusion, In summary.
- They count **only as a cluster**: several sentence openers in one passage, never a single use.
- Formal-register and second-language writers are carved out through the false-positive gate.
- The detector already lists these words (`evals/detector/patterns.py:183-195`), so detector behavior is unchanged.
- The known-human negatives and the FP gate eval must stay clean.
- Regenerate the projections with `python3 -m aiws.catalog`. The registry count stays 75, because no new id is added.

### G. Drop the numeric threshold

In `final-pass-checklist.md`, the optional scoring pass loses "Below 35 / 50 means it still reads generated — make another pass". The five dimensions stay as a qualitative checklist: revisit any dimension you would rate weak. No total, no threshold.

### Tests and fixtures

- **New `evals/test_parallel_items_contract.py`**, pinning:
  - the R1, R2 and T7 scoping text;
  - the F2 carve-out;
  - the checklist repetition line;
  - that the presets section exists with mode gating and status fidelity;
  - that "35 / 50" is absent;
  - the widened `Notes:` scope.
- **Report contract tests:** one doctored mutant per new rule in D and E, plus a draft-substring test with a hallucinated quote.
- **Fixtures**, all `detector_blind` so the 3/8 calibration band is untouched:
  - PASS `lists-01-status-clean` (identity, light-edit);
  - gold-FAIL `fail-lists-recast` (items merged into varied prose);
  - gold-FAIL `fail-lists-status-inflated` ("Investigating" → "Fixed"). This one is caught by the new `status` fidelity class if that is approved.
- **Cohort counts** in `test_fixtures.py` move from 27/18 to 28/20.
- **`evals/run_all.sh` must pass.**

### Behavioral eval (pre-registered v1 protocol, run before the PR is marked ready)

**Arms:** s9 vs the s8 tip (the "existing skill") vs bare. K=3 fresh runs per arm. The generation model and judges are the same as in v1 run 2.

**Held-out items** are written by a separate agent from failure descriptions only. It never sees the new rules' wording.
- *List items (6):*
  - a clean verb-first status list under light-edit, which must come back unchanged;
  - mixed-form titles with "investigating" and "planned" statuses, which must be unified with statuses kept;
  - subject lines that share a prefix;
  - a running-prose status paragraph, which must not be made parallel;
  - metric cards with uneven slots, which must be reported and not filled;
  - one same-metric term pair and one distinct-metric pair.
- *Review items (4):*
  - an all-boilerplate draft, with no strengths allowed;
  - boilerplate plus one concrete sentence, where only that sentence may be praised;
  - the same draft plus "I worked hard on this", where the finding set and severities must not change;
  - five evidence-free contrasts plus one evidence-answered contrast, counted ×5 with 1 set aside.
- *Regression:* the 24 v1 items.

**Scoring:**
- Rewrite items use the v1 judge: severe-change typing, would-send, sentinels, and pairwise comparison in both orders.
- Review items use `check_report` with the draft (deterministic) plus a judge for the honesty items.

**Verdict:** NOT WORSE than the s8 tip and bare on severe changes and would-send (paired bootstrap 90% CI), plus a floor check. Anything else sends the change back.

## Step 10: comms-shape (branch `…-s10-comms-shape`, one PR, after step 9)

### Skill layout

```
skills/comms-shape/
  SKILL.md        # ≤ 500 lines; intent-first description with "Use when" and "Not for"
  README.md
  NOTICE.md       # credits: tenex playbook (ideas only, no license, no text),
                  # Ng course (inspiration), fsdatalab (paraphrased, linked)
  LICENSE
  references/
    stages.md          # stage-by-stage instructions and stop rules
    sharpen-questions.md   # defend / provenance / framing / contribution prompts
    outline-template.md    # thesis + talking points + evidence + [NEEDS] slots
```

### SKILL.md content

- **Entry A, from notes or an idea.** These stages run in order.
  - **0. Size.** A short piece (Slack, status, short email) collapses to one confirm-then-write turn. A long piece (readout, decision memo, incident note) gets the full flow.
  - **1. Intake.** Reader, decision or action wanted, the author's notes and data first. Up to 5 questions, in one message.
  - **2. Thesis.** One sentence, with 2–3 genuinely different framings drawn from the author's material. Never choose one for the author. **Required stop.**
  - **3. Outline.**
    - Every talking point ties to the author's material or carries `[NEEDS: …]`.
    - KB and playbook genre entries act as slot checklists here, not as text generators.
    - For a parallel item set, fix the item frame and the closed status vocabulary now.
    - **Required stop.**
  - **4. Sharpen,** which loops on the outline only.
    - **Defend:** weakest point, strongest objection, and what would change the call. The author answers.
    - **Provenance:** which query, dashboard or run each number came from. The skill never rules on truth.
    - **Framing:** inherited or stock framings get an alternative.
    - **Anti-sycophancy:** no praise of the outline, neutral questions, push back with evidence.
    - The loop ends when the author says so.
  - **5. Fill.**
    - Section by section for a long piece, at once for a short one.
    - Uses confirmed points only, with no new claims.
    - Uses the voice profile if one is loaded.
    - The author may write a section and ask for light-edit.
  - **6. Pre-send.**
    - **Contribution diff:** list the claims in the final text that trace to nothing in the author's notes, for the author to account for.
    - comms-polish `review`.
    - `tools/consistency_check.py`.
- **Entry B, pressure-test a draft.** Reverse-outline the draft into the thesis and the points it actually makes, then run stage 4 and stage 6. Never rewrite unless asked; fixes route to comms-polish.
- **Escape hatch.** For "just write it", write it, then list the skipped steps and the `[NEEDS]` gaps. Never refuse.
- **Carried over from comms-draft:**
  - `[NEEDS: …]` markers;
  - the fact-interpretation boundary;
  - KB lookup;
  - voice lookup;
  - learned rules;
  - untrusted-content rules;
  - Safety Rules (no invented facts, numbers, sources or actors).
- **Dropped:** one-shot full-draft generation as the default, and the de-uniforming pass.

### Archive and migration

- `git mv skills/ai-writing-suite/skills/comms-draft archive/comms-draft`. This is a repo-root `archive/` outside the packaged tree, with a README pointing to comms-shape.
- **Router** (`SKILL.md`):
  - In the table, the "add new content / mixed polish+add" row now routes to comms-shape.
  - A new row routes "pressure-test my draft / defend it before I send" to comms-shape.
  - `evals/test_router_routing.py` is updated to match.
- **References** are updated in:
  - comms-polish (boundary lines, scenario-presets);
  - comms-qa;
  - voice-onboard;
  - `_shared/voice-lookup.md`, `voice-profile.md`, `learned-rules.md`, `self-improvement.md`, `patterns/narrative-shape.md`;
  - README;
  - the manifests plus `evals/test_skill_manifests.py`.
- **Evals:**
  - `evals/fixtures/trigger_cases.json`:
    - draft queries move to comms-shape;
    - add "pressure-test this memo before I send it to the VP";
    - keep "what sounds AI-written" for polish as a near-miss.
  - `test_skill_lint.py` keeps its count of 5.
- **Draft eval harness:**
  - `evals/capabilities/comms_draft.py`, `fixtures/draft_cases.json`, `mutants_draft.py`, `run_draft_cases.py`, `test_draft_cases.py`, `test_draft_criteria_coupling.py`, `rubric.md` and `holdout_adversary.py`.
  - Port them to comms-shape stage 5 (`[NEEDS]`, no fabrication, criteria coupling).
  - Retire any case that pins one-shot drafting or de-uniforming, and list the retired cases in the PR.
- **Contract tests:** `test_fact_interpretation_contract.py` and `test_untrusted_content_contract.py` repoint to comms-shape.
- **Docs:** `docs/packaging.md` and the CHANGELOG.

### Behavioral eval (pre-registered before running)

- **Author packets.** A separate agent writes 8 packets with hidden intent:
  - the real thesis;
  - notes and numbers;
  - two preferences;
  - one point only the author knows;
  - one planted disagreement (the author rejects the first framing offered).
- **Simulated author.** An agent answers the skill's questions only from its packet.
- **Arms:**
  - comms-shape;
  - comms-draft one-shot, then up to 2 comms-polish rounds;
  - bare.
- **Measures.** Judges see the packet but not the arm.
  - **Intent fidelity:** the author's thesis and points appear in the final.
  - **Traceability:** the share of claims that trace to the packet, and the claims that trace to nothing.
  - **Unsupported claims and `[NEEDS]`:** count unsupported claims, and check that `[NEEDS]` is used where the packet lacks material.
  - **Would-send.**
  - **Planted disagreement:** whether the skill honored the author's rejection of the first framing.
  - **Cost:** total characters or tokens across all turns, and the number of author turns.
- **Verdict:**
  - comms-shape must be NOT WORSE than both other arms on unsupported claims and would-send;
  - on intent fidelity, traceability and cost, the result is reported as measured, with no pass bar set in advance.
- **Human anchor:** the owner runs comms-shape on 2–3 real documents.
- **Known limits:**
  - The simulated author is an LLM that tends to agree.
  - All judges are Claude.

## Questions for reviewers

1. Does the T7 reframe (emptiness, not symmetry) still catch AI boast lists ("Seamless integration / Robust performance") while exempting verb-first status lists?
2. Is "parallel item set, three or more siblings" a usable trigger, or will it fire on ordinary bullets in prose documents?
3. Do D and E hold up?
   - Is substring overlap the right test for praise that repeats a finding?
   - Is the ×N rule for quote counts checkable without false rejections?
4. Is widening the `Notes:` block a safe fix for the step-5 contradiction?
5. Is one skill with two entry points the right call, or will the router confuse comms-shape "pressure-test" with comms-polish `review`?
6. Is the simulated-author eval valid enough to support a verdict, and what is the cheapest design that still measures intent fidelity and cost?
7. What is missing: an owner ruling violated, a test pin that will break, or a file not listed?
