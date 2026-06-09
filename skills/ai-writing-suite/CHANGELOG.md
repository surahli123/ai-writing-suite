# Changelog

All notable changes to the AI Writing Suite are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

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

### Added
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
