# Design Spec — voice-onboard: Exemplar Anchors + Checkable Hard Rules

- **Date:** 2026-07-03
- **Status:** SPEC — awaiting owner approval. **No code until owner says "go".**
- **Author flow:** brainstorming → grill-me (21 branches resolved) → this spec.
- **Source idea:** @0xxDana, *"why your AI sucks at writing + how to fix it"* (https://x.com/0xxDana/status/2073030267552616936).
- **Working notes / decision trail:** `docs/brainstorm-voice-onboard-dana-sharpen-2026-07-03.md`.

---

## 1. Summary

Sharpen `voice-onboard` by adding two new, append-only sections to the voice-profile
contract, and teaching `comms-polish` + `comms-draft` to consume them:

- **B — Exemplars:** 2-3 verbatim "what good looks like" samples, used as a **few-shot
  style anchor** (calibrate *how* the author writes; never copy *what* they wrote).
- **C — Hard Rules:** ≤7 blunt, **checkable** imperatives distilled from the profile's
  strongest signals, enforced **advisory** (flag, never hard-block).

Both are new `## H2` sections in `_shared/voice-profile.md` — the existing frozen
contract that `comms-polish`/`comms-draft` already read. **No new read paths** (both
consumers already read this file); the only added files are structural tests.

## 2. Motivation

Dana's method is strong on the **dynamic / corpus / outcome-coupled** side; `voice-onboard`
is strong on the **static / disciplined / contract** side. This spec grafts two of Dana's
dynamic strengths onto `voice-onboard` **without** losing its discipline.

**Regime = internal DS comms (owner decision Q1=a):** small samples (often 3-10), no
engagement metrics. This kills two otherwise-tempting ideas: computed statistical
distributions (noise at n<~50) and an engagement-feedback loop (no metric). It also flips
the philosophy: in a data-poor regime, **concrete exemplars + human judgment** beat
statistical mining. B and C are exactly the data-poor-appropriate moves.

## 3. Scope

**In (this round):** B (Exemplars) + C (Hard Rules), consumed by both `comms-polish` and
`comms-draft`.

**Out / deferred:**
- **F — tacit-knowledge interview** (actively elicit never-write phrases, opinions,
  work-vs-personal line). High-value in this regime, but it changes `voice-onboard`'s Step
  flow → **next round**, discussed separately.
- **A — computed distributions:** off (small-sample noise).
- **E — engagement→re-profile loop:** off (no internal-comms metric; also conflicts with
  the human-gated anti-drift design).
- **D — formalized multi-register profiles:** largely covered by the existing
  `Scope & Calibration` section; YAGNI for now.

## 4. Constraints & invariants (must not break)

1. **Frozen contract:** `comms-polish`/`comms-draft` read `voice-profile.md` by **named
   H2 header**. Only **append** new headers; never rename/drop existing ones.
2. **Human-gated, append-only self-improvement:** never auto-edit any SKILL.md, the pattern
   catalog, or the profile schema outside this deliberate, owner-approved change.
3. **OSS engine, not user data:** the shipped `voice-profile.md` is a *sample* (fictional
   "Sam"). New sections ship filled with Sam's fictional content to demonstrate shape only.
4. **Eval discipline:** any fixture keeps the 30-40% baseline-fail band; blind;
   instance-specific; judge calibrated to human labels. **Detector = regression signal,
   never a KPI.**
5. **No fabrication / never invent voice:** thin data → sections degrade honestly, never
   manufacture an exemplar or a rule.

## 5. Design

### 5.1 `_shared/voice-profile.md` — two new H2 sections

Appended **after `## Scope & Calibration`, before `## Changelog`** (Changelog stays last).

**`## Exemplars`** — 2-3 entries. Each entry:
- the **verbatim** sample (fenced),
- a one-line **"Why gold"** naming the dimension to emulate (rhythm? bluntness?
  structure?) — this is what stops the model from surface pattern-matching the wrong axis,
- a **genre tag** (memo / analysis-report / LinkedIn / …).

**`## Hard Rules`** — ≤7 entries (soft cap; typically ~5), high-confidence only. Each rule:
- an **imperative + checkable** assertion (good, checkable: "Never use hype words like
  'unlock' or 'amazing'"; bad, vague: "Sound authentic"),
- an **evidence** pointer (a sample quote or the author's stated never-write),
- distilled from `Vocabulary Don't` + `Things To Avoid` (+ strongest `Signature Moves`
  turned positive). **Author-specific**, not a copy of the generic AI-tell catalog.

### 5.2 `_shared/host-profile-template.md`

Add the two matching blank fields so `voice-onboard`'s fill-in step produces them.

### 5.3 `voice-onboard/SKILL.md` — production side

- **Step 2 (extract):** after the 10 dimensions, distill the ≤7 hard rules from the
  strongest `Vocabulary Don't` / `Things To Avoid` signals (evidence-backed).
- **Step 3 (fill + show):** additionally **propose 2-3 exemplar candidates** (the samples
  that read most like the author) and name their "why gold"; show the draft hard-rules.
- **Step 4 (confirm + write):** author **confirms/replaces** exemplars and rules (they own
  "what good looks like") before writing —延续 the existing human gate.
- **Degrade:** if samples are too thin to extract a confident exemplar/rule, write the
  header with an honest empty marker consistent with the profile's existing convention —
  `Unknown — not enough signal` (the same sentinel voice-onboard already writes for thin
  dimensions) or `None yet — add after a few polish runs` — never fabricate.
- Update the skill's "What you read and write" to list the two new output sections.

### 5.4 `comms-polish/SKILL.md` — consumption side

- **Voice Matching list** (currently enumerates Tone … Scope & Calibration): **add
  `Exemplars` and `Hard Rules`.**
- **Rewrite step 7** (bias toward voice): read same-genre exemplars as a **few-shot style
  anchor**, with an explicit **anti-copy guardrail** — calibrate rhythm/word-choice/
  structure, **never lift phrases or content** (copying hurts lexical originality and
  violates "don't add content not present").
- **`references/final-pass-checklist.md`:** add a **Hard Rules sweep** — check each rule
  pass/fail on the output, **advisory** (flag, don't block). Genre hard-constraints and
  facts still win.

### 5.5 `comms-draft/SKILL.md` — consumption side

- **Inputs list** (L44-48): **add `Exemplars` and `Hard Rules`.**
- **Step 3 (draft under constraints):** use same-genre exemplars as a few-shot target
  (same anti-copy guardrail); apply hard rules as an additional **negative checklist** at
  write-time.
- **Step 5 (self-scan):** include the hard-rules pass in the post-draft scan.

### 5.6 Precedence (conflict resolution)

When sources disagree:

1. **Hard constraints** — genre limits (280 chars), sacred code blocks, facts, legal/
   safety warnings — always win.
2. **Author-specific** — Hard Rules + Exemplars + voice-profile + the author's
   `learned-rules` — beat the generic AI-tell catalog (it's their voice, not slop;
   precedent: `learned-rules.md` `LR-000`).
3. **Generic AI-tell catalog** — default; yields to author-specific.

Hard Rules (onboard-extracted) vs `learned-rules` (later human-gated corrections) conflict
→ **`learned-rules` win** (newer, explicitly corrected).

### 5.7 Graceful degradation & OSS sample

- Missing sections never error (both consumers already degrade on absent sections).
- A present-but-empty sentinel body (`Unknown — not enough signal` / `None yet`) is treated
  as **absent** — consumers neither few-shot against it nor score output against it.
- If no same-genre exemplar exists, **skip** the exemplar few-shot and note it — never
  substitute a cross-genre exemplar.
- Shipped sample profile demonstrates both sections with **fictional Sam** data only.

## 6. Testing & eval

### 6.1 Structural tests — DO NOW (stdlib-only, CI-safe; matches the existing stdlib suite — 78 tests as of 2026-07-03)

- New sections parse from `voice-profile.md`.
- `comms-polish` + `comms-draft` consume-lists include `Exemplars` + `Hard Rules`.
- Anti-copy guardrail text present at both consumption points.
- Graceful degradation: both skills behave when the sections are absent/`None yet`.
- Hard Rules wired as **advisory** (present in final-pass sweep; not a hard block).

### 6.2 Quality eval — DESIGN NOW, NUMBERS BLOCKED

Fixtures to design (not run for numbers yet): (a) exemplar on/off voice-match; (b) hard-rule
flag precision/recall **and false-positive rate**; (c) a **copy-rate / longest-shared-span
overlap** check between a generated draft and its exemplars — **seedable with synthetic
same-genre inputs**, so it can run *before* the 16-24 real drafts arrive, partially
de-risking the anti-copy guardrail ahead of the P3 block. Keep the 30-40% band; blind;
instance-specific; judge calibrated to human labels. **Quality numbers inherit the existing
P3 block (needs 16-24 real enterprise drafts) — do not report, do not fabricate.** No new
blocker is introduced.

## 7. Rollout

- **Branch:** implement on a **new** `feat/voice-onboard-exemplars-hardrules` off `main`
  (not on the current unrelated `feat/audit-report-template`). Never commit to `main`.
- **Contract evolution:** append one `voice-profile.md` Changelog line noting the two new
  sections. **Suite version 1.1.0 → 1.2.0 bumped after implement + acceptance**, not now.
- **Deliverable this round:** this SPEC only → **STOP**. No code until owner says "go".

## 8. File-touch map (for the eventual implementation plan)

1. `_shared/voice-profile.md` — add `## Exemplars` + `## Hard Rules` (Sam sample content).
2. `_shared/host-profile-template.md` — add the two blank fields.
3. `skills/voice-onboard/SKILL.md` — extraction + proposal + confirm + degrade + I/O note.
4. `skills/comms-polish/SKILL.md` — Voice Matching list + step 7 exemplar few-shot (anti-copy).
5. `skills/comms-polish/references/final-pass-checklist.md` — advisory Hard Rules sweep.
6. `skills/comms-draft/SKILL.md` — Inputs list + step 3 few-shot (anti-copy) + step 5 scan.
7. `evals/` — structural tests now; quality fixtures designed (numbers deferred).
8. `CHANGELOG.md` + `voice-profile.md` Changelog line.

(Byte-exact edits are the writing-plans deliverable, not this spec.)

## 9. Decision log (grill-me, 21 branches, all owner-approved 2026-07-03)

| # | Branch | Decision |
|---|---|---|
| B1+C1 | Store where | Approach 1: two new H2 in `voice-profile.md` |
| X1 | Consumers | Both `comms-polish` + `comms-draft` |
| B5 | Exemplar use | Reference, not copy (anti-copy guardrail) |
| C5+C7 | Rule enforcement | Advisory (final-pass sweep + draft negative checklist) |
| C6 | Precedence | hard-constraint > author-specific > generic; learned-rules > hard-rules |
| B3+B4+B6 | Exemplar shape | 2-3 × (verbatim + "why gold" + genre); propose→confirm; same-genre use |
| C2+C3+C4 | Rule shape | ≤7, high-confidence; from Don't/Avoid; imperative+checkable+evidence |
| C8+X3 | Verify | Structural tests now; quality numbers blocked on real drafts |
| B7+B8 | Degrade | Fictional Sam in OSS sample; honest "None yet", never fabricate |
| X2+X4+X5 | Process | Changelog line + version-later; spec-only-then-STOP; new branch off main |

## 10. Open / next

- **F (tacit-knowledge interview)** — next round, separate discussion (owner flagged).
- **Quality numbers** — unblock when 16-24 real enterprise drafts are collected (P3).
