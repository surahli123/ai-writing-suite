# Codex E2E Product Review (A1) — the four sub-skill SKILL.md files + suite router as runtime prompt-code

Model: gpt-5.6-sol xhigh, read-only sandbox. Date: 2026-07-13. VERDICT: PROSE FIX-FIRST
Scope note: evals/ explicitly off-limits (reviewed three times prior); this pass covers the PRODUCT surface.

---

Direct single-agent pass completed. No `evals/`, `_shared/patterns/`, or `_shared/knowledge/` contents were reviewed.

## Findings

### BLOCKER

1. **The suite-root router promises routing, then refuses to route on its main hosts.**  
   [router:3](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/SKILL.md:3) says it “Routes a request to the right sub-skill.” But [router:31-35](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/SKILL.md:31) says: “Do **not** intercept or re-route here. Let the host pick the sub-skill.”

   Why it breaks: if the root skill itself is selected or explicitly invoked in Claude/Codex/Cursor, it has no executable dispatch step and produces nothing. Success depends on an undocumented assumption that the host discovered and selected a nested skill instead.

   Fix: when the root skill is loaded, always classify and load the chosen child. Skip routing only when a child skill was already selected directly.

2. **Mixed polish-plus-add requests have contradictory routing and execution contracts.**  
   [polish:3](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:3) says: “A mixed request to polish AND add … routes to `comms-draft`.”  
   [draft:3](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:3) agrees: “mixed polish-plus-add requests” belong there.  
   But [router:44-50](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/SKILL.md:44) maps polish to `comms-polish`, drafting to `comms-draft`, then defaults ambiguous requests to `comms-polish`. Worse, [draft:138-145](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:138) says the draft skill “does not edit existing user text.”

   Why it breaks: the intended skill is forbidden from operating on the existing document, while the fallback skill is forbidden from adding the requested substance. Draft’s final step merely *offers* polish as a later pass; it does not complete the polish already requested.

   Fix: add a universal precedence rule: “Any requested substantive addition routes to `comms-draft`.” Define mixed mode explicitly: existing text becomes immutable source material, `comms-draft` returns the revised full document, then runs the polish final-pass requirements before returning.

3. **The polish prose teaches fabrication while prohibiting it.**  
   [polish:138](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:138) instructs the agent to replace abstractions with “concrete actors, actions, examples, or consequences,” while [polish:149-150](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:149) forbids adding examples or claims. The example at [polish:171-183](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:171) turns a generic migration claim into an invented retry job and “last week’s duplicate sends.”

   The same drift appears in [scenario-presets:49-50](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:49): replace “many / some / a lot” with “the actual number,” despite [scenario-presets:161-164](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:161) prohibiting invented facts and changes to numbers.

   Fix: say “make sourced concrete details more prominent; if none exist, preserve the abstraction or flag the missing detail.” Replace the migration example with one whose after-version contains no new facts.

4. **`voice-onboard` promises multiple genre profiles but defines only one storage and consumption path.**  
   [voice:59-60](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:59) says to offer two profiles for mixed genres; [voice:104-105](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:104) says “split, don’t flatten.” Yet [voice:42-44](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:42) defines only `_shared/voice-profile.md`, and consumers load only that singular file.

   Why it breaks: the agent cannot name, store, select, or consume the second profile.

   Fix: either restrict v1 onboarding to one target genre per run, or define profile IDs, paths, default-selection rules, and consumer lookup behavior.

### CONCERN

5. **The voice-profile schema has drifted between producer and consumers.**  
   [voice:81-98](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:81) claims its ten dimensions map 1:1 to profile headers and includes `Vocabulary`, but not `Scope & Calibration`.  
   [polish:86-90](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:86) and [draft:45-48](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:45) include `Scope & Calibration` but omit `Vocabulary`.

   Fix: publish one canonical ordered header list and make producer and consumers reference it rather than restating divergent schemas.

6. **`comms-qa` both promises KB-only answers and permits non-KB answers.**  
   [qa:3](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-qa/SKILL.md:3) says it “answers only from that entry’s content.” [qa:82-87](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-qa/SKILL.md:82) and [qa:116-118](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-qa/SKILL.md:116) allow an “Outside the playbook” answer.

   Fix: choose one policy. If outside advice remains allowed, frontmatter must say that the KB answer is source-locked while optional general advice is separately labeled.

7. **The router defeats selective loading and causes unnecessary context expansion.**  
   [router:58-60](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/SKILL.md:58) says to read “every file that sub-skill references.” That conflicts with selective instructions such as [polish:37-38](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:37), which loads only relevant pattern categories, and [draft:38-57](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:38), which selects relevant KB entries and catalog categories.

   Fix: “Load the child skill, then let that skill determine which referenced assets are required.”

8. **Draft input failure behavior is contradictory.**  
   [draft:32](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:32) says to degrade gracefully on “anything absent”; [draft:34](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:34) marks the brief required; [draft:81-82](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:81) says never block on a missing input. The shared-path protocol, correctly, requires asking for the install path when the suite root cannot be found.

   Fix: classify inputs explicitly: brief and suite root are required; profile, KB match, and genre preset are optional.

9. **Polish output requirements cannot all be followed.**  
   [polish:75](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:75) and [polish:244](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:244) require polished text only. But [polish:94-96](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:94) requires noting a missing profile, and [polish:145](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:145) requires mentioning unsupported claims.

   Fix: define narrow exceptions to text-only output, such as an optional `Notes:` block only for missing evidence—not routine missing-profile fallback.

10. **Router status prose is stale and internally contradictory.**  
    [router:3](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/SKILL.md:3) says QA/drafting arrive “later”; [router:18-19](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/SKILL.md:18) marks them available, and [router:75](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/SKILL.md:75) says QA now ships. [router:45](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/SKILL.md:45) still says “until then” for an already-built `voice-onboard`.

    Fix: remove Layer-era roadmap language from runtime prose and use only current availability.

11. **The repeated self-improvement rule has drifted.**  
    [draft:175-178](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:175) explicitly requires scope `comms-draft`; [polish:234-236](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:234) and [voice:155-158](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:155) merely say “scope.” Polish, draft, and voice mention Layer-3 evaluation; QA omits it.

    Fix: use identical boilerplate with the concrete current-skill scope in every child—or keep only a concise pointer to the shared protocol.

12. **Voice onboarding leaves several runtime decisions underspecified.**  
    [voice:56-71](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:56) defines Low only loosely and calls six samples Medium without defining thresholds. [voice:41](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:41) says to “fill in” the blank template, which can be read as editing the template itself. [voice:132](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:132) says to update “the changelog” without saying whether that is the package `CHANGELOG.md` or a profile field.

    Fix: define confidence thresholds, say “copy the template into a draft; never modify the template,” and store sample date inside the profile contract.

13. **Draft citations lack an output location.**  
    [draft:42-43](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:42) requires citing the KB filename when a choice came from it, but [draft:184-195](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:184) provides no sources field and does not say whether citations belong inside the deliverable.

    Fix: add a non-deliverable `Sources used:` line after the draft, or explicitly say citations are internal unless the user requests provenance.

14. **Two prose backreferences are dead in the working tree.**  
    [voice:140-142](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:140) says “see the project plan, R1,” and [scenario-presets:18](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:18) says “design §5.” No plan/design file exists under the suite working tree.

    Fix: link a shipped file and heading, or remove these internal-development references.

### SUGGESTION

15. **Fully qualify the pattern catalog paths.**  
    [polish:40-48](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:40) fully qualifies only `00-index.md`; subsequent filenames are bare. Prefix each with `_shared/patterns/` so they unambiguously use the suite-root protocol.

## Checks that passed

- The four child skills’ “Locating shared assets” blocks are byte-for-byte identical.
- Both referenced `comms-polish/references/` files exist.
- Numeric workflow backreferences—polish step 5, draft step 1, and QA steps 3–5—are correct.
- No missing numbered workflow steps were found.

## Context bloat

Token estimates use approximately four bytes per token.

| File | Lines | Words | Approx. tokens |
|---|---:|---:|---:|
| `skills/comms-polish/SKILL.md` | 246 | 1,726 | 2,920 |
| `skills/comms-draft/SKILL.md` | 195 | 1,712 | 2,733 |
| `skills/comms-qa/SKILL.md` | 168 | 1,463 | 2,189 |
| `skills/voice-onboard/SKILL.md` | 178 | 1,353 | 2,202 |
| Router `SKILL.md` | 75 | 660 | 1,023 |
| `references/scenario-presets.md` | 167 | 1,080 | 1,777 |
| `references/final-pass-checklist.md` | 67 | 486 | 779 |
| **Total** | **1,096** | **8,480** | **13,623** |

About 1,730 tokens—roughly 13%—can leave the normal invocation context:

- Polish: examples plus score/edit-only instructions, ~476 tokens.
- Draft: explanatory design rationale, ~259.
- QA: repeated intro and boundary prose, ~383.
- Voice: product-owner mental model and attribution comment, ~220.
- Router: “Engine vs fuel” packaging explanation, ~104.
- Presets: attribution prose, ~59.
- Checklist: attribution plus optional scoring rubric, ~231.

Keep executable rules inline; move examples, rationale, attribution, and mode-only rubrics to conditional references.

## Router dispatch coverage

The descriptions are exhaustive only if the product promise is narrowed to the four named atomic jobs. They are not exhaustive under the root’s broader “writing-assistant … docs, emails, posts, reports” positioning.

- Matches none: “Translate this launch email into Spanish without changing its meaning.”
- Matches two: “Learn my voice from these samples, then polish this memo in that voice.” It independently triggers `voice-onboard` and `comms-polish`, but the router defines no composition sequence.

Compound requests therefore make the four descriptions non-mutually-exclusive even though their negative clauses mostly separate atomic requests.

## Runtime simulation

Request: “Polish this doc and add a risks section, in my voice.”

1. On Claude/Codex/Cursor, the root router declines to route. If host-native discovery works perfectly, the mixed-request clauses should select `comms-draft`. If the root skill itself was selected, execution stalls.
2. On RovoDev, the request matches both the polish and draft rows. The only tie-break says default to `comms-polish`, which is the wrong skill for adding risks.
3. If `comms-draft` is selected, it loads `_shared/voice-profile.md` during step 2 at [draft:76-82](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:76).
4. If the profile exists, voice loading works. If absent, the skill infers a generic context-appropriate voice; it does not request a voice sample or hand off to `voice-onboard`, so “in my voice” is unmet.
5. Draft then contradicts itself by operating on an existing document despite saying it does not edit existing text.
6. Its final handoff merely offers `comms-polish` as an optional future pass. It does not complete the polish already requested.
7. If `comms-polish` was selected instead, it can load the voice profile but must refuse to add the risks section—and its body contains no executable handoff for the mixed case.

Result: the request cannot be completed as written on either dispatch path.

## Hard questions

1. For mixed edit-plus-add work, should `comms-draft` return a fully revised document, or generate only the new section and then obligatorily invoke `comms-polish`?
2. Does “in my voice” require a real profile/sample, or is generic inferred voice an acceptable fallback? If it is not acceptable, what is the mandatory onboarding gate?
3. Is `comms-qa` strictly KB-only, or is separately labeled general advice part of the product?
4. Is multi-genre voice profiling actually a v1 capability? If yes, what is the storage and selection contract?

PROSE: FIX-FIRST