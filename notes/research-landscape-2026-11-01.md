# Research — writing-skill landscape, Aug–Nov 2026, vs the suite (2026-11-01)

**Status: RESEARCH + PROPOSAL ONLY. Nothing is implemented. Owner approval is required before any item is built.**

VERIFIED_AGAINST: `main` @ `233d54a` (72-entry catalog, 4 sub-skills, Waves 1–3 shipped)

## Method

A 5-agent Sonnet workflow (`wf_e4bb856a-cca`, about 1.5M subagent tokens, 387 tool calls). The orchestrator did the synthesis and spot checks.

| Lane | Scope | Sources read |
|---|---|---|
| stars-writing | Owner's stars from 2026-07-14 to 2026-11-01 that are writing skills, plus change checks on two repos studied earlier | 12 |
| stars-engineering | Owner's stars on skill/agent engineering (evals, self-improvement, cross-host packaging) | 18 |
| gh-landscape | `gh api search/repositories` for writing skills pushed or created since 2026-08 that were not studied before | 22 |
| discourse | X posts, practitioner essays, lab guidance, and 2026 papers | 47 |
| compare | Dedupe all 66 candidate practices into 27 clusters, then check each against the actual suite files and earlier plans and rulings, with `file:line` evidence | — |

Star list: the orchestrator read the first two pages of `github.com/surahli123?tab=stars` (60 repos, starred from about 2026-07-14 to 2026-11-01) and seeded the two star lanes from them. About 20 of the 60 are writing or skill-engineering repos. The rest are data-agent, harness, and memory projects outside this suite's scope.

Evidence limits. Read this before trusting any number below.

- **x.com was blocked by DNS in this environment.** Every X post cited here is a search snippet. The fix is to allow `x.com` under Network access in the cloud environment settings.
- arxiv.org, Substack, HN, Reddit, and most blogs were also unreachable. Paper findings come from search summaries or from Nanako0129/sepia's pinned source ledger, so they are second-hand.
- Most quantitative claims in the external repos are single-repo, author-run, and small-n.
- The orchestrator verified these primary sources directly:
  - Anthropic's *Prompting Claude Fable 5.1* "Writing density" section (fetched; the mannered-prose text is quoted below).
  - forjd/better-writing `evals/README.md` (the read-tracing numbers and the dev/held-out split).
  - Star, license, and push data for the six main repos.
  - Our own `rhythm-stylometric.md` R1, the scoring table in `comms-polish/SKILL.md`, and the fact that plan item T1-5 was never built.

## What changed in the field since our July round

1. **The value has moved from the tell list to measurement and restraint.** The strongest new repos compete on eval method, not catalog size. Their methods:
   - dev/held-out splits, K-repeat runs with Wilson intervals, and a no-skill baseline arm;
   - pre-registered win margins, and withdrawn or negative results published openly.

   Several projects *shrank* their skill and lost nothing:
   - shuorenhua went from 13 runtime files to 3 after 13 failed rounds of fixes;
   - short-humanizer, at 2.6k characters, tied blader/humanizer, at 32k, on 2 of 3 tasks;
   - plain-writing-skill publishes the rules on which the unaided model won.
2. **Tells are perishable and specific to each model release.** Two model cycles landed: Fable 5.1 on 2026-09-01 and Opus 5.5 on 2026-09-22. Reported changes (snippet-only, via Arena and Graphite):
   - Em dashes fell from about 15.2 to 0.8 per 1,000 words in one release.
   - Hedges ("perhaps", "arguably") rose about 97%.
   - New tells appeared: importance-flagging ("this matters", "why X matters"), "dependable", and Fable 5.1's **mannered prose** and denser sentences.

   The labs now publish anti-slop prompt text themselves. Anthropic's Fable 5.1 guide is verified. OpenAI's GPT-6 Astra slop list was read only via sepia. Repos such as sepia now key their fingerprint tables to exact model releases.
3. **Fidelity is now evaluated as a first-class property.** work-humanizer asks blind judges two separate questions: "reads human?" and "would you send this, given what the writer meant?" The one-line "make it human" prompt won the first question, changed 42 meanings, and was almost never chosen to send. Added-claims judges classify the rewrite's changes: hope restated as fact, emphasis restated as cause, hedge turned into assertion.
4. **Restraint has become a feature.** Recurring rules across sources:
   - "Clean text comes back unchanged."
   - A change needs a nameable failure; appearing on a tell list is not one.
   - After editing, run a reversion test on each replacement.

   New research shows editing and generating leave different footprints (all second-hand):
   - AI editing dilutes content words (Shan et al.).
   - It homogenizes variance (Sourati et al., *Nature Human Behaviour*).
   - Review-flavored prompts make models *add* defensive qualifications the source never had (Liao et al.).
5. **Detectors have hardened, and detect-mode scores are falling out of favor.** shuorenhua, no-ai-slop, forjd, qu-ai-wei, and sloptrim refuse to output authorship probabilities. Narayanan reports that a rewrite loop of Claude Code against the Pangram API made no progress at all. Substack's Pangram rollout drew broad backlash. Karr et al. find detectors cannot tell honest AI editing from AI drafting.
6. **The practitioner workflow norm is "human drafts, model critiques".** Ptacek and Willison: the model is a copyeditor, and you keep none of its words. Peter Yang: 25/50/25. Mollick says the same. All of these were seen as snippets.

## Where the suite stands

**Ahead of every writing skill we saw** in these areas:

- the deterministic detector with mutant families and a holdout adversary;
- the known-human false-positive eval;
- the audit-report contract enforced by a checker;
- the epistemic-modality protected class;
- per-genre voice profiles with a recomputable stylometric fingerprint, verbatim anchors, and self-report-vs-corpus divergence;
- human-gated learned rules;
- the untrusted-content contract.

No external writing skill ships a quantitative voice fingerprint or a holdout adversary.

**At par:** the false-positive gate, the narrative/structure-first tells (N1–N4, which match SlopShape and StoryScope), deletion-first density, and BLUF.

**Behind:**

1. We have no measurement of *skill lift*. Nothing compares the suite with a bare agent or a one-line prompt.
2. Fidelity checks stop at literal substrings. Nothing checks scope words or changes in claim strength. Plan item T1-5 (FIDELITY-FIXTURES) was proposed on 2026-07-21 but never built.
3. We have no edit-restraint mode and no fixture where the correct output is "no change".
4. The catalog is timeless (E2 is still design-only), so it cannot express "this tell decayed in Opus 5.5".
5. R1 prescribes the burstiness bands that the 2026 evidence calls weak or counterproductive.
6. The detect-mode score table still says "detectors will probably catch it" (`comms-polish/SKILL.md:245`).

**Dogfood note.** Our own files use the phrases Anthropic's guide gives as its examples of mannered prose:

- "earns its keep": `_shared/patterns/00-index.md:28`, `overstepping-presumption.md:135`;
- "load-bearing": 10+ hits, including a memo preset line that *whitelists* it (`scenario-presets.md:154`).

These are internal docs, not user output. But the memo preset line should change if a mannered-prose entry lands.

## Recommendations (prioritized by value ÷ effort)

The verdicts come from the compare agent's file-level check. "Pending" means an earlier doc already proposed the item and an owner ruling is outstanding.

### Tier A: small changes with high leverage (S each; most need no new infrastructure)

**A1. Fidelity classes: build T1-5 plus scope words** *(partial; 7 sources; S)*

- Add a `scope_tokens` class to `must_preserve`: a closed list such as only / first / most / never / may / often / all.
- Add the gold-FAIL lane T1-5 proposed: hope→fact, correlation→cause, hedge dropped, attribution-verb drift ("suggests"→"shows").
- Add a `no_strength_change` rubric dimension.
- Eval: a `scope_word_drop` mutant (drop "only", the check must FAIL). Gold-FAIL items stay outside the 30–40% calibration denominator.
- Sources: forjd (MIT), work-humanizer (MIT), and no-ai-style's anchor-compare script (MIT). quiron is AGPL, so ideas only.

**A2. Edit restraint** *(partial; 5 sources; S)*

- A light-edit switch in comms-polish, triggered by "light edit", "proofread", or "keep my voice". Under it, every word starts as kept, and a change needs a named failure: grammar, ambiguity, factual inconsistency, a house rule, or filler. Being on the tell list is not a failure.
- Add a reversion test and a dangling-reference check to `final-pass-checklist.md`.
- New fixture family: a clean human paragraph with one "delve" and one em dash. It passes iff the output is essentially unchanged. Edit distance is reported as a warning only, never as a numeric gate (the owner rejected numeric levers).
- Gold-FAIL: a rewrite that "improves" every sentence of a human text.

**A3. Guard against what a rewrite adds** *(partial; 4 sources; S)*

- One Safety Rule line: do not add qualifications, limits, or negative scoping the source lacks, even when asked to "make it more rigorous". Liao et al. report about 1.3 unsupported qualifications per 100 words from GPT-6 Astra under review-flavored prompts, and that AI judges *reward* them.
- An optional advisory diff of tell counts per category, source versus rewrite. It warns when a rewrite wipes a whole class (every dash stripped from a dash-leaning author) or introduces one the source never had. This is the patina pattern (MIT).
- Gold-FAIL: "make this more rigorous", where the output adds two caveats.

**A4. Detect-score epistemics: needs the pending owner ruling** *(pending; 7 sources; S)*

Seven sources converge on evidence first and scores never as authorship evidence. Recommended minimal shape, consistent with existing doctrine:

1. Keep the optional score, but present it as a **pattern-density band** with a fixed footer: "surface tells only, not authorship or humanness".
2. Delete "detectors will probably catch it" from the 61–80 row.
3. Add a Coverage line: which categories were checked deterministically, which by judge only, which as advisory, and which were left unverified.
4. Never output an authorship verdict.

Update `check_report.py` and the contract tests in the same PR.

**A5. Catalog additions with fresh multi-source or vendor evidence** *(pending + partial; S)*

- (a) Run the queued no-ai-slop lane, now corroborated by forjd, ZeroSlop, omp, and plain-writing rule 16:
  - faux-insight setups;
  - the statement-form C7 colon reveal, with the colon-for-lists carve-out;
  - "delete, don't substitute" for aphorism endings, with an exception when the closer carries a fact or a next action.
- (b) **New judge-only entry: mannered prose.** Anthropic's own definition, verified 2026-11-01 and to be quoted verbatim with attribution: *"Mannered prose substitutes metaphor and flourish for direct statement … When a literal phrase is available, use it."* The test is "is a literal phrase available?" Mark it model-scoped (Fable 5.1 era) once A7 exists. Fix the `scenario-presets.md:154` "load-bearing" whitelist in the same change.
- (c) Add the **portability/swap test** as one final-pass line: a sentence that could sit unchanged in another company's copy is filler. no-ai-slop added it in #33 (2026-08-05), and patina added it as detect-only.
- (d) Extend H6 to cover interpretive metadiscourse ("that last part matters more than it sounds"; no-ai-slop #34). Do not create a new entry for it.
- Skip: a standalone list of abstract metaphor nouns (high false-positive risk), and every source's em-dash ban (owner-rejected).

**A6. Soften R1 burstiness** *(gap; S)*

- R1's Fix prescribes word bands (3–8 / 12–20 / 25–40) and "never 3+ similar-length sentences in a row". That is the generic-numeric-lever class the owner already rejected.
- The 2026 evidence (second-hand) is mixed to negative:
  - sentence-length CV caught 2.5% of machine text at 1% false-positive rate (OPACE);
  - a "vary sentence length" instruction *raised* detector AUROC (BAIDYA);
  - against that, ai-spotter, at n=25, found spread to be its best signal.
- Recommendation: keep R1 as a detection signal. Rewrite its Fix so rhythm follows from content, never from a target band. Soften the "vary and roughen" bullets in comms-draft the same way.
- Fixture: a human text with deliberately uniform sentence lengths must not be rewritten just to add variance.

### Tier B: medium lanes

**B7. Build E2 tell-catalog versioning, plus four additions the design lacks** *(pending; M)*

E2's design (`docs/design-tell-catalog-versioning.md`) stands. Add:

1. An optional release-range field per entry: `Observed-in` / `Decayed-in`. These are priors, never inferred from the prose itself.
2. A **dormant** status distinct from retire. Dormant entries are demoted to advisory but still match human-pasted or older-model text.
3. An optional evidence-tier field.
4. An opt-in re-baseline probe. It generates no-skill outputs from the owner's actual target models on the fixture prompts, runs the stdlib detector, and emits a hit-rate table per entry. The table is evidence, and every status change stays behind the human gate.

Motivating case: the em-dash collapse in Opus 5.5.

**B8. DS-audience presets and document-mode gating** *(pending E3 + partial; M)*

- New qualitative presets with no numeric caps: **executive brief**, **analytical report**, **incident/postmortem**.
- A one-line document-mode classifier (reference / how-to / explanation). It gates hedging and modality findings: a hedge in a reference page is a tell, while calibrated uncertainty in an analytical memo is protected.
- A **content-gap** finding type in the audit report, kept outside the tell score. It covers a hollow span with no claim to recover: report it with `[NEEDS: …]` and never invent.
- Draft-side certainty guard: a lead that states a cause must carry its evidence status. Answer-first can manufacture certainty, and i-have-adhd's own eval found that regression.
- Sequence: after E3's register-overlay migration.

**B9. Static lint that skills tell the model to read their references** *(gap; S–M)*

forjd traced its progressive-disclosure arm. The model read **no reference file in 33 of 39 runs** until SKILL.md explicitly said "read X before every rewrite". After the fix, it read one in 35 of 39, and the progressive pass rate rose from 77/110 to 101/110. We verified this in their `evals/README.md`. Our router plus sub-skills plus `_shared/patterns` layout is exactly that shape.

- Cheap step: extend `test_skill_manifests.py` to assert that each step needing a catalog or reference file says "read <path>", and that the path exists.
- Mutant: remove one "read" instruction; the lint must fail.
- Later: an opt-in live read-trace and trigger eval.

**B10. Hygiene for live evals** *(partial; S–M)*

Do this before any live arm:

- a run header recording model, judge, suite version, fixture hash, and K;
- `AIWS_STATE_DIR` pointed at an empty temp dir, so learned rules and voice profiles cannot leak into baselines;
- K-repeat with Wilson intervals;
- a pre-registered threshold file, and a third "review" verdict.

### Tier C: large or deferred

- **C11. Skill-lift ablation arm** *(gap; the single highest-value item; L)*
  - Three arms: bare / one-liner ("clean this up, keep facts and voice, add nothing") / suite.
  - Each arm is scored by the existing deterministic checks plus a blind pairwise judge.
  - Optional per-rule ablation to prune the 72 entries.
  - Advisory only, kept out of `run_all.sh` (ruling D2).
  - Its numbers only mean something on real DS drafts, so it is **blocked on the P3 real-writer corpus**. Do B10 first.
- **C12. Judge protocol upgrade.** Order-swapped pairwise judging, where a win counts only if it holds both ways; the "would you send this?" question; a multi-family panel; a tie and margin policy. This only has value once C11 produces competing outputs.
- **C13. Recipient proxy.** A fixture class built from de-identified real reviewer comments on DS drafts, with a disposition ledger. This is DocWriter's coverage-ledger idea, under E4 consent rules. It would also feed the blocked P3 corpus. Defer the reader-model comprehension probe (an unproven proxy).
- **C14. Harden the learned-rule loop.** A rejected-proposals ledger, a `quarantined` status, promotion only on recurrence plus a violating / safe-exception / adjacent-irrelevant fixture triple, voice-vs-content edit separation, and channel tags. Sources: agents-spec (MIT), agent-skills-platform (MIT), my-voice (MIT). Defer until real learned rules exist; the live file is empty.
- **C15. Small follow-ups.**
  - Have the owner run `npx skills add . --list` once, to see whether the router's SKILL.md shadows the nested sub-skills. Seven of 13 starred engineering repos ship through `npx skills`. Never add Node to CI.
  - KB provenance: add `fetched_at` / `source_revision` to kb_ingest's provenance line, and show the verified date in comms-qa. This matters once a fork's Confluence playbook drifts.
  - Finish the `docs/forking.md` deliverable from Q12, which is still missing from the tree.

### Covered, or not worth doing

- Structure before surface: already covered by `narrative-shape.md` N1–N4 and the comms-draft shape pass.
- A word-level revision view (DocWriter): useful for owner review but not a quality lever. At most an optional stdlib `difflib` helper later.
- Voice A/B confirmation probes: mostly already built (anchors, divergence, minimum sample counts). The only small delta is a guard that "a zero metric does not establish an absence".
- A fork-declaration manifest (pstack `forks.json`): premature, since no fork exists.

## Re-proposals of owner-rejected items (seen, not recommended)

- **Outright em-dash bans:** plain-writing rule 15, pstack/unslop rule 13, no-ai-slop ("in short copy, use none"), omp, slopbeth, stop-slop.
- **Generic numeric levers:**
  - i-have-adhd's 5-item list cap;
  - plain-writing's 20/25-word gates and ASD-STE100's sentence limits;
  - work-humanizer's 70% band and "one word in six" quota;
  - jakubkrehel's 30-word ceiling;
  - clearmode's CI score gate.
- **Manufactured personality:** outbound-writing's "volunteer a disqualifier" and "costly take", zh-humanizer's literary lift, unslop's "soul".
- **Multi-role and router pipelines:** ZeroSlop's eight roles, de-ai-router, im-not-ai.
- **Writing for AI-agent readers:** clearmode's reader profiles, agents-spec, openwiki. A related data point: ETH found that LLM-generated AGENTS.md files *reduced* agent task success.
- **Public corpus as the main evidence:** plain-writing, quiron, ai-spotter, im-not-ai, sloptrim.

## Source notes

### Owner's stars: writing

| Repo | License | Stars | What's distinctive / transferable |
|---|---|---|---|
| [forjd/better-writing](https://github.com/forjd/better-writing) | MIT | 52 | Richest eval method in the lane: an always-on vs progressive-disclosure arm with read tracing, a 13/9 dev/held-out split enforced by `validate.py`, K=5 with Wilson and Newcombe intervals, an added-claims judge, a trigger eval, a dated tell catalog. **Not** derived from jpcaparas (different lineage, MIT), so the D5 license block does not apply to it. |
| [docwriter-org/plain-writing-skill](https://github.com/docwriter-org/plain-writing-skill) | MIT | 739 | Shreya Shankar. 25 rules, each with a before/after pair. Blind per-rule pairwise judging against the unaided model, with a published list of rules where the baseline won. The style is extreme (no dashes, no analogies). The "revision view" lives in the sibling [DocWriter](https://github.com/docwriter-org/docwriter) app (MIT): tracked changes with the rationale shown before each edit, freeze spans, critique lenses, a reviewer-comment coverage ledger. |
| [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) | MIT | 59.6k | Answer-first output rules plus an honest eval: 14 cases × 3 trials, a blocker veto, a release gate. It published its own gate failure and a regression caused by its answer-first rule. |
| [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop) | MIT | 13k | Since 07-22: a portability test (#33), removal of interpretive metadiscourse (#34), and dropping the voice-signal-note ritual (#49). Detect mode refuses to score. |
| [plannotator/write-better](https://github.com/plannotator/write-better) | MIT | 35 | Since 07-14: an asd-ste100 sibling skill, plus "don't announce how many points follow". |
| [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | MIT | 21.8k | khazix-writer is **unchanged** since 07-02. The new skills (leader, neat-freak) are not prose editors. |
| [mengke-wang/zh-humanizer-literary](https://github.com/mengke-wang/zh-humanizer-literary) | MIT | 89 | The same repo as nihe0909, renamed. No rule changes. |
| [barretlee/agent-pulse](https://github.com/barretlee/agent-pulse) | MIT | 239 | Not a writing skill. Transferable idea: cited URLs must be a subset of the supplied evidence, with separate fact fields and judgment fields. |

### Owner's stars: skill engineering

| Repo | License | Stars | Transferable pattern |
|---|---|---|---|
| [Sahir619/fable-method](https://github.com/Sahir619/fable-method) | MIT | 2.3k | Rules ship only with a failing trap fixture. Forced artifact lines at decision points lifted Haiku from 1/4 to 4/4. Rule lift falls as model tier rises. |
| [Leonxlnx/unlazy](https://github.com/Leonxlnx/unlazy) | MIT | 4.2k | An acceptance ledger written before the work. `gate-lint` asks whether a gate can fail at all. It demotes its own unreproducible results to provenance only. |
| [michael-denyer/pstack-claude](https://github.com/michael-denyer/pstack-claude) | MIT (from Cursor pstack) | 3.7k | `forks.json` divergence declarations; validator invariants each with a fixture that trips them; an unslop catalog with stable ids; Diataxis-mode technical writing. |
| [majiayu000/spellbook](https://github.com/majiayu000/spellbook) | MIT | 288 | One source tree for Claude and Codex; a strict skill validator; capability-distill, which re-diffs rules at each model upgrade. |
| [langchain-ai/openwiki](https://github.com/langchain-ai/openwiki) | MIT | 17.6k | Grounded claims with versioned evidence; a supported / stale / invented / unverified ledger; a read boundary via an ignore file. |
| [leftzzzz/agents-spec-skill](https://github.com/leftzzzz/agents-spec-skill) | MIT | 37 | Rule governance: admit a rule on recurrence or material harm, and validate it with a violating / safe-exception / adjacent case. Exit codes 0/1/2. |
| [jakubkrehel/skills](https://github.com/jakubkrehel/skills) | MIT | 9.6k | A calibration line per skill ("taste is not a finding"); a review format with a coverage section, a "Not verified" section, and a verdict. |
| [google-research/harness2](https://github.com/google-research/harness2) | Apache-2.0 | 21.7k | Propose-probe-compose: separate editors for invariant behavior and domain knowledge. |
| [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | MIT | 73.5k | Per-host generation from one template behind a parity test. Prose is localized; structural keywords stay in English. |
| [TianyuCodings/JevHarness](https://github.com/TianyuCodings/JevHarness), [hermes-skill-factory](https://github.com/Romanescu11/hermes-skill-factory), [unclebob/ub-mode](https://github.com/unclebob/ub-mode) | **none declared** | — | Ideas only: rejected-proposal memory, propose-one-at-a-time, "a test that passes when everything returns nothing is worthless". |

Found by search, not starred: [edonadei/caliper](https://github.com/edonadei/caliper) (MIT; ablation and activation evals for skills), [ai-evals-course/evals-skills](https://github.com/ai-evals-course/evals-skills) (Apache-2.0; Husain/Shankar judge validation), [vercel-labs/skills](https://github.com/vercel-labs/skills) (MIT; the `npx skills` channel).

### New writing skills on GitHub (not starred, not studied before)

| Repo | License | Stars | Distinctive |
|---|---|---|---|
| [MrGeDiao/shuorenhua](https://github.com/MrGeDiao/shuorenhua) | MIT | 2.4k | Fidelity-first Chinese rewrite skill. v2.5 collapsed 13 runtime files to 3. Eval set: 65 needs-edit and 58 should-not-touch cases. Outputs no AI score. |
| [Nanako0129/sepia](https://github.com/Nanako0129/sepia) | MIT | 3.6k | Fingerprint tables keyed to model releases, separating author model from executor model. A graded evidence ledger of about 70 sources. Deletion and reversion tests. A no-plugin baseline arm in CI. |
| [phuryn/work-humanizer](https://github.com/phuryn/work-humanizer) | MIT | 122 | For commitment-bearing work prose. A fact ledger with certainty levels; an interview mode; 4 judge families × 2 orders × 2 questions (reads human / would send). |
| [ilien-dev/quiron](https://github.com/ilien-dev/quiron) | **AGPL-3.0** (ideas only) | 62 | Human-baseline bands with an overshoot side. Best negative results: a plausible checklist item made blind-judge P(AI) *worse*, and the writer's own material moved readers where style fixes did not. |
| [manavmishra/ZeroSlop](https://github.com/manavmishra/ZeroSlop) | MIT | 152 | Experiential claims count as fabrication; idempotent on human text; a replication that cut its own headline result from 32/50 to a pooled 55/100. |
| [devswha/patina](https://github.com/devswha/patina) | MIT | — | An advisory source-vs-rewrite overcorrection diff; a detect-only portability probe; patterns promoted only at precision 1.00 on 50 documents. |
| [LifelongLazyLearner/qu-ai-wei](https://github.com/LifelongLazyLearner/qu-ai-wei) | MIT | 707 | A frozen information ledger before rewriting; verdicts describe editing status, never authorship; 20 clean-session fixtures with invariant-only checks. |
| [seyedehsanhadi/sloptrim](https://github.com/seyedehsanhadi/sloptrim) | Apache-2.0 | 412 | A stdlib detector in which 12 of 71 patterns are advice-only because they mark formal register. ETHICS.md: "a score describes prose, never a person". |
| [01NGVI-QINGYI/no-ai-style](https://github.com/01NGVI-QINGYI/no-ai-style) | MIT | 6 | Fact / interpretation / unverified boundary; EVIDENCE GAP vs INTERPRETATION FLAG markers; a before/after anchor-compare script for numbers and DOIs. |
| [Dexxter182/humanizer-hu](https://github.com/Dexxter182/humanizer-hu) | MIT (from blader) | 6 | Document-level decisions made before the first sentence; the lint reads its phrase list from SKILL.md, so there is one source of truth. |
| [bnivanov/omp-writing-skills](https://github.com/bnivanov/omp-writing-skills) | MIT | 7 | A separate drafter and editor subagent above about 300 words; a deterministic lint with exit codes 0/1/2. |
| [larashero3-dotcom/lieflat-less-ai-tone](https://github.com/larashero3-dotcom/lieflat-less-ai-tone) | **CC BY-NC** (ideas only) | 4.7k | A matched-pair study of 5.2M characters showing em-dash direction *flips* between GPT-5.6 and Opus 4.6. |

stop-slop has no commits since 2026-03-18. anthropics/skills shipped no writing skill. Its relevant changes were the eval-hillclimb and eval-audit guides and a frontend-design update with a dated list of default tells.

### X and web discourse (all X items are snippet-only)

- **The Fable 5.1 "mannered prose" wave, 2026-09-01 to 09-03.** Anthropic's guide (verified) was amplified by @addyosmani, @MaxForAI, @Voxyz_ai ("You removed the It's-not-X-it's-Y lines. It still reads like AI."), @alex_prompter, and @NFT_Chen. A Reddit thread reportedly called the guide itself dense; that is unverified.
- **The Opus 5.5 em-dash collapse, 2026-09-22 to 09-25.** @theo ("THEY REMOVED THE EMDASHES") and @arena (10 of 12 writing measures improved, hedges up 97%). Pebblous relayed Graphite's finding that 2,548 tells remain and "this matters" appears at about 100× the human rate.
- **Detection.** The Narayanan note, the HackerNoon test, Pangram vendor claims, and the Substack rollout backlash (AI Weekly / 404 Media). @jbruce218 offers an anecdotal counterexample of a humanizer beating Pangram. @LeahLibresco wants a Pangram MCP for hiring.
- **Workflow.** Willison's post on Ptacek's "How to Write with an LLM" (2026-09-17). @petergyang's 25/50/25 (2026-07-22). @Jayyanginspires: 15–30 pieces per client, a quoted line for every voice claim, blind testing.
- **Research, second-hand:**
  - Shan et al. 2608.27855 (editing vs writing footprints);
  - Liao et al. 2610.11355 (defensive writing);
  - Karr et al. 2608.11256 (detectors cannot separate editing from drafting);
  - Baumler et al., ACL 2026 (writers feel post-edited LLM text is theirs while it stays closer to the LLM);
  - Sourati et al., *NHB* 2026 (homogenization);
  - SlopShape 2609.15369 (structure alone reaches 98 macro-F1 on commercial web posts);
  - position-bias work 2602.02219.
- **Thin:** no 2026 source specifically on writing for data-science audiences (BLUF, decision memos) beyond generic guides and Anthropic's "Lead with the outcome".

## Suggested build order (after owner rulings)

1. **A4 ruling, then A1 + A2 + A3.** These are fidelity and restraint changes: all S, all with deterministic fixtures, and none touching the calibration band.
2. **A5 + A6.** Catalog updates through the normal catalog process: NOTICE credits, plus a probe and a known-human negative for each entry.
3. **B9 + B10.** Cheap static lint and live-eval hygiene. These unblock any later live arm.
4. **B7 (E2 build) → B8 (presets/mode, after E3).**
5. **C11 ablation, once real DS drafts exist (P3).** Then C12, then C13.

Owner decisions this note needs:

- (i) A4 score shape.
- (ii) Whether mannered prose enters as a judge-only entry now, or waits for release scoping (B7).
- (iii) R1 softening (A6). It edits a shipped regex entry's Fix prose, not its detector behavior.
- (iv) Whether to allow `x.com` in the environment network policy, so the next round can read threads and replies directly instead of snippets.
