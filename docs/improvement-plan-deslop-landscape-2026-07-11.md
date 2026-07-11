# Improvement Plan — De-slop Landscape Research + Suite Audit

Date: 2026-07-11
Author: Claude (orchestrator) for surahli (product owner)
Status: **PLAN — awaiting product-owner triage; no code changes made**
Method: 11-agent research workflow (Sonnet subagents) — repo recon + 6 channel researchers
(GitHub, HN, Reddit, X, blogs/newsletters, skill ecosystems) → gap analysis + Autorefine-style
audit (D10: Three Gulfs / error analysis / skill-quality pass) → adversarial grounding critic
(spot-checked cited URLs and repo claims) + completeness critic.

## Coverage caveats (read before trusting the evidence)

- **Reddit and news.ycombinator.com were blocked at the network egress layer** in this
  session. Reddit findings are near-zero; HN findings were reconstructed from search
  snippets and secondary write-ups (rmoff.net, chyshkala.com). A follow-up pass from an
  unrestricted environment would strengthen those channels.
- **Direct x.com fetches 403'd 100% of the time.** The one X finding (Slopbeth) was
  date-confirmed by decoding the tweet's snowflake ID; other X-origin items could not be
  independently dated.
- Recency filter: items created/updated after **2026-05-01**. Items whose dates could not
  be confirmed are marked as such in the findings appendix and were down-weighted.
- Every opportunity below marked ✅ was verified by an adversarial critic that re-checked
  the cited URL **and** confirmed the gap actually exists in this repo (file/line-level
  spot checks). Items the critic killed are listed in "Rejected" with reasons.

---

## TL;DR

1. **Lexical de-slopping is now a crowded commodity.** stop-slop (13.6k★) proved the
   demand with six terse rules in one file; a dozen post-May-2026 competitors ship banned-word
   lists and 0-100 scores. The suite should not compete on catalog size.
2. **The suite's defensible edges are (a) eval rigor, (b) voice, (c) the pluggable KB** —
   and all three have verified holes. The eval harness never tests the judge on a FAIL case
   (all 13 fixtures are expected-PASS); comms-draft and voice-onboard have effectively zero
   behavioral eval coverage; there is no false-positive suite despite the catalog itself citing
   60-70%+ FP rates on non-native writers; and no tooling exists for the company-fork
   playbook drop-in that the whole v1 bet rests on.
3. **The research surfaced one genuinely new detection frontier:** document/narrative-shape
   tells. StoryScope (UMD + DeepMind) classifies human-vs-AI at 93.2% from structure alone,
   and the signal survives lexical de-slopping — "you cannot prose-edit your way out of a
   structural fingerprint." No category in `_shared/patterns/` operates at that altitude.
4. **The strongest external methodology find** is adewale/anti-slop-writing's eval
   engineering: tune/holdout splits per suite, a first-class adversarial false-positive suite,
   quoted-evidence judge protocol, and paired-bootstrap statistical gating for small-N evals.
   Directly portable to `evals/`.
5. Recommended sequence: **harden evals first** (Phase 1), then catalog/voice differentiation,
   then workflow/product, then packaging/distribution. Eval hardening comes first because
   every later change is supposed to be eval-gated by D10 — right now the gate itself is
   under-tested.

---

## Landscape highlights (what post-May-2026 tools actually do)

| Tool / source | What it does that we don't | Evidence |
| --- | --- | --- |
| [harshaneel/humanize](https://github.com/harshaneel/humanize) (209★) | 9 humanization levers with numeric thresholds (burstiness ≥1 sentence ≤6 words per 150; ≤1 em dash/300 words); "RLHF voice stripping" framing; 50+ cited papers | May 26–Jul 10 commits |
| [theclaymethod/unslop](https://github.com/theclaymethod/unslop) | 3-layer deterministic scanning (phrase/structure/**silhouette** — outline-following detection, 12/12 AI, 0/8 human on holdout); 313 contextually-gated phrases; 440-case eval CI | Jul 7 |
| [adewale/anti-slop-writing](https://github.com/adewale/anti-slop-writing) | 5 eval suites each split tune/holdout; **adversarial FP suite as first-class category**; quoted-evidence judge protocol; paired-bootstrap 95% CI gating for N<30 | v0.1.0 Jun 11 |
| [yzhao062/agent-style](https://github.com/yzhao062/agent-style) | 21 rules split **canonical (Orwell/Strunk/Pinker/Gopen-Swan) vs field-observed LLM tells**; 4-level severity mapped to enforcement mechanism | thru Jun 13 |
| [tbhb/vale-ai-tells](https://github.com/tbhb/vale-ai-tells) (41★) | 63 deterministic Vale rules with a documented "linter-catchable vs needs-LLM" split | v1.21.2 Jul 9 |
| [StoryScope (arXiv 2604.03136)](https://arxiv.org/pdf/2604.03136) | Narrative-structure features alone → 93.2% human-vs-AI accuracy; survives adversarial lexical cleanup; per-model fingerprints (Claude = flat escalation) | press wave Jul 5 |
| [realrossmanngroup/no_ai_slop_writing_rules](https://github.com/realrossmanngroup/no_ai_slop_writing_rules) | Voice profile derived from **513k-word corpus statistics** (testable-number density, sentence-length variance, claim→proof structure) — not adjectives | May 25–30 |
| [blader/humanizer update](https://github.com/blader/humanizer) | v2.6–2.8 added voice calibration from user samples + **diff-anchored tell detection** (tells visible only when diffing against the user's own prior drafts) | May 27–Jul 7 |
| [Slopbeth (@synopsi)](https://x.com/synopsi/status/2067976938095063063) | "Most humanizers turn AI slop into cleaner AI slop." Public 88-case benchmark vs named competitors; names failure modes: fake clarity, invented mechanisms, cosmetic swaps | Jun 19 (snowflake-confirmed) |
| [AgriciDaniel/claude-blog](https://github.com/AgriciDaniel/claude-blog) (1.3k★) | **Blocking** delivery gate (score <90 cannot ship; 3 autonomous retries then escalate) vs advisory scores | May 20 |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) (13.6k★) | Minimalism benchmark: 6 imperative rules, 8-item quick diagnostic — the "smallest viable version" that captured the market | trending late May |
| [gradpilot FP-rate comparison](https://gradpilot.com/news/ai-detector-false-positive-rates-compared) | 61.22% of TOEFL essays by non-native students misflagged as AI; names the mechanism (perplexity ∝ L1 fluency) | May 19, upd. Jun 19 |
| HN community signal ([rmoff.net](https://www.rmoff.net/2026/05/06/ai-slop-is-killing-online-communities/), dontquotetheai.com — 511 & 161 pts) | Reader objection is **"AI-pasted" vs "AI-assisted"** — the missing human editing pass, not AI involvement per se. Framing + reputational-risk note for README | May 6 / May 23 |

Full 35-finding appendix at the bottom.

---

## Verified improvement opportunities

Priority = product-owner-facing recommendation combining verified impact, effort, and
strategic fit (evals/voice/KB moat first). Impact values are the **critic-corrected** ones.

### P1 — Eval hardening (make the D10 gate real)

| # | Opportunity | Impact | Effort | Verified gap |
| --- | --- | --- | --- | --- |
| 1 | **Gold-FAIL prose fixtures.** Add 3-5 `expected_verdict: FAIL` before/after fixtures (fabricated number, over-corrected overstepping, live payoff_clear stub) so the judge is tested on discrimination, not just agreement. Keep them in a separate file if needed to preserve the 30-40% calibration band. | High | M | All 13 fixtures.json entries are PASS; FAIL paths only exist as canned strings in test_fixtures.py. ✅ |
| 2 | **Adversarial false-positive suite.** Holdout of clean human prose incl. non-native-English and stylistically-unusual samples the judge/detector must NOT flag; report a should-not-trigger pass rate in run_all.sh. Model: adewale's 18-tune/11-holdout adversarial.json. | High | M | rhythm-stylometric.md:94-100 cites the 60-70% FP stats as advisory prose; zero FP fixtures exist. ✅ (absorbs duplicate O21) |
| 3 | **comms-draft fixtures.** Exercise the 5-step workflow end to end: missing-fact brief must yield `[NEEDS:]` not invention; thin brief triggers the ask-2-3-questions branch; acceptance criteria match the 5 named dimensions. | High | M | Nothing under evals/ references comms-draft at all — the newest v1.1 capability has zero coverage. ✅ |
| 4 | **voice-onboard extraction eval.** Synthetic 3-5-sample corpus with engineered traits (word used 4x vs 2x, mixed genres); assert the profile includes the 4x trait, excludes the 2x trait (tests the "3+ occurrences" rule), and doesn't average across genres. | High | L | test_voice_contract.py is a header-presence check only; its docstring defers quality to "Phase 2b". ✅ |
| 5 | **Quoted-evidence judge protocol + cross-family check.** Every judge PASS/FAIL must cite a quoted snippet; warn when judge model shares a family with the rewriting model. | Medium | S | Not present in judge.py/rubric.md; adewale's judge-protocol.md verified as the model. ✅ |
| 6 | **O2 (presumed-misconception strawman) fixture.** The one overstepping sub-type with zero dedicated example. | Low | S | Fixtures map to O1/O3/O4/payoff only. ✅ |
| 7 | **Statistical gating for growing eval scale** *(completeness-critic addition, unverified)*: adopt adewale's paired-bootstrap 95% CI + sign-flip permutation test — matters more as items 1-4 multiply the number of small-N suites. | Medium | M | New candidate — triage. |
| 8 | **Scheduled/dispatch judge run in CI.** 3 of 8 catalog categories are detector-blind and judge-only; add a `workflow_dispatch`/cron job running `run_fixtures.py --judge` with a repo secret, posting agreement as an artifact — without breaking the deliberate key-free default CI. | Medium | M | test_run_all_and_ci_never_invoke_the_judge asserts the judge is absent from CI by design; nothing runs it on a cadence. ✅ |

### P2 — Catalog & detection differentiation

| # | Opportunity | Impact | Effort | Verified gap |
| --- | --- | --- | --- | --- |
| 9 | **Document/narrative-shape tell category** (judge-only, never-gate-CI, parallel to overstepping's design): over-explained themes, tidy single-track resolution, flat escalation, absent ambiguity. Wire into comms-draft's structural planning, not just line editing. | High | M | All 8 existing categories are sentence/paragraph-level (00-index.md confirmed); StoryScope evidence verified. ✅ |
| 10 | **Severity + enforcement-tier metadata on every catalog entry** (Critical/High/Medium/Low × mechanical/statistical/judge-only/human-only); use the tier to drive which entries `detector/patterns.py` must implement. | Medium | M | lexical-tells.md has a Tier 1/2/3 detection-confidence scheme but nothing catalog-wide; agent-style's scheme verified. ✅ |
| 11 | **Detector↔catalog coverage matrix.** Extend test_catalog_sync.py beyond the Tier-1 lexical table: every pattern id across all 8 files maps to a detector rule id or an explicit "judge-only" marker. Natural companion to #10. | Medium | M | test_catalog_sync.py parses only the replace-on-sight table vs the TIER1 dict. ✅ |
| 12 | **Small-pattern bundle (one ticket):** parataxis (rhythm-stylometric), "fake hedging" — intensifiers disguised as softeners (split from hedging-filler), and "manufactured personality" — forced quirkiness/false relatability (communication-artifacts). | Low | S | First two critic-verified as absent; third from completeness critic. Bundled per critic advice. ✅ |
| 13 | **Omniscience / mediated-speech-act null-hypothesis check** for comms-draft + overstepping-presumption.md: would this author plausibly know this (cross-domain breadth)? Does the draft reference meetings/prior messages like a real participant? | Medium | S | O1-O4 has no null-hypothesis mechanism; lmmx gist concepts verified. ✅ |
| 14 | **Multilingual catalog architecture** *(completeness-critic addition, unverified)*: split patterns into language-universal (structural/rhythm/hedging shape) vs language-specific phrase lists — prerequisite for any non-English company fork; EN+RU and EN+ID competitors demonstrate the split. | — | — | New candidate — triage. |

### P3 — Voice (the differentiator)

| # | Opportunity | Impact | Effort | Verified gap |
| --- | --- | --- | --- | --- |
| 15 | **Quantitative stylometric fingerprint in voice-profile.md**: optional deterministic pass (char 3-grams, function-word deltas vs generic baseline, sentence-length variance) computed from the ≥3 samples, stored as measured numbers alongside the 10 qualitative dimensions — gives test_voice_contract.py real numbers to assert. | High | M | Two independent precedents verified (unslop silhouette-layer validation; rossmann 513k-word corpus stats). ✅ |
| 16 | **Edit-based voice-profile updater** via the existing learned-rules loop: treat the delta between AI draft and the user's final edit as a voice signal; propose as a learned-rules.md candidate scoped to voice-profile.md. No new machinery. | Medium | M | self-improvement.md loop verified as the right slot; LR-001 still `proposed` since 2026-06-14. ✅ |
| 17 | **Voice drift / staleness signal** *(completeness-critic addition, unverified)*: age/draft-count-based re-onboard prompt + blader's diff-anchored detection (tells visible only against the user's own prior drafts). | — | — | New candidate — triage. |
| 18 | **"Don't over-smooth" guardrail** *(completeness-critic addition, unverified)*: polish itself erases voice (Axios framing); add a checkable guardrail/eval dimension preserving irregular rhythm and personal register — distinct from the fact-fidelity guardrail. | — | — | New candidate — triage. |

### P4 — Workflow & product

| # | Opportunity | Impact | Effort | Verified gap |
| --- | --- | --- | --- | --- |
| 19 | **Audit-report output contract for comms-polish detect/review (Ogilvy #1).** Fixed template: one-line biggest problem → findings under named severity tiers (Critical/Moderate/Minor), each = quoted snippet → tell name → why → fix → closing "reads well" note. | High | M | comms-polish/SKILL.md:245 is still the vague "grouped by severity" wording; the Ogilvy doc tagged this strong-recommend and it remains unbuilt. (Not critic-verdicted — evidence is repo-internal and was verified by the audit agent at file:line.) |
| 20 | **Blocking self-scan gate for comms-draft** — bounded retry. Critic caveat: unlike claude-blog's background CI, retries here burn live conversation turns; recommend **1 bounded retry or opt-in**, not 3. | Medium | M | comms-draft SKILL.md steps 5-6 verified advisory-only. ✅ |
| 21 | **comms-qa retrieval fixtures** — scoped to what smoke_test.py doesn't cover: zero-match refusal path, multi-part decomposition, one-hop Related-entries traversal. (Critic: disambiguation/near-miss cases already covered by smoke_test's 5 cases.) | Medium | M | kb_lint.py checks structure only; refusal/decomposition/one-hop untested. ✅ |
| 22 | **Deterministic pre-filter fast path** *(completeness-critic addition, unverified)*: cheap non-LLM triage (stop-slop's 8-item checklist / vale-style rules) before invoking the full judge pipeline on obviously-clean text; pairs with #23. | — | — | New candidate — triage. |
| 23 | **JSON/machine-readable output mode** for detect/review *(completeness-critic addition, unverified)*: dual human+JSON report (kill-ai-slop pattern) — enables CI gating and tooling. | — | — | New candidate — triage. |
| 24 | **Truth/voice guardrail — name the failure modes.** Most substance already shipped in final-pass-checklist.md's L1 mechanical floor; remaining delta is naming Slopbeth's four failure modes (fake clarity, invented mechanisms, cosmetic swaps, unnecessary rewrites of good sentences) in rewrite/edit modes and the judge rubric. | Low-Med | S | L1 floor verified as existing prior art; scope reduced accordingly. ✅ |

### P5 — Packaging, adoption, distribution

| # | Opportunity | Impact | Effort | Verified gap |
| --- | --- | --- | --- | --- |
| 25 | **KB/playbook ingestion tooling for company forks** *(completeness-critic addition — arguably the highest-stakes item here)*: a validator that a dropped-in playbook satisfies the markdown+INDEX contract comms-qa depends on, a Confluence/Notion/GDocs→KB conversion helper, and an onboarding checklist. The entire v1 bet rests on this step being near-zero-effort; today it's untooled. | — | — | New candidate — triage. |
| 26 | **Cut a tagged v1.1.0 release.** plugin.json still says 1.0.0 while [Unreleased] has accumulated ~120 lines of shipped features (comms-qa, comms-draft, overstepping, payoff_clear). | Medium | S | Verified against CHANGELOG.md + docs/packaging.md. ✅ |
| 27 | **Re-run the RovoDev smoke test** against all four current sub-skills (baseline predates comms-qa/comms-draft/overstepping/payoff_clear; a path-resolution regression already occurred on that surface once). | Medium | S | Router table verified; only verification on record is 2026-06-08. ✅ |
| 28 | **Packaging-hygiene bundle (one ticket):** audit frontmatter against the now-formalized Agent Skills open standard (anthropics/skills, June 2026) + revisit the Cursor install path (manual folder copy) against single-file-paste and generator-CLI models from jalaalrd / agent-style. | Very low | S | Bundled per critic advice; note: "writing" is NOT a top-level category in anthropics/skills (critic corrected that claim). ✅ |
| 29 | **Distribution & positioning** *(completeness-critic addition, unverified)*: traction among near-identical tools varies 1000x (stop-slop 13.6k★ vs single digits). Concrete tactics observed: public head-to-head benchmark vs named competitors (Slopbeth), published cross-model violation-reduction numbers (agent-style), companion site (kill-ai-slop). Also adopt the "AI-assisted vs AI-pasted" framing in the README — it both positions the suite and addresses the reputational risk (HN communities banning AI content). | — | — | New candidate — triage. |
| 30 | **Router/description seam fix:** add one disambiguating clause each to comms-polish and comms-draft frontmatter descriptions for mixed "polish this AND add a section" requests. | Low | S | Both descriptions verified as quoted; seam is real. ✅ |
| 31 | **Exercise the self-improvement lifecycle once, end to end:** take LR-001 (proposed since 2026-06-14) through Layer-3 eval → active → one manual graduation, to prove the D10 loop actually runs. | Low | S | learned-rules.md has exactly one entry, never promoted; GRADUATION step never exercised. ✅ |

### Rejected by the adversarial critic (do not build)

| Proposed | Why killed |
| --- | --- |
| Readability score (Flesch/Gunning-Fog) in comms-polish | **Contradicts the documented Ogilvy #5 decision** — that doc explicitly argues against publishing a Flesch-Kincaid score as a knob or gate. |
| Cluster-sensitivity scoring for common-word tells | **Already implemented** — detector.py's tier2_clusters requires 2+ distinct hits per paragraph; lexical-tells.md states the cluster principle in its opening line. |
| Decorative-vs-genuine emoji rule | **Already shipped** as punctuation-formatting.md F3, including the genuine-social-use carve-out. |
| Periodic passive-voice re-validation | The suite **carries no passive-voice tell** (grep of all 8 files: zero mentions); premise doesn't apply. Generic quarterly re-validation folded into #31's self-improvement hygiene if desired. |
| Standalone non-native-English FP eval | Exact duplicate of #2; merged. |

---

## Suggested sequencing

1. **Now (small, unblocked, high leverage):** #1, #2, #5, #6 (eval hardening core), #26, #30 — mostly S/M effort, all critic-verified, no design ambiguity.
2. **Next:** #3, #4 (close the zero-coverage holes on the newest capabilities), #19 (Ogilvy #1 output contract — already strong-recommended twice), #9 (narrative-shape category — the new frontier).
3. **Then:** voice track (#15, #16) and catalog metadata track (#10, #11) in parallel.
4. **Product-owner decisions needed before build:** #20 (retry-cost tradeoff), #25 (ingestion tooling scope — company-facing), #29 (whether OSS traction is a goal), #14/#17/#18/#22/#23 (unverified completeness-critic candidates — worth a verification pass like the one that vetted the main list).

Per CLAUDE.md working style, each build item should land as feature-branch → PR with
before/after eval evidence; anything touching the catalog or judge should demonstrate the
30-40% calibration band still holds.

---

## Appendix — research provenance

- Workflow: 11 Sonnet agents, 442 tool calls, ~965k subagent tokens; run id `wf_b7f58bb5-a1a`.
- Findings corpus: 35 deduplicated items (23 GitHub repos/gists, 2 HN threads, 1 X thread,
  1 arXiv paper, 8 blog/press/newsletter pieces). 5 items carry unconfirmed dates and were
  down-weighted, not excluded.
- Verification: grounding critic spot-checked the most load-bearing URLs via live fetch and
  re-checked every "the repo lacks X" claim against the working tree at file/line level;
  completeness critic reviewed findings-vs-opportunities for dropped signal.
- Channel notes: Reddit egress-blocked (near-zero yield); HN egress-blocked (reconstructed
  via secondary sources); X 403'd on direct fetch (one snowflake-confirmed thread).

### Full findings list

| Source | Date | Note |
| --- | --- | --- |
| [harshaneel/humanize](https://github.com/harshaneel/humanize) | May 26–Jul 10 | 9 levers, numeric thresholds, 209★ |
| [theclaymethod/unslop](https://github.com/theclaymethod/unslop) | Jul 7 | 3-layer scanner, silhouette detection, 440-case evals |
| [Aboudjem/humanizer-skill](https://github.com/Aboudjem/humanizer-skill) | May 13/30 update | 43 patterns incl. "emerging" tier (UTM leaks, treadmill effects) |
| [tbhb/vale-ai-tells](https://github.com/tbhb/vale-ai-tells) | Jul 9 | 63 Vale rules; linter-vs-LLM split |
| [realrossmanngroup/no_ai_slop_writing_rules](https://github.com/realrossmanngroup/no_ai_slop_writing_rules) | May 25–30 | corpus-statistics voice profile |
| [tuwulalo/ai-slop-cleaner-en-ru](https://github.com/tuwulalo/ai-slop-cleaner-en-ru) | Jun 13–18 | bilingual EN+RU; calibrated confidence on short text |
| [timolabs-ai/claude-humanize-skill](https://github.com/timolabs-ai/claude-humanize-skill) | May 12–Jun 1 | 5 editorial layers |
| [blader/humanizer](https://github.com/blader/humanizer) v2.6–2.8 | May 27–Jul 7 | voice calibration; diff-anchored tells |
| [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) v3.15 | thru Jul 8 | 5 new named patterns (recap-flattery, vague third-party validation, speculative-scenario-opener, bold list-label periods, wall-of-text) |
| [aplaceforallmystuff/claude-voice-editor](https://github.com/aplaceforallmystuff/claude-voice-editor) + slop-detector + analyzer | recency unconfirmed | VOICE.md 6-dimension schema; tiered forbidden list; 3-tier slop score |
| [yetone/kill-ai-slop](https://github.com/yetone/kill-ai-slop) | Jul 10 | signal/rationale/fix entry format; dual human+JSON reports (UI-slop domain) |
| [matsuikentaro1/humanizer_academic](https://github.com/matsuikentaro1/humanizer_academic) | thru Jul 7 | live engine-vs-fuel fork example |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) | trending late May | 13.6k★ minimalism benchmark |
| [StoryScope, arXiv 2604.03136](https://arxiv.org/pdf/2604.03136) | press Jul 5 | 93.2% structural classification |
| [HN: AI slop is killing online communities](https://news.ycombinator.com/item?id=48053203) | May 6 | 511 pts; moderator burden |
| [HN: dontquotetheai.com](https://news.ycombinator.com/item?id=48242648) | May 23 | 161 pts; AI-pasted vs AI-assisted |
| [aiprompthackers voice prompts](https://www.aiprompthackers.com/p/how-to-get-ai-to-write-in-your-voice) | ~mid-Jun (est.) | edit-based profile updater; <200-word instructional profiles |
| [gradpilot FP rates](https://gradpilot.com/news/ai-detector-false-positive-rates-compared) | May 19/Jun 19 | ESL bias mechanism |
| [jalaalrd/anti-ai-slop-writing](https://github.com/jalaalrd/anti-ai-slop-writing) | Apr 18 commit (borderline) | single-file <500-line portability; parataxis rule |
| [adenaufal/anti-slop-writing](https://github.com/adenaufal/anti-slop-writing) | Jul 6 | EN+ID locale-specific tells; claims passive-voice reversal |
| [BioInfo/slopless](https://github.com/BioInfo/slopless) | unconfirmed | one voice file governing prose + agent chatter |
| [AgriciDaniel/claude-blog](https://github.com/AgriciDaniel/claude-blog) | May 20 | blocking 5-gate delivery contract, 1.3k★ |
| [haowjy/creative-writing-skills](https://github.com/haowjy/creative-writing-skills) | Jul 9 | style refs stored in kb/ tree; reader-sim critique agents, 312★ |
| [Slopbeth thread + repo](https://x.com/synopsi/status/2067976938095063063) | Jun 19 | public benchmark; named rewrite failure modes |
| [Stephen Turner deslop](https://blog.stephenturner.us/p/deslop) | unconfirmed | stop-slop rubric forked for scientific writing |
| [Ruben Hassid anti-ai-writing-style.md](https://substack.com/@ruben/note/c-250465609) | unconfirmed | mandatory pre-output self-audit framing |
| [adewale/anti-slop-writing](https://github.com/adewale/anti-slop-writing) | Jun 11 | tune/holdout × 5 suites; adversarial FP suite; bootstrap gating |
| [lmmx AI-tells rubric gist](https://gist.github.com/lmmx/d91de290ea4e6d9631e32c2dd43da413) | Jun 18 | null-hypothesis testing; omniscience problem; fake hedging |
| [yzhao062/agent-style](https://github.com/yzhao062/agent-style) (+ RULES.md) | thru Jun 13 | canonical vs field-observed split; severity→enforcement mapping |
| [Axios: AI reshaping writing](https://www.axios.com/2026/05/02/ai-changing-writing-speaking) | May 2 | over-smoothing itself erases voice |
| [humanizerai/agent-skills](https://github.com/humanizerai/agent-skills) | unconfirmed | 4-formula readability; intensity tiers |
| [anthropics/skills open standard](https://github.com/anthropics/skills) | Jun 2026 | SKILL.md as cross-vendor standard, ~160k★ |
