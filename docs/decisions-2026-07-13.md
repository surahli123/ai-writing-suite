# Owner decisions — 2026-07-13 (verbatim record)

Answered by the product owner via the decision artifact; recorded here so every future
session can cite the ruling instead of re-asking. Q1–Q6 unblock the architecture roadmap;
Q7–Q16 unblock remediation items 1.6–1.13 and the fork-strategy docs.

| # | Key | Decision | Notes / implications |
| --- | --- | --- | --- |
| Q1 | severity-axis | **two-fields** | Severity = editorial harm; Enforcement = mechanism. Detection confidence stays in detector tiers. Unblocks #10. |
| Q2 | live-lane-purpose | **release-regression** | Scheduled judge lane compares against a pinned baseline on skill changes; quality trend is a byproduct artifact. Unblocks #8. |
| Q3 | tell-id-language | **universal-ids** | One ID per tell; language is a field. Per-language evidence/rules hang off the ID. Unblocks #14 + registry migration. |
| Q4 | score-contract | **versioned-policy** | Detector score is NOT a compatibility contract. Measurement-policy version + band recalibration commit on tokenizer change. Unblocks aiws/text.py. |
| Q5 | generated-projections | **checked-in-lockfile** | Generated index/rubric/coverage projections are committed, marker-bounded, CI-freshness-checked; reviewed like lockfiles. No build step at use time. |
| Q6 | judge-dimension-granularity | **aggregate-with-subtype-evidence** | One dimension per multi-sub-type tell; judge must NAME the sub-type in its EVIDENCE line; coverage reporting parses evidence. |
| Q7 | mixed-mode-contract | **full-document** | comms-draft handles mixed polish+add: existing text = immutable source; returns the fully revised document; runs the polish final-pass itself. Fixes the A1 BLOCKER routing dead-end. |
| Q8 | voice-fallback | **offer-then-degrade** + owner rider | Offer voice-onboard once, degrade to inferred voice with an output note. **Rider (owner, verbatim intent): prompt/offer voice onboarding even after comms-polish runs and after the user's MANUAL EDITS — the edit delta is the strongest voice signal.** Implements research #16's edit-based updater direction as a product behavior. |
| Q9 | qa-scope | **labeled-extra-ok** + "user can specify" | Keep "Outside the playbook" labeled section; fix frontmatter wording; allow the user to request strict-KB-only per invocation. |
| Q10 | multi-genre-voice | **build-multi** (overrides the one-genre-v1 recommendation) | Build the real contract: profile IDs/paths (per-genre files), default-selection rules, and consumer lookup in comms-polish + comms-draft. Design before build; this is the largest new work item from the decisions. |
| Q11 | generic-kb-default | **replace-default** | Fork onboarding Step 0: delete the five generic entries + rows by default; keep-both is the documented exception. Decides the shadowing fix. |
| Q12 | upgrade-ownership | **document-honestly** | Ship docs/forking.md (pin to tags, merge recipe, ours-strategy for replaced KB, stability guarantees); an engineer in the upgrade loop is acknowledged. Fuel-out-of-tree stays a v2 option. |
| Q13 | index-protocol-canonical | **index-canonical** | INDEX.md's frozen 4-step protocol is canonical; tools must never rewrite it. Confirms the kb round-2 fix direction. |
| Q14 | nature-skills-attribution | **record-commit** | Archaeology: pin the absorbed MIT-era commit SHA + license snapshot in NOTICE. Extraction predates the 2026-06-18 relicense. |
| Q15 | rovodev-claim | **narrow-now** | Narrow shipped claims to "registration + comms-polish verified 2026-06-08; other skills untested on RovoDev". #27 re-verification stays owner-scheduled (company machine). |
| Q16 | catalog-purpose | **quality-first** | A tell is actionable only when the prose is genuinely worse; provenance-only signals become advisory, never mandatory edits. Drives validity-condition work on C11-class entries. |
