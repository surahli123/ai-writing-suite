# Plan — Engine-Polish Workstream (distilled from 4 external writing skills) — 2026-06-07

**Status: PLAN ONLY — awaiting owner go before any mutation.**
Source: `docs/proposal-distill-writing-skills-2026-06-07.md` (workflow `wf_49f1178c-50b`).
Target branch: new `feat/engine-polish-distill` off `main` (@ `0a4de7f`) → PR → review → merge.

## ⚠️ Key difference from Phase 2a
Phase 2a touched **`evals/` (dev-only, not shipped)**. This workstream edits the
**shipped skill body** (`comms-polish`, `voice-onboard`, the pattern catalog, the
self-improvement hook) — these install on Claude/Codex/Cursor and are **consumer-facing**.
Therefore: **adversarial review before the PR** (CLAUDE.md production default), and a
**version-bump decision** (both `plugin.json` are `1.0.0`; instruction enrichments →
likely `1.1.0`, bumped together per `docs/packaging.md`, on release).

## What this is / is NOT
- IS: the 5 high-confidence, engine-appropriate enrichments from the distillation, all
  instruction-or-single-catalog edits, no new skills, no deps, cross-surface-safe.
- IS NOT: building `comms-draft`/`comms-qa` (v2, D9), deepening the KB (fuel, not engine),
  or wiring the Python detector at runtime (breaks zero-dep/cross-surface). Those were
  adversarially rejected — see the proposal.

---

## The 5 edits (file-level)

### #1 — Re-scan the output against the catalog (comms-polish) · S
- **File:** `skills/comms-polish/SKILL.md`, "Rewrite Workflow" (lines 107–132).
- **Now:** step 8 runs `final-pass-checklist.md` (a qualitative read); the workflow never
  explicitly re-scans the **output** against the pattern catalog. (The checklist *mentions*
  reintroduced tells at line 4, but the catalog re-scan isn't a workflow step.)
- **Edit:** insert a **step 8.5**: "Treat your rewrite as a new draft and re-scan it against
  the pattern catalog (the step-5 scan) — rewriting reintroduces tells. Fix any new tell,
  then run the final-pass checklist." One paragraph; no new file.
- **Why:** all 4 external skills independently shipped a mandatory output re-scan; this is the
  single most cross-validated gap and the cheapest correctness win.

### #2 — Negative routing in sub-skill frontmatter · S
- **Files:** `skills/comms-polish/SKILL.md:3`, `skills/voice-onboard/SKILL.md:3` (and a light
  line on `comms-draft`/`comms-qa` stubs).
- **Edit:** append explicit hand-offs/exclusions to each `description:`
  — comms-polish: "Not for learning an author's voice (→ voice-onboard); not for source code."
  — voice-onboard: "Not for rewriting/polishing (→ comms-polish); this skill only profiles."
- **Why:** our router SKILL.md states it is **not** a runtime interceptor on
  Claude/Codex/Cursor — mis-routing is fixable **only** in the descriptions. Pure metadata.

### #3 — Surface the replacement table into the catalog · S
- **Files:** read `evals/detector/patterns.py` `TIER1` (lines 17–58) + `TIER1_PHRASES` (60+);
  write into `_shared/patterns/lexical-tells.md` (L1 section, after line ~25).
- **Edit:** add a markdown **word → plain-swap table** (e.g. `robust → strong/reliable/solid`,
  `leverage → use`) sourced from the `TIER1` dict the detector already owns. Bare word lists
  become deterministic swaps.
- **Why:** `patterns.py` has the suggestions; the catalog ships only bare lists — the model
  currently guesses the swap. Dedup of data we already own.
- **Drift guard (eng-review outcome):** prose notes don't catch drift — add a **dev sync-test**
  (`evals/test_catalog_sync.py`, same pattern as `test_voice_contract.py`) asserting every
  `patterns.py` `TIER1` key appears in `lexical-tells.md`. Divergence becomes a red CI check,
  not a hope. Keep the provenance comment too. (Bumps #3 from prose-note to tested; still S.)

### #4 — Graduation / anti-bloat step in the self-improvement loop · S
- **File:** `_shared/self-improvement.md` (add a lifecycle phase).
- **Edit:** add a **human-gated GRADUATION** step: when an `active` learned rule has proven
  stable (and, in Layer 3, eval-passed), the **maintainer** folds it into the appropriate
  catalog file and sets the `learned-rules.md` entry `status: retired` — so the on-start read
  doesn't grow unbounded. **Must stay human-gated** — the hook still NEVER auto-edits the
  catalog (lines 97–105); graduation is a maintainer action, mirroring Waza's "fold lessons
  into existing entries, don't append."
- **Why:** the loop is propose→approve→append-only with no consolidation; read cost grows
  linearly with every accepted rule.

### #5 — Layered final-pass gate (comms-polish) · M
- **File:** `skills/comms-polish/references/final-pass-checklist.md`.
- **Edit:** keep all 13 items, **re-bucket** into layers: **L1 mechanical floor** — pull the
  facts/numbers/code/quotes-unchanged item (currently line 25, buried) to the top as a
  **hard, non-tradeable gate**; **L2 style**; **L3 genre+voice cross-checks** (existing);
  **L4** one subjective acceptance question ("did I just read an informed person?"). The
  highest-stakes layer can't be traded off against polish.
- **Why:** mirrors `rubric.md`'s "no_fabrication always required" and the external skills'
  QA-pyramid pattern. Editorial reorganization, not new content.

### Optional (defer unless cheap while in the file)
- **#6** somatic-over-knowledge rewrite *direction* on the C9 emotional-flatline entry
  (`communication-artifacts.md`, currently delete-only) — payoff concentrated in narrative
  genres (2 of 4 presets).
- **#7** a one-line design NOTE (typology-gate + ask-don't-fabricate + human/AI input
  partition) in the `comms-draft`/`comms-qa` stubs — records the constraint for v2, builds
  nothing.

---

## Sequencing & branching
1. Branch `feat/engine-polish-distill` off `main`.
2. Apply #1, #2, #3, #4 (all S) — one commit each (clean, single-concern).
3. Apply #5 (M) — its own commit.
4. (Optional #6/#7 only if you want them in this pass.)

## Verification ("done")
- `bash skills/ai-writing-suite/evals/run_all.sh` still green (these edits don't touch
  `evals/`, but confirm no accidental coupling) — **47 tests + calibration intact**.
- Frontmatter still valid (name + description present) on every edited SKILL.md.
- `_shared/patterns/00-index.md` still coherent after the lexical-tells table add.
- These are **prose/instruction** changes — there is no unit test for "the model follows
  step 8.5"; the eval that would measure it is the **Phase 2b live end-to-end judge**, noted
  but not built here. Honest "done" = files load on host + edits are coherent + review-passed.

## Review gate (production default)
- **Adversarial review (Codex) on the diff before the PR** — these are shipped, consumer-facing
  skill instructions. Show critique + response + revised diff before merge.

## Owner decisions
1. **Scope:** all of #1–#5, or a subset? (Rec: all 5 — they're cohesive and small.)
2. **Optional #6/#7:** include now or defer? (Rec: defer #6; do the #7 note — near-zero cost,
   fence-respecting.)
3. **Version bump:** bump both `plugin.json` to `1.1.0` as part of this, or leave at `1.0.0`
   until a release is cut? (Rec: bump on release, not in this PR.)

## Risks
- **Consumer-facing drift:** edits change what installers get from `main`. Mitigate: review
  gate + the changes are additive/clarifying, not behavior-breaking.
- **#3 catalog/detector drift:** the new table mirrors `patterns.py` — add the provenance note
  so a future patterns.py change is known to need a catalog sync (or, v2, generate it).
- **#4 must not weaken the anti-drift guarantee:** graduation stays human-gated; the hook's
  "never auto-edit the catalog" rule is preserved verbatim.

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 1 | CLEAR | HOLD scope; build all 5 now → 2b next; 0 critical gaps; on-strategy |
| Eng Review | `/plan-eng-review` | Architecture & tests | 1 | CLEAR | 1 finding (#3 catalog/detector drift) → fixed (added dev sync-test); 0 critical gaps |

- **CEO call:** Sequencing resolved → build all 5 engine edits now (HOLD scope, low-risk
  hygiene that doesn't depend on 2b), then make **Phase 2b** (live-judge quality eval) the
  next workstream. The suite's bigger "trust" lever is 2b, but #2–#5 aren't quality bets it
  would measure, so deferring them buys nothing.
- **Eng finding:** #3 (surface `patterns.py` swaps into `lexical-tells.md`) created a DRY
  drift risk → upgraded from a prose note to a **dev sync-test** (red CI check on divergence).
- **Sections (CEO 1–11 / Eng Arch·Quality·Tests·Perf):** N/A — instruction + single-catalog
  edits; no new runtime, endpoints, migrations, data flow, or UI.
- **UNRESOLVED:** none.
- **VERDICT:** CEO + ENG CLEARED — ready to implement (build all 5 now, then Phase 2b).
