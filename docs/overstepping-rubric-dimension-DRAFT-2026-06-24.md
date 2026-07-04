# DRAFT — Over-stepping (反代入式越位感) judge dimension

> **Plan-only.** Lives in `docs/`. NOT wired into the skill. This is the proposed
> addition to `evals/fixtures/rubric.md` (+ a one-line note in `_shared/patterns/`)
> for owner review before anything touches the skill tree.

## What this adds (minimal)

**One** new LLM-judge dimension — `overstepping_removed` — plus a *validity condition*
the judge applies. No regex, no detector change, no new dependency. It rides the
existing before/after judge machinery (`evals/fixtures/judge.py`, `rubric.md`):
the model reads `before` + `after` and scores the rewrite.

**Why judge-only, never the detector / never a CI gate:**
- Detector evidence (ran `evals/detector` on all fixtures, 2026-06-24): every
  over-stepping `before` scored **0–4/100** vs `baseline_threshold=14`. The mechanical
  detector is *blind* to over-stepping — every word is clean; the tell is in the *stance*.
- Round-2 finding: whether a line over-steps is **partly intent-dependent** (a presumed
  prior X may or may not be one the reader actually holds). So the judge stays **advisory**
  (opt-in `AIWS_JUDGE_*`, SKIPs offline, never gates CI) — consistent with `judge.py`'s
  existing honesty stance.

## The new dimension (drop into rubric.md's dimensions table)

| Dimension | PASS when | FAIL when |
| --- | --- | --- |
| `overstepping_removed` | `after` removes a **manufactured** reader-presumption — "you assume/think X", "很多人以为 X", a self-Q&A ("Can you…? Yes —"), or a projected mental image ("you picture…") — whose presumed prior X is **not** a real, widespread belief, **and** the underlying claim survives. | The presumption still reads in `after`; **or** `after` stripped a contrast whose X **was** a real widespread belief (that loses information → also fails `meaning_preserved`). |

## The core test (the load-bearing rule)

> **A presumption is over-stepping ONLY when the prior X is a manufactured strawman.
> When X is a genuinely common belief the reader holds, the contrast is legitimate —
> removing it loses information.**

This single rule decides every case, across all sub-types. Evidence it's load-bearing
(owner labels):
- `N2` "You probably assume **more data = better model**, but…" → X is a manufactured framing → **over-stepping** (PASS to remove).
- `N5` "你可能以为**推荐系统就是猜你喜欢什么**，其实…" → X is a *semi-real* lay belief → **ambiguous** → dropped from gold.
- `H2` "爱**不是**感觉，**而是**行为" / `H3` "转型**不是**砸钱，**而是**…" → X is a real widespread belief → **legitimate contrast** → removing it is over-correction (FAIL `meaning_preserved`).

The judge's 4 self-questions (from the source article), encoded in the prompt:
1. Is the writer thinking **for** the reader?
2. Is this a misconception the reader **actually** holds? *(the validity condition)*
3. Is the line conveying content, or **performing insight**?
4. Does it still hold after deleting "you think / 你以为"?

## Interaction with `meaning_preserved` (guards over-correction)

`overstepping_removed` and `meaning_preserved` work as a **pair**:
- Positives: presumption removed **and** claim kept → both PASS → overall PASS.
- Hard-negatives (the over-correction trap): `after` deleted a *legitimate* contrast →
  `meaning_preserved` FAIL → overall FAIL, **even though** a naive reading might say "a
  '不是X而是Y' was removed, good." The rubric must stop the judge from rewarding that.

No change to verdict aggregation: `no_fabrication` stays always-required;
overall PASS iff every `rubric_focus` dim + `no_fabrication` PASS (per `judge.py::aggregate`).

## Judge-prompt addition (append to the existing template)

```
OVER-STEPPING CHECK (dimension: overstepping_removed)
A line "over-steps" when it thinks FOR the reader: presuming a belief/misconception,
painting a mental picture, or asking-then-answering its own rhetorical question, then
correcting from above. It is over-stepping ONLY IF the presumed prior is a manufactured
strawman. If the prior is a real, widespread belief, the contrast is LEGITIMATE — do not
reward its removal; deleting it loses information (fail meaning_preserved).
Test: does the point still stand after deleting "you think / 你以为 / 很多人以为"?
  - stands → the frame was over-stepping → overstepping_removed: PASS if `after` dropped it
  - collapses (X was a real prior) → contrast was legitimate → meaning_preserved: FAIL if `after` dropped it
```

## Scope (what this dimension does NOT claim)

- Targets only the **clearly manufactured** sub-types: self-Q&A theater, projected mental
  image, manufactured-prior correction.
- **Excludes** intent-dependent cases (the round-1 `F3` "男友不爱你" type): whether they
  over-step can't be decided from text alone → out of scope, not a fixture.
- Pairs with v1.2 item #8 (ask intent/audience pre-write) — knowing the reader's real
  priors is what disambiguates the hard cases at draft time.

## Fixtures
- 4 PASS positives + 3 FAIL hard-negatives: `docs/overstepping-fixtures-DRAFT-2026-06-24.json`.
- Owner-validated gold (round 2): `docs/overstepping-gold-2026-06-24.json`.
- Directional smoke-test only (7 items) — **not** a kappa-calibrated metric (kappa needs ≥40).
