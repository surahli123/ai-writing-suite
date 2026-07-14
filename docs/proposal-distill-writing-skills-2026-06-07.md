# Proposal — Distilling 4 External Writing Skills into the AI Writing Suite (2026-06-07)

**Status: PROPOSAL / MENU — no code. Separate workstream from Phase 2 (eval).**
Produced by workflow `wf_49f1178c-50b` (11 agents: 4 external analyzers + our-suite
mapper → 5 per-dimension distillers → adversarial prioritizer).

Sources analyzed:
- `alchaincyf/huashu-skills` — `huashu-proofreading` + `huashu-article-edit` (zh-CN; WeChat/short-video; persona 花生/花叔)
- `KKKKhazix/khazix-skills` — `khazix-writer` (zh-CN; persona 卡兹克; SKILL.md + references)
- `tw93/Waza` — `skills/write` (zh+en; indie-maker voice; ~208-line router + 6 reference files)

---

## The core framing: generalizable CRAFT vs non-generalizable STYLE

You asked to keep only what generalizes. The agents separated every technique into
**engine-worthy craft** (a language-agnostic mechanism) vs **fuel/locale style** (belongs
in a company's pluggable KB, or is one author's voice — never in the OSS engine).

**NOT generalizable (correctly excluded):**
- Chinese banned-phrase blocklists + stiff→spoken swap tables (在当今时代 / 综上所述 / 不是…而是…).
- Formatting thresholds tuned to Chinese character counts + WeChat mobile (15–25 字, subhead every 300–500).
- Chinese typography rules (no colon/em-dash; use 「」).
- **Named-persona voice contracts** (花生/花叔, 卡兹克, tw93's indie voice) — these ARE the product/fuel.
- Hardcoded macOS paths to one author's corpus.

---

## The 5 dimensions — generalizable patterns found

**1. How they CREATE the skill**
- Two-layer **router-SKILL + on-demand reference catalogs** (progressive disclosure): thin SKILL.md holds contract/modes/control-flow; heavy pattern libraries live in `references/` loaded on demand. *(Waza, khazix)*
- **Frontmatter description doubles as the router** — packs POSITIVE trigger phrases AND **negative routing** (explicit hand-offs + exclusions). *(all)*
- **❌/✅ contrast pair** as the atomic teaching unit for every rule (show bad form AND fix, not just a ban). *(all)*
- **Anti-bloat maintenance discipline embedded in the artifact** ("fold new lessons into existing entries, don't append"). *(Waza)*

**2. Criteria to REDUCE AI slop**
- Slop reduction is **bidirectional**, not just deletion: "add calibrated uncertainty + take a stance" is itself an anti-slop move. *(huashu)*
- Banned-token list ships **with approved replacements + a MANDATORY SECOND PASS** because revision reintroduces the slop it removed. *(khazix)*
- **"Catalog of smells, NOT a checklist"** meta-instruction to license judgment and stop the list degrading into mechanical find/replace. *(Waza)*
- **Layered QA pyramid** (L1 mechanical → L2 style → L3 content → L4 subjective). *(khazix)*

**3. Where AI is genuinely EFFECTIVE**
- Explicit **two-column delegation contract**: a named list of "AI licensed to do this" vs "AI doing this exposes you." *(khazix)*
- Pyramid escalates **mechanical (delegate to find/replace) → subjective (delegate to judgment)**. *(khazix)*
- **Inverted objective** to counter the model's default: "remove the *performance* of improvement, do not improve"; "over-editing is failure." *(Waza)*

**4. Orchestration + context management**
- Two-layer router + on-demand catalogs (tiered depth). *(Waza)*
- **Route on the ARTIFACT, not the command** — detect genre/language/surface from the text being edited. *(Waza)*
- **Confirm-scope-before-acting** blocking gate with edits pre-enumerated (location+type+content). *(huashu-article-edit)*
- **Externalize state to disk** to survive context truncation (save-after-batch + periodic X/Y progress report). *(huashu-article-edit)*

**5. Essential dimensions you didn't name**
- **Human/AI input partitioning**: name what ONLY the human may supply (lived experience, the core angle, real emotion). *(khazix)*
- A QA pyramid ending in **one irreducible acceptance test** ("did I just read an informed person?"). *(khazix)*
- **Somatic/embodied concreteness over knowledge-style labeling** as the core human-vs-AI tell ("I froze" > "this was stressful"). *(khazix)*
- **Narrative scaffolds as a small menu to PICK from, not invent** (opening repertoire: scene / number / question / counter). *(khazix)*

---

## Prioritized roadmap (adversarially filtered)

All 5 recommended are **ENGINE edits to existing files**, instruction-only or single-KB-file,
**no new skills**, none breaks the zero-dep / cross-surface promise.

| # | Proposal | Effort | Confidence | Engine/Fuel |
|---|---|---|---|---|
| 1 | **Re-scan the OUTPUT for reintroduced tells** — add a step 8.5 to comms-polish Rewrite Workflow. *All 4 skills independently found the polish pass itself leaks slop; we scan input then return with no output re-scan.* | S | high | ENGINE |
| 2 | **Negative routing in sub-skill frontmatter** (comms-polish "not for learning a voice → voice-onboard; not for code"; voice-onboard "not for rewriting → comms-polish"). *Our router admits it is not a runtime interceptor on Claude/Codex/Cursor, so mis-routing is fixable only in the description.* | S | high | ENGINE (metadata) |
| 3 | **Surface the replacement table** (robust→strong, leverage→use) from `detector/patterns.py` into `lexical-tells.md`. *patterns.py already has the swaps; the catalog ships bare word lists — dedup data we own, deterministic swaps.* | S | high | ENGINE-adjacent catalog |
| 4 | **Graduation/consolidation step in the self-improvement loop** — human-gated fold-back so `learned-rules.md` (append-only) doesn't bloat every on-start read. | S | high | ENGINE (lifecycle) |
| 5 | **Restructure `final-pass-checklist.md` into a layered gate** — same 13 items, L1 hard facts-floor (facts/numbers/code/quotes) separate from style layers + 1 subjective acceptance question on top. *Mirrors rubric.md's "no_fabrication always required."* | M | high | ENGINE |
| 6 (opt) | Somatic-over-knowledge rewrite DIRECTION on the C9 emotional-flatline entry (currently delete-only). | S | medium | catalog/fuel-leaning |
| 7 (opt) | Record a **typology-gate + ask-don't-fabricate + human/AI input-partition** design NOTE in the comms-draft/comms-qa stubs (note only — building is v2). | S | high | ENGINE (design note) |

## Rejected (and why) — the discipline that keeps this small
- **Build comms-draft now** → scope creep vs design decision D9 (v1 = enriched polish + voice-onboard + skeleton).
- **Deepen the 5 generic KB entries** → **fuel, not engine** — the KB is the pluggable slot a company fork swaps (D4/D11).
- **Wire the Python detector into comms-polish at runtime** → **breaks the cross-surface / zero-dep contract** (D5/D8: identical behavior on Claude/Codex/Cursor/RovoDev).
- **Deterministic voice-fidelity stylometric back-check** → over-engineered for v1 + needs the detector at runtime (same contract break).
- **Confirm-scope + incremental-save + progress cadence for edit mode** → duplicates/low-leverage; comms-polish edits a single doc, not a 4000–8000-item batch.
- **Active 2–3 question audience probe** → friction vs your hard 3-question limit; mostly not worth it for v1.

---

## Recommendation
Treat #1–#5 as a small, high-confidence **"engine polish" workstream**, separate from Phase 2.
#1 (re-scan output) is the single cheapest correctness win and the most cross-source-validated.
This is a MENU — your call which (if any) to pursue, and when relative to the Phase 2 eval work.
