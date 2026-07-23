> ⚠️ **HISTORICAL — superseded by [`docs/packaging.md`](packaging.md) (2026-06-07 restructure).**
> This document is kept for its decision log (D1–D12) and rationale only. Its packaging
> prescriptions — the `packaging/`/`sync.sh` generate-and-sync machinery and the
> `cursor-rules/`/`rovodev/` manifest directories — were **removed**; all hosts now read the
> single source tree directly. The v1/v2 scope split is also historical: QA and drafting
> (`comms-qa`, `comms-draft`) shipped in v1.1, so this document's "Deferred to v2" list is
> stale; see the CHANGELOG for shipped scope. For the current, authoritative packaging and
> install model, read `docs/packaging.md`. Do not follow the packaging/sync steps below.

# Design Plan — AI Writing Suite (OSS) v1

Date: 2026-06-06
Author: surahli (product owner) + Claude (grill-me session)
Status: **PLAN ONLY — awaiting explicit "go" before any code**
Repo: `~/Documents/Codex/2026-06-01/personal-productivity-skills`
Current branch: `add-ai-writing-humanizer` (behind `origin/main`, PR #3 merged)

---

## 1. Vision

Turn the existing single-purpose `ai-writing-humanizer` skill into the **open-source
version of a writing-assistant skill SET** that surahli will build for the company's
Data Scientists. The company version is driven by a proprietary **DS Comms Playbook**;
the OSS version ships the same engine with a generic best-practices knowledge base.

The suite does four things:
1. **Knowledge QA / mini-RAG** over the comms playbook + real-world best practices.
2. **Guided drafting** of a page, using the playbook.
3. **Polish / review** of a page, using the playbook + best practices (this is the
   piece that already half-exists today as `ai-writing-humanizer`).
4. **Voice learning + proactive self-improvement** — learn the user's historical
   writing style; each session propose new rules (human-gated) to get better.

> **Engine vs Fuel principle:** the OSS repo is the *engine*; the playbook is *fuel*.
> The knowledge base is a pluggable asset. OSS bundles a generic KB distilled from the
> 4 reference repos. The company fork drops the real DS Comms Playbook into the same slot.
> The playbook **never** enters the public repo.

---

## 2. Decision Log (resolved in grill-me session)

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| D1 | Product identity | **Full writing-assistant suite** (not a narrow humanizer) | OSS face of a company DS skillset |
| D2 | Reuse of 4 ref repos | **Absorb all**, attribute in NOTICE | All MIT-licensed → copy/derive OK with copyright + license retained |
| D2b | nature-skills scope | **Only `nature-writing` + `nature-polishing`** | Other 28k lines are paper2ppt/citation/academic — irrelevant |
| D3 | Architecture | **Suite**: router + `comms-qa` + `comms-draft` + `comms-polish` + `voice-onboard`; self-improvement = cross-cutting hook | Matches the 4 functions; nature-skills suite shape |
| D3b | Router weight (eng-review) | **Thin router**: a documentation/entry skill listing sub-skills. Claude/Codex/Cursor use host-native skill dispatch (no interception). Explicit intent routing ONLY on RovoDev (no auto-trigger). | Avoids reinventing host dispatch ([Layer 1]) |
| D10 | Eval + self-improvement (eng-review) | **eval harness in v1**: (a) before/after fixtures across genres, LLM-judged, baseline calibrated to fail 30-40%; (b) ported avoid-ai JS detector as mechanical regression gate; (c) self-improvement loop borrows **Autorefine** methodology — Hamel Three Gulfs + error analysis + Karpathy mutation. Each proposed rule is eval-measured before human approval. | A self-improving skill needs a holdout; matches CLAUDE.md eval-calibration rule |
| D11 | Build sequencing (ceo-review) | **OSS engine first; playbook dropped in later via Confluence page → `knowledge/` slot** (company step = add data, not build engine). | OSS-first is low-risk + produces public artifact; playbook integration designed as near-zero-effort |
| D12 | Ingestion/retrieval coherence (ceo-review) | **v1 must prove ONE end-to-end ingestion+retrieval smoke path** (markdown/Confluence page → INDEX → correct passage retrieved), even though full `comms-qa` is v2. | Without it, the "just add a Confluence page" promise is hollow — company step would still need an unbuilt RAG engine |
| D4 | OSS / company boundary | **Pluggable KB + bundled generic KB** | Engine reusable, playbook stays private |
| D5 | RAG mechanism | **Pure markdown KB + INDEX.md navigation, zero-dep.** "Wiki-style" = structure/convention only (entries + index + cross-links), NOT OMC wiki MCP tools (those are Claude+OMC-only and break on Codex/Cursor/RovoDev). OMC `wiki_*` tools = optional Claude-side accelerator. | Portable across all 4 surfaces (D8); keyword/navigation recall beats dense retrieval for a moderate playbook |
| D6 | Self-improvement safety | **Human-gated** — propose deltas, user approves, append to side files; never auto-edit core SKILL.md | Prevents drift/degradation; suits high-value/company use |
| D7 | Voice sample source | **Local files/paste (primary) + Confluence page link** | Company DS history lives in folders + Confluence; KB can use same ingestion |
| D8 | Target environments | **Claude + Codex + Cursor + RovoDev** (single source → 4 packages) | surahli uses Claude; company may use any; RovoDev = constrained in-house agent |
| D9 | v1 scope | **Vertical slice: enriched polish + voice-onboard + suite skeleton** | Polish is half-built; voice is the differentiator; QA/draft are heaviest net-new |

---

## 3. What each reference repo contributes (all MIT)

| Repo | Absorbed contribution | Lands in |
|---|---|---|
| **weijt606/anti-vibe-writing** | Bilingual (中/EN) pattern sets, `scenario-presets`, `learning-mode`, `host-profile` voice template, `final-pass-checklist`, before/after benchmarks | `comms-polish` references + `voice-onboard` template |
| **conorbronsdon/avoid-ai-writing** | Programmatic JS detector + tests + CI, CATEGORIES taxonomy, multi-surface packaging (Claude plugin + Cursor `.mdc`) + `sync-plugin-skill.sh` | Detector (v2), packaging/sync scaffold, Cursor target |
| **donghuixin/AI-Vibe-Writing-Skills** | Local AI-detector idea, style-extractor / reviewer agent prompts, soft/hard memory pattern | Optional detector (v2), `voice-onboard` distillation prompt, self-improvement memory shape |
| **Yuan1z0825/nature-skills** (`nature-writing` + `nature-polishing` only) | Academic polish/writing rubric, codex/plugin manifest conventions | `comms-polish` rubric, packaging conventions |
| **(existing) installed refs** | `stop-slop` (8 rules), `blader-humanizer` (43 patterns — **corrupted text, must clean**), `aboudjem-humanizer` (Wikipedia 30 patterns) | Consolidated into ONE clean pattern catalog |

**Attribution rule:** `NOTICE.md` lists every source repo + author + MIT copyright line +
link. Replaces the current "we avoided wholesale reuse" wording (D2 reverses that stance,
which is fine under MIT as long as notices are preserved).

---

## 4. Target architecture (full, eventual)

```
ai-writing-suite/                      # OSS repo (rename or keep ai-writing-humanizer)
├── SKILL.md (router)                  # detects intent → routes to qa/draft/polish/voice
├── skills/
│   ├── comms-qa/        SKILL.md      # ① mini-RAG over KB (wiki-style)
│   ├── comms-draft/     SKILL.md      # ② playbook-guided drafting
│   ├── comms-polish/    SKILL.md      # ③ polish/review/de-AI (enriched humanizer)
│   └── voice-onboard/   SKILL.md      # ④ interview + distill historical writing
├── _shared/
│   ├── knowledge/                     # PLUGGABLE KB (OSS=generic; company=playbook)
│   │   ├── INDEX.md                   # wiki-style index for navigation/recall
│   │   └── *.md                       # topic entries (ingested via wiki_ingest pattern)
│   ├── patterns/                      # ONE consolidated AI-tell catalog (dedup of 3+4 sources)
│   ├── voice-profile.md              # learned user style (read every session)
│   ├── learned-rules.md             # human-gated self-improvement log (append-only)
│   └── host-profile-template.md     # from anti-vibe
├── packaging/
│   ├── sync.sh                        # single source → 4 targets
│   ├── .claude-plugin/ .codex-plugin/ cursor-rules/ rovodev/
├── NOTICE.md  LICENSE  README.md  CHANGELOG.md
```

Self-improvement = lifecycle hook in **every** sub-skill: on start, read
`voice-profile.md` + `learned-rules.md`; on end, **propose** candidate rules → user
approves → append. Core SKILL.md logic is never auto-modified.

---

## 5. v1 scope (this build)

**Ships:**
1. **Suite skeleton + router** — directory structure above; router SKILL.md that routes
   intent (v1 router only needs to reach `comms-polish` + `voice-onboard`; qa/draft are
   stubs with "coming in v2" notes).
2. **`comms-polish`** — enrich the existing humanizer:
   - Consolidate the 3 existing refs + 4 repos into ONE clean `_shared/patterns/` catalog
     (fix the corrupted `blader-humanizer` text; dedup overlapping patterns; keep source
     tags for attribution).
   - Add `scenario-presets` (tweet / LinkedIn / README / memo) from anti-vibe.
   - Add `final-pass-checklist`.
   - Reads `voice-profile.md` if present (voice matching).
   - Keep modes: detect / review / rewrite / edit + 0–100 score.
3. **`voice-onboard`** — interview + distill from local files/paste → writes
   `voice-profile.md` using the host-profile template. (Confluence link = v2.)
4. **Generic KB seed** — `_shared/knowledge/INDEX.md` + a few topic entries distilled
   from the 4 repos (wiki-style), proving the pluggable slot. (Full `comms-qa` retrieval = v2.)
5. **Self-improvement hook (human-gated)** wired into `comms-polish` + `voice-onboard`:
   propose → approve → append to `learned-rules.md`.
6. **NOTICE.md** rewritten with all attributions; **CHANGELOG** entry; README updated.
7. **Packaging: Claude + Codex** only in v1 (the two surfaces surahli can test now).
8. **Eval harness (D10)** — `evals/` with before/after fixtures across genres (tweet /
   LinkedIn / README / memo), expected score bands, LLM-judge rubric calibrated so the
   baseline fails 30-40%; + ported avoid-ai JS detector as a mechanical regression gate;
   + self-improvement loop wired to Autorefine-style error analysis + mutation, eval-gated
   before each human-approved rule append.
9. **KB ingestion+retrieval smoke path (D12)** — prove ONE end-to-end chain on the generic
   KB: a markdown/Confluence-style page → `_shared/knowledge/INDEX.md` → agent retrieves the
   correct passage for a query. NOT full `comms-qa` (that's v2); just enough to guarantee the
   company step is "drop in a Confluence page", not "build a retrieval engine".

**Deferred to v2:** `comms-qa` full RAG, `comms-draft`, Confluence ingestion,
programmatic JS/Python detector, Cursor + RovoDev packaging, bilingual Chinese path,
optional embedding index.

---

## 6. Risks & flags

- **R1 — Ghostwriting philosophy conflict.** surahli's writing-vault rule is "AI
  scaffolds, never ghostwrites." This suite *does* draft/rewrite. Resolution: this is a
  **separate, general/company tool**, not the personal writing-vault. Keep them distinct;
  do not let suite rewrite-mode bleed into `/distill`/`/voicecheck` behavior.
- **R2 — RovoDev constraints.** No skill auto-trigger, general-purpose subagents only,
  limited tools (`reference_inhouse_agent.md`). The human-gated self-improvement and
  file-read RAG must degrade gracefully there. Company version targets RovoDev explicitly.
- **R3 — Self-improvement drift.** Mitigated by D6 (human gate + append-only side files +
  periodic lint/dedup). Never auto-edit core logic.
- **R4 — 4-surface sync drift.** Single source of truth + `sync.sh` (avoid-ai pattern).
  Don't hand-edit generated packages.
- **R5 — Scope.** Full vision is large; v1 deliberately a vertical slice (D9).
- **R6 — Corrupted `blader-humanizer` reference.** Must be re-derived cleanly, not copied
  verbatim.

---

## 7. Pre-build checklist (before "go")

1. `git checkout main && git pull` to sync local to `origin/main` (currently behind).
2. Cut fresh branch `feat/ai-writing-suite-v1` (do NOT build on stale `add-ai-writing-humanizer`).
3. Confirm repo rename decision: keep `ai-writing-humanizer` package name vs `ai-writing-suite`.
4. (Optional, recommended) one plan review pass: `/plan-eng-review`.

## 8. Success criteria (what "done" looks like for v1)

- `comms-polish` runs in Claude + Codex, consolidated catalog, scenario presets, voice
  matching when a profile exists, 0–100 score, no corrupted text.
- `voice-onboard` produces a usable `voice-profile.md` from pasted/local samples.
- Self-improvement proposes a rule, waits for approval, appends on yes.
- Generic KB slot present and documented as swappable for the company playbook.
- NOTICE.md credits all 4 repos; licenses preserved; CHANGELOG + README updated.
- Verification: skill loads without error in both targets; one end-to-end polish demo
  shown with before/after + score.

## 9. v2 roadmap (not now)

`comms-qa` full wiki-RAG → `comms-draft` → Confluence ingestion → programmatic detector
→ Cursor + RovoDev packaging → bilingual path → company fork with real playbook.

---

## What already exists (reuse, don't rebuild)

- Installed `ai-writing-humanizer` + 3 refs (`stop-slop`, `blader`, `aboudjem`) → polish/detect base.
- 4 MIT repos → detectors, scenario presets, voice templates, packaging/sync scaffolds.
- User's own `/distill`, `/voicecheck`, `write` skills → personal voice/polish (keep separate, R1).
- avoid-ai JS detector + tests → port as regression gate (D10).
- Autorefine skill → borrow eval + mutation methodology (D10).

## NOT in scope (v1)

- `comms-qa` full retrieval, `comms-draft` — deferred (KB seed only in v1).
- Confluence ingestion — v2 (local files/paste only in v1).
- Cursor + RovoDev packaging — v2 (Claude + Codex only).
- Bilingual Chinese path — v2.
- Embedding/vector index — v2 (markdown+INDEX only).

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 1 | HOLD_SCOPE, issues_resolved | sequencing confirmed (OSS-first via Confluence drop-in, D11); 1 coherence gap fixed (v1 smoke path, D12) |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 1 | clean | 4 issues: scope(kept full per owner), D5 portability fix, thin router, eval harness added |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | n/a | prompt-only, no UI |

- **CROSS-REVIEW:** eng (architecture) + ceo (strategy) agree the plan is sound after D5/D3b/D10/D11/D12; no tension.
- **UNRESOLVED:** 0. Scope kept full by owner; all findings resolved into D3b/D5/D10/D11/D12.
- **VERDICT:** CEO + ENG CLEARED — ready to implement. Pre-build checklist §7 still applies (sync main, cut `feat/ai-writing-suite-v1`).

