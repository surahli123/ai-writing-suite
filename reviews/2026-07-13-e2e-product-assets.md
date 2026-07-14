# Codex E2E Product Review (A2) — pattern catalog + seed KB + voice/self-improvement shared assets

Model: gpt-5.6-sol xhigh, read-only sandbox. Date: 2026-07-13. VERDICT: ASSETS FIX-FIRST
Scope note: evals/ explicitly off-limits (reviewed three times prior); this pass covers the PRODUCT surface.

---

Reviewed all 21 in-scope files breadth-first. No edits made; `evals/` was not reviewed, and skill prose was opened only for lifecycle/header cross-reference checks.

## 1. Pattern catalog

1. **BLOCKER** — Register shift has contradictory verdicts and incorrect index placement.

   - C11 says a sudden formal/casual shift “catches mixed human+AI authorship” and should be rewritten: [communication-artifacts.md:131](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:131).
   - The catalog guardrail says mixed casual/formal register often signals legitimate technical, young, or neurodivergent writing: [rhythm-stylometric.md:75](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:75).
   - The index places “register shift” under rhythm even though the entry lives in communication artifacts: [00-index.md:44](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/00-index.md:44).

   Why: the same passage can receive both “rewrite as AI-generated” and “do not flag” instructions.

   Fix: consolidate this into one entry with a validity condition: flag only an unexplained discontinuity corroborated by other signals, not ordinary mixed register. Correct the category row.

2. **CONCERN** — The “deduplicated single source of truth” promise is not true.

   - C2 calls tutorial-script framing “Collaborative-framing leaks” and says to delete the meta-commentary: [communication-artifacts.md:20](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:20).
   - H7 calls the same “Signposting / announcements”: [hedging-filler.md:85](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/hedging-filler.md:85).
   - H8 separately flags the overlapping `Let's + verb` subset: [hedging-filler.md:100](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/hedging-filler.md:100).
   - S9 lists `best-in-class`, `learnings`, `actionable`, `holistic`, and `synergy` as consultant-speak: [significance-attribution.md:115](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/significance-attribution.md:115). Those same terms already appear in L1’s vocabulary tiers: [lexical-tells.md:17](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/lexical-tells.md:17).

   Why: a reviewer can double-flag one phrase and choose between shallow word substitution and the deeper “replace with what happened” fix.

   Fix: assign one canonical entry per phenomenon. Keep narrower cases as aliases or subtypes with an explicit precedence rule.

3. **CONCERN** — A documented fix can immediately trigger another catalog entry.

   - R1 recommends questions to break sentence-length monotony: [rhythm-stylometric.md:20](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:20).
   - C8 flags rhetorical questions used as transitions, including “But what does this mean for developers?”: [communication-artifacts.md:94](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:94).

   Concrete loop: replace the third of four similar-length statements with “But what does this mean for developers?” R1 is satisfied, then C8 requires deleting it.

   Fix: R1 should prefer genuine syntactic variation and permit questions only when the question itself carries reader value—not as a rhythm device.

4. **CONCERN** — Comparable judgment-heavy categories lack overstepping’s validity discipline.

   Overstepping explicitly tests whether the corrected prior is real or manufactured before editing: [overstepping-presumption.md:10](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/overstepping-presumption.md:10). Comparable entries do not:

   - S1 defaults to deleting significance framing without asking whether it is evidence-backed analysis: [significance-attribution.md:9](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/significance-attribution.md:9).
   - S2 defaults to cutting interpretive meaning, although interpretation can be the document’s purpose: [significance-attribution.md:23](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/significance-attribution.md:23).
   - T9 treats paragraph independence as “AI-shaped” without a carve-out for references, FAQs, or deliberately modular documents: [structural-tells.md:112](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/structural-tells.md:112).

   Fix: add genre, evidence, and reader-purpose validity questions to every stance-level or document-level judgment.

5. **SUGGESTION** — Concrete exemplars are too sparse for the riskiest judgments.

   Only 12 of 67 entries have formal `Before` and `After` pairs; 55 do not. The index permits omission “where it earns its keep” [00-index.md:25](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/00-index.md:25), but all five stylometric entries lack paired examples, including the highly subjective low-perplexity fix: [rhythm-stylometric.md:50](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:50).

   Fix: prioritize paired exemplars for C11, R1–R5, T9, S2, and S3 rather than filling all 55 mechanically.

6. **CONCERN** — `00-index.md` is descriptive, not a reliable operational index.

   The inventory itself checks out: 8 category files, 67 entries, 3 lexical tiers, and all 67 entries have `Sources`. But:

   - No totals or per-file counts are exposed.
   - Category filenames are code spans, not Markdown links: [00-index.md:36](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/00-index.md:36).
   - “See `notes/`” points to no directory beneath the skill: [00-index.md:59](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/00-index.md:59).
   - Its “consolidated, deduplicated” promise conflicts with the overlaps above: [00-index.md:3](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/00-index.md:3).

   Fix: add counts, real links, a valid lineage path, and canonical/alias relationships.

## 2. Seed KB

1. **CONCERN** — Smoke Case 1 reaches the right answer for the wrong documented reason.

   The query is “My sentences are too long and try to say too much at once”: [SMOKE-TEST.md:58](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:58). The test claims keyword overlap with `one idea`, but `one idea` is absent from `clarity.md`’s Keywords column; it appears only in the Summary: [INDEX.md:27](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/knowledge/INDEX.md:27).

   Hand-check: `clarity.md` is still the best result through Summary/intent matching, but literal keyword overlap is effectively zero. The test therefore does not prove the keyword step it claims to prove.

   Fix: distinguish exact alias matching from semantic Summary matching and revise the rationale accordingly.

2. **SUGGESTION** — The smoke document has stale test-count language.

   Five cases are present, but the close says “run these two cases”: [SMOKE-TEST.md:162](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:162).

   Fix: say “all five cases,” or label a deliberate two-case minimum subset.

3. **CONCERN** — The company-fork promise is directionally sound but the demonstration skips the hard transformation.

   The product promise says a company “just drops in a Confluence page”: [SMOKE-TEST.md:3](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:3). The supposed raw incoming page is actually an already-curated passage from `clarity.md`: [SMOKE-TEST.md:28](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:28). A real addition also requires manually authored summary/keywords, smoke cases, and at least two bidirectional related-entry edits: [README.md:37](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/knowledge/README.md:37), [README.md:59](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/knowledge/README.md:59).

   Why: copying the five-entry structure would work, but it is “curate and index a page,” not merely “drop in a page.”

   Fix: include one genuine raw-page → normalized-entry → index-row example and a reusable entry template.

4. **CONCERN — retrieval simulation:** the graph works, but `INDEX.md` omits the one-hop instruction.

   Query: “How should I open an update for executives when it is too technical and buries the decision?”

   - `audience.md` is the strongest keyword match through `exec vs engineer` and `too technical`: [INDEX.md:29](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/knowledge/INDEX.md:29).
   - Its Moves provide reader/job calibration: [audience.md:16](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/knowledge/audience.md:16).
   - Its actual footer links one hop to `structure.md`: [audience.md:46](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/knowledge/audience.md:46).
   - `structure.md` supplies the second half—BLUF, decision/result/ask first: [structure.md:15](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/knowledge/structure.md:15).
   - The reverse link exists: [structure.md:45](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/knowledge/structure.md:45).

   Verdict: the real footers support the hop and are bidirectional. However, the retrieval protocol only says “pick one” or open both on a tie; it never instructs the agent to inspect `Related entries`: [INDEX.md:13](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/knowledge/INDEX.md:13). That behavior exists only in README prose.

   Fix: add an explicit bounded one-hop step to the canonical INDEX protocol.

Passed check: all five INDEX summaries and keyword sets honestly reflect their entry bodies; all five entries share a copyable `Principle / Moves / Before-After / When / Sources / Related` shape.

## 3. Voice and self-improvement assets

1. **BLOCKER** — The lifecycle’s legal statuses disagree.

   - `learned-rules.md` defines only `proposed | active | retired`: [learned-rules.md:25](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/learned-rules.md:25).
   - `self-improvement.md` instructs maintainers to set `status: graduated`: [self-improvement.md:97](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/self-improvement.md:97).

   Why: `graduated` violates the declared stable schema and has no defined on-start behavior.

   Fix: add `graduated` to the schema, lifecycle diagram, and ignore/apply rules—or represent graduation using an existing status plus a separate field.

2. **BLOCKER** — The lifecycle’s legal scopes disagree with participating skills.

   - Shared protocol permits only `comms-polish`, `voice-onboard`, or `all`: [self-improvement.md:71](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/self-improvement.md:71).
   - The stable entry schema repeats those three values: [learned-rules.md:27](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/learned-rules.md:27).
   - `comms-draft` requires scope `comms-draft`: [comms-draft/SKILL.md:166](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:166).
   - `comms-qa` requires scope `comms-qa`: [comms-qa/SKILL.md:136](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-qa/SKILL.md:136).

   Fix: either add all four current sub-skill scopes to the shared schema or remove the two unsupported participants.

3. **BLOCKER** — The only real learned rule cannot advance through an executable process.

   LR-001 has remained `proposed` since 2026-06-14: [learned-rules.md:84](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/learned-rules.md:84). The only promotion guidance is “Layer 3 eval passes, or user says make it active”: [learned-rules.md:39](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/learned-rules.md:39), [self-improvement.md:82](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/self-improvement.md:82).

   Missing: who initiates evaluation, when it runs, which evidence qualifies, who edits status, and how an old proposal is surfaced for a user decision. As written, no agent is responsible for moving LR-001.

   Fix: define an owner-run promotion procedure with a trigger/cadence, exact validation evidence, decision authority, and permitted one-line status edit.

4. **BLOCKER** — README describes a different approval/eval order.

   README says “approve → eval-test → append”: [README.md:120](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/README.md:120). The shared protocol says “approve → append as proposed → later eval/promote”: [self-improvement.md:82](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/self-improvement.md:82).

   Fix: select one canonical order and make every summary point to it without restating divergent steps.

5. **BLOCKER** — The blank and example profiles agree only by jointly omitting `Measured Fingerprint`.

   Their existing 13 H2 headers match exactly, satisfying the current “blank twin” claim: [host-profile-template.md:13](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/host-profile-template.md:13), [voice-profile.md:21](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/voice-profile.md:21). But a repo-wide exact search finds no `## Measured Fingerprint` in either file; both go directly from `Scope & Calibration` to `Changelog`: [host-profile-template.md:106](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/host-profile-template.md:106), [voice-profile.md:131](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/voice-profile.md:131). The writer contract still enumerates only the old ten dimensions: [voice-onboard/SKILL.md:81](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:81).

   Fix: add the identical H2 and field schema to both assets, provide a filled example with evidence/provenance, and update the writer’s dimension mapping.

## Hard questions

1. Is this catalog optimizing prose quality or detecting AI provenance? C11 and several stylometric entries currently turn weak provenance signals into mandatory style edits.

2. What exact authority promotes a rule: eval evidence, an explicit user override, or either—and who is responsible for revisiting old `proposed` entries?

3. Is `Measured Fingerprint` a stable contract field? If yes, which measurements, sample provenance, uncertainty, and recalculation date are mandatory?

ASSETS: FIX-FIRST