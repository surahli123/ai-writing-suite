# Codex Adversarial Review — research findings + repo (2026-07-21)

VERIFIED_AGAINST: docs/genre-presets-pr-release-note @ f46ce6e @ 2026-07-21T22:45-07:00
MODEL: gpt-5.6-sol, reasoning=high, read-only sandbox, session 019f8843-57f2-7022-b2ad-552ce3d9e81b (62 investigation commands + forced final report after 10-min cap)

## Claude disk-arbitration of the four P1s (re-checked at HEAD before accepting)

- P1-1 KB retriever vs protocol: CONFIRMED. retrieval.py:100-101 scores primary=UNION(keywords,summary) while its own docstring and INDEX/comms-qa protocol say keywords-first-then-summary; tie returns first entry only (score > best_score), protocol requires opening BOTH. Impact = eval-harness replica can false-green behavior the skill forbids (runtime agent follows prose, so this is an eval-validity defect, not production misretrieval).
- P1-2 detector bypasses CJK refusal: CONFIRMED. detector.py imports only primitives (WORD_RE/TOKEN_RE/tokenize/count_words/split_paragraphs); zero segment() calls; CJK-dominant text is scored Clean instead of refused.
- P1-3 mutable state in shipped package: CONFIRMED. voice-onboard SKILL.md writes per-user profiles under _shared/voice-profiles/ inside the distributable tree; .gitignore excludes neither profiles nor learned-rules state.
- P1-4 fabrication gate blind to plain-language fabrications: CONFIRMED mechanically (gate = digit tokens + 2+ capitalized runs + corporate suffixes only; the three counterexample sentences match none). Nuance: limits are self-documented in run_draft_cases.py:271-288; the finding's real target is the 'highest-stakes check' framing in test_draft_cases.py.
- Corrections accepted: SECURITY-01 'verbatim HTML' overstated (ingest.py parses + strips script/style); DOCS-03 count is 46 files (37 md); voice-lookup 'verbatim copy' overstated (semantic drift, which strengthens the extraction case).

---

## 1. Refutation

| Claim | Result | Evidence / correction |
|---|---|---|
| CORRECTNESS-01 | **[HOLDS]** | `_CJK_RE` is duplicated in [aiws/text.py:59-63](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/aiws/text.py:59) and [stylometry.py:174-177](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/stylometry.py:174). Only `SENT_SPLIT` has a sync pin at [test_text_seam.py:157-176](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/test_text_seam.py:157); the 20% behavior is pinned separately at [test_text_seam.py:147-154](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/test_text_seam.py:147). |
| SECURITY-01 | **[OVERSTATED]** | The missing untrusted-data boundary holds: `comms-qa` treats KB content as authoritative at [comms-qa/SKILL.md:69-87](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-qa/SKILL.md:69). But “Confluence/Notion HTML verbatim” is false. Confluence HTML is parsed, with script/style discarded, at [ingest.py:137-214](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/aiws/kb/ingest.py:137); Notion input is markdown, not HTML, at [ingest.py:79-85](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/aiws/kb/ingest.py:79). |
| TEST-COVERAGE-01 | **[OVERSTATED]** | Router precedence is untested: contract at [SKILL.md:25-47](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/SKILL.md:25), while the manifest test checks only child frontmatter at [test_skill_manifests.py:18-56](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/test_skill_manifests.py:18). “Unlike every sub-skill” is unsupported; artifact discrimination is not equivalent to executing sub-skill routing behavior. |
| TEST-COVERAGE-02 | **[HOLDS]** | The repository itself documents the knife edge: only 3/8 passes; 2/8 and 4/8 fail at [calibration.py:5-12](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/calibration.py:5), asserted at [test_calibration.py:18-27](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/test_calibration.py:18). It is eval fragility, not “test coverage.” |
| TEST-COVERAGE-03 | **[HOLDS]** | Five criteria are specified at [comms-draft/SKILL.md:110-119](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:110) and manually copied into [run_draft_cases.py:49-54](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_draft_cases.py:49). No coupling mechanism was found. |
| TEST-COVERAGE-04 | **[HOLDS]** | Zero-overlap returns `None` at [retrieval.py:104-109](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/aiws/kb/retrieval.py:104). Smoke cases only compare a retrieved entry against a positive expected entry at [smoke_test.py:101-128](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/smoke_test.py:101). |
| DXTOOL-01 | **[HOLDS]** | Four manifests are documented at [docs/packaging.md:11-18](/Users/surahli/Documents/ai-writing-suite/docs/packaging.md:11), but the validator loads only three at [validate_packaging.py:48-53](/Users/surahli/Documents/ai-writing-suite/scripts/validate_packaging.py:48), omitting `.agents/plugins/marketplace.json`. No validator self-test was found. |
| TECHDEBT-01 | **[HOLDS]** | `.omx/` appears only in [.git/info/exclude:7](/Users/surahli/Documents/ai-writing-suite/.git/info/exclude:7); committed [.gitignore:1-8](/Users/surahli/Documents/ai-writing-suite/.gitignore:1) omits it. |
| DOCS-01 | **[HOLDS]** | `[Unreleased]` at [CHANGELOG.md:10-53](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/CHANGELOG.md:10) lacks the shipped PR/release-note presets at [scenario-presets.md:164](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:164) and [scenario-presets.md:200](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:200). |
| DOCS-02 | **[HOLDS]** | The banner limits its warning to packaging at [design-v1:1-6](/Users/surahli/Documents/ai-writing-suite/docs/design-ai-writing-suite-v1-2026-06-06.md:1), while the document still says QA/draft are v2 at [design-v1:107-141](/Users/surahli/Documents/ai-writing-suite/docs/design-ai-writing-suite-v1-2026-06-06.md:107) and [design-v1:182-203](/Users/surahli/Documents/ai-writing-suite/docs/design-ai-writing-suite-v1-2026-06-06.md:182). Current README says both ship in v1.1 at [README.md:96-117](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/README.md:96). |
| DOCS-03 | **[OVERSTATED]** | Filesystem enumeration produced **46** flat files, not 37; **37 are Markdown**. `596K` and absence of `README`/`INDEX` hold. Directory counts are not line-addressable. |
| DIRECTION-02 | **[OVERSTATED]** | A public corpus can supplement regression testing, but cannot substitute for independently labelled real-writer/L1/genre data. The fixture explicitly disclaims benchmark validity at [false_positives.json:2](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/false_positives.json:2); current tests merely enforce synthetic cohort shape at [test_false_positives.py:43-71](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/test_false_positives.py:43). |
| PERFORMANCE | **[UNVERIFIED]** | “No findings clear the bar” is a research-process assertion, not a repository invariant. No complete performance audit was finished before the stop instruction. |
| Lane 2 Strong — shared text seam | **[OVERSTATED]** | Duplication exists, but the file explicitly preserves separate calibrated consumer policies at [aiws/text.py:1-16](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/aiws/text.py:1). More seriously, `segment()` is not used by the detector; the detector imports only primitives at [detector.py:37-43](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/detector/detector.py:37). This is a bypass problem, not merely an abstraction problem. |
| Lane 2 Strong — voice lookup | **[OVERSTATED]** | It is not verbatim. Polish rejects the sample banner only in legacy fallback at [comms-polish/SKILL.md:106-110](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:106); draft rejects it in either location at [comms-draft/SKILL.md:63-67](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:63). The canonical rule says **any** carrying file is invalid at [voice-profile.md:71-79](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/voice-profile.md:71). Extraction is justified by semantic drift, not verbatim duplication. |

## 2. Missed

1. **[P1] The executable KB retriever contradicts the published protocol.**

   The skill requires keyword-first ranking and opening both tied entries at [comms-qa/SKILL.md:55-67](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-qa/SKILL.md:55). The implementation unions keyword and summary terms, then silently preserves only the first full tie at [retrieval.py:83-109](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/aiws/kb/retrieval.py:83).

   Minimal verified counterexample:

   ```text
   keyword.md: keywords={alpha}, summary={}
   summary.md: keywords={}, summary={alpha,beta}
   query: alpha beta
   actual: summary.md

   first.md and second.md: identical score
   actual: first.md only
   ```

   Thus the smoke harness can certify behavior the skill explicitly forbids.

2. **[P1] The CJK refusal seam is bypassed by the detector that produces scores.**

   `segment()` refuses input at ≥20% CJK at [aiws/text.py:110-120](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/aiws/text.py:110). The detector never calls it; it directly tokenizes and scores at [detector.py:106-123](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/detector/detector.py:106).

   Verified counterexample: repeated `界abcd` input yielded `segment = CJK / unsupported script / 0 words`, but detector returned `score=0`, `label=Clean`, `classification=HUMAN_ONLY`.

3. **[P1] Mutable personal state is stored inside the distributable package.**

   `voice-onboard` writes personal profiles under the shipped `_shared/` tree at [voice-onboard/SKILL.md:39-55](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:39) and [voice-onboard/SKILL.md:193-209](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:193). The same package ships maintainer-specific state at [learned-rules.md:105-124](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/learned-rules.md:105), whose age now mandates pausing users under [self-improvement.md:98-115](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/self-improvement.md:98). [.gitignore:1-8](/Users/surahli/Documents/ai-writing-suite/.gitignore:1) protects neither profile data nor learned state. This risks privacy leaks, cross-user contamination, write failures in plugin caches, and update-time data loss.

4. **[P1] The deterministic “no fabrication” gate cannot detect ordinary fabricated claims.**

   It recognizes numeric tokens and narrow capitalized-name shapes at [run_draft_cases.py:62-92](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_draft_cases.py:62), while admitting its limitations at [run_draft_cases.py:271-288](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_draft_cases.py:271). The broader semantic judge is advisory and skips offline at [run_draft_cases.py:529-540](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_draft_cases.py:529).

   Against an unrelated source, all three verified fabrications returned `[]`:

   - “The migration completed yesterday and customers were unaffected.”
   - “The rollout caused an outage and support handled every complaint.”
   - “Legal approved the policy.”

   Calling this the suite’s “highest-stakes check” at [test_draft_cases.py:64-66](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/test_draft_cases.py:64) is false confidence.

5. **[P2] Packaging validation omits the root router—the primary discovery surface.**

   Both validator and tests glob only child skills at [validate_packaging.py:95-117](/Users/surahli/Documents/ai-writing-suite/scripts/validate_packaging.py:95) and [test_skill_manifests.py:18-56](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/test_skill_manifests.py:18). The attempted root path at [test_skill_manifests.py:130-135](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/test_skill_manifests.py:130) resolves incorrectly and is silently skipped when nonexistent.

## 3. Plan challenge

Wrong priorities:

- CJK regex pinning is busywork until the scoring detector actually enforces CJK refusal.
- Router tests and voice extraction are useful but secondary to broken runtime/state boundaries.
- CHANGELOG, docs indexing, and `.omx/` ignore are housekeeping.
- A public corpus is not a substitute for the owner-gated corpus.
- Artifact preflight and `must_preserve` improve polish quality but do not repair false-green correctness gates.
- “Guard clause in all SKILL.md” invites another copy-drift surface. Define one shared untrusted-content contract and reference it from every ingestion/reading boundary.
- Voice extraction should remain, but the reason is observed behavioral divergence.
- Plugin registration is operationally important; it does not cure the package’s underlying mutable-state design.

**Single highest-leverage change:** separate immutable plugin assets from per-user state. Move voice profiles and learned rules to a user-owned state directory, define one resolver consumed by `voice-onboard`, `comms-polish`, and `comms-draft`, and ship no maintainer-specific live rule state.

This outranks the alternatives because it fixes privacy, install-cache writability, cross-user contamination, update durability, and the current forced-pause defect at once. Next priorities should be canonical KB retrieval semantics, detector CJK refusal, and a genuinely semantic fabrication gate.

## 4. Install topology

**Partially verified; core claim holds.**

- Plugin registrations exist at [config.toml:54-120](/Users/surahli/.codex/config.toml:54) and marketplaces at [config.toml:545-565](/Users/surahli/.codex/config.toml:545), with no `ai-writing-suite` registration.
- `/Users/surahli/.codex/plugins/cache/ai-writing-suite` exists and was empty when inspected.
- `/Users/surahli/.codex/skills/ai-writing-humanizer/SKILL.md` exists, is 85 lines, and was modified 2026-05-31.
- The additional claim that a particular 2026-07-21 session actually used that standalone skill is **UNVERIFIED**; no session-log proof was inspected.

**VERDICT:** Roughly two-thirds of the research survives directionally, but several “confirmed” claims contain factual errors, and it missed four P1 failures more consequential than most of its proposed P0 work.

**Three claims most likely wrong:**

1. “Confluence/Notion HTML is ingested verbatim.”
2. “`docs/` contains 37 flat files.”
3. “The voice-lookup protocol is copy-pasted verbatim.”

**Recommendation:** Fix the package/user-state boundary first, then make retrieval, CJK refusal, and fabrication claims executable and impossible to falsely green.