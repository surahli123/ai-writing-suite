# voice-onboard Exemplars + Hard Rules — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two append-only sections (`## Exemplars`, `## Hard Rules`) to the voice-profile contract and teach `comms-polish` + `comms-draft` to consume them, per `docs/design-voice-onboard-exemplars-hardrules-2026-07-03.md`.

**Architecture:** Producer (`voice-onboard`) writes the two sections into `_shared/voice-profile.md`; consumers (`comms-polish`, `comms-draft`) already read that file and only need their consumed-section lists + workflow steps extended. No new read paths. Exemplars are a same-genre few-shot **style anchor** (reference, never copy); Hard Rules are an **advisory** final-pass sweep (flag, never block). Verification is stdlib structural tests now (headers present, consume-lists updated, guardrail text present, graceful degrade) plus one runnable behavioral tripwire (an anti-copy overlap scorer on synthetic inputs); the LLM-quality numbers stay blocked on the P3 real-draft gap.

**Tech Stack:** Markdown SKILL.md / contract files; Python **stdlib-only** pytest under `skills/ai-writing-suite/evals/`.

## Global Constraints

_Every task implicitly includes these (verbatim from spec §4):_
- **Frozen contract, append-only:** consumers read `_shared/voice-profile.md` by **named H2 header**; only append new headers, never rename/drop existing ones.
- **Human-gated, append-only self-improvement:** never auto-edit SKILL.md/catalog/schema outside this deliberate change.
- **OSS engine, fictional data only:** shipped `voice-profile.md` is the fictional "Sam" sample; new sections ship with Sam content demonstrating shape, never real user data.
- **Eval discipline:** any fixture keeps the 30-40% baseline-fail band; blind; instance-specific; judge calibrated to human. **Detector = regression signal, never a KPI.**
- **Never invent voice:** thin data → honest empty marker (`Unknown — not enough signal` / `None yet`), never fabricate.
- **Tests are stdlib-only, CI-safe** (no network, no LLM call) — matches the existing suite (78 tests as of 2026-07-03).
- **Advisory, not gating:** Hard Rules flag; only genre hard-constraints (280 chars, code) and facts hard-block.

**Repo root for all paths below:** `skills/ai-writing-suite/`
**Run tests from:** `cd skills/ai-writing-suite && python3 -m pytest evals/ -q`

---

### Task 1: Voice-profile contract — add `## Exemplars` + `## Hard Rules` (Sam sample) + header tripwire

**Files:**
- Modify: `skills/ai-writing-suite/_shared/voice-profile.md` (append two H2 after `## Scope & Calibration`, before `## Changelog`)
- Modify: `skills/ai-writing-suite/_shared/host-profile-template.md` (add the two blank fields, same position)
- Create: `skills/ai-writing-suite/evals/test_bc_sections.py`

**Interfaces:**
- Produces (the contract every later task depends on): exact H2 header strings `## Exemplars` and `## Hard Rules` present in `voice-profile.md`. Exemplar entry shape = `### Exemplar N — genre: <tag>` + fenced quote + `**Why gold:**` line. Hard Rule entry shape = numbered `**imperative**` + `Evidence:` line.

- [ ] **Step 1: Write the failing test**

```python
# skills/ai-writing-suite/evals/test_bc_sections.py
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent           # skills/ai-writing-suite/
PROFILE = (ROOT / "_shared" / "voice-profile.md").read_text(encoding="utf-8")
TEMPLATE = (ROOT / "_shared" / "host-profile-template.md").read_text(encoding="utf-8")

def test_contract_has_new_headers():
    assert "## Exemplars" in PROFILE
    assert "## Hard Rules" in PROFILE

def test_template_has_new_fields():
    assert "## Exemplars" in TEMPLATE
    assert "## Hard Rules" in TEMPLATE

def test_existing_headers_untouched():
    # frozen contract: appends must not drop old headers
    for h in ("## Tone", "## Vocabulary Don't", "## Scope & Calibration", "## Changelog"):
        assert h in PROFILE
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd skills/ai-writing-suite && python3 -m pytest evals/test_bc_sections.py -q`
Expected: FAIL on `test_contract_has_new_headers` / `test_template_has_new_fields` (headers absent).

- [ ] **Step 3: Append the two sections to `_shared/voice-profile.md`** (immediately before `## Changelog`)

```markdown
## Exemplars

<!-- 2-3 verbatim "what good looks like" samples. Each: the sample (fenced), a
     one-line "Why gold" naming the dimension to emulate, and a genre tag.
     comms-polish/comms-draft read these as a SAME-GENRE few-shot STYLE anchor —
     calibrate rhythm/word-choice/structure, NEVER lift phrases or content.
     Thin data -> "Unknown — not enough signal". -->

### Exemplar 1 — genre: blog
> The reranker helped NDCG by 2 points. It also doubled our latency, which nobody
> wanted to talk about. We shipped it anyway, then spent a month paying for it.

**Why gold:** period-heavy short declaratives; leads with a number; ends on a
concrete consequence, not a summary.

### Exemplar 2 — genre: memo
> We turned off the retry job. Duplicate sends dropped to zero the same afternoon.
> The tradeoff: a failed send now waits for the next run instead of retrying.

**Why gold:** plain cause->effect rhythm; quantified result; states the tradeoff
without hedging.

## Hard Rules

<!-- <=7 blunt, checkable, author-specific imperatives distilled from Vocabulary
     Don't + Things To Avoid (+ strongest Signature Moves turned positive), each
     with an evidence pointer. comms-polish runs these as an ADVISORY final-pass
     sweep (flag, never hard-block); comms-draft uses them as a write-time
     negative checklist. Author-specific, NOT the generic AI-tell catalog.
     Thin data -> "Unknown — not enough signal". -->

1. **Never use hype words like "unlock", "amazing", or "game-changing."**
   Evidence: Vocabulary Don't — absent across all samples; author uses plain verbs.
2. **End on a specific consequence or open question, never a motivational wrap-up.**
   Evidence: Signature Moves — every sample closes on a concrete outcome.
3. **State a result with a number whenever one exists.**
   Evidence: Vocabulary Do — "2 points", "zero", not "significantly".
4. **Never use an exclamation point for emphasis.**
   Evidence: Punctuation & Formatting — exclamation almost never.
```

- [ ] **Step 4: Add matching blank fields to `_shared/host-profile-template.md`** (same position, using the file's existing `Unknown — not enough signal` sentinel)

```markdown
## Exemplars

<!-- 2-3 verbatim best samples; each with a "Why gold" line + genre tag.
     Or "None yet — add after a few polish runs" if too thin. -->
Unknown — not enough signal

## Hard Rules

<!-- <=7 checkable author-specific imperatives + evidence each.
     Or "None yet — add after a few polish runs" if too thin. -->
Unknown — not enough signal
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd skills/ai-writing-suite && python3 -m pytest evals/test_bc_sections.py -q`
Expected: PASS (3 tests).

- [ ] **Step 6: Commit**

```bash
git add skills/ai-writing-suite/_shared/voice-profile.md \
        skills/ai-writing-suite/_shared/host-profile-template.md \
        skills/ai-writing-suite/evals/test_bc_sections.py
git commit -m "feat(voice-onboard): add Exemplars + Hard Rules to the voice-profile contract"
```

---

### Task 2: voice-onboard SKILL — produce the two sections (extract + propose + confirm + degrade)

**Files:**
- Modify: `skills/ai-writing-suite/skills/voice-onboard/SKILL.md` (Step 2 extract, Step 3 propose, Step 4 confirm/write, degrade note, "What you read and write")
- Modify: `skills/ai-writing-suite/evals/test_bc_sections.py` (add producer-side text assertions)

**Interfaces:**
- Consumes: the contract header strings from Task 1.
- Produces: SKILL.md instructions that (a) distill Hard Rules in Step 2, (b) propose 2-3 exemplars in Step 3, (c) author confirms/replaces in Step 4, (d) degrade honestly.

- [ ] **Step 1: Write the failing test** (append to `test_bc_sections.py`)

```python
ONBOARD = (ROOT / "skills" / "voice-onboard" / "SKILL.md").read_text(encoding="utf-8")

def test_voice_onboard_produces_new_sections():
    assert "Exemplars" in ONBOARD and "Hard Rules" in ONBOARD

def test_voice_onboard_has_anticopy_and_degrade():
    assert "why gold" in ONBOARD.lower()
    assert "confirm" in ONBOARD.lower() or "replace" in ONBOARD.lower()   # human gate
    assert "None yet" in ONBOARD or "Unknown — not enough signal" in ONBOARD
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd skills/ai-writing-suite && python3 -m pytest evals/test_bc_sections.py -k voice_onboard -q`
Expected: FAIL (SKILL.md not yet edited).

- [ ] **Step 3: Edit `skills/voice-onboard/SKILL.md`** — apply these prose additions:
  - **Step 2 (Extract):** after the 10 dimensions, add: *"Then distill ≤7 **Hard Rules** — blunt, checkable, author-specific imperatives from the strongest `Vocabulary Don't` + `Things To Avoid` (+ strongest `Signature Moves` turned positive), each with an evidence pointer. Not the generic AI-tell catalog."*
  - **Step 3 (Fill + show):** add: *"Also propose 2-3 **Exemplar** candidates — the samples that read most like the author — each with a one-line 'Why gold' (the dimension to emulate) and a genre tag; show the drafted Hard Rules."*
  - **Step 4 (Confirm + write):** add: *"The author **confirms or replaces** the exemplars and Hard Rules before writing — they own 'what good looks like'."*
  - **Degrade note:** *"If samples are too thin for a confident exemplar/rule, write the header with an honest `Unknown — not enough signal` / `None yet — add after a few polish runs`, never fabricate."*
  - **"What you read and write":** add `## Exemplars` and `## Hard Rules` to the list of sections this skill writes.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd skills/ai-writing-suite && python3 -m pytest evals/test_bc_sections.py -k voice_onboard -q`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add skills/ai-writing-suite/skills/voice-onboard/SKILL.md \
        skills/ai-writing-suite/evals/test_bc_sections.py
git commit -m "feat(voice-onboard): produce Exemplars + Hard Rules (propose -> author-confirm -> write)"
```

---

### Task 3: comms-polish consumption — Voice Matching list + exemplar few-shot (anti-copy) + degrade

**Files:**
- Modify: `skills/ai-writing-suite/skills/comms-polish/SKILL.md` (Voice Matching "Sections to use" list; Rewrite step 7; graceful-degrade note)
- Modify: `skills/ai-writing-suite/evals/test_bc_sections.py`

**Interfaces:**
- Consumes: contract headers (Task 1). Produces: comms-polish reads `Exemplars` (same-genre few-shot anchor, anti-copy) + `Hard Rules`.

- [ ] **Step 1: Write the failing test** (append)

```python
POLISH = (ROOT / "skills" / "comms-polish" / "SKILL.md").read_text(encoding="utf-8")

def test_polish_consumes_new_sections():
    assert "Exemplars" in POLISH and "Hard Rules" in POLISH

def test_polish_has_anticopy_and_genre_fallback():
    low = POLISH.lower()
    assert "never lift" in low or "not copy" in low or "anti-copy" in low
    assert "same-genre" in low or "same genre" in low
    assert "cross-genre" in low or "no same-genre" in low            # R4 fallback
```

- [ ] **Step 2: Run to verify fail**

Run: `cd skills/ai-writing-suite && python3 -m pytest evals/test_bc_sections.py -k polish -q`
Expected: FAIL.

- [ ] **Step 3: Edit `skills/comms-polish/SKILL.md`:**
  - **Voice Matching → "Sections to use when present":** add `Exemplars` and `Hard Rules`.
  - **Rewrite step 7:** add: *"If a same-genre `Exemplar` is present, read it as a **few-shot style anchor** — calibrate rhythm/word-choice/structure, **never lift its phrases or content** (copying hurts lexical originality and violates 'don't add content not present'). If no same-genre exemplar exists, **skip** the anchor and note it — never substitute a cross-genre exemplar."*
  - **Graceful degrade:** add that a present-but-empty sentinel body (`Unknown — not enough signal` / `None yet`) is treated as absent.

- [ ] **Step 4: Run to verify pass**

Run: `cd skills/ai-writing-suite && python3 -m pytest evals/test_bc_sections.py -k polish -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/ai-writing-suite/skills/comms-polish/SKILL.md \
        skills/ai-writing-suite/evals/test_bc_sections.py
git commit -m "feat(comms-polish): consume Exemplars (anti-copy few-shot) + Hard Rules"
```

---

### Task 4: comms-polish final-pass — advisory Hard Rules sweep

**Files:**
- Modify: `skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md`
- Modify: `skills/ai-writing-suite/evals/test_bc_sections.py`

**Interfaces:** Consumes Hard Rules header (Task 1). Produces an advisory sweep in the pre-ship checklist.

- [ ] **Step 1: Write the failing test** (append)

```python
CHECKLIST = (ROOT / "skills" / "comms-polish" / "references" / "final-pass-checklist.md").read_text(encoding="utf-8")

def test_final_pass_has_advisory_hardrules_sweep():
    low = CHECKLIST.lower()
    assert "hard rule" in low
    assert "advisory" in low or "flag" in low          # advisory wording
    assert "do not block" in low or "never block" in low or "not a hard block" in low
```

- [ ] **Step 2: Run to verify fail** — `pytest evals/test_bc_sections.py -k final_pass -q` → FAIL.

- [ ] **Step 3: Add to `final-pass-checklist.md`:**

```markdown
- **Hard Rules sweep (advisory).** If the voice profile has a `## Hard Rules` section,
  check the rewrite against each rule and **flag** any violation with the rule text.
  This is advisory — it does **not** block the return. Genre hard-constraints and facts
  still win. Skip silently if the section is absent or reads `Unknown`/`None yet`.
```

- [ ] **Step 4: Run to verify pass** — `pytest evals/test_bc_sections.py -k final_pass -q` → PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md \
        skills/ai-writing-suite/evals/test_bc_sections.py
git commit -m "feat(comms-polish): advisory Hard Rules sweep in final-pass checklist"
```

---

### Task 5: comms-draft consumption — Inputs list + step 3 few-shot (anti-copy) + step 5 scan

**Files:**
- Modify: `skills/ai-writing-suite/skills/comms-draft/SKILL.md` (Inputs list; step 3; step 5)
- Modify: `skills/ai-writing-suite/evals/test_bc_sections.py`

**Interfaces:** Consumes contract headers (Task 1). Produces comms-draft reading Exemplars (few-shot target, anti-copy) + Hard Rules (write-time negative checklist).

- [ ] **Step 1: Write the failing test** (append)

```python
DRAFT = (ROOT / "skills" / "comms-draft" / "SKILL.md").read_text(encoding="utf-8")

def test_draft_consumes_new_sections():
    assert "Exemplars" in DRAFT and "Hard Rules" in DRAFT

def test_draft_has_anticopy_and_genre_fallback():
    low = DRAFT.lower()
    assert "never lift" in low or "not copy" in low or "anti-copy" in low
    assert "same-genre" in low or "same genre" in low
    assert "cross-genre" in low or "no same-genre" in low
```

- [ ] **Step 2: Run to verify fail** — `pytest evals/test_bc_sections.py -k draft -q` → FAIL.

- [ ] **Step 3: Edit `skills/comms-draft/SKILL.md`:**
  - **Inputs:** add `Exemplars` and `Hard Rules` to the voice-profile sections list.
  - **Step 3 (Draft under constraints):** add: *"If a same-genre `Exemplar` is present, use it as a **few-shot target** — match rhythm/structure, **never lift phrases or content**; skip and note if no same-genre exemplar exists, never cross-genre. Apply `Hard Rules` as an additional write-time negative checklist."*
  - **Step 5 (Self-scan):** add the Hard Rules check to the post-draft scan.

- [ ] **Step 4: Run to verify pass** — `pytest evals/test_bc_sections.py -k draft -q` → PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/ai-writing-suite/skills/comms-draft/SKILL.md \
        skills/ai-writing-suite/evals/test_bc_sections.py
git commit -m "feat(comms-draft): consume Exemplars (anti-copy few-shot) + Hard Rules"
```

---

### Task 6: Anti-copy overlap scorer (runnable, synthetic-seeded) + quality-fixture stubs (§6.2, R5)

**Files:**
- Create: `skills/ai-writing-suite/evals/anti_copy.py`
- Create: `skills/ai-writing-suite/evals/test_anti_copy.py`
- Create: `skills/ai-writing-suite/evals/fixtures/quality_bc_README.md` (design stub for the P3-blocked (a)/(b) fixtures)

**Interfaces:**
- Produces: `longest_shared_span(a: str, b: str) -> int` and `copy_rate(draft: str, exemplars: list) -> float` (0..1). This is the only behavioral tripwire runnable before real drafts.

- [ ] **Step 1: Write the failing test**

```python
# skills/ai-writing-suite/evals/test_anti_copy.py
from anti_copy import copy_rate

def test_verbatim_copy_scores_high():
    ex = "the reranker helped ndcg by two points"
    draft = "the reranker helped ndcg by two points and we shipped it anyway"
    assert copy_rate(draft, [ex]) >= 0.6

def test_paraphrase_scores_low():
    ex = "the reranker helped ndcg by two points"
    draft = "our new model improved ranking quality a little that quarter"
    assert copy_rate(draft, [ex]) <= 0.2

def test_no_exemplars_is_zero():
    assert copy_rate("anything here", []) == 0
```

- [ ] **Step 2: Run to verify fail**

Run: `cd skills/ai-writing-suite && python3 -m pytest evals/test_anti_copy.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'anti_copy'`.

- [ ] **Step 3: Implement `evals/anti_copy.py`**

```python
"""Anti-copy overlap scorer (stdlib-only). Synthetic-seeded tripwire for the
exemplar 'reference, never copy' guardrail — runnable before the P3 real drafts."""

def longest_shared_span(a: str, b: str) -> int:
    """Longest contiguous shared word span between two texts."""
    ta, tb = a.lower().split(), b.lower().split()
    best = 0
    dp = [0] * (len(tb) + 1)
    for i in range(1, len(ta) + 1):
        prev = 0
        for j in range(1, len(tb) + 1):
            cur = dp[j]
            if ta[i - 1] == tb[j - 1]:
                dp[j] = prev + 1
                if dp[j] > best:
                    best = dp[j]
            else:
                dp[j] = 0
            prev = cur
    return best

def copy_rate(draft: str, exemplars) -> float:
    """Max longest-shared-span / draft word count across exemplars (0..1)."""
    n = len(draft.split()) or 1
    if not exemplars:
        return 0.0
    return max(longest_shared_span(draft, ex) for ex in exemplars) / n
```

- [ ] **Step 4: Run to verify pass**

Run: `cd skills/ai-writing-suite && python3 -m pytest evals/test_anti_copy.py -q`
Expected: PASS (3 tests).

- [ ] **Step 5: Write the blocked-fixture design stub** — `evals/fixtures/quality_bc_README.md`:

```markdown
# B+C quality fixtures (DESIGN ONLY — numbers BLOCKED on P3 real drafts)

- (a) exemplar on/off voice-match — needs a live model run + 16-24 real drafts. BLOCKED.
- (b) hard-rule flag precision/recall + false-positive rate — needs real drafts. BLOCKED.
- (c) anti-copy overlap — RUNNABLE NOW via evals/anti_copy.py on synthetic inputs.
Discipline: 30-40% baseline-fail band; blind; instance-specific; judge calibrated to human.
Detector = regression signal, never a KPI. Do not report (a)/(b) numbers until drafts exist.
```

- [ ] **Step 6: Commit**

```bash
git add skills/ai-writing-suite/evals/anti_copy.py \
        skills/ai-writing-suite/evals/test_anti_copy.py \
        skills/ai-writing-suite/evals/fixtures/quality_bc_README.md
git commit -m "feat(evals): anti-copy overlap tripwire + blocked B+C quality-fixture design"
```

---

### Task 7: CHANGELOG + voice-profile Changelog line (version bump deferred)

**Files:**
- Modify: `skills/ai-writing-suite/CHANGELOG.md` (`[Unreleased]` → Added)
- Modify: `skills/ai-writing-suite/_shared/voice-profile.md` (Changelog section — one line)

**Interfaces:** none downstream.

- [ ] **Step 1: Add to `CHANGELOG.md` under `## [Unreleased]` → `### Added`:**

```markdown
- voice-onboard: `## Exemplars` (same-genre few-shot style anchor, anti-copy) and
  `## Hard Rules` (advisory, checkable) sections in the voice profile; consumed by
  comms-polish and comms-draft. Structural tests added; quality numbers deferred (P3).
```

- [ ] **Step 2: Add one line to the `## Changelog` section of `_shared/voice-profile.md`:**

```markdown
- 2026-07-03: Added Exemplars + Hard Rules sections (B+C). Append-only; contract headers unchanged.
```

- [ ] **Step 3: Run the FULL suite (no regressions)**

Run: `cd skills/ai-writing-suite && python3 -m pytest evals/ -q`
Expected: PASS — all prior tests + the new `test_bc_sections.py` / `test_anti_copy.py` green. (Do **not** bump the suite version to 1.2.0 here — that happens after implement + owner acceptance.)

- [ ] **Step 4: Commit**

```bash
git add skills/ai-writing-suite/CHANGELOG.md skills/ai-writing-suite/_shared/voice-profile.md
git commit -m "docs(voice-onboard): changelog for Exemplars + Hard Rules (B+C)"
```

---

## Self-Review

**Spec coverage** (spec §5-§8 → task):
- §5.1 two new sections + shapes → **T1** (content) + T2 (production).
- §5.2 host-profile-template fields → **T1** Step 4.
- §5.3 voice-onboard produce/confirm/degrade → **T2**.
- §5.4 comms-polish consume + final-pass → **T3** + **T4**.
- §5.5 comms-draft consume → **T5**.
- §5.6 precedence → prose already in `voice-profile`/catalog; enforced by advisory wording in T3/T4/T5 (no code). Covered.
- §5.7 graceful degrade + fictional Sam → T1 (Sam content) + T3/T5 (sentinel-as-absent).
- §6.1 structural tests → T1/T2/T3/T4/T5 (each ships its tripwire).
- §6.2 quality fixtures (incl. R5 copy-rate) → **T6**.
- §7 changelog + version-deferred → **T7**.
- **R1-R5** (review residuals) already folded into the spec; R6 (test-file targeting) satisfied by add-only `test_bc_sections.py`; R7/R8 out of scope (noted).

**Placeholder scan:** none — every markdown addition and every test/impl body is shown verbatim.

**Type consistency:** `longest_shared_span` / `copy_rate` names + signatures match between T6 impl and test. Header strings `## Exemplars` / `## Hard Rules` identical across T1-T5.

## Execution Handoff

Two execution options when the owner gives the code-go:
1. **Subagent-Driven (recommended)** — fresh subagent per task, two-stage review between tasks.
2. **Inline Execution** — batch tasks in this session with checkpoints.
