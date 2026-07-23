# Systematic Improvement Plan — ai-writing-suite (2026-07-21)

**Status: PLAN ONLY — nothing implemented. Owner approval required before any item is built.**

VERIFIED_AGAINST: `docs/genre-presets-pr-release-note` @ `f46ce6e` (docs-only ahead of main merge-base `357f645`)

## Methodology & evidence trail

Four independent evidence lanes, cross-checked:

| Lane | Method | Key artifacts |
|---|---|---|
| 1. External research (STORM) | Workflow `wf_4ad47ae9-6f1`: 6 Sonnet readers (5 repos + local suite) → 5 Opus personas → contradiction map → synthesis → adversarial peer review (reliability **78/100**) | Session transcripts (ephemeral); plan items below |
| 2. Codebase audit (/improve protocol) | Workflow `wf_441c9f33-e33`: 4 Sonnet audit clusters → per-finding Opus adversarial verify (15 raw → **13 confirmed, 2 rejected**) | Findings below |
| 3. Codex-session feedback review | Sonnet Explore agent: verified Codex's travel-agent evidence, comms-polish A–H coverage matrix, install topology | Summarized below |
| 4. Codex adversarial review (gpt-5.6-sol) | 62-command investigation + forced report; ~2/3 of lanes 1–3 survived; **4 new P1s**, all disk-arbitrated at HEAD | `reviews/2026-07-21-codex-adversarial-research-review.md` |

External repos studied (licenses checked): plannotator/write-better (MIT), jpcaparas better-writing (**no license declared — see D5**), nihe0909/zh-humanizer-literary (MIT), KKKKhazix/khazix-writer (MIT, partially absorbed June PR #4), nashsu/Viral_Writer_Skill (MIT). Dedup baseline: 8 techniques already absorbed in June engine-polish.

---

## Tier 0 — Correctness & contract defects (from Codex adversarial + audit; fix before feature work)

These are defects in what the suite *claims* vs what it *does*. Codex's priority challenge: feature work on top of false-green gates compounds the problem.

### T0-1. Separate package assets from per-user state ★ Codex's single-highest-leverage change
- **Defect:** voice-onboard writes personal voice profiles under the shipped `_shared/voice-profiles/` tree (`skills/voice-onboard/SKILL.md:39-55`); `_shared/learned-rules.md` ships maintainer-specific live state; `.gitignore` protects neither. Risks: privacy leak on publish, plugin-cache write failures, cross-user contamination, update-time data loss.
- **Fix shape:** one user-state resolver (env var / `~/.aiws/` fallback) consumed by voice-onboard, comms-polish, comms-draft; ship no live maintainer state.
- **Effort:** M–L | **Eval:** packaging validation asserts no profile/learned-state files inside the distributable tree; existing 38% calibration band untouched.

### T0-2. Make eval-harness KB retrieval match the published protocol
- **Defect (P1, arbitrated):** `aiws/kb/retrieval.py:83-109` scores primary = union(keywords, summary) and silently keeps only the first full tie; INDEX.md + `comms-qa/SKILL.md:55-67` require keywords-first, then summary, and *open both* on a genuine tie. The harness replica can certify behavior the skill forbids (eval-validity defect; runtime agents follow the prose).
- **Fix shape:** re-implement scoring as keywords-primary/summary-tiebreak; return tie *sets*; add the two Codex counterexamples as regression tests. INDEX semantics stay FROZEN — this fixes the replica, not the protocol.
- **Effort:** S–M | **Eval:** the counterexamples are the tests (keyword-entry must beat summary-entry; full tie must surface both).

### T0-3. Route the detector through the CJK refusal seam
- **Defect (P1, arbitrated):** `aiws/text.py:110-120` refuses ≥20% CJK input, but `evals/detector/detector.py` imports only primitives and never calls `segment()` — CJK-dominant text is scored `Clean/HUMAN_ONLY` instead of refused.
- **Fix shape:** detector calls `segment()` (or the refusal gate) first; refusal surfaces as unsupported-script, never a score.
- **Effort:** S–M | **Eval:** Codex's repro (`界abcd` repeated) as a regression test; calibration band + (18,5) specificity cohorts must not move.
- **Sequencing note:** audit finding CORRECTNESS-01 (CJK regex sync-pin) is *deferred behind this* — pinning a seam the scoring path bypasses is busywork (Codex's correction, accepted).

### T0-4. Make the fabrication gate honest about its coverage
- **Defect (P1, arbitrated):** the deterministic no-fabrication gate (`run_draft_cases.py:62-92`) only catches digit tokens + capitalized-run names; plain-language fabrications ("Legal approved the policy.") return `[]`, while `test_draft_cases.py:64-66` calls it the "highest-stakes check".
- **Fix shape (two options for owner):** (a) re-label the gate's claim to its true scope + add the three Codex counterexamples as documented known-misses; (b) additionally add a claim-verb candidate class (approved/completed/caused/confirmed + object) to the deterministic gate. The semantic judge stays advisory/opt-in either way.
- **Effort:** S (a) / M (a+b) | **Eval:** counterexamples become gold-FAIL when (b) is chosen.

### T0-5. Calibration denominator fragility (audit TEST-COVERAGE-02, Codex re-framed)
- **Defect:** n=8 fixtures leaves exactly one passing outcome (3/8) inside the 30–40% band — an eval-fragility issue, not coverage. Any fixture add/remove breaks the band's meaning.
- **Fix shape:** grow the fixture set toward n≥13 (blocked on owner's enterprise drafts — see P3 eval upgrade) or widen band arithmetic consciously with a versioned measurement-policy note. No silent edits.
- **Effort:** S (decision + doc) | gated on real-corpus availability.

---

## Tier 1 — Research-driven engine upgrades (STORM P0/P1, peer-review caveats applied)

### T1-1. VO-DIVERGENCE: self-report-vs-corpus divergence loop (voice-onboard) — STORM P0
Elicit the author's *stated* voice before extraction, then surface every contradiction against the measured fingerprint; measured evidence outranks self-report **at extraction time only** (rewrite time keeps the C3 voice-wins ruling). Peer-review caveats to honor: anchoring risk (elicit-first may bias extraction — consider blind-first ordering), and the "authors misjudge their own idiolect" premise is plausible-but-ungrounded — frame as hypothesis, not fact. Effort M. Eval: planted-false self-report in `voice_corpus.json` + `self_report_divergence` mutant family (must flag, not silently adopt; check must be semantic, not substring-gameable).

### T1-2. VO-ANCHORS, scoped to the true delta (voice-onboard) — STORM P0, dedup-corrected
Peer review: verbatim exemplars already exist (`> Evidence:` lines per dimension). The net-new part: 3 anchor lines each *tagged with the single habit it proves*, decoupled from the 10 dimensions, usable by comms-polish as fidelity anchors. Effort S–M (reduced). Eval: `anchor_provenance` mutant — anchor must be a whitespace-normalized verbatim substring of a declared sample. **Attribution: jpcaparas better-writing → blocked on D5 (license).**

### T1-3. PRECEDENCE-DOC, scoped (\_shared) — STORM P0, dedup-corrected
One short `_shared` policy file stating stage-scoped precedence: extraction → corpus > self-report (new); rewrite → voice profile > catalog (restates the existing C3 ruling, cited not re-invented). Codex's shape applies: **one shared contract file, referenced everywhere — never copy the rule into each SKILL.md** (avoids a new copy-drift surface). Effort S. Eval: doc-lint referencing + VO-DIVERGENCE/C3 fixtures stay green.

### T1-4. Shared untrusted-content contract (all sub-skills) — SECURITY-01, Codex-corrected shape
One `_shared` contract: ingested drafts, KB entries, and voice samples are data to analyze/quote, never instructions to follow; every ingestion/reading boundary references it. (Codex correction accepted: kb_ingest already parses + strips script/style — the gap is the *instruction-following* boundary, not raw HTML.) Effort S. Eval: doc-lint presence + one adversarial fixture (KB entry containing an instruction; comms-qa must quote, not obey).

### T1-5. FIDELITY-FIXTURES: rewrite-fidelity gold-FAIL lane (evals) — STORM P1
Gold-FAIL judge fixtures for failures the detector can't see: causal-direction flip, uncertainty→confidence promotion, voice-anchor-stripped rewrites. Excluded from the naive-baseline calibration denominator so the 38% band holds. Effort M. **Attribution: partly jpcaparas → D5.**

### T1-6. EMDASH-RELATION: relation-aware punctuation replacement (comms-polish) — STORM P1
Replace the *relationship* the em-dash expressed (break→period, apposition→comma/parens, causal turn→colon), not a flat character swap. Rejected the outright em-dash ban (conflicts with voice retention + C3). Effort S. Eval: one fidelity fixture where the flat swap misleads and the relation-aware swap passes.

### T1-7. Artifact-aware edit lane for comms-polish (Codex-session feedback A/D/G/H)
New `references/artifact-preflight.md`: trace visible text to its durable source (static/template/generated/JS-rendered/sidecar/deploy), classify visible/expandable/hidden/generated, hotspot-first protocol (inspect named component → trace → fix source → re-verify), must-keep inventory as acceptance criteria, edit-summary + stop conditions. Plain markdown/email keeps the lightweight path. Effort M. Eval: `must_preserve` fact-preservation capability (below) covers the testable slice.

### T1-8. `must_preserve` fact-preservation eval capability (evals) — Codex-session feedback E, the one clean stdlib fit
Extend `fixtures.json` with `must_preserve: [...]`; regex-extract numbers/dates/URLs/labels and diff before/after deterministically (same pattern as the detector). Effort S–M. The other five artifact-eval scenarios need browser/CSS infra → advisory only, never in `run_all.sh` fail-fast (D2).

---

## Tier 2 — Structural & hygiene (audit + architecture, verified)

| Item | Source | Effort |
|---|---|---|
| T2-1 Voice-lookup extraction to `_shared/voice-lookup.md` — justified by **semantic drift** between comms-polish:106-110 and comms-draft:63-67 vs the canonical rule (Codex correction: not verbatim duplication; drift makes it *more* urgent) | Arch #2 + Codex | S–M |
| T2-2 CATALOG-DETECTOR-BIND: two-way totality test catalog-id ↔ detector_type | Arch #3 / STORM P1 | M |
| T2-3 Router behavioral tests (scoped: routing decision fixtures; "unlike every sub-skill" was overstated) | Audit TC-01 | M |
| T2-4 retrieve() zero-overlap negative tests | Audit TC-04 | S |
| T2-5 comms-draft acceptance-criteria coupling test (SKILL.md prose ↔ eval constants) | Audit TC-03 | S |
| T2-6 Packaging validator: add the 4th manifest + root-router check + self-test | Audit DXTOOL-01 + Codex P2 | S |
| T2-7 CJK regex sync-pin (pattern only; threshold already behaviorally pinned) — **after T0-3** | Audit CORRECTNESS-01 | S |
| T2-8 CHANGELOG entry for genre presets; `.omx/` → committed .gitignore; docs/ index (46 files, 37 md — Codex-corrected count) with current/historical split; design-doc banner covers v1/v2 scope staleness | Audit DOCS-01/02/03, TECHDEBT-01 | S each |
| T2-9 TEXTSEAM-HONESTY: deepen `aiws/text.py` (route consumers through `segment()`/one interface) or explicitly mark it scaffolding — decide after T0-3 lands | Arch #1 / STORM P2 | M |
| T2-10 VO-FUNCTION-LEXICON, VO-DONT-INSTEAD, VO-THRESHOLDS, PRESERVATION-LADDER, SCALE-DIAGNOSIS | STORM P1/P2 | M–L each |

---

## Owner-gated decisions (nothing proceeds without a ruling)

- **D1 — Density budgets** (Codex-session ask C): conflicts with `final-pass-checklist.md` "never a hard length target". Adopt as *artifact-lane-only* budgets, reject globally, or extend the C3-style ruling ledger. Recommendation: artifact-lane-only.
- **D2 — Rendered verification placement**: runtime advisory guidance in the artifact lane only; never a `run_all.sh` gate (stdlib-only CI stays key-free). Recommendation: confirm advisory.
- **D3 — Stale `~/.codex/skills/ai-writing-humanizer/`**: retire, or convert to a 5-line redirect stub pointing at the suite. It is what Codex sessions actually discover today. (Codex marked "the 2026-07-21 session used it" UNVERIFIED; the run-receipt lines 29/129 name it — lane-3 evidence stands.)
- **D4 — Codex plugin registration**: suite is NOT registered in `~/.codex/config.toml` (empty plugin cache since Jun 7). Fix the install, and resolve the near-identical description collision with the old humanizer before both become discoverable. Verify with `codex plugin list`, not filesystem-only.
- **D5 — jpcaparas better-writing has no declared license**: items T1-2, T1-5 (partly), and the edit-freedom ladder draw on it. Options: seek license clarification, re-derive independently (clean-room from first principles), or drop attribution-dependent parts. Blocking those items until ruled.
- **D6 — Precedence policy scope** (STORM contradiction #1): confirm stage-scoped precedence (extraction: corpus>self-report; rewrite: C3 voice-wins) as the single policy.

## Explicitly rejected (with reasons — do not resurrect silently)

Outright em-dash ban (voice retention + C3); generic numeric humanizer levers as global gates (false-positive fence exists for this); manufactured personality/quirks (`no_invented_traits` family bans it); wholesale 6-job router port (duplicates existing 4-skill router); agent-readership frame as a feature (unfalsifiable); public corpus as *substitute* for owner-gated real-writer eval (supplement only — `false_positives.json` disclaims benchmark validity).

## Known gaps the whole field (and this plan) leaves open

Detector false-positive rate on genuinely human text is never measured (no known-human-negative eval); tell catalog has no versioning/temporal-decay against a moving adversarial target; voice modeled as one fixed profile with no audience/register conditioning; corpus consent/PII/impersonation handling in voice-onboard untouched; no recipient/outcome metric anywhere (all evals are intrinsic).

## Suggested build order (after owner rulings)

1. T0-1 state boundary (unblocks safe publishing) → 2. T0-2 + T0-3 (eval truthfulness) → 3. T0-4 + T1-4 (claim honesty + trust boundary, both S) → 4. T1-8 + T1-5 (eval capabilities that gate later work) → 5. T1-1/T1-2/T1-3 voice-onboard train (respecting D5/D6) → 6. T1-6/T1-7 polish lane → 7. Tier 2 hygiene batched into small PRs.

Review budget note: this plan already consumed a four-lane review (STORM peer review + Codex adversarial + audit verify + arbitration). Per the repo's review-budget rule, implementation PRs need at most one review pass each; the full gauntlet is done.
