# Changelog

All notable changes to the AI Writing Suite are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **Document/narrative-shape tell category (#9)** — the first document-altitude
  category (`narrative-shape.md`, N1–N4): over-explained themes, tidy single-track
  resolution, flat escalation, absent ambiguity, each with a validity condition so
  a genuinely simple update is never forced to fake complexity. Judge-only/advisory
  `narrative_shape_ok` dimension wired into comms-draft's structural planning, with
  a gold-FAIL over-correction partner fixture.
- **Quantitative stylometric fingerprint (#15)** — `_shared/stylometry.py` computes a
  per-genre measured fingerprint (sentence-length variance/burstiness, function-word
  deltas, char 3-grams, punctuation and testable-number density, AI-register absences)
  written alongside the 10 qualitative dimensions; every number is recomputable from
  the samples, so the voice-contract eval asserts on numbers, not prose. CJK is
  detected and refused rather than silently mismeasured.
- **Audit-report output contract (#19)** — comms-polish detect/review now emit a fixed
  report shape (worst-offender lead, Critical/Moderate/Minor with definitions,
  Quote→Tell→Why→Fix findings resolved against the live 71-id catalog, calibrated
  "reads well" close, on-demand score as the final line), enforced by a deterministic
  output-contract check (`run_all.sh` step 7) — structure only, not behavioral coverage.
- **Fork KB ingestion tooling (#25)** — `tools/kb_ingest.py` (Confluence HTML/markdown
  export → KB entries + INDEX merge; idempotent including the collision path; atomic
  writes; the frozen INDEX protocol header is never rewritten) and `tools/kb_validate.py`
  (structural pre-flight wrapping kb_lint, with retrieval-smoke tie/shadow detection and
  a generic-KB shadowing warning), plus a data-person onboarding guide
  (`docs/kb-onboarding.md`).
- **Behavioral-eval lanes for comms-draft and voice-onboard** (`run_all.sh` steps 5–6):
  pre-authored good/bad artifact discrimination with white-box mutant families
  (must-catch floors) and a black-box holdout adversary corpus.

### Fixed
- **Pattern-catalog contradictions** — register shift consolidated to one canonical
  entry with a validity condition; C2/H7/H8 and S9/L1 duplicates resolved via
  canonical/alias precedence; the R1→C8 rhetorical-question fix-loop closed; validity
  conditions added to S1/S2/T9 (owner ruling: the catalog optimizes prose quality,
  not provenance detection).
- **Self-improvement lifecycle** — `graduated` status defined everywhere; scope enum
  covers all four sub-skills; a concrete owner-gated promotion procedure replaces the
  ownerless one (a proposed rule older than 30 days now prompts a decision).
- **Release hygiene** — version-neutral manifest descriptions; root LICENSE; corrected
  copyright holder; NOTICE records the MIT-era nature-skills absorption bounds; CI now
  validates manifests + SKILL.md frontmatter (`scripts/validate_packaging.py`); README
  reconciled to shipped reality with a quickstart; RovoDev claims narrowed to the
  verified 2026-06-08 scope.

---

## [1.1.0] — 2026-07-13

### Added (eval hardening — 2026-07-13, from the de-slop landscape research)
- **Gold-FAIL fixture suite** (`evals/fixtures/fixtures_fail.json`, 4 bad-rewrite pairs:
  fabricated number, over-corrected overstepping, payoff stub, dropped claim) so the LLM
  judge is tested on discrimination, not just agreement; plus the O2 presumed-misconception
  strawman fixture (`overstep-06-strawman-en`). Both excluded from the naive-baseline
  calibration denominator (band stays 38%).
- **Synthetic false-positive regression fence** (`evals/fixtures/false_positives.json` +
  `run_false_positives.py`, wired as a `run_all.sh` step): hand-authored pseudo-human
  clean samples (non-native ESL, terse-parataxis, formal-academic, and ordinary
  professional prose across all four genres) the detector must NOT flag, plus planted
  AI-slop controls it MUST catch; the run fails on any false positive, missed control,
  or empty cohort. This is a guard against detector-rule regressions, NOT evidence about
  real non-native writers — a de-identified real-writer corpus is an owner-gated follow-up.
- **Quoted-evidence judge protocol**: per-dimension verdicts now require a verbatim
  quoted snippet. Paired-quote parsing keeps contractions/apostrophes intact (the old
  regex truncated `"We're behind"` to `We`); `verify_evidence()` checks each quote is a
  whitespace-normalized substring of the before/after, so a well-formed but fabricated
  quote is caught. Missing, malformed, and not-verbatim evidence surface as advisory
  warnings (never blocks — the judge stays advisory). Added a judge/rewriter cross-family
  self-preference warning via the optional `AIWS_REWRITER_MODEL` env var.

### Changed
- **Router seam fix**: `comms-polish` and `comms-draft` frontmatter descriptions each
  gained one disambiguating clause so mixed "polish this AND add a section" requests
  route to `comms-draft` (polishing never adds substance).

### Fixed
- **Publishable installs across hosts** — the published repo was not actually
  installable: the plugin body was gitignored (only manifests reached the remote)
  and the Claude marketplace manifest was not at a resolvable location. Both Claude
  and Codex now install **directly from the single source tree** via repo-root
  marketplace manifests (`.claude-plugin/marketplace.json` and
  `.agents/plugins/marketplace.json`), each backed by an in-source `plugin.json`.
- **`detector.py` SyntaxWarning** — `\S+` in the module docstring was an invalid
  escape sequence; escaped it. The evals tree now compiles clean under
  `python3 -W error::SyntaxWarning`.
- **Suite-root path protocol** — replaced parent-relative `../../_shared/...` references
  in `comms-polish` and `voice-onboard` with a stated suite-root location protocol plus
  root-relative `_shared/...` paths. Fixes silent shared-asset loading failure on RovoDev
  manual installs, where the agent resolves relative paths against the session cwd.

### Added
- **`payoff_clear` judge leg (Ogilvy rule 9 — "make the ask clear")** — pairs with
  `overstepping_removed`: after a manufactured presumption is deleted via 少写, it
  checks the surviving claim still stands on its own instead of a stub that lost the
  antecedent the deleted frame supplied ("It reduces them" → "Merging reduces
  outages"). Judge-only/advisory, never gates CI; scored only when a removal happened.
  Adds the `overstep-05-payoff-en` minimal-pair anchor + revert-guarded tests
  (`PayoffClearGuards`: the fenced judge prompt documents the dimension; the fixture
  exists; the FAIL partner is detector-blind and drops the presumption).
- **`aggregate()` N/A handling** — the LLM-judge aggregator now recognizes an explicit
  `N/A` dimension state and treats it as *vacuously satisfied* (dropped from the verdict)
  rather than an incomplete rep. A conditional dimension like `payoff_clear` can thus be
  marked N/A when it doesn't apply without silently voiding the fixture's whole verdict;
  `no_fabrication` can never be N/A (still forces a genuine PASS/FAIL). Covered by
  `NaAwareAggregate`.
- **Over-stepping (反代入式越位感) judge dimension** — a new advisory LLM-judge
  dimension `overstepping_removed` for the before/after fixtures, catching prose
  that thinks *for* the reader (presumed cognition, strawman misconception,
  projected mental image, self-Q&A-as-judge). The load-bearing **validity
  condition** — a presumption is over-stepping ONLY when the prior is a
  manufactured strawman; a real widespread belief makes the contrast legitimate —
  pairs it with `meaning_preserved` so stripping a legitimate contrast (e.g. "love
  isn't a feeling, it is behavior") fails as over-correction. Judge-only by
  design: the mechanical detector is blind to it (the tell is in stance, not
  vocabulary), it never gates CI, and it stays advisory/opt-in consistent with
  `judge.py`. Ships: the `overstepping_removed` rubric row + validity-condition +
  judge-prompt addition in `evals/fixtures/rubric.md`; 4 PASS minimal-pair
  fixtures (en/zh, readme/linkedin) embedded in genre-realistic paragraphs whose
  context is word-for-word identical before/after so the signal isolates stance,
  not verbosity (marked `detector_blind: true` and excluded from the naive-baseline
  calibration denominator — they are misses by construction, not calibration
  failures); 3 real-mined FAIL hard-negative exemplars (over-correction of a
  legitimate contrast) as unit tests; and a new catalog file
  `_shared/patterns/overstepping-presumption.md` (4 sub-types, 4 self-test
  questions, validity condition, 少写/多写 substitution guidance) registered in the
  pattern index, with self-scan items added to `comms-polish` and `comms-draft`.
- **KB wiki cross-links + `kb_lint` validation** — each KB entry now ends with a
  `## Related entries` footer (2-3 bidirectional wiki links to adjacent entries), giving
  `comms-qa` one-hop multi-hop retrieval when a question spans two topics. A new stdlib-only
  `evals/kb_lint.py` enforces the pluggable-KB add-an-entry contract for company forks
  (INDEX↔directory sync, link validity / no rot / no self-links / ≥2 per entry,
  bidirectionality, non-empty Keywords); `evals/test_kb_wiki.py` runs it against the shipped
  KB under `run_all.sh`. `comms-qa` step 4 gains a one-hop follow: if part of a question is
  still unanswered, check the entry's `## Related entries` footer and open one obvious
  neighbor before declaring that part uncovered. INDEX.md retrieval semantics unchanged.
- **`comms-qa` v1.1** — the placeholder is now a working question-answering sub-skill: a
  mini-RAG over the pluggable KB that wraps `INDEX.md`'s retrieval protocol exactly (match
  Keywords then Summary intent → open the single best entry; synthesize both on a tie; say the
  KB does not cover it on zero match). Answers are KB-only and cited to the entry file they came
  from; knowledge from outside the KB is allowed only in a clearly separated, labeled "Outside
  the playbook:" section, never blended into the playbook answer — because in a company fork the
  KB is policy and a fabricated "the playbook says…" is the worst failure. Multi-part questions
  are decomposed and answered per part with per-part citations; a missing or empty KB makes it
  say so and stop rather than answer from general knowledge. Added two question-path smoke cases
  (3 → 5) to the existing deterministic runner.
- **`comms-draft` v1.1** — the placeholder is now a working drafting sub-skill that produces
  playbook-guided first drafts which read human, instead of generating generic text and leaning
  on a later polish. Research-grounded design: per-task acceptance criteria derived from the brief
  before drafting (dynamic per-query criteria track human judgment better than a fixed rubric);
  draft-time KB/voice injection and concreteness plus varied sentence rhythm (burstiness) as
  write-time constraints, with the AI-tell catalog as a negative checklist; a deliberate
  vary/roughen pass (uniform output is itself a tell); and a post-draft self-scan against the
  catalog (mirrors comms-polish's re-scan). Never fabricates — gaps are marked `[NEEDS: …]`;
  degrades gracefully on a missing voice profile or empty KB; hands off to comms-polish for the
  final pass.
- **RovoDev support (manual install)** — the router's RovoDev section now tells the agent to read
  the chosen sub-skill on demand (self-sufficient routing), and `docs/packaging.md` + the README
  document the manual copy + explicit-invocation path. Smoke-tested working on an in-house RovoDev
  (2026-06-08): `/skills` registered the router and all four sub-skills, and `comms-polish` produced
  a before/after rewrite. Supersedes the earlier "deferred to v2" status.
- **Cursor support** — Cursor reads Anthropic-format `SKILL.md` Agent Skills from
  `.cursor/skills/`; install = copy `skills/ai-writing-suite/` into a Cursor skills
  directory. (Corrects the earlier plan that targeted `.cursor/rules/*.mdc`, the wrong
  primitive for callable skills.)
- **Per-host install Quickstart** in the README (Claude, Codex, Cursor) and a
  maintainer packaging note at `docs/packaging.md`.
- **Regression runner + CI** (`evals/run_all.sh` + `.github/workflows/ci.yml`) — one
  stdlib-only command (unit tests + KB smoke + fixture calibration) gating every push
  and PR. (Phase 1)
- **Opt-in advisory LLM judge** for the before/after fixtures (`evals/fixtures/judge.py`)
  — env-driven, key-gated, stdlib-only; parses per-dimension verdicts and re-computes the
  result in Python (`no_fabrication`-overrides-FAIL); SKIPPED offline, advisory (never
  gates CI), loud on auth/transport failure. Adds `expected_verdict` gold labels for
  judge-vs-gold agreement. (Phase 2a)
- **Engine-polish from cross-skill distillation** — `comms-polish` now re-scans its output
  against the catalog before returning; negative-routing hand-offs in sub-skill frontmatter;
  a deterministic Tier-1 word→swap table in `lexical-tells.md`; a human-gated graduation step
  in the self-improvement loop; a layered final-pass checklist with a hard facts-floor.
- **Expanded test suite** (51 stdlib-only tests) — judge parse/aggregate + fabrication-trap,
  voice-profile header contract, catalog↔detector sync, and SKILL.md frontmatter contract.
- **Miss-target calibration table** (`evals/fixtures/calibration.py` + test) — a stdlib-only
  helper that, per eval-set size n, returns the naive-baseline miss count(s) that keep the fail
  rate in the 30-40% band (and flags uncalibratable sizes like n=4, n=7). Turns the calibration
  knife-edge into a lookup before adding or removing fixtures; cross-checked against the live
  `fixtures.json` so it can't drift from the `run_fixtures` assert. (Phase 2b prep)

### Removed
- **Generate-and-sync packaging** (`packaging/` + `sync.sh`) — obsolete now that every
  host reads the source tree directly. This eliminates the gitignored-body trap that
  made v1 uninstallable and removes the per-host sync-drift surface entirely.

---

## [1.0.0] — 2026-06-06

### Added

#### Suite Foundation
- **Suite skeleton and router** (`SKILL.md`) — unified entry point for writing-assistant features. Routes user intent to appropriate sub-skills.
- **Sub-skill stubs** — `comms-qa` (v2), `comms-draft` (v2), `comms-polish` (v1), `voice-onboard` (v1). Each includes README and "coming in v2" notes where applicable.
- **Directory structure** — standardized layout with `skills/`, `_shared/` (knowledge, patterns, voice profiles), and `packaging/` for multi-surface distribution.

#### comms-polish (Enriched Humanizer)
- **Consolidated pattern catalog** (`_shared/patterns/`) — deduplicated and merged seven overlapping AI-writing pattern lists into a single source of truth.
  - Seven pattern files: `lexical-tells.md`, `significance-attribution.md`, `structural-tells.md`, `hedging-filler.md`, `punctuation-formatting.md`, `communication-artifacts.md`, `rhythm-stylometric.md`.
  - Each pattern includes: Tell (what the model does), Fix (editing move), Before/After examples, and source attribution.
  - Pattern IDs are stable and not source-specific; source lineage is traceable via `Sources` field.
- **Scenario presets** (`skills/comms-polish/references/scenario-presets.md`) — templates for common write contexts: tweet, LinkedIn post, technical README, memo.
- **Final-pass checklist** (`skills/comms-polish/references/final-pass-checklist.md`) — structured review points before publishing.
- **Voice matching** — reads `_shared/voice-profile.md` (if present) to calibrate tone and style to the author's historical writing.
- **Multiple modes** — detect (find AI tells without rewriting), review (prioritized findings), rewrite (produce polished prose), edit (modify files in place).
- **0–100 score** — quantified AI-tell density for before/after comparison.
- **Corrupted source cleanup** — `blader/humanizer` patterns (P31-P43) were re-derived cleanly from intent, not copied verbatim; duplicated/run-together blocks fixed.

#### voice-onboard
- **Interview flow** — guided conversation to collect writing samples (local files or pasted text).
- **Profile distillation** — extracts author voice signature (tone, vocabulary, sentence shape, register preferences) into `_shared/voice-profile.md`.
- **Host-profile template** — structured markdown format (from anti-vibe-writing) for consistent voice capture and reuse.
- **Multi-surface support** — works in Claude and Codex (v1); Cursor and RovoDev support deferred to v2.

#### Generic Knowledge Base Slot
- **Pluggable KB foundation** (`_shared/knowledge/`) — wiki-style markdown structure (zero external dependencies) for portable knowledge ingestion and retrieval.
- **INDEX.md** — navigation index for manual and programmatic lookup.
- **Seed topics** — starter entries on audience, clarity, revision, structure, tone (distilled from source repos).
- **Smoke-test path** (`_shared/knowledge/SMOKE-TEST.md`) — proves end-to-end ingestion → retrieval chain before `comms-qa` full RAG lands in v2.
- **Design rationale:** Pure markdown + convention, not host-specific MCP tools (OMC wiki), so the slot remains portable across Claude, Codex, Cursor, and RovoDev.

#### Self-Improvement Loop (Human-Gated)
- **Lifecycle hook** — wired into `comms-polish` and `voice-onboard`.
- **Propose → Approve → Append workflow** — after each session, suggest candidate rules based on error analysis (Autorefine methodology).
- **Side-file storage** — proposed rules append to `_shared/learned-rules.md` (append-only, never auto-editing core SKILL.md).
- **Eval-gated approval** — each proposed rule is measured against the eval harness before human confirmation.
- **Memory patterns** — soft (session-scoped) and hard (persistent) memory shape from AI-Vibe-Writing-Skills.

#### Evaluation Harness
- **Before/after fixtures** (`evals/`) — across genres (tweet, LinkedIn post, README, memo).
- **LLM-judged scoring** — rubric-based evaluation using Claude as a judge.
- **Baseline calibration** — tuned so the baseline fails 30–40% of cases, enabling regressions to surface.
- **Mechanical regression gate** — ported avoid-ai JavaScript detector as a language-agnostic reference test (Python detector to follow in v2).
- **Self-improvement loop integration** — Autorefine-style error analysis and mutation; each proposed rule is eval-measured before user approval.

#### Attribution & Licensing
- **NOTICE.md** — comprehensive attribution for all seven source projects (anti-vibe-writing, avoid-ai-writing, AI-Vibe-Writing-Skills, nature-skills, stop-slop, blader/humanizer, aboudjem/humanizer-skill). Preserves copyright and MIT license for each.
- **Pattern source legend** (`_shared/patterns/00-index.md`) — cross-reference for tracing pattern lineage.
- **LICENSE** (MIT) — full license text in repository root.

#### Packaging & Distribution
- **Sync tooling scaffold** (`packaging/sync.sh`) — single source of truth distributed to four surfaces (Claude, Codex, Cursor, RovoDev).
- **Multi-surface manifests** — `.claude-plugin/`, `.codex-plugin/`, `cursor-rules/`, `rovodev/` directories (v1: Claude + Codex only; v2: Cursor + RovoDev).
- **README.md** (suite-level) — explains the four sub-skills, engine-vs-fuel KB model, self-improvement workflow, installation, and use.

#### Documentation
- **Design plan** (`docs/design-ai-writing-suite-v1-2026-06-06.md`) — decision log (D1–D12), risk analysis, success criteria, and v2 roadmap.
- **Project CLAUDE.md** — project-specific conventions and working style.

### Technical Details

#### Architecture Decisions (from design plan)
- **D1 (Product identity):** Full writing-assistant suite (not a narrow humanizer); OSS face of a company DS skillset.
- **D2 (Reuse of 7 sources):** Absorb all MIT-licensed sources with preserved attribution.
- **D3 (Architecture):** Suite = router + `comms-qa` + `comms-draft` + `comms-polish` + `voice-onboard`; self-improvement = cross-cutting hook.
- **D5 (RAG mechanism):** Pure markdown KB + INDEX.md navigation, zero-dep; wiki-style structure/convention only (not OMC wiki MCP tools).
- **D6 (Self-improvement safety):** Human-gated — propose deltas, user approves, append to side files; never auto-edit core logic.
- **D10 (Eval framework):** Baseline calibrated to fail 30–40%; ported avoid-ai JS detector as mechanical gate; Autorefine-style error analysis.
- **D12 (KB coherence):** v1 must prove one end-to-end ingestion+retrieval smoke path to guarantee company step is "drop in a Confluence page", not "build a retrieval engine".

#### v1 Scope vs v2 Deferral
- **Ships in v1:** Suite skeleton, `comms-polish`, `voice-onboard`, generic KB seed, self-improvement hook, eval harness, Claude + Codex packaging, NOTICE/CHANGELOG/README.
- **Deferred to v2:** `comms-qa` full RAG, `comms-draft`, Confluence ingestion, programmatic detector, Cursor + RovoDev packaging, bilingual Chinese path, embedding index.

### Compatibility

- **Target environments:** Claude, Codex (v1); Cursor, RovoDev (v2).
- **Dependencies:** None (pure markdown, zero external packages).
- **Knowledge base:** Pluggable slot designed for OSS (generic best-practices KB shipped) and company use (proprietary DS Comms Playbook via Confluence).

### Verification

- Suite loads without error in Claude and Codex.
- One end-to-end polish demo: before/after text with score.
- Pattern catalog deduplication verified; no orphaned source references.
- Self-improvement loop proposed and approved a rule end-to-end.
- Generic KB smoke test: markdown page ingested, correct passage retrieved.

---

## Future Versions

### v2 Roadmap (Not in this release)

- `comms-qa` — full wiki-RAG over knowledge base.
- `comms-draft` — playbook-guided drafting flow.
- Confluence ingestion — company step adds playbook via web page link.
- Programmatic detector — Python version + CI integration.
- Cursor + RovoDev packaging — surface-specific manifests.
- Bilingual Chinese path — full support for 中 content.
- Optional embedding index — dense retrieval for large playbooks.

---

## Contributing

See `docs/design-ai-writing-suite-v1-2026-06-06.md` for design decisions and the engine-vs-fuel principle. All absorbed material is MIT-licensed; new contributions should follow the same.

---

## License

MIT License. See `LICENSE` and `NOTICE.md` for details.
